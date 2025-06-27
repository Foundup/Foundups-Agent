# Placeholder for the Testing Agent

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

class TestingAgent:
    def __init__(self):
        """Initializes the Testing Agent (WSP-54 Duty 3.5)."""
        self.project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        print("TestingAgent initialized for WSP compliance validation.")

    def run_tests(self, target_module: Optional[str] = None) -> Dict:
        """
        WSP-54 Duty 3.5.1: Execute the pytest suite for a specified module or entire project.
        
        Args:
            target_module: Module path or None for full project
            
        Returns:
            Dict with test results and WSP_48 enhancement opportunities
        """
        print(f"Running tests for {target_module or 'entire project'}...")
        
        # Construct pytest command
        if target_module:
            test_path = self.project_root / "modules" / target_module / "tests"
            if not test_path.exists():
                return {
                    "status": "error",
                    "message": f"Test directory not found: {test_path}",
                    "wsp48_enhancement": "missing_test_structure",
                    "enhancement_trigger": f"Module {target_module} lacks proper test structure"
                }
            cmd = [sys.executable, '-m', 'pytest', str(test_path), '-v']
        else:
            cmd = [sys.executable, '-m', 'pytest', 'modules/', '-v', '--tb=short']
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            # Parse results for WSP_48 enhancement opportunities
            enhancement_opportunities = self._analyze_test_failures(result.stdout, result.stderr)
            
            return {
                "status": "success" if result.returncode == 0 else "failed",
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "wsp48_enhancements": enhancement_opportunities
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "wsp48_enhancement": "test_infrastructure_failure",
                "enhancement_trigger": f"Testing infrastructure needs improvement: {e}"
            }

    def check_coverage(self, target_module: Optional[str] = None) -> Dict:
        """
        WSP-54 Duty 3.5.2: Calculate test coverage percentage via pytest --cov.
        WSP-54 Duty 3.5.3: Compare coverage against required threshold (≥90% per WSP 6).
        
        Args:
            target_module: Module to check or None for project-wide
            
        Returns:
            Dict with coverage results and WSP_48 enhancement opportunities
        """
        print(f"Checking coverage for {target_module or 'entire project'}...")
        
        # Construct coverage command
        if target_module:
            module_path = f"modules.{target_module.replace('/', '.')}"
            cmd = [sys.executable, '-m', 'pytest', f'modules/{target_module}/tests/', 
                   f'--cov={module_path}.src', '--cov-report=term-missing']
        else:
            cmd = [sys.executable, '-m', 'pytest', 'modules/', 
                   '--cov=modules', '--cov-report=term-missing']
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            # Parse coverage percentage
            coverage_pct = self._parse_coverage_percentage(result.stdout)
            wsp6_compliant = coverage_pct >= 90.0 if coverage_pct else False
            
            # Generate WSP_48 enhancement opportunities
            enhancements = []
            if not wsp6_compliant:
                enhancements.append({
                    "type": "coverage_improvement",
                    "current": coverage_pct,
                    "target": 90.0,
                    "priority": "high" if coverage_pct < 70 else "medium"
                })
            
            return {
                "status": "success",
                "coverage_percentage": coverage_pct,
                "wsp6_compliant": wsp6_compliant,
                "threshold": 90.0,
                "stdout": result.stdout,
                "wsp48_enhancements": enhancements
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "wsp48_enhancement": "coverage_infrastructure_failure",
                "enhancement_trigger": f"Coverage analysis needs improvement: {e}"
            }

    def _analyze_test_failures(self, stdout: str, stderr: str) -> List[Dict]:
        """Analyze test output for WSP_48 enhancement opportunities."""
        enhancements = []
        
        # Check for missing test files
        if "test session starts" in stdout and "collected 0 items" in stdout:
            enhancements.append({
                "type": "missing_tests",
                "description": "No tests found - module needs test implementation",
                "priority": "critical"
            })
        
        # Check for import errors (common architectural issue)
        if "ImportError" in stderr or "ModuleNotFoundError" in stderr:
            enhancements.append({
                "type": "import_architecture",
                "description": "Import errors suggest architectural improvements needed",
                "priority": "high"
            })
        
        # Check for failing tests
        if "FAILED" in stdout:
            enhancements.append({
                "type": "test_failures",
                "description": "Failing tests indicate code quality issues",
                "priority": "medium"
            })
        
        return enhancements

    def _parse_coverage_percentage(self, output: str) -> Optional[float]:
        """Parse coverage percentage from pytest-cov output."""
        import re
        
        # Look for coverage summary line
        coverage_match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', output)
        if coverage_match:
            return float(coverage_match.group(1))
        
        # Alternative format
        coverage_match = re.search(r'(\d+)%\s+coverage', output)
        if coverage_match:
            return float(coverage_match.group(1))
        
        return None 