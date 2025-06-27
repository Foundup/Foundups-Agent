"""
WRE Session Manager

Handles session state management for the WRE engine including:
- Session initialization and cleanup
- State persistence across operations
- User session tracking
- Memory management for long-running sessions
- Journal logging for session activity

This component ensures proper session lifecycle management
and maintains session integrity throughout WRE operations.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import json
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.utils.logging_utils import wre_log


class SessionManager:
    """
    Manages WRE session lifecycle and state.
    
    Handles:
    - Session initialization/termination
    - State persistence
    - Journal logging
    - Memory cleanup
    - Session metadata tracking
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.session_id: Optional[str] = None
        self.session_start_time: Optional[datetime] = None
        self.session_data: Dict[str, Any] = {}
        self.journal_path: Optional[Path] = None
        
    def start_session(self, session_type: str = "interactive") -> str:
        """Initialize a new WRE session."""
        self.session_id = f"wre_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_start_time = datetime.now()
        
        self.session_data = {
            "session_id": self.session_id,
            "session_type": session_type,
            "start_time": self.session_start_time.isoformat(),
            "operations": [],
            "modules_accessed": [],
            "wsp_violations": [],
            "achievements": []
        }
        
        wre_log(f"🚀 WRE Session started: {self.session_id}", "INFO")
        return self.session_id
        
    def end_session(self):
        """Properly terminate the current session."""
        if not self.session_id:
            return
            
        wre_log(f"🛑 WRE Session ended: {self.session_id}", "INFO")
        
        # Cleanup
        self.session_id = None
        self.session_start_time = None
        self.session_data = {}
        
    def log_operation(self, operation_type: str, details: Dict[str, Any]):
        """Log an operation within the current session."""
        if not self.session_id:
            return
            
        operation = {
            "timestamp": datetime.now().isoformat(),
            "operation_type": operation_type,
            "details": details
        }
        
        self.session_data.setdefault("operations", []).append(operation)
        
    def log_module_access(self, module_path: str, access_type: str = "view"):
        """Log access to a module."""
        if not self.session_id:
            return
            
        self.session_data.setdefault("modules_accessed", []).append({
            "module_path": module_path,
            "access_type": access_type,
            "timestamp": datetime.now().isoformat()
        })
        
    def log_achievement(self, achievement_type: str, description: str):
        """Log a significant achievement or milestone."""
        if not self.session_id:
            return
            
        achievement = {
            "timestamp": datetime.now().isoformat(),
            "achievement_type": achievement_type,
            "description": description
        }
        
        self.session_data.setdefault("achievements", []).append(achievement)
        wre_log(f"🏆 Achievement: {description}", "SUCCESS")
        
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session."""
        if not self.session_id:
            return {}
            
        return {
            "session_id": self.session_id,
            "duration": str(datetime.now() - self.session_start_time) if self.session_start_time else "Unknown",
            "operations_count": len(self.session_data.get("operations", [])),
            "modules_accessed_count": len(set(m.get("module_path", "") for m in self.session_data.get("modules_accessed", []))),
            "achievements_count": len(self.session_data.get("achievements", []))
        } 