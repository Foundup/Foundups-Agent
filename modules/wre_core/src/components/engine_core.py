"""
WRE Engine Core Component

Handles the essential WRE lifecycle and coordination between components.
This is the minimal core that orchestrates the modular architecture.

WSP Compliance:
- Single responsibility: Engine lifecycle management
- Clean interfaces: Delegates to specialized components
- Modular cohesion: Only core coordination logic
"""

import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from modules.wre_core.src.utils.logging_utils import wre_log
from modules.wre_core.src.components.component_manager import ComponentManager
from modules.wre_core.src.components.session_manager import SessionManager
from modules.wre_core.src.components.module_prioritizer import ModulePrioritizer
from modules.wre_core.src.components.wsp30_orchestrator import WSP30Orchestrator
from modules.wre_core.src.interfaces.ui_interface import UIInterface
from modules.wre_core.src.components.menu_handler import MenuHandler
from modules.wre_core.src.components.system_manager import SystemManager
from modules.wre_core.src.components.module_analyzer import ModuleAnalyzer

class WRECore:
    """
    WRE Core Engine - Minimal lifecycle coordinator
    
    Responsibilities:
    - Engine initialization and shutdown
    - Component coordination
    - Main event loop
    - Error handling and recovery
    
    Delegates to specialized components:
    - MenuHandler: User interaction processing
    - SystemManager: System operations
    - ModuleAnalyzer: Module analysis
    """
    
    def __init__(self, project_root_path: str = None):
        # Initialize core paths
        if project_root_path:
            self.project_root = Path(project_root_path)
        else:
            self.project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
            
        # Initialize core components
        self.component_manager = ComponentManager(self.project_root)
        self.session_manager = SessionManager(self.project_root)
        self.module_prioritizer = ModulePrioritizer(self.project_root)
        self.wsp30_orchestrator = WSP30Orchestrator(self.project_root, self.module_prioritizer.mps_calculator)
        self.ui_interface = UIInterface()
        
        # Initialize specialized handlers
        self.menu_handler = MenuHandler(self.project_root, self.ui_interface, self.session_manager)
        self.system_manager = SystemManager(self.project_root, self.session_manager)
        self.module_analyzer = ModuleAnalyzer(self.project_root, self.session_manager)
        
        # Engine state
        self.running = False
        self.current_session_id = None
        
    def start(self):
        """Start the WRE engine with full component initialization."""
        wre_log("🚀 Starting Windsurf Recursive Engine (WRE)...", "INFO")
        
        # Start session
        self.current_session_id = self.session_manager.start_session("interactive")
        
        # Initialize all components
        self._initialize_engine()
        
        # Enter main loop
        self.running = True
        self._main_loop()
        
    def _initialize_engine(self):
        """Initialize all WRE components and validate setup."""
        wre_log("⚙️ Initializing WRE components...", "INFO")
        
        # Initialize windsurfing components with session manager for quantum operations
        self.component_manager.initialize_all_components(self.session_manager)
        
        # Validate critical components
        if not self.component_manager.validate_components():
            self.ui_interface.display_warning("Some components failed to initialize - running in degraded mode")
            
        # Log successful initialization
        self.session_manager.log_achievement("engine_init", "WRE engine successfully initialized with modular architecture")
        wre_log("✅ WRE engine initialized successfully", "SUCCESS")
        
    def _main_loop(self):
        """Main engine event loop."""
        wre_log("🔄 Entering WRE main loop", "INFO")
        
        while self.running:
            try:
                # Display main menu
                choice = self.ui_interface.display_main_menu()
                
                # Process user selection through menu handler
                self.menu_handler.handle_choice(choice, self)
                
            except KeyboardInterrupt:
                self.ui_interface.display_warning("Operation interrupted by user")
                if self.ui_interface.prompt_yes_no("Do you want to exit WRE?"):
                    self.shutdown()
                    
            except Exception as e:
                wre_log(f"❌ Unexpected error in main loop: {e}", "ERROR")
                self.ui_interface.display_error(f"Unexpected error: {e}")
                
                if self.ui_interface.prompt_yes_no("Do you want to continue?"):
                    continue
                else:
                    self.shutdown()
                    
    def shutdown(self):
        """Gracefully shutdown the WRE engine."""
        wre_log("🛑 Shutting down WRE engine...", "INFO")
        
        # End session
        if self.current_session_id:
            self.session_manager.end_session()
            
        # Log shutdown
        self.session_manager.log_achievement("engine_shutdown", "WRE engine shutdown completed")
        wre_log("✅ WRE engine shutdown complete", "SUCCESS")
        
        self.running = False
        sys.exit(0)
        
    def get_component_manager(self):
        """Get the component manager for external access."""
        return self.component_manager
        
    def get_session_manager(self):
        """Get the session manager for external access."""
        return self.session_manager
        
    def get_module_prioritizer(self):
        """Get the module prioritizer for external access."""
        return self.module_prioritizer
        
    def get_wsp30_orchestrator(self):
        """Get the WSP30 orchestrator for external access."""
        return self.wsp30_orchestrator
        
    def get_quantum_operations(self):
        """Get the quantum-cognitive operations component for external access."""
        return self.component_manager.navigation 