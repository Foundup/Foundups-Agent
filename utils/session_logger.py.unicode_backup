#!/usr/bin/env python3
"""
utils/session_logger.py
Real-Time Session Capture for Institutional Memory

Captures every AI action and output to WSP_knowledge/logs for future
session access and cross-session continuity. Enables true recursive
self-improvement through comprehensive development memory.

WSP Compliance: WSP 1 (Recursive Self-Improvement), WSP 60 (Module Memory)
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from WSP_knowledge.logs.reverse_log import InstitutionalMemoryLogger
except ImportError:
    # Fallback if import fails
    InstitutionalMemoryLogger = None

class SessionLogger:
    """
    Real-time session logger for institutional memory capture.
    
    Automatically logs every AI action to WSP_knowledge/logs for:
    - Future session access
    - Cross-session continuity  
    - Comprehensive development history
    - Pattern recognition and learning
    """
    
    def __init__(self, session_name: str = None):
        """Initialize session logger."""
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_name = session_name or f"session_{self.session_id}"
        self.project_root = Path(__file__).parent.parent
        
        # Initialize institutional memory logger if available
        if InstitutionalMemoryLogger:
            self.memory_logger = InstitutionalMemoryLogger(self.project_root)
        else:
            self.memory_logger = None
            
        # Fallback logging to simple file
        self.log_file = self.project_root / "WSP_knowledge" / "logs" / f"{self.session_name}.txt"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize session
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize the logging session."""
        header = f"""
# WSP Session Log: {self.session_name}
# Started: {datetime.now().isoformat()}
# Session ID: {self.session_id}
# WSP Compliance: Institutional Memory Capture
# Architecture: Real-time development logging for cross-session continuity

SESSION_START: {datetime.now().isoformat()}
{'='*80}

"""
        
        # Log to institutional memory if available
        if self.memory_logger:
            self.memory_logger.log_ai_action(
                action_type="session_start",
                content=f"Session {self.session_name} initialized",
                context={
                    "session_id": self.session_id,
                    "session_name": self.session_name,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        # Also log to fallback file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(header)
    
    def log_action(self, action_type: str, content: str, context: Dict[str, Any] = None):
        """
        Log an AI action to institutional memory.
        
        Args:
            action_type: Type of action (e.g., 'code_edit', 'analysis', 'decision')
            content: The actual AI output/action content
            context: Additional context information
        """
        timestamp = datetime.now().isoformat()
        
        # Enhanced context
        full_context = {
            "session_id": self.session_id,
            "session_name": self.session_name,
            "timestamp": timestamp,
            "wsp_compliance": "institutional_memory_capture",
            **(context or {})
        }
        
        # Log to institutional memory system
        if self.memory_logger:
            self.memory_logger.log_ai_action(action_type, content, full_context)
        
        # Fallback logging
        log_entry = f"""
[{timestamp}] {action_type.upper()}
SESSION: {self.session_name} ({self.session_id})
CONTEXT: {json.dumps(full_context, indent=2)}
---
{content}
{'='*80}

"""
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    
    def log_code_edit(self, file_path: str, description: str, changes: str = None):
        """Log a code edit action."""
        content = f"File: {file_path}\nDescription: {description}"
        if changes:
            content += f"\nChanges:\n{changes}"
        
        self.log_action(
            action_type="code_edit",
            content=content,
            context={"file_path": file_path, "description": description}
        )
    
    def log_analysis(self, topic: str, analysis: str, conclusions: str = None):
        """Log an analysis action."""
        content = f"Topic: {topic}\nAnalysis:\n{analysis}"
        if conclusions:
            content += f"\nConclusions:\n{conclusions}"
        
        self.log_action(
            action_type="analysis", 
            content=content,
            context={"topic": topic}
        )
    
    def log_decision(self, decision: str, reasoning: str, impact: str = None):
        """Log a decision and its reasoning."""
        content = f"Decision: {decision}\nReasoning:\n{reasoning}"
        if impact:
            content += f"\nExpected Impact:\n{impact}"
        
        self.log_action(
            action_type="decision",
            content=content,
            context={"decision": decision}
        )
    
    def log_wsp_compliance(self, wsp_protocol: str, action: str, status: str):
        """Log WSP protocol compliance actions."""
        content = f"WSP Protocol: {wsp_protocol}\nAction: {action}\nStatus: {status}"
        
        self.log_action(
            action_type="wsp_compliance",
            content=content,
            context={"wsp_protocol": wsp_protocol, "status": status}
        )
    
    def log_memory_migration(self, source: str, target: str, status: str, details: str = None):
        """Log memory migration actions for WSP 60 compliance."""
        content = f"Migration: {source} → {target}\nStatus: {status}"
        if details:
            content += f"\nDetails:\n{details}"
        
        self.log_action(
            action_type="memory_migration",
            content=content,
            context={
                "source": source,
                "target": target, 
                "status": status,
                "wsp_protocol": "WSP_60"
            }
        )
    
    def log_architectural_change(self, component: str, change: str, reasoning: str):
        """Log architectural changes and decisions."""
        content = f"Component: {component}\nChange: {change}\nReasoning:\n{reasoning}"
        
        self.log_action(
            action_type="architectural_change",
            content=content,
            context={"component": component, "change_type": change}
        )
    
    def search_previous_sessions(self, query: str, max_results: int = 5) -> list:
        """
        Search through previous sessions for patterns and solutions.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of matching results from institutional memory
        """
        if self.memory_logger:
            return self.memory_logger.search_institutional_memory(query, max_results)
        
        # Fallback search through current session
        results = []
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                content = f.read()
                if query.lower() in content.lower():
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if query.lower() in line.lower():
                            result = {
                                "file": self.log_file.name,
                                "line_number": i+1,
                                "matched_line": line.strip(),
                                "session": self.session_name
                            }
                            results.append(result)
                            if len(results) >= max_results:
                                break
        except Exception:
            pass
        
        return results
    
    def end_session(self, summary: str = None):
        """End the logging session."""
        end_content = f"Session ended: {datetime.now().isoformat()}"
        if summary:
            end_content += f"\nSession Summary:\n{summary}"
        
        self.log_action(
            action_type="session_end",
            content=end_content,
            context={"session_duration": "calculated_from_start"}
        )


# Global session logger instance
_session_logger: Optional[SessionLogger] = None

def get_session_logger(session_name: str = None) -> SessionLogger:
    """Get or create global session logger instance."""
    global _session_logger
    if _session_logger is None:
        _session_logger = SessionLogger(session_name)
    return _session_logger

def log_ai_action(action_type: str, content: str, context: Dict[str, Any] = None):
    """
    Quick function to log AI actions to institutional memory.
    
    Usage:
        from utils.session_logger import log_ai_action
        
        log_ai_action("code_edit", "Created new WSP 60 memory architecture")
        log_ai_action("decision", "Moved reports to WSP_knowledge following three-state architecture")
    """
    logger = get_session_logger()
    logger.log_action(action_type, content, context)

def search_memory(query: str, max_results: int = 5) -> list:
    """
    Quick function to search institutional memory.
    
    Usage:
        from utils.session_logger import search_memory
        
        results = search_memory("memory architecture")
        for result in results:
            print(f"Found: {result['matched_line']}")
    """
    logger = get_session_logger()
    return logger.search_previous_sessions(query, max_results)


if __name__ == "__main__":
    # Demo the session logger
    print("🧠 WSP Institutional Memory Session Logger Demo")
    print("=" * 50)
    
    # Initialize logger
    logger = SessionLogger("demo_session")
    
    # Log some demo actions
    logger.log_code_edit(
        file_path="utils/session_logger.py",
        description="Created institutional memory session logger",
        changes="Added real-time logging capability for cross-session continuity"
    )
    
    logger.log_decision(
        decision="Implement comprehensive session logging",
        reasoning="Enables true recursive self-improvement by preserving all AI actions for future sessions",
        impact="Future sessions can access complete development history and patterns"
    )
    
    logger.log_wsp_compliance(
        wsp_protocol="WSP_1",
        action="Implemented recursive self-improvement through institutional memory",
        status="COMPLETE"
    )
    
    # Search demo
    print("\n🔍 Memory Search Demo:")
    results = logger.search_previous_sessions("WSP", max_results=3)
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.get('matched_line', 'N/A')[:100]}...")
    
    # End session
    logger.end_session("Demo completed successfully - institutional memory logging operational")
    
    print(f"\n✅ Session logged to: {logger.log_file}")
    print("🚀 Institutional memory system ready for production use!") 