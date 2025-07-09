"""
Module Development Handler Component (WSP 62 Refactored)

Refactored coordinator that delegates to specialized component managers.
Replaces the oversized module_development_handler.py per WSP 62 compliance.

WSP Compliance:
- WSP 62: Large File and Refactoring Enforcement Protocol (refactored)
- WSP 1: Single responsibility principle (coordination only)
- WSP 49: Module directory structure standardization
"""

from pathlib import Path
from modules.wre_core.src.utils.logging_utils import wre_log
from modules.wre_core.src.components.module_status_manager import ModuleStatusManager
from modules.wre_core.src.components.module_test_runner import ModuleTestRunner
from modules.wre_core.src.components.manual_mode_manager import ManualModeManager


class ModuleDevelopmentHandler:
    """
    Module Development Handler - Coordinates module development workflows
    
    Responsibilities:
    - Workflow coordination and routing
    - Component manager initialization
    - Development option handling
    - Session management integration
    
    NOTE: This is the WSP 62 compliant refactored version that replaced
    the original 1,008-line file with focused component delegation.
    """
    
    def __init__(self, project_root: Path, session_manager):
        self.project_root = project_root
        self.session_manager = session_manager
        
        # Initialize component managers
        self.module_status_manager = ModuleStatusManager(project_root)
        self.module_test_runner = ModuleTestRunner(project_root)
        self.manual_mode_manager = ManualModeManager(project_root)
        
    def handle_module_development(self, module_name: str, engine):
        """Handle module development workflow."""
        wre_log(f"🏗️ Handling module development for: {module_name}", "INFO")
        self.session_manager.log_operation("module_development", {"module": module_name})
        
        try:
            # Display module development menu
            engine.ui_interface.display_module_development_menu()
            
            # Get user choice
            dev_choice = engine.ui_interface.get_user_input("Select development option: ")
            
            # Route to appropriate component manager
            if dev_choice == "1":
                # Display module status - delegate to status manager
                self.module_status_manager.display_module_status(module_name, self.session_manager)
                
            elif dev_choice == "2":
                # Run module tests - delegate to test runner
                module_path = self.module_status_manager.find_module_path(module_name)
                if module_path:
                    self.module_test_runner.run_module_tests(module_name, module_path, self.session_manager)
                else:
                    wre_log(f"❌ Module not found: {module_name}", "ERROR")
                
            elif dev_choice == "3":
                # Enter manual mode - delegate to manual mode manager
                # Pass engine with component managers attached
                engine.module_status_manager = self.module_status_manager
                engine.module_test_runner = self.module_test_runner
                self.manual_mode_manager.enter_manual_mode(module_name, engine, self.session_manager)
                
            elif dev_choice == "4":
                # View roadmap - placeholder for roadmap manager
                wre_log("🗺️ Roadmap functionality - coming soon", "INFO")
                # TODO: Implement ModuleRoadmapManager and delegate here
                
            else:
                wre_log("❌ Invalid development choice", "ERROR")
                
        except Exception as e:
            wre_log(f"❌ Module development failed: {e}", "ERROR")
            self.session_manager.log_operation("module_development", {"error": str(e)})
            
    def get_component_managers(self) -> dict:
        """Get all component managers for integration."""
        return {
            "status_manager": self.module_status_manager,
            "test_runner": self.module_test_runner,
            "manual_mode_manager": self.manual_mode_manager
        }
        
    def run_comprehensive_tests(self):
        """Run comprehensive test suite across all modules."""
        wre_log("🧪 Running comprehensive test suite", "INFO")
        return self.module_test_runner.run_all_tests(self.session_manager)
        
    def get_system_status(self) -> dict:
        """Get comprehensive system status."""
        wre_log("📊 Gathering system status", "INFO")
        
        # Get all modules
        modules_dir = self.project_root / "modules"
        system_status = {
            "total_modules": 0,
            "active_modules": 0,
            "modules_with_tests": 0,
            "modules_with_docs": 0,
            "wsp_62_violations": 0
        }
        
        for domain_dir in modules_dir.iterdir():
            if domain_dir.is_dir() and domain_dir.name != "__pycache__":
                for module_dir in domain_dir.iterdir():
                    if module_dir.is_dir() and module_dir.name != "__pycache__":
                        system_status["total_modules"] += 1
                        
                        # Check module status
                        status_info = self.module_status_manager.get_module_status_info(
                            module_dir, module_dir.name
                        )
                        
                        if status_info["status"] == "Active":
                            system_status["active_modules"] += 1
                            
                        if status_info["test_count"] > 0:
                            system_status["modules_with_tests"] += 1
                            
                        if status_info["docs_status"] in ["Complete", "Partial"]:
                            system_status["modules_with_docs"] += 1
                            
                        if status_info.get("size_violations"):
                            system_status["wsp_62_violations"] += len(status_info["size_violations"])
        
        return system_status 