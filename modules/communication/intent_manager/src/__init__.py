"""
Intent Manager Module - Meeting Intent Capture and Management

Part of the Autonomous Meeting Orchestrator (AMO) ecosystem.
Captures meeting intents, 3-question context, and stores in persistence layer.
"""

from .intent_manager import IntentManager, MeetingIntent, IntentStatus, ContextQuestion

__version__ = "0.0.1"
__all__ = ["IntentManager", "MeetingIntent", "IntentStatus", "ContextQuestion"] 