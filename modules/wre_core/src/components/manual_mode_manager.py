"""
Manual Mode Manager Component

Handles manual development mode workflows and interactive development.
Extracted from module_development_handler.py per WSP 62 refactoring requirements.

WSP Compliance:
- WSP 62: Large File and Refactoring Enforcement Protocol (refactoring)
- WSP 1: Single responsibility principle (manual mode only)
- WSP 54: WRE agent duties specification (manual mode support)
"""

from pathlib import Path
from modules.wre_core.src.utils.logging_utils import wre_log


class ManualModeManager:
    """
    Manual Mode Manager - Handles manual development mode workflows
    
    Responsibilities:
    - Manual development mode entry and exit
    - Interactive development session management
    - Manual workflow guidance
    - Development mode session tracking
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.manual_mode_active = False
        
    def enter_manual_mode(self, module_name: str, engine, session_manager):
        """Enter manual development mode for a module."""
        wre_log(f"🔧 Entering manual mode for: {module_name}", "INFO")
        session_manager.log_operation("manual_mode", {"module": module_name, "action": "enter"})
        
        try:
            self.manual_mode_active = True
            
            # Display manual mode instructions
            self._display_manual_mode_instructions(module_name)
            
            # Enter interactive session
            self._run_manual_session(module_name, engine, session_manager)
            
        except Exception as e:
            wre_log(f"❌ Manual mode failed: {e}", "ERROR")
            session_manager.log_operation("manual_mode", {"error": str(e)})
        finally:
            self.manual_mode_active = False
            wre_log(f"🔧 Exiting manual mode for: {module_name}", "INFO")
            session_manager.log_operation("manual_mode", {"module": module_name, "action": "exit"})
            
    def _display_manual_mode_instructions(self, module_name: str):
        """Display instructions for manual development mode."""
        wre_log("🔧 Manual Development Mode", "INFO")
        wre_log("=" * 50, "INFO")
        wre_log(f"Module: {module_name}", "INFO")
        wre_log("", "INFO")
        wre_log("Available Commands:", "INFO")
        wre_log("  status   - Display module status", "INFO")
        wre_log("  test     - Run module tests", "INFO")
        wre_log("  roadmap  - View/generate roadmap", "INFO")
        wre_log("  create   - Create new files", "INFO")
        wre_log("  help     - Show this help", "INFO")
        wre_log("  exit     - Exit manual mode", "INFO")
        wre_log("", "INFO")
        wre_log("Enter commands to interact with the module.", "INFO")
        wre_log("=" * 50, "INFO")
        
    def _run_manual_session(self, module_name: str, engine, session_manager):
        """Run the interactive manual development session."""
        while self.manual_mode_active:
            try:
                # Get user command
                command = engine.ui_interface.get_user_input(f"[{module_name}] manual> ")
                
                if not command:
                    continue
                    
                command = command.strip().lower()
                
                # Process command
                if command == "exit":
                    break
                elif command == "help":
                    self._display_manual_mode_instructions(module_name)
                elif command == "status":
                    self._handle_status_command(module_name, engine, session_manager)
                elif command == "test":
                    self._handle_test_command(module_name, engine, session_manager)
                elif command == "roadmap":
                    self._handle_roadmap_command(module_name, engine, session_manager)
                elif command == "create":
                    self._handle_create_command(module_name, engine, session_manager)
                else:
                    wre_log(f"❌ Unknown command: {command}", "ERROR")
                    wre_log("Type 'help' for available commands", "INFO")
                    
            except KeyboardInterrupt:
                wre_log("\n🔧 Manual mode interrupted", "INFO")
                break
            except Exception as e:
                wre_log(f"❌ Command error: {e}", "ERROR")
                
    def _handle_status_command(self, module_name: str, engine, session_manager):
        """Handle status command in manual mode."""
        try:
            # Delegate to module status manager
            if hasattr(engine, 'module_status_manager'):
                engine.module_status_manager.display_module_status(module_name, session_manager)
            else:
                wre_log("❌ Module status manager not available", "ERROR")
        except Exception as e:
            wre_log(f"❌ Status command failed: {e}", "ERROR")
            
    def _handle_test_command(self, module_name: str, engine, session_manager):
        """Handle test command in manual mode."""
        try:
            # Find module path
            modules_dir = self.project_root / "modules"
            module_path = None
            
            for path in modules_dir.rglob("*"):
                if path.is_dir() and path.name == module_name:
                    module_path = path
                    break
                    
            if not module_path:
                wre_log(f"❌ Module not found: {module_name}", "ERROR")
                return
                
            # Delegate to module test runner
            if hasattr(engine, 'module_test_runner'):
                engine.module_test_runner.run_module_tests(module_name, module_path, session_manager)
            else:
                wre_log("❌ Module test runner not available", "ERROR")
        except Exception as e:
            wre_log(f"❌ Test command failed: {e}", "ERROR")
            
    def _handle_roadmap_command(self, module_name: str, engine, session_manager):
        """Handle roadmap command in manual mode."""
        try:
            # Delegate to roadmap manager
            if hasattr(engine, 'module_roadmap_manager'):
                engine.module_roadmap_manager.view_roadmap(module_name, engine, session_manager)
            else:
                wre_log("❌ Module roadmap manager not available", "ERROR")
        except Exception as e:
            wre_log(f"❌ Roadmap command failed: {e}", "ERROR")
            
    def _handle_create_command(self, module_name: str, engine, session_manager):
        """Handle create command in manual mode."""
        try:
            wre_log("🔧 Create File Options:", "INFO")
            wre_log("  1. Python source file", "INFO")
            wre_log("  2. Test file", "INFO")
            wre_log("  3. Documentation file", "INFO")
            wre_log("  4. Configuration file", "INFO")
            
            choice = engine.ui_interface.get_user_input("Select file type (1-4): ")
            
            if choice == "1":
                self._create_source_file(module_name, engine, session_manager)
            elif choice == "2":
                self._create_test_file(module_name, engine, session_manager)
            elif choice == "3":
                self._create_doc_file(module_name, engine, session_manager)
            elif choice == "4":
                self._create_config_file(module_name, engine, session_manager)
            else:
                wre_log("❌ Invalid choice", "ERROR")
                
        except Exception as e:
            wre_log(f"❌ Create command failed: {e}", "ERROR")
            
    def _create_source_file(self, module_name: str, engine, session_manager):
        """Create a new source file."""
        filename = engine.ui_interface.get_user_input("Enter source filename (without .py): ")
        if filename:
            wre_log(f"📝 Creating source file: {filename}.py", "INFO")
            # Implementation would create the file with template
            session_manager.log_operation("manual_create", {"type": "source", "file": f"{filename}.py"})
            
    def _create_test_file(self, module_name: str, engine, session_manager):
        """Create a new test file."""
        filename = engine.ui_interface.get_user_input("Enter test filename (without test_ prefix): ")
        if filename:
            wre_log(f"🧪 Creating test file: test_{filename}.py", "INFO")
            # Implementation would create the file with template
            session_manager.log_operation("manual_create", {"type": "test", "file": f"test_{filename}.py"})
            
    def _create_doc_file(self, module_name: str, engine, session_manager):
        """Create a new documentation file."""
        filename = engine.ui_interface.get_user_input("Enter doc filename (without .md): ")
        if filename:
            wre_log(f"📖 Creating documentation file: {filename}.md", "INFO")
            # Implementation would create the file with template
            session_manager.log_operation("manual_create", {"type": "doc", "file": f"{filename}.md"})
            
    def _create_config_file(self, module_name: str, engine, session_manager):
        """Create a new configuration file."""
        filename = engine.ui_interface.get_user_input("Enter config filename: ")
        if filename:
            wre_log(f"⚙️ Creating config file: {filename}", "INFO")
            # Implementation would create the file with template
            session_manager.log_operation("manual_create", {"type": "config", "file": filename}) 