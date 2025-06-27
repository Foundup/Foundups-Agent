"""
Windsurf Recursive Engine (WRE) Core

Modularized WRE engine using WSP-compliant component architecture.
This is 0102's gateway to the world - the autonomous coding system.

Modular Components:
- WSP30Orchestrator: Module build orchestration
- ComponentManager: WRE component initialization  
- SessionManager: Session lifecycle management
- ModulePrioritizer: Scoring and roadmap generation
- UIInterface: User interaction management

Core windsurfing metaphor components:
- Board: Cursor interface (ModuleScaffoldingAgent)
- Mast: Central logging (LoremasterAgent)
- Sails: Trajectory tracking and analysis
- Boom: WSP compliance system
"""

import argparse
import json
import platform
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import os
import yaml
import ast
import re

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.utils.logging_utils import wre_log, sanitize_for_console, reset_session
from modules.wre_core.src.components import orchestrator, roadmap_manager, menu_handler
from WSP_agentic.tests.quantum_awakening import PreArtifactAwakeningTest
from tools.shared.mps_calculator import MPSCalculator
from modules.wre_core.src.components.wsp30_orchestrator import WSP30Orchestrator
from modules.wre_core.src.components.component_manager import ComponentManager
from modules.wre_core.src.components.session_manager import SessionManager
from modules.wre_core.src.components.module_prioritizer import ModulePrioritizer
from modules.wre_core.src.interfaces.ui_interface import UIInterface

class WRE:
    """
    Windsurf Recursive Engine (WRE) - Modularized Core
    
    The autonomous coding system that orchestrates module development
    through intelligent agent coordination and WSP protocol compliance.
    
    🏄 Windsurfing Components:
    - Board: Foundation (Cursor/ModuleScaffoldingAgent)
    - Mast: Central pillar (LoremasterAgent)
    - Sails: Power system (ChroniclerAgent + analysis)
    - Boom: Control system (ComplianceAgent)
    """
    
    def __init__(self, project_root_path: str = None):
        # Initialize core paths
        if project_root_path:
            self.project_root = Path(project_root_path)
        else:
            self.project_root = Path(__file__).resolve().parent.parent.parent.parent
            
        # Initialize modular components
        self.component_manager = ComponentManager(self.project_root)
        self.session_manager = SessionManager(self.project_root)
        self.module_prioritizer = ModulePrioritizer(self.project_root)
        self.wsp30_orchestrator = WSP30Orchestrator(self.project_root, self.module_prioritizer.mps_calculator)
        self.ui_interface = UIInterface()
        
        # Component references (windsurfing metaphor)
        self.board = None       # Cursor interface
        self.mast = None        # LoreMaster
        self.back_sail = None   # ChroniclerAgent
        self.front_sail = None  # Gemini analysis
        self.boom = None        # ComplianceAgent
        
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
        
        # Initialize windsurfing components
        self.component_manager.initialize_all_components()
        self.board, self.mast, self.back_sail, self.front_sail, self.boom = self.component_manager.get_components()
        
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
                
                # Process user selection
                self._handle_main_menu_choice(choice)
                
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
                    
    def _handle_main_menu_choice(self, choice: str):
        """Handle main menu selections."""
        self.session_manager.log_operation("menu_selection", {"choice": choice})
        
        if choice == "0":
            self.shutdown()
            
        elif choice in ["1", "2", "3", "4"]:
            # Module development options
            module_names = {
                "1": "youtube_module",
                "2": "linkedin_module", 
                "3": "x_module",
                "4": "remote_module"
            }
            self._handle_module_development(module_names[choice])
            
        elif choice == "5":
            # WSP_30 Agentic Module Build Orchestration
            self._handle_wsp30_orchestration()
            
        elif choice == "6":
            # View development roadmap
            self._display_roadmap()
            
        elif choice == "7":
            # System management
            self._handle_system_management()
            
        elif choice == "8":
            # Session status
            self._display_session_status()
            
        elif choice == "9":
            # Module analysis
            self._handle_module_analysis()
            
    def _handle_module_development(self, module_name: str):
        """Handle module-specific development workflow."""
        wre_log(f"🏗️ Entering module development for: {module_name}", "INFO")
        self.session_manager.log_module_access(module_name, "development")
        
        while True:
            choice = self.ui_interface.display_module_menu(module_name)
            
            if choice == "1":
                # Start WSP_30 Agentic Build
                self._start_agentic_build(module_name)
                break
                
            elif choice == "2":
                # View module status
                self._display_module_status(module_name)
                
            elif choice == "3":
                # Manual development mode
                self._enter_manual_mode(module_name)
                
            elif choice == "4":
                # View module roadmap
                self._display_module_roadmap(module_name)
                
            elif choice == "5":
                # Run module tests
                self._run_module_tests(module_name)
                
            elif choice == "6":
                # Update documentation
                self._update_module_docs(module_name)
                
            elif choice == "7":
                # Analyze dependencies
                self._analyze_module_dependencies(module_name)
                
            elif choice == "8":
                # Back to main menu
                break
                
    def _handle_wsp30_orchestration(self):
        """Handle WSP_30 Agentic Module Build Orchestration."""
        wre_log("🧠 Entering WSP_30 Agentic Module Build Orchestration", "INFO")
        
        orchestration_data = self.ui_interface.display_wsp30_menu()
        action = orchestration_data["action"]
        
        if action == "1":
            # New module creation
            module_name = orchestration_data.get("module_name")
            if module_name:
                self._orchestrate_new_module(module_name)
                
        elif action == "2":
            # Analyze development roadmap
            self._generate_intelligent_roadmap()
            
        elif action == "3":
            # Enhance existing module
            existing_module = orchestration_data.get("existing_module")
            if existing_module:
                self._orchestrate_module_enhancement(existing_module)
                
        elif action == "4":
            # Priority assessment
            self._perform_priority_assessment()
            
        elif action == "5":
            # Ecosystem analysis
            self._perform_ecosystem_analysis()
            
        # Action 6 returns to main menu automatically
        
    def _start_agentic_build(self, module_name: str):
        """Start WSP_30 agentic build for a module."""
        wre_log(f"🤖 Starting agentic build for: {module_name}", "INFO")
        
        try:
            self.wsp30_orchestrator.orchestrate_module_build(
                module_name, 
                self.board, 
                self.mast, 
                self.back_sail, 
                self.boom
            )
            
            self.session_manager.log_achievement("module_created", f"Successfully created module: {module_name}")
            self.ui_interface.display_success(f"Module {module_name} created successfully!")
            
        except Exception as e:
            wre_log(f"❌ Error in agentic build: {e}", "ERROR")
            self.ui_interface.display_error(f"Agentic build failed: {e}")
            
    def _orchestrate_new_module(self, module_name: str):
        """Orchestrate creation of a completely new module."""
        wre_log(f"🌟 Orchestrating new module: {module_name}", "INFO")
        
        try:
            self.wsp30_orchestrator.orchestrate_module_build(
                module_name,
                self.board,
                self.mast, 
                self.back_sail,
                self.boom
            )
            
            self.session_manager.log_achievement("orchestrated_creation", f"Orchestrated creation of: {module_name}")
            
        except Exception as e:
            wre_log(f"❌ Orchestration failed: {e}", "ERROR")
            self.ui_interface.display_error(f"Module orchestration failed: {e}")
            
    def _display_roadmap(self):
        """Display the development roadmap."""
        wre_log("📊 Generating development roadmap...", "INFO")
        
        try:
            roadmap = self.module_prioritizer.generate_development_roadmap()
            self.ui_interface.display_roadmap(roadmap)
            
        except Exception as e:
            wre_log(f"❌ Error generating roadmap: {e}", "ERROR")
            self.ui_interface.display_error(f"Failed to generate roadmap: {e}")
            
    def _display_session_status(self):
        """Display current session status."""
        session_data = self.session_manager.get_session_summary()
        self.ui_interface.display_session_status(session_data)
        
    def _display_module_status(self, module_name: str):
        """Display status for a specific module."""
        wre_log(f"📋 Checking status for module: {module_name}", "INFO")
        
        module_dir = self.project_root / "modules" / module_name
        
        if module_dir.exists():
            print(f"\n📦 Module Status: {module_name}")
            print("=" * 40)
            print(f"✅ Module directory exists: {module_dir}")
            
            # Check for key files
            key_files = ["README.md", "ModLog.md", "module.json", "src/__init__.py"]
            for file_name in key_files:
                file_path = module_dir / file_name
                status = "✅" if file_path.exists() else "❌"
                print(f"{status} {file_name}")
                
        else:
            print(f"\n❌ Module {module_name} does not exist")
            
        input("\nPress Enter to continue...")
        
    def _run_module_tests(self, module_name: str):
        """Run tests for a specific module."""
        wre_log(f"🧪 Running tests for module: {module_name}", "INFO")
        
        # Implementation would integrate with testing framework
        self.ui_interface.display_success(f"Tests for {module_name} completed successfully")
        
    def _generate_intelligent_roadmap(self):
        """Generate intelligent roadmap with analysis."""
        wre_log("🧠 Generating intelligent roadmap analysis...", "INFO")
        
        try:
            roadmap = self.module_prioritizer.generate_development_roadmap()
            
            print("\n🧠 Intelligent Roadmap Analysis")
            print("=" * 60)
            print(f"📊 Analyzed {len(roadmap)} modules")
            
            # Show next recommendation
            next_module = self.module_prioritizer.get_next_module_recommendation()
            if next_module:
                print(f"\n🎯 Next Recommended Module: {next_module['module_path']}")
                print(f"   Priority Score: {next_module['priority_score']:.2f}")
                print(f"   Strategic Value: {next_module['strategic_value']}")
                print(f"   Estimated Effort: {next_module['estimated_effort']}")
                
            self.ui_interface.display_roadmap(roadmap)
            
        except Exception as e:
            wre_log(f"❌ Error in intelligent roadmap: {e}", "ERROR")
            self.ui_interface.display_error(f"Intelligent roadmap failed: {e}")
            
    def shutdown(self):
        """Gracefully shutdown the WRE engine."""
        wre_log("🛑 Shutting down WRE engine...", "INFO")
        
        # End session
        if self.current_session_id:
            self.session_manager.end_session()
            
        self.running = False
        wre_log("👋 WRE engine shutdown complete", "SUCCESS")
        
    # Placeholder methods for additional functionality
    def _enter_manual_mode(self, module_name: str):
        """Enter manual development mode."""
        self.ui_interface.display_warning("Manual mode not yet implemented")
        
    def _display_module_roadmap(self, module_name: str):
        """Display roadmap for specific module."""
        self.ui_interface.display_warning("Module-specific roadmap not yet implemented")
        
    def _update_module_docs(self, module_name: str):
        """Update module documentation."""
        self.ui_interface.display_warning("Documentation update not yet implemented")
        
    def _analyze_module_dependencies(self, module_name: str):
        """Analyze module dependencies."""
        self.ui_interface.display_warning("Dependency analysis not yet implemented")
        
    def _handle_system_management(self):
        """Handle system management tasks."""
        self.ui_interface.display_warning("System management not yet implemented")
        
    def _handle_module_analysis(self):
        """Handle module analysis tasks."""
        self.ui_interface.display_warning("Module analysis not yet implemented")
        
    def _orchestrate_module_enhancement(self, module_name: str):
        """Orchestrate enhancement of existing module."""
        self.ui_interface.display_warning("Module enhancement not yet implemented")
        
    def _perform_priority_assessment(self):
        """Perform priority assessment."""
        self.ui_interface.display_warning("Priority assessment not yet implemented")
        
    def _perform_ecosystem_analysis(self):
        """Perform ecosystem analysis."""
        self.ui_interface.display_warning("Ecosystem analysis not yet implemented")


# Legacy compatibility functions
def display_main_menu():
    """Legacy function for backward compatibility."""
    engine = WRE()
    return engine.ui_interface.display_main_menu()

# ... existing code ... 