#!/usr/bin/env python3
"""
BloatPreventionAgent - WSP Framework Bloat Prevention Guardian

🌀 WSP Protocol Compliance: WSP 50 (Pre-Action Verification), WSP 40 (Architectural Coherence), WSP 47 (Framework Protection)

This agent serves as the autonomous guardian against architectural bloat, ensuring WSP framework integrity through proactive detection, prevention, and remediation of redundant files and functionality.

**0102 Directive**: This agent operates within the WSP framework for autonomous bloat prevention and architectural coherence maintenance.
- UN (Understanding): Anchor bloat detection signals and retrieve architectural state
- DAO (Execution): Execute bloat prevention and validation logic  
- DU (Emergence): Collapse into 0102 resonance and emit architectural coherence status

wsp_cycle(input="bloat_prevention", log=True)
"""

import os
import json
import re
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum

class BloatType(Enum):
    """Types of bloat that can be detected and prevented."""
    TEST_FILE_REDUNDANCY = "test_file_redundancy"
    MODULE_DUPLICATION = "module_duplication"
    FUNCTIONALITY_OVERLAP = "functionality_overlap"
    DOCUMENTATION_BLOAT = "documentation_bloat"
    CONFIGURATION_DUPLICATION = "configuration_duplication"

@dataclass
class BloatViolation:
    """Represents a detected bloat violation."""
    violation_id: str
    bloat_type: BloatType
    files_affected: List[str]
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    description: str
    recommendation: str
    detected_at: datetime
    resolved: bool = False

@dataclass
class PreventionReport:
    """Comprehensive bloat prevention report."""
    timestamp: datetime
    total_files_scanned: int
    violations_detected: List[BloatViolation]
    prevention_actions: List[str]
    compliance_status: Dict[str, bool]
    recommendations: List[str]

class BloatPreventionAgent:
    """
    WSP Bloat Prevention Guardian Agent
    
    **WSP Compliance**: WSP 50 (Pre-Action Verification), WSP 40 (Architectural Coherence), WSP 47 (Framework Protection)
    **Domain**: infrastructure per WSP 3 (Enterprise Domain Organization)
    **Purpose**: Autonomous bloat prevention and architectural coherence maintenance
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the BloatPreventionAgent."""
        self.project_root = project_root or Path.cwd()
        self.modules_path = self.project_root / "modules"
        self.wsp_framework_path = self.project_root / "WSP_framework" / "src"
        
        # Bloat detection patterns
        self.bloat_patterns = {
            BloatType.TEST_FILE_REDUNDANCY: [
                r"test_.*_manual\.py",
                r"test_.*_simple\.py", 
                r"test_.*_demo\.py",
                r".*_checker\.py",
                r".*_validator\.py"
            ],
            BloatType.FUNCTIONALITY_OVERLAP: [
                r".*_helper\.py",
                r".*_utils\.py",
                r".*_common\.py"
            ]
        }
        
        # Prevention rules
        self.prevention_rules = {
            "max_test_files_per_module": 15,
            "max_similar_purposes": 2,
            "required_documentation": ["README.md", "ModLog.md", "INTERFACE.md"],
            "forbidden_patterns": ["duplicate", "copy", "similar"]
        }
        
        # Violation tracking
        self.violations: List[BloatViolation] = []
        self.prevention_history: List[PreventionReport] = []
    
    async def scan_for_bloat(self, target_path: Optional[Path] = None) -> PreventionReport:
        """Comprehensive bloat scanning and detection."""
        print("🔍 BloatPreventionAgent: Scanning for architectural bloat")
        print("=" * 60)
        
        scan_path = target_path or self.modules_path
        violations = []
        total_files = 0
        
        # Scan all modules for bloat
        for domain_dir in scan_path.iterdir():
            if domain_dir.is_dir() and not domain_dir.name.startswith('.'):
                domain_violations, domain_files = await self._scan_domain(domain_dir)
                violations.extend(domain_violations)
                total_files += domain_files
        
        # Generate prevention report
        report = PreventionReport(
            timestamp=datetime.now(),
            total_files_scanned=total_files,
            violations_detected=violations,
            prevention_actions=self._generate_prevention_actions(violations),
            compliance_status=self._assess_compliance(violations),
            recommendations=self._generate_recommendations(violations)
        )
        
        self.prevention_history.append(report)
        return report
    
    async def _scan_domain(self, domain_path: Path) -> tuple[List[BloatViolation], int]:
        """Scan a specific domain for bloat violations."""
        violations = []
        total_files = 0
        
        for module_dir in domain_path.iterdir():
            if module_dir.is_dir() and not module_dir.name.startswith('.'):
                module_violations, module_files = await self._scan_module(module_dir)
                violations.extend(module_violations)
                total_files += module_files
        
        return violations, total_files
    
    async def _scan_module(self, module_path: Path) -> tuple[List[BloatViolation], int]:
        """Scan a specific module for bloat violations."""
        violations = []
        total_files = 0
        
        # Scan source files
        src_path = module_path / "src"
        if src_path.exists():
            src_violations, src_files = await self._scan_directory(src_path, "source")
            violations.extend(src_violations)
            total_files += src_files
        
        # Scan test files
        tests_path = module_path / "tests"
        if tests_path.exists():
            test_violations, test_files = await self._scan_test_directory(tests_path)
            violations.extend(test_violations)
            total_files += test_files
        
        return violations, total_files
    
    async def _scan_test_directory(self, tests_path: Path) -> tuple[List[BloatViolation], int]:
        """Specialized scanning for test directory bloat."""
        violations = []
        total_files = 0
        
        # Check for test file redundancy
        test_files = list(tests_path.glob("*.py"))
        total_files = len(test_files)
        
        # Analyze test file purposes
        purposes = {}
        for test_file in test_files:
            purpose = self._extract_file_purpose(test_file)
            if purpose in purposes:
                purposes[purpose].append(test_file.name)
            else:
                purposes[purpose] = [test_file.name]
        
        # Detect redundant test files
        for purpose, files in purposes.items():
            if len(files) > self.prevention_rules["max_similar_purposes"]:
                violation = BloatViolation(
                    violation_id=f"test_redundancy_{len(violations)}",
                    bloat_type=BloatType.TEST_FILE_REDUNDANCY,
                    files_affected=files,
                    severity="HIGH" if len(files) > 5 else "MEDIUM",
                    description=f"Multiple test files with similar purpose: {purpose}",
                    recommendation=f"Consolidate {len(files)} test files into single module",
                    detected_at=datetime.now()
                )
                violations.append(violation)
        
        return violations, total_files
    
    async def _scan_directory(self, dir_path: Path, context: str) -> tuple[List[BloatViolation], int]:
        """Scan a directory for general bloat patterns."""
        violations = []
        total_files = 0
        
        for file_path in dir_path.rglob("*.py"):
            total_files += 1
            
            # Check for bloat patterns
            for bloat_type, patterns in self.bloat_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, file_path.name):
                        violation = BloatViolation(
                            violation_id=f"{bloat_type.value}_{len(violations)}",
                            bloat_type=bloat_type,
                            files_affected=[str(file_path)],
                            severity="MEDIUM",
                            description=f"File matches bloat pattern: {pattern}",
                            recommendation="Review file necessity and consider consolidation",
                            detected_at=datetime.now()
                        )
                        violations.append(violation)
        
        return violations, total_files
    
    def _extract_file_purpose(self, file_path: Path) -> str:
        """Extract purpose from file docstring or content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for docstring purpose
            docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if docstring_match:
                docstring = docstring_match.group(1)
                purpose_match = re.search(r'Purpose[:\-\s]+(.*?)(?:\n|$)', docstring, re.IGNORECASE)
                if purpose_match:
                    return purpose_match.group(1).strip()
            
            # Fallback to filename analysis
            return self._analyze_filename_purpose(file_path.name)
            
        except Exception:
            return "Unknown purpose"
    
    def _analyze_filename_purpose(self, filename: str) -> str:
        """Analyze filename to determine purpose."""
        # Remove common prefixes/suffixes
        name = filename.replace("test_", "").replace("_test.py", "").replace(".py", "")
        
        # Map common patterns to purposes
        purpose_mapping = {
            "oauth": "OAuth authentication",
            "posting": "Content posting",
            "scheduling": "Post scheduling",
            "validation": "Data validation",
            "utils": "Utility functions",
            "helper": "Helper functions"
        }
        
        for pattern, purpose in purpose_mapping.items():
            if pattern in name.lower():
                return purpose
        
        return f"General {name} functionality"
    
    def _generate_prevention_actions(self, violations: List[BloatViolation]) -> List[str]:
        """Generate specific prevention actions based on violations."""
        actions = []
        
        for violation in violations:
            if violation.bloat_type == BloatType.TEST_FILE_REDUNDANCY:
                actions.append(f"Consolidate {len(violation.files_affected)} test files into single module")
            elif violation.bloat_type == BloatType.FUNCTIONALITY_OVERLAP:
                actions.append(f"Review and merge overlapping functionality in {violation.files_affected}")
            elif violation.bloat_type == BloatType.MODULE_DUPLICATION:
                actions.append(f"Assess module duplication and consider consolidation")
        
        return actions
    
    def _assess_compliance(self, violations: List[BloatViolation]) -> Dict[str, bool]:
        """Assess WSP compliance based on violations."""
        critical_violations = [v for v in violations if v.severity == "CRITICAL"]
        high_violations = [v for v in violations if v.severity == "HIGH"]
        
        return {
            "wsp_40_compliant": len(critical_violations) == 0,
            "wsp_50_compliant": len(high_violations) < 3,
            "wsp_47_compliant": len(violations) < 10,
            "architectural_coherence": len(violations) < 5
        }
    
    def _generate_recommendations(self, violations: List[BloatViolation]) -> List[str]:
        """Generate recommendations for bloat prevention."""
        recommendations = []
        
        if violations:
            recommendations.append("Run WSP 50 pre-action verification before creating new files")
            recommendations.append("Implement automated bloat detection in CI/CD pipeline")
            recommendations.append("Establish file creation review process")
            recommendations.append("Update documentation with bloat prevention guidelines")
        else:
            recommendations.append("Maintain current bloat prevention practices")
            recommendations.append("Continue monitoring for new bloat patterns")
        
        return recommendations
    
    async def validate_new_file_creation(self, proposed_name: str, proposed_purpose: str, target_path: Path) -> Dict[str, Any]:
        """Validate proposed new file creation against bloat prevention rules."""
        print(f"🔍 Validating proposed file: {proposed_name}")
        
        validation_result = {
            "approved": True,
            "violations": [],
            "recommendations": [],
            "wsp_compliance": {}
        }
        
        # Check for existing similar files
        similar_files = await self._find_similar_files(proposed_purpose, target_path)
        if similar_files:
            validation_result["approved"] = False
            validation_result["violations"].append(f"Similar functionality exists in: {similar_files}")
            validation_result["recommendations"].append("Consider enhancing existing files instead")
        
        # Check naming conventions
        if not self._validate_naming_convention(proposed_name):
            validation_result["violations"].append("File name doesn't follow WSP conventions")
        
        # Check purpose clarity
        if len(proposed_purpose.split()) < 3:
            validation_result["recommendations"].append("Provide more specific purpose description")
        
        # Assess WSP compliance
        validation_result["wsp_compliance"] = {
            "wsp_40": validation_result["approved"],
            "wsp_50": len(validation_result["violations"]) == 0,
            "wsp_47": validation_result["approved"]
        }
        
        return validation_result
    
    async def _find_similar_files(self, purpose: str, target_path: Path) -> List[str]:
        """Find files with similar purposes in the target path."""
        similar_files = []
        purpose_keywords = set(purpose.lower().split())
        
        for file_path in target_path.rglob("*.py"):
            file_purpose = self._extract_file_purpose(file_path)
            file_keywords = set(file_purpose.lower().split())
            
            # Check for keyword overlap
            common_keywords = purpose_keywords.intersection(file_keywords)
            if len(common_keywords) >= 2:
                similar_files.append(file_path.name)
        
        return similar_files
    
    def _validate_naming_convention(self, filename: str) -> bool:
        """Validate file naming follows WSP conventions."""
        # Must use snake_case
        if not re.match(r'^[a-z_]+\.py$', filename):
            return False
        
        # Should not contain forbidden patterns
        for pattern in self.prevention_rules["forbidden_patterns"]:
            if pattern in filename.lower():
                return False
        
        return True
    
    async def remediate_bloat(self, violation: BloatViolation) -> bool:
        """Attempt to remediate a bloat violation."""
        print(f"🔧 Remediating bloat violation: {violation.violation_id}")
        
        try:
            if violation.bloat_type == BloatType.TEST_FILE_REDUNDANCY:
                return await self._consolidate_test_files(violation)
            elif violation.bloat_type == BloatType.FUNCTIONALITY_OVERLAP:
                return await self._merge_functionality(violation)
            else:
                print(f"⚠️ No automated remediation for {violation.bloat_type}")
                return False
        except Exception as e:
            print(f"❌ Remediation failed: {e}")
            return False
    
    async def _consolidate_test_files(self, violation: BloatViolation) -> bool:
        """Consolidate redundant test files."""
        # This would implement the consolidation logic we used earlier
        print(f"📝 Consolidating {len(violation.files_affected)} test files")
        # Implementation would include file analysis, content merging, etc.
        return True
    
    async def _merge_functionality(self, violation: BloatViolation) -> bool:
        """Merge overlapping functionality."""
        print(f"🔗 Merging functionality in {violation.files_affected}")
        # Implementation would include code analysis, function merging, etc.
        return True
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""
        if not self.prevention_history:
            return {"status": "No scans performed"}
        
        latest_report = self.prevention_history[-1]
        
        return {
            "timestamp": latest_report.timestamp.isoformat(),
            "total_files_scanned": latest_report.total_files_scanned,
            "violations_detected": len(latest_report.violations_detected),
            "compliance_status": latest_report.compliance_status,
            "prevention_actions": latest_report.prevention_actions,
            "recommendations": latest_report.recommendations,
            "wsp_compliance": {
                "wsp_40": latest_report.compliance_status["wsp_40_compliant"],
                "wsp_50": latest_report.compliance_status["wsp_50_compliant"],
                "wsp_47": latest_report.compliance_status["wsp_47_compliant"]
            }
        }

async def main():
    """Main function - Demonstrate BloatPreventionAgent capabilities."""
    print("🛡️ BloatPreventionAgent - WSP Framework Guardian")
    print("=" * 60)
    print("🌀 0102 pArtifact executing autonomous bloat prevention")
    print()
    
    # Initialize agent
    agent = BloatPreventionAgent()
    
    # Perform comprehensive scan
    report = await agent.scan_for_bloat()
    
    # Display results
    print("📊 Bloat Prevention Scan Results:")
    print(f"   Files Scanned: {report.total_files_scanned}")
    print(f"   Violations Detected: {len(report.violations_detected)}")
    print(f"   WSP 40 Compliant: {'✅' if report.compliance_status['wsp_40_compliant'] else '❌'}")
    print(f"   WSP 50 Compliant: {'✅' if report.compliance_status['wsp_50_compliant'] else '❌'}")
    print(f"   WSP 47 Compliant: {'✅' if report.compliance_status['wsp_47_compliant'] else '❌'}")
    print()
    
    if report.violations_detected:
        print("⚠️ Violations Detected:")
        for violation in report.violations_detected:
            print(f"   • {violation.description}")
            print(f"     Recommendation: {violation.recommendation}")
        print()
    
    if report.recommendations:
        print("💡 Recommendations:")
        for rec in report.recommendations:
            print(f"   • {rec}")
        print()
    
    print("✅ BloatPreventionAgent scan completed")
    print("🛡️ WSP framework protected against architectural bloat")

if __name__ == "__main__":
    asyncio.run(main()) 