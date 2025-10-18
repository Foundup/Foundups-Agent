# -*- coding: utf-8 -*-
import sys
import io


"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

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