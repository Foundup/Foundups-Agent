"""
WRE Logging Framework

Core logging utilities for the Windsurf Recursive Engine (WRE), providing
structured logging, session management, and console output sanitization.

Author: FoundUps Agent Utilities Team
Version: 1.0.0
Date: 2025-01-29
WSP Compliance: WSP 46 (WRE Protocol), WSP 22 (Traceable Narrative)

Dependencies:
- None (uses only standard library)

Usage:
    from tools.wre.tools.logging_utils import wre_log, sanitize_for_console
    wre_log("Message", level="INFO", data={"key": "value"})
    
Features:
- Structured JSONL logging to session chronicles
- Session ID management and persistence
- Console output sanitization for ASCII compatibility
- Centralized logging for WRE operations
"""

import json
from pathlib import Path
from datetime import datetime
import os
import uuid

LOGS_DIR = Path(__file__).parent.parent.parent / "logs"
SESSION_ID_FILE = LOGS_DIR / ".session_id"

def get_session_id():
    """
    Retrieves the current session ID, creating one if it doesn't exist.
    The session ID is stored in a file to persist across different script runs
    within the same "session".
    """
    if SESSION_ID_FILE.exists():
        return SESSION_ID_FILE.read_text().strip()
    else:
        # Format: YYYYMMDD_HHMMSS_short_uuid
        session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        SESSION_ID_FILE.write_text(session_id)
        return session_id

# Initialize session ID at module load time
SESSION_ID = get_session_id()
CHRONICLE_FILE = LOGS_DIR / f"session_{SESSION_ID}.chronicle.jsonl"

def sanitize_for_console(text):
    """
    Encodes a string to ASCII, replacing any non-compliant characters.
    This ensures compatibility with non-UTF-8 console environments.
    """
    return str(text).encode('ascii', 'replace').decode('ascii')

def wre_log(message: str, level: str = 'INFO', data: dict = None):
    """
    The central logging function for the WRE.
    It writes a structured log to the session's chronicle file and
    prints a human-readable message to the console.

    Args:
        message: The core message to log.
        level: The log level (e.g., INFO, WARNING, ERROR, DEBUG).
        data: An optional dictionary for additional structured data.
    """
    # 1. Record to Chronicle
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level.upper(),
        "message": message,
        "data": data or {}
    }
    try:
        with open(CHRONICLE_FILE, "a", encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        # Fallback to simple print if logging fails
        print(f"!!! CHRONICLE LOGGING FAILED: {e} !!!")

    # 2. Print to Console
    console_message = f"[{level.upper()}] {message}"
    print(sanitize_for_console(console_message))

def reset_session():
    """
    Deletes the session ID file, forcing a new session on next run.
    Useful for manually starting a new session log.
    """
    if SESSION_ID_FILE.exists():
        SESSION_ID_FILE.unlink()
        print(sanitize_for_console(f"Session reset. New session will be created on next run."))

if __name__ == '__main__':
    # Example usage and testing of the logger
    print(f"Logging to session: {SESSION_ID}")
    wre_log("This is a standard informational message.")
    wre_log("This is a warning.", level="WARNING")
    wre_log("An error occurred!", level="ERROR", data={"error_code": 500, "module": "test"})
    print(f"\nLog file created at: {CHRONICLE_FILE}") 