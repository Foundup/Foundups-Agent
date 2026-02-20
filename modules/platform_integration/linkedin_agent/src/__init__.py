"""
LinkedIn Agent Source Module

This package intentionally uses lazy exports so importing
`modules.platform_integration.linkedin_agent.src.git_linkedin_bridge`
does not trigger the full LinkedIn agent import side effects.
"""

from importlib import import_module
from typing import Any

__version__ = "1.0.0"
__all__ = [
    "LinkedInAgent",
    "LinkedInPost",
    "LinkedInProfile",
    "EngagementAction",
    "EngagementType",
    "PostType",
    "create_linkedin_agent",
]


def __getattr__(name: str) -> Any:
    """Lazily expose LinkedIn agent symbols on first access."""
    if name in __all__:
        module = import_module(".linkedin_agent", __name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
