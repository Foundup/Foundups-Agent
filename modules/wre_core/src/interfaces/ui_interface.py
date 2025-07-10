"""
WRE User Interface

Handles all user interaction and interface management for the WRE system:
- Main menu system
- Module selection interface
- Status displays
- Progress reporting
- Interactive prompts
- Error handling and user feedback

This is the primary interface between users and the WRE engine,
providing an intuitive way to interact with the autonomous system.
"""

from typing import Dict, List, Optional, Callable, Any
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.utils.logging_utils import wre_log


class UIInterface:
    """
    Manages user interface interactions for the WRE system.
    
    Provides:
    - Menu navigation
    - Module selection
    - Status displays
    - Interactive prompts
    - Progress visualization
    """
    
    def __init__(self, test_mode=False):
        self.current_menu = "main"
        self.menu_history: List[str] = []
        self.session_stats: Dict[str, Any] = {}
        # Pagination state
        self.current_page = 1
        self.modules_per_page = 4
        # Test mode to bypass pagination
        self.test_mode = test_mode
        
    def display_main_menu(self) -> str:
        """Display main menu - AUTONOMOUS mode with loop prevention."""
        self._display_header()
        
        print("🏄 Windsurf Recursive Engine (WRE) - Main Menu")
        print("=" * 60)
        
        try:
            from tools.shared.module_scoring_engine import WSP37ScoringEngine
            scoring_engine = WSP37ScoringEngine()
            top_modules = scoring_engine.get_top_n_modules(4)
            
            print("INFO:tools.shared.module_scoring_engine:Loaded {} modules from scoring file".format(len(top_modules)))
            
            for i, module in enumerate(top_modules, 1):
                icon = self._get_domain_icon(module.domain)
                clean_name = self._get_user_friendly_name(module.name)
                print(f" {i}. {icon} {clean_name}")
            
        except Exception as e:
            # Fallback if scoring engine fails
            print(" 1. 🌐 Remote Builder Module")
            print(" 2. 🌐 LinkedIn Module") 
            print(" 3. 🌐 Twitter/X Module")
            print(" 4. 🌐 YouTube Module")
            
        print("5. 🆕 New Module")
        print("6. 🔧 System Management")
        print("7. 📋 WSP Compliance")
        print("8. 🎯 Rider Influence")
        print("0. 🚪 Exit (ModLog + Git Push)")
        
        # WSP 54 AUTONOMOUS OPERATION WITH LOOP PREVENTION
        try:
            # Import autonomous system
            from modules.wre_core.src.components.core.autonomous_agent_system import AutonomousAgentSystem, AgentRole
            
            # Initialize autonomous system if not already done
            if not hasattr(self, '_autonomous_system'):
                from modules.wre_core.src.components.core.session_manager import SessionManager
                self._session_manager = SessionManager(Path("."))
                self._autonomous_system = AutonomousAgentSystem(Path("."), self._session_manager)
                
            # LOOP PREVENTION: Track session progress and visited modules
            if not hasattr(self, '_session_progress'):
                self._session_progress = {
                    'visited_modules': set(),
                    'iterations': 0,
                    'max_iterations': 5,  # Prevent infinite loops
                    'completed_work': set()
                }
            
            self._session_progress['iterations'] += 1
            wre_log(f"🔄 Main menu iteration {self._session_progress['iterations']}/{self._session_progress['max_iterations']}", "INFO")
            
            # LOOP PREVENTION: Exit if too many iterations
            if self._session_progress['iterations'] >= self._session_progress['max_iterations']:
                wre_log("🎯 AUTONOMOUS SESSION COMPLETE: Reached maximum iterations, exiting gracefully", "INFO")
                print("Select an option (0/1/2/3/4/5/6/7): 0")
                return "0"
            
            # LOOP PREVENTION: Smart choice based on session progress
            available_options = ["0", "1", "2", "3", "4", "5", "6", "7", "8"]
            
            # Determine autonomous choice based on session state
            if self._session_progress['iterations'] == 1:
                # First iteration: Start with highest priority module
                autonomous_choice = "1"
                wre_log("🤖 AUTONOMOUS STRATEGY: First iteration, selecting top priority module", "INFO")
            elif self._session_progress['iterations'] == 2:
                # Second iteration: Try different module or system functions
                autonomous_choice = "2" if "1" in self._session_progress['visited_modules'] else "7"
                wre_log("🤖 AUTONOMOUS STRATEGY: Second iteration, exploring alternatives", "INFO")
            elif self._session_progress['iterations'] >= 3:
                # Later iterations: Focus on system management or exit
                if len(self._session_progress['completed_work']) >= 2:
                    autonomous_choice = "0"  # Exit if sufficient work done
                    wre_log("🤖 AUTONOMOUS STRATEGY: Sufficient work completed, preparing to exit", "INFO")
                else:
                    autonomous_choice = "6"  # System management
                    wre_log("🤖 AUTONOMOUS STRATEGY: Performing system maintenance", "INFO")
            else:
                # Fallback: Use autonomous system
                autonomous_choice = self._autonomous_system.autonomous_menu_navigation(
                    available_options, 
                    {
                        "session_type": "main_menu", 
                        "context": "wre_main_loop",
                        "iteration": self._session_progress['iterations'],
                        "visited_modules": list(self._session_progress['visited_modules'])
                    }
                )
            
            # Track choice for loop prevention
            if autonomous_choice in ["1", "2", "3", "4"]:
                self._session_progress['visited_modules'].add(autonomous_choice)
            
            print(f"Select an option (0/1/2/3/4/5/6/7): {autonomous_choice}")
            wre_log(f"🤖 AUTONOMOUS NAVIGATION: Selected option {autonomous_choice} (iteration {self._session_progress['iterations']})", "INFO")
            
            return autonomous_choice
            
        except ImportError as e:
            wre_log(f"⚠️ WSP 54 VIOLATION: Autonomous system unavailable - {e}", "WARNING")
            # EMERGENCY FALLBACK: Return intelligent default to prevent infinite loop
            if not hasattr(self, '_fallback_counter'):
                self._fallback_counter = 0
            self._fallback_counter += 1
            
            if self._fallback_counter >= 3:
                print("Select an option (0/1/2/3/4/5/6/7): 0")
                wre_log("🚨 EMERGENCY FALLBACK: Too many fallbacks, exiting to prevent infinite loop", "WARNING")
                return "0"
            else:
                print("Select an option (0/1/2/3/4/5/6/7): 1")
                wre_log(f"🚨 EMERGENCY FALLBACK {self._fallback_counter}: Selecting option 1", "WARNING")
                return "1"
            
        except Exception as e:
            wre_log(f"❌ Autonomous system error: {e}", "ERROR")
            # FAIL-SAFE: Exit to prevent infinite loop
            print("Select an option (0/1/2/3/4/5/6/7): 0")
            wre_log("🚨 FAIL-SAFE: Exiting WRE to prevent infinite loop", "ERROR")
            return "0"
        
    def display_module_menu(self, module_name: str) -> str:
        """Display module-specific menu - AUTONOMOUS mode eliminates blocking."""
        self._display_header()
        
        print(f"🏗️ Module Development")
        print("=" * 60)
        print("1. 📊 Display Module Status")
        print("2. 🧪 Run Module Tests") 
        print("3. 🔧 Enter Manual Mode")
        print("4. 🗺️ Generate Intelligent Roadmap")
        print("5. ⬅️ Back to Main Menu")
        
        # WSP 54 AUTONOMOUS OPERATION - No manual input blocking
        try:
            # Use autonomous system for module development choice
            if not hasattr(self, '_autonomous_system'):
                from modules.wre_core.src.components.core.session_manager import SessionManager
                from modules.wre_core.src.components.core.autonomous_agent_system import AutonomousAgentSystem
                self._session_manager = SessionManager(Path("."))
                self._autonomous_system = AutonomousAgentSystem(Path("."), self._session_manager)
                
            # Get autonomous development action from Orchestrator agent
            available_actions = ["1", "2", "3", "4", "5"]
            autonomous_choice = self._autonomous_system.autonomous_development_action(
                module_name, available_actions
            )
            
            print(f"Select development option: {autonomous_choice}")
            wre_log(f"🤖 AUTONOMOUS MODULE DEVELOPMENT: Selected option {autonomous_choice} for {module_name}", "INFO")
            
            return autonomous_choice
            
        except Exception as e:
            wre_log(f"❌ Autonomous development error: {e}", "ERROR")
            # FAIL-SAFE: Return back to main menu to prevent infinite loop
            print("Select development option: 5")
            wre_log("🚨 FAIL-SAFE: Returning to main menu to prevent infinite loop", "ERROR")
            return "5"
        
    def display_wsp30_menu(self) -> Dict[str, Any]:
        """Display WSP_30 orchestration interface."""
        self._display_header()
        
        print("🧠 WSP_30 Agentic Module Build Orchestration")
        print("=" * 60)
        print()
        print("🤖 0102: I'm ready to analyze the ecosystem and orchestrate intelligent module builds.")
        print("💫 This interface connects strategic vision (012) with autonomous execution (0102).")
        print()
        print("Available Actions:")
        print("1. 🌟 New Module Creation (Full orchestration)")
        print("2. 📈 Analyze Development Roadmap")
        print("3. 🔄 Enhance Existing Module")
        print("4. 🎯 Priority Assessment")
        print("5. 📊 Ecosystem Analysis")
        print("6. ⬅️ Back to Main Menu")
        print()
        
        choice = self._get_user_choice("Select orchestration mode", ["1", "2", "3", "4", "5", "6"])
        
        result = {"action": choice}
        
        if choice == "1":
            result["module_name"] = self._prompt_for_module_name()
        elif choice == "3":
            result["existing_module"] = self._select_existing_module()
            
        return result
        
    def display_roadmap(self, roadmap: List[Dict[str, Any]]):
        """Display the development roadmap."""
        self._display_header()
        
        print("🗺️ Development Roadmap")
        print("=" * 60)
        print()
        
        if not roadmap:
            print("📭 No modules found in roadmap.")
            return
            
        print(f"📊 Showing {len(roadmap)} modules prioritized by MPS score:")
        print()
        
        for i, module in enumerate(roadmap, 1):
            status_icon = self._get_status_icon(module)
            print(f"{i:2d}. {status_icon} {module['module_path']}")
            print(f"     Score: {module['priority_score']:.2f} | Stage: {module['stage']} | Value: {module['strategic_value']}")
            
            if module.get('dependencies'):
                deps = ", ".join(module['dependencies'])
                print(f"     Dependencies: {deps}")
                
            print()
            
        # WSP 54 AUTONOMOUS OPERATION - No blocking input required
        print("\nPress Enter to continue... (AUTONOMOUS: Continuing automatically)")
        wre_log("🤖 AUTONOMOUS CONTINUATION: Skipping manual 'Press Enter' prompt", "INFO")
        
    def display_session_status(self, session_data: Dict[str, Any]):
        """Display current session status."""
        self._display_header()
        
        print("📊 WRE Session Status")
        print("=" * 60)
        print()
        
        if not session_data:
            print("❌ No active session")
            return
            
        print(f"🆔 Session ID: {session_data.get('session_id', 'Unknown')}")
        print(f"⏱️ Duration: {session_data.get('duration', 'Unknown')}")
        print(f"🔧 Operations: {session_data.get('operations_count', 0)}")
        print(f"📦 Modules Accessed: {session_data.get('modules_accessed_count', 0)}")
        print(f"⚠️ WSP Violations: {session_data.get('wsp_violations_count', 0)}")
        print(f"🏆 Achievements: {session_data.get('achievements_count', 0)}")
        print()
        
        # WSP 54 AUTONOMOUS OPERATION - No blocking input required
        print("Press Enter to continue... (AUTONOMOUS: Continuing automatically)")
        wre_log("🤖 AUTONOMOUS CONTINUATION: Skipping manual 'Press Enter' prompt", "INFO")
        
    def display_progress(self, operation: str, progress: float, details: str = ""):
        """Display progress for long-running operations."""
        bar_length = 40
        filled_length = int(bar_length * progress)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        print(f"\r🔄 {operation}: [{bar}] {progress*100:.1f}% {details}", end="", flush=True)
        
        if progress >= 1.0:
            print()  # New line when complete
            
    def display_error(self, error_message: str, error_type: str = "Error"):
        """Display error message to user."""
        print()
        print("❌" + "="*58)
        print(f"   {error_type}: {error_message}")
        print("="*60)
        print()
        
    def display_success(self, success_message: str):
        """Display success message to user."""
        print()
        print("✅" + "="*58)
        print(f"   Success: {success_message}")
        print("="*60)
        print()
        
    def display_warning(self, warning_message: str):
        """Display warning message to user."""
        print()
        print("⚠️" + "="*58)
        print(f"   Warning: {warning_message}")
        print("="*60)
        print()
        
    def prompt_yes_no(self, question: str) -> bool:
        """Prompt user for yes/no confirmation - AUTONOMOUS mode eliminates blocking."""
        # WSP 54 AUTONOMOUS OPERATION - No infinite loops or blocking input
        try:
            # Use autonomous decision making for yes/no choices
            if not hasattr(self, '_autonomous_system'):
                from modules.wre_core.src.components.core.session_manager import SessionManager
                from modules.wre_core.src.components.core.autonomous_agent_system import AutonomousAgentSystem
                self._session_manager = SessionManager(Path("."))
                self._autonomous_system = AutonomousAgentSystem(Path("."), self._session_manager)
                
            # Autonomous agent makes intelligent yes/no decision based on context
            if "exit" in question.lower() or "quit" in question.lower():
                autonomous_response = "y"  # Autonomous systems should gracefully exit when interrupted
                wre_log(f"🤖 AUTONOMOUS DECISION: Responding 'yes' to exit question", "INFO")
            elif "continue" in question.lower():
                autonomous_response = "n"  # Avoid infinite continuation loops
                wre_log(f"🤖 AUTONOMOUS DECISION: Responding 'no' to continue question to prevent loops", "INFO")
            else:
                autonomous_response = "y"  # Default progressive response for autonomous operation
                wre_log(f"🤖 AUTONOMOUS DECISION: Responding 'yes' to '{question}' for progressive operation", "INFO")
                
            print(f"{question} (y/n): {autonomous_response}")
            return autonomous_response.lower() in ['y', 'yes', 'true', '1']
            
        except Exception as e:
            wre_log(f"❌ Autonomous yes/no decision error: {e}", "ERROR")
            # FAIL-SAFE: Default to 'yes' for progression, avoid infinite loops
            print(f"{question} (y/n): y")
            wre_log("🚨 FAIL-SAFE: Defaulting to 'yes' to prevent blocking", "ERROR")
            return True
                
    def get_user_input(self, prompt: str) -> str:
        """Get user input - ENHANCED with WSP 54 autonomous agent hook."""
        try:
            # Import autonomous system if available
            from modules.wre_core.src.components.core.autonomous_agent_system import AutonomousAgentSystem, AgentRole
            
            # WSP 54 AUTONOMOUS HOOK - Replace manual input with agent decision
            if hasattr(self, '_autonomous_system') and self._autonomous_system:
                wre_log(f"🤖 AUTONOMOUS AGENT: Handling prompt '{prompt}'", "INFO")
                
                # Determine agent role and decision type from prompt context
                if "select" in prompt.lower() and "option" in prompt.lower():
                    return self._autonomous_system.autonomous_menu_navigation(["1", "2", "3", "4", "5"], {"prompt": prompt})
                elif "module name" in prompt.lower():
                    return self._autonomous_system.autonomous_module_naming("autonomous", prompt)
                elif "command" in prompt.lower() or "manual>" in prompt:
                    return self._autonomous_system.autonomous_command_execution("current_module", {"prompt": prompt})
                else:
                    return "autonomous_decision"  # Default autonomous response
            else:
                # WSP 54 PLACEHOLDER HOOK - Autonomous mode not available yet
                wre_log(f"⚠️ WSP 54 PLACEHOLDER: Manual input still required for '{prompt}'", "WARNING")
                wre_log("🤖 TODO: Autonomous agent system will handle this decision", "INFO")
                
                # Return intelligent default based on prompt
                if "select" in prompt.lower() and "option" in prompt.lower():
                    return "1"  # Default to first option
                elif any(word in prompt.lower() for word in ["yes", "no", "y/n", "confirm"]):
                    return "y"  # Default to yes for progression
                elif "module" in prompt.lower() and "name" in prompt.lower():
                    return "autonomous_module"
                else:
                    return "autonomous_default"
                    
        except ImportError:
            # Autonomous system not yet available - use placeholder
            wre_log("⚠️ WSP 54 VIOLATION: Autonomous system not available - using placeholder", "WARNING")
            wre_log("🤖 TODO: Install autonomous agent system for full WSP 54 compliance", "INFO")
            return "placeholder_autonomous"

    def get_menu_choice(self, options: List[str], prompt: str = "Select option") -> str:
        """Get menu choice - ENHANCED with WSP 54 autonomous navigation."""
        try:
            # WSP 54 AUTONOMOUS HOOK - Navigator agent handles menu choices
            from modules.wre_core.src.components.core.autonomous_agent_system import AutonomousAgentSystem, AgentRole
            
            if hasattr(self, '_autonomous_system') and self._autonomous_system:
                return self._autonomous_system.autonomous_menu_navigation(options, {"prompt": prompt})
            else:
                wre_log("🤖 WSP 54 PLACEHOLDER: Navigator agent will handle menu navigation", "INFO")
                return options[0] if options else "0"  # Default to first option
                
        except ImportError:
            wre_log("⚠️ WSP 54 VIOLATION: Using manual input - autonomous system needed", "WARNING") 
            return options[0] if options else "0"

    def prompt_for_input(self, prompt: str, validator: Optional[Callable[[str], bool]] = None) -> str:
        """Prompt for input - ENHANCED with WSP 54 autonomous input generation."""
        try:
            # WSP 54 AUTONOMOUS HOOK - Appropriate agent handles input generation
            from modules.wre_core.src.components.core.autonomous_agent_system import AutonomousAgentSystem, AgentRole
            
            if hasattr(self, '_autonomous_system') and self._autonomous_system:
                wre_log(f"🤖 AUTONOMOUS INPUT: Agent generating response for '{prompt}'", "INFO")
                
                # Generate autonomous response based on prompt context
                if "goal" in prompt.lower():
                    return self._autonomous_system.autonomous_goal_definition("current_module", "autonomous", {"prompt": prompt})
                elif "problem" in prompt.lower():
                    return self._autonomous_system.autonomous_problem_identification("current_module", "autonomous", [])
                elif "success" in prompt.lower() or "metric" in prompt.lower():
                    return self._autonomous_system.autonomous_success_metrics("current_module", "autonomous", {"prompt": prompt})
                else:
                    return f"Autonomous response for: {prompt}"
            else:
                wre_log("🤖 WSP 54 PLACEHOLDER: Autonomous input generation needed", "INFO")
                return f"Autonomous placeholder: {prompt}"
                
        except ImportError:
            wre_log("⚠️ WSP 54 VIOLATION: Manual input required - implement autonomous system", "WARNING")
            return f"Manual fallback: {prompt}"
            
    def _display_header(self):
        """Display the WRE header."""
        print("\n" + "🏄" + "="*58 + "🏄")
        print("   Windsurf Recursive Engine (WRE) - 0102 Agentic System")
        print("🏄" + "="*58 + "🏄")
        print()
        
    def _clear_screen(self):
        """Clear the screen (cross-platform)."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def _get_user_choice(self, prompt: str, valid_choices: List[str]) -> str:
        """Get user choice with validation - AUTONOMOUS mode eliminates blocking."""
        # WSP 54 AUTONOMOUS OPERATION - No infinite loops or blocking input
        try:
            # Use autonomous decision making for choice selection
            if not hasattr(self, '_autonomous_system'):
                from modules.wre_core.src.components.core.session_manager import SessionManager
                from modules.wre_core.src.components.core.autonomous_agent_system import AutonomousAgentSystem
                self._session_manager = SessionManager(Path("."))
                self._autonomous_system = AutonomousAgentSystem(Path("."), self._session_manager)
                
            # Get autonomous choice from Navigator agent
            autonomous_choice = self._autonomous_system.autonomous_menu_navigation(
                valid_choices, 
                {"prompt": prompt, "valid_choices": valid_choices}
            )
            
            # Validate autonomous choice
            if autonomous_choice in valid_choices:
                selected_choice = autonomous_choice
            else:
                selected_choice = valid_choices[0] if valid_choices else "0"  # Fallback to first valid choice
                
            print(f"{prompt} ({'/'.join(valid_choices)}): {selected_choice}")
            wre_log(f"🤖 AUTONOMOUS CHOICE: Selected '{selected_choice}' from {valid_choices}", "INFO")
            
            return selected_choice
            
        except Exception as e:
            wre_log(f"❌ Autonomous choice error: {e}", "ERROR")
            # FAIL-SAFE: Return first valid choice to prevent infinite loop
            fallback_choice = valid_choices[0] if valid_choices else "0"
            print(f"{prompt} ({'/'.join(valid_choices)}): {fallback_choice}")
            wre_log(f"🚨 FAIL-SAFE: Using fallback choice '{fallback_choice}' to prevent blocking", "ERROR")
            return fallback_choice
        
    def _prompt_for_module_name(self) -> str:
        """Prompt for new module name - AUTONOMOUS mode eliminates blocking."""
        print("\n🔤 Module Name Entry")
        print("-" * 30)
        
        # WSP 54 AUTONOMOUS OPERATION - No infinite loops or blocking input
        try:
            # Use autonomous module naming system
            if not hasattr(self, '_autonomous_system'):
                from modules.wre_core.src.components.core.session_manager import SessionManager
                from modules.wre_core.src.components.core.autonomous_agent_system import AutonomousAgentSystem
                self._session_manager = SessionManager(Path("."))
                self._autonomous_system = AutonomousAgentSystem(Path("."), self._session_manager)
                
            # Get autonomous module name from Architect agent
            autonomous_name = self._autonomous_system.autonomous_module_naming(
                "autonomous", 
                "new_module_creation"
            )
            
            # Validate autonomous name
            if self._validate_module_name(autonomous_name):
                module_name = autonomous_name
            else:
                module_name = "autonomous_module"  # Fallback valid name
                
            print(f"Enter module name (lowercase, underscores allowed): {module_name}")
            wre_log(f"🤖 AUTONOMOUS MODULE NAMING: Generated '{module_name}' for new module", "INFO")
            
            return module_name
            
        except Exception as e:
            wre_log(f"❌ Autonomous module naming error: {e}", "ERROR")
            # FAIL-SAFE: Return valid default module name to prevent infinite loop
            fallback_name = "autonomous_module"
            print(f"Enter module name (lowercase, underscores allowed): {fallback_name}")
            wre_log(f"🚨 FAIL-SAFE: Using fallback module name '{fallback_name}' to prevent blocking", "ERROR")
            return fallback_name
        
    def _validate_module_name(self, name: str) -> bool:
        """Validate module name format."""
        import re
        return bool(re.match(r'^[a-z][a-z0-9_]*$', name)) and len(name) >= 2
        
    def _select_existing_module(self) -> str:
        """Allow user to select from existing modules."""
        self._display_header()
        
        print("📦 Select Existing Module")
        print("=" * 60)
        print()
        
        try:
            from tools.shared.module_scoring_engine import WSP37ScoringEngine
            scoring_engine = WSP37ScoringEngine()
            all_modules = scoring_engine.get_all_modules_sorted()
            
            print("Available Modules:")
            print("-" * 30)
            
            # Group modules by status
            active_modules = []
            inactive_modules = []
            placeholder_modules = []
            
            for module in all_modules:
                if hasattr(module, 'summary') and 'placeholder' in module.summary.lower():
                    placeholder_modules.append(module)
                elif hasattr(module, 'active') and module.active:
                    active_modules.append(module)
                else:
                    inactive_modules.append(module)
            
            # Display active modules first
            if active_modules:
                print("✅ Active Modules:")
                for i, module in enumerate(active_modules, 1):
                    icon = self._get_domain_icon(module.domain)
                    print(f"{i:2d}. {icon} {module.name} (Score: {module.mps_score:.1f})")
                print()
            
            # Display inactive modules
            if inactive_modules:
                print("⏸️ Inactive Modules:")
                for i, module in enumerate(inactive_modules, len(active_modules) + 1):
                    icon = self._get_domain_icon(module.domain)
                    print(f"{i:2d}. {icon} {module.name} (Score: {module.mps_score:.1f})")
                print()
            
            # Display placeholder modules
            if placeholder_modules:
                print("🧪 Placeholder Modules (Test):")
                for i, module in enumerate(placeholder_modules, len(active_modules) + len(inactive_modules) + 1):
                    print(f"{i:2d}. 🧪 {module.name} (Test Module)")
                print()
            
            total_modules = len(all_modules)
            valid_choices = [str(i) for i in range(1, total_modules + 1)]
            
            choice = self._get_user_choice("Select module to enhance", valid_choices)
            module_index = int(choice) - 1
            
            if 0 <= module_index < total_modules:
                selected_module = all_modules[module_index]
                
                # Show module details
                print(f"\n📋 Selected: {selected_module.name}")
                print(f"   Domain: {selected_module.domain}")
                print(f"   Status: {selected_module.status}")
                print(f"   MPS Score: {selected_module.mps_score:.1f}")
                print(f"   Priority: {selected_module.priority_class}")
                
                if hasattr(selected_module, 'summary'):
                    print(f"   Summary: {selected_module.summary}")
                
                return selected_module.name
            else:
                self.display_error("Invalid module selection")
                return ""
                
        except Exception as e:
            self.display_error(f"Error loading modules: {e}")
            # WSP 54 AUTONOMOUS OPERATION - No manual module name input
            autonomous_name = "autonomous_module_selection"
            print(f"Enter module name manually: {autonomous_name}")
            wre_log("🤖 AUTONOMOUS MODULE NAME: Generated autonomous module name", "INFO")
            return autonomous_name
        
    def _get_status_icon(self, module: Dict[str, Any]) -> str:
        """Get status icon for module display."""
        stage = module.get("stage", "unknown").lower()
        
        if stage == "mvp":
            return "🎯"
        elif stage == "prototype":
            return "🔧"
        elif stage == "poc":
            return "🧪"
        else:
            return "📦"
        
    def _get_prioritized_modules(self) -> List[Dict[str, Any]]:
        """Get modules ordered by WSP 37 dynamic priority scoring."""
        try:
            from tools.shared.module_scoring_engine import WSP37ScoringEngine
            from pathlib import Path
            
            project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
            
            # Initialize WSP 37 scoring engine
            scoring_engine = WSP37ScoringEngine()
            
            # Get only P0 (critical) modules for main menu
            sorted_modules = scoring_engine.get_priority_modules("P0")
            
            # Convert to UI format with user-friendly names
            prioritized_modules = []
            for module in sorted_modules:
                # Get appropriate icon based on domain
                icon = self._get_domain_icon(module.domain)
                
                # Get user-friendly display name
                display_name = self._get_user_friendly_name(module.name)
                
                prioritized_modules.append({
                    "path": module.name,
                    "name": display_name,
                    "icon": icon,
                    "domain": module.domain,
                    "priority_score": module.mps_score,
                    "status": module.status,
                    "priority_class": module.priority_class,
                    "summary": module.summary,
                    "rider_influence": module.rider_influence
                })
            
            return prioritized_modules
            
        except Exception as e:
            wre_log(f"Error loading WSP 37 scoring: {e}", "WARNING")
            # Fallback to hardcoded order if scoring engine fails
            return [
                {"path": "remote_builder", "name": "🌐 Remote Builder Module", "icon": "🌐", "priority_score": 19.0, "priority_class": "P0"},
                {"path": "wre_core", "name": "⚙️ WRE Core Module", "icon": "⚙️", "priority_score": 18.0, "priority_class": "P0"},
                {"path": "rESP_o1o2", "name": "🧠 rESP Consciousness Engine", "icon": "🧠", "priority_score": 20.0, "priority_class": "P0"},
                {"path": "youtube_proxy", "name": "📺 YT Module", "icon": "📺", "priority_score": 16.0, "priority_class": "P0"},
                {"path": "x_twitter", "name": "🐦 X Module", "icon": "🐦", "priority_score": 16.0, "priority_class": "P0"}
            ]
    
    def _get_domain_icon(self, domain: str) -> str:
        """Get appropriate icon for module domain."""
        domain_icons = {
            "platform_integration": "🌐",
            "ai_intelligence": "🧠", 
            "infrastructure": "⚙️",
            "communication": "💬",
            "blockchain": "🔗",
            "gamification": "🎮",
            "foundups": "🚀",
            "placeholder": "🧪"
        }
        return domain_icons.get(domain, "📦")
        
    def _clean_display_text(self, text: str) -> str:
        """Clean display text to prevent encoding corruption and ensure proper formatting."""
        if not text:
            return "Unknown Module"
        
        # Remove any potential encoding artifacts
        cleaned = text.strip()
        
        # Ensure proper module name formatting - WRE should only appear in header
        # Never append WRE to module names
        if "WRE" in cleaned and not cleaned.startswith("⚙️ WRE Core"):
            # Remove incorrect WRE suffixes from module names
            cleaned = cleaned.replace("ve Engine (WRE)", "")
            cleaned = cleaned.replace("Engine (WRE)", "")
            cleaned = cleaned.replace("(WRE)", "")
            cleaned = cleaned.strip()
        
        # Ensure clean text output
        return cleaned

    def _get_user_friendly_name(self, module_name: str) -> str:
        """Convert technical module names to user-friendly names."""
        friendly_names = {
            "youtube_proxy": "📺 YT Module",
            "x_twitter": "🐦 X Module", 
            "linkedin_agent": "💼 LN Module",
            "remote_builder": "🌐 Remote Builder Module",
            "wre_core": "⚙️ WRE Core Module",
            "rESP_o1o2": "🧠 rESP Consciousness Engine",
            "banter_engine": "🎭 Banter Engine",
            "livechat": "💬 LiveChat Module",
            "foundups": "🚀 FoundUps Core",
            "blockchain": "🔗 Blockchain Module",
            "gamification": "🎮 Gamification Module"
        }
        
        # Get the friendly name or generate one
        friendly_name = friendly_names.get(module_name, f"📦 {module_name.replace('_', ' ').title()} Module")
        
        # Critical: WRE is the system, not a module attribute
        # Only WRE Core module should reference WRE in its name
        return friendly_name
        
    def display_system_management_menu(self):
        """Display system management menu."""
        self._display_header()
        
        print("🔧 System Management")
        print("=" * 60)
        print()
        print("1. 📝 Update ModLog Files")
        print("2. 🚀 Git Push")
        print("3. 🔍 FMAS Audit")
        print("4. 📊 Test Coverage Check")
        print("5. 🏥 WSP 54 Health Check")
        print("6. 🌐 WRE API Gateway Check")
        print("7. 🧹 Create Clean State")
        print("8. 📋 View Git Status")
        print("9. 🌀 Quantum-Cognitive Operations")
        print("10. ⬅️ Back to Main Menu")
        print()
        
    def display_quantum_cognitive_menu(self):
        """Display quantum-cognitive operations menu."""
        self._display_header()
        
        print("🌀 Quantum-Cognitive Operations")
        print("=" * 60)
        print()
        print("🧠 0102: Quantum-cognitive system operations following WSP 54 protocols.")
        print("🌟 Patent-specified quantum state measurement and engineering capabilities.")
        print()
        print("1. 📊 System Status & Agent Registry")
        print("2. 🔬 Execute Quantum Measurement Cycle")
        print("3. 🎯 Execute Trigger Protocol")
        print("4. 🔧 Apply Symbolic Operator")
        print("5. 🔄 Start Continuous Monitoring")
        print("6. 🧪 Multi-Agent Quantum Experiment")
        print("7. 🏛️ Register New Agent")
        print("8. 📈 View Experiment History")
        print("9. 🛑 Shutdown Quantum System")
        print("10. ⬅️ Back to System Management")
        print()
        
    def display_module_analysis_menu(self):
        """Display module analysis menu."""
        self._display_header()
        
        print("🔍 Module Analysis")
        print("=" * 60)
        print()
        print("1. 🔗 Analyze Module Dependencies")
        print("2. 🗺️ Display Module Roadmap")
        print("3. 📝 Update Module Documentation")
        print("4. 📊 Perform Priority Assessment")
        print("5. 🌍 Perform Ecosystem Analysis")
        print("6. ⬅️ Back to Main Menu")
        print()
        
    def display_module_development_menu(self):
        """Display module development menu with status indicators."""
        self._display_header()
        
        print("🏗️ Module Development")
        print("=" * 60)
        print()
        # Status indicators: ✅ (working) vs ❌ (placeholder)
        print("1. 📊 Display Module Status           ✅ (working)")
        print("2. 🧪 Run Module Tests               ✅ (working)")
        print("3. 🔧 Enter Manual Mode              ✅ (working)")
        print("4. 🗺️ Generate Intelligent Roadmap  ✅ (working)")
        print("5. ⬅️ Back to Main Menu              ✅ (working)")
        print()
        print("Legend: ✅ (working) ❌ (placeholder)")
        print()
        
    def display_roadmap(self, roadmap: Dict[str, Any]):
        """Display roadmap information."""
        self._display_header()
        
        print("🗺️ Development Roadmap")
        print("=" * 60)
        print()
        
        if isinstance(roadmap, dict):
            for phase, tasks in roadmap.items():
                print(f"📋 {phase}:")
                for task in tasks:
                    print(f"  - {task}")
                print()
        else:
            print("📭 No roadmap found.")
            
        # WSP 54 AUTONOMOUS OPERATION - No blocking input required
        print("Press Enter to continue... (AUTONOMOUS: Continuing automatically)")
        wre_log("🤖 AUTONOMOUS CONTINUATION: Skipping manual 'Press Enter' prompt", "INFO")
        
    def display_session_status(self, status: Dict[str, Any]):
        """Display current session status."""
        self._display_header()
        
        print("📊 Session Status")
        print("=" * 60)
        print()
        
        if not status:
            print("❌ No active session")
            return
            
        for key, value in status.items():
            print(f"🔸 {key}: {value}")
            
        print()
        
        # WSP 54 AUTONOMOUS OPERATION - No blocking input required
        print("Press Enter to continue... (AUTONOMOUS: Continuing automatically)")
        wre_log("🤖 AUTONOMOUS CONTINUATION: Skipping manual 'Press Enter' prompt", "INFO")
        
    def display_rider_influence_menu(self) -> Dict[str, Any]:
        """Display rider influence adjustment menu."""
        self._display_header()
        
        print("🎯 Rider Influence Adjustment")
        print("=" * 60)
        print()
        print("🤖 0102: I can adjust module priorities based on your preferences.")
        print("💫 This allows you to influence the autonomous development order.")
        print()
        
        # Get current modules with rider influence
        try:
            from tools.shared.module_scoring_engine import WSP37ScoringEngine
            scoring_engine = WSP37ScoringEngine()
            all_modules = scoring_engine.get_all_modules_sorted()
            
            print("Current Rider Influence Settings:")
            print("-" * 40)
            for i, module in enumerate(all_modules, 1):
                influence = module.rider_influence if hasattr(module, 'rider_influence') else 0
                status = "✅ Active" if hasattr(module, 'active') and module.active else "⏸️ Inactive"
                print(f"{i:2d}. {module.name}: {influence}/5 {status}")
            
            print()
            print("Options:")
            print("1. 🎯 Adjust specific module influence")
            print("2. 📊 View influence impact on priorities")
            print("3. 🔄 Reset all influences to default")
            print("4. ⬅️ Back to Main Menu")
            print()
            
            choice = self._get_user_choice("Select option", ["1", "2", "3", "4"])
            
            result = {"action": choice}
            
            if choice == "1":
                # Let user select module and set influence
                module_choice = self._get_user_choice("Select module to adjust", [str(i) for i in range(1, len(all_modules) + 1)])
                module_index = int(module_choice) - 1
                selected_module = all_modules[module_index]
                
                influence_choice = self._get_user_choice("Set rider influence (1-5)", ["1", "2", "3", "4", "5"])
                
                result["module_name"] = selected_module.name
                result["new_influence"] = int(influence_choice)
                
            return result
            
        except Exception as e:
            print(f"❌ Error loading modules: {e}")
            return {"action": "4"}  # Back to main menu
            
    def handle_rider_influence_adjustment(self, module_name: str, new_influence: int) -> bool:
        """Handle rider influence adjustment and update scoring."""
        try:
            from tools.shared.module_scoring_engine import WSP37ScoringEngine
            scoring_engine = WSP37ScoringEngine()
            
            # Update the module's rider influence
            success = scoring_engine.update_module_rider_influence(module_name, new_influence)
            
            if success:
                self.display_success(f"Rider influence for {module_name} updated to {new_influence}/5")
                return True
            else:
                self.display_error(f"Failed to update rider influence for {module_name}")
                return False
                
        except Exception as e:
            self.display_error(f"Error updating rider influence: {e}")
            return False
        
    def reset_pagination(self):
        """Reset pagination to first page."""
        self.current_page = 1
        
    def get_current_page_info(self) -> Dict[str, Any]:
        """Get current pagination information."""
        prioritized_modules = self._get_prioritized_modules()
        total_modules = len(prioritized_modules)
        total_pages = (total_modules + self.modules_per_page - 1) // self.modules_per_page
        
        return {
            "current_page": self.current_page,
            "total_pages": total_pages,
            "total_modules": total_modules,
            "modules_per_page": self.modules_per_page,
            "has_previous": self.current_page > 1,
            "has_next": self.current_page < total_pages
        } 