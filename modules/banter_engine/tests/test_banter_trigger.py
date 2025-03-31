# Windsurfer-Test
# Test module for emoji trigger and BanterEngine functionality

import sys
import os
import logging
from dotenv import load_dotenv

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

def test_emoji_trigger():
    """Test the emoji trigger (✊✋🖐️) in LiveChatListener."""
    logger = logging.getLogger(__name__)
    logger.info("Starting emoji trigger test...")

    try:
        # Initialize YouTube service (required for LiveChatListener)
        youtube_service = get_authenticated_service_with_fallback()
        if not youtube_service:
            logger.error("Failed to initialize YouTube service")
            return False

        # Create a test instance of LiveChatListener
        test_video_id = "test_video_id"
        test_chat_id = "test_chat_id"
        listener = LiveChatListener(youtube_service, test_video_id, test_chat_id)

        # Test with sequence map
        test_tuple = (1, 2, 3)  # Corresponds to ✊✋🖐️
        test_emoji = tuple_to_emoji_string(test_tuple)
        test_state = SEQUENCE_MAP[test_tuple]
        
        # Construct test message with trigger emojis
        test_message = {
            "id": "test_message_id",
            "snippet": {
                "displayMessage": test_emoji,
                "publishedAt": "2024-03-30T00:00:00Z"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "test_channel_id"
            }
        }

        logger.info(f"Processing test message with emoji trigger: {test_state['tone']}")
        listener._process_message(test_message)
        logger.info("Test message processed successfully")
        return True

    except Exception as e:
        logger.error(f"Error during emoji trigger test: {str(e)}")
        return False

if __name__ == "__main__":
    setup_logging()
    # Run both tests
    mapping_success = test_emoji_mapping()
    trigger_success = test_emoji_trigger()
    
    print(f"Emoji mapping test {'passed' if mapping_success else 'failed'}")
    print(f"Emoji trigger test {'passed' if trigger_success else 'failed'}") 