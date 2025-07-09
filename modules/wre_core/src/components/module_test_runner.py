"""
Module Test Runner Component

Handles module test execution and validation.
Extracted from module_development_handler.py per WSP 62 refactoring requirements.

WSP Compliance:
- WSP 62: Large File and Refactoring Enforcement Protocol (refactoring)
- WSP 1: Single responsibility principle (test execution only)
- WSP 5: Test coverage enforcement protocol (≥90%)
"""

import subprocess
import sys
from pathlib import Path

from modules.wre_core.src.utils.logging_utils import wre_log


class ModuleTestRunner:
    """
    Module Test Runner - Handles module test execution and validation
    
    Responsibilities:
    - Test execution for specific modules
    - Test result reporting
    - Test coverage validation
    - WSP 5 compliance checking
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
    def run_module_tests(self, module_name: str, module_path: Path, session_manager):
        """Run tests for a specific module."""
        wre_log(f"🧪 Running tests for: {module_name}", "INFO")
        session_manager.log_operation("module_tests", {"module": module_name})
        
        try:
            # Check if tests directory exists
            tests_dir = module_path / "tests"
            if not tests_dir.exists():
                wre_log(f"⚠️ No tests directory found for {module_name}", "WARNING")
                return False
                
            # Run tests with coverage
            test_result = self._execute_tests_with_coverage(tests_dir, module_path)
            
            if test_result["success"]:
                wre_log(f"✅ Tests passed for {module_name}", "SUCCESS")
                if test_result["output"]:
                    wre_log(f"Test output: {test_result['output']}", "INFO")
                    
                # Check coverage if available
                if test_result.get("coverage"):
                    coverage_pct = test_result["coverage"]
                    if coverage_pct >= 90:
                        wre_log(f"✅ WSP 5 Coverage: {coverage_pct:.1f}% (≥90% required)", "SUCCESS")
                    else:
                        wre_log(f"⚠️ WSP 5 Coverage: {coverage_pct:.1f}% (below 90% requirement)", "WARNING")
                        
                session_manager.log_achievement("module_tests", f"Tests passed for {module_name}")
                return True
            else:
                wre_log(f"❌ Tests failed for {module_name}", "ERROR")
                if test_result["error"]:
                    wre_log(f"Test errors: {test_result['error']}", "ERROR")
                session_manager.log_operation("module_tests", {"error": "Tests failed"})
                return False
                
        except Exception as e:
            wre_log(f"❌ Test execution failed: {e}", "ERROR")
            session_manager.log_operation("module_tests", {"error": str(e)})
            return False
            
    def _execute_tests_with_coverage(self, tests_dir: Path, module_path: Path) -> dict:
        """Execute tests with coverage reporting."""
        try:
            # Try to run with coverage first
            coverage_result = subprocess.run(
                [sys.executable, "-m", "pytest", str(tests_dir), "-v", 
                 f"--cov={module_path}/src", "--cov-report=term-missing"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if coverage_result.returncode == 0:
                # Extract coverage percentage if available
                coverage_pct = self._extract_coverage_percentage(coverage_result.stdout)
                return {
                    "success": True,
                    "output": coverage_result.stdout,
                    "error": None,
                    "coverage": coverage_pct
                }
            else:
                # Fall back to basic pytest if coverage fails
                basic_result = subprocess.run(
                    [sys.executable, "-m", "pytest", str(tests_dir), "-v"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                
                return {
                    "success": basic_result.returncode == 0,
                    "output": basic_result.stdout,
                    "error": basic_result.stderr if basic_result.returncode != 0 else None,
                    "coverage": None
                }
                
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": str(e),
                "coverage": None
            }
            
    def _extract_coverage_percentage(self, output: str) -> float:
        """Extract coverage percentage from pytest-cov output."""
        try:
            lines = output.split('\n')
            for line in lines:
                if 'TOTAL' in line and '%' in line:
                    # Look for pattern like "TOTAL    123    45    63%"
                    parts = line.split()
                    for part in parts:
                        if part.endswith('%'):
                            return float(part[:-1])
            return 0.0
        except Exception:
            return 0.0
            
    def run_all_tests(self, session_manager):
        """Run all tests in the project."""
        wre_log("🧪 Running all project tests", "INFO")
        session_manager.log_operation("all_tests", {})
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "modules/", "-v"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                wre_log("✅ All tests passed", "SUCCESS")
                wre_log(f"Test output: {result.stdout}", "INFO")
                session_manager.log_achievement("all_tests", "All tests passed")
                return True
            else:
                wre_log("❌ Some tests failed", "ERROR")
                wre_log(f"Test output: {result.stderr}", "ERROR")
                session_manager.log_operation("all_tests", {"error": "Some tests failed"})
                return False
                
        except Exception as e:
            wre_log(f"❌ Test execution failed: {e}", "ERROR")
            session_manager.log_operation("all_tests", {"error": str(e)})
            return False 