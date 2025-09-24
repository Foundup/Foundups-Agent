#!/usr/bin/env python3
"""
Intelligent Monitoring System for HoloIndex DAE

Context-aware subroutines that run automatically based on algorithmic triggers,
not timers or manual commands. The DAE intelligently decides when to run health
checks, detect duplicates, or monitor patterns.

WSP Compliance: WSP 87, WSP 49, WSP 84, WSP 50
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib
import json


@dataclass
class MonitoringContext:
    """Context that triggers monitoring subroutines"""
    query: str
    search_results: List[Dict]
    file_paths: List[str] = field(default_factory=list)
    modules_touched: List[str] = field(default_factory=list)
    patterns_detected: List[str] = field(default_factory=list)
    agent_actions: List[str] = field(default_factory=list)


@dataclass
class MonitoringResult:
    """Result from intelligent monitoring"""
    health_warnings: List[str] = field(default_factory=list)
    duplicates_found: List[Dict] = field(default_factory=list)
    size_issues: List[Dict] = field(default_factory=list)
    structure_violations: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class IntelligentMonitor:
    """
    Context-aware monitoring that runs subroutines based on algorithmic triggers.
    No timers, no manual commands - pure intelligent decision making.
    """

    def __init__(self):
        # Trigger thresholds (algorithmic, not time-based)
        self.triggers = {
            'size_check': self._should_check_size,
            'duplicate_check': self._should_check_duplicates,
            'structure_check': self._should_check_structure,
            'pattern_analysis': self._should_analyze_patterns,
            'agent_behavior': self._should_monitor_agent
        }

        # Cache to avoid redundant checks
        self.check_cache = {}
        self.module_fingerprints = {}

        # Agent behavior tracking
        self.agent_behavior = defaultdict(list)

    def monitor(self, context: MonitoringContext) -> MonitoringResult:
        """
        Main monitoring function - intelligently decides what to check
        based on context, not time or manual triggers.
        """
        result = MonitoringResult()

        # Extract relevant paths from search results
        self._extract_context_paths(context)

        # Run subroutines based on algorithmic triggers
        for check_name, should_check in self.triggers.items():
            if should_check(context):
                self._run_subroutine(check_name, context, result)

        # Add intelligent insights based on combined results
        self._add_intelligent_insights(context, result)

        return result

    def _should_check_size(self, context: MonitoringContext) -> bool:
        """
        Algorithm: Check size when working with specific files or
        when search touches modules with many results.
        """
        # Check if query mentions files or modules
        if any(word in context.query.lower() for word in ['file', 'module', 'refactor', 'large', 'size']):
            return True

        # Check if search results concentrate in few files (potential large files)
        if context.file_paths:
            file_counts = defaultdict(int)
            for path in context.file_paths:
                file_counts[path] += 1

            # If any file appears > 3 times in results, it's likely large
            if any(count > 3 for count in file_counts.values()):
                return True

        return False

    def _should_check_duplicates(self, context: MonitoringContext) -> bool:
        """
        Algorithm: Check duplicates when creating new code or
        when search reveals similar function names.
        """
        # Keywords that suggest potential duplication
        duplicate_indicators = ['create', 'new', 'add', 'implement', 'copy', 'similar', 'like']
        if any(word in context.query.lower() for word in duplicate_indicators):
            return True

        # Check if search results have similar function names
        if context.search_results:
            functions = [r.get('function', '') for r in context.search_results if r.get('function')]
            if len(functions) > len(set(functions)):  # Duplicate function names
                return True

        return False

    def _should_check_structure(self, context: MonitoringContext) -> bool:
        """
        Algorithm: Check structure when working with new modules or
        when query suggests module-level operations.
        """
        structure_keywords = ['module', 'structure', 'scaffold', 'create', 'organize', 'wsp 49']
        if any(word in context.query.lower() for word in structure_keywords):
            return True

        # Check if touching modules without proper structure
        for module in context.modules_touched:
            if not self._is_module_cached(module):
                return True

        return False

    def _should_analyze_patterns(self, context: MonitoringContext) -> bool:
        """
        Algorithm: Analyze patterns when multiple similar operations detected
        or when working with pattern-heavy code.
        """
        # Check for pattern keywords
        if any(word in context.query.lower() for word in ['pattern', 'template', 'reuse', 'common']):
            return True

        # Check if agent is repeating actions (pattern forming)
        if len(context.agent_actions) > 5:
            action_types = [a.split(':')[0] for a in context.agent_actions if ':' in a]
            if len(action_types) > len(set(action_types)) * 1.5:  # Repetition detected
                return True

        return False

    def _should_monitor_agent(self, context: MonitoringContext) -> bool:
        """
        Algorithm: Monitor agent behavior when vibecoding patterns detected
        or when agent deviates from WSP compliance.
        """
        # Always monitor if agent actions present
        if context.agent_actions:
            # Check for vibecoding patterns
            vibecode_patterns = ['file_create:new', 'skip_search', 'no_holoindex', 'direct_write']
            if any(pattern in ' '.join(context.agent_actions).lower() for pattern in vibecode_patterns):
                return True

        return len(context.agent_actions) > 0  # Always light monitoring

    def _run_subroutine(self, check_name: str, context: MonitoringContext, result: MonitoringResult):
        """Run specific monitoring subroutine"""

        if check_name == 'size_check':
            self._check_file_sizes(context, result)
        elif check_name == 'duplicate_check':
            self._check_duplicates(context, result)
        elif check_name == 'structure_check':
            self._check_module_structure(context, result)
        elif check_name == 'pattern_analysis':
            self._analyze_patterns(context, result)
        elif check_name == 'agent_behavior':
            self._monitor_agent_behavior(context, result)

    def _check_file_sizes(self, context: MonitoringContext, result: MonitoringResult):
        """Intelligent file size checking"""
        for file_path in context.file_paths[:10]:  # Check top 10 files
            if not os.path.exists(file_path):
                continue

            try:
                # Use subprocess for fast line counting
                line_count = int(subprocess.check_output(
                    ['wc', '-l', file_path],
                    universal_newlines=True,
                    stderr=subprocess.DEVNULL
                ).split()[0])

                if line_count > 800:
                    severity = 'CRITICAL' if line_count > 1000 else 'WARNING'
                    result.size_issues.append({
                        'file': file_path,
                        'lines': line_count,
                        'severity': severity,
                        'action': f"Refactor {Path(file_path).name} ({line_count} lines)"
                    })

                    # Add to health warnings for display
                    result.health_warnings.append(
                        f"[WSP 87] {severity}: {Path(file_path).name} has {line_count} lines"
                    )

            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to Python line counting
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        line_count = sum(1 for _ in f)
                        if line_count > 800:
                            result.size_issues.append({
                                'file': file_path,
                                'lines': line_count,
                                'severity': 'WARNING'
                            })
                except:
                    pass

    def _check_duplicates(self, context: MonitoringContext, result: MonitoringResult):
        """Intelligent duplicate detection using fingerprinting"""

        # Build function fingerprints from search results
        function_fingerprints = defaultdict(list)

        for hit in context.search_results:
            if hit.get('function') and hit.get('content'):
                # Create fingerprint from function signature
                content = hit['content'][:200]  # First 200 chars
                fingerprint = hashlib.md5(
                    re.sub(r'\s+', '', content).encode()
                ).hexdigest()[:8]

                function_fingerprints[fingerprint].append({
                    'function': hit['function'],
                    'file': hit.get('file', 'unknown'),
                    'module': hit.get('module', 'unknown')
                })

        # Detect duplicates
        for fingerprint, functions in function_fingerprints.items():
            if len(functions) > 1:
                result.duplicates_found.append({
                    'fingerprint': fingerprint,
                    'instances': functions,
                    'severity': 'HIGH' if len(functions) > 2 else 'MEDIUM'
                })

                # Add warning
                func_names = [f['function'] for f in functions]
                result.health_warnings.append(
                    f"[WSP 84] Duplicate pattern detected: {', '.join(func_names[:3])}"
                )

    def _check_module_structure(self, context: MonitoringContext, result: MonitoringResult):
        """Check WSP 49 compliance for touched modules"""

        required_structure = ['README.md', 'INTERFACE.md', 'ModLog.md', 'tests/', 'src/']

        for module_path in context.modules_touched[:5]:  # Check top 5 modules
            if not os.path.exists(module_path):
                continue

            missing = []
            for required in required_structure:
                full_path = os.path.join(module_path, required)
                if not os.path.exists(full_path):
                    missing.append(required)

            if missing:
                result.structure_violations.append(
                    f"{Path(module_path).name}: Missing {', '.join(missing)}"
                )
                result.health_warnings.append(
                    f"[WSP 49] {Path(module_path).name} missing: {', '.join(missing[:2])}"
                )

    def _analyze_patterns(self, context: MonitoringContext, result: MonitoringResult):
        """Detect and suggest patterns for extraction"""

        # Analyze search result patterns
        pattern_candidates = defaultdict(int)

        for hit in context.search_results:
            # Look for pattern indicators in content
            content = hit.get('content', '')
            if 'pattern' in content.lower() or 'template' in content.lower():
                pattern_candidates['explicit_pattern'] += 1

            # Check for repeated code structures
            if 'def ' in content and content.count('def ') > 1:
                pattern_candidates['multi_function'] += 1

            if 'class ' in content:
                pattern_candidates['class_pattern'] += 1

        # Generate suggestions
        if pattern_candidates:
            top_pattern = max(pattern_candidates, key=pattern_candidates.get)
            result.optimization_suggestions.append(
                f"Pattern opportunity: {top_pattern} detected {pattern_candidates[top_pattern]} times"
            )

    def _monitor_agent_behavior(self, context: MonitoringContext, result: MonitoringResult):
        """Monitor agent for vibecoding and WSP compliance"""

        if not context.agent_actions:
            return

        # Analyze action sequence
        action_sequence = ' '.join(context.agent_actions)

        # Vibecoding detection
        if 'file_create' in action_sequence and 'search' not in action_sequence:
            result.health_warnings.append(
                "[WSP 50] Vibecoding risk: Creating files without searching first"
            )
            result.metadata['vibecode_risk'] = 'HIGH'

        # Pattern detection
        action_types = [a.split(':')[0] for a in context.agent_actions if ':' in a]
        if action_types:
            most_common = max(set(action_types), key=action_types.count)
            if action_types.count(most_common) > 3:
                result.optimization_suggestions.append(
                    f"Agent pattern detected: {most_common} repeated {action_types.count(most_common)} times"
                )

        # WSP compliance check
        if 'wsp_violation' in action_sequence.lower():
            result.health_warnings.append(
                "[WSP 64] WSP violation detected in agent behavior"
            )

    def _extract_context_paths(self, context: MonitoringContext):
        """Extract file paths and modules from search results"""

        for hit in context.search_results:
            # Extract file paths
            if 'file' in hit:
                context.file_paths.append(hit['file'])

                # Extract module path
                module_path = self._get_module_path(hit['file'])
                if module_path and module_path not in context.modules_touched:
                    context.modules_touched.append(module_path)

    def _get_module_path(self, file_path: str) -> Optional[str]:
        """Extract module root path from file path"""
        path_parts = Path(file_path).parts

        # Look for module indicators
        for i, part in enumerate(path_parts):
            if part == 'modules' and i + 2 < len(path_parts):
                # modules/domain/module_name
                return str(Path(*path_parts[:i+3]))
            elif part == 'src' or part == 'tests':
                # Back up to module root
                return str(Path(*path_parts[:i]))

        return None

    def _is_module_cached(self, module_path: str) -> bool:
        """Check if module structure is already cached"""
        return module_path in self.check_cache

    def _add_intelligent_insights(self, context: MonitoringContext, result: MonitoringResult):
        """Add intelligent insights based on combined monitoring results"""

        # Combine insights
        if result.size_issues and result.duplicates_found:
            result.optimization_suggestions.append(
                "Consider refactoring large files and consolidating duplicates together"
            )

        if result.structure_violations and 'create' in context.query.lower():
            result.optimization_suggestions.append(
                "Ensure new code follows WSP 49 structure from the start"
            )

        # Risk assessment
        risk_score = 0
        risk_score += len(result.size_issues) * 2
        risk_score += len(result.duplicates_found) * 3
        risk_score += len(result.structure_violations)

        if risk_score > 5:
            result.metadata['overall_risk'] = 'HIGH'
            result.health_warnings.insert(0,
                f"[HEALTH] High risk score ({risk_score}): Review warnings before proceeding"
            )
        elif risk_score > 2:
            result.metadata['overall_risk'] = 'MEDIUM'

        # Success tracking
        if not result.health_warnings:
            result.metadata['health_status'] = 'EXCELLENT'


# Integration with HoloIndex search flow
def monitor_search_context(query: str, search_results: List[Dict],
                          agent_actions: Optional[List[str]] = None) -> MonitoringResult:
    """
    Main entry point for intelligent monitoring.
    Called automatically by HoloIndex during search operations.
    """
    monitor = IntelligentMonitor()

    context = MonitoringContext(
        query=query,
        search_results=search_results,
        agent_actions=agent_actions or []
    )

    return monitor.monitor(context)


if __name__ == "__main__":
    # Test the intelligent monitor

    # Simulate a search context
    test_context = MonitoringContext(
        query="create new authentication module for large system",
        search_results=[
            {'function': 'authenticate', 'file': 'modules/auth/src/auth.py', 'content': 'def authenticate()...'},
            {'function': 'authenticate', 'file': 'modules/user/src/login.py', 'content': 'def authenticate()...'},
            {'function': 'validate', 'file': 'modules/auth/src/auth.py', 'content': 'def validate()...'},
        ],
        agent_actions=['search:auth', 'file_create:new', 'search:auth', 'file_create:new']
    )

    monitor = IntelligentMonitor()
    result = monitor.monitor(test_context)

    print("Intelligent Monitoring Results:")
    print(f"Health Warnings: {len(result.health_warnings)}")
    for warning in result.health_warnings:
        print(f"  - {warning}")

    print(f"\nDuplicates Found: {len(result.duplicates_found)}")
    print(f"Size Issues: {len(result.size_issues)}")
    print(f"Structure Violations: {len(result.structure_violations)}")

    print(f"\nOptimization Suggestions:")
    for suggestion in result.optimization_suggestions:
        print(f"  - {suggestion}")

    print(f"\nMetadata: {result.metadata}")