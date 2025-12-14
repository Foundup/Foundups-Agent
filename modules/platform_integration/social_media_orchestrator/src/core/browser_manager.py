"""
Browser Manager - DEPRECATED LOCATION

⚠️ This module has been migrated to foundups_selenium (Sprint V4)

Please update your imports to:
    from modules.infrastructure.foundups_selenium.src.browser_manager import BrowserManager, get_browser_manager

This file remains for backwards compatibility only.

WSP References: WSP 3 (Architecture), WSP 72 (Module Independence)
Migration: Sprint V4 - Browser Manager Migration (foundups_vision roadmap)
"""

# Backwards-compatible shim: Import from new location
from modules.infrastructure.foundups_selenium.src.browser_manager import (
    BrowserManager,
    get_browser_manager,
)

__all__ = ["BrowserManager", "get_browser_manager"]
