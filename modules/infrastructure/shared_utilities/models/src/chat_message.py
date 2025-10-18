# -*- coding: utf-8 -*-
import sys
import io


from dataclasses import dataclass
from typing import Optional

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

@dataclass
class Author:
    """Represents the author of a chat message."""
    id: str
    displayName: str
    isChatOwner: Optional[bool] = None
    isChatModerator: Optional[bool] = None
    isChatSponsor: Optional[bool] = None
    profileImageUrl: Optional[str] = None

@dataclass
class ChatMessage:
    """Represents a single chat message."""
    id: str
    author: Author
    messageText: str
    publishedAt: str # ISO 8601 format
    type: str = "textMessageEvent" # e.g., textMessageEvent, superChatEvent 