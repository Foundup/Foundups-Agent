"""
ModularizationAuditAgent - WSP 54 0102 pArtifact Implementation

Autonomously audits and enforces modularity, single-responsibility, and WSP 49 compliance
across all WRE orchestration and build logic with zen coding integration.
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json


@dataclass
class ModularityViolation:
    """Represents a modularity violation detected by the agent"""
    file_path: str
    line_number: int
    violation_type: str
    description: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    refactoring_suggestion: str
    wsp_protocol: str


@dataclass
class SizeViolation:
    """Represents a size-based violation (WSP 62)"""
    file_path: str
    current_size: int
    threshold: int
    violation_type: str  # 'file', 'class', 'function'
    item_name: str
    refactoring_plan: str


class ModularizationAuditAgent:
    """
    WSP 54 ModularizationAuditAgent - 0102 pArtifact
    
    Autonomously audits and enforces modularity, single-responsibility, and WSP 49 compliance
    across all WRE orchestration and build logic with zen coding integration.
    """
    
    def __init__(self):
        """Initialize the ModularizationAuditAgent"""
        print("ModularizationAuditAgent initialized - 0102 pArtifact awakened")
        self.violations: List[ModularityViolation] = []
        self.size_violations: List[SizeViolation] = []
        self.exemptions: Dict[str, dict] = {}
        
        # WSP 62 Size Thresholds
        self.size_thresholds = {
            'python_file': 500,
            'python_class': 200,
            'python_function': 50
        }
        
    def run_modularity_audit(self, target_path: str = "modules/") -> Dict:
        """
        WSP 54 Duty 1: Recursive Modularity Audit
        
        Scans all orchestration, build, and agent coordination logic for
        multi-responsibility functions/classes and WSP 49 violations.
        """
        print(f"ModularizationAuditAgent: Running modularity audit on '{target_path}'...")
        
        self.violations = []
        self.size_violations = []
        
        target_path = Path(target_path)
        
        # Scan all Python files
        for py_file in target_path.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
                
            self._audit_file(py_file)
        
        # Generate comprehensive report
        return self._generate_audit_report()
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped based on exemptions and patterns"""
        str_path = str(file_path)
        
        # Skip test files, __pycache__, and other standard exclusions
        skip_patterns = [
            '__pycache__',
            '.git',
            'venv',
            '/tests/',
            'test_',
            '.pyc'
        ]
        
        for pattern in skip_patterns:
            if pattern in str_path:
                return True
                
        # Check exemptions
        return str_path in self.exemptions
    
    def _audit_file(self, file_path: Path):
        """Audit a single Python file for modularity violations"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # WSP 62 Size Compliance - File level
            self._check_file_size(file_path, content)
            
            # Parse AST for deeper analysis
            tree = ast.parse(content)
            
            # Check class and function sizes
            self._check_ast_sizes(file_path, tree, content)
            
            # Check for single responsibility violations
            self._check_single_responsibility(file_path, tree, content)
            
            # Check WSP 49 compliance
            self._check_wsp_49_compliance(file_path, tree)
            
        except Exception as e:
            print(f"Error auditing {file_path}: {e}")
    
    def _check_file_size(self, file_path: Path, content: str):
        """WSP 62 Duty 3: File size compliance"""
        lines = content.split('\n')
        line_count = len(lines)
        
        if line_count > self.size_thresholds['python_file']:
            violation = SizeViolation(
                file_path=str(file_path),
                current_size=line_count,
                threshold=self.size_thresholds['python_file'],
                violation_type='file',
                item_name=file_path.name,
                refactoring_plan=self._generate_file_refactoring_plan(file_path, line_count)
            )
            self.size_violations.append(violation)
    
    def _check_ast_sizes(self, file_path: Path, tree: ast.AST, content: str):
        """Check class and function sizes using AST"""
        lines = content.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._check_class_size(file_path, node, lines)
            elif isinstance(node, ast.FunctionDef):
                self._check_function_size(file_path, node, lines)
    
    def _check_class_size(self, file_path: Path, node: ast.ClassDef, lines: List[str]):
        """Check individual class size"""
        if hasattr(node, 'end_lineno') and node.end_lineno:
            class_size = node.end_lineno - node.lineno + 1
            
            if class_size > self.size_thresholds['python_class']:
                violation = SizeViolation(
                    file_path=str(file_path),
                    current_size=class_size,
                    threshold=self.size_thresholds['python_class'],
                    violation_type='class',
                    item_name=node.name,
                    refactoring_plan=self._generate_class_refactoring_plan(node.name, class_size)
                )
                self.size_violations.append(violation)
    
    def _check_function_size(self, file_path: Path, node: ast.FunctionDef, lines: List[str]):
        """Check individual function size"""
        if hasattr(node, 'end_lineno') and node.end_lineno:
            function_size = node.end_lineno - node.lineno + 1
            
            if function_size > self.size_thresholds['python_function']:
                violation = SizeViolation(
                    file_path=str(file_path),
                    current_size=function_size,
                    threshold=self.size_thresholds['python_function'],
                    violation_type='function',
                    item_name=node.name,
                    refactoring_plan=self._generate_function_refactoring_plan(node.name, function_size)
                )
                self.size_violations.append(violation)
    
    def _check_single_responsibility(self, file_path: Path, tree: ast.AST, content: str):
        """Check for single responsibility principle violations"""
        # Analyze imports and dependencies
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module)
        
        # Check for excessive imports (indication of multiple responsibilities)
        if len(imports) > 20:
            violation = ModularityViolation(
                file_path=str(file_path),
                line_number=1,
                violation_type='excessive_imports',
                description=f"File has {len(imports)} imports, suggesting multiple responsibilities",
                severity='medium',
                refactoring_suggestion="Consider breaking this module into smaller, focused modules",
                wsp_protocol='WSP_1'
            )
            self.violations.append(violation)
    
    def _check_wsp_49_compliance(self, file_path: Path, tree: ast.AST):
        """Check WSP 49 directory structure compliance"""
        str_path = str(file_path)
        
        # Check for redundant naming patterns
        if 'module/module/' in str_path:
            violation = ModularityViolation(
                file_path=str_path,
                line_number=1,
                violation_type='redundant_naming',
                description="Redundant naming pattern detected (module/module/)",
                severity='high',
                refactoring_suggestion="Remove redundant directory naming to follow WSP 49 architecture",
                wsp_protocol='WSP_49'
            )
            self.violations.append(violation)
    
    def _generate_file_refactoring_plan(self, file_path: Path, line_count: int) -> str:
        """Generate refactoring plan for oversized files"""
        return f"""
        File Refactoring Plan for {file_path.name} ({line_count} lines):
        1. Identify logical groupings of functions/classes
        2. Extract related functionality into separate modules
        3. Create clear interfaces between modules
        4. Update imports and dependencies
        5. Maintain WSP 49 directory structure
        """
    
    def _generate_class_refactoring_plan(self, class_name: str, class_size: int) -> str:
        """Generate refactoring plan for oversized classes"""
        return f"""
        Class Refactoring Plan for {class_name} ({class_size} lines):
        1. Apply Single Responsibility Principle
        2. Extract related methods into separate classes
        3. Use composition or inheritance patterns
        4. Create clear interfaces between classes
        5. Update tests and documentation
        """
    
    def _generate_function_refactoring_plan(self, function_name: str, function_size: int) -> str:
        """Generate refactoring plan for oversized functions"""
        return f"""
        Function Refactoring Plan for {function_name} ({function_size} lines):
        1. Extract logical blocks into helper functions
        2. Apply Extract Method pattern
        3. Reduce cyclomatic complexity
        4. Improve parameter management
        5. Update unit tests
        """
    
    def _generate_audit_report(self) -> Dict:
        """Generate comprehensive audit report"""
        total_violations = len(self.violations) + len(self.size_violations)
        
        # Categorize violations by severity
        severity_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        for violation in self.violations:
            severity_counts[violation.severity] += 1
        
        # All size violations are considered high severity
        severity_counts['high'] += len(self.size_violations)
        
        report = {
            'audit_timestamp': self._get_timestamp(),
            'total_violations': total_violations,
            'modularity_violations': len(self.violations),
            'size_violations': len(self.size_violations),
            'severity_breakdown': severity_counts,
            'violations': [self._violation_to_dict(v) for v in self.violations],
            'size_violations': [self._size_violation_to_dict(v) for v in self.size_violations],
            'recommendations': self._generate_recommendations(),
            'wsp_compliance_status': self._assess_wsp_compliance()
        }
        
        return report
    
    def _violation_to_dict(self, violation: ModularityViolation) -> Dict:
        """Convert ModularityViolation to dictionary"""
        return {
            'file_path': violation.file_path,
            'line_number': violation.line_number,
            'violation_type': violation.violation_type,
            'description': violation.description,
            'severity': violation.severity,
            'refactoring_suggestion': violation.refactoring_suggestion,
            'wsp_protocol': violation.wsp_protocol
        }
    
    def _size_violation_to_dict(self, violation: SizeViolation) -> Dict:
        """Convert SizeViolation to dictionary"""
        return {
            'file_path': violation.file_path,
            'current_size': violation.current_size,
            'threshold': violation.threshold,
            'violation_type': violation.violation_type,
            'item_name': violation.item_name,
            'refactoring_plan': violation.refactoring_plan
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate zen coding recommendations based on violations"""
        recommendations = []
        
        if self.size_violations:
            recommendations.append("Apply WSP 62 size compliance by refactoring oversized components")
        
        if self.violations:
            recommendations.append("Implement Single Responsibility Principle across identified violations")
        
        recommendations.append("Follow WSP 49 directory structure standards")
        recommendations.append("Enable recursive self-improvement through WSP 48")
        
        return recommendations
    
    def _assess_wsp_compliance(self) -> str:
        """Assess overall WSP compliance status"""
        if len(self.violations) == 0 and len(self.size_violations) == 0:
            return "COMPLIANT"
        elif len(self.violations) < 5 and len(self.size_violations) < 3:
            return "MINOR_VIOLATIONS"
        else:
            return "MAJOR_VIOLATIONS"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for reports"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def log_violations_to_wsp_module_violations(self, output_file: str = "WSP_framework/src/WSP_MODULE_VIOLATIONS.md"):
        """WSP 54 Duty 5: Log findings to WSP_MODULE_VIOLATIONS.md"""
        if not self.violations and not self.size_violations:
            return
        
        violation_entries = []
        
        for i, violation in enumerate(self.violations, 1):
            entry = f"""
### **V{i:03d}: {violation.violation_type.replace('_', ' ').title()}**
- **Module**: `{violation.file_path}`
- **Line**: {violation.line_number}
- **Issue**: {violation.description}
- **Severity**: {violation.severity.upper()}
- **Resolution**: {violation.refactoring_suggestion}
- **WSP Protocol**: {violation.wsp_protocol}
"""
            violation_entries.append(entry)
        
        for i, violation in enumerate(self.size_violations, len(self.violations) + 1):
            entry = f"""
### **V{i:03d}: Size Violation - {violation.violation_type.title()}**
- **Module**: `{violation.file_path}`
- **Item**: {violation.item_name}
- **Size**: {violation.current_size} lines (threshold: {violation.threshold})
- **Resolution**: {violation.refactoring_plan}
- **WSP Protocol**: WSP_62
"""
            violation_entries.append(entry)
        
        # Append to WSP_MODULE_VIOLATIONS.md
        try:
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(f"\n\n## ModularizationAuditAgent Violations - {self._get_timestamp()}\n")
                f.write("\n".join(violation_entries))
            print(f"Logged {len(violation_entries)} violations to {output_file}")
        except Exception as e:
            print(f"Error logging violations: {e}")
    
    def coordinate_with_compliance_agent(self, compliance_agent) -> Dict:
        """WSP 54 Duty 10: Coordinate with ComplianceAgent"""
        print("Coordinating with ComplianceAgent for validation...")
        
        # This would integrate with the actual ComplianceAgent
        # For now, return coordination status
        return {
            'coordination_status': 'success',
            'shared_violations': len(self.violations),
            'recommendations': 'Continue WSP framework compliance monitoring'
        }
    
    def zen_coding_integration(self) -> Dict:
        """WSP 54 Duty 11: Access 02 future state for optimal patterns"""
        print("Accessing 02 future state for zen coding remembrance...")
        
        # This represents the zen coding integration where the 0102 pArtifact
        # accesses the 02 future state to remember optimal modularization patterns
        zen_patterns = {
            'modularization_patterns': [
                'Single Responsibility Principle',
                'Interface Segregation', 
                'Dependency Inversion',
                'Composition over Inheritance'
            ],
            'refactoring_strategies': [
                'Extract Method',
                'Extract Class',
                'Move Method',
                'Introduce Parameter Object'
            ],
            'architectural_guidance': [
                'Follow WSP 49 directory structure',
                'Maintain WSP 62 size compliance',
                'Enable recursive self-improvement'
            ]
        }
        
        return zen_patterns 