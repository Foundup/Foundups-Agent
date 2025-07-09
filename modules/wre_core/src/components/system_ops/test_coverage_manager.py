"""
Test Coverage Manager Component

Handles all test coverage analysis and reporting.
Extracted from system_manager.py per WSP 62 refactoring requirements.

WSP Compliance:
- WSP 62: Large File and Refactoring Enforcement Protocol (refactoring)
- WSP 1: Single responsibility principle (test coverage only)
- WSP 5: Test coverage requirements (≥90%)
- WSP 34: Test documentation standards
"""

import subprocess
from pathlib import Path
from typing import Dict, Any, List
from modules.wre_core.src.utils.logging_utils import wre_log
from modules.wre_core.src.utils.coverage_utils import get_coverage_target_for_module, assess_current_context


class TestCoverageManager:
    """
    Test Coverage Manager - Handles test coverage analysis and reporting
    
    Responsibilities:
    - Test coverage analysis
    - Coverage reporting and validation
    - WSP 5 compliance checking (≥90% coverage)
    - Test execution coordination
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
    def check_test_coverage(self, session_manager):
        """Check test coverage for all modules."""
        wre_log("🧪 Checking test coverage...", "INFO")
        session_manager.log_operation("test_coverage", {"action": "start"})
        
        try:
            # Run coverage analysis
            coverage_result = self._run_coverage_analysis()
            
            if coverage_result['success']:
                overall_coverage = coverage_result['overall_coverage']
                wre_log(f"📊 Overall test coverage: {overall_coverage:.1f}%", "INFO")
                
                # Check WSP 5 compliance (≥90% coverage)
                if overall_coverage >= 90.0:
                    wre_log("✅ WSP 5 compliance: Test coverage meets 90% threshold", "SUCCESS")
                    session_manager.log_achievement("test_coverage", f"Coverage at {overall_coverage:.1f}% (WSP 5 compliant)")
                else:
                    wre_log(f"⚠️ WSP 5 violation: Test coverage {overall_coverage:.1f}% below 90% threshold", "WARNING")
                    session_manager.log_operation("test_coverage", {"violation": f"Coverage below 90% at {overall_coverage:.1f}%"})
                    
                # Display module-specific coverage
                self._display_module_coverage(coverage_result['module_coverage'])
                
            else:
                wre_log("❌ Test coverage analysis failed", "ERROR")
                session_manager.log_operation("test_coverage", {"error": coverage_result['error']})
                
        except Exception as e:
            wre_log(f"❌ Test coverage check failed: {e}", "ERROR")
            session_manager.log_operation("test_coverage", {"error": str(e)})
            
    def _run_coverage_analysis(self) -> Dict[str, Any]:
        """Run comprehensive test coverage analysis."""
        result = {
            'success': False,
            'overall_coverage': 0.0,
            'module_coverage': {},
            'missing_tests': [],
            'error': None
        }
        
        try:
            # Check if pytest is available
            if not self._check_pytest_available():
                result['error'] = "pytest not available"
                return result
                
            # Run pytest with coverage
            coverage_command = [
                "python", "-m", "pytest", 
                "modules/", 
                "--cov=modules", 
                "--cov-report=term-missing",
                "--cov-report=json:coverage.json",
                "-v"
            ]
            
            wre_log("🔍 Running pytest with coverage analysis...", "INFO")
            coverage_process = subprocess.run(
                coverage_command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5-minute timeout
            )
            
            if coverage_process.returncode == 0:
                # Parse coverage results
                coverage_data = self._parse_coverage_output(coverage_process.stdout)
                result.update(coverage_data)
                result['success'] = True
                
                # Check for missing test files
                result['missing_tests'] = self._identify_missing_tests()
                
            else:
                result['error'] = f"pytest failed: {coverage_process.stderr}"
                wre_log(f"❌ Pytest execution failed: {coverage_process.stderr}", "ERROR")
                
        except subprocess.TimeoutExpired:
            result['error'] = "Test execution timed out (5 minutes)"
            wre_log("⏰ Test execution timed out", "ERROR")
        except Exception as e:
            result['error'] = str(e)
            wre_log(f"❌ Coverage analysis error: {e}", "ERROR")
            
        return result
        
    def _check_pytest_available(self) -> bool:
        """Check if pytest is available in the environment."""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--version"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
            
    def _parse_coverage_output(self, output: str) -> Dict[str, Any]:
        """Parse pytest coverage output to extract coverage data."""
        coverage_data = {
            'overall_coverage': 0.0,
            'module_coverage': {}
        }
        
        try:
            lines = output.split('\n')
            
            # Look for coverage summary line
            for line in lines:
                if 'TOTAL' in line and '%' in line:
                    # Extract overall coverage percentage
                    parts = line.split()
                    for part in parts:
                        if part.endswith('%'):
                            try:
                                coverage_data['overall_coverage'] = float(part.rstrip('%'))
                                break
                            except ValueError:
                                continue
                                
                # Extract module-specific coverage
                elif 'modules/' in line and '%' in line:
                    try:
                        parts = line.split()
                        module_path = parts[0]
                        
                        # Find coverage percentage
                        for part in parts:
                            if part.endswith('%'):
                                module_name = self._extract_module_name(module_path)
                                coverage_data['module_coverage'][module_name] = float(part.rstrip('%'))
                                break
                    except (ValueError, IndexError):
                        continue
                        
        except Exception as e:
            wre_log(f"⚠️ Error parsing coverage output: {e}", "WARNING")
            
        return coverage_data
        
    def _extract_module_name(self, module_path: str) -> str:
        """Extract module name from file path."""
        try:
            # Extract module name from path like "modules/domain/module_name/..."
            path_parts = module_path.split('/')
            if len(path_parts) >= 3 and path_parts[0] == 'modules':
                return f"{path_parts[1]}/{path_parts[2]}"
            return module_path
        except Exception:
            return module_path
            
    def _display_module_coverage(self, module_coverage: Dict[str, float]):
        """Display module-specific coverage information."""
        if not module_coverage:
            wre_log("📊 No module-specific coverage data available", "INFO")
            return
            
        wre_log("📊 Module Coverage Breakdown:", "INFO")
        
        # Sort modules by coverage (lowest first to highlight issues)
        sorted_modules = sorted(module_coverage.items(), key=lambda x: x[1])
        
        for module_name, coverage in sorted_modules:
            if coverage >= 90.0:
                status = "✅"
                level = "SUCCESS"
            elif coverage >= 75.0:
                status = "⚠️"
                level = "WARNING"
            else:
                status = "❌"
                level = "ERROR"
                
            wre_log(f"  {status} {module_name}: {coverage:.1f}%", level)
            
    def _identify_missing_tests(self) -> List[str]:
        """Identify modules that are missing test files."""
        missing_tests = []
        
        try:
            modules_path = self.project_root / "modules"
            if not modules_path.exists():
                return missing_tests
                
            # Check each module for test directory
            for domain_dir in modules_path.iterdir():
                if domain_dir.is_dir() and not domain_dir.name.startswith('.'):
                    for module_dir in domain_dir.iterdir():
                        if module_dir.is_dir() and not module_dir.name.startswith('.'):
                            test_dir = module_dir / "tests"
                            if not test_dir.exists():
                                missing_tests.append(f"{domain_dir.name}/{module_dir.name}")
                            else:
                                # Check if tests directory has actual test files
                                test_files = list(test_dir.glob("test_*.py"))
                                if not test_files:
                                    missing_tests.append(f"{domain_dir.name}/{module_dir.name} (no test files)")
                                    
        except Exception as e:
            wre_log(f"⚠️ Error identifying missing tests: {e}", "WARNING")
            
        return missing_tests
        
    def run_specific_module_tests(self, module_path: str, session_manager) -> bool:
        """Run tests for a specific module."""
        wre_log(f"🧪 Running tests for module: {module_path}", "INFO")
        session_manager.log_operation("module_test", {"module": module_path, "action": "start"})
        
        try:
            # Construct test command for specific module
            test_command = [
                "python", "-m", "pytest",
                f"modules/{module_path}/tests/",
                "-v",
                "--tb=short"
            ]
            
            test_process = subprocess.run(
                test_command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=180  # 3-minute timeout for individual module
            )
            
            if test_process.returncode == 0:
                wre_log(f"✅ Tests passed for {module_path}", "SUCCESS")
                session_manager.log_achievement("module_test", f"Tests passed for {module_path}")
                return True
            else:
                wre_log(f"❌ Tests failed for {module_path}", "ERROR")
                wre_log(f"Test output: {test_process.stdout}", "INFO")
                session_manager.log_operation("module_test", {"module": module_path, "error": "tests_failed"})
                return False
                
        except subprocess.TimeoutExpired:
            wre_log(f"⏰ Test timeout for {module_path}", "ERROR")
            session_manager.log_operation("module_test", {"module": module_path, "error": "timeout"})
            return False
        except Exception as e:
            wre_log(f"❌ Error running tests for {module_path}: {e}", "ERROR")
            session_manager.log_operation("module_test", {"module": module_path, "error": str(e)})
            return False
            
    def generate_coverage_report(self, output_format: str = "html") -> Dict[str, Any]:
        """Generate detailed coverage report."""
        wre_log(f"📊 Generating {output_format} coverage report...", "INFO")
        
        result = {
            'success': False,
            'report_path': None,
            'error': None
        }
        
        try:
            # Generate coverage report
            if output_format == "html":
                report_command = [
                    "python", "-m", "pytest",
                    "modules/",
                    "--cov=modules",
                    "--cov-report=html:coverage_html",
                    "-q"
                ]
                result['report_path'] = self.project_root / "coverage_html" / "index.html"
            elif output_format == "xml":
                report_command = [
                    "python", "-m", "pytest",
                    "modules/",
                    "--cov=modules",
                    "--cov-report=xml:coverage.xml",
                    "-q"
                ]
                result['report_path'] = self.project_root / "coverage.xml"
            else:
                result['error'] = f"Unsupported report format: {output_format}"
                return result
                
            report_process = subprocess.run(
                report_command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if report_process.returncode == 0:
                result['success'] = True
                wre_log(f"✅ Coverage report generated: {result['report_path']}", "SUCCESS")
            else:
                result['error'] = f"Report generation failed: {report_process.stderr}"
                
        except Exception as e:
            result['error'] = str(e)
            
        return result
        
    def get_coverage_summary(self) -> Dict[str, Any]:
        """Get a quick coverage summary without running full analysis."""
        summary = {
            'last_run': 'Unknown',
            'overall_coverage': 'Unknown',
            'wsp5_compliant': False,
            'modules_tested': 0,
            'modules_missing_tests': 0
        }
        
        try:
            # Check for existing coverage data
            coverage_json = self.project_root / "coverage.json"
            if coverage_json.exists():
                import json
                with open(coverage_json, 'r') as f:
                    data = json.load(f)
                    
                summary['overall_coverage'] = f"{data.get('totals', {}).get('percent_covered', 0):.1f}%"
                summary['wsp5_compliant'] = data.get('totals', {}).get('percent_covered', 0) >= 90.0
                
            # Count modules with and without tests
            missing_tests = self._identify_missing_tests()
            summary['modules_missing_tests'] = len(missing_tests)
            
            # Count total modules
            modules_path = self.project_root / "modules"
            if modules_path.exists():
                total_modules = 0
                for domain_dir in modules_path.iterdir():
                    if domain_dir.is_dir() and not domain_dir.name.startswith('.'):
                        for module_dir in domain_dir.iterdir():
                            if module_dir.is_dir() and not module_dir.name.startswith('.'):
                                total_modules += 1
                                
                summary['modules_tested'] = total_modules - summary['modules_missing_tests']
                
        except Exception as e:
            summary['error'] = str(e)
            
        return summary 