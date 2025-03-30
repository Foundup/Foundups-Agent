"""
AI Package for Windsurfer

Contains AI-related modules for prompt management, personality, and routing.
"""

from .prompt_engine import PromptEngine
from .personality_core import PersonalityCore
from .ai_router import AIRouter

__all__ = ['PromptEngine', 'PersonalityCore', 'AIRouter'] 