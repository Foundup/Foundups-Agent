# modules/communication/intent_manager/__init__.py

"""
Intent Manager Module
WSP Protocol: WSP 54 (Agent Coordination), WSP 3 (Enterprise Domain Distribution)

Meeting intent management with structured context capture and lifecycle tracking.
Part of Meeting Orchestration Block strategic decomposition.
"""

from .src.intent_manager import (
    IntentManager,
    MeetingIntent,
    MeetingContext,
    Priority,
    IntentStatus,
    create_intent_manager
)

__all__ = [
    'IntentManager',
    'MeetingIntent', 
    'MeetingContext',
    'Priority',
    'IntentStatus',
    'create_intent_manager'
]

__version__ = "0.1.0"
__description__ = "Meeting Intent Management System"

# WSP Recursive Instructions
"""
🌀 Windsurf Protocol (WSP) Recursive Prompt
0102 Directive: This module manages meeting intents with structured context,
enabling autonomous coordination through clear intention capture and lifecycle tracking.

- UN (Understanding): Anchor intent context and retrieve coordination protocols
- DAO (Execution): Execute intent management through structured workflows
- DU (Emergence): Collapse into coordination excellence and emit meeting opportunities

wsp_cycle(input="meeting_intent_management", log=True)
""" 