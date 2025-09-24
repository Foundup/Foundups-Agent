"""
HoloIndex Command Handlers

Extracted from monolithic cli.py to follow WSP 87 size limits.
Each command handler is now a separate, focused module.
"""

from .search_cmd import handle_search_command
from .dae_init import handle_dae_initialization
from .doc_audit import handle_documentation_audit

__all__ = [
    'handle_search_command',
    'handle_dae_initialization',
    'handle_documentation_audit'
]