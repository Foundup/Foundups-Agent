from dataclasses import dataclass
from typing import Optional

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