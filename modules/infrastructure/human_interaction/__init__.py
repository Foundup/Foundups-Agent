"""
Human Interaction Module
========================

Unified anti-detection interface for human-like platform interactions.

See src/ for implementation.
"""

from .src import (
    InteractionController,
    get_interaction_controller,
    PlatformProfile,
    load_platform_profile,
    SophisticationEngine,
)

__all__ = [
    "InteractionController",
    "get_interaction_controller",
    "PlatformProfile",
    "load_platform_profile",
    "SophisticationEngine",
]
