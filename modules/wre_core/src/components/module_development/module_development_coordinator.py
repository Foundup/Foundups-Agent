"""
Module Development Coordinator

Main coordinator for module development workflows, replacing the massive 
module_development_handler.py with WSP-compliant component architecture.

WSP Compliance:
- Single responsibility: Development workflow coordination
- Clean interfaces: Delegates to specialized components
- Modular cohesion: Loose coupling with clear boundaries
"""

from pathlib import Path
from typing import Dict, Any, Optional

from modules.wre_core.src.utils.logging_utils import wre_log
from .module_status_manager import ModuleStatusManager
from .module_test_runner import ModuleTestRunner
from .module_roadmap_viewer import ModuleRoadmapViewer
from .module_creator import ModuleCreator
from .manual_mode_manager import ManualModeManager

class ModuleDevelopmentCoordinator:
    """
    Module Development Coordinator - WSP-compliant workflow orchestration
    
    Responsibilities:
    - Coordinate module development workflows
    - Route user choices to appropriate components
    - Manage component lifecycle and dependencies
    - Provide unified interface for module development
    """
    
    def __init__(self, project_root: Path, session_manager):
        self.project_root = project_root
        self.session_manager = session_manager
        
        # Initialize specialized components
        self.status_manager = ModuleStatusManager(project_root, session_manager)
        self.test_runner = ModuleTestRunner(project_root, session_manager)
        self.roadmap_viewer = ModuleRoadmapViewer(project_root, session_manager)
        self.module_creator = ModuleCreator(project_root, session_manager)
        self.manual_mode_manager = ManualModeManager(project_root, session_manager)
        
    def handle_module_development(self, module_name: str, engine):
        """Handle module development workflow - main entry point."""
        wre_log(f"🏗️ Module Development Coordinator: {module_name}", "INFO")
        self.session_manager.log_operation("module_development", {"module": module_name})
        
        try:
            # Display module development menu
            engine.ui_interface.display_module_development_menu()
            
            # Get user choice
            dev_choice = engine.ui_interface.get_user_input("Select development option: ")
            
            # Route to appropriate component
            self._route_development_choice(dev_choice, module_name, engine)
            
        except Exception as e:
            wre_log(f"❌ Module development coordination failed: {e}", "ERROR")
            self.session_manager.log_operation("module_development", {"error": str(e)})
            
    def _route_development_choice(self, choice: str, module_name: str, engine):
        """Route user choice to appropriate specialized component."""
        if choice == "1":
            # Display module status
            self.status_manager.display_module_status(module_name, engine)
            
        elif choice == "2":
            # Run module tests
            self.test_runner.run_module_tests(module_name, engine)
            
        elif choice == "3":
            # Enter manual mode
            self.manual_mode_manager.enter_manual_mode(module_name, engine)
            
        elif choice == "4":
            # View roadmap
            self.roadmap_viewer.view_roadmap(module_name, engine)
            
        elif choice == "5":
            # Back to main menu
            wre_log("🔙 Returning to main menu", "INFO")
            
        else:
            wre_log(f"❌ Invalid development choice: {choice}", "ERROR")
            
    def create_new_module(self, module_name: str, domain: str, path: str):
        """Create a new module - delegates to module creator."""
        return self.module_creator.create_new_module(module_name, domain, path)
        
    def find_module_path(self, module_name: str) -> Optional[Path]:
        """Find module path - delegates to status manager."""
        return self.status_manager.find_module_path(module_name)
        
    def get_module_status_info(self, module_path: Path, module_name: str) -> Dict[str, Any]:
        """Get module status information - delegates to status manager."""
        return self.status_manager.get_module_status_info(module_path, module_name) 