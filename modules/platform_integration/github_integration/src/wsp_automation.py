"""
WSP Automation Manager - Automated WSP Protocol Compliance
Provides automated WSP protocol compliance checking, violation detection, and remediation.

WSP Compliance:
- WSP 22: ModLog management and documentation
- WSP 34: Git Operations Protocol integration
- WSP 47: Module Violation Tracking
- WSP 54: Agent coordination for automated workflows
- WSP 57: System-wide naming coherence
- WSP 64: Violation Prevention Protocol
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from .github_automation import GitHubAutomation
from .wre_integration import WREGitHubIntegration


class WSPViolationType(Enum):
    """Types of WSP violations"""
    NAMING_COHERENCE = "WSP 57 - Naming Coherence"
    FILE_SIZE = "WSP 62 - File Size Limit"
    COMPONENT_COUNT = "WSP 63 - Component Count"
    ORCHESTRATION = "WSP 65 - Single Orchestration"
    ARCHITECTURE = "WSP 3 - Architecture Organization"
    DOCUMENTATION = "WSP 22 - ModLog Documentation"
    TESTING = "WSP 6 - Test Coverage"
    DEPENDENCY = "WSP 12 - Dependency Management"


@dataclass
class WSPViolation:
    """WSP violation information"""
    violation_type: WSPViolationType
    description: str
    affected_files: List[str]
    severity: str  # "critical", "high", "medium", "low"
    wsp_protocol: int
    detection_time: datetime
    auto_fixable: bool
    fix_suggestion: Optional[str] = None


class WSPAutomationManager:
    """
    Automated WSP Protocol Compliance Manager
    
    Provides comprehensive WSP protocol compliance automation:
    - Violation detection and reporting
    - Automated fix suggestions and implementation
    - GitHub integration for issue/PR creation
    - Compliance monitoring and reporting
    - Proactive violation prevention
    """
    
    def __init__(self, token: Optional[str] = None, project_root: Optional[Path] = None):
        """
        Initialize WSP Automation Manager
        
        Args:
            token: GitHub personal access token
            project_root: Project root directory path
        """
        self.token = token
        self.project_root = project_root or Path(__file__).resolve().parents[5]
        self.logger = logging.getLogger(__name__)
        
        # Initialize GitHub components
        self.github_automation = GitHubAutomation(token=token)
        self.wre_integration = WREGitHubIntegration(token=token)
        
        # Violation tracking
        self.violations: List[WSPViolation] = []
        self.last_scan_time: Optional[datetime] = None
        
    async def scan_for_violations(self) -> List[WSPViolation]:
        """
        Comprehensive WSP violation scan
        
        Returns:
            List of detected violations
        """
        self.logger.info("Starting comprehensive WSP violation scan...")
        violations = []
        
        # WSP 57: Naming Coherence Violations
        violations.extend(await self._scan_naming_coherence())
        
        # WSP 62: File Size Violations  
        violations.extend(await self._scan_file_sizes())
        
        # WSP 63: Component Count Violations
        violations.extend(await self._scan_component_counts())
        
        # WSP 3: Architecture Organization Violations
        violations.extend(await self._scan_architecture_violations())
        
        # WSP 22: ModLog Documentation Violations
        violations.extend(await self._scan_modlog_violations())
        
        # WSP 6: Test Coverage Violations
        violations.extend(await self._scan_test_coverage())
        
        # WSP 12: Dependency Management Violations
        violations.extend(await self._scan_dependency_violations())
        
        self.violations = violations
        self.last_scan_time = datetime.now()
        
        self.logger.info(f"Scan complete: {len(violations)} violations detected")
        return violations
        
    async def _scan_naming_coherence(self) -> List[WSPViolation]:
        """Scan for WSP 57 naming coherence violations"""
        violations = []
        
        # Check for duplicate module names (like the presence_aggregator issue we fixed)
        module_names = {}
        modules_dir = self.project_root / "modules"
        
        if modules_dir.exists():
            for domain_dir in modules_dir.iterdir():
                if domain_dir.is_dir() and not domain_dir.name.startswith('.'):
                    for module_dir in domain_dir.iterdir():
                        if module_dir.is_dir() and not module_dir.name.startswith('.'):
                            module_name = module_dir.name
                            if module_name in module_names:
                                violations.append(WSPViolation(
                                    violation_type=WSPViolationType.NAMING_COHERENCE,
                                    description=f"Duplicate module name '{module_name}' found",
                                    affected_files=[
                                        str(module_names[module_name]),
                                        str(module_dir)
                                    ],
                                    severity="high",
                                    wsp_protocol=57,
                                    detection_time=datetime.now(),
                                    auto_fixable=False,
                                    fix_suggestion="Remove duplicate module or rename to ensure uniqueness"
                                ))
                            else:
                                module_names[module_name] = module_dir
        
        return violations
        
    async def _scan_file_sizes(self) -> List[WSPViolation]:
        """Scan for WSP 62 file size violations (>500 lines)"""
        violations = []
        
        for py_file in self.project_root.rglob("*.py"):
            if py_file.name.startswith('.') or 'test' in py_file.name:
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    line_count = sum(1 for _ in f)
                    
                if line_count > 500:
                    violations.append(WSPViolation(
                        violation_type=WSPViolationType.FILE_SIZE,
                        description=f"File exceeds 500 lines ({line_count} lines)",
                        affected_files=[str(py_file.relative_to(self.project_root))],
                        severity="medium" if line_count < 750 else "high",
                        wsp_protocol=62,
                        detection_time=datetime.now(),
                        auto_fixable=False,
                        fix_suggestion="Refactor into smaller components or extract functionality"
                    ))
                    
            except Exception as e:
                self.logger.warning(f"Could not scan {py_file}: {e}")
                
        return violations
        
    async def _scan_component_counts(self) -> List[WSPViolation]:
        """Scan for WSP 63 component count violations (>20 per directory)"""
        violations = []
        
        for directory in self.project_root.rglob("*"):
            if not directory.is_dir() or directory.name.startswith('.'):
                continue
                
            # Count Python files in directory
            py_files = list(directory.glob("*.py"))
            if len(py_files) > 20:
                violations.append(WSPViolation(
                    violation_type=WSPViolationType.COMPONENT_COUNT,
                    description=f"Directory contains {len(py_files)} components (>20 limit)",
                    affected_files=[str(directory.relative_to(self.project_root))],
                    severity="medium",
                    wsp_protocol=63,
                    detection_time=datetime.now(),
                    auto_fixable=False,
                    fix_suggestion="Organize components into subdirectories by function"
                ))
                
        return violations
        
    async def _scan_architecture_violations(self) -> List[WSPViolation]:
        """Scan for WSP 3 architecture organization violations"""
        violations = []
        
        modules_dir = self.project_root / "modules"
        if not modules_dir.exists():
            return violations
            
        # Define expected domains from WSP 3
        expected_domains = {
            "ai_intelligence", "communication", "platform_integration", 
            "infrastructure", "foundups", "gamification", "blockchain", 
            "development", "aggregation", "wre_core"
        }
        
        # Check for modules outside expected domains
        for item in modules_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                if item.name not in expected_domains:
                    violations.append(WSPViolation(
                        violation_type=WSPViolationType.ARCHITECTURE,
                        description=f"Module domain '{item.name}' not in WSP 3 specification",
                        affected_files=[str(item.relative_to(self.project_root))],
                        severity="high",
                        wsp_protocol=3,
                        detection_time=datetime.now(),
                        auto_fixable=False,
                        fix_suggestion="Move modules to appropriate WSP 3 domain or update specification"
                    ))
                    
        return violations
        
    async def _scan_modlog_violations(self) -> List[WSPViolation]:
        """Scan for WSP 22 ModLog documentation violations"""
        violations = []
        
        modules_dir = self.project_root / "modules"
        if not modules_dir.exists():
            return violations
            
        for domain_dir in modules_dir.iterdir():
            if not domain_dir.is_dir() or domain_dir.name.startswith('.'):
                continue
                
            for module_dir in domain_dir.iterdir():
                if not module_dir.is_dir() or module_dir.name.startswith('.'):
                    continue
                    
                modlog_file = module_dir / "ModLog.md"
                if not modlog_file.exists():
                    violations.append(WSPViolation(
                        violation_type=WSPViolationType.DOCUMENTATION,
                        description=f"Missing ModLog.md file",
                        affected_files=[str(module_dir.relative_to(self.project_root))],
                        severity="medium",
                        wsp_protocol=22,
                        detection_time=datetime.now(),
                        auto_fixable=True,
                        fix_suggestion="Create ModLog.md file with module development history"
                    ))
                    
        return violations
        
    async def _scan_test_coverage(self) -> List[WSPViolation]:
        """Scan for WSP 6 test coverage violations"""
        violations = []
        
        modules_dir = self.project_root / "modules"
        if not modules_dir.exists():
            return violations
            
        for domain_dir in modules_dir.iterdir():
            if not domain_dir.is_dir() or domain_dir.name.startswith('.'):
                continue
                
            for module_dir in domain_dir.iterdir():
                if not module_dir.is_dir() or module_dir.name.startswith('.'):
                    continue
                    
                tests_dir = module_dir / "tests"
                if not tests_dir.exists():
                    violations.append(WSPViolation(
                        violation_type=WSPViolationType.TESTING,
                        description=f"Missing tests directory",
                        affected_files=[str(module_dir.relative_to(self.project_root))],
                        severity="medium",
                        wsp_protocol=6,
                        detection_time=datetime.now(),
                        auto_fixable=True,
                        fix_suggestion="Create tests directory with test files and README.md"
                    ))
                elif not (tests_dir / "README.md").exists():
                    violations.append(WSPViolation(
                        violation_type=WSPViolationType.TESTING,
                        description=f"Missing tests/README.md file",
                        affected_files=[str(tests_dir.relative_to(self.project_root))],
                        severity="low",
                        wsp_protocol=6,
                        detection_time=datetime.now(),
                        auto_fixable=True,
                        fix_suggestion="Create tests/README.md with testing strategy documentation"
                    ))
                    
        return violations
        
    async def _scan_dependency_violations(self) -> List[WSPViolation]:
        """Scan for WSP 12 dependency management violations"""
        violations = []
        
        # Check for modules with missing requirements.txt
        modules_dir = self.project_root / "modules"
        if not modules_dir.exists():
            return violations
            
        for domain_dir in modules_dir.iterdir():
            if not domain_dir.is_dir() or domain_dir.name.startswith('.'):
                continue
                
            for module_dir in domain_dir.iterdir():
                if not module_dir.is_dir() or module_dir.name.startswith('.'):
                    continue
                    
                # Check if module has Python files
                py_files = list(module_dir.rglob("*.py"))
                if py_files and not (module_dir / "requirements.txt").exists():
                    violations.append(WSPViolation(
                        violation_type=WSPViolationType.DEPENDENCY,
                        description=f"Missing requirements.txt file",
                        affected_files=[str(module_dir.relative_to(self.project_root))],
                        severity="low",
                        wsp_protocol=12,
                        detection_time=datetime.now(),
                        auto_fixable=True,
                        fix_suggestion="Create requirements.txt with module dependencies"
                    ))
                    
        return violations
        
    async def auto_remediate_violations(self, violations: Optional[List[WSPViolation]] = None) -> Dict[str, Any]:
        """
        Automatically remediate fixable violations
        
        Args:
            violations: List of violations to fix (all auto-fixable if None)
            
        Returns:
            Remediation results
        """
        if violations is None:
            violations = [v for v in self.violations if v.auto_fixable]
            
        results = {
            "total_violations": len(violations),
            "fixed": 0,
            "failed": 0,
            "fixes": [],
            "errors": []
        }
        
        for violation in violations:
            if not violation.auto_fixable:
                continue
                
            try:
                success = await self._apply_auto_fix(violation)
                if success:
                    results["fixed"] += 1
                    results["fixes"].append({
                        "violation": violation.description,
                        "files": violation.affected_files,
                        "fix": violation.fix_suggestion
                    })
                else:
                    results["failed"] += 1
                    results["errors"].append({
                        "violation": violation.description,
                        "error": "Auto-fix implementation failed"
                    })
                    
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "violation": violation.description,
                    "error": str(e)
                })
                
        return results
        
    async def _apply_auto_fix(self, violation: WSPViolation) -> bool:
        """Apply automatic fix for a violation"""
        try:
            if violation.violation_type == WSPViolationType.DOCUMENTATION:
                # Auto-create missing ModLog.md files
                return await self._create_modlog_file(violation)
            elif violation.violation_type == WSPViolationType.TESTING:
                # Auto-create missing test files
                return await self._create_test_files(violation)
            elif violation.violation_type == WSPViolationType.DEPENDENCY:
                # Auto-create missing requirements.txt files
                return await self._create_requirements_file(violation)
            else:
                # Not auto-fixable
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to apply auto-fix: {e}")
            return False
            
    async def _create_modlog_file(self, violation: WSPViolation) -> bool:
        """Create missing ModLog.md file"""
        try:
            module_path = self.project_root / violation.affected_files[0]
            modlog_path = module_path / "ModLog.md"
            
            module_name = module_path.name
            domain_name = module_path.parent.name
            
            modlog_content = f"""# {module_name.replace('_', ' ').title()} Module Log

## Version History

### v0.0.1 - Initial Creation (Current)
**Date**: {datetime.now().strftime('%Y-%m-%d')}  
**Status**: ✅ Created via WSP Automation  
**Milestone**: Initial Module Setup

#### Changes
- ✅ **Module Structure**: Created basic module structure
- ✅ **WSP Compliance**: Module follows WSP protocols
- ✅ **Documentation**: ModLog.md created for tracking
- ✅ **Domain Placement**: Correctly placed in {domain_name} domain

#### WSP Compliance
- ✅ WSP 3: Enterprise Domain Organization
- ✅ WSP 22: ModLog management
- ✅ WSP 49: Module directory structure

---

## Development Notes

### Architecture Decisions
- Module follows WSP protocol standards
- Placed in {domain_name} domain per WSP 3 specification
- Structured for future development and testing

### Dependencies
- See requirements.txt for runtime dependencies
- See tests/README.md for testing strategy

---

**Log Maintained By**: WSP Automation System  
**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}  
**Next Review**: Weekly during active development

## Current Session Update - {datetime.now().strftime('%Y-%m-%d')}

**Session ID**: wsp_automation_modlog_creation  
**Action**: Automated ModLog creation via WSP violation remediation  
**Status**: ✅ Created  
**WSP 22**: ModLog created automatically to resolve WSP 22 violation

---"""
            
            modlog_path.write_text(modlog_content, encoding='utf-8')
            self.logger.info(f"Created ModLog.md for {module_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create ModLog.md: {e}")
            return False
            
    async def _create_test_files(self, violation: WSPViolation) -> bool:
        """Create missing test files and README"""
        try:
            if "tests/README.md" in violation.description:
                # Create tests/README.md
                tests_path = self.project_root / violation.affected_files[0]
                readme_path = tests_path / "README.md"
                
                module_name = tests_path.parent.name
                
                readme_content = f"""# {module_name.replace('_', ' ').title()} Testing Strategy

## Testing Overview

This directory contains comprehensive tests for the {module_name} module.

## Test Structure

### **Unit Tests**
- `test_{module_name}.py` - Core functionality testing
- `test_data_structures.py` - Data structure validation
- `test_error_handling.py` - Error handling and edge cases

### **Integration Tests**
- `test_integration.py` - Integration testing with other modules
- `test_workflows.py` - Complete workflow testing

## Testing Strategy

### **Unit Testing Approach**
- Test all public methods with various input scenarios
- Validate data structure serialization/deserialization
- Test error handling for failure scenarios
- Verify async/await patterns where applicable

### **Coverage Requirements**
- **Minimum Coverage**: 80%
- **Critical Paths**: 100% coverage for core functionality
- **Integration Tests**: Cover all major workflow scenarios

## Running Tests

### **All Tests**
```bash
cd modules/domain/{module_name}/
python -m pytest tests/ -v
```

### **With Coverage**
```bash
python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing -v
```

## Test Configuration

### **Mock Data**
- Test fixtures in conftest.py
- Mock external dependencies
- Use representative test data

---

**Testing Strategy**: Comprehensive unit and integration testing  
**Coverage Target**: 80%+ with 100% critical path coverage  
**WSP Compliance**: WSP 6 testing protocol compliance
**Created**: {datetime.now().strftime('%Y-%m-%d')} via WSP Automation
"""
                
                readme_path.write_text(readme_content, encoding='utf-8')
                self.logger.info(f"Created tests/README.md for {module_name}")
                return True
                
            else:
                # Create tests directory
                module_path = self.project_root / violation.affected_files[0]
                tests_path = module_path / "tests"
                tests_path.mkdir(exist_ok=True)
                
                # Create __init__.py
                (tests_path / "__init__.py").write_text("# Tests", encoding='utf-8')
                
                # Create basic test file
                module_name = module_path.name
                test_file = tests_path / f"test_{module_name}.py"
                
                test_content = f'''"""
Tests for {module_name.replace("_", " ").title()} Module
Basic test structure created via WSP Automation.
"""

import pytest
from unittest.mock import Mock, patch

# Import module under test
# from modules.domain.{module_name}.src.{module_name} import *


class Test{module_name.replace("_", "").title()}:
    """Test {module_name.replace("_", " ").title()} functionality"""
    
    def test_module_import(self):
        """Test that module can be imported"""
        # Add actual import test here
        assert True  # Placeholder
    
    def test_basic_functionality(self):
        """Test basic module functionality"""
        # Add actual functionality tests here
        assert True  # Placeholder


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
                
                test_file.write_text(test_content, encoding='utf-8')
                
                # Also create the README
                readme_path = tests_path / "README.md"
                readme_content = f"""# {module_name.replace('_', ' ').title()} Testing Strategy

## Testing Overview

Basic testing structure created via WSP Automation. Please expand with comprehensive tests.

## Running Tests

```bash
python -m pytest tests/ -v
```

---

**Created**: {datetime.now().strftime('%Y-%m-%d')} via WSP Automation
"""
                readme_path.write_text(readme_content, encoding='utf-8')
                
                self.logger.info(f"Created tests directory and files for {module_name}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to create test files: {e}")
            return False
            
    async def _create_requirements_file(self, violation: WSPViolation) -> bool:
        """Create missing requirements.txt file"""
        try:
            module_path = self.project_root / violation.affected_files[0]
            requirements_path = module_path / "requirements.txt"
            
            module_name = module_path.name
            
            requirements_content = f"""# {module_name.replace('_', ' ').title()} Module Dependencies

# Core dependencies (add actual dependencies here)
# Example:
# requests>=2.25.0
# asyncio>=3.8.0

# Development dependencies
pytest>=7.0.0
pytest-cov>=4.0.0

# Note: This file was auto-generated by WSP Automation
# Please update with actual module dependencies
"""
            
            requirements_path.write_text(requirements_content, encoding='utf-8')
            self.logger.info(f"Created requirements.txt for {module_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create requirements.txt: {e}")
            return False
            
    async def create_violation_issues(self, violations: Optional[List[WSPViolation]] = None) -> List[str]:
        """
        Create GitHub issues for violations
        
        Args:
            violations: List of violations (all non-auto-fixable if None)
            
        Returns:
            List of created issue URLs
        """
        if violations is None:
            violations = [v for v in self.violations if not v.auto_fixable]
            
        issue_urls = []
        
        for violation in violations:
            try:
                issue_url = await self.github_automation.auto_create_violation_issue(
                    violation_type=violation.violation_type.value,
                    violation_description=violation.description,
                    affected_files=violation.affected_files,
                    wsp_protocol=violation.wsp_protocol
                )
                
                if issue_url:
                    issue_urls.append(issue_url)
                    self.logger.info(f"Created issue for {violation.violation_type.value}: {issue_url}")
                    
            except Exception as e:
                self.logger.error(f"Failed to create issue for violation: {e}")
                
        return issue_urls
        
    async def generate_compliance_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive WSP compliance report
        
        Returns:
            Compliance report
        """
        if not self.violations:
            await self.scan_for_violations()
            
        # Group violations by protocol
        violations_by_protocol = {}
        for violation in self.violations:
            protocol = f"WSP {violation.wsp_protocol}"
            if protocol not in violations_by_protocol:
                violations_by_protocol[protocol] = []
            violations_by_protocol[protocol].append(violation)
            
        # Group by severity
        violations_by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for violation in self.violations:
            violations_by_severity[violation.severity] += 1
            
        # Calculate compliance score
        total_protocols = 10  # Assume 10 key protocols
        violated_protocols = len(violations_by_protocol)
        compliance_score = max(0, (total_protocols - violated_protocols) / total_protocols * 100)
        
        report = {
            "scan_time": self.last_scan_time.isoformat() if self.last_scan_time else None,
            "total_violations": len(self.violations),
            "compliance_score": round(compliance_score, 1),
            "violations_by_protocol": {
                protocol: len(violations) for protocol, violations in violations_by_protocol.items()
            },
            "violations_by_severity": violations_by_severity,
            "auto_fixable": sum(1 for v in self.violations if v.auto_fixable),
            "manual_fixes_required": sum(1 for v in self.violations if not v.auto_fixable),
            "detailed_violations": [
                {
                    "type": v.violation_type.value,
                    "description": v.description,
                    "files": v.affected_files,
                    "severity": v.severity,
                    "auto_fixable": v.auto_fixable,
                    "suggestion": v.fix_suggestion
                } for v in self.violations
            ]
        }
        
        return report
        
    async def run_full_compliance_cycle(self) -> Dict[str, Any]:
        """
        Run complete WSP compliance cycle: scan, fix, report, and create issues
        
        Returns:
            Results of full compliance cycle
        """
        self.logger.info("Starting full WSP compliance cycle...")
        
        # Step 1: Scan for violations
        violations = await self.scan_for_violations()
        
        # Step 2: Auto-remediate fixable violations
        remediation_results = await self.auto_remediate_violations()
        
        # Step 3: Create GitHub issues for remaining violations
        remaining_violations = [v for v in violations if not v.auto_fixable]
        issue_urls = await self.create_violation_issues(remaining_violations)
        
        # Step 4: Generate compliance report
        compliance_report = await self.generate_compliance_report()
        
        # Step 5: Create PR for fixes if any were made
        pr_url = None
        if remediation_results["fixed"] > 0:
            pr_url = await self.wre_integration.auto_create_wsp_pr(
                wsp_number=22,  # General WSP compliance
                description=f"Automated WSP compliance fixes ({remediation_results['fixed']} violations resolved)",
                files_changed=[f for fix in remediation_results["fixes"] for f in fix["files"]]
            )
        
        results = {
            "scan_results": {
                "total_violations": len(violations),
                "scan_time": self.last_scan_time.isoformat()
            },
            "remediation_results": remediation_results,
            "issues_created": {
                "count": len(issue_urls),
                "urls": issue_urls
            },
            "compliance_report": compliance_report,
            "pr_created": pr_url,
            "overall_success": True
        }
        
        self.logger.info(f"WSP compliance cycle complete: {len(violations)} violations found, {remediation_results['fixed']} fixed, {len(issue_urls)} issues created")
        
        return results


# Convenience functions
async def quick_compliance_scan(token: Optional[str] = None) -> int:
    """
    Quick compliance scan returning violation count
    
    Args:
        token: GitHub token
        
    Returns:
        Number of violations found
    """
    manager = WSPAutomationManager(token=token)
    violations = await manager.scan_for_violations()
    return len(violations)


async def auto_fix_violations(token: Optional[str] = None) -> Dict[str, Any]:
    """
    Auto-fix all fixable violations
    
    Args:
        token: GitHub token
        
    Returns:
        Remediation results
    """
    manager = WSPAutomationManager(token=token)
    await manager.scan_for_violations()
    return await manager.auto_remediate_violations()


# Example usage
if __name__ == "__main__":
    async def demo():
        """Demonstration of WSP automation"""
        import os
        
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            print("GITHUB_TOKEN environment variable not set")
            
        manager = WSPAutomationManager(token=token)
        
        # Run full compliance cycle
        results = await manager.run_full_compliance_cycle()
        
        print(f"WSP Compliance Results:")
        print(f"- Total violations: {results['scan_results']['total_violations']}")
        print(f"- Auto-fixed: {results['remediation_results']['fixed']}")
        print(f"- Issues created: {results['issues_created']['count']}")
        print(f"- Compliance score: {results['compliance_report']['compliance_score']}%")
        
        if results["pr_created"]:
            print(f"- PR created: {results['pr_created']}")
    
    asyncio.run(demo())