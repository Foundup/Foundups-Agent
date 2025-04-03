# Windsurfer-Test
# Test module for emoji trigger and BanterEngine functionality

import sys
import os
import logging
from dotenv import load_dotenv
import unittest
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# Add project root to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_config import setup_logging
from modules.livechat import LiveChatListener
from utils.oauth_manager import get_authenticated_service_with_fallback

@pytest.mark.asyncio
async def test_emoji_trigger():
    """Test emoji trigger logic using LiveChatListener instance"""
    mock_youtube = MagicMock()
    listener = LiveChatListener(youtube_service=mock_youtube, video_id="test_video_id")
    listener.live_chat_id = "test_chat_id"
    # Use AsyncMock for the async send_chat_message
    listener.send_chat_message = AsyncMock(return_value=True)  
    listener.banter_engine = MagicMock()  # Mock banter_engine
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
    
    # Await the call to the async function
    await listener._process_message(test_message)
    
    # Assertions
    listener._is_rate_limited.assert_called_once() # Verify rate limit check happened
    listener.banter_engine.get_random_banter.assert_called_once_with(theme="greeting")
    # Assert that the AsyncMock was awaited
    listener.send_chat_message.assert_awaited_once_with("Banter response")
    assert True

# REMOVE THE if __name__ == "__main__" block below
# if __name__ == "__main__":
#     # Setup logging
#     setup_logging()
#     
#     # Load environment variables
#     load_dotenv()
#     
#     # Run the test using asyncio
#     import asyncio
#     try:
#         asyncio.run(test_emoji_trigger())
#         print("✅ Emoji trigger test completed successfully")
#     except AssertionError as e:
#         print(f"❌ Emoji trigger test failed: {e}")
#         sys.exit(1)
#     except Exception as e:
#         print(f"❌ Emoji trigger test failed with unexpected error: {e}")
#         sys.exit(1) 