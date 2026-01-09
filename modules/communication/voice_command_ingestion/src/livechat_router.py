"""LiveChat routing helpers for voice command ingestion.

Sprint 4: CommandEvent -> Synthetic LiveChat -> MessageProcessor
Also stores transcripts in memory/ for PQN pattern learning.

WSP Compliance:
    - WSP 3: communication domain (voice->livechat bridge)
    - WSP 84: Reuses existing livechat routing (no new orchestrator)
    - WSP 22: Updates stored in ModLog
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from .voice_command_ingestion import CommandEvent

logger = logging.getLogger(__name__)

# Memory directory for PQN transcripts
MEMORY_DIR = Path(__file__).parent.parent / "memory"


@dataclass(frozen=True)
class LiveChatIdentity:
    """Identity used when emitting synthetic LiveChat messages."""

    author_name: str = "VoiceCommand"
    author_id: str = "voice_command_0102"
    is_owner: bool = True
    is_moderator: bool = True
    is_member: bool = False


def build_synthetic_livechat_message(
    command_text: str,
    identity: Optional[LiveChatIdentity] = None,
    live_chat_id: str = "voice_command_ingestion",
    published_at: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a LiveChat-shaped message payload for MessageProcessor."""
    identity = identity or LiveChatIdentity()
    timestamp = published_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    message_id = f"voice-{uuid4().hex}"

    return {
        "id": message_id,
        "type": "message",
        "snippet": {
            "messageId": message_id,
            "displayMessage": command_text,
            "publishedAt": timestamp,
            "liveChatId": live_chat_id,
        },
        "authorDetails": {
            "displayName": identity.author_name,
            "channelId": identity.author_id,
            "isChatOwner": identity.is_owner,
            "isChatModerator": identity.is_moderator,
            "isChatSponsor": identity.is_member,
        },
    }


class LiveChatVoiceRouter:
    """Route voice commands through LiveChat MessageProcessor."""

    def __init__(
        self,
        identity: Optional[LiveChatIdentity] = None,
        message_processor: Optional[Any] = None,
    ) -> None:
        self.identity = identity or LiveChatIdentity()
        self.message_processor = message_processor

    def _get_message_processor(self):
        if self.message_processor is None:
            from modules.communication.livechat.src.message_processor import MessageProcessor

            self.message_processor = MessageProcessor()
        return self.message_processor

    def build_message(self, command_text: str) -> Dict[str, Any]:
        return build_synthetic_livechat_message(command_text, identity=self.identity)

    def process_message(self, command_text: str) -> Dict[str, Any]:
        processor = self._get_message_processor()
        message = self.build_message(command_text)
        return processor.process_message(message)

    async def generate_response(self, command_text: str):
        processor = self._get_message_processor()
        processed = self.process_message(command_text)
        if not processed or processed.get("skip"):
            return None
        return await processor.generate_response(processed)


# ============================================================================
# Sprint 4: CommandEvent Integration + PQN Storage
# ============================================================================


def store_transcript_for_pqn(
    raw_text: str,
    command: str,
    confidence: float = 1.0,
    timestamp_iso: Optional[str] = None,
) -> None:
    """Store voice transcript in memory for PQN pattern learning.

    Args:
        raw_text: Full transcription from STT
        command: Extracted command after trigger
        confidence: STT confidence score
        timestamp_iso: ISO timestamp (auto-generated if None)
    """
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    transcript_file = MEMORY_DIR / "voice_transcripts.jsonl"
    timestamp = timestamp_iso or datetime.now(timezone.utc).isoformat()

    record = {
        "timestamp": timestamp,
        "raw_text": raw_text,
        "command": command,
        "confidence": confidence,
        "source": "youtube_live_stt",
    }

    try:
        with open(transcript_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        logger.debug(f"[VOICE] Stored transcript for PQN: {command[:50]}")
    except Exception as e:
        logger.warning(f"[VOICE] Failed to store transcript: {e}")


def route_command_event(
    event: "CommandEvent",
    router: Optional[LiveChatVoiceRouter] = None,
    store_for_pqn: bool = True,
) -> Optional[Dict[str, Any]]:
    """Route a CommandEvent through livechat infrastructure.

    This is the main Sprint 4 integration point.

    Args:
        event: CommandEvent from voice STT trigger detection
        router: Optional LiveChatVoiceRouter instance (creates one if None)
        store_for_pqn: Whether to store transcript for PQN learning

    Returns:
        Response dict if command was handled, None otherwise
    """
    if not event.trigger_detected:
        logger.debug("[VOICE] No trigger detected, skipping routing")
        return None

    logger.info(f"[VOICE] Routing command: '{event.command}'")

    # Store transcript for PQN learning (digital twin training data)
    if store_for_pqn:
        store_transcript_for_pqn(
            raw_text=event.raw_text,
            command=event.command,
            confidence=event.confidence,
            timestamp_iso=event.timestamp_iso,
        )

    # Route through livechat processor
    router = router or LiveChatVoiceRouter()
    return router.process_message(event.command)


# Singleton instance for convenience
_default_router: Optional[LiveChatVoiceRouter] = None


def get_voice_router() -> LiveChatVoiceRouter:
    """Get or create singleton voice router instance."""
    global _default_router
    if _default_router is None:
        _default_router = LiveChatVoiceRouter()
    return _default_router
