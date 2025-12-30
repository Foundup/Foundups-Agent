"""
Human Interaction Module - Anti-Detection Platform Interactions
==============================================================

One module. All platforms. Maximum sophistication.

Public API:
    from modules.infrastructure.human_interaction import get_interaction_controller

    interaction = get_interaction_controller(driver, platform="youtube_chat")
    await interaction.click_action("reaction_celebrate")
    await interaction.spam_action("reaction_heart", count=30)

WSP Compliance: WSP 49 (Platform Integration Safety), WSP 3 (Module Organization)
"""

from .interaction_controller import InteractionController, get_interaction_controller
from .platform_profiles import PlatformProfile, load_platform_profile
from .sophistication_engine import SophisticationEngine

__all__ = [
    "InteractionController",
    "get_interaction_controller",
    "PlatformProfile",
    "load_platform_profile",
    "SophisticationEngine",
]

__version__ = "0.1.0"
