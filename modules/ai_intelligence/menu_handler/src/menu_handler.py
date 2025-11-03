"""
Menu Handler Component - AI Intelligence Domain

Handles all menu selection logic and user interaction processing.
Moved to ai_intelligence domain per WSP 3 enterprise structure.

WSP Compliance:
- Domain: ai_intelligence (intelligent menu processing)
- Single responsibility: Menu processing and routing
- Clean interfaces: Delegates to appropriate components
- Modular cohesion: Only menu-related logic
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import sys

from modules.wre_core.src.utils.logging_utils import wre_log
from modules.wre_core.src.components.module_development.module_development_coordinator import ModuleDevelopmentCoordinator as ModuleDevelopmentHandler

class MenuHandler:
    """
    Menu Handler - Processes user menu selections (AI Intelligence Domain)
    
    Responsibilities:
    - Parse menu choices with intelligent routing
    - Route to appropriate handlers based on context
    - Handle module development workflows
    - Manage system operations routing
    """
    
    def __init__(self, project_root: Path, ui_interface, session_manager):
        self.project_root = project_root
        self.ui_interface = ui_interface
        self.session_manager = session_manager
        self.module_dev_handler = ModuleDevelopmentHandler(project_root, session_manager)
        
    def handle_choice(self, choice: str, engine):
        """Handle main menu selection and route to appropriate handler."""
        self.session_manager.log_operation("menu_selection", {"choice": choice})
        
        if choice == "0":
            engine.shutdown()
            
        # Get prioritized modules to map choice to module
        prioritized_modules = self.ui_interface._get_prioritized_modules()
        num_modules = len(prioritized_modules)
        
        # Handle module development options (1 to num_modules)
        if choice.isdigit() and 1 <= int(choice) <= num_modules:
            module_index = int(choice) - 1
            selected_module = prioritized_modules[module_index]
            module_path = f"modules/{selected_module['domain']}/{selected_module['path']}"
            self._handle_module_development(module_path, engine)
            
        # Handle system options
        elif choice == str(num_modules + 1):
            # WSP_30 Agentic Module Build Orchestration
            self._handle_wsp30_orchestration(engine)
            
        elif choice == str(num_modules + 2):
            # View development roadmap
            self._display_roadmap(engine)
            
        elif choice == str(num_modules + 3):
            # System management
            self._handle_system_management(engine)
            
        elif choice == str(num_modules + 4):
            # Session status
            self._display_session_status(engine)
            
        elif choice == str(num_modules + 5):
            # Module analysis
            self._handle_module_analysis(engine)
            
        elif choice == str(num_modules + 6):
            # Follow WSP (ModLog + Git Push)
            self._follow_wsp_compliance(engine)
            
    def _handle_module_development(self, module_name: str, engine):
        """Handle module-specific development workflow."""
        wre_log(f"[U+1F3D7]️ Entering module development for: {module_name}", "INFO")
        self.session_manager.log_module_access(module_name, "development")
        
        # Special handling for YouTube module - redirect to main.py
        if module_name == "youtube_module":
            wre_log("[U+1F4FA] YouTube module selected - redirecting to main.py", "INFO")
            self.ui_interface.display_success("Launching FoundUps Agent main.py for YouTube module...")
            
            try:
                # Launch main.py in the same terminal
                subprocess.run([sys.executable, "main.py"], cwd=self.project_root)
            except Exception as e:
                wre_log(f"[FAIL] Failed to launch main.py: {e}", "ERROR")
                self.ui_interface.display_error(f"Failed to launch main.py: {e}")
        else:
            # Use module development handler
            self.module_dev_handler.handle_module_development(module_name, engine)
            
    def _handle_wsp30_orchestration(self, engine):
        """Handle WSP_30 Agentic Module Build Orchestration."""
        wre_log("[TARGET] WSP_30 Agentic Module Build Orchestration", "INFO")
        self.session_manager.log_operation("wsp30_orchestration", {"action": "start"})
        
        # Get WSP30 orchestrator from engine
        orchestrator = engine.get_wsp30_orchestrator()
        
        # Display orchestration menu
        self.ui_interface.display_wsp30_menu()
        
        # Get user choice for orchestration
        orchestration_choice = self.ui_interface.get_user_input("Select orchestration option: ")
        
        if orchestration_choice == "1":
            # Start agentic build
            module_name = self.ui_interface.get_user_input("Enter module name to build: ")
            self._start_agentic_build(module_name, orchestrator)
            
        elif orchestration_choice == "2":
            # Orchestrate new module
            module_name = self.ui_interface.get_user_input("Enter new module name: ")
            self._orchestrate_new_module(module_name, orchestrator)
            
        elif orchestration_choice == "3":
            # Manual mode
            module_name = self.ui_interface.get_user_input("Enter module name for manual mode: ")
            self._enter_manual_mode(module_name, engine)
            
        else:
            self.ui_interface.display_warning("Invalid orchestration choice")
            
    def _start_agentic_build(self, module_name: str, orchestrator):
        """Start agentic build for a module."""
        wre_log(f"[BOT] Starting agentic build for: {module_name}", "INFO")
        
        try:
            # Use orchestrator to start build
            success = orchestrator.start_agentic_build(module_name)
            
            if success:
                self.ui_interface.display_success(f"Agentic build started for {module_name}")
                self.session_manager.log_achievement("agentic_build_started", f"Build started for {module_name}")
            else:
                self.ui_interface.display_error(f"Failed to start agentic build for {module_name}")
                
        except Exception as e:
            wre_log(f"[FAIL] Agentic build failed: {e}", "ERROR")
            self.ui_interface.display_error(f"Agentic build failed: {e}")
            
    def _orchestrate_new_module(self, module_name: str, orchestrator):
        """Orchestrate creation of a new module."""
        wre_log(f"[MUSIC] Orchestrating new module: {module_name}", "INFO")
        
        try:
            # Use orchestrator to create new module
            success = orchestrator.orchestrate_new_module(module_name)
            
            if success:
                self.ui_interface.display_success(f"New module {module_name} orchestrated successfully")
                self.session_manager.log_achievement("new_module_orchestrated", f"Module {module_name} created")
            else:
                self.ui_interface.display_error(f"Failed to orchestrate new module {module_name}")
                
        except Exception as e:
            wre_log(f"[FAIL] Module orchestration failed: {e}", "ERROR")
            self.ui_interface.display_error(f"Module orchestration failed: {e}")
            
    def _enter_manual_mode(self, module_name: str, engine):
        """Enter manual development mode for a module."""
        wre_log(f"[TOOL] Entering manual mode for: {module_name}", "INFO")
        self.session_manager.log_operation("manual_mode", {"module": module_name})
        
        # Use module development handler for manual mode
        self.module_dev_handler.enter_manual_mode(module_name, engine)
        
    def _display_roadmap(self, engine):
        """Display development roadmap."""
        wre_log("[U+1F5FA]️ Displaying development roadmap", "INFO")
        
        try:
            # Get module prioritizer from engine
            prioritizer = engine.get_module_prioritizer()
            
            # Generate and display roadmap
            roadmap = prioritizer.generate_development_roadmap()
            self.ui_interface.display_roadmap(roadmap)
            
        except Exception as e:
            wre_log(f"[FAIL] Failed to display roadmap: {e}", "ERROR")
            self.ui_interface.display_error(f"Failed to display roadmap: {e}")
            
    def _handle_system_management(self, engine):
        """Handle system management operations."""
        wre_log("[U+2699]️ System management", "INFO")
        
        # Get system manager from engine
        system_manager = engine.system_manager
        
        # Display system management menu
        self.ui_interface.display_system_management_menu()
        
        # Get user choice
        system_choice = self.ui_interface.get_user_input("Select system option: ")
        
        # Route to system manager
        system_manager.handle_system_choice(system_choice, engine)
        
    def _display_session_status(self, engine):
        """Display current session status."""
        wre_log("[DATA] Displaying session status", "INFO")
        
        try:
            # Get session manager from engine
            session_manager = engine.get_session_manager()
            
            # Get session status
            status = session_manager.get_session_status()
            self.ui_interface.display_session_status(status)
            
        except Exception as e:
            wre_log(f"[FAIL] Failed to display session status: {e}", "ERROR")
            self.ui_interface.display_error(f"Failed to display session status: {e}")
            
    def _handle_module_analysis(self, engine):
        """Handle module analysis operations."""
        wre_log("[SEARCH] Module analysis", "INFO")
        
        # Get module analyzer from engine
        module_analyzer = engine.module_analyzer
        
        # Display analysis menu
        self.ui_interface.display_module_analysis_menu()
        
        # Get user choice
        analysis_choice = self.ui_interface.get_user_input("Select analysis option: ")
        
        # Route to module analyzer
        module_analyzer.handle_analysis_choice(analysis_choice, engine)
        
    def _follow_wsp_compliance(self, engine):
        """Follow WSP compliance workflow (ModLog + Git Push)."""
        wre_log("[CLIPBOARD] Following WSP compliance workflow", "INFO")
        
        # Get system manager from engine
        system_manager = engine.system_manager
        
        # Execute WSP compliance workflow
        system_manager.execute_wsp_compliance_workflow(engine) 