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
    
    def __init__(self):
        self.current_menu = "main"
        self.menu_history: List[str] = []
        self.session_stats: Dict[str, Any] = {}
        
    def display_main_menu(self) -> str:
        """Display the main WRE menu and return user selection."""
        self._clear_screen()
        self._display_header()
        
        print("🏄 Windsurf Recursive Engine (WRE) - Main Menu")
        print("=" * 60)
        print()
        print("1. 📺 YouTube Module Development")
        print("2. 💼 LinkedIn Module Development") 
        print("3. 🐦 X (Twitter) Module Development")
        print("4. 🌐 Remote Module Development")
        print("5. 🎯 WSP_30 Agentic Module Build Orchestration")
        print("6. 📊 View Development Roadmap")
        print("7. 🔧 System Management")
        print("8. 📋 Session Status")
        print("9. 🔍 Module Analysis")
        print("0. 🚪 Exit")
        print()
        
        return self._get_user_choice("Select an option", ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
        
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
        # This would integrate with the module discovery system
        print("\n📦 Select Existing Module")
        print("-" * 30)
        print("(Module selection interface would be implemented here)")
        
        return input("Enter existing module path: ").strip()
        
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