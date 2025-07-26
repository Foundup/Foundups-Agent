"""
Intent Manager Module - Meeting Intent Capture and Context Management

Public API for structured meeting intent lifecycle management.
Extracted from auto_meeting_orchestrator strategic decomposition.
"""

from .src.intent_manager import (
    IntentManager,
    MeetingIntent,
    MeetingContext,
    IntentStatus,
    Priority
)

__all__ = [
    'IntentManager',
    'MeetingIntent',
    'MeetingContext', 
    'IntentStatus',
    'Priority'
]

# Module metadata
__version__ = "0.1.0"
__domain__ = "communication"
__purpose__ = "Meeting intent capture, storage, and retrieval with structured context" 