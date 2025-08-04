"""
Code Analyzer - WSP/WRE AI Intelligence Module

WSP Compliance:
- WSP 34 (Testing Protocol): Comprehensive code analysis and testing capabilities
- WSP 54 (Agent Duties): AI-powered code analysis for autonomous development
- WSP 22 (ModLog): Change tracking and analysis history
- WSP 50 (Pre-Action Verification): Enhanced verification before code analysis

Provides AI-powered code analysis capabilities for autonomous development operations.
Enables 0102 pArtifacts to analyze code quality, complexity, and compliance.
"""

import ast
import os
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CodeAnalysisResult:
    """Result of code analysis operation."""
    file_path: str
    complexity_score: float
    quality_score: float
    compliance_score: float
    issues: List[str]
    recommendations: List[str]
    wsp_compliance: Dict[str, bool]


class CodeAnalyzer:
    """
    AI-powered code analyzer for autonomous development operations.
    
    Provides comprehensive code analysis including:
    - Complexity analysis
    - Quality assessment
    - WSP compliance checking
    - Issue identification
    - Improvement recommendations
    """
    
    def __init__(self):
        """Initialize the code analyzer with WSP compliance standards."""
        self.wsp_standards = {
            'modlog_present': False,
            'readme_present': False,
            'interface_documented': False,
            'tests_present': False,
            'proper_structure': False
        }
        
    def analyze_file(self, file_path: str) -> CodeAnalysisResult:
        """
        Analyze a single file for code quality and WSP compliance.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            CodeAnalysisResult with analysis findings
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse AST for complexity analysis
            tree = ast.parse(content)
            
            # Calculate complexity metrics
            complexity_score = self._calculate_complexity(tree)
            quality_score = self._assess_quality(content, tree)
            compliance_score = self._check_wsp_compliance(file_path, content)
            
            # Identify issues and recommendations
            issues = self._identify_issues(content, tree)
            recommendations = self._generate_recommendations(issues, compliance_score)
            
            return CodeAnalysisResult(
                file_path=file_path,
                complexity_score=complexity_score,
                quality_score=quality_score,
                compliance_score=compliance_score,
                issues=issues,
                recommendations=recommendations,
                wsp_compliance=self.wsp_standards.copy()
            )
            
        except Exception as e:
            return CodeAnalysisResult(
                file_path=file_path,
                complexity_score=0.0,
                quality_score=0.0,
                compliance_score=0.0,
                issues=[f"Analysis failed: {str(e)}"],
                recommendations=["Fix file access or syntax issues"],
                wsp_compliance=self.wsp_standards.copy()
            )
    
    def analyze_directory(self, directory_path: str) -> List[CodeAnalysisResult]:
        """
        Analyze all Python files in a directory.
        
        Args:
            directory_path: Path to directory to analyze
            
        Returns:
            List of CodeAnalysisResult objects
        """
        results = []
        directory = Path(directory_path)
        
        for python_file in directory.rglob("*.py"):
            if python_file.is_file():
                result = self.analyze_file(str(python_file))
                results.append(result)
                
        return results
    
    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calculate cyclomatic complexity of the code."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
                
        return complexity
    
    def _assess_quality(self, content: str, tree: ast.AST) -> float:
        """Assess code quality based on various metrics."""
        quality_score = 100.0
        
        # Check for docstrings
        if not self._has_docstrings(tree):
            quality_score -= 20
            
        # Check for long functions
        if self._has_long_functions(tree):
            quality_score -= 15
            
        # Check for proper naming conventions
        if not self._follows_naming_conventions(tree):
            quality_score -= 10
            
        # Check for comments
        if not self._has_adequate_comments(content):
            quality_score -= 10
            
        return max(0.0, quality_score)
    
    def _check_wsp_compliance(self, file_path: str, content: str) -> float:
        """Check WSP compliance of the file and its module structure."""
        compliance_score = 100.0
        file_path_obj = Path(file_path)
        module_dir = file_path_obj.parent.parent
        
        # Check for ModLog.md
        modlog_path = module_dir / "ModLog.md"
        self.wsp_standards['modlog_present'] = modlog_path.exists()
        if not self.wsp_standards['modlog_present']:
            compliance_score -= 25
            
        # Check for README.md
        readme_path = module_dir / "README.md"
        self.wsp_standards['readme_present'] = readme_path.exists()
        if not self.wsp_standards['readme_present']:
            compliance_score -= 20
            
        # Check for INTERFACE.md
        interface_path = module_dir / "INTERFACE.md"
        self.wsp_standards['interface_documented'] = interface_path.exists()
        if not self.wsp_standards['interface_documented']:
            compliance_score -= 15
            
        # Check for tests
        tests_dir = module_dir / "tests"
        self.wsp_standards['tests_present'] = tests_dir.exists() and any(tests_dir.rglob("*.py"))
        if not self.wsp_standards['tests_present']:
            compliance_score -= 20
            
        # Check for proper structure
        src_dir = module_dir / "src"
        self.wsp_standards['proper_structure'] = src_dir.exists()
        if not self.wsp_standards['proper_structure']:
            compliance_score -= 20
            
        return max(0.0, compliance_score)
    
    def _identify_issues(self, content: str, tree: ast.AST) -> List[str]:
        """Identify specific issues in the code."""
        issues = []
        
        # Check for missing docstrings
        if not self._has_docstrings(tree):
            issues.append("Missing module or function docstrings")
            
        # Check for long functions
        if self._has_long_functions(tree):
            issues.append("Functions exceed recommended length")
            
        # Check for naming violations
        if not self._follows_naming_conventions(tree):
            issues.append("Naming conventions not followed")
            
        # Check for WSP compliance issues
        if not all(self.wsp_standards.values()):
            missing_items = [k for k, v in self.wsp_standards.items() if not v]
            issues.append(f"Missing WSP compliance items: {', '.join(missing_items)}")
            
        return issues
    
    def _generate_recommendations(self, issues: List[str], compliance_score: float) -> List[str]:
        """Generate improvement recommendations based on issues."""
        recommendations = []
        
        for issue in issues:
            if "docstrings" in issue:
                recommendations.append("Add comprehensive docstrings to all modules and functions")
            elif "length" in issue:
                recommendations.append("Refactor long functions into smaller, focused functions")
            elif "naming" in issue:
                recommendations.append("Follow PEP 8 naming conventions")
            elif "WSP compliance" in issue:
                recommendations.append("Create missing WSP compliance files (ModLog.md, README.md, etc.)")
                
        if compliance_score < 50:
            recommendations.append("Priority: Address WSP compliance violations immediately")
        elif compliance_score < 80:
            recommendations.append("Improve WSP compliance for better integration")
            
        return recommendations
    
    def _has_docstrings(self, tree: ast.AST) -> bool:
        """Check if the code has adequate docstrings."""
        has_module_docstring = False
        has_function_docstrings = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Module) and ast.get_docstring(node):
                has_module_docstring = True
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if ast.get_docstring(node):
                    has_function_docstrings = True
                    break
                    
        return has_module_docstring and has_function_docstrings
    
    def _has_long_functions(self, tree: ast.AST) -> bool:
        """Check for functions that exceed recommended length."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if len(node.body) > 20:  # More than 20 lines
                    return True
        return False
    
    def _follows_naming_conventions(self, tree: ast.AST) -> bool:
        """Check if naming conventions are followed."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                    return False
            elif isinstance(node, ast.ClassDef):
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    return False
        return True
    
    def _has_adequate_comments(self, content: str) -> bool:
        """Check if the code has adequate comments."""
        lines = content.split('\n')
        code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        comment_lines = [line for line in lines if line.strip().startswith('#')]
        
        if not code_lines:
            return True
            
        comment_ratio = len(comment_lines) / len(code_lines)
        return comment_ratio >= 0.1  # At least 10% comments


def analyze_code(file_path: str) -> CodeAnalysisResult:
    """
    Convenience function to analyze a single file.
    
    Args:
        file_path: Path to the file to analyze
        
    Returns:
        CodeAnalysisResult with analysis findings
    """
    analyzer = CodeAnalyzer()
    return analyzer.analyze_file(file_path)


def analyze_module(module_path: str) -> List[CodeAnalysisResult]:
    """
    Convenience function to analyze an entire module.
    
    Args:
        module_path: Path to the module to analyze
        
    Returns:
        List of CodeAnalysisResult objects
    """
    analyzer = CodeAnalyzer()
    return analyzer.analyze_directory(module_path)


if __name__ == "__main__":
    """Test the code analyzer with a sample file."""
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        result = analyze_code(file_path)
        print(f"Analysis of {file_path}:")
        print(f"Complexity Score: {result.complexity_score}")
        print(f"Quality Score: {result.quality_score}")
        print(f"Compliance Score: {result.compliance_score}")
        print(f"Issues: {result.issues}")
        print(f"Recommendations: {result.recommendations}")
    else:
        print("Usage: python code_analyzer.py <file_path>") 