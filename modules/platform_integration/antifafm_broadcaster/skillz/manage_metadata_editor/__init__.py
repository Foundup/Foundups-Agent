"""
Manage Metadata Editor Skillz

Edit past/scheduled broadcast metadata via YouTube Studio Manage page DOM automation.

CLI Usage:
    python executor.py list                           # List recent broadcasts
    python executor.py edit <index> --title "..."     # Edit specific broadcast
    python executor.py recent --title "..."           # Edit most recent
    python executor.py clickbait                      # Apply clickbait to most recent
"""

from .executor import (
    list_broadcasts,
    edit_broadcast_metadata,
    apply_clickbait_to_recent,
    get_shareable_link,
)

__all__ = [
    "list_broadcasts",
    "edit_broadcast_metadata",
    "apply_clickbait_to_recent",
    "get_shareable_link",
]
