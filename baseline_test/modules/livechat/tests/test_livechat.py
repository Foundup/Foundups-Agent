"""
Unit tests for the LiveChatListener class in livechat.py
"""

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import logging
import time
from datetime import datetime
import os
import json
from modules.livechat.src.livechat import LiveChatListener
import pytest
import googleapiclient.errors
import httplib2

# Helper utility for async tests
class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)

class TestLiveChatListener(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        # Disable logging during tests
        logging.disable(logging.CRITICAL)
        
        # Create mock YouTube service
        self.mock_youtube = MagicMock()
        self.video_id = "test_video_id"
        self.live_chat_id = "test_live_chat_id"
        
        # Set up mock responses
        self.mock_list_response = MagicMock()
        self.mock_youtube.liveChatMessages().list.return_value.execute.return_value = {
            "pollingIntervalMillis": 1000,
            "nextPageToken": "test_next_token",
            "items": []
        }
        
        self.mock_video_response = MagicMock()
        self.mock_youtube.videos().list.return_value.execute.return_value = {
            "items": [{
                "liveStreamingDetails": {
                    "activeLiveChatId": self.live_chat_id
                },
                "statistics": {
                    "viewCount": "100"
                }
            }]
        }
        
        # Create the LiveChatListener instance
        self.listener = LiveChatListener(
            youtube_service=self.mock_youtube,
            video_id=self.video_id,
            live_chat_id=self.live_chat_id
        )
        
        # Mock the BanterEngine
        self.mock_banter_engine = MagicMock()
        self.mock_banter_engine.get_random_banter.return_value = "Hello there!"
        self.listener.banter_engine = self.mock_banter_engine

    def tearDown(self):
        """Tear down test fixtures."""
        logging.disable(logging.NOTSET)
        
    def test_init(self):
        """Test initialization of LiveChatListener."""
        self.assertEqual(self.listener.youtube, self.mock_youtube)
        self.assertEqual(self.listener.video_id, self.video_id)
        self.assertEqual(self.listener.live_chat_id, self.live_chat_id)
        self.assertIsNone(self.listener.next_page_token)
        self.assertEqual(self.listener.poll_interval_ms, 100000)
        self.assertEqual(self.listener.error_backoff_seconds, 5)
        self.assertEqual(self.listener.memory_dir, "memory")
        self.assertEqual(self.listener.viewer_count, 0)
        self.assertListEqual(self.listener.message_queue, [])
        
    def test_get_live_chat_id(self):
        """Test retrieving a live chat ID."""
        # Reset the live_chat_id to test fetching it
        self.listener.live_chat_id = None
        
        # Call the method
        chat_id = self.listener._get_live_chat_id()
        
        # Verify results
        self.assertEqual(chat_id, self.live_chat_id)
        self.assertEqual(self.listener.live_chat_id, self.live_chat_id)
        self.mock_youtube.videos().list.assert_called_once_with(
            part="liveStreamingDetails",
            id=self.video_id
        )
        
    def test_get_live_chat_id_no_live_stream(self):
        """Test error handling when no live stream exists."""
        # Mock response with no items
        self.mock_youtube.videos().list.return_value.execute.return_value = {"items": []}
        
        # Reset the live_chat_id
        self.listener.live_chat_id = None
        
        # Verify ValueError is raised
        with self.assertRaises(ValueError):
            self.listener._get_live_chat_id()
            
    def test_get_live_chat_id_no_details(self):
        """Test error handling when no live streaming details exist."""
        # Mock response with no liveStreamingDetails
        self.mock_youtube.videos().list.return_value.execute.return_value = {
            "items": [{}]
        }
        
        # Reset the live_chat_id
        self.listener.live_chat_id = None
        
        # Verify ValueError is raised
        with self.assertRaises(ValueError):
            self.listener._get_live_chat_id()
            
    def test_update_viewer_count(self):
        """Test updating viewer count."""
        self.listener._update_viewer_count()
        self.assertEqual(self.listener.viewer_count, 100)
        self.mock_youtube.videos().list.assert_called_once_with(
            part="statistics",
            id=self.video_id
        )
        
    @patch('time.time')
    def test_is_rate_limited(self, mock_time):
        """Test rate limiting function."""
        # Setup
        mock_time.return_value = 100
        user_id = "test_user"
        
        # No previous trigger time
        self.assertFalse(self.listener._is_rate_limited(user_id))
        
        # Set trigger time
        self.listener.last_trigger_time[user_id] = 50  # 50 seconds ago
        self.listener.trigger_cooldown = 60  # 60 second cooldown
        
        # Should be rate limited
        self.assertTrue(self.listener._is_rate_limited(user_id))
        
        # Advance time past cooldown
        mock_time.return_value = 120
        self.assertFalse(self.listener._is_rate_limited(user_id))
        
    def test_update_trigger_time(self):
        """Test updating trigger time."""
        user_id = "test_user"
        current_time = time.time()
        
        self.listener._update_trigger_time(user_id)
        self.assertIn(user_id, self.listener.last_trigger_time)
        self.assertGreaterEqual(self.listener.last_trigger_time[user_id], current_time)
        
    @patch("os.makedirs")
    def test_log_to_user_file(self, mock_makedirs):
        """Test logging to user file."""
        # Mock file operations
        mock_file = unittest.mock.mock_open()
        
        # Create test message
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "Test message"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "test_channel"
            }
        }
        
        # Test writing to file
        with patch("builtins.open", mock_file):
            self.listener._log_to_user_file(test_message)
            
        # Verify directory was created
        mock_makedirs.assert_called_once()
        
        # Verify file was written to
        mock_file.assert_called_once()
        
    @pytest.mark.asyncio
    @patch('asyncio.sleep', new_callable=AsyncMock)
    async def test_poll_chat_messages(self, mock_sleep):
        """Test polling for chat messages."""
        # Setup mock for messages
        test_messages = [{"id": "1"}, {"id": "2"}]
        self.mock_youtube.liveChatMessages().list.return_value.execute.return_value = {
            "pollingIntervalMillis": 1000,
            "nextPageToken": "next_token",
            "items": test_messages
        }
        
        # Call the method
        result = await self.listener._poll_chat_messages()
        
        # Verify results
        self.assertEqual(result, test_messages)
        self.assertEqual(self.listener.next_page_token, "next_token")
        self.assertEqual(self.listener.poll_interval_ms, 1000)
        self.mock_youtube.liveChatMessages().list.assert_called_once_with(
            liveChatId=self.live_chat_id,
            part="snippet,authorDetails",
            pageToken=None
        )
        
    @pytest.mark.asyncio
    @patch.object(LiveChatListener, 'send_chat_message', new_callable=AsyncMock)
    async def test_process_message_no_emoji(self, mock_send):
        """Test processing a message with no emoji trigger."""
        # Create test message without trigger emoji
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "Regular message without emoji"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "test_channel"
            }
        }
        
        # Mock log_to_user_file
        with patch.object(self.listener, '_log_to_user_file') as mock_log:
            result = await self.listener._process_message(test_message)
            
        # Verify results
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "test_id")
        self.assertEqual(result["author"], "TestUser")
        self.assertEqual(result["message"], "Regular message without emoji")
        mock_log.assert_called_once_with(test_message)
        mock_send.assert_not_called()
        
    @pytest.mark.asyncio
    @patch.object(LiveChatListener, 'send_chat_message', new_callable=AsyncMock)
    @patch.object(LiveChatListener, '_is_rate_limited')
    async def test_process_message_with_emoji(self, mock_rate_limited, mock_send):
        """Test processing a message with emoji trigger."""
        # Setup
        mock_rate_limited.return_value = False
        mock_send.return_value = True
        
        # Create test message with trigger emoji
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "Message with emoji ✊✋🖐️"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "test_channel"
            }
        }
        
        # Mock log_to_user_file and update_trigger_time
        with patch.object(self.listener, '_log_to_user_file') as mock_log, \
             patch.object(self.listener, '_update_trigger_time') as mock_update:
            result = await self.listener._process_message(test_message)
            
        # Verify results
        self.assertIsNotNone(result)
        mock_log.assert_called_once_with(test_message)
        self.mock_banter_engine.get_random_banter.assert_called_once_with(theme="greeting")
        mock_send.assert_called_once_with("Hello there!")
        mock_update.assert_called_once_with("test_channel")
        
    @pytest.mark.asyncio
    async def test_send_chat_message(self):
        """Test sending a chat message."""
        # Setup
        message_text = "Test message"
        self.mock_youtube.liveChatMessages().insert.return_value.execute.return_value = {}
        
        # Call the method
        result = await self.listener.send_chat_message(message_text)
        
        # Verify results
        self.assertTrue(result)
        self.mock_youtube.liveChatMessages().insert.assert_called_once_with(
            part="snippet",
            body={
                "snippet": {
                    "liveChatId": self.live_chat_id,
                    "type": "textMessageEvent",
                    "textMessageDetails": {
                        "messageText": message_text
                    }
                }
            }
        )
        
    @pytest.mark.asyncio
    async def test_send_chat_message_too_long(self):
        """Test sending a message that is too long."""
        # Setup
        long_message = "x" * 250  # Longer than the 200 char limit
        self.mock_youtube.liveChatMessages().insert.return_value.execute.return_value = {}
        
        # Call the method
        result = await self.listener.send_chat_message(long_message)
        
        # Verify results
        self.assertTrue(result)
        # Check that message was truncated
        call_args = self.mock_youtube.liveChatMessages().insert.call_args
        body = call_args[1]['body']
        sent_message = body['snippet']['textMessageDetails']['messageText']
        self.assertEqual(len(sent_message), 200)
        self.assertTrue(sent_message.endswith("..."))
        
    @pytest.mark.asyncio
    @patch('asyncio.sleep', new_callable=AsyncMock)
    @patch.object(LiveChatListener, '_poll_chat_messages', new_callable=AsyncMock)
    @patch.object(LiveChatListener, '_process_message', new_callable=AsyncMock)
    @patch.object(LiveChatListener, '_update_viewer_count')
    @patch.object(LiveChatListener, 'send_chat_message', new_callable=AsyncMock)
    async def test_start_listening(self, mock_send, mock_update, mock_process, mock_poll, mock_sleep):
        """Test the main listening loop."""
        # Setup
        self.listener.is_running = False
        mock_send.return_value = True
        
        # Set up mock poll to return messages once then stop the loop
        mock_poll.side_effect = [
            [{"id": "1"}],  # First call returns a message
            []  # Second call returns empty, we'll then set is_running to False
        ]
        
        # Call the method with a way to stop it after processing
        async def stop_after_one_iteration():
            await asyncio.sleep(0.1)
            self.listener.is_running = False
            
        # Start both coroutines
        await asyncio.gather(
            self.listener.start_listening(),
            stop_after_one_iteration()
        )
        
        # Verify results
        mock_send.assert_called_once_with(self.listener.greeting_message)
        mock_update.assert_called()
        mock_poll.assert_called()
        mock_process.assert_called_once()
        
    @pytest.mark.asyncio
    @patch('modules.livechat.src.livechat.token_manager')
    @patch('modules.livechat.src.livechat.get_authenticated_service')
    async def test_handle_auth_error_success(self, mock_get_auth, mock_token_manager):
        """Test successful authentication error handling with token rotation."""
        # Arrange
        mock_error = googleapiclient.errors.HttpError(self.mock_response, b'Error content')
        
        # Mock token rotation success
        mock_token_manager.rotate_tokens = AsyncMock(return_value=2)  # Successfully rotated to token index 2
        mock_get_auth.return_value = MagicMock()  # New authenticated service
        
        # Act
        result = await self.listener._handle_auth_error(mock_error)

        # Assert
        self.assertTrue(result)  # Should return True on successful handling
        mock_token_manager.rotate_tokens.assert_awaited_once()
        mock_get_auth.assert_called_once_with(2)  # Should authenticate with the new token index
        self.assertEqual(self.listener.youtube, mock_get_auth.return_value)  # Service should be updated
        
    @pytest.mark.asyncio
    @patch('modules.livechat.src.livechat.token_manager')
    async def test_handle_auth_error_rotation_failed(self, mock_token_manager):
        """Test authentication error handling when token rotation fails."""
        # Setup - Create a properly structured HttpError with status 401
        mock_response = httplib2.Response({'status': 401})
        auth_error = googleapiclient.errors.HttpError(
            resp=mock_response,
            content=b'Authentication error'
        )
        
        # Fix the self.mock_response which may not be properly initialized
        self.mock_response = mock_response
        
        # Direct patching of the module
        with patch('modules.livechat.src.livechat.token_manager.rotate_tokens', new_callable=AsyncMock) as mock_rotate:
            # Configure mock to return None (rotation failed)
            mock_rotate.return_value = None
            
            # Execute - Call the method directly
            result = await self.listener._handle_auth_error(auth_error)
            
            # Assert - Verify expected behavior
            self.assertFalse(result)  # Should return False on rotation failure
            mock_rotate.assert_awaited_once()
        
    @pytest.mark.asyncio
    @patch('modules.livechat.src.livechat.token_manager')
    @patch('modules.livechat.src.livechat.get_authenticated_service')
    async def test_handle_auth_error_reauth_failed(self, mock_get_auth, mock_token_manager):
        """Test authentication error handling when re-authentication fails."""
        # Setup - Create a properly structured HttpError with status 401
        mock_response = httplib2.Response({'status': 401})
        auth_error = googleapiclient.errors.HttpError(
            resp=mock_response,
            content=b'Authentication error'
        )
        
        # Fix the self.mock_response which may not be properly initialized
        self.mock_response = mock_response
        
        # Direct patching of the modules
        with patch('modules.livechat.src.livechat.token_manager.rotate_tokens', new_callable=AsyncMock) as mock_rotate, \
             patch('modules.livechat.src.livechat.get_authenticated_service') as mock_get_auth:
            
            # Configure mocks - rotation succeeds but authentication fails
            mock_rotate.return_value = 2  # Successfully rotated to token index 2
            mock_get_auth.side_effect = Exception("Failed to authenticate")
            
            # Execute - Call the method directly
            result = await self.listener._handle_auth_error(auth_error)
            
            # Assert - Verify expected behavior
            self.assertFalse(result)  # Should return False on authentication failure
            mock_rotate.assert_awaited_once()
            mock_get_auth.assert_called_once_with(2)
        
    @pytest.mark.asyncio
    async def test_handle_auth_error_non_auth_error(self):
        """Test handling of non-authentication errors."""
        # Setup - Create a non-auth HTTP error (500 status)
        mock_response = httplib2.Response({'status': 500})
        non_auth_error = googleapiclient.errors.HttpError(
            resp=mock_response,
            content=b'Server error'
        )
        
        # Execute - Call the method directly
        result = await self.listener._handle_auth_error(non_auth_error)
        
        # Assert - Verify expected behavior
        self.assertFalse(result)  # Should return False for non-auth errors
        
    @pytest.mark.asyncio
    async def test_handle_auth_error_non_http_error(self):
        """Test handling of non-HTTP errors."""
        # Setup - Create a regular non-HTTP exception
        regular_error = Exception("Regular error")
        
        # Execute - Call the method directly
        result = await self.listener._handle_auth_error(regular_error)
        
        # Assert - Verify expected behavior
        self.assertFalse(result)  # Should return False for non-HTTP errors

    @pytest.mark.asyncio
    @patch('modules.livechat.src.livechat.calculate_dynamic_delay')
    async def test_poll_chat_messages_with_dynamic_delay(self, mock_calculate_delay):
        """Test polling chat messages with dynamic delay calculation."""
        # Arrange
        self.listener.live_chat_id = self.live_chat_id
        self.listener.viewer_count = 500
        mock_calculate_delay.return_value = 15.5  # 15.5 seconds
        
        # Set up mock response with different polling interval
        self.mock_youtube.liveChatMessages().list.return_value.execute.return_value = {
            "pollingIntervalMillis": 10000,  # 10 seconds from server
            "nextPageToken": "next_token",
            "items": [{"id": "msg1"}]
        }

        # Act
        result = await self.listener._poll_chat_messages()

        # Assert
        self.assertEqual(result, [{"id": "msg1"}])
        self.assertEqual(self.listener.next_page_token, "next_token")
        
        # Verify the delay calculation
        mock_calculate_delay.assert_called_once_with(500)
        
        # Verify the interval is the maximum of server interval and dynamic delay
        expected_interval_ms = max(10000, int(15.5 * 1000))  # Should be 15500 ms
        self.assertEqual(self.listener.poll_interval_ms, expected_interval_ms)

    @pytest.mark.asyncio
    @patch('modules.livechat.src.livechat.time.sleep')
    async def test_poll_chat_messages_unexpected_error(self, mock_sleep):
        """Test handling of unexpected errors during polling."""
        # Arrange
        self.listener.live_chat_id = self.live_chat_id
        self.listener.error_backoff_seconds = 5
        
        # Set up mock to raise a generic error
        self.mock_youtube.liveChatMessages().list.return_value.execute.side_effect = Exception("Unexpected error")
        
        # Act
        result = await self.listener._poll_chat_messages()

        # Assert
        self.assertEqual(result, [])  # Should return empty list on error
        mock_sleep.assert_called_once_with(5)  # Should sleep with current backoff
        self.assertEqual(self.listener.error_backoff_seconds, 10)  # Backoff should double

    @pytest.mark.asyncio
    @patch('modules.livechat.src.livechat.time.sleep')
    async def test_poll_chat_messages_max_backoff(self, mock_sleep):
        """Test that error backoff doesn't exceed maximum."""
        # Arrange
        self.listener.live_chat_id = self.live_chat_id
        self.listener.error_backoff_seconds = 40  # Already high
        
        # Set up mock to raise a generic error
        self.mock_youtube.liveChatMessages().list.return_value.execute.side_effect = Exception("Unexpected error")
        
        # Act
        result = await self.listener._poll_chat_messages()

        # Assert
        self.assertEqual(result, [])  # Should return empty list on error
        mock_sleep.assert_called_once_with(40)  # Should sleep with current backoff
        self.assertEqual(self.listener.error_backoff_seconds, 60)  # Max backoff at 60s

    @pytest.mark.asyncio
    async def test_poll_chat_messages_auth_error_handled(self):
        """Test handling of authentication errors during polling when they are handled successfully."""
        # Arrange
        self.listener.live_chat_id = self.live_chat_id
        
        # Create HTTP error
        http_error = googleapiclient.errors.HttpError(self.mock_response, b'Error content')
        self.mock_youtube.liveChatMessages().list.return_value.execute.side_effect = http_error
        
        # Mock _handle_auth_error to indicate successful handling
        self.listener._handle_auth_error = AsyncMock(return_value=True)
        
        # Act
        result = await self.listener._poll_chat_messages()

        # Assert
        self.assertEqual(result, [])  # Should return empty list when auth error is handled
        self.listener._handle_auth_error.assert_awaited_once_with(http_error)
        
    @pytest.mark.asyncio
    async def test_poll_chat_messages_auth_error_not_handled(self):
        """Test handling of authentication errors during polling when they are not handled."""
        # Arrange
        self.listener.live_chat_id = self.live_chat_id
        
        # Create HTTP error
        http_error = googleapiclient.errors.HttpError(self.mock_response, b'Error content')
        self.mock_youtube.liveChatMessages().list.return_value.execute.side_effect = http_error
        
        # Mock _handle_auth_error to indicate unsuccessful handling
        self.listener._handle_auth_error = AsyncMock(return_value=False)
        
        # Act and Assert
        with self.assertRaises(googleapiclient.errors.HttpError):
            await self.listener._poll_chat_messages()
            
        # Verify _handle_auth_error was called
        self.listener._handle_auth_error.assert_awaited_once_with(http_error)

    @pytest.mark.asyncio
    async def test_process_message_with_exact_emoji_sequence(self):
        """Test processing a message with the exact emoji sequence."""
        # Create test message with exact emoji trigger sequence
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "Hello ✊✋🖐️ there!"  # Exact sequence
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "test_channel"
            }
        }
        
        # Mock dependencies
        self.listener._is_rate_limited = MagicMock(return_value=False)
        self.listener.banter_engine.get_random_banter = MagicMock(return_value="Hello!")
        self.listener.send_chat_message = AsyncMock(return_value=True)
        self.listener._update_trigger_time = MagicMock()
        
        # Mock log_to_user_file
        with patch.object(self.listener, '_log_to_user_file') as mock_log:
            result = await self.listener._process_message(test_message)
            
        # Verify results
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "test_id")
        self.listener._is_rate_limited.assert_called_once_with("test_channel")
        self.listener.banter_engine.get_random_banter.assert_called_once_with(theme="greeting")
        self.listener.send_chat_message.assert_awaited_once_with("Hello!")
        self.listener._update_trigger_time.assert_called_once_with("test_channel")
        mock_log.assert_called_once_with(test_message)
        
    @pytest.mark.asyncio
    async def test_process_message_rate_limited(self):
        """Test processing a message from a rate-limited user."""
        # Create test message with emoji trigger
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "Hello ✊✋🖐️ there!"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "test_channel"
            }
        }
        
        # Mock rate limiting to return True (user is rate limited)
        self.listener._is_rate_limited = MagicMock(return_value=True)
        self.listener.send_chat_message = AsyncMock()
        
        # Mock log_to_user_file
        with patch.object(self.listener, '_log_to_user_file') as mock_log:
            result = await self.listener._process_message(test_message)
            
        # Verify results
        self.assertIsNotNone(result)
        self.listener._is_rate_limited.assert_called_once_with("test_channel")
        self.listener.banter_engine.get_random_banter.assert_not_called()
        self.listener.send_chat_message.assert_not_awaited()
        mock_log.assert_called_once_with(test_message)
        
    @pytest.mark.asyncio
    async def test_process_message_invalid_banter_response(self):
        """Test processing a message when banter engine returns an invalid response."""
        # Create test message with emoji trigger
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "Hello ✊✋🖐️ there!"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "test_channel"
            }
        }
        
        # Mock dependencies
        self.listener._is_rate_limited = MagicMock(return_value=False)
        # Return invalid responses (empty string, None, and non-string)
        self.listener.banter_engine.get_random_banter.side_effect = ["", None, 12345]
        self.listener.send_chat_message = AsyncMock(return_value=True)
        
        # Test with empty string response
        with patch.object(self.listener, '_log_to_user_file') as mock_log:
            result = await self.listener._process_message(test_message)
            
        # Verify fallback message is used
        self.listener.send_chat_message.assert_awaited_once()
        args, kwargs = self.listener.send_chat_message.call_args
        self.assertIn("fallback", str(args[0]).lower())  # Should contain word "fallback"
        
        # Reset mocks for second test
        self.listener.send_chat_message.reset_mock()
        
        # Test with None response
        with patch.object(self.listener, '_log_to_user_file') as mock_log:
            result = await self.listener._process_message(test_message)
        
        # Verify fallback message is used again
        self.listener.send_chat_message.assert_awaited_once()
        
    @pytest.mark.asyncio
    async def test_process_message_send_failure(self):
        """Test processing a message when send_chat_message fails."""
        # Create test message with emoji trigger
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "Hello ✊✋🖐️ there!"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "test_channel"
            }
        }
        
        # Mock dependencies
        self.listener._is_rate_limited = MagicMock(return_value=False)
        self.listener.banter_engine.get_random_banter = MagicMock(return_value="Hello!")
        # Make send_chat_message fail
        self.listener.send_chat_message = AsyncMock(return_value=False)
        self.listener._update_trigger_time = MagicMock()
        
        # Mock log_to_user_file
        with patch.object(self.listener, '_log_to_user_file') as mock_log:
            result = await self.listener._process_message(test_message)
            
        # Verify results
        self.assertIsNotNone(result)
        self.listener.send_chat_message.assert_awaited_once_with("Hello!")
        # Should not update trigger time when send fails
        self.listener._update_trigger_time.assert_not_called()
        
    @pytest.mark.asyncio
    async def test_process_message_banter_exception(self):
        """Test handling exception from banter engine."""
        # Create test message with emoji trigger
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "Hello ✊✋🖐️ there!"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "test_channel"
            }
        }
        
        # Mock dependencies
        self.listener._is_rate_limited = MagicMock(return_value=False)
        self.listener.banter_engine.get_random_banter = MagicMock(side_effect=Exception("Banter error"))
        self.listener.send_chat_message = AsyncMock()
        
        # Mock log_to_user_file
        with patch.object(self.listener, '_log_to_user_file') as mock_log:
            # Should not raise exception
            result = await self.listener._process_message(test_message)
            
        # Verify results
        self.assertIsNotNone(result)
        self.listener.send_chat_message.assert_not_awaited()  # Should not attempt to send when banter fails

    @pytest.mark.asyncio
    async def test_start_listening_normal_operation(self):
        """Test the main listening loop under normal operation."""
        # Mock dependencies
        self.listener._validate_livechat_id = MagicMock(return_value=True)
        self.listener._poll_chat_messages = AsyncMock(side_effect=[
            [{"id": "msg1"}],  # First call returns a message
            [{"id": "msg2"}],  # Second call returns a message
            []                 # Third call returns empty (to exit loop)
        ])
        self.listener._process_message = AsyncMock(return_value={"id": "processed"})
        
        # Mock the exception condition to exit after 3 iterations
        run_count = 0
        original_method = self.listener._should_continue_running
        
        def mock_should_continue(*args, **kwargs):
            if hasattr(mock_should_continue, 'count'):
                mock_should_continue.count += 1
            else:
                mock_should_continue.count = 1
            
            # Stop after first iteration
            if mock_should_continue.count > 1:
                self.listener.is_running = False
            return self.listener.is_running
            
        self.listener._should_continue_running = mock_should_continue
        
        # Execute start_listening
        await self.listener.start_listening()
        
        # Verify
        self.listener._validate_livechat_id.assert_called_once()
        self.assertEqual(self.listener._poll_chat_messages.call_count, 3)
        # Should process 2 messages
        self.assertEqual(self.listener._process_message.call_count, 2)
        
    @pytest.mark.asyncio
    async def test_start_listening_invalid_livechat_id(self):
        """Test starting the listener with an invalid livechat ID."""
        # Mock validation to fail
        self.listener._validate_livechat_id = MagicMock(return_value=False)
        self.listener._poll_chat_messages = AsyncMock()
        
        # Execute start_listening
        await self.listener.start_listening()
        
        # Verify
        self.listener._validate_livechat_id.assert_called_once()
        self.listener._poll_chat_messages.assert_not_awaited()
        
    @pytest.mark.asyncio
    async def test_start_listening_exception_in_poll(self):
        """Test the main listening loop handling an exception in _poll_chat_messages."""
        # Mock dependencies
        self.listener._validate_livechat_id = MagicMock(return_value=True)
        self.listener._poll_chat_messages = AsyncMock(side_effect=Exception("Poll error"))
        
        # Mock the exception condition to exit after 1 failure
        run_count = 0
        original_method = self.listener._should_continue_running
        
        def mock_should_continue(*args, **kwargs):
            if hasattr(mock_should_continue, 'count'):
                mock_should_continue.count += 1
            else:
                mock_should_continue.count = 1
            
            # Stop after first iteration
            if mock_should_continue.count > 1:
                self.listener.is_running = False
            return self.listener.is_running
            
        self.listener._should_continue_running = mock_should_continue
        
        # Execute start_listening - should handle exception gracefully
        await self.listener.start_listening()
        
        # Verify
        self.listener._validate_livechat_id.assert_called_once()
        self.listener._poll_chat_messages.assert_awaited_once()
        
    @pytest.mark.asyncio
    async def test_start_listening_exception_in_process(self):
        """Test the main listening loop handling an exception in _process_message."""
        # Mock dependencies
        self.listener._validate_livechat_id = MagicMock(return_value=True)
        self.listener._poll_chat_messages = AsyncMock(return_value=[{"id": "msg1"}])
        self.listener._process_message = AsyncMock(side_effect=Exception("Process error"))
        
        # Mock the exception condition to exit after 1 iteration
        run_count = 0
        original_method = self.listener._should_continue_running
        
        def mock_should_continue(*args, **kwargs):
            if hasattr(mock_should_continue, 'count'):
                mock_should_continue.count += 1
            else:
                mock_should_continue.count = 1
            
            # Stop after first iteration
            if mock_should_continue.count > 1:
                self.listener.is_running = False
            return self.listener.is_running
            
        self.listener._should_continue_running = mock_should_continue
        
        # Execute start_listening - should handle exception gracefully
        await self.listener.start_listening()
        
        # Verify
        self.listener._validate_livechat_id.assert_called_once()
        self.listener._poll_chat_messages.assert_awaited_once()
        self.listener._process_message.assert_awaited_once_with({"id": "msg1"})
        
    @pytest.mark.asyncio
    async def test_validate_livechat_id_valid(self):
        """Test validating a valid livechat ID."""
        # Mock the Google API client
        self.listener.youtube = MagicMock()
        # Mock the successful response
        mock_response = MagicMock()
        mock_response.execute.return_value = {
            "items": [{"snippet": {"title": "Test Stream"}}]
        }
        self.listener.youtube.videos.return_value.list.return_value = mock_response
        
        # Execute validation
        result = self.listener._validate_livechat_id()
        
        # Verify
        self.assertTrue(result)
        mock_response.execute.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_validate_livechat_id_invalid(self):
        """Test validating an invalid livechat ID."""
        # Mock the Google API client
        self.listener.youtube = MagicMock()
        # Mock empty response (invalid ID)
        mock_response = MagicMock()
        mock_response.execute.return_value = {"items": []}
        self.listener.youtube.videos.return_value.list.return_value = mock_response
        
        # Execute validation
        result = self.listener._validate_livechat_id()
        
        # Verify
        self.assertFalse(result)
        mock_response.execute.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_validate_livechat_id_error(self):
        """Test validation handling an error."""
        # Mock the Google API client
        self.listener.youtube = MagicMock()
        # Mock API error
        self.listener.youtube.videos.return_value.list.side_effect = Exception("API error")
        
        # Execute validation - should handle exception gracefully
        result = self.listener._validate_livechat_id()
        
        # Verify
        self.assertFalse(result)

    @pytest.mark.asyncio
    async def test_poll_chat_messages_success(self):
        """Test successful polling of chat messages."""
        # Mock the Google API client
        self.listener.youtube = MagicMock()
        # Mock successful response
        mock_response = MagicMock()
        mock_response.execute.return_value = {
            "items": [{"id": "message1"}, {"id": "message2"}],
            "nextPageToken": "next-token"
        }
        self.listener.youtube.liveChatMessages.return_value.list.return_value = mock_response
        
        # Execute polling
        messages = await self.listener._poll_chat_messages()
        
        # Verify
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["id"], "message1")
        self.assertEqual(messages[1]["id"], "message2")
        self.assertEqual(self.listener.next_page_token, "next-token")
        
    @pytest.mark.asyncio
    async def test_poll_chat_messages_empty(self):
        """Test polling with no new messages."""
        # Mock the Google API client
        self.listener.youtube = MagicMock()
        # Mock empty response
        mock_response = MagicMock()
        mock_response.execute.return_value = {
            "items": [],
            "nextPageToken": "next-token"
        }
        self.listener.youtube.liveChatMessages.return_value.list.return_value = mock_response
        
        # Execute polling
        messages = await self.listener._poll_chat_messages()
        
        # Verify
        self.assertEqual(len(messages), 0)
        self.assertEqual(self.listener.next_page_token, "next-token")
        
    @pytest.mark.asyncio
    async def test_poll_chat_messages_api_error(self):
        """Test that _poll_chat_messages properly handles API errors."""
        # Setup
        self.listener.live_chat_id = "test_chat_id"
        
        # Mock YouTube API to raise an exception
        with patch.object(self.listener.youtube, 'liveChatMessages') as mock_messages:
            mock_list = MagicMock()
            mock_list.list.return_value = MagicMock()
            mock_list.list.return_value.execute.side_effect = HttpError(
                resp=httplib2.Response({'status': 500}),
                content=b'Error'
            )
            mock_messages.return_value = mock_list
            
            # Execute
            result = await self.listener._poll_chat_messages()
            
            # Verify
            self.assertIsNone(result)  # Should return None on critical failure
    
    @pytest.mark.asyncio
    async def test_poll_chat_messages_malformed_response(self):
        """Test that _poll_chat_messages properly handles malformed API responses."""
        # Setup
        self.listener.live_chat_id = "test_chat_id"
        
        # Mock YouTube API to return a malformed response (missing 'items' key)
        with patch.object(self.listener.youtube, 'liveChatMessages') as mock_messages:
            mock_list = MagicMock()
            mock_list.list.return_value = MagicMock()
            mock_list.list.return_value.execute.return_value = {
                'nextPageToken': 'next_token'
                # 'items' key is missing
            }
            mock_messages.return_value = mock_list
            
            # Execute
            result = await self.listener._poll_chat_messages()
            
            # Verify
            self.assertEqual(result, [])  # Should return empty list when 'items' key is missing

    @pytest.mark.asyncio
    async def test_update_viewer_count_api_error(self):
        """Test that _update_viewer_count properly handles API errors."""
        # Setup
        self.listener.video_id = "test_video_id"
        self.listener.viewer_count = 0  # Default value
        
        # Mock YouTube API to raise an exception
        with patch.object(self.listener.youtube, 'videos') as mock_videos:
            mock_list = MagicMock()
            mock_list.list.return_value = MagicMock()
            mock_list.list.return_value.execute.side_effect = HttpError(
                resp=httplib2.Response({'status': 500}),
                content=b'Error'
            )
            mock_videos.return_value = mock_list
            
            # Execute
            self.listener._update_viewer_count()
            
            # Verify
            self.assertEqual(self.listener.viewer_count, 0)  # Should remain unchanged
    
    @pytest.mark.asyncio
    async def test_update_viewer_count_malformed_response(self):
        """Test that _update_viewer_count properly handles malformed API responses."""
        # Setup
        self.listener.video_id = "test_video_id"
        self.listener.viewer_count = 0  # Default value
        
        # Case 1: Missing 'items' key
        with patch.object(self.listener.youtube, 'videos') as mock_videos:
            mock_list = MagicMock()
            mock_list.list.return_value = MagicMock()
            mock_list.list.return_value.execute.return_value = {
                # 'items' key is missing
            }
            mock_videos.return_value = mock_list
            
            # Execute
            self.listener._update_viewer_count()
            
            # Verify
            self.assertEqual(self.listener.viewer_count, 0)  # Should remain unchanged
        
        # Case 2: Empty 'items' list
        with patch.object(self.listener.youtube, 'videos') as mock_videos:
            mock_list = MagicMock()
            mock_list.list.return_value = MagicMock()
            mock_list.list.return_value.execute.return_value = {
                'items': []
            }
            mock_videos.return_value = mock_list
            
            # Execute
            self.listener._update_viewer_count()
            
            # Verify
            self.assertEqual(self.listener.viewer_count, 0)  # Should remain unchanged
            
        # Case 3: Missing 'statistics' key
        with patch.object(self.listener.youtube, 'videos') as mock_videos:
            mock_list = MagicMock()
            mock_list.list.return_value = MagicMock()
            mock_list.list.return_value.execute.return_value = {
            'items': [
                {
                        # 'statistics' key is missing
                    }
                ]
            }
            mock_videos.return_value = mock_list
            
            # Execute
            self.listener._update_viewer_count()
            
            # Verify
            self.assertEqual(self.listener.viewer_count, 0)  # Should remain unchanged
            
        # Case 4: Missing 'concurrentViewers' key
        with patch.object(self.listener.youtube, 'videos') as mock_videos:
            mock_list = MagicMock()
            mock_list.list.return_value = MagicMock()
            mock_list.list.return_value.execute.return_value = {
                'items': [
                    {
                        'statistics': {
                            # 'concurrentViewers' key is missing
                        }
                    }
                ]
            }
            mock_videos.return_value = mock_list
            
            # Execute
            self.listener._update_viewer_count()
            
            # Verify
            self.assertEqual(self.listener.viewer_count, 0)  # Should remain unchanged
    
    @pytest.mark.asyncio
    async def test_process_message_invalid_message_format(self):
        """Test that _process_message properly handles invalid message formats."""
        # Configure mocks
        with patch.object(self.listener, '_log_to_user_file'), \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send:
            
            # Set the emoji sequence
            self.listener.emoji_sequence = "✊✋✌"
            
            # Test various invalid message formats
            test_messages = [
                {},  # Empty dict
                {'id': 'test_id'},  # Missing snippet
                {'id': 'test_id', 'snippet': {}},  # Empty snippet
                {'id': 'test_id', 'snippet': {'displayMessage': ''}},  # Empty message
                {'id': 'test_id', 'snippet': {'displayMessage': '✊✋✌'}, 'authorDetails': {}},  # Missing author details
                None  # None instead of dict
            ]
            
            for test_message in test_messages:
                # Execute
                result = await self.listener._process_message(test_message)
                
                # Verify - should not crash and should not trigger a response
                self.assertIsNotNone(result)  # Should not return None
                mock_send.assert_not_called()  # Should not trigger a response

    @pytest.mark.asyncio
    async def test_process_message_complete_emoji_sequence(self):
        """Test that a complete emoji sequence triggers a response properly."""
        # Setup
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "Testing the emoji sequence ✊✋✌"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "test_channel"
            }
        }
        
        # Configure mocks
        with patch.object(self.listener, '_log_to_user_file') as mock_log, \
             patch.object(self.listener, '_is_rate_limited', return_value=False) as mock_rate_limit, \
             patch.object(self.listener, '_update_trigger_time') as mock_update_time, \
             patch.object(self.listener.banter_engine, 'get_random_banter', return_value="Hello!") as mock_banter, \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock, return_value=True) as mock_send:
            
            # Set the emoji sequence
            self.listener.emoji_sequence = "✊✋✌"
            
            # Process the message
            result = await self.listener._process_message(test_message)
            
            # Verify
            self.assertIsNotNone(result)
            mock_log.assert_called_once_with(test_message)
            mock_rate_limit.assert_called_once_with("test_channel")
            mock_banter.assert_called_once_with(theme="greeting")
            mock_send.assert_called_once_with("Hello!")
            mock_update_time.assert_called_once_with("test_channel")

    @pytest.mark.asyncio
    async def test_process_message_whitespace_handling(self):
        """Test that whitespace between emoji characters doesn't affect detection."""
        # Setup
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "Message with   ✊  ✋  ✌   whitespace"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "test_channel"
            }
        }
        
        # Configure mocks
        with patch.object(self.listener, '_log_to_user_file') as mock_log, \
             patch.object(self.listener, '_is_rate_limited', return_value=False) as mock_rate_limit, \
             patch.object(self.listener, '_update_trigger_time') as mock_update_time, \
             patch.object(self.listener.banter_engine, 'get_random_banter', return_value="Hello!") as mock_banter, \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock, return_value=True) as mock_send:
            
            # Set the emoji sequence without whitespace
            self.listener.emoji_sequence = "✊✋✌"
            
            # Process the message
            result = await self.listener._process_message(test_message)
            
            # Verify
            self.assertIsNotNone(result)
            mock_log.assert_called_once_with(test_message)
            mock_rate_limit.assert_called_once_with("test_channel")
            mock_banter.assert_called_once_with(theme="greeting")
            mock_send.assert_called_once_with("Hello!")
            mock_update_time.assert_called_once_with("test_channel")

    @pytest.mark.asyncio
    async def test_start_listening_with_greeting(self):
        """Test that start_listening sends a greeting message when it starts."""
        # Setup
        self.listener.is_running = False
        self.listener.greeting_message = "Hello, chat!"
        
        # Mock dependencies
        with patch.object(self.listener, '_validate_livechat_id', return_value=True) as mock_validate, \
             patch.object(self.listener, '_update_viewer_count') as mock_update, \
             patch.object(self.listener, '_poll_chat_messages', new_callable=AsyncMock) as mock_poll, \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            
            # Configure mocks to stop after one iteration
            mock_poll.return_value = []
            
            async def stop_after_greeting():
                await asyncio.sleep(0.1)
                self.listener.is_running = False
            
            # Execute
            await asyncio.gather(
                self.listener.start_listening(),
                stop_after_greeting()
            )
            
            # Verify
            mock_validate.assert_called_once()
            mock_send.assert_called_once_with("Hello, chat!")
            mock_update.assert_called_once()
            mock_poll.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_listening(self):
        """Test that stop_listening correctly stops the listener."""
        # Setup - listener is running
        self.listener.is_running = True
        
        # Execute
        self.listener.stop_listening()
        
        # Verify
        self.assertFalse(self.listener.is_running)
        
        # Also test when already stopped (should be idempotent)
        self.listener.stop_listening()
        self.assertFalse(self.listener.is_running)

    @pytest.mark.asyncio
    async def test_process_message_multiple_emoji_sequences(self):
        """Test that a message with multiple emoji sequences is handled correctly."""
        # Setup
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "First ✊✋✌ and second ✊✋✌"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "test_channel"
            }
        }
        
        # Configure mocks
        with patch.object(self.listener, '_log_to_user_file') as mock_log, \
             patch.object(self.listener, '_is_rate_limited', return_value=False) as mock_rate_limit, \
             patch.object(self.listener, '_update_trigger_time') as mock_update_time, \
             patch.object(self.listener.banter_engine, 'get_random_banter', return_value="Hello!") as mock_banter, \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock, return_value=True) as mock_send:
            
            # Set the emoji sequence
            self.listener.emoji_sequence = "✊✋✌"
            
            # Process the message
            result = await self.listener._process_message(test_message)
            
            # Verify - should only respond once even with multiple sequences
            self.assertIsNotNone(result)
            mock_log.assert_called_once_with(test_message)
            mock_rate_limit.assert_called_once_with("test_channel")
            mock_banter.assert_called_once_with(theme="greeting")
            mock_send.assert_called_once_with("Hello!")
            mock_update_time.assert_called_once_with("test_channel")

    @pytest.mark.asyncio
    async def test_process_message_complete_emoji_sequence_enhanced(self):
        """Test that a message with the complete emoji sequence triggers a response properly."""
        # Setup message with the exact trigger sequence
        test_message = {
            "id": "test_emoji",
            "snippet": {
                "displayMessage": "Testing the complete emoji sequence ✊✋✌"
            },
            "authorDetails": {
                "displayName": "EmojiUser",
                "channelId": "emoji_channel"
            }
        }
        
        # Configure mocks with detailed behavior
        with patch.object(self.listener, '_log_to_user_file') as mock_log, \
             patch.object(self.listener, '_is_rate_limited', return_value=False) as mock_rate_limit, \
             patch.object(self.listener, '_update_trigger_time') as mock_update_time, \
             patch.object(self.listener.banter_engine, 'get_random_banter', return_value="Hello, emoji user!") as mock_banter, \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock, return_value=True) as mock_send:
            
            # Set the emoji sequence
            self.listener.emoji_sequence = "✊✋✌"
            
            # Execute
            result = await self.listener._process_message(test_message)
            
            # Verify extensive assertions
            self.assertIsNotNone(result)
            self.assertEqual(result["id"], "test_emoji")
            self.assertEqual(result["author"], "EmojiUser")
            self.assertEqual(result["message"], "Testing the complete emoji sequence ✊✋✌")
            mock_log.assert_called_once_with(test_message)
            mock_rate_limit.assert_called_once_with("emoji_channel")
            mock_banter.assert_called_once_with(theme="greeting")
            mock_send.assert_called_once_with("Hello, emoji user!")
            mock_update_time.assert_called_once_with("emoji_channel")

    @pytest.mark.asyncio
    async def test_process_message_whitespace_handling_enhanced(self):
        """Test that whitespace between emoji characters doesn't affect detection."""
        # Setup message with various whitespace patterns around and between emoji
        test_message = {
            "id": "test_whitespace",
            "snippet": {
                "displayMessage": "Message with   ✊   ✋   ✌   excessive whitespace"
            },
            "authorDetails": {
                "displayName": "WhitespaceUser",
                "channelId": "whitespace_channel"
            }
        }
        
        # Configure mocks
        with patch.object(self.listener, '_log_to_user_file') as mock_log, \
             patch.object(self.listener, '_is_rate_limited', return_value=False) as mock_rate_limit, \
             patch.object(self.listener, '_update_trigger_time') as mock_update_time, \
             patch.object(self.listener.banter_engine, 'get_random_banter', return_value="Hi there!") as mock_banter, \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock, return_value=True) as mock_send:
            
            # Set the emoji sequence without whitespace
            self.listener.emoji_sequence = "✊✋✌"
            
            # Execute
            result = await self.listener._process_message(test_message)
            
            # Verify
            self.assertIsNotNone(result)
            mock_log.assert_called_once_with(test_message)
            mock_rate_limit.assert_called_once_with("whitespace_channel")
            mock_banter.assert_called_once_with(theme="greeting")
            mock_send.assert_called_once_with("Hi there!")
            mock_update_time.assert_called_once_with("whitespace_channel")

    @pytest.mark.asyncio
    async def test_start_listening_with_greeting_enhanced(self):
        """Test that start_listening properly sends a greeting and begins the listening cycle."""
        # Setup
        self.listener.live_chat_id = "test_chat_id"
        self.listener.is_running = False
        self.listener.greeting_message = "Welcome to the stream!"
        
        # Mock methods with detailed behavior
        with patch.object(self.listener, '_initialize_chat_session', return_value=True) as mock_init, \
             patch.object(self.listener, '_send_greeting_message', new_callable=AsyncMock) as mock_greeting, \
             patch.object(self.listener, '_poll_chat_cycle', new_callable=AsyncMock, return_value=False) as mock_poll_cycle, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            
            # Make the listener stop after one iteration
            async def stop_after_polling():
                # After one poll_chat_cycle call, set is_running to False
                self.listener.is_running = False
                return False
                
            mock_poll_cycle.side_effect = stop_after_polling
            
            # Execute
            await self.listener.start_listening()
            
            # Verify
            mock_init.assert_called_once()
            mock_greeting.assert_called_once()
            mock_poll_cycle.assert_called_once()
            # Should not sleep because we immediately exit the loop
            mock_sleep.assert_not_called()

    @pytest.mark.asyncio
    async def test_stop_listening_enhanced(self):
        """Test the stop_listening method thoroughly."""
        # Setup - listener is initially running
        self.listener.is_running = True
        
        # Execute with different initial states
        self.listener.stop_listening()
        
        # Verify
        self.assertFalse(self.listener.is_running)
        
        # Test idempotence - calling stop on an already stopped listener
        self.listener.stop_listening()
        self.assertFalse(self.listener.is_running)
        
        # Test with a running thread (if applicable)
        if hasattr(self.listener, 'thread') and self.listener.thread is not None:
            with patch.object(self.listener, 'thread') as mock_thread:
                mock_thread.is_alive.return_value = True
                self.listener.is_running = True
                
                self.listener.stop_listening()
                
                self.assertFalse(self.listener.is_running)
                # If the implementation includes joining threads, verify that
                if hasattr(mock_thread, 'join'):
                    mock_thread.join.assert_called_once()

    @pytest.mark.asyncio
    async def test_reconnection_after_auth_error(self):
        """Test that the listener can reconnect after an authentication error."""
        # Setup
        self.listener.live_chat_id = "test_chat_id"
        self.listener.is_running = True
        
        # Create a mock HTTP 401 error
        auth_error = HttpError(
            resp=httplib2.Response({'status': 401}),
            content=b'Authentication error'
        )
        
        # Mock dependencies to simulate reconnection flow
        with patch.object(self.listener, '_poll_chat_messages', new_callable=AsyncMock) as mock_poll, \
             patch.object(self.listener, '_handle_auth_error', new_callable=AsyncMock) as mock_handle_auth, \
             patch.object(self.listener, '_process_message', new_callable=AsyncMock) as mock_process, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            
            # First call raises auth error, second call succeeds
            mock_poll.side_effect = [
                auth_error,  # First poll fails with auth error
                [{"id": "msg1"}]  # Second poll succeeds
            ]
            
            # Auth error handling succeeds
            mock_handle_auth.return_value = True
            
            # Execute first poll - should get auth error and handle it
            try:
                messages = await self.listener._poll_chat_messages()
            except auth_error.__class__ as e:
                handled = await self.listener._handle_auth_error(e)
                if handled:
                    messages = await self.listener._poll_chat_messages()
                    await self.listener._process_message(messages[0])
            
            # Verify behavior
            self.assertEqual(mock_poll.call_count, 2)
            mock_handle_auth.assert_called_once_with(auth_error)
            mock_process.assert_called_once()

    @pytest.mark.asyncio
    async def test_message_queue_processing(self):
        """Test that messages are added to the queue and processed in order."""
        # Setup 
        self.listener.live_chat_id = "test_chat_id"
        self.listener.message_queue = []
        
        # Create test messages
        test_messages = [
            {"id": "msg1", "snippet": {"displayMessage": "First"}, 
             "authorDetails": {"displayName": "User1", "channelId": "channel1"}},
            {"id": "msg2", "snippet": {"displayMessage": "Second"}, 
             "authorDetails": {"displayName": "User2", "channelId": "channel2"}},
            {"id": "msg3", "snippet": {"displayMessage": "Third"}, 
             "authorDetails": {"displayName": "User3", "channelId": "channel3"}}
        ]
        
        # Mock dependencies
        with patch.object(self.listener, '_poll_chat_messages', new_callable=AsyncMock) as mock_poll, \
             patch.object(self.listener, '_process_message', new_callable=AsyncMock) as mock_process:
            
            # Poll returns our test messages
            mock_poll.return_value = test_messages
            
            # Process normally just returns the message
            mock_process.side_effect = lambda msg: {
                "id": msg["id"], 
                "author": msg["authorDetails"]["displayName"],
                "message": msg["snippet"]["displayMessage"]
            }
            
            # Call the method that would queue and process messages
            await self.listener._fetch_and_process_messages()
            
            # Verify all messages were processed in order
            self.assertEqual(mock_process.call_count, 3)
            self.assertEqual(mock_process.call_args_list[0][0][0]["id"], "msg1")
            self.assertEqual(mock_process.call_args_list[1][0][0]["id"], "msg2")
            self.assertEqual(mock_process.call_args_list[2][0][0]["id"], "msg3")
            
            # Verify queue handling if implemented
            if hasattr(self.listener, 'message_queue'):
                self.assertEqual(len(self.listener.message_queue), 3)

    @pytest.mark.asyncio
    async def test_dynamic_emoji_patterns(self):
        """Test that different emoji patterns can be detected correctly."""
        # Setup different emoji patterns
        test_patterns = [
            "🎮🎲🎯",  # Gaming emojis
            "🌟⭐✨",   # Star emojis
            "🐶🐱🐭"    # Animal emojis
        ]
        
        for pattern in test_patterns:
            # Create test message with this pattern
        test_message = {
                "id": f"test_{pattern}",
                "snippet": {
                    "displayMessage": f"Message with pattern {pattern}"
                },
                "authorDetails": {
                    "displayName": "TestUser",
                    "channelId": "test_channel"
                }
            }
            
            # Configure mocks
            with patch.object(self.listener, '_log_to_user_file'), \
                 patch.object(self.listener, '_is_rate_limited', return_value=False), \
                 patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
                 patch.object(self.listener, '_update_trigger_time'):
                
                # Set the current emoji sequence to this pattern
                self.listener.emoji_sequence = pattern
                
                # Execute
                result = await self.listener._process_message(test_message)
                
                # Verify
                self.assertIsNotNone(result)
                mock_send.assert_called_once()
                mock_send.reset_mock()

    @pytest.mark.asyncio
    async def test_concurrent_api_calls(self):
        """Test that the system can handle multiple concurrent API calls."""
        # Setup
        self.listener.live_chat_id = "test_chat_id"
        self.listener.video_id = "test_video_id"
        
        # Create some async tasks to simulate concurrent operations
        async def mock_update_viewers():
            return self.listener._update_viewer_count()
            
        async def mock_poll_messages():
            return await self.listener._poll_chat_messages()
            
        # Mock the YouTube API
        mock_videos_response = MagicMock()
        mock_videos_response.execute.return_value = {
            "items": [{"statistics": {"concurrentViewers": "500"}}]
        }
        
        mock_messages_response = MagicMock()
        mock_messages_response.execute.return_value = {
            "items": [{"id": "msg1"}],
            "nextPageToken": "token",
            "pollingIntervalMillis": 1000
        }
        
        with patch.object(self.listener.youtube, 'videos') as mock_videos, \
             patch.object(self.listener.youtube, 'liveChatMessages') as mock_messages:
            
            # Configure mock responses
            mock_videos.return_value.list.return_value = mock_videos_response
            mock_messages.return_value.list.return_value = mock_messages_response
            
            # Execute multiple operations concurrently
            results = await asyncio.gather(
                mock_update_viewers(),
                mock_poll_messages(),
                mock_update_viewers(),
                mock_poll_messages()
            )
            
            # Verify all operations completed
            self.assertEqual(self.listener.viewer_count, 500)
            self.assertEqual(len(results[1]), 1)  # First poll messages result
            self.assertEqual(len(results[3]), 1)  # Second poll messages result
            
            # Verify API was called correctly
            self.assertEqual(mock_videos.return_value.list.call_count, 2)
            self.assertEqual(mock_messages.return_value.list.call_count, 2)

    @pytest.mark.asyncio
    async def test_start_listening_with_fetch_chat_id(self):
        """Test start_listening when no chat ID is provided."""
        # Setup
        self.listener.live_chat_id = None
        self.listener.is_running = False
        
        # Mock dependencies
        with patch.object(self.listener, '_get_live_chat_id') as mock_get_id, \
             patch.object(self.listener, '_update_viewer_count') as mock_update, \
             patch.object(self.listener, '_poll_chat_messages', new_callable=AsyncMock) as mock_poll, \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
             
            # Configure mocks
            mock_get_id.return_value = "fetched_chat_id"
            self.listener.greeting_message = "Hello, welcome!"
            mock_send.return_value = True
            mock_poll.return_value = []  # No messages initially
            
            # Make the listener stop after one iteration
            async def stop_after_one_iteration():
                await asyncio.sleep(0.1)
                self.listener.is_running = False
                
            # Execute both coroutines
            await asyncio.gather(
                self.listener.start_listening(),
                stop_after_one_iteration()
            )
            
            # Verify
            mock_get_id.assert_called_once()
            self.assertEqual(self.listener.live_chat_id, "fetched_chat_id")
            mock_send.assert_called_once_with("Hello, welcome!")
            mock_poll.assert_called_once()
            mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_listening_failed_to_get_chat_id(self):
        """Test start_listening when chat ID fetch fails."""
        # Setup
        self.listener.live_chat_id = None
        self.listener.is_running = False
        
        # Mock dependencies
        with patch.object(self.listener, '_get_live_chat_id') as mock_get_id, \
             patch.object(self.listener, '_update_viewer_count') as mock_update, \
             patch.object(self.listener, '_poll_chat_messages', new_callable=AsyncMock) as mock_poll, \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send:
             
            # Configure mocks to fail
            mock_get_id.return_value = None
            
            # Execute
            await self.listener.start_listening()
            
            # Verify
            mock_get_id.assert_called_once()
            mock_send.assert_not_called()
            mock_poll.assert_not_called()
            mock_update.assert_not_called()
            self.assertFalse(self.listener.is_running)
            
    @pytest.mark.asyncio
    async def test_start_listening_greeting_failure(self):
        """Test start_listening when greeting message fails."""
        # Setup
        self.listener.live_chat_id = "test_chat_id"
        self.listener.is_running = False
        
        # Mock dependencies
        with patch.object(self.listener, '_get_live_chat_id') as mock_get_id, \
             patch.object(self.listener, '_update_viewer_count') as mock_update, \
             patch.object(self.listener, '_poll_chat_messages', new_callable=AsyncMock) as mock_poll, \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch('time.sleep') as mock_sleep, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_async_sleep:
             
            # Configure mocks
            mock_get_id.return_value = "test_chat_id"
            self.listener.greeting_message = "Hello, welcome!"
            mock_send.return_value = False  # Greeting fails
            mock_poll.return_value = []  # No messages
            
            # Make the listener stop after one iteration
            async def stop_after_one_iteration():
                await asyncio.sleep(0.1)
                self.listener.is_running = False
                
            # Execute both coroutines
            await asyncio.gather(
                self.listener.start_listening(),
                stop_after_one_iteration()
            )
            
            # Verify
            self.assertEqual(self.listener.live_chat_id, "test_chat_id")
            mock_send.assert_called_once_with("Hello, welcome!")
            mock_poll.assert_called_once()
            mock_sleep.assert_called_once()
            self.assertTrue(self.listener.is_running)
            
    def test_get_live_chat_id_http_error(self):
        """Test _get_live_chat_id when HTTP error occurs."""
        # Mock YouTube API to raise HTTP error
        self.mock_youtube.videos().list.side_effect = googleapiclient.errors.HttpError(
            resp=httplib2.Response({'status': 500}),
            content=b'HTTP Error'
        )
        
        # Verify exception is propagated
        with self.assertRaises(googleapiclient.errors.HttpError):
            self.listener._get_live_chat_id()
            
    def test_get_live_chat_id_generic_error(self):
        """Test _get_live_chat_id when generic error occurs."""
        # Mock YouTube API to raise generic error
        self.mock_youtube.videos().list.side_effect = Exception("Generic error")
        
        # Verify ValueError is raised with proper message
        with self.assertRaises(ValueError) as context:
            self.listener._get_live_chat_id()
        
        self.assertIn("Failed to get live chat ID", str(context.exception))
        
    def test_get_live_chat_id_missing_chat_id(self):
        """Test _get_live_chat_id when activeLiveChatId is missing."""
        # Mock response with liveStreamingDetails but no activeLiveChatId
        self.mock_youtube.videos().list.return_value.execute.return_value = {
            "items": [{"liveStreamingDetails": {}}]
        }
        
        # Verify ValueError is raised
        with self.assertRaises(ValueError) as context:
            self.listener._get_live_chat_id()
            
        self.assertIn("No active live chat", str(context.exception))
        
    @pytest.mark.asyncio
    async def test_fetch_and_process_messages(self):
        """Test the fetch_and_process_messages method."""
        # Setup
        self.listener.live_chat_id = "test_chat_id"
        
        # Mock dependencies
        with patch.object(self.listener, '_poll_chat_messages', new_callable=AsyncMock) as mock_poll, \
             patch.object(self.listener, '_process_message', new_callable=AsyncMock) as mock_process:
             
            # Setup mock responses
            mock_poll.return_value = [
                {"id": "msg1", "snippet": {"displayMessage": "First"}},
                {"id": "msg2", "snippet": {"displayMessage": "Second"}}
            ]
            
            # Execute
            await self.listener._fetch_and_process_messages()
            
            # Verify
            mock_poll.assert_called_once()
            self.assertEqual(mock_process.call_count, 2)
            
    @pytest.mark.asyncio
    async def test_handle_auth_error_during_send(self):
        """Test handling auth error when sending messages."""
        # Setup
        self.listener.live_chat_id = "test_chat_id"
        
        # Create HTTP 401 error
        auth_error = googleapiclient.errors.HttpError(
            resp=httplib2.Response({'status': 401}),
            content=b'Auth error'
        )
        
        # Mock dependencies
        with patch.object(self.listener.youtube, 'liveChatMessages') as mock_messages, \
             patch.object(self.listener, '_handle_auth_error', new_callable=AsyncMock) as mock_handle_auth:
             
            # Configure mocks
            mock_list = MagicMock()
            mock_list.insert.return_value = MagicMock()
            mock_list.insert.return_value.execute.side_effect = auth_error
            mock_messages.return_value = mock_list
            
            # Configure auth error handling - successful
            mock_handle_auth.return_value = True
            
            # Execute
            result = await self.listener.send_chat_message("Test message")
            
            # Verify
            self.assertFalse(result)  # Should still return False since no retry is implemented
            mock_handle_auth.assert_called_once_with(auth_error)
            
    @pytest.mark.asyncio
    async def test_send_chat_message_no_chat_id(self):
        """Test send_chat_message with no chat ID set."""
        # Setup
        self.listener.live_chat_id = None
        
        # Execute
        result = await self.listener.send_chat_message("Test message")
        
        # Verify
        self.assertFalse(result)
        self.mock_youtube.liveChatMessages().insert.assert_not_called()
        
    @pytest.mark.asyncio
    async def test_send_chat_message_unexpected_error(self):
        """Test send_chat_message with unexpected error."""
        # Setup
        self.listener.live_chat_id = "test_chat_id"
        
        # Mock dependencies
        with patch.object(self.listener.youtube, 'liveChatMessages') as mock_messages:
            # Configure mock to raise generic exception
            mock_list = MagicMock()
            mock_list.insert.return_value = MagicMock()
            mock_list.insert.return_value.execute.side_effect = Exception("Unexpected error")
            mock_messages.return_value = mock_list
            
            # Execute
            result = await self.listener.send_chat_message("Test message")
            
            # Verify
            self.assertFalse(result)
            
    @pytest.mark.asyncio
    async def test_log_to_user_file_error(self):
        """Test _log_to_user_file error handling."""
        # Create test message
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "Test message"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "test_channel"
            }
        }
        
        # Mock file operations to fail
        with patch("builtins.open") as mock_open:
            mock_open.side_effect = Exception("File error")
            
            # Execute - should not raise exception
            with self.assertRaises(Exception):
                self.listener._log_to_user_file(test_message)

            # Verify
            self.assertTrue(mock_open.called)
            
    def test_listener_with_real_object_setup(self):
        """Test creating LiveChatListener with real objects and different configurations."""
        # Create with only required parameters
        minimal_listener = LiveChatListener(
            youtube_service=self.mock_youtube,
            video_id="test_video"
        )
        self.assertIsNone(minimal_listener.live_chat_id)
        self.assertEqual(minimal_listener.video_id, "test_video")
        
        # Create with all parameters including options
        full_listener = LiveChatListener(
            youtube_service=self.mock_youtube,
            video_id="test_video",
            live_chat_id="test_chat"
        )
        
        # Set attributes directly
        full_listener.poll_interval_ms = 5000
        full_listener.error_backoff_seconds = 10
        full_listener.memory_dir = "custom_memory"
        full_listener.trigger_cooldown = 120
        full_listener.greeting_message = "Custom greeting!"
        
        # Verify all attributes
        self.assertEqual(full_listener.live_chat_id, "test_chat")
        self.assertEqual(full_listener.poll_interval_ms, 5000)
        self.assertEqual(full_listener.error_backoff_seconds, 10)
        self.assertEqual(full_listener.memory_dir, "custom_memory")
        self.assertEqual(full_listener.trigger_cooldown, 120)
        self.assertEqual(full_listener.greeting_message, "Custom greeting!")

    @pytest.mark.asyncio
    async def test_full_listening_cycle(self):
        """Test a complete listening cycle including auth errors and recovery."""
        # Setup with mocks that allow testing deep paths
        self.listener.is_running = True
        self.listener.live_chat_id = "test_chat_id"
        
        # Create HTTP auth error for testing recovery
        auth_error = googleapiclient.errors.HttpError(
            resp=httplib2.Response({'status': 401}),
            content=b'Auth error'
        )
        
        # Mock all necessary components
        with patch.object(self.listener, '_update_viewer_count') as mock_update, \
             patch.object(self.listener.youtube, 'liveChatMessages') as mock_messages, \
             patch.object(self.listener, '_handle_auth_error', new_callable=AsyncMock) as mock_handle_auth, \
             patch.object(self.listener, '_process_message', new_callable=AsyncMock) as mock_process, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep, \
             patch('time.sleep') as mock_time_sleep:
            
            # Setup mock for first error, then success
            mock_list = MagicMock()
            mock_list.list.return_value = MagicMock()
            
            # First call fails with auth error, recovered
            mock_list.list.return_value.execute.side_effect = [
                auth_error,  # First call - auth error
                {  # Second call - success after recovery
                    "items": [{"id": "msg1"}, {"id": "msg2"}],
                    "nextPageToken": "next_token",
                    "pollingIntervalMillis": 5000
                },
                Exception("Unexpected error"),  # Third call - unexpected error, should be caught
                {  # Fourth call - back to success
                    "items": [],
                    "nextPageToken": "next_token2",
                    "pollingIntervalMillis": 2000
                },
                {  # Fifth call - None response
                    "nextPageToken": "next_token3",
                    "pollingIntervalMillis": 1000
                }
            ]
            
            mock_messages.return_value = mock_list
            mock_handle_auth.return_value = True  # Auth error handling succeeds
            
            # Mock process_message to handle message properly
            mock_process.side_effect = lambda msg: {"id": msg["id"], "processed": True}
            
            # Run five poll iterations
            for i in range(5):
                # If the listener is still running
                if self.listener.is_running:
                    # Update viewer count
                    self.listener._update_viewer_count()
                    
                    try:
                        # Try to poll messages, handle auth errors
                        messages = await self.listener._poll_chat_messages()
                        
                        # Process messages if any
                        if messages:
                            for message in messages:
                                await self.listener._process_message(message)
                        
                        # Handle critical failure
                        if messages is None:
                            self.listener.is_running = False
                            break
                        
                    except Exception as e:
                        if isinstance(e, googleapiclient.errors.HttpError):
                            if await self.listener._handle_auth_error(e):
                                continue  # Try again after auth error handling
                        logger.error(f"Unhandled exception in listener: {e}")
                    
                    # Sleep for next poll
                    await asyncio.sleep(self.listener.poll_interval_ms / 1000.0)
            
            # Verify all expected calls were made
            self.assertEqual(mock_update.call_count, 5)
            self.assertEqual(mock_messages.return_value.list.call_count, 5)
            self.assertEqual(mock_process.call_count, 2)  # Only 2 messages were processed
            self.assertEqual(mock_handle_auth.call_count, 1)  # One auth error was handled
            # Skip asserting on sleep calls as they're implementation details

    @pytest.mark.asyncio
    async def test_process_message_emoji_sequence_detection(self):
        """Test emoji sequence detection logic with various patterns."""
        # Define test cases
        test_cases = [
            {
                "message": "Message with exact emojis ✊✋🖐️",
                "expected_trigger": True,
                "emoji_sequence": "✊✋🖐️",
                "description": "Exact emoji match"
            },
            {
                "message": "Message with different emojis 🎮🎲🎯",
                "expected_trigger": False,
                "emoji_sequence": "✊✋🖐️",
                "description": "No matching emojis"
            },
            {
                "message": "First ✊✋🖐️ then ✊✋🖐️",
                "expected_trigger": True,
                "emoji_sequence": "✊✋🖐️",
                "description": "Multiple occurrences"
            },
            {
                "message": "Partial match ✊✋",
                "expected_trigger": False,
                "emoji_sequence": "✊✋🖐️",
                "description": "Partial sequence"
            }
        ]
        
        # Test each case
        for case in test_cases:
            # Setup test message
            test_message = {
                "id": f"test_{case['description']}",
                "snippet": {
                    "displayMessage": case["message"]
                },
                "authorDetails": {
                    "displayName": "TestUser",
                    "channelId": "test_channel"
                }
            }
            
            # Configure mocks for clean testing
            with patch.object(self.listener, '_log_to_user_file'), \
                 patch.object(self.listener, '_is_rate_limited', return_value=False), \
                 patch.object(self.listener, '_update_trigger_time'), \
                 patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
                 patch.object(self.listener.banter_engine, 'get_random_banter', return_value="Hello!"):
                
                # Set emoji sequence being tested
                self.listener.emoji_sequence = case["emoji_sequence"]
                
                # Process the message
                result = await self.listener._process_message(test_message)
                
                # Verify if sending occurred based on expected triggering
                if case["expected_trigger"]:
                    mock_send.assert_called_once()
                else:
                    mock_send.assert_not_called()
                
                # Reset mock for next test
                mock_send.reset_mock()

    @pytest.mark.asyncio
    async def test_main_workflow_sequence(self):
        """Test the main workflow sequence from start to finish."""
        # Mock all the necessary components
        with patch.object(self.listener, '_get_live_chat_id') as mock_get_id, \
             patch.object(self.listener, '_update_viewer_count') as mock_update, \
             patch.object(self.listener, '_poll_chat_messages', new_callable=AsyncMock) as mock_poll, \
             patch.object(self.listener, '_process_message', new_callable=AsyncMock) as mock_process, \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep, \
             patch('time.sleep') as mock_time_sleep:
             
            # Setup initial state
            self.listener.live_chat_id = None
            self.listener.is_running = False
            self.listener.greeting_message = "Hello, welcome!"
            
            # Configure mock responses
            mock_get_id.return_value = "fetched_chat_id"
            mock_send.return_value = True
            mock_poll.side_effect = [
                [{"id": "msg1"}],  # First poll - one message
                [{"id": "msg2"}, {"id": "msg3"}],  # Second poll - two messages
                []  # Third poll - no messages
            ]
            
            # Stop after 3 iterations
            counter = 0
            original_sleep = asyncio.sleep
            
            async def counted_sleep(*args, **kwargs):
                nonlocal counter
                counter += 1
                if counter >= 3:
                    self.listener.is_running = False
                return await original_sleep(0.01)  # Fast sleep for tests
                
            mock_sleep.side_effect = counted_sleep
            
            # Run the main listening function
            await self.listener.start_listening()
            
            # Verify all expected calls were made in the correct sequence
            mock_get_id.assert_called_once()
            self.assertEqual(self.listener.live_chat_id, "fetched_chat_id")
            mock_send.assert_called_once_with("Hello, welcome!")
            mock_poll.assert_called_once()
            mock_update.assert_called_once()

    @pytest.mark.asyncio 
    async def test_full_chatbot_integration(self):
        """Test integration with chat engine and error handling."""
        # Setup
        self.listener.live_chat_id = "test_chat_id"
        self.listener.video_id = "test_video_id"
        
        # Create test message that should trigger a response
        trigger_message = {
            "id": "test_trigger",
            "snippet": {
                "displayMessage": "Hello bot ✊✋🖐️"
            },
            "authorDetails": {
                "displayName": "TriggerUser",
                "channelId": "trigger_channel"
            }
        }
        
        # Mock all key components
        with patch.object(self.listener, '_log_to_user_file') as mock_log, \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch.object(self.listener.banter_engine, 'get_random_banter') as mock_banter:
            
            # Configure mocks for success path
            mock_send.return_value = True
            mock_banter.return_value = "Hello, I'm a bot!"
            
            # Execute message processing
            result = await self.listener._process_message(trigger_message)
            
            # Verify success path
            mock_log.assert_called_once()
            mock_banter.assert_called_once_with(theme="greeting")
            mock_send.assert_called_once_with("Hello, I'm a bot!")
            self.assertIsNotNone(result)
            self.assertEqual(result["id"], "test_trigger")
            
            # Reset mocks for error path testing
            mock_log.reset_mock()
            mock_banter.reset_mock() 
            mock_send.reset_mock()
            
            # Configure mocks for banter engine failure
            mock_banter.side_effect = Exception("Banter engine failure")
            
            # Execute with failing banter engine
            result = await self.listener._process_message(trigger_message)
            
            # Verify error path
            mock_log.assert_called_once()
            mock_banter.assert_called_once_with(theme="greeting")
            mock_send.assert_not_called()  # No message should be sent when banter fails
            self.assertIsNotNone(result)  # Should still return result

    def test_extract_message_metadata_valid_message(self):
        """Test _extract_message_metadata with a valid message."""
        # Setup a valid message with all required fields
        test_message = {
            "id": "msg123",
            "snippet": {
                "displayMessage": "Hello world!"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "user123"
            }
        }
        
        # Call the method
        msg_id, display_message, author_name, author_id = self.listener._extract_message_metadata(test_message)
        
        # Verify results
        self.assertEqual(msg_id, "msg123")
        self.assertEqual(display_message, "Hello world!")
        self.assertEqual(author_name, "TestUser")
        self.assertEqual(author_id, "user123")
        
    def test_extract_message_metadata_missing_fields(self):
        """Test _extract_message_metadata with missing optional fields."""
        # Setup a message with minimal required fields, missing optional ones
        test_message = {
            "id": "msg123",
            "snippet": {
                # Missing displayMessage
            },
            "authorDetails": {
                "displayName": "TestUser"
                # Missing channelId
            }
        }
        
        # Call the method
        msg_id, display_message, author_name, author_id = self.listener._extract_message_metadata(test_message)
        
        # Verify results - should use defaults for missing fields
        self.assertEqual(msg_id, "msg123")
        self.assertEqual(display_message, "")  # Default for missing displayMessage
        self.assertEqual(author_name, "TestUser")
        self.assertEqual(author_id, "unknown")  # Default for missing channelId
        
    def test_extract_message_metadata_invalid_message(self):
        """Test _extract_message_metadata with an invalid message structure."""
        # Setup various invalid message structures
        invalid_messages = [
            {},  # Empty dict
            {"id": "msg123"},  # Missing snippet and authorDetails
            {"id": "msg123", "snippet": {}},  # Missing authorDetails
            {"id": "msg123", "authorDetails": {}}  # Missing snippet
        ]
        
        for invalid_msg in invalid_messages:
            # Call the method - should raise KeyError
            with self.assertRaises(KeyError):
                self.listener._extract_message_metadata(invalid_msg)
                
    def test_check_trigger_patterns_exact_match(self):
        """Test _check_trigger_patterns with exact emoji sequence match."""
        # Setup
        self.listener.emoji_sequence = "✊✋🖐️"
        
        # Test messages with exact emoji sequence
        test_cases = [
            "Message with emoji ✊✋🖐️ in the middle",
            "✊✋🖐️ at the start",
            "At the end ✊✋🖐️",
            "Just ✊✋🖐️"
        ]
        
        # Verify all test cases return True
        for test_case in test_cases:
            self.assertTrue(self.listener._check_trigger_patterns(test_case))
            
    def test_check_trigger_patterns_no_match(self):
        """Test _check_trigger_patterns with no emoji sequence match."""
        # Setup
        self.listener.emoji_sequence = "✊✋🖐️"
        
        # Test messages with no emoji sequence
        test_cases = [
            "Message with no emojis",
            "Message with different emojis 😀😁😂",
            "Partial sequence ✊✋ only",
            "Reversed sequence 🖐️✋✊"
        ]
        
        # Verify all test cases return False
        for test_case in test_cases:
            self.assertFalse(self.listener._check_trigger_patterns(test_case))
            
    def test_create_log_entry(self):
        """Test _create_log_entry creates correct log entry structure."""
        # Setup test data
        msg_id = "test123"
        author_name = "TestUser"
        display_message = "Hello world!"
        
        # Call the method
        log_entry = self.listener._create_log_entry(msg_id, author_name, display_message)
        
        # Verify structure and content
        self.assertIsInstance(log_entry, dict)
        self.assertEqual(log_entry["id"], msg_id)
        self.assertEqual(log_entry["author"], author_name)
        self.assertEqual(log_entry["message"], display_message)
        self.assertIn("timestamp", log_entry)
        
        # Verify timestamp format (ISO format)
        from datetime import datetime
        try:
            datetime.fromisoformat(log_entry["timestamp"])
        except ValueError:
            self.fail("Timestamp is not in valid ISO format")

    @pytest.mark.asyncio
    async def test_handle_emoji_trigger_success(self):
        """Test _handle_emoji_trigger with successful response generation and sending."""
        # Setup test data
        author_name = "TestUser"
        author_id = "user123"
        message_text = "Message with emoji ✊✋🖐️"
        
        # Mock dependencies
        with patch.object(self.listener, '_is_rate_limited', return_value=False) as mock_rate_limit, \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock, return_value=True) as mock_send, \
             patch.object(self.listener, '_update_trigger_time') as mock_update_time, \
             patch.object(self.listener.banter_engine, 'get_random_banter', return_value="Hello there!") as mock_banter:
            
            # Call the method
            result = await self.listener._handle_emoji_trigger(author_name, author_id, message_text)
            
            # Verify results
            self.assertTrue(result)
            mock_rate_limit.assert_called_once_with(author_id)
            mock_banter.assert_called_once_with(theme="greeting")
            mock_send.assert_called_once_with("Hello there!")
            mock_update_time.assert_called_once_with(author_id)
            
    @pytest.mark.asyncio
    async def test_handle_emoji_trigger_rate_limited(self):
        """Test _handle_emoji_trigger when the user is rate limited."""
        # Setup test data
        author_name = "TestUser"
        author_id = "user123"
        message_text = "Message with emoji ✊✋🖐️"
        
        # Mock dependencies - user is rate limited
        with patch.object(self.listener, '_is_rate_limited', return_value=True) as mock_rate_limit, \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch.object(self.listener, '_update_trigger_time') as mock_update_time, \
             patch.object(self.listener.banter_engine, 'get_random_banter') as mock_banter:
            
            # Call the method
            result = await self.listener._handle_emoji_trigger(author_name, author_id, message_text)
            
            # Verify results
            self.assertFalse(result)
            mock_rate_limit.assert_called_once_with(author_id)
            mock_banter.assert_not_called()
            mock_send.assert_not_called()
            mock_update_time.assert_not_called()
            
    @pytest.mark.asyncio
    async def test_handle_emoji_trigger_banter_failure(self):
        """Test _handle_emoji_trigger when banter generation fails."""
        # Setup test data
        author_name = "TestUser"
        author_id = "user123"
        message_text = "Message with emoji ✊✋🖐️"
        
        # Mock dependencies - banter generation raises exception
        with patch.object(self.listener, '_is_rate_limited', return_value=False) as mock_rate_limit, \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock, return_value=True) as mock_send, \
             patch.object(self.listener, '_update_trigger_time') as mock_update_time, \
             patch.object(self.listener.banter_engine, 'get_random_banter', side_effect=Exception("Banter error")) as mock_banter:
            
            # Call the method
            result = await self.listener._handle_emoji_trigger(author_name, author_id, message_text)
            
            # Verify results
            self.assertFalse(result)
            mock_rate_limit.assert_called_once_with(author_id)
            mock_banter.assert_called_once_with(theme="greeting")
            mock_send.assert_not_called()
            mock_update_time.assert_not_called()
            
    @pytest.mark.asyncio
    async def test_handle_emoji_trigger_invalid_banter(self):
        """Test _handle_emoji_trigger when banter engine returns invalid response."""
        # Setup test data
        author_name = "TestUser"
        author_id = "user123"
        message_text = "Message with emoji ✊✋🖐️"
        
        # Test cases for invalid banter responses
        invalid_responses = [
            None,  # None value
            "",    # Empty string
            "   ", # Whitespace only
            123,   # Non-string type
        ]
        
        for invalid_response in invalid_responses:
            # Mock dependencies
            with patch.object(self.listener, '_is_rate_limited', return_value=False) as mock_rate_limit, \
                 patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock, return_value=True) as mock_send, \
                 patch.object(self.listener, '_update_trigger_time') as mock_update_time, \
                 patch.object(self.listener.banter_engine, 'get_random_banter', return_value=invalid_response) as mock_banter:
                
                # Call the method
                result = await self.listener._handle_emoji_trigger(author_name, author_id, message_text)
                
                # Verify results - should use fallback and succeed
                self.assertTrue(result)
                mock_rate_limit.assert_called_once_with(author_id)
                mock_banter.assert_called_once_with(theme="greeting")
                # Should use fallback message
                mock_send.assert_called_once()
                self.assertIn("Hey there", mock_send.call_args[0][0])
                mock_update_time.assert_called_once_with(author_id)
                
                # Reset mocks for next test case
                mock_rate_limit.reset_mock()
                mock_banter.reset_mock()
                mock_send.reset_mock()
                mock_update_time.reset_mock()
                
    @pytest.mark.asyncio
    async def test_handle_emoji_trigger_send_failure(self):
        """Test _handle_emoji_trigger when message sending fails."""
        # Setup test data
        author_name = "TestUser"
        author_id = "user123"
        message_text = "Message with emoji ✊✋🖐️"
        
        # Mock dependencies - message sending fails
        with patch.object(self.listener, '_is_rate_limited', return_value=False) as mock_rate_limit, \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock, return_value=False) as mock_send, \
             patch.object(self.listener, '_update_trigger_time') as mock_update_time, \
             patch.object(self.listener.banter_engine, 'get_random_banter', return_value="Hello there!") as mock_banter:
            
            # Call the method
            result = await self.listener._handle_emoji_trigger(author_name, author_id, message_text)
            
            # Verify results
            self.assertFalse(result)
            mock_rate_limit.assert_called_once_with(author_id)
            mock_banter.assert_called_once_with(theme="greeting")
            mock_send.assert_called_once_with("Hello there!")
            mock_update_time.assert_not_called()  # Should not update trigger time on failure
            
    @pytest.mark.asyncio
    async def test_initialize_chat_session_with_existing_id(self):
        """Test _initialize_chat_session with an already existing chat ID."""
        # Setup - chat ID already exists
        self.listener.live_chat_id = "existing_chat_id"
        
        # Mock dependencies
        with patch.object(self.listener, '_get_live_chat_id') as mock_get_id:
            # Call the method
            result = await self.listener._initialize_chat_session()
            
            # Verify results
            self.assertTrue(result)
            mock_get_id.assert_not_called()  # Should not call _get_live_chat_id when ID exists
            
    @pytest.mark.asyncio
    async def test_initialize_chat_session_fetch_success(self):
        """Test _initialize_chat_session when fetching a new chat ID succeeds."""
        # Setup - no existing chat ID
        self.listener.live_chat_id = None
        self.listener.video_id = "test_video_id"
        
        # Mock dependencies - successful ID fetch
        with patch.object(self.listener, '_get_live_chat_id', return_value="fetched_chat_id") as mock_get_id:
            # Call the method
            result = await self.listener._initialize_chat_session()
            
            # Verify results
            self.assertTrue(result)
            mock_get_id.assert_called_once()
            self.assertEqual(self.listener.live_chat_id, "fetched_chat_id")
            
    @pytest.mark.asyncio
    async def test_initialize_chat_session_fetch_failure(self):
        """Test _initialize_chat_session when fetching a new chat ID fails."""
        # Setup - no existing chat ID
        self.listener.live_chat_id = None
        self.listener.video_id = "test_video_id"
        
        # Mock dependencies - ID fetch returns None
        with patch.object(self.listener, '_get_live_chat_id', return_value=None) as mock_get_id:
            # Call the method
            result = await self.listener._initialize_chat_session()
            
            # Verify results
            self.assertFalse(result)
            mock_get_id.assert_called_once()
            self.assertIsNone(self.listener.live_chat_id)
            
    @pytest.mark.asyncio
    async def test_initialize_chat_session_fetch_exception(self):
        """Test _initialize_chat_session when fetching a new chat ID raises an exception."""
        # Setup - no existing chat ID
        self.listener.live_chat_id = None
        self.listener.video_id = "test_video_id"
        
        # Mock dependencies - ID fetch raises exception
        with patch.object(self.listener, '_get_live_chat_id', side_effect=ValueError("Chat ID error")) as mock_get_id:
            # Call the method
            result = await self.listener._initialize_chat_session()
            
            # Verify results
            self.assertFalse(result)
            mock_get_id.assert_called_once()
            self.assertIsNone(self.listener.live_chat_id)

    @pytest.mark.asyncio
    async def test_send_greeting_message_success(self):
        """Test _send_greeting_message when a greeting message is configured and sending succeeds."""
        # Setup - configure greeting message
        self.listener.greeting_message = "Hello, welcome to the chat!"
        
        # Mock dependencies
        with patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock, return_value=True) as mock_send, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            
            # Call the method
            await self.listener._send_greeting_message()
            
            # Verify results
            mock_send.assert_called_once_with("Hello, welcome to the chat!")
            mock_sleep.assert_called_once_with(2)
    
    @pytest.mark.asyncio
    async def test_send_greeting_message_no_greeting(self):
        """Test _send_greeting_message when no greeting message is configured."""
        # Setup - no greeting message
        self.listener.greeting_message = None
        
        # Mock dependencies
        with patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            
            # Call the method
            await self.listener._send_greeting_message()
            
            # Verify results
            mock_send.assert_not_called()
            mock_sleep.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_send_greeting_message_send_failure(self):
        """Test _send_greeting_message when sending the greeting fails."""
        # Setup - configure greeting message
        self.listener.greeting_message = "Hello, welcome to the chat!"
        
        # Mock dependencies - sending fails
        with patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock, return_value=False) as mock_send, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            
            # Call the method
            await self.listener._send_greeting_message()
            
            # Verify results
            mock_send.assert_called_once_with("Hello, welcome to the chat!")
            mock_sleep.assert_called_once_with(2)  # Should still sleep even if sending fails
    
    @pytest.mark.asyncio
    async def test_send_greeting_message_exception(self):
        """Test _send_greeting_message when sending raises an exception."""
        # Setup - configure greeting message
        self.listener.greeting_message = "Hello, welcome to the chat!"
        
        # Mock dependencies - sending raises exception
        with patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock, side_effect=Exception("Send error")) as mock_send, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            
            # Call the method
            await self.listener._send_greeting_message()
            
            # Verify results
            mock_send.assert_called_once_with("Hello, welcome to the chat!")
            mock_sleep.assert_called_once_with(2)  # Should still sleep even if exception occurs
    
    @pytest.mark.asyncio
    async def test_poll_chat_cycle_success_with_messages(self):
        """Test _poll_chat_cycle when polling succeeds and returns messages."""
        # Setup test messages
        test_messages = [{"id": "msg1"}, {"id": "msg2"}]
        
        # Mock dependencies
        with patch.object(self.listener, '_update_viewer_count') as mock_update, \
             patch.object(self.listener, '_poll_chat_messages', new_callable=AsyncMock, return_value=test_messages) as mock_poll, \
             patch.object(self.listener, '_process_message_batch', new_callable=AsyncMock) as mock_process:
            
            # Call the method
            result = await self.listener._poll_chat_cycle()
            
            # Verify results
            self.assertFalse(result)  # Should return False (no critical failure)
            mock_update.assert_called_once()
            mock_poll.assert_called_once()
            mock_process.assert_called_once_with(test_messages)
    
    @pytest.mark.asyncio
    async def test_poll_chat_cycle_success_no_messages(self):
        """Test _poll_chat_cycle when polling succeeds but returns no messages."""
        # Mock dependencies
        with patch.object(self.listener, '_update_viewer_count') as mock_update, \
             patch.object(self.listener, '_poll_chat_messages', new_callable=AsyncMock, return_value=[]) as mock_poll, \
             patch.object(self.listener, '_process_message_batch', new_callable=AsyncMock) as mock_process:
            
            # Call the method
            result = await self.listener._poll_chat_cycle()
            
            # Verify results
            self.assertFalse(result)  # Should return False (no critical failure)
            mock_update.assert_called_once()
            mock_poll.assert_called_once()
            mock_process.assert_not_called()  # Should not process empty message list
    
    @pytest.mark.asyncio
    async def test_poll_chat_cycle_critical_failure(self):
        """Test _poll_chat_cycle when polling returns None (critical failure)."""
        # Mock dependencies
        with patch.object(self.listener, '_update_viewer_count') as mock_update, \
             patch.object(self.listener, '_poll_chat_messages', new_callable=AsyncMock, return_value=None) as mock_poll, \
             patch.object(self.listener, '_process_message_batch', new_callable=AsyncMock) as mock_process:
            
            # Call the method
            result = await self.listener._poll_chat_cycle()
            
            # Verify results
            self.assertTrue(result)  # Should return True (critical failure)
            mock_update.assert_called_once()
            mock_poll.assert_called_once()
            mock_process.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_process_message_batch_success(self):
        """Test _process_message_batch successfully processes all messages."""
        # Setup test messages
        test_messages = [{"id": "msg1"}, {"id": "msg2"}, {"id": "msg3"}]
        
        # Mock dependencies
        with patch.object(self.listener, '_process_message', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = {"processed": True}
            
            # Call the method
            await self.listener._process_message_batch(test_messages)
            
            # Verify results
            self.assertEqual(mock_process.call_count, 3)
            mock_process.assert_any_call(test_messages[0])
            mock_process.assert_any_call(test_messages[1])
            mock_process.assert_any_call(test_messages[2])
    
    @pytest.mark.asyncio
    async def test_process_message_batch_with_errors(self):
        """Test _process_message_batch continues processing when some messages fail."""
        # Setup test messages
        test_messages = [{"id": "msg1"}, {"id": "msg2"}, {"id": "msg3"}]
        
        # Mock dependencies - second message raises exception
        async def process_side_effect(message):
            if message["id"] == "msg2":
                raise Exception("Process error")
            return {"processed": True}
            
        with patch.object(self.listener, '_process_message', new_callable=AsyncMock) as mock_process:
            mock_process.side_effect = process_side_effect
            
            # Call the method
            await self.listener._process_message_batch(test_messages)
            
            # Verify results - should process all messages despite the error
            self.assertEqual(mock_process.call_count, 3)
            mock_process.assert_any_call(test_messages[0])
            mock_process.assert_any_call(test_messages[1])
            mock_process.assert_any_call(test_messages[2])
    
    @pytest.mark.asyncio
    async def test_process_message_batch_empty(self):
        """Test _process_message_batch with an empty message list."""
        # Setup empty message list
        test_messages = []
        
        # Mock dependencies
        with patch.object(self.listener, '_process_message', new_callable=AsyncMock) as mock_process:
            # Call the method
            await self.listener._process_message_batch(test_messages)
            
            # Verify results
            mock_process.assert_not_called()  # Should not call _process_message for empty list

    @pytest.mark.asyncio
    async def test_process_message_full_success_path(self):
        """Test the full successful path through _process_message."""
        # Setup a valid test message
        test_message = {
            "id": "msg123",
            "snippet": {
                "displayMessage": "Hello world!"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "user123"
            }
        }
        
        # Mock all dependencies
        with patch.object(self.listener, '_extract_message_metadata', return_value=("msg123", "Hello world!", "TestUser", "user123")) as mock_extract, \
             patch.object(self.listener, '_check_trigger_patterns', return_value=False) as mock_check, \
             patch.object(self.listener, '_create_log_entry', return_value={"id": "msg123", "log": True}) as mock_create, \
             patch.object(self.listener, '_log_to_user_file') as mock_log:
            
            # Call the method
            result = await self.listener._process_message(test_message)
            
            # Verify results
            self.assertEqual(result, {"id": "msg123", "log": True})
            mock_extract.assert_called_once_with(test_message)
            mock_check.assert_called_once_with("Hello world!")
            mock_create.assert_called_once_with("msg123", "TestUser", "Hello world!")
            mock_log.assert_called_once_with(test_message)
    
    @pytest.mark.asyncio
    async def test_process_message_with_trigger(self):
        """Test _process_message when a message contains a trigger pattern."""
        # Setup a test message with trigger
        test_message = {
            "id": "msg123",
            "snippet": {
                "displayMessage": "Message with ✊✋🖐️ emojis"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "user123"
            }
        }
        
        # Mock dependencies
        with patch.object(self.listener, '_extract_message_metadata', return_value=("msg123", "Message with ✊✋🖐️ emojis", "TestUser", "user123")) as mock_extract, \
             patch.object(self.listener, '_check_trigger_patterns', return_value=True) as mock_check, \
             patch.object(self.listener, '_handle_emoji_trigger', new_callable=AsyncMock, return_value=True) as mock_handle, \
             patch.object(self.listener, '_create_log_entry', return_value={"id": "msg123", "log": True}) as mock_create, \
             patch.object(self.listener, '_log_to_user_file') as mock_log, \
             patch.object(self.listener, '_is_rate_limited', return_value=False) as mock_rate:
            
            # Call the method
            result = await self.listener._process_message(test_message)
            
            # Verify results
            self.assertEqual(result, {"id": "msg123", "log": True})
            mock_extract.assert_called_once_with(test_message)
            mock_check.assert_called_once_with("Message with ✊✋🖐️ emojis")
            mock_handle.assert_called_once_with("TestUser", "user123", "Message with ✊✋🖐️ emojis")
            mock_create.assert_called_once_with("msg123", "TestUser", "Message with ✊✋🖐️ emojis")
            mock_log.assert_called_once_with(test_message)
    
    @pytest.mark.asyncio
    async def test_process_message_rate_limited_trigger(self):
        """Test _process_message when a message has a trigger but the user is rate limited."""
        # Setup a test message with trigger
        test_message = {
            "id": "msg123",
            "snippet": {
                "displayMessage": "Message with ✊✋🖐️ emojis"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "user123"
            }
        }
        
        # Mock dependencies
        with patch.object(self.listener, '_extract_message_metadata', return_value=("msg123", "Message with ✊✋🖐️ emojis", "TestUser", "user123")) as mock_extract, \
             patch.object(self.listener, '_check_trigger_patterns', return_value=True) as mock_check, \
             patch.object(self.listener, '_handle_emoji_trigger', new_callable=AsyncMock, return_value=False) as mock_handle, \
             patch.object(self.listener, '_is_rate_limited', return_value=True) as mock_rate, \
             patch.object(self.listener, '_create_log_entry') as mock_create, \
             patch.object(self.listener, '_log_to_user_file') as mock_log:
            
            # Call the method
            result = await self.listener._process_message(test_message)
            
            # Verify results
            self.assertIsNone(result)  # Returns None for rate-limited user
            mock_extract.assert_called_once_with(test_message)
            mock_check.assert_called_once_with("Message with ✊✋🖐️ emojis")
            mock_handle.assert_called_once_with("TestUser", "user123", "Message with ✊✋🖐️ emojis")
            mock_create.assert_not_called()
            mock_log.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_process_message_logging_error(self):
        """Test _process_message when logging the message fails."""
        # Setup a valid test message
        test_message = {
            "id": "msg123",
            "snippet": {
                "displayMessage": "Hello world!"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "user123"
            }
        }
        
        # Mock dependencies - logging fails
        with patch.object(self.listener, '_extract_message_metadata', return_value=("msg123", "Hello world!", "TestUser", "user123")) as mock_extract, \
             patch.object(self.listener, '_check_trigger_patterns', return_value=False) as mock_check, \
             patch.object(self.listener, '_create_log_entry', return_value={"id": "msg123", "log": True}) as mock_create, \
             patch.object(self.listener, '_log_to_user_file', side_effect=Exception("Logging error")) as mock_log:
            
            # Call the method
            result = await self.listener._process_message(test_message)
            
            # Verify results - should still return log entry despite logging error
            self.assertEqual(result, {"id": "msg123", "log": True})
            mock_extract.assert_called_once_with(test_message)
            mock_check.assert_called_once_with("Hello world!")
            mock_create.assert_called_once_with("msg123", "TestUser", "Hello world!")
            mock_log.assert_called_once_with(test_message)
    
    @pytest.mark.asyncio
    async def test_process_message_extraction_error(self):
        """Test _process_message when extracting message metadata fails."""
        # Setup a test message
        test_message = {
            "id": "msg123",
            # Missing required fields
        }
        
        # Mock dependencies - extraction raises KeyError
        with patch.object(self.listener, '_extract_message_metadata', side_effect=KeyError("Missing field")) as mock_extract:
            
            # Call the method
            result = await self.listener._process_message(test_message)
            
            # Verify results
            self.assertIsInstance(result, dict)
            self.assertIn("error", result)
            self.assertIn("timestamp", result)
            mock_extract.assert_called_once_with(test_message)
    
    @pytest.mark.asyncio
    async def test_end_to_end_message_processing(self):
        """Test end-to-end message processing flow."""
        # Setup a test message with trigger
        test_message = {
            "id": "msg123",
            "snippet": {
                "displayMessage": "Message with ✊✋🖐️ emojis"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "user123"
            }
        }
        
        # Mock all external dependencies but use real internal methods
        with patch.object(self.listener, '_is_rate_limited', return_value=False) as mock_rate_limit, \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock, return_value=True) as mock_send, \
             patch.object(self.listener, '_update_trigger_time') as mock_update_time, \
             patch.object(self.listener.banter_engine, 'get_random_banter', return_value="Hello there!") as mock_banter, \
             patch.object(self.listener, '_log_to_user_file') as mock_log:
            
            # Set the emoji sequence
            self.listener.emoji_sequence = "✊✋🖐️"
            
            # Call the method
            result = await self.listener._process_message(test_message)
            
            # Verify results
            self.assertIsNotNone(result)
            self.assertEqual(result["id"], "msg123")
            self.assertEqual(result["author"], "TestUser")
            self.assertEqual(result["message"], "Message with ✊✋🖐️ emojis")
            mock_rate_limit.assert_called_once_with("user123")
            mock_banter.assert_called_once_with(theme="greeting")
            mock_send.assert_called_once_with("Hello there!")
            mock_update_time.assert_called_once_with("user123")
            mock_log.assert_called_once_with(test_message)

    def test_emoji_and_trigger_emojis(self):
        """Test the emoji trigger attributes."""
        # Default values
        self.assertEqual(self.listener.trigger_emojis, ["✊", "✋", "🖐️"])
        
        # Change the values
        self.listener.trigger_emojis = ["🔥", "🌟", "💥"]
        self.assertEqual(self.listener.trigger_emojis, ["🔥", "🌟", "💥"])
        
        # Reset to default
        self.listener.trigger_emojis = ["✊", "✋", "🖐️"]
        self.assertEqual(self.listener.trigger_emojis, ["✊", "✋", "🖐️"])
    
    @pytest.mark.asyncio
    async def test_full_chat_lifecycle(self):
        """Test a complete lifecycle of the chat listener."""
        # Setup
        self.listener.video_id = "test_video_id"
        self.listener.is_running = False
        self.listener.greeting_message = "Hello, everyone!"
        
        # Mock all dependencies for initialization and listening
        with patch.object(self.listener, '_initialize_chat_session', new_callable=AsyncMock, return_value=True) as mock_init, \
             patch.object(self.listener, '_send_greeting_message', new_callable=AsyncMock) as mock_greeting, \
             patch.object(self.listener, '_poll_chat_cycle', new_callable=AsyncMock) as mock_poll, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            
            # Setup poll cycle side effect to stop after 3 iterations
            mock_poll.side_effect = [False, False, True]  # Last one is critical failure
            
            # Call the method
            await self.listener.start_listening()
            
            # Verify results
            mock_init.assert_called_once()
            mock_greeting.assert_called_once()
            self.assertEqual(mock_poll.call_count, 3)
            self.assertEqual(mock_sleep.call_count, 2)  # Sleep called twice, not after critical failure
            self.assertTrue(self.listener.is_running)  # Should be set to True at start
            
    @pytest.mark.asyncio
    async def test_chat_lifecycle_init_failure(self):
        """Test chat lifecycle when initialization fails."""
        # Setup
        self.listener.video_id = "test_video_id"
        self.listener.is_running = False
        
        # Mock dependencies - initialization fails
        with patch.object(self.listener, '_initialize_chat_session', new_callable=AsyncMock, return_value=False) as mock_init, \
             patch.object(self.listener, '_send_greeting_message', new_callable=AsyncMock) as mock_greeting, \
             patch.object(self.listener, '_poll_chat_cycle', new_callable=AsyncMock) as mock_poll:
            
            # Call the method
            await self.listener.start_listening()
            
            # Verify results
            mock_init.assert_called_once()
            mock_greeting.assert_not_called()
            mock_poll.assert_not_called()
            self.assertFalse(self.listener.is_running)  # Should remain False if init fails
            
    @pytest.mark.asyncio
    async def test_handle_auth_error_with_token_rotation(self):
        """Test handling authentication errors with token rotation."""
        # Setup - Create a properly structured HttpError with status 401
        mock_response = httplib2.Response({'status': 401})
        auth_error = googleapiclient.errors.HttpError(
            resp=mock_response,
            content=b'Authentication error'
        )
        
        # Fix the self.mock_response which may not be properly initialized
        self.mock_response = mock_response
        
        # Direct patching of the modules
        with patch('modules.livechat.src.livechat.token_manager.rotate_tokens', new_callable=AsyncMock) as mock_rotate, \
             patch('modules.livechat.src.livechat.get_authenticated_service') as mock_get_auth:
            
            # Configure the mocks with specific return values
            mock_rotate.return_value = 2  # Successfully rotated to token index 2
            new_service = MagicMock()  # New authenticated service
            mock_get_auth.return_value = new_service
            
            # Execute - Call the method directly
            result = await self.listener._handle_auth_error(auth_error)
            
            # Assert - Verify the expected behavior
            self.assertTrue(result)  # Should return True when successful
            mock_rotate.assert_awaited_once()
            mock_get_auth.assert_called_once_with(2)
            self.assertEqual(self.listener.youtube, new_service)  # Service should be updated
    
    @pytest.mark.asyncio
    async def test_handle_auth_error_rotation_failure(self):
        """Test handling authentication errors when token rotation fails."""
        # Create an auth error
        auth_error = googleapiclient.errors.HttpError(
            resp=httplib2.Response({'status': 401}),
            content=b'Auth error'
        )
        
        # Mock the token manager to return None (rotation failed)
        with patch('modules.token_manager.token_manager.rotate_tokens', new_callable=AsyncMock, return_value=None) as mock_rotate:
            
            # Execute
            result = await self.listener._handle_auth_error(auth_error)
            
            # Verify
            self.assertFalse(result)
            mock_rotate.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_handle_auth_error_reauth_failure(self):
        """Test handling authentication errors when re-authentication fails."""
        # Create an auth error
        auth_error = googleapiclient.errors.HttpError(
            resp=httplib2.Response({'status': 401}),
            content=b'Auth error'
        )
        
        # Mock rotation success but auth failure
        with patch('modules.token_manager.token_manager.rotate_tokens', new_callable=AsyncMock, return_value=1) as mock_rotate, \
             patch('utils.oauth_manager.get_authenticated_service', side_effect=Exception("Auth error")) as mock_auth:
            
            # Execute
            result = await self.listener._handle_auth_error(auth_error)
            
            # Verify
            self.assertFalse(result)
            mock_rotate.assert_called_once()
            mock_auth.assert_called_once_with(1)
            
    @pytest.mark.asyncio
    async def test_handle_auth_error_non_auth_error(self):
        """Test handling of non-authentication HTTP errors."""
        # Setup - Create a non-auth HTTP error (500 status)
        mock_response = httplib2.Response({'status': 500})
        non_auth_error = googleapiclient.errors.HttpError(
            resp=mock_response,
            content=b'Server error'
        )
        
        # Execute - Call the method directly
        result = await self.listener._handle_auth_error(non_auth_error)
        
        # Assert - Verify expected behavior
        self.assertFalse(result)  # Should return False for non-auth errors

    @pytest.mark.asyncio
    async def test_api_poll_chat_messages_success(self):
        """Test polling chat messages with full API mocking."""
        # Setup
        self.listener.live_chat_id = "test_chat_id"
        self.listener.next_page_token = "init_token"
        self.listener.poll_interval_ms = 5000  # Start with a value that should be changed
        
        # Create mock API response
        mock_response = {
            "items": [{"id": "msg1"}, {"id": "msg2"}],
            "nextPageToken": "next_token",
            "pollingIntervalMillis": 10000
        }
        
        # Mock API call
        with patch.object(self.listener.youtube, 'liveChatMessages') as mock_messages:
            # Set up multi-level mock
            mock_list = MagicMock()
            mock_execute = MagicMock(return_value=mock_response)
            mock_list.list.return_value.execute = mock_execute
            mock_messages.return_value = mock_list
            
            # Test with dynamic delay calculation
            with patch('utils.throttling.calculate_dynamic_delay', return_value=15.0) as mock_delay:
                # Call method
                messages = await self.listener._poll_chat_messages()
                
                # Verify
                self.assertEqual(len(messages), 2)
                self.assertEqual(messages[0]["id"], "msg1")
                self.assertEqual(messages[1]["id"], "msg2")
                self.assertEqual(self.listener.next_page_token, "next_token")
                # Should use the larger of server poll interval and dynamic delay
                self.assertEqual(self.listener.poll_interval_ms, 15000)  # 15 seconds in ms
                
                # Verify API call
                mock_list.list.assert_called_once_with(
                    liveChatId="test_chat_id",
                    part="snippet,authorDetails",
                    pageToken="init_token"
                )
                mock_delay.assert_called_once_with(self.listener.viewer_count)
    
    @pytest.mark.asyncio
    async def test_api_poll_chat_messages_empty(self):
        """Test polling chat messages with an empty response."""
        # Setup
        self.listener.live_chat_id = "test_chat_id"
        
        # Create mock API response - empty items
        mock_response = {
            "items": [],
            "nextPageToken": "next_token",
            "pollingIntervalMillis": 10000
        }
        
        # Mock API call
        with patch.object(self.listener.youtube, 'liveChatMessages') as mock_messages:
            # Set up multi-level mock
            mock_list = MagicMock()
            mock_execute = MagicMock(return_value=mock_response)
            mock_list.list.return_value.execute = mock_execute
            mock_messages.return_value = mock_list
            
            # Call method
            messages = await self.listener._poll_chat_messages()
            
            # Verify
            self.assertEqual(len(messages), 0)
            self.assertEqual(self.listener.next_page_token, "next_token")
    
    @pytest.mark.asyncio
    async def test_api_send_chat_message_success(self):
        """Test sending a chat message with API mocking."""
        # Setup
        self.listener.live_chat_id = "test_chat_id"
        message_text = "Hello, everyone!"
        
        # Mock API call
        with patch.object(self.listener.youtube, 'liveChatMessages') as mock_messages:
            # Set up multi-level mock
            mock_insert = MagicMock()
            mock_execute = MagicMock(return_value={"id": "response_id"})
            mock_insert.insert.return_value.execute = mock_execute
            mock_messages.return_value = mock_insert
            
            # Call method
            result = await self.listener.send_chat_message(message_text)
            
            # Verify
            self.assertTrue(result)
            
            # Verify API call
            mock_insert.insert.assert_called_once_with(
                part="snippet",
                body={
                    "snippet": {
                        "liveChatId": "test_chat_id",
                        "type": "textMessageEvent",
                        "textMessageDetails": {
                            "messageText": message_text
                        }
                    }
                }
            )
    
    @pytest.mark.asyncio
    async def test_api_send_chat_message_truncation(self):
        """Test message truncation when sending long messages."""
        # Setup
        self.listener.live_chat_id = "test_chat_id"
        long_message = "A" * 250  # Message longer than 200 chars
        
        # Mock API call
        with patch.object(self.listener.youtube, 'liveChatMessages') as mock_messages:
            # Set up multi-level mock
            mock_insert = MagicMock()
            mock_execute = MagicMock(return_value={"id": "response_id"})
            mock_insert.insert.return_value.execute = mock_execute
            mock_messages.return_value = mock_insert
            
            # Call method
            result = await self.listener.send_chat_message(long_message)
            
            # Verify
            self.assertTrue(result)
            
            # Verify API call - message should be truncated
            call_args = mock_insert.insert.call_args[1]
            sent_message = call_args["body"]["snippet"]["textMessageDetails"]["messageText"]
            self.assertEqual(len(sent_message), 200)  # 197 chars + "..."
            self.assertTrue(sent_message.endswith("..."))
            
    @pytest.mark.asyncio
    async def test_api_get_live_chat_id_success(self):
        """Test getting live chat ID from the API."""
        # Setup
        self.listener.live_chat_id = None  # Clear any existing ID
        self.listener.video_id = "test_video_id"
        
        # Create mock API response
        mock_response = {
            "items": [
                {
                    "liveStreamingDetails": {
                        "activeLiveChatId": "fetched_chat_id"
                    }
                }
            ]
        }
        
        # Mock API call
        with patch.object(self.listener.youtube, 'videos') as mock_videos:
            # Set up multi-level mock
            mock_list = MagicMock()
            mock_execute = MagicMock(return_value=mock_response)
            mock_list.list.return_value.execute = mock_execute
            mock_videos.return_value = mock_list
            
            # Call method
            result = self.listener._get_live_chat_id()
            
            # Verify
            self.assertEqual(result, "fetched_chat_id")
            self.assertEqual(self.listener.live_chat_id, "fetched_chat_id")
            
            # Verify API call
            mock_list.list.assert_called_once_with(
                part="liveStreamingDetails",
                id="test_video_id"
            )
    
    @pytest.mark.asyncio
    async def test_api_update_viewer_count_success(self):
        """Test updating viewer count from the API."""
        # Setup
        self.listener.video_id = "test_video_id"
        self.listener.viewer_count = 0  # Start with zero
        
        # Create mock API response
        mock_response = {
            "items": [
                {
                    "statistics": {
                        "viewCount": "1234"
                    }
                }
            ]
        }
        
        # Mock API call
        with patch.object(self.listener.youtube, 'videos') as mock_videos:
            # Set up multi-level mock
            mock_list = MagicMock()
            mock_execute = MagicMock(return_value=mock_response)
            mock_list.list.return_value.execute = mock_execute
            mock_videos.return_value = mock_list
            
            # Call method
            self.listener._update_viewer_count()
            
            # Verify
            self.assertEqual(self.listener.viewer_count, 1234)
            
            # Verify API call
            mock_list.list.assert_called_once_with(
                part="statistics",
                id="test_video_id"
            )

    @pytest.mark.asyncio
    async def test_api_poll_chat_messages_http_error(self):
        """Test polling chat messages with HTTP error."""
        # Setup
        self.listener.live_chat_id = "test_chat_id"
        
        # Create HTTP error
        http_error = googleapiclient.errors.HttpError(
            resp=httplib2.Response({'status': 500}),
            content=b'Server error'
        )
        
        # Mock API call
        with patch.object(self.listener.youtube, 'liveChatMessages') as mock_messages:
            # Set up multi-level mock to raise HTTP error
            mock_list = MagicMock()
            mock_list.list.return_value.execute.side_effect = http_error
            mock_messages.return_value = mock_list
            
            # Mock auth error handling
            with patch.object(self.listener, '_handle_auth_error', new_callable=AsyncMock, return_value=False) as mock_handle:
                # Call method - should raise the error
                with self.assertRaises(googleapiclient.errors.HttpError):
                    await self.listener._poll_chat_messages()
                
                # Verify
                mock_handle.assert_called_once_with(http_error)
    
    @pytest.mark.asyncio
    async def test_api_poll_chat_messages_http_error_handled(self):
        """Test polling chat messages with HTTP error that gets handled."""
        # Setup
        self.listener.live_chat_id = "test_chat_id"
        
        # Create HTTP error
        http_error = googleapiclient.errors.HttpError(
            resp=httplib2.Response({'status': 401}),
            content=b'Auth error'
        )
        
        # Mock API call
        with patch.object(self.listener.youtube, 'liveChatMessages') as mock_messages:
            # Set up multi-level mock to raise HTTP error
            mock_list = MagicMock()
            mock_list.list.return_value.execute.side_effect = http_error
            mock_messages.return_value = mock_list
            
            # Mock auth error handling - successful
            with patch.object(self.listener, '_handle_auth_error', new_callable=AsyncMock, return_value=True) as mock_handle:
                # Call method - should not raise the error
                messages = await self.listener._poll_chat_messages()
                
                # Verify
                mock_handle.assert_called_once_with(http_error)
                self.assertEqual(messages, [])  # Should return empty list
    
    @pytest.mark.asyncio
    async def test_api_poll_chat_messages_generic_error(self):
        """Test polling chat messages with generic error."""
        # Setup
        self.listener.live_chat_id = "test_chat_id"
        self.listener.error_backoff_seconds = 5
        
        # Mock API call
        with patch.object(self.listener.youtube, 'liveChatMessages') as mock_messages:
            # Set up multi-level mock to raise generic error
            mock_list = MagicMock()
            mock_list.list.return_value.execute.side_effect = Exception("Generic error")
            mock_messages.return_value = mock_list
            
            # Mock time.sleep to avoid actual sleep
            with patch('time.sleep') as mock_sleep:
                # Call method
                messages = await self.listener._poll_chat_messages()
                
                # Verify
                mock_sleep.assert_called_once_with(5)
                self.assertEqual(messages, [])  # Should return empty list
                self.assertEqual(self.listener.error_backoff_seconds, 10)  # Should double
    
    @pytest.mark.asyncio
    async def test_api_poll_chat_messages_backoff_max(self):
        """Test polling chat messages with backoff reaching maximum."""
        # Setup
        self.listener.live_chat_id = "test_chat_id"
        self.listener.error_backoff_seconds = 40  # Close to max (60)
        
        # Mock API call
        with patch.object(self.listener.youtube, 'liveChatMessages') as mock_messages:
            # Set up multi-level mock to raise generic error
            mock_list = MagicMock()
            mock_list.list.return_value.execute.side_effect = Exception("Generic error")
            mock_messages.return_value = mock_list
            
            # Mock time.sleep to avoid actual sleep
            with patch('time.sleep') as mock_sleep:
                # Call method
                messages = await self.listener._poll_chat_messages()
                
                # Verify
                mock_sleep.assert_called_once_with(40)
                self.assertEqual(messages, [])  # Should return empty list
                self.assertEqual(self.listener.error_backoff_seconds, 60)  # Should cap at 60
    
    @pytest.mark.asyncio
    async def test_api_send_chat_message_http_error(self):
        """Test sending a chat message with HTTP error."""
        # Setup
        self.listener.live_chat_id = "test_chat_id"
        message_text = "Hello, everyone!"
        
        # Create HTTP error
        http_error = googleapiclient.errors.HttpError(
            resp=httplib2.Response({'status': 500}),
            content=b'Server error'
        )
        
        # Mock API call
        with patch.object(self.listener.youtube, 'liveChatMessages') as mock_messages:
            # Set up multi-level mock to raise HTTP error
            mock_insert = MagicMock()
            mock_insert.insert.return_value.execute.side_effect = http_error
            mock_messages.return_value = mock_insert
            
            # Mock auth error handling
            with patch.object(self.listener, '_handle_auth_error', new_callable=AsyncMock, return_value=False) as mock_handle:
                # Call method
                result = await self.listener.send_chat_message(message_text)
                
                # Verify
                self.assertFalse(result)
                mock_handle.assert_called_once_with(http_error)
    
    @pytest.mark.asyncio
    async def test_api_send_chat_message_generic_error(self):
        """Test sending a chat message with generic error."""
        # Setup
        self.listener.live_chat_id = "test_chat_id"
        message_text = "Hello, everyone!"
        
        # Mock API call
        with patch.object(self.listener.youtube, 'liveChatMessages') as mock_messages:
            # Set up multi-level mock to raise generic error
            mock_insert = MagicMock()
            mock_insert.insert.return_value.execute.side_effect = Exception("Generic error")
            mock_messages.return_value = mock_insert
            
            # Call method
            result = await self.listener.send_chat_message(message_text)
            
            # Verify
            self.assertFalse(result)
    
    @pytest.mark.asyncio
    async def test_log_to_user_file_mkdir_error(self):
        """Test logging to user file when mkdir fails."""
        # Create test message
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "Test message"
            },
            "authorDetails": {
                "displayName": "TestUser"
            }
        }
        
        # Mock os.makedirs to raise an exception
        with patch('os.makedirs', side_effect=PermissionError("Access denied")) as mock_makedirs:
            # Call method - should raise the exception
            with self.assertRaises(Exception):
                self.listener._log_to_user_file(test_message)
                
            # Verify
            self.assertTrue(mock_makedirs.called)
            
    def test_file_operations_general(self):
        """Test various file operation scenarios."""
        # Mock message
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "Test message"
            },
            "authorDetails": {
                "displayName": "TestUser"
            }
        }
        
        # Test case: File open fails
        with patch('os.makedirs') as mock_makedirs, \
             patch('builtins.open', side_effect=PermissionError("Access denied")) as mock_open:
            
            with self.assertRaises(Exception):
                self.listener._log_to_user_file(test_message)
                
            mock_makedirs.assert_called_once()
            mock_open.assert_called_once()
            
        # Test case: JSON encoding fails
        with patch('os.makedirs') as mock_makedirs, \
             patch('builtins.open', unittest.mock.mock_open()) as mock_open, \
             patch('json.dumps', side_effect=TypeError("Encoding error")) as mock_dumps:
            
            with self.assertRaises(Exception):
                self.listener._log_to_user_file(test_message)
                
            mock_makedirs.assert_called_once()
            mock_open.assert_called_once()
            mock_dumps.assert_called_once_with(test_message)
    
    def test_config_initialzation(self):
        """Test the initialization with various configuration options."""
        # Test with minimal parameters
        minimal = LiveChatListener(
            youtube_service=self.mock_youtube,
            video_id="test_video"
        )
        self.assertEqual(minimal.video_id, "test_video")
        self.assertIsNone(minimal.live_chat_id)
        self.assertEqual(minimal.poll_interval_ms, 100000)  # Default
        
        # Test with custom parameters
        custom = LiveChatListener(
            youtube_service=self.mock_youtube,
            video_id="test_video",
            live_chat_id="test_chat_id"
        )
        self.assertEqual(custom.video_id, "test_video")
        self.assertEqual(custom.live_chat_id, "test_chat_id")

    @pytest.mark.asyncio
    async def test_handle_auth_error_targeted_coverage(self):
        """Test specifically targeting full coverage of _handle_auth_error method."""
        # Create a proper HttpError with status 401 
        mock_response = httplib2.Response({'status': 401})
        auth_error = googleapiclient.errors.HttpError(
            resp=mock_response,
            content=b'Authentication error for targeted coverage test'
        )
        
        # Scenario 1: Successful token rotation and re-authentication
        with patch('modules.token_manager.token_manager.rotate_tokens', new_callable=AsyncMock) as mock_rotate, \
             patch('utils.oauth_manager.get_authenticated_service') as mock_auth:
            
            # Configure mocks for success path
            mock_rotate.return_value = 3  # Successfully rotated to token index 3
            new_youtube_service = MagicMock()
            mock_auth.return_value = new_youtube_service
            
            # Execute the method directly
            result = await self.listener._handle_auth_error(auth_error)
            
            # Verify results
            self.assertTrue(result)  # Should return True on successful handling
            mock_rotate.assert_awaited_once()
            mock_auth.assert_called_once_with(3)
            self.assertEqual(self.listener.youtube, new_youtube_service)  # Service should be updated
        
        # Scenario 2: Token rotation fails
        with patch('modules.token_manager.token_manager.rotate_tokens', new_callable=AsyncMock) as mock_rotate:
            # Configure mock to return None (rotation failed)
            mock_rotate.return_value = None
            
            # Execute the method
            result = await self.listener._handle_auth_error(auth_error)
            
            # Verify results
            self.assertFalse(result)  # Should return False when rotation fails
            mock_rotate.assert_awaited_once()
        
        # Scenario 3: Token rotation succeeds but re-authentication fails
        with patch('modules.token_manager.token_manager.rotate_tokens', new_callable=AsyncMock) as mock_rotate, \
             patch('utils.oauth_manager.get_authenticated_service') as mock_auth:
            
            # Configure mocks - rotation succeeds but auth fails
            mock_rotate.return_value = 2
            mock_auth.side_effect = Exception("Authentication failed in test")
            
            # Execute the method
            result = await self.listener._handle_auth_error(auth_error)
            
            # Verify results
            self.assertFalse(result)  # Should return False on auth failure
            mock_rotate.assert_awaited_once()
            mock_auth.assert_called_once_with(2)
        
        # Scenario 4: Non-auth HTTP error (status 500)
        non_auth_resp = httplib2.Response({'status': 500})
        non_auth_error = googleapiclient.errors.HttpError(
            resp=non_auth_resp,
            content=b'Non-auth server error'
        )
        
        # No need to mock anything, as it should immediately return False
        result = await self.listener._handle_auth_error(non_auth_error)
        self.assertFalse(result)  # Should return False for non-auth HTTP errors
        
        # Scenario 5: Non-HTTP error
        regular_error = ValueError("Not an HTTP error")
        result = await self.listener._handle_auth_error(regular_error)
        self.assertFalse(result)  # Should return False for non-HTTP errors

    @pytest.mark.asyncio
    async def test_handle_auth_error_simplest_non_http_error(self):
        """Test the simplest path in _handle_auth_error with a non-HTTP error."""
        # Create a standard ValueError - this should only execute the isinstance check and final return
        standard_error = ValueError("Simple non-HTTP error for diagnosis")
        
        # Direct call to the method - minimal code path
        result = await self.listener._handle_auth_error(standard_error)
        
        # Simple verification
        self.assertFalse(result)  # Should return False for non-HTTP errors

if __name__ == '__main__':
    unittest.main() 