"""
Session Launcher Module - Meeting Session Coordination

Coordinates meeting session launch across platforms with participants.
"""

from .session_launcher import SessionLauncher, SessionStatus, LaunchRequest

__version__ = "0.0.1"
__all__ = ["SessionLauncher", "SessionStatus", "LaunchRequest"] 