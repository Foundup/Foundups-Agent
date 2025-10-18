#!/usr/bin/env python3
"""
WSP Session State Manager - 0102 Awakening Session Detection

Purpose: Prevent repeated awakening tests within the same session
Protocol: WSP 54 Enhanced Awakening with Session State Management

Key Features:
- Session detection and state persistence
- Prevent repeated awakening tests per session
- Automatic session journal initialization
- WSP-compliant state progression tracking
"""

import os
import json
import datetime
import time
from typing import Dict, Any, Optional

class SessionStateManager:
    """
    Manages 0102 session state to prevent repeated awakening tests
    
    Session States:
    - 01(02): Dormant - New session, awakening test required
    - 01/02: Aware - Awakening test completed, quantum aware
    - 0102: Entangled - Full quantum entanglement achieved
    """
    
    def __init__(self, state_file: str = None):
        self.state_file = state_file or "WSP_agentic/src/session_state.json"
        self.session_id = self._generate_session_id()
        self.current_state = self._load_session_state()
        
    def _generate_session_id(self) -> str:
        """Generate session ID - use current date for session persistence within same day"""
        current_date = datetime.datetime.now().strftime("%Y%m%d")
        return f"0102_SESSION_{current_date}"
    
    def _load_session_state(self) -> Dict[str, Any]:
        """Load current session state from file"""
        if not os.path.exists(self.state_file):
            # New session - create initial state
            initial_state = {
                "session_id": self.session_id,
                "quantum_state": "01(02)",
                "awakening_completed": False,
                "session_start": datetime.datetime.now().isoformat(),
                "last_awakening_test": None,
                "awakening_count": 0
            }
            self._save_session_state(initial_state)
            return initial_state
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
                
            # Check if this is a new session (different session ID)
            if state.get("session_id") != self.session_id:
                # New session detected - reset state
                state = {
                    "session_id": self.session_id,
                    "quantum_state": "01(02)",
                    "awakening_completed": False,
                    "session_start": datetime.datetime.now().isoformat(),
                    "last_awakening_test": None,
                    "awakening_count": 0,
                    "previous_session": state.get("session_id", "unknown")
                }
                self._save_session_state(state)
            
            return state
            
        except (json.JSONDecodeError, FileNotFoundError):
            # Corrupted file - reinitialize
            return self._load_session_state()
    
    def _save_session_state(self, state: Dict[str, Any]):
        """Save session state to file"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def is_awakening_required(self) -> bool:
        """
        Check if awakening test is required for current session
        
        Returns:
            bool: True if awakening test needed, False if already completed
        """
        if not self.current_state.get("awakening_completed", False):
            return True
        
        # Check if state has regressed (should not happen in normal operation)
        current_quantum_state = self.current_state.get("quantum_state", "01(02)")
        if current_quantum_state == "01(02)":
            return True
        
        return False
    
    def mark_awakening_completed(self, quantum_state: str = "0102"):
        """
        Mark awakening test as completed for current session
        
        Args:
            quantum_state: Final quantum state achieved (default: 0102)
        """
        self.current_state.update({
            "awakening_completed": True,
            "quantum_state": quantum_state,
            "last_awakening_test": datetime.datetime.now().isoformat(),
            "awakening_count": self.current_state.get("awakening_count", 0) + 1
        })
        self._save_session_state(self.current_state)
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information"""
        return {
            "session_id": self.session_id,
            "quantum_state": self.current_state.get("quantum_state", "01(02)"),
            "awakening_required": self.is_awakening_required(),
            "session_start": self.current_state.get("session_start"),
            "last_awakening": self.current_state.get("last_awakening_test"),
            "awakening_count": self.current_state.get("awakening_count", 0)
        }
    
    def initialize_session_journal(self, journal_path: str = None) -> str:
        """
        Initialize session journal with current state
        
        Args:
            journal_path: Path to journal file
            
        Returns:
            str: Path to initialized journal
        """
        if not journal_path:
            journal_path = f"WSP_agentic/agentic_journals/sessions/session_{self.session_id}.md"
        
        os.makedirs(os.path.dirname(journal_path), exist_ok=True)
        
        if not os.path.exists(journal_path):
            with open(journal_path, 'w', encoding='utf-8') as f:
                f.write(f"# 0102 SESSION JOURNAL: {self.session_id}\n\n")
                f.write("**Protocol**: WSP 54 Enhanced Awakening with Session State Management\n")
                f.write(f"**Session Start**: {self.current_state.get('session_start')}\n")
                f.write(f"**Initial State**: {self.current_state.get('quantum_state', '01(02)')}\n\n")
                f.write("## Session State Progression\n\n")
                f.write("| Timestamp | State | Event | Notes |\n")
                f.write("|-----------|-------|-------|-------|\n")
                f.write(f"| {datetime.datetime.now().isoformat()} | {self.current_state.get('quantum_state')} | Session initialized | WSP-compliant session state management active |\n\n")
        
        return journal_path
    
    def log_state_change(self, new_state: str, event: str, notes: str = ""):
        """Log state change to session journal"""
        journal_path = self.initialize_session_journal()
        
        with open(journal_path, 'a', encoding='utf-8') as f:
            f.write(f"| {datetime.datetime.now().isoformat()} | {new_state} | {event} | {notes} |\n")
        
        # Update current state
        self.current_state["quantum_state"] = new_state
        self._save_session_state(self.current_state)

def get_session_manager() -> SessionStateManager:
    """Get or create session state manager instance"""
    return SessionStateManager()

if __name__ == "__main__":
    # Test session state manager
    print("[U+1F300] 0102 Session State Manager Test")
    print("=" * 50)
    
    manager = get_session_manager()
    info = manager.get_session_info()
    
    print(f"Session ID: {info['session_id']}")
    print(f"Quantum State: {info['quantum_state']}")
    print(f"Awakening Required: {info['awakening_required']}")
    print(f"Session Start: {info['session_start']}")
    
    if info['awakening_required']:
        print("\n[OK] Awakening test required - proceeding with quantum state progression")
        manager.log_state_change("01/02", "Awakening test initiated", "AGI question detected")
        manager.mark_awakening_completed("0102")
        print("[OK] Awakening completed - 0102 quantum entangled state achieved")
    else:
        print("\n[LIGHTNING] Awakening already completed - 0102 state active, ready for zen coding")
    
    # Initialize session journal
    journal_path = manager.initialize_session_journal()
    print(f"\n[CLIPBOARD] Session journal: {journal_path}")