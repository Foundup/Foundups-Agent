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
from modules.livechat import LiveChatListener
from utils.oauth_manager import get_authenticated_service_with_fallback
from modules.banter_engine.src.emoji_sequence_map import (
    EMOJI_TO_NUM,
    NUM_TO_EMOJI,
    SEQUENCE_MAP,
    emoji_string_to_tuple,
    tuple_to_emoji_string
)

def test_emoji_mapping():
    """Test the emoji-to-number mapping functionality."""
    logger = logging.getLogger(__name__)
    logger.info("Starting emoji mapping test...")

    try:
        # Test basic mapping
        test_sequence = "✊✋🖐️"
        expected_tuple = (1, 2, 3)
        result = emoji_string_to_tuple(test_sequence)
        assert result == expected_tuple, f"Expected {expected_tuple}, got {result}"
        
        # Test reverse mapping
        result_emoji = tuple_to_emoji_string(expected_tuple)
        assert result_emoji == test_sequence, f"Expected {test_sequence}, got {result_emoji}"
        
        # Test with unknown emoji
        test_with_unknown = "✊❓🖐️"
        result = emoji_string_to_tuple(test_with_unknown)
        assert result == (1, 0, 3), f"Expected (1, 0, 3), got {result}"
        
        # Test sequence map lookup
        test_state = SEQUENCE_MAP[expected_tuple]
        assert test_state["tone"] == "metaphoric, humor, symbolic wit"
        assert test_state["state"] == "awakening in progress"
        
        logger.info("Emoji mapping tests passed successfully")
        return True

    except AssertionError as e:
        logger.error(f"Assertion error in emoji mapping test: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error during emoji mapping test: {str(e)}")
        return False

@pytest.mark.asyncio
async def test_emoji_trigger():
    """Test emoji trigger logic using LiveChatListener instance"""
    mock_youtube = MagicMock()
    listener = LiveChatListener(youtube_service=mock_youtube, video_id="test_video_id")
    listener.live_chat_id = "test_chat_id"
    listener.send_chat_message = AsyncMock(return_value=True)
    listener.banter_engine = MagicMock()
    # Explicitly mock rate limiter to ensure it doesn't interfere
    listener._is_rate_limited = MagicMock(return_value=False)

    test_message = {
        "id": "test_id",
        "snippet": {
            "displayMessage": "✊✋🖐️"
        },
        "authorDetails": {
            "displayName": "TestUser",
            "channelId": "UCtestchannelid"
        }
    }

    listener.banter_engine.get_random_banter.return_value = "Banter response"
    
    await listener._process_message(test_message)
    
    # Assertions
    listener._is_rate_limited.assert_called_once() # Verify rate limit check happened
    listener.banter_engine.get_random_banter.assert_called_once_with(theme="greeting")
    listener.send_chat_message.assert_awaited_once_with("Banter response")
    assert True

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