"""
Manual Mode Manager

Handles manual development mode entry and interactive tools.
Extracted from module_development_handler.py following WSP principles.

WSP Compliance:
- Single responsibility: Manual mode management only
- Clean interfaces: Focused API for manual operations
- Modular cohesion: Self-contained manual mode logic
"""

from pathlib import Path

from modules.wre_core.src.utils.logging_utils import wre_log

class ManualModeManager:
    """
    Manual Mode Manager - WSP-compliant manual development handling
    
    Responsibilities:
    - Manual development mode entry
    - Interactive development tools
    - Manual workflow coordination
    """
    
    def __init__(self, project_root: Path, session_manager):
        self.project_root = project_root
        self.session_manager = session_manager
        
    def enter_manual_mode(self, module_name: str, engine):
        """Enter manual development mode for a module."""
        wre_log(f"🔧 Entering manual mode for: {module_name}", "INFO")
        self.session_manager.log_operation("manual_mode", {"module": module_name})
        
        try:
            # Find module path
            module_path = self._find_module_path(module_name)
            if not module_path:
                wre_log(f"❌ Module not found: {module_name}", "ERROR")
                return
                
            # Display manual mode options
            wre_log(f"🛠️ Manual Development Mode: {module_name}", "INFO")
            wre_log(f"  📁 Module Path: {module_path}", "INFO")
            wre_log(f"  🎯 This is where you would implement manual development tools", "INFO")
            wre_log(f"  🔧 Interactive development environment would be launched here", "INFO")
            
            # For now, just log that manual mode was entered
            self.session_manager.log_achievement("manual_mode", f"Entered manual mode for {module_name}")
            
        except Exception as e:
            wre_log(f"❌ Manual mode entry failed: {e}", "ERROR")
            self.session_manager.log_operation("manual_mode", {"error": str(e)})
            
    def _find_module_path(self, module_name: str) -> Path:
        """Find the path to a module by name."""
        modules_dir = self.project_root / "modules"
        
        for module_path in modules_dir.rglob("*"):
            if module_path.is_dir() and module_path.name == module_name:
                return module_path
                
        return None 