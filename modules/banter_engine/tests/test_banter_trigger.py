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
        # Using dummy values since we're only testing message processing
        test_video_id = "test_video_id"
        test_chat_id = "test_chat_id"
        listener = LiveChatListener(youtube_service, test_video_id, test_chat_id)

        # Construct test message with trigger emojis
        test_message = {
            "id": "test_message_id",  # Required field for message processing
            "snippet": {
                "displayMessage": "✊✋🖐️",
                "publishedAt": "2024-03-30T00:00:00Z"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "test_channel_id"
            }
        }

        logger.info("Processing test message with emoji trigger...")
        listener._process_message(test_message)
        logger.info("Test message processed successfully")
        return True

    except Exception as e:
        logger.error(f"Error during emoji trigger test: {str(e)}")
        return False

if __name__ == "__main__":
    setup_logging()
    success = test_emoji_trigger()
    print(f"Test {'passed' if success else 'failed'}") 