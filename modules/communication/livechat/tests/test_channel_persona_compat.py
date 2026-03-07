import asyncio
from unittest.mock import AsyncMock, MagicMock

from modules.communication.livechat.src.core.orchestrator import LiveChatOrchestrator
from modules.communication.livechat.src.livechat_core import LiveChatCore
from modules.communication.livechat.src.persona_registry import resolve_persona_key


FOUNDUPS_ID = "UCSNTUXjAgpd4sgWYP0xoJgw"
MOVE2JAPAN_ID = "UC-LSSlOZwpGIRIYihaz8zCw"


def test_resolve_persona_key_keeps_channel_identity_by_default():
    assert resolve_persona_key(
        channel_name="FoundUps",
        channel_id=FOUNDUPS_ID,
        bot_channel_id=FOUNDUPS_ID,
    ) == "foundups"


def test_resolve_persona_key_allows_same_family_stream_brand_override():
    assert resolve_persona_key(
        channel_name="FoundUps",
        channel_id=FOUNDUPS_ID,
        bot_channel_id=FOUNDUPS_ID,
        stream_title="antifaFM Live Stream",
    ) == "antifafm"


def test_resolve_persona_key_blocks_cross_family_stream_brand_override():
    assert resolve_persona_key(
        channel_name="Move2Japan",
        channel_id=MOVE2JAPAN_ID,
        bot_channel_id=MOVE2JAPAN_ID,
        stream_title="FoundUps mention during relocation stream",
    ) == "move2japan"


def test_livechat_core_refreshes_persona_from_session_metadata():
    youtube = MagicMock()
    youtube.channels().list().execute.return_value = {"items": [{"id": FOUNDUPS_ID}]}

    core = LiveChatCore(
        youtube_service=youtube,
        video_id="video_123",
        live_chat_id="chat_123",
    )
    core.memory_manager.start_session = MagicMock()
    core.session_manager.initialize_session = AsyncMock(return_value=True)
    core.session_manager.send_greeting = AsyncMock(return_value=True)
    core.session_manager.live_chat_id = "chat_123"
    core.session_manager.channel_title = "FoundUps"
    core.session_manager.channel_id = FOUNDUPS_ID
    core.session_manager.stream_title = "antifaFM Live Stream"
    core.session_manager.actual_start_time = None

    result = asyncio.run(core.initialize())

    assert result is True
    assert core.persona_key == "antifafm"
    assert core.message_processor.persona_key == "antifafm"


def test_orchestrator_refreshes_message_processor_context_from_session_metadata():
    youtube = MagicMock()

    orchestrator = LiveChatOrchestrator(
        youtube_service=youtube,
        video_id="video_123",
        live_chat_id="chat_123",
    )
    orchestrator.session_manager.initialize_session = AsyncMock(return_value=True)
    orchestrator.session_manager.send_greeting = AsyncMock(return_value=True)
    orchestrator.session_manager.live_chat_id = "chat_123"
    orchestrator.session_manager.channel_title = "FoundUps"
    orchestrator.session_manager.channel_id = FOUNDUPS_ID
    orchestrator.session_manager.stream_title = "antifaFM Live Stream"
    orchestrator.message_processor.update_persona_context = MagicMock()

    result = asyncio.run(orchestrator.initialize())

    assert result is True
    orchestrator.message_processor.update_persona_context.assert_called_once()
