"""
Unified Metadata Updater Skillz

Agent chooses best method to update YouTube metadata:
- API (fastest for LIVE)
- DOM Live Dashboard (fallback for LIVE)
- DOM Manage Page (any broadcast)

CLI Usage:
    python executor.py auto --title "..."      # Auto-select method
    python executor.py clickbait               # Clickbait + M2M
    python executor.py major-event             # Title only (major event)
    python executor.py seo-refresh             # Description only (SEO)
"""

from .executor import (
    check_stream_live,
    update_via_api,
    update_via_dom_live,
    update_via_dom_manage,
    auto_update,
    apply_clickbait,
    major_event_update,
    seo_refresh,
)

__all__ = [
    "check_stream_live",
    "update_via_api",
    "update_via_dom_live",
    "update_via_dom_manage",
    "auto_update",
    "apply_clickbait",
    "major_event_update",
    "seo_refresh",
]
