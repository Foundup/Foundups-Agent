# Windsurfer-Test
# Test module for emoji trigger and BanterEngine functionality

import sys
import os
import logging
from dotenv import load_dotenv

# Add project root to Python path for imports
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

        # Test BanterEngine reply variation
        logger.info("Testing BanterEngine reply variation...")
        from modules.banter_engine import BanterEngine
        banter = BanterEngine()
        samples = set()
        for _ in range(10):
            line = banter.get_random_banter(theme="greeting")
            samples.add(line)
            logger.debug(f"Generated banter: {line}")

        logger.info(f"Collected {len(samples)} unique greeting replies:")
        for line in samples:
            logger.info(f"- {line}")

        return True

    except Exception as e:
        logger.error(f"Error during emoji trigger test: {e}")
        return False

if __name__ == "__main__":
    # Setup logging
    setup_logging()
    
    # Load environment variables
    load_dotenv()
    
    # Run the test
    success = test_emoji_trigger()
    
    if success:
        print("✅ Emoji trigger test completed successfully")
    else:
        print("❌ Emoji trigger test failed")
        sys.exit(1) 