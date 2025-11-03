# -*- coding: utf-8 -*-
import sys
import io


"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

WSP Compliance Engine for FoundUps Agent

This module provides a comprehensive compliance checking system that enables
Agent 0102 to autonomously enforce WSP (Windsurfer Protocol) rules and make
informed decisions about task execution.

The engine integrates with existing shared tools (mps_calculator, modlog_integration)
to provide a unified automation layer for WSP compliance.

Author: FoundUps Agent Utilities Team
Version: 1.0
Date: 2025-05-29
WSP Compliance: WSP 0, 1, 3, 4, 5, 7, 10, 11, 12, 13, 14
"""

import os
import re
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import logging

# Import our existing shared tools
try:
    from .mps_calculator import MPSCalculator
    from .modlog_integration import ModLogIntegration
except ImportError:
    # Fallback for direct execution
    from mps_calculator import MPSCalculator
    from modlog_integration import ModLogIntegration

logger = logging.getLogger(__name__)


@dataclass
class WSPPromptDetails:
    """Structure for WSP Prompt validation"""
    task: str
    scope_files: List[str]
    constraints: List[str]
    expected_deliverables: List[str]
    wsp_references: List[str]


@dataclass
class TestStrategyResult:
    """Result structure for test strategy evaluation"""
    action: str  # 'EXTEND', 'CREATE_NEW', 'REJECT_DUPLICATE', 'NO_TESTS_EXIST_YET'
    target_file: Optional[str]
    rationale: str
    readme_needs_update: bool
    existing_coverage: List[str] = None


class WSPComplianceChecker:
    """
    Unified WSP compliance checking engine for Agent 0102.
    
    This class provides comprehensive pre-execution validation and decision support
    for WSP-compliant task execution, integrating MPS calculation, ModLog management,
    and protocol enforcement.
    """
    
    def __init__(self, project_root: str = "."):
        """
        Initialize the WSP Compliance Engine.
        
        Args:
            project_root: Path to the project root directory
        """
        self.project_root = Path(project_root)
        self.mps_calculator = MPSCalculator()
        self.modlog_integration = ModLogIntegration()
        
        # Load project configuration
        self._load_project_config()
        
        # WSP 7 commit types from Conventional Commits
        self.valid_commit_types = {
            'feat', 'fix', 'docs', 'style', 'refactor', 'perf', 'test', 'chore',
            'build', 'ci', 'revert', 'wip', 'merge', 'arch', 'breaking'
        }
        
        # WSP 10 ESM emoji mappings
        self.esm_emojis = {
            'feat': '[U+2728]', 'fix': '[U+1F41B]', 'docs': '[NOTE]', 'style': '[U+1F484]',
            'refactor': '[U+267B]️', 'perf': '[LIGHTNING]', 'test': '[OK]', 'chore': '[TOOL]',
            'build': '[BOX]', 'ci': '[U+1F477]', 'revert': '⏪', 'arch': '[U+1F3D7]️',
            'breaking': '[U+1F4A5]', 'wip': '[U+1F6A7]', 'merge': '[U+1F500]'
        }

    def _load_project_config(self):
        """Load project-specific WSP configuration files"""
        try:
            # Load .foundups_project_rules if it exists
            rules_file = self.project_root / '.foundups_project_rules'
            if rules_file.exists():
                with open(rules_file, 'r') as f:
                    self.project_rules = yaml.safe_load(f)
            else:
                self.project_rules = {}
                
            # Load global rules reference
            global_rules_file = self.project_root / 'docs' / 'foundups_global_rules.md'
            self.has_global_rules = global_rules_file.exists()
            
        except Exception as e:
            logger.warning(f"Could not load project configuration: {e}")
            self.project_rules = {}
            self.has_global_rules = False

    def check_prompt_constraints(self, prompt_details: WSPPromptDetails) -> Dict[str, Any]:
        """
        Validates task, scope, and constraints from a WSP Prompt.
        
        Args:
            prompt_details: Structured WSP prompt information
            
        Returns:
            Dictionary with validation results
            
        WSP References: WSP 0, Appendix A
        """
        result = {
            'is_valid': True,
            'violations': [],
            'recommendations': [],
            'warnings': []
        }
        
        # Check task atomicity
        if self._check_task_atomicity(prompt_details.task):
            result['violations'].append("Task appears to bundle multiple unrelated changes")
            result['is_valid'] = False
            
        # Validate file scope boundaries
        scope_issues = self._validate_file_scope(prompt_details.scope_files)
        if scope_issues:
            result['violations'].extend(scope_issues)
            result['is_valid'] = False
            
        # Check constraint compliance
        constraint_issues = self._validate_constraints(prompt_details.constraints)
        if constraint_issues:
            result['violations'].extend(constraint_issues)
            result['is_valid'] = False
            
        # Validate WSP references
        wsp_issues = self._validate_wsp_references(prompt_details.wsp_references)
        if wsp_issues:
            result['warnings'].extend(wsp_issues)
            
        return result

    def evaluate_test_strategy(self, module_path: str, functionality_description: str) -> TestStrategyResult:
        """
        Evaluates test creation/extension strategy per WSP 14.
        
        Args:
            module_path: Path to the target module
            functionality_description: Description of functionality to test
            
        Returns:
            TestStrategyResult with recommended action
            
        WSP References: WSP 14, WSP 3, AI Guidelines
        """
        module_path = Path(module_path)
        tests_dir = module_path / 'tests'
        readme_path = tests_dir / 'README.md'
        
        # Check if tests directory exists
        if not tests_dir.exists():
            return TestStrategyResult(
                action='NO_TESTS_EXIST_YET',
                target_file=str(tests_dir / f'test_{self._generate_test_name(functionality_description)}.py'),
                rationale='No tests directory exists for this module',
                readme_needs_update=True
            )
            
        # Parse existing tests README
        existing_tests = self._parse_tests_readme(readme_path)
        if not existing_tests and not list(tests_dir.glob('test_*.py')):
            return TestStrategyResult(
                action='NO_TESTS_EXIST_YET',
                target_file=str(tests_dir / f'test_{self._generate_test_name(functionality_description)}.py'),
                rationale='Tests directory exists but no tests found',
                readme_needs_update=True
            )
            
        # Analyze existing test coverage
        coverage_analysis = self._analyze_test_coverage(tests_dir, functionality_description)
        
        if coverage_analysis['exact_match']:
            return TestStrategyResult(
                action='REJECT_DUPLICATE',
                target_file=coverage_analysis['exact_match'],
                rationale=f"Functionality already covered in {coverage_analysis['exact_match']}",
                readme_needs_update=False,
                existing_coverage=coverage_analysis['similar_tests']
            )
            
        elif coverage_analysis['extend_candidate']:
            return TestStrategyResult(
                action='EXTEND',
                target_file=coverage_analysis['extend_candidate'],
                rationale=f"Extending existing test file with related functionality",
                readme_needs_update=True,
                existing_coverage=coverage_analysis['similar_tests']
            )
            
        else:
            return TestStrategyResult(
                action='CREATE_NEW',
                target_file=str(tests_dir / f'test_{self._generate_test_name(functionality_description)}.py'),
                rationale='No existing tests cover this specific functionality',
                readme_needs_update=True,
                existing_coverage=coverage_analysis['similar_tests']
            )

    def validate_module_file_path(self, proposed_path: str, is_test_file: bool = False) -> Dict[str, Any]:
        """
        Validates if a proposed file path conforms to WSP 1 and WSP 3.
        
        Args:
            proposed_path: The proposed file path
            is_test_file: Whether this is a test file
            
        Returns:
            Validation result dictionary
            
        WSP References: WSP 1, WSP 3
        """
        path = Path(proposed_path)
        result = {
            'is_valid': True,
            'expected_structure': None,
            'reason': '',
            'suggestions': []
        }
        
        # Check if path follows WSP 3 enterprise domain architecture
        if not self._validate_domain_structure(path):
            result['is_valid'] = False
            result['reason'] = 'Path does not follow WSP 3 enterprise domain architecture'
            result['expected_structure'] = 'modules/{domain}/{feature_group}/{module}/'
            
        # Check WSP 1 module structure
        if not self._validate_module_structure(path, is_test_file):
            result['is_valid'] = False
            if result['reason']:
                result['reason'] += '; '
            result['reason'] += 'Path does not follow WSP 1 module structure'
            result['suggestions'].append('Files should be in src/ or tests/ subdirectories')
            
        return result

    def assess_modlog_update_necessity(self, change_type: str, scope: List[str], 
                                     is_release: bool = False, is_clean_state: bool = False) -> bool:
        """
        Determines if a ModLog.md update is needed per WSP 11.
        
        Args:
            change_type: Type of change (FEATURE, FIX, REFACTOR, etc.)
            scope: List of affected modules/files
            is_release: Whether this is a release
            is_clean_state: Whether this creates a clean state
            
        Returns:
            True if ModLog update is recommended
            
        WSP References: WSP 11
        """
        # WSP 11.2.4 Rules for ModLog updates
        if is_release or is_clean_state:
            return True
            
        # Significant features, critical fixes, architectural changes
        significant_changes = {
            'FEATURE_COMPLETION', 'CRITICAL_FIX', 'ARCH_CHANGE', 
            'BREAKING_INTERFACE_CHANGE', 'MAJOR_REFACTOR'
        }
        
        if change_type in significant_changes:
            return True
            
        # Check scope significance - if affects multiple modules
        if len(scope) > 3:  # Arbitrary threshold for "significant scope"
            return True
            
        # Check if any affected files are in critical modules (high MPS)
        for item in scope:
            module_context = self.get_task_mps_context(self._extract_module_name(item))
            if module_context['exists'] and module_context['mps_score'] > 85:  # High priority threshold
                return True
                
        return False

    def check_interface_dependency_files(self, module_path: str) -> Dict[str, Any]:
        """
        Checks for presence and basic validity of interface and dependency files.
        
        Args:
            module_path: Path to the module to check
            
        Returns:
            Dictionary with interface and dependency validation results
            
        WSP References: WSP 12, WSP 13, WSP 4
        """
        module_path = Path(module_path)
        result = {
            'interface_ok': True,
            'interface_issues': [],
            'dependencies_ok': True,
            'dependencies_issues': []
        }
        
        # Check for interface artifacts (WSP 12)
        interface_files = ['interface.py', 'interface.md', '__init__.py']
        found_interface = False
        for iface_file in interface_files:
            if (module_path / iface_file).exists():
                found_interface = True
                break
                
        if not found_interface:
            result['interface_ok'] = False
            result['interface_issues'].append('No interface artifact found')
            
        # Check for dependency manifest (WSP 13)
        dep_files = ['dependencies.yaml', 'requirements.txt', 'pyproject.toml']
        found_deps = False
        for dep_file in dep_files:
            if (module_path / dep_file).exists():
                found_deps = True
                break
                
        if not found_deps:
            result['dependencies_ok'] = False
            result['dependencies_issues'].append('No dependency manifest found')
            
        return result

    def get_task_mps_context(self, affected_module_name: str) -> Dict[str, Any]:
        """
        Retrieves MPS score for an affected module to provide context for task impact.
        
        Args:
            affected_module_name: Name of the module
            
        Returns:
            Dictionary with MPS context information
            
        WSP References: WSP 5
        """
        try:
            # Try to load modules_to_score.yaml
            yaml_path = self.project_root / 'modules_to_score.yaml'
            if yaml_path.exists():
                with open(yaml_path, 'r') as f:
                    modules_data = yaml.safe_load(f)
                    
                for module in modules_data.get('modules', []):
                    if module.get('name') == affected_module_name:
                        scores = {k: v for k, v in module.items() if k != 'name'}
                        mps_score = self.mps_calculator.calculate(scores)
                        
                        # Classify based on score
                        if mps_score >= 90:
                            classification = 'CRITICAL'
                        elif mps_score >= 75:
                            classification = 'HIGH'
                        elif mps_score >= 50:
                            classification = 'MEDIUM'
                        else:
                            classification = 'LOW'
                            
                        return {
                            'module_name': affected_module_name,
                            'mps_score': mps_score,
                            'classification': classification,
                            'exists': True,
                            'raw_scores': scores
                        }
                        
        except Exception as e:
            logger.warning(f"Could not load MPS data: {e}")
            
        return {
            'module_name': affected_module_name,
            'mps_score': 0,
            'classification': 'UNKNOWN',
            'exists': False
        }

    def validate_commit_message(self, commit_message: str) -> Dict[str, Any]:
        """
        Validates commit message format against WSP 7 and WSP 10.
        
        Args:
            commit_message: The proposed commit message
            
        Returns:
            Validation result dictionary
            
        WSP References: WSP 7, WSP 10
        """
        result = {
            'is_valid': True,
            'errors': [],
            'suggestions': [],
            'detected_type': None,
            'detected_scope': None,
            'has_emoji': False
        }
        
        # WSP 7: Conventional Commits format
        # Pattern: type(scope): [emoji] summary
        pattern = r'^([a-z]+)(\([^)]+\))?\s*:\s*([[ART][U+1F41B][NOTE][U+1F484][U+267B]️[LIGHTNING][OK][TOOL][BOX][U+1F477]⏪[U+1F3D7]️[U+1F4A5][U+1F6A7][U+1F500]]?\s*)?(.+)$'
        match = re.match(pattern, commit_message.strip())
        
        if not match:
            result['is_valid'] = False
            result['errors'].append('Does not follow Conventional Commits format: type(scope): summary')
            return result
            
        commit_type = match.group(1)
        scope = match.group(2)
        emoji = match.group(3)
        summary = match.group(4)
        
        result['detected_type'] = commit_type
        result['detected_scope'] = scope[1:-1] if scope else None  # Remove parentheses
        result['has_emoji'] = bool(emoji and emoji.strip())
        
        # Validate commit type
        if commit_type not in self.valid_commit_types:
            result['is_valid'] = False
            result['errors'].append(f'Invalid commit type: {commit_type}')
            result['suggestions'].append(f'Valid types: {", ".join(sorted(self.valid_commit_types))}')
            
        # WSP 10: ESM emoji validation
        if emoji and emoji.strip():
            expected_emoji = self.esm_emojis.get(commit_type)
            actual_emoji = emoji.strip()
            if expected_emoji and actual_emoji != expected_emoji:
                result['suggestions'].append(f'Consider using {expected_emoji} for {commit_type} commits')
                
        # Validate summary
        if len(summary) < 10:
            result['suggestions'].append('Summary should be more descriptive (at least 10 characters)')
            
        if summary[0].isupper():
            result['suggestions'].append('Summary should start with lowercase letter')
            
        if summary.endswith('.'):
            result['suggestions'].append('Summary should not end with a period')
            
        return result

    def generate_pre_execution_report(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive pre-execution compliance report.
        
        Args:
            task_context: Context information about the task
            
        Returns:
            Comprehensive compliance report
        """
        report = {
            'timestamp': str(Path.cwd()),  # Placeholder for actual timestamp
            'task_context': task_context,
            'compliance_checks': {},
            'recommendations': [],
            'blocking_issues': [],
            'overall_status': 'PENDING'
        }
        
        # Run all applicable checks based on task context
        if 'prompt_details' in task_context:
            report['compliance_checks']['prompt'] = self.check_prompt_constraints(
                task_context['prompt_details']
            )
            
        if 'module_path' in task_context and 'functionality' in task_context:
            report['compliance_checks']['test_strategy'] = self.evaluate_test_strategy(
                task_context['module_path'], 
                task_context['functionality']
            )
            
        if 'proposed_files' in task_context:
            report['compliance_checks']['file_paths'] = []
            for file_path in task_context['proposed_files']:
                validation = self.validate_module_file_path(file_path)
                report['compliance_checks']['file_paths'].append({
                    'file': file_path,
                    'validation': validation
                })
                
        # Determine overall status
        has_blocking = any(
            not check.get('is_valid', True) 
            for check in report['compliance_checks'].values()
            if isinstance(check, dict)
        )
        
        report['overall_status'] = 'BLOCKED' if has_blocking else 'APPROVED'
        
        return report

    # Helper methods
    def _check_task_atomicity(self, task: str) -> bool:
        """Check if task appears to bundle multiple unrelated changes"""
        # Simple heuristic: look for conjunctions that might indicate bundled tasks
        bundling_indicators = [' and ', ' also ', ' plus ', ' additionally ', ' furthermore ']
        return any(indicator in task.lower() for indicator in bundling_indicators)

    def _validate_file_scope(self, scope_files: List[str]) -> List[str]:
        """Validate that file scope is appropriate"""
        issues = []
        
        # Check for scope creep (too many unrelated files)
        if len(scope_files) > 10:  # Arbitrary threshold
            issues.append(f"Large scope with {len(scope_files)} files may indicate task bundling")
            
        # Check for cross-domain modifications
        domains = set()
        for file_path in scope_files:
            domain = self._extract_domain(file_path)
            if domain:
                domains.add(domain)
                
        if len(domains) > 2:
            issues.append(f"Task spans multiple domains: {', '.join(domains)}")
            
        return issues

    def _validate_constraints(self, constraints: List[str]) -> List[str]:
        """Validate constraint compliance"""
        issues = []
        
        # Check for external dependency constraints
        no_external_deps = any('no external' in c.lower() for c in constraints)
        if no_external_deps:
            # This would need more sophisticated analysis of proposed changes
            pass
            
        return issues

    def _validate_wsp_references(self, wsp_refs: List[str]) -> List[str]:
        """Validate WSP reference citations"""
        warnings = []
        
        valid_wsps = {f'WSP {i}' for i in range(0, 15)}  # WSP 0-14
        
        for ref in wsp_refs:
            if ref not in valid_wsps:
                warnings.append(f"Unknown WSP reference: {ref}")
                
        return warnings

    def _parse_tests_readme(self, readme_path: Path) -> Dict[str, str]:
        """Parse tests/README.md to extract existing test descriptions"""
        if not readme_path.exists():
            return {}
            
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Simple parsing - look for test file mentions
            tests = {}
            lines = content.split('\n')
            current_test = None
            
            for line in lines:
                if 'test_' in line and '.py' in line:
                    # Extract test file name
                    match = re.search(r'test_\w+\.py', line)
                    if match:
                        current_test = match.group()
                        tests[current_test] = line.strip()
                        
            return tests
            
        except Exception as e:
            logger.warning(f"Could not parse tests README: {e}")
            return {}

    def _analyze_test_coverage(self, tests_dir: Path, functionality: str) -> Dict[str, Any]:
        """Analyze existing test coverage for functionality"""
        result = {
            'exact_match': None,
            'extend_candidate': None,
            'similar_tests': []
        }
        
        # Get functionality keywords
        keywords = self._extract_keywords(functionality)
        
        # Analyze existing test files
        for test_file in tests_dir.glob('test_*.py'):
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    
                # Simple keyword matching
                matches = sum(1 for keyword in keywords if keyword.lower() in content)
                
                if matches >= len(keywords) * 0.8:  # 80% keyword match
                    result['exact_match'] = str(test_file.name)
                    break
                elif matches >= len(keywords) * 0.4:  # 40% keyword match
                    if not result['extend_candidate']:
                        result['extend_candidate'] = str(test_file.name)
                    result['similar_tests'].append({
                        'file': str(test_file.name),
                        'match_score': matches / len(keywords)
                    })
                    
            except Exception as e:
                logger.warning(f"Could not analyze test file {test_file}: {e}")
                
        return result

    def _generate_test_name(self, functionality: str) -> str:
        """Generate appropriate test file name from functionality description"""
        # Extract key words and convert to snake_case
        words = re.findall(r'\w+', functionality.lower())
        key_words = [w for w in words if len(w) > 2 and w not in {'the', 'and', 'for', 'with', 'that'}]
        return '_'.join(key_words[:3])  # Limit to 3 key words

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        words = re.findall(r'\w+', text.lower())
        # Filter out common words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an'}
        return [w for w in words if len(w) > 2 and w not in stop_words]

    def _validate_domain_structure(self, path: Path) -> bool:
        """Validate path follows WSP 3 enterprise domain architecture"""
        parts = path.parts
        
        # Should start with 'modules'
        if not parts or parts[0] != 'modules':
            return False
            
        # Should have at least: modules/domain/feature_group/module/
        return len(parts) >= 4

    def _validate_module_structure(self, path: Path, is_test_file: bool) -> bool:
        """Validate path follows WSP 1 module structure"""
        parts = path.parts
        
        if is_test_file:
            # Test files should be in tests/ directory
            return 'tests' in parts
        else:
            # Source files should be in src/ directory
            return 'src' in parts

    def _extract_domain(self, file_path: str) -> Optional[str]:
        """Extract domain from file path"""
        parts = Path(file_path).parts
        if len(parts) >= 2 and parts[0] == 'modules':
            return parts[1]
        return None

    def _extract_module_name(self, file_path: str) -> str:
        """Extract module name from file path"""
        parts = Path(file_path).parts
        if len(parts) >= 4 and parts[0] == 'modules':
            return parts[3]  # modules/domain/feature_group/module
        return Path(file_path).stem


# Convenience functions for backward compatibility and ease of use
def check_wsp_compliance(task_context: Dict[str, Any], project_root: str = ".") -> Dict[str, Any]:
    """
    Convenience function for quick WSP compliance checking.
    
    Args:
        task_context: Task context information
        project_root: Project root directory
        
    Returns:
        Compliance check results
    """
    checker = WSPComplianceChecker(project_root)
    return checker.generate_pre_execution_report(task_context)


def validate_test_strategy(module_path: str, functionality: str, project_root: str = ".") -> TestStrategyResult:
    """
    Convenience function for test strategy validation.
    
    Args:
        module_path: Path to the module
        functionality: Functionality description
        project_root: Project root directory
        
    Returns:
        Test strategy recommendation
    """
    checker = WSPComplianceChecker(project_root)
    return checker.evaluate_test_strategy(module_path, functionality)


def check_commit_message(message: str, project_root: str = ".") -> Dict[str, Any]:
    """
    Convenience function for commit message validation.
    
    Args:
        message: Commit message to validate
        project_root: Project root directory
        
    Returns:
        Validation results
    """
    checker = WSPComplianceChecker(project_root)
    return checker.validate_commit_message(message) 