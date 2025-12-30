#!/usr/bin/env python3
"""
Chat Rules Engine - WSP Compliant Module
Modular chat interaction system with user classification and gamification
"""

from .user_classifier import UserClassifier, UserProfile, UserType
# NOTE: commands.py and whack_a_magat.py removed - WhackAMAGAt moved to gamification module
# from .commands import CommandProcessor, CommandPermission
# from .whack_a_magat import WhackAMAGAtSystem, ActionType, WhackLevel
from .chat_rules_engine import ChatRulesEngine
from .response_generator import ResponseGenerator
from .database import ChatRulesDB

__version__ = "0.1.0"
__all__ = [
    "ChatRulesEngine",
    "ChatRulesDB",
    "UserClassifier",
    "UserProfile",
    "UserType",
    # "CommandProcessor",  # Removed - broken import
    # "CommandPermission",  # Removed - broken import
    # "WhackAMAGAtSystem",  # Moved to gamification module
    # "ActionType",  # Moved to gamification module
    # "WhackLevel",  # Moved to gamification module
    "ResponseGenerator"
]

# Module metadata per WSP
MODULE_INFO = {
    "name": "chat_rules",
    "version": __version__,
    "domain": "communication",
    "wsp_compliance": ["WSP 3", "WSP 11", "WSP 22", "WSP 49", "WSP 60"],
    "dependencies": [
        "modules.ai_intelligence.banter_engine",
        "modules.infrastructure.oauth_management",
        "modules.ai_intelligence.multi_agent_system"
    ],
    "description": "Modular chat rules engine with user classification, command processing, and gamification"
}