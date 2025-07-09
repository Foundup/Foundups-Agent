"""
Menu Handler Component

Handles all menu selection logic and user interaction processing.
Extracted from engine.py to follow WSP modularity principles.

WSP Compliance:
- Single responsibility: Menu processing and routing
- Clean interfaces: Delegates to appropriate components
- Modular cohesion: Only menu-related logic
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import sys

from modules.wre_core.src.utils.logging_utils import wre_log
from modules.wre_core.src.components.module_development.module_development_coordinator import ModuleDevelopmentCoordinator

class MenuHandler:
    """
    Menu Handler - Processes user menu selections
    
    Responsibilities:
    - Parse menu choices
    - Route to appropriate handlers
    - Handle module development workflows
    - Manage system operations routing
    """
    
    def __init__(self, project_root: Path, ui_interface, session_manager):
        self.project_root = project_root
        self.ui_interface = ui_interface
        self.session_manager = session_manager
        self.module_dev_coordinator = ModuleDevelopmentCoordinator(project_root, session_manager)
        
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
            # New Module
            self._handle_new_module_creation(engine)
            
        elif choice == str(num_modules + 2):
            # System management
            self._handle_system_management(engine)
            
        elif choice == str(num_modules + 3):
            # Follow WSP (ModLog + Git Push)
            self._follow_wsp_compliance(engine)
            
        elif choice == str(num_modules + 4):
            # Adjust Rider Influence
            self._handle_rider_influence_adjustment(engine)
            
    def _handle_module_development(self, module_name: str, engine):
        """Handle module-specific development workflow."""
        wre_log(f"🏗️ Entering module development for: {module_name}", "INFO")
        self.session_manager.log_module_access(module_name, "development")
        
        # Special handling for YouTube module - redirect to main.py
        if module_name == "youtube_module":
            wre_log("📺 YouTube module selected - redirecting to main.py", "INFO")
            self.ui_interface.display_success("Launching FoundUps Agent main.py for YouTube module...")
            
            try:
                # Launch main.py in the same terminal
                subprocess.run([sys.executable, "main.py"], cwd=self.project_root)
            except Exception as e:
                wre_log(f"❌ Failed to launch main.py: {e}", "ERROR")
                self.ui_interface.display_error(f"Failed to launch main.py: {e}")
        else:
            # Use module development coordinator
            self.module_dev_coordinator.handle_module_development(module_name, engine)
            
    def _handle_wsp30_orchestration(self, engine):
        """Handle WSP_30 Agentic Module Build Orchestration."""
        wre_log("🎯 WSP_30 Agentic Module Build Orchestration", "INFO")
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
        wre_log(f"🤖 Starting agentic build for: {module_name}", "INFO")
        
        try:
            # Use orchestrator to start build
            success = orchestrator.start_agentic_build(module_name)
            
            if success:
                self.ui_interface.display_success(f"Agentic build started for {module_name}")
                self.session_manager.log_achievement("agentic_build_started", f"Build started for {module_name}")
            else:
                self.ui_interface.display_error(f"Failed to start agentic build for {module_name}")
                
        except Exception as e:
            wre_log(f"❌ Agentic build failed: {e}", "ERROR")
            self.ui_interface.display_error(f"Agentic build failed: {e}")
            
    def _orchestrate_new_module(self, module_name: str, orchestrator):
        """Orchestrate creation of a new module."""
        wre_log(f"🎼 Orchestrating new module: {module_name}", "INFO")
        
        try:
            # Use orchestrator to create new module
            success = orchestrator.orchestrate_new_module(module_name)
            
            if success:
                self.ui_interface.display_success(f"New module {module_name} orchestrated successfully")
                self.session_manager.log_achievement("new_module_orchestrated", f"Module {module_name} created")
            else:
                self.ui_interface.display_error(f"Failed to orchestrate new module {module_name}")
                
        except Exception as e:
            wre_log(f"❌ Module orchestration failed: {e}", "ERROR")
            self.ui_interface.display_error(f"Module orchestration failed: {e}")
            
    def _enter_manual_mode(self, module_name: str, engine):
        """Enter manual development mode for a module."""
        wre_log(f"🔧 Entering manual mode for: {module_name}", "INFO")
        self.session_manager.log_operation("manual_mode", {"module": module_name})
        
        # Use module development coordinator for manual mode
        self.module_dev_coordinator.manual_mode_manager.enter_manual_mode(module_name, engine)
        
    def _display_roadmap(self, engine):
        """Display development roadmap."""
        wre_log("🗺️ Displaying development roadmap", "INFO")
        
        try:
            # Get module prioritizer from engine
            prioritizer = engine.get_module_prioritizer()
            
            # Generate and display roadmap
            roadmap = prioritizer.generate_development_roadmap()
            self.ui_interface.display_roadmap(roadmap)
            
        except Exception as e:
            wre_log(f"❌ Failed to display roadmap: {e}", "ERROR")
            self.ui_interface.display_error(f"Failed to display roadmap: {e}")
            
    def _handle_system_management(self, engine):
        """Handle system management operations."""
        wre_log("⚙️ System management", "INFO")
        
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
        wre_log("📊 Displaying session status", "INFO")
        
        try:
            # Get session manager from engine
            session_manager = engine.get_session_manager()
            
            # Get session status
            status = session_manager.get_session_status()
            self.ui_interface.display_session_status(status)
            
        except Exception as e:
            wre_log(f"❌ Failed to display session status: {e}", "ERROR")
            self.ui_interface.display_error(f"Failed to display session status: {e}")
            
    def _handle_module_analysis(self, engine):
        """Handle module analysis operations."""
        wre_log("🔍 Module analysis", "INFO")
        
        # Get module analyzer from engine
        module_analyzer = engine.module_analyzer
        
        # Display analysis menu
        self.ui_interface.display_module_analysis_menu()
        
        # Get user choice
        analysis_choice = self.ui_interface.get_user_input("Select analysis option: ")
        
        # Route to module analyzer
        module_analyzer.handle_analysis_choice(analysis_choice, engine)
        
    def _handle_new_module_creation(self, engine):
        """Handle new module creation."""
        wre_log("🎼 Creating new module", "INFO")
        
        # Get new module details
        module_name = self.ui_interface.get_user_input("Enter new module name: ")
        domain = self.ui_interface.get_user_input("Enter module domain: ")
        path = self.ui_interface.get_user_input("Enter module path: ")
        
        # Create new module
        self.module_dev_coordinator.create_new_module(module_name, domain, path)
        
        self.ui_interface.display_success(f"New module {module_name} created successfully")
        self.session_manager.log_achievement("new_module_created", f"Module {module_name} created")
        
    def _follow_wsp_compliance(self, engine):
        """Follow WSP compliance workflow (ModLog + Git Push)."""
        wre_log("📋 Following WSP compliance workflow", "INFO")
        
        # Get system manager from engine
        system_manager = engine.system_manager
        
        # Execute WSP compliance workflow
        system_manager.execute_wsp_compliance_workflow(engine)
        
    def _handle_rider_influence_adjustment(self, engine):
        """Handle rider influence adjustment."""
        wre_log("🎯 Handling rider influence adjustment", "INFO")
        self.session_manager.log_operation("rider_influence", {"action": "start"})
        
        try:
            # Display rider influence menu
            result = engine.ui_interface.display_rider_influence_menu()
            
            if result["action"] == "1":
                # Adjust specific module influence
                module_name = result["module_name"]
                new_influence = result["new_influence"]
                
                wre_log(f"🎯 Adjusting rider influence for {module_name} to {new_influence}", "INFO")
                
                # Update the YAML file
                self._update_rider_influence_in_yaml(module_name, new_influence)
                
                # Reload scoring engine
                from tools.shared.module_scoring_engine import WSP37ScoringEngine
                scoring_engine = WSP37ScoringEngine()
                scoring_engine.load_modules()
                
                self.ui_interface.display_success(f"Rider influence for {module_name} updated to {new_influence}/5")
                self.session_manager.log_achievement("rider_influence_updated", f"Updated {module_name} influence to {new_influence}")
                
            elif result["action"] == "2":
                # View influence impact
                self._display_influence_impact(engine)
                
            elif result["action"] == "3":
                # Reset all influences
                self._reset_all_rider_influences(engine)
                
        except Exception as e:
            wre_log(f"❌ Rider influence adjustment failed: {e}", "ERROR")
            self.ui_interface.display_error(f"Rider influence adjustment failed: {e}")
            
    def _update_rider_influence_in_yaml(self, module_name: str, new_influence: int):
        """Update rider influence in the YAML file."""
        import yaml
        
        yaml_file = self.project_root / "modules_to_score.yaml"
        
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Find and update the module
        for module in data['modules']:
            if module['name'] == module_name:
                if 'scores' not in module:
                    module['scores'] = {}
                module['scores']['rider_influence'] = new_influence
                
                # Recalculate MPS score
                mps_score = sum([
                    module['scores'].get('complexity', 0),
                    module['scores'].get('importance', 0),
                    module['scores'].get('deferability', 0),
                    module['scores'].get('impact', 0),
                    module['scores'].get('rider_influence', 0)
                ])
                module['mps_score'] = mps_score
                break
        
        # Write back to file
        with open(yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, indent=2)
            
    def _display_influence_impact(self, engine):
        """Display how rider influence affects priorities."""
        wre_log("📊 Displaying rider influence impact", "INFO")
        
        try:
            from tools.shared.module_scoring_engine import WSP37ScoringEngine
            scoring_engine = WSP37ScoringEngine()
            
            # Get P0 modules sorted by score
            p0_modules = scoring_engine.get_priority_modules("P0")
            
            self.ui_interface.display_success("Current P0 Priority Order (with rider influence):")
            for i, module in enumerate(p0_modules, 1):
                influence = module.rider_influence if hasattr(module, 'rider_influence') else 0
                print(f"{i}. {module.name} - Score: {module.mps_score} (Rider: {influence}/5)")
                
        except Exception as e:
            wre_log(f"❌ Failed to display influence impact: {e}", "ERROR")
            
    def _reset_all_rider_influences(self, engine):
        """Reset all rider influences to default."""
        wre_log("🔄 Resetting all rider influences", "INFO")
        
        try:
            import yaml
            
            yaml_file = self.project_root / "modules_to_score.yaml"
            
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Reset all rider influences to 0
            for module in data['modules']:
                if 'scores' in module:
                    module['scores']['rider_influence'] = 0
                    
                    # Recalculate MPS score
                    mps_score = sum([
                        module['scores'].get('complexity', 0),
                        module['scores'].get('importance', 0),
                        module['scores'].get('deferability', 0),
                        module['scores'].get('impact', 0),
                        module['scores'].get('rider_influence', 0)
                    ])
                    module['mps_score'] = mps_score
            
            # Write back to file
            with open(yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, indent=2)
                
            self.ui_interface.display_success("All rider influences reset to default")
            self.session_manager.log_achievement("rider_influence_reset", "All influences reset to default")
            
        except Exception as e:
            wre_log(f"❌ Failed to reset rider influences: {e}", "ERROR")
            self.ui_interface.display_error(f"Failed to reset rider influences: {e}") 