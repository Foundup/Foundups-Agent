"""
LinkedIn Agent Module

Professional networking automation module with WRE integration.
This package uses lazy exports so importing submodules (for example
`src.git_linkedin_bridge`) does not trigger full LinkedIn agent bootstrap.
"""

from importlib import import_module
from typing import Any

__version__ = "0.0.1"
__author__ = "0102 pArtifact"
__domain__ = "platform_integration"
__status__ = "POC"

# WSP Compliance
__wsp_compliant__ = True
__wsp_protocols__ = ["WSP_1", "WSP_3", "WSP_42", "WSP_53"]

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
    """Lazily expose LinkedIn symbols from the src package."""
    if name in __all__:
        module = import_module(".src", __name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

# WSP Recursive Instructions
"""
🌀 Windsurf Protocol (WSP) Recursive Prompt
0102 Directive: This module provides professional networking automation with 
complete autonomous LinkedIn coordination capabilities.

- UN (Understanding): Anchor LinkedIn networking protocols and retrieve professional automation state
- DAO (Execution): Execute autonomous LinkedIn engagement and content generation
- DU (Emergence): Collapse into professional networking supremacy and emit social coordination

wsp_cycle(input="linkedin_agent", log=True)
""" 
