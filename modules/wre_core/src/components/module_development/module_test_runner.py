"""
Module Test Runner

Handles test execution for modules.
Extracted from module_development_handler.py following WSP principles.

WSP Compliance:
- Single responsibility: Test execution only
- Clean interfaces: Focused API for test operations
- Modular cohesion: Self-contained test logic
"""

import subprocess
import sys
from pathlib import Path

from modules.wre_core.src.utils.logging_utils import wre_log

class ModuleTestRunner:
    """
    Module Test Runner - WSP-compliant test execution
    
    Responsibilities:
    - Test execution for modules
    - Test result parsing and display
    - Test environment management
    """
    
    def __init__(self, project_root: Path, session_manager):
        self.project_root = project_root
        self.session_manager = session_manager
        
    def run_module_tests(self, module_name: str, engine):
        """Run tests for a specific module."""
        wre_log(f"🧪 Running tests for: {module_name}", "INFO")
        self.session_manager.log_operation("module_tests", {"module": module_name})
        
        try:
            # Find module path
            module_path = self._find_module_path(module_name)
            if not module_path:
                wre_log(f"❌ Module not found: {module_name}", "ERROR")
                return
                
            # Check if tests directory exists
            tests_dir = module_path / "tests"
            if not tests_dir.exists():
                wre_log(f"⚠️ No tests directory found for {module_name}", "WARNING")
                return
                
            # Run tests
            test_result = subprocess.run(
                [sys.executable, "-m", "pytest", str(tests_dir), "-v"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if test_result.returncode == 0:
                wre_log(f"✅ Tests passed for {module_name}", "SUCCESS")
                wre_log(f"Test output: {test_result.stdout}", "INFO")
                self.session_manager.log_achievement("module_tests", f"Tests passed for {module_name}")
            else:
                wre_log(f"❌ Tests failed for {module_name}", "ERROR")
                wre_log(f"Test output: {test_result.stderr}", "ERROR")
                self.session_manager.log_operation("module_tests", {"error": "Tests failed"})
                
        except Exception as e:
            wre_log(f"❌ Test execution failed: {e}", "ERROR")
            self.session_manager.log_operation("module_tests", {"error": str(e)})
            
    def _find_module_path(self, module_name: str) -> Path:
        """Find the path to a module by name."""
        modules_dir = self.project_root / "modules"
        
        for module_path in modules_dir.rglob("*"):
            if module_path.is_dir() and module_path.name == module_name:
                return module_path
                
        return None 