# Windsurfer-Test
# Test module for emoji trigger and BanterEngine functionality

import sys
import os
import logging
from dotenv import load_dotenv
import unittest
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# Add module root to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_config import setup_logging
from modules.communication.livechat.livechat import LiveChatListener
from utils.oauth_manager import get_authenticated_service_with_fallback
from modules.ai_intelligence.banter_engine.banter_engine.emoji_sequence_map import (
    EMOJI_TO_NUMBER,
    NUM_TO_EMOJI,
    emoji_string_to_tuple,
    tuple_to_emoji_string,
)
from modules.ai_intelligence.banter_engine.banter_engine.sequence_responses import SEQUENCE_MAP

def test_emoji_mapping():
    """Test the emoji-to-number mapping functionality."""
    # Test basic mapping
    test_sequence = "✊✋🖐️"
    expected_tuple = (0, 1, 2)
    result = emoji_string_to_tuple(test_sequence)
    assert result == expected_tuple, f"Expected {expected_tuple}, got {result}"
    
    # Test reverse mapping
    result_emoji = tuple_to_emoji_string(expected_tuple)
    assert result_emoji == test_sequence, f"Expected {test_sequence}, got {result_emoji}"
    
    # Test with invalid sequence (contains unknown emoji) - should return empty tuple
    test_with_unknown = "✊❓🖐️"
    result = emoji_string_to_tuple(test_with_unknown)
    assert result == (), f"Expected (), got {result}"  # Invalid sequence returns empty tuple
    
    # Test that single emojis return empty tuple (only 3-emoji sequences are valid)
    for emoji, expected_num in EMOJI_TO_NUMBER.items():
        result = emoji_string_to_tuple(emoji)
        assert result == (), f"Expected (), got {result} for single emoji '{emoji}'"
    
    # Test valid 3-emoji sequences
    valid_sequences = [
        ("✊✊✊", (0, 0, 0)),
        ("✊✊✋", (0, 0, 1)),
        ("✊✊🖐️", (0, 0, 2)),
        ("✊✋✋", (0, 1, 1)),
        ("✊✋🖐️", (0, 1, 2)),
        ("✊🖐️🖐️", (0, 2, 2)),
        ("✋✋✋", (1, 1, 1)),
        ("✋✋🖐️", (1, 1, 2)),
        ("✋🖐️🖐️", (1, 2, 2)),
        ("🖐️🖐️🖐️", (2, 2, 2))
    ]
    
    for emoji_seq, expected_tuple in valid_sequences:
        result = emoji_string_to_tuple(emoji_seq)
        assert result == expected_tuple, f"Expected {expected_tuple}, got {result} for sequence '{emoji_seq}'"

@pytest.mark.asyncio
async def test_emoji_trigger():
    """Test emoji trigger logic using LiveChatListener instance"""
    mock_youtube = MagicMock()
    listener = LiveChatListener(youtube_service=mock_youtube, video_id="test_video_id")
    listener.live_chat_id = "test_chat_id"
    listener.send_chat_message = AsyncMock(return_value=True)
    
    # Mock the banter engine to return a proper response
    listener.banter_engine.process_input = MagicMock(return_value=("State: test", "Test response"))
    
    # Mock rate limiter to ensure it doesn't interfere
    listener._is_rate_limited = MagicMock(return_value=False)
    listener._update_trigger_time = MagicMock()
    
    # Mock bot channel ID to prevent self-message filtering
    listener.bot_channel_id = "different_channel_id"

    test_message = {
        "id": "test_id",
        "snippet": {
            "displayMessage": "✊✋🖐️"  # This should trigger the emoji pattern
        },
        "authorDetails": {
            "displayName": "TestUser",
            "channelId": "UCtestchannelid"
        }
    }

    # Process the message
    await listener._process_message(test_message)

    # Verify that the banter engine was called
    listener.banter_engine.process_input.assert_called_once_with("✊✋🖐️")
    
    # Verify that send_chat_message was called
    listener.send_chat_message.assert_called_once_with("Test response")

# REMOVE THE if __name__ == "__main__" block below
# if __name__ == "__main__":
#     setup_logging()
#     # Run both tests
#     mapping_success = test_emoji_mapping()
#     # Need asyncio.run for async test if run directly
#     # trigger_success = asyncio.run(test_emoji_trigger())
#     
#     print(f"Emoji mapping test {'passed' if mapping_success else 'failed'}")
#     # print(f"Emoji trigger test {'passed' if trigger_success else 'failed'}") 