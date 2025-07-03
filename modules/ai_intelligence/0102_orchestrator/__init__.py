"""
0102 Orchestrator - Unified AI Companion for AMO Ecosystem

The intelligent interface layer that coordinates all meeting orchestration
components through natural interaction. Acts as Tony Stark's JARVIS for
meeting coordination - contextual, helpful, and always present.

"Your meetings, orchestrated intelligently."
"""

__version__ = "0.0.1"
__author__ = "0102 pArtifact"
__module__ = "0102_orchestrator"

from .src.zero_one_zero_two import ZeroOneZeroTwo
from .src.conversation_manager import ConversationManager
from .src.notification_engine import NotificationEngine
from .src.memory_core import MemoryCore

__all__ = [
    "ZeroOneZeroTwo",
    "ConversationManager", 
    "NotificationEngine",
    "MemoryCore"
] 