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
        """Display the main WRE menu and return user selection."""
        self._clear_screen()
        self._display_header()
        
        print("🏄 Windsurf Recursive Engine (WRE) - Main Menu")
        print("=" * 60)
        print()
        
        # Get prioritized module list using WSP 37 scoring
        prioritized_modules = self._get_prioritized_modules()
        
        # In test mode, bypass pagination to prevent infinite loops
        if self.test_mode:
            # Display all modules without pagination
            for i, module in enumerate(prioritized_modules, 1):
                icon = module.get('icon', '📦')
                name = module.get('name', module.get('path', 'Unknown'))
                print(f"{i:2d}. {icon} {name}")
            
            # Add system options
            system_start = len(prioritized_modules) + 1
            print(f"{system_start}. 🆕 New Module")
            print(f"{system_start + 1}. 🔧 System Management")
            print(f"{system_start + 2}. 📋 WSP Compliance")
            print(f"{system_start + 3}. 🎯 Rider Influence")
            
            print("0. 🚪 Exit (ModLog + Git Push)")
            print()
            
            # Build valid choices list
            valid_choices = ["0"] + [str(i) for i in range(1, system_start + 3)]
            return self._get_user_choice("Select an option", valid_choices)
        
        # Normal pagination logic
        # Calculate pagination
        total_modules = len(prioritized_modules)
        total_pages = (total_modules + self.modules_per_page - 1) // self.modules_per_page
        
        # Display current page of modules
        start_idx = (self.current_page - 1) * self.modules_per_page
        end_idx = min(start_idx + self.modules_per_page, total_modules)
        current_page_modules = prioritized_modules[start_idx:end_idx]
        
        # Display modules for current page
        for i, module in enumerate(current_page_modules, start_idx + 1):
            icon = module.get('icon', '📦')
            name = module.get('name', module.get('path', 'Unknown'))
            
            print(f"{i:2d}. {icon} {name}")
        
        # Display pagination controls if needed
        if total_pages > 1:
            print()
            print(f"📄 Page {self.current_page} of {total_pages} ({total_modules} total modules)")
            if self.current_page > 1:
                print(f"   [P] Previous page")
            if self.current_page < total_pages:
                print(f"   [N] Next page")
            print()
        
        # Add system options
        system_start = total_modules + 1
        print(f"{system_start}. 🆕 New Module")
        print(f"{system_start + 1}. 🔧 System Management")
        print(f"{system_start + 2}. 📋 WSP Compliance")
        print(f"{system_start + 3}. 🎯 Rider Influence")
        
        print("0. 🚪 Exit (ModLog + Git Push)")
        print()
        
        # Build valid choices list including pagination
        valid_choices = ["0"]
        if total_pages > 1:
            if self.current_page > 1:
                valid_choices.append("P")
            if self.current_page < total_pages:
                valid_choices.append("N")
        
        # Add module choices and system choices
        valid_choices.extend([str(i) for i in range(1, system_start + 3)])
        
        choice = self._get_user_choice("Select an option", valid_choices)
        
        # Handle pagination
        if choice == "P" and self.current_page > 1:
            self.current_page -= 1
            return self.display_main_menu()
        elif choice == "N" and self.current_page < total_pages:
            self.current_page += 1
            return self.display_main_menu()
        
        return choice
        
    def display_module_menu(self, module_name: str) -> str:
        """Display module-specific menu."""
        self._display_header()
        
        print(f"📦 {module_name} Module Development")
        print("=" * 60)
        print()
        print("1. 🚀 Start WSP_30 Agentic Build")
        print("2. 📋 View Module Status")
        print("3. 🔧 Manual Development Mode")
        print("4. 📊 View Module Roadmap")
        print("5. 🧪 Run Module Tests")
        print("6. 📝 Update Documentation")
        print("7. 🔍 Analyze Dependencies")
        print("8. ⬅️ Back to Main Menu")
        print()
        
        return self._get_user_choice("Select an option", ["1", "2", "3", "4", "5", "6", "7", "8"])
        
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
            
        input("\nPress Enter to continue...")
        
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
        
        input("Press Enter to continue...")
        
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
        """Prompt user for yes/no confirmation."""
        while True:
            response = input(f"{question} (y/n): ").lower().strip()
            if response in ['y', 'yes', 'true', '1']:
                return True
            elif response in ['n', 'no', 'false', '0']:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")
                
    def prompt_for_input(self, prompt: str, validator: Optional[Callable[[str], bool]] = None) -> str:
        """Prompt user for text input with optional validation."""
        while True:
            response = input(f"{prompt}: ").strip()
            
            if validator and not validator(response):
                print("Invalid input. Please try again.")
                continue
                
            return response
            
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
        """Get user choice with validation."""
        while True:
            choice = input(f"{prompt} ({'/'.join(valid_choices)}): ").strip()
            
            if choice in valid_choices:
                return choice
            else:
                print(f"Invalid choice. Please select from: {', '.join(valid_choices)}")
                
    def _prompt_for_module_name(self) -> str:
        """Prompt for new module name."""
        print("\n🔤 Module Name Entry")
        print("-" * 30)
        
        while True:
            name = input("Enter module name (lowercase, underscores allowed): ").strip().lower()
            
            if self._validate_module_name(name):
                return name
            else:
                print("Invalid module name. Use lowercase letters, numbers, and underscores only.")
                
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
            return input("Enter module name manually: ").strip()
        
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
        return domain_icons.get(domain, "��")
        
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
        
        return friendly_names.get(module_name, f"📦 {module_name.replace('_', ' ').title()} Module")
        
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
        print("9. ⬅️ Back to Main Menu")
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
        print("4. 🎼 Orchestrate Module Enhancement")
        print("5. 📊 Perform Priority Assessment")
        print("6. 🌍 Perform Ecosystem Analysis")
        print("7. ⬅️ Back to Main Menu")
        print()
        
    def display_module_development_menu(self):
        """Display module development menu."""
        self._display_header()
        
        print("🏗️ Module Development")
        print("=" * 60)
        print()
        print("1. 📊 Display Module Status")
        print("2. 🧪 Run Module Tests")
        print("3. 🔧 Enter Manual Mode")
        print("4. 🗺️ Generate Intelligent Roadmap")
        print("5. ⬅️ Back to Main Menu")
        print()
        
    def get_user_input(self, prompt: str) -> str:
        """Get user input with a prompt."""
        return input(f"{prompt}: ").strip()
        
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
            print("📭 No roadmap data available.")
            
        input("Press Enter to continue...")
        
    def display_session_status(self, status: Dict[str, Any]):
        """Display session status information."""
        self._display_header()
        
        print("📊 Session Status")
        print("=" * 60)
        print()
        
        if isinstance(status, dict):
            for key, value in status.items():
                print(f"  {key}: {value}")
        else:
            print("📭 No session status available.")
            
        input("Press Enter to continue...")
        
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