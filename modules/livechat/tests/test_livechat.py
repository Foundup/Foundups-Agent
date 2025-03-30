import unittest
from unittest.mock import patch, MagicMock, mock_open, call, Mock
import os
import logging
import asyncio
from datetime import datetime
from googleapiclient.errors import HttpError

# Add module root to Python path for imports
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.livechat import LiveChatListener
from modules.banter_engine import BanterEngine

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AsyncTestCase(unittest.TestCase):
    """Base class for async test cases."""
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def run_async(self, coro):
        """Run a coroutine in the test loop."""
        return self.loop.run_until_complete(coro)

class TestLiveChatListener(AsyncTestCase):
    """Test suite for LiveChatListener class."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        
        # Mock YouTube service
        self.mock_youtube = MagicMock()
        self.mock_youtube.videos().list().execute.return_value = {
            'items': [{
                'liveStreamingDetails': {
                    'activeLiveChatId': 'test_chat_id'
                }
            }]
        }
        self.mock_youtube.liveChat().messages().list().execute.return_value = {
            'items': [],
            'nextPageToken': None
        }
        self.mock_youtube.liveChat().messages().insert().execute.return_value = {
            'id': 'message_id'
        }
        
        self.video_id = "test_video_id"
        self.listener = LiveChatListener(self.mock_youtube, self.video_id)
        
        # Common test data
        self.test_chat_id = "test_chat_id"
        self.test_message = "Test message"
        self.test_username = "TestUser"
        
        # Mock HTTP response for errors
        self.mock_response = MagicMock()
        self.mock_response.status = 403
        self.mock_response.reason = "Forbidden"

        # Create a mock logger for each test
        self.mock_logger = MagicMock()
        self.logger_patcher = patch('src.livechat.logger', self.mock_logger)
        self.logger_patcher.start()
        self.addCleanup(self.logger_patcher.stop)

    def test_init(self):
        """Test initialization of LiveChatListener."""
        self.assertEqual(self.listener.youtube, self.mock_youtube)
        self.assertEqual(self.listener.video_id, self.video_id)
        self.assertIsNone(self.listener.live_chat_id)
        self.assertEqual(self.listener.next_page_token, None)
        self.assertTrue(isinstance(self.listener.message_queue, list))

    @patch('src.livechat.logger')
    def test_get_live_chat_id_success(self, mock_logger):
        """Test successful retrieval of live chat ID."""
        # Act
        chat_id = self.listener._get_live_chat_id()

        # Assert
        self.assertEqual(chat_id, self.test_chat_id)
        self.assertEqual(self.listener.live_chat_id, self.test_chat_id)
        mock_logger.info.assert_called_once_with(f"Found live chat ID: {self.test_chat_id}")

    @patch('src.livechat.logger')
    def test_get_live_chat_id_video_not_found(self, mock_logger):
        """Test handling of video not found error."""
        # Arrange
        self.mock_youtube.videos().list().execute.side_effect = HttpError(
            self.mock_response, b'Video not found'
        )

        # Act
        chat_id = self.listener._get_live_chat_id()

        # Assert
        self.assertIsNone(chat_id)
        mock_logger.error.assert_called_once_with(f"Error getting live chat ID: <HttpError 403 when requesting None returned \"Forbidden\". Details: \"Video not found\">")

    @patch('src.livechat.logger')
    def test_get_live_chat_id_no_active_chat(self, mock_logger):
        """Test handling of no active chat."""
        # Arrange
        self.mock_youtube.videos().list().execute.return_value = {'items': [{'liveStreamingDetails': {}}]}

        # Act
        chat_id = self.listener._get_live_chat_id()

        # Assert
        self.assertIsNone(chat_id)
        mock_logger.warning.assert_called_once_with(f"No active chat found for video: {self.video_id}")

    @patch('src.livechat.logger')
    async def test_poll_chat_messages_success(self, mock_logger):
        """Test successful polling of chat messages."""
        # Arrange
        mock_messages = {
            'items': [
                {
                    'snippet': {
                        'displayMessage': self.test_message,
                        'publishedAt': datetime.utcnow().isoformat() + 'Z'
                    },
                    'authorDetails': {
                        'displayName': self.test_username
                    }
                }
            ],
            'nextPageToken': 'next_page_token'
        }
        self.mock_youtube.liveChat().messages().list().execute.return_value = mock_messages

        # Act
        messages = await self.listener._poll_chat_messages()

        # Assert
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['snippet']['displayMessage'], self.test_message)
        self.assertEqual(self.listener.next_page_token, 'next_page_token')

    @patch('src.livechat.logger')
    async def test_poll_chat_messages_http_error(self, mock_logger):
        """Test handling of HTTP errors during message polling."""
        # Arrange
        self.mock_youtube.liveChat().messages().list().execute.side_effect = HttpError(
            self.mock_response, b'API Error'
        )

        # Act
        messages = await self.listener._poll_chat_messages()

        # Assert
        self.assertEqual(messages, [])
        mock_logger.error.assert_called_once_with(f"Error polling chat messages: <HttpError 403 when requesting None returned \"Forbidden\". Details: \"API Error\">")

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('src.livechat.logger')
    def test_log_to_user_file(self, mock_logger, mock_makedirs, mock_exists, mock_file):
        """Test logging messages to user-specific files."""
        # Arrange
        mock_exists.return_value = False
        test_message = {
            'snippet': {
                'displayMessage': self.test_message,
                'publishedAt': datetime.utcnow().isoformat() + 'Z'
            },
            'authorDetails': {
                'displayName': self.test_username
            }
        }

        # Act
        self.listener._log_to_user_file(test_message)

        # Assert
        expected_dir = os.path.join(self.listener.memory_dir, self.test_username)
        mock_exists.assert_called_once_with(expected_dir)
        mock_makedirs.assert_called_once_with(expected_dir, exist_ok=True)
        mock_file.assert_called_once()
        mock_logger.debug.assert_called_once_with(f"Logged message for user: {self.test_username}")

    @patch('src.livechat.logger')
    async def test_send_chat_message_success(self, mock_logger):
        """Test successful sending of chat message."""
        # Arrange
        self.listener.live_chat_id = self.test_chat_id
        self.mock_youtube.liveChat().messages().insert().execute.return_value = {'id': 'message_id'}

        # Act
        success = await self.listener.send_chat_message(self.test_message)

        # Assert
        self.assertTrue(success)
        mock_logger.info.assert_called_once_with(f"Successfully sent message: {self.test_message}")

    @patch('src.livechat.logger')
    async def test_send_chat_message_failure(self, mock_logger):
        """Test handling of message sending failure."""
        # Arrange
        self.listener.live_chat_id = self.test_chat_id
        self.mock_youtube.liveChat().messages().insert().execute.side_effect = HttpError(
            self.mock_response, b'Failed to send message'
        )

        # Act
        success = await self.listener.send_chat_message(self.test_message)

        # Assert
        self.assertFalse(success)
        mock_logger.error.assert_called_once_with(f"Failed to send message: <HttpError 403 when requesting None returned \"Forbidden\". Details: \"Failed to send message\">")

    def test_send_chat_message_truncation(self):
        """Test message truncation for long messages."""
        # Arrange
        long_message = "x" * 250  # Message longer than YouTube's limit
        expected_length = 197  # 200 - 3 for "..."

        # Act
        truncated = self.listener._truncate_message(long_message)

        # Assert
        self.assertEqual(len(truncated), expected_length)
        self.assertTrue(truncated.endswith("..."))
        self.assertEqual(truncated[:194], "x" * 194)  # Check the content before the ellipsis

class TestLiveChatEmojiTrigger(AsyncTestCase):
    """Test suite for emoji trigger functionality."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        
        # Mock YouTube service
        self.mock_youtube = MagicMock()
        self.mock_youtube.videos().list().execute.return_value = {
            'items': [{
                'liveStreamingDetails': {
                    'activeLiveChatId': 'test_chat_id'
                }
            }]
        }
        self.mock_youtube.liveChat().messages().list().execute.return_value = {
            'items': [],
            'nextPageToken': None
        }
        self.mock_youtube.liveChat().messages().insert().execute.return_value = {
            'id': 'message_id'
        }
        
        self.video_id = "test_video_id"
        self.listener = LiveChatListener(self.mock_youtube, self.video_id)
        self.test_chat_id = "test_chat_id"
        self.test_message = "Test message"
        self.test_username = "TestUser"

        # Create a mock logger for each test
        self.mock_logger = MagicMock()
        self.logger_patcher = patch('src.livechat.logger', self.mock_logger)
        self.logger_patcher.start()
        self.addCleanup(self.logger_patcher.stop)

    def test_emoji_trigger_all_present(self):
        """Test detection of all required emojis."""
        # Arrange
        test_message = {
            'snippet': {
                'displayMessage': "✊✋🖐️",
                'publishedAt': datetime.utcnow().isoformat() + 'Z'
            },
            'authorDetails': {
                'displayName': self.test_username
            }
        }

        # Act
        has_trigger = self.listener._check_emoji_trigger(test_message)

        # Assert
        self.assertTrue(has_trigger)

    def test_emoji_trigger_missing_emoji(self):
        """Test handling of missing emojis."""
        # Arrange
        test_message = {
            'snippet': {
                'displayMessage': "✊✋",  # Missing one emoji
                'publishedAt': datetime.utcnow().isoformat() + 'Z'
            },
            'authorDetails': {
                'displayName': self.test_username
            }
        }

        # Act
        has_trigger = self.listener._check_emoji_trigger(test_message)

        # Assert
        self.assertFalse(has_trigger)

    @patch('src.livechat.logger')
    async def test_emoji_trigger_send_failure(self, mock_logger):
        """Test handling of message sending failure during emoji trigger."""
        # Arrange
        test_message = {
            'snippet': {
                'displayMessage': "✊✋🖐️",
                'publishedAt': datetime.utcnow().isoformat() + 'Z'
            },
            'authorDetails': {
                'displayName': self.test_username,
                'channelId': 'test_channel_id'
            }
        }
        self.mock_youtube.liveChat().messages().insert().execute.side_effect = HttpError(
            self.mock_response, b'Failed to send message'
        )

        # Act
        await self.listener._process_message(test_message)

        # Assert
        mock_logger.error.assert_called_once()

    @patch('src.livechat.logger')
    async def test_emoji_trigger_banter_error(self, mock_logger):
        """Test handling of banter generation error."""
        # Arrange
        test_message = {
            'snippet': {
                'displayMessage': "✊✋🖐️",
                'publishedAt': datetime.utcnow().isoformat() + 'Z'
            },
            'authorDetails': {
                'displayName': self.test_username,
                'channelId': 'test_channel_id'
            }
        }
        self.listener.banter_engine.get_random_banter.side_effect = Exception("Banter error")

        # Act
        await self.listener._process_message(test_message)

        # Assert
        mock_logger.error.assert_called_once()

if __name__ == '__main__':
    unittest.main() 