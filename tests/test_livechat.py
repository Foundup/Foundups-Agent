import unittest
from unittest.mock import patch, MagicMock, mock_open, call, Mock
import os
from datetime import datetime
from googleapiclient.errors import HttpError
from modules.livechat import LiveChatListener
from modules.banter_engine import BanterEngine

class TestLiveChatListener(unittest.TestCase):
    """Test suite for LiveChatListener class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_youtube = MagicMock()
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

    def test_init(self):
        """Test initialization of LiveChatListener."""
        self.assertEqual(self.listener.youtube, self.mock_youtube)
        self.assertEqual(self.listener.video_id, self.video_id)
        self.assertIsNone(self.listener.live_chat_id)
        self.assertEqual(self.listener.next_page_token, None)
        self.assertTrue(isinstance(self.listener.message_queue, list))

    @patch('modules.livechat.logging')
    def test_get_live_chat_id_success(self, mock_logging):
        """Test successful retrieval of live chat ID."""
        # Arrange
        mock_response = {
            'items': [{
                'liveStreamingDetails': {
                    'activeLiveChatId': self.test_chat_id
                }
            }]
        }
        self.mock_youtube.videos().list().execute.return_value = mock_response

        # Act
        chat_id = self.listener._get_live_chat_id()

        # Assert
        self.assertEqual(chat_id, self.test_chat_id)
        self.mock_youtube.videos().list.assert_called_once_with(
            part='liveStreamingDetails',
            id=self.video_id
        )
        mock_logging.info.assert_called_with(f"Retrieved live chat ID: {self.test_chat_id}")

    @patch('modules.livechat.logging')
    def test_get_live_chat_id_video_not_found(self, mock_logging):
        """Test handling of video not found."""
        # Arrange
        self.mock_youtube.videos().list().execute.return_value = {'items': []}

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.listener._get_live_chat_id()
        
        self.assertIn("Video not found", str(context.exception))
        mock_logging.error.assert_called_with(f"Video not found: {self.video_id}")

    @patch('modules.livechat.logging')
    def test_get_live_chat_id_no_active_chat(self, mock_logging):
        """Test handling of no active chat."""
        # Arrange
        mock_response = {
            'items': [{
                'liveStreamingDetails': {}
            }]
        }
        self.mock_youtube.videos().list().execute.return_value = mock_response

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.listener._get_live_chat_id()
        
        self.assertIn("No active live chat", str(context.exception))
        mock_logging.error.assert_called_with(f"No active live chat for video: {self.video_id}")

    @patch('modules.livechat.logging')
    def test_poll_chat_messages_success(self, mock_logging):
        """Test successful polling of chat messages."""
        # Arrange
        self.listener.live_chat_id = self.test_chat_id
        mock_message = {
            'authorDetails': {'displayName': self.test_username},
            'snippet': {'displayMessage': self.test_message},
            'id': 'msg123'
        }
        mock_response = {
            'items': [mock_message],
            'nextPageToken': 'next_token',
            'pollingIntervalMillis': 1000
        }
        self.mock_youtube.liveChatMessages().list().execute.return_value = mock_response

        # Act
        messages = self.listener._poll_chat_messages()

        # Assert
        self.assertEqual(messages, [mock_message])
        self.assertEqual(self.listener.next_page_token, 'next_token')
        self.mock_youtube.liveChatMessages().list.assert_called_with(
            liveChatId=self.test_chat_id,
            part='snippet,authorDetails',
            pageToken=None
        )

    @patch('modules.livechat.logging')
    def test_poll_chat_messages_http_error(self, mock_logging):
        """Test handling of HTTP errors during polling."""
        # Arrange
        self.listener.live_chat_id = self.test_chat_id
        http_error = HttpError(self.mock_response, b'Error content')
        self.mock_youtube.liveChatMessages().list().execute.side_effect = http_error

        # Act
        messages = self.listener._poll_chat_messages()

        # Assert
        self.assertEqual(messages, [])
        mock_logging.error.assert_called_with(f"HTTP Error during polling: {http_error}")

    @patch('builtins.open', new_callable=mock_open)
    @patch('modules.livechat.logging')
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_log_to_user_file(self, mock_makedirs, mock_exists, mock_logging, mock_file):
        """Test logging messages to user-specific files."""
        # Arrange
        mock_exists.return_value = False
        test_message = {
            'authorDetails': {'displayName': self.test_username},
            'snippet': {'displayMessage': self.test_message},
            'id': 'msg123'
        }

        # Act
        self.listener._log_to_user_file(test_message)

        # Assert
        expected_path = "memory/chat_logs"
        mock_makedirs.assert_called_once_with(expected_path, exist_ok=True)
        mock_file.assert_called_once_with(f"{expected_path}/{self.test_username}.jsonl", 'a', encoding='utf-8')
        mock_file().write.assert_called_once()  # Check if write was called
        mock_logging.debug.assert_called_with(f"Logged message from {self.test_username}")

    @patch('modules.livechat.logging')
    def test_send_chat_message_success(self, mock_logging):
        """Test successful sending of chat message."""
        # Arrange
        self.listener.live_chat_id = self.test_chat_id
        mock_response = {'id': 'sent_msg_123'}
        self.mock_youtube.liveChatMessages().insert().execute.return_value = mock_response

        # Act
        result = self.listener.send_chat_message(self.test_message)

        # Assert
        self.assertTrue(result)
        self.mock_youtube.liveChatMessages().insert.assert_called_with(
            part='snippet',
            body={
                'snippet': {
                    'liveChatId': self.test_chat_id,
                    'type': 'textMessageEvent',
                    'textMessageDetails': {'messageText': self.test_message}
                }
            }
        )
        mock_logging.info.assert_called_with("Message sent successfully")

    @patch('modules.livechat.logging')
    def test_send_chat_message_failure(self, mock_logging):
        """Test handling of failed message sending."""
        # Arrange
        self.listener.live_chat_id = self.test_chat_id
        http_error = HttpError(self.mock_response, b'Error content')
        self.mock_youtube.liveChatMessages().insert().execute.side_effect = http_error

        # Act
        result = self.listener.send_chat_message(self.test_message)

        # Assert
        self.assertFalse(result)
        mock_logging.error.assert_called_with(f"Failed to send message: {http_error}")

    def test_send_chat_message_truncation(self):
        """Test message truncation for long messages."""
        # Arrange
        self.listener.live_chat_id = self.test_chat_id
        long_message = "x" * 1000  # Message longer than YouTube's limit
        expected_length = 200  # YouTube's maximum message length

        # Act
        self.listener.send_chat_message(long_message)

        # Assert
        sent_message = self.mock_youtube.liveChatMessages().insert.call_args[1]['body']['snippet']['textMessageDetails']['messageText']
        self.assertEqual(len(sent_message), expected_length)
        self.assertTrue(sent_message.endswith('...'))

    def tearDown(self):
        """Clean up test fixtures."""
        pass

class TestLiveChatEmojiTrigger(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.mock_youtube = Mock()
        self.listener = LiveChatListener(
            youtube_service=self.mock_youtube,
            video_id="test_video_id"
        )
        self.listener.live_chat_id = "test_chat_id"
        self.listener.send_chat_message = Mock(return_value=True)
        self.listener.banter_engine = Mock()  # Mock the banter engine

    def test_emoji_trigger_all_present(self):
        """Test when all required emojis are present in message."""
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "Hello ✊ world ✋ test 🖐️"
            },
            "authorDetails": {
                "displayName": "TestUser"
            }
        }
        
        # Set up mock response
        self.listener.banter_engine.get_random_banter.return_value = "Test banter response"
        
        self.listener._process_message(test_message)
        
        # Verify banter was called with correct theme
        self.listener.banter_engine.get_random_banter.assert_called_once_with(theme="greeting")
        
        # Verify send_chat_message was called
        self.listener.send_chat_message.assert_called_once_with("Test banter response")

    def test_emoji_trigger_missing_emoji(self):
        """Test when one or more required emojis are missing."""
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "Hello ✊ world ✋ test"  # Missing 🖐️
            },
            "authorDetails": {
                "displayName": "TestUser"
            }
        }
        
        self.listener._process_message(test_message)
        
        # Verify banter was not called
        self.listener.banter_engine.get_random_banter.assert_not_called()
        
        # Verify send_chat_message was not called
        self.listener.send_chat_message.assert_not_called()

    def test_emoji_trigger_send_failure(self):
        """Test when banter response fails to send."""
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "Hello ✊ world ✋ test 🖐️"
            },
            "authorDetails": {
                "displayName": "TestUser"
            }
        }
        
        # Set up mock response
        self.listener.banter_engine.get_random_banter.return_value = "Test banter response"
        self.listener.send_chat_message.return_value = False
        
        self.listener._process_message(test_message)
        
        # Verify banter was called
        self.listener.banter_engine.get_random_banter.assert_called_once_with(theme="greeting")
        
        # Verify send_chat_message was called but failed
        self.listener.send_chat_message.assert_called_once_with("Test banter response")

    def test_emoji_trigger_banter_error(self):
        """Test when banter engine raises an exception."""
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "Hello ✊ world ✋ test 🖐️"
            },
            "authorDetails": {
                "displayName": "TestUser"
            }
        }
        
        # Make banter engine raise an exception
        self.listener.banter_engine.get_random_banter.side_effect = Exception("Test banter error")
        
        # Should not raise exception
        self.listener._process_message(test_message)
        
        # Verify send_chat_message was not called
        self.listener.send_chat_message.assert_not_called()

if __name__ == '__main__':
    unittest.main()

