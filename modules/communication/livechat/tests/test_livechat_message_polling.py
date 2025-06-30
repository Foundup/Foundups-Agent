"""
Unit tests for the message polling functionality of LiveChatListener class
"""

import unittest
import logging
import time
import httplib2
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import googleapiclient.errors
from modules.communication.livechat.src.livechat import LiveChatListener

class AsyncMock(MagicMock):
    """Mock class for async methods."""
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)

class TestLiveChatListenerMessagePolling(unittest.TestCase):
    """Test cases for message polling functionality of LiveChatListener."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Disable logging during tests
        logging.disable(logging.CRITICAL)
        
        # Create mock YouTube service
        self.mock_youtube = MagicMock()
        self.video_id = "test_video_id"
        self.live_chat_id = "test_live_chat_id"
        
        # Set up mock responses
        self.mock_youtube.liveChatMessages().list.return_value.execute.return_value = {
            "pollingIntervalMillis": 1000,
            "nextPageToken": "test_next_token",
            "items": []
        }
        
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
        
    def tearDown(self):
        """Tear down test fixtures."""
        logging.disable(logging.NOTSET)
    
    # Basic polling tests
    
    @pytest.mark.asyncio
    async def test_poll_chat_messages_success(self):
        """Test successful polling of chat messages."""
        # Setup test messages
        test_messages = [{"id": "msg1"}, {"id": "msg2"}]
        
        # Setup mock response
        self.mock_youtube.liveChatMessages().list.return_value.execute.return_value = {
            "pollingIntervalMillis": 1000,
            "nextPageToken": "next_token",
            "items": test_messages
        }
        
        # Call the method
        messages = await self.listener._poll_chat_messages()
        
        # Verify results
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["id"], "msg1")
        self.assertEqual(messages[1]["id"], "msg2")
        self.assertEqual(self.listener.next_page_token, "next_token")
        self.assertEqual(self.listener.poll_interval_ms, 1000)
        self.assertEqual(self.listener.error_backoff_seconds, 5)  # Should reset on success
        
        # Verify API call
        self.mock_youtube.liveChatMessages().list.assert_called_once_with(
            liveChatId=self.live_chat_id,
            part="snippet,authorDetails",
            pageToken=self.listener.next_page_token
        )
    
    @pytest.mark.asyncio
    async def test_poll_chat_messages_empty(self):
        """Test polling chat messages when no new messages are available."""
        # Setup mock response with no messages
        self.mock_youtube.liveChatMessages().list.return_value.execute.return_value = {
            "pollingIntervalMillis": 2000,
            "nextPageToken": "next_token",
            "items": []
        }
        
        # Call the method
        messages = await self.listener._poll_chat_messages()
        
        # Verify results
        self.assertEqual(len(messages), 0)
        self.assertEqual(self.listener.next_page_token, "next_token")
        self.assertEqual(self.listener.poll_interval_ms, 2000)
        
        # Verify API call
        self.mock_youtube.liveChatMessages().list.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_poll_chat_messages_api_error(self):
        """Test polling chat messages when an API error occurs."""
        # Setup API error
        self.mock_youtube.liveChatMessages().list.return_value.execute.side_effect = \
            googleapiclient.errors.HttpError(
                resp=httplib2.Response({"status": 500}),
                content=b"Server error"
            )
        
        # Mock handle_auth_error to return False (unhandled error)
        with patch.object(self.listener, '_handle_auth_error', new_callable=AsyncMock, return_value=False) as mock_handle:
            # Call the method - should raise the error
            with self.assertRaises(googleapiclient.errors.HttpError):
                await self.listener._poll_chat_messages()
            
            # Verify handle_auth_error was called
            mock_handle.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_poll_chat_messages_auth_error_handled(self):
        """Test polling chat messages when an auth error is handled."""
        # Setup auth error
        auth_error = googleapiclient.errors.HttpError(
            resp=httplib2.Response({"status": 401}),
            content=b"Auth error"
        )
        self.mock_youtube.liveChatMessages().list.return_value.execute.side_effect = auth_error
        
        # Mock handle_auth_error to return True (handled error)
        with patch.object(self.listener, '_handle_auth_error', new_callable=AsyncMock, return_value=True) as mock_handle:
            # Call the method - should not raise the error
            messages = await self.listener._poll_chat_messages()
            
            # Verify results
            self.assertEqual(len(messages), 0)  # Should return empty list on handled auth error
            mock_handle.assert_called_once_with(auth_error)
    
    @pytest.mark.asyncio
    async def test_poll_chat_messages_auth_error_not_handled(self):
        """Test polling chat messages when an auth error is not handled."""
        # Setup auth error
        auth_error = googleapiclient.errors.HttpError(
            resp=httplib2.Response({"status": 401}),
            content=b"Auth error"
        )
        self.mock_youtube.liveChatMessages().list.return_value.execute.side_effect = auth_error
        
        # Mock handle_auth_error to return False (unhandled error)
        with patch.object(self.listener, '_handle_auth_error', new_callable=AsyncMock, return_value=False) as mock_handle:
            # Call the method - should raise the error
            with self.assertRaises(googleapiclient.errors.HttpError):
                await self.listener._poll_chat_messages()
            
            # Verify handle_auth_error was called
            mock_handle.assert_called_once_with(auth_error)
    
    @pytest.mark.asyncio
    @patch('time.sleep')
    async def test_poll_chat_messages_unexpected_error(self, mock_sleep):
        """Test polling chat messages when an unexpected error occurs."""
        # Setup unexpected error
        self.mock_youtube.liveChatMessages().list.return_value.execute.side_effect = Exception("Unexpected error")
        
        # Call the method - should handle the error and return empty list
        messages = await self.listener._poll_chat_messages()
        
        # Verify results
        self.assertEqual(len(messages), 0)
        mock_sleep.assert_called_once_with(5)  # Should sleep for backoff time
        self.assertEqual(self.listener.error_backoff_seconds, 10)  # Should double backoff time
    
    @pytest.mark.asyncio
    @patch('time.sleep')
    async def test_poll_chat_messages_max_backoff(self, mock_sleep):
        """Test polling chat messages with maximum backoff time."""
        # Set initial backoff to high value
        self.listener.error_backoff_seconds = 45
        
        # Setup unexpected error
        self.mock_youtube.liveChatMessages().list.return_value.execute.side_effect = Exception("Unexpected error")
        
        # Call the method - should handle the error and use max backoff
        messages = await self.listener._poll_chat_messages()
        
        # Verify results
        self.assertEqual(len(messages), 0)
        mock_sleep.assert_called_once_with(45)  # Should sleep for current backoff
        self.assertEqual(self.listener.error_backoff_seconds, 60)  # Should cap at 60 seconds
    
    # Dynamic delay tests
    
    @pytest.mark.asyncio
    @patch('modules.livechat.src.livechat.calculate_dynamic_delay')
    async def test_poll_chat_messages_with_dynamic_delay(self, mock_calculate_delay):
        """Test polling chat messages with dynamic delay calculation."""
        # Setup dynamic delay greater than server value
        mock_calculate_delay.return_value = 15.0  # 15 seconds
        
        # Setup mock response with smaller server interval
        self.mock_youtube.liveChatMessages().list.return_value.execute.return_value = {
            "pollingIntervalMillis": 5000,  # 5 seconds
            "nextPageToken": "next_token",
            "items": []
        }
        
        # Call the method
        await self.listener._poll_chat_messages()
        
        # Verify results - should use dynamic delay since it's greater
        self.assertEqual(self.listener.poll_interval_ms, 15000)  # 15 seconds in ms
        mock_calculate_delay.assert_called_once_with(self.listener.viewer_count)
    
    @pytest.mark.asyncio
    @patch('modules.livechat.src.livechat.calculate_dynamic_delay')
    async def test_poll_chat_messages_server_delay_higher(self, mock_calculate_delay):
        """Test polling chat messages when server delay is higher than dynamic delay."""
        # Setup dynamic delay smaller than server value
        mock_calculate_delay.return_value = 3.0  # 3 seconds
        
        # Setup mock response with larger server interval
        self.mock_youtube.liveChatMessages().list.return_value.execute.return_value = {
            "pollingIntervalMillis": 8000,  # 8 seconds
            "nextPageToken": "next_token",
            "items": []
        }
        
        # Call the method
        await self.listener._poll_chat_messages()
        
        # Verify results - should use server delay since it's greater
        self.assertEqual(self.listener.poll_interval_ms, 8000)  # 8 seconds in ms
        mock_calculate_delay.assert_called_once_with(self.listener.viewer_count)
    
    # Process message batch tests
    
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
    async def test_poll_chat_messages_quota_error(self):
        """Test polling chat messages when a quota error (403) occurs."""
        # Setup quota error
        quota_error = googleapiclient.errors.HttpError(
            resp=httplib2.Response({"status": 403}),
            content=b"Quota Exceeded"
        )
        self.mock_youtube.liveChatMessages().list.return_value.execute.side_effect = quota_error

        # Mock handle_auth_error to return True (handled error)
        with patch.object(self.listener, '_handle_auth_error', new_callable=AsyncMock, return_value=True) as mock_handle:
            messages = await self.listener._poll_chat_messages()
            self.assertEqual(messages, [])
            mock_handle.assert_called_once_with(quota_error)

    @pytest.mark.asyncio
    @patch('time.sleep')
    async def test_poll_chat_messages_general_exception_backoff(self, mock_sleep):
        """Test that error_backoff_seconds doubles and caps at 60 on repeated exceptions."""
        self.listener.error_backoff_seconds = 30
        self.mock_youtube.liveChatMessages().list.return_value.execute.side_effect = Exception("General error")
        messages = await self.listener._poll_chat_messages()
        self.assertEqual(messages, [])
        mock_sleep.assert_called_once_with(30)
        self.assertEqual(self.listener.error_backoff_seconds, 60)

    @pytest.mark.asyncio
    async def test_poll_chat_messages_next_page_token_and_items(self):
        """Test that next_page_token and poll_interval_ms are set from response."""
        test_messages = [{"id": "msg1"}]
        self.mock_youtube.liveChatMessages().list.return_value.execute.return_value = {
            "pollingIntervalMillis": 1234,
            "nextPageToken": "token123",
            "items": test_messages
        }
        messages = await self.listener._poll_chat_messages()
        self.assertEqual(messages, test_messages)
        self.assertEqual(self.listener.next_page_token, "token123")
        self.assertEqual(self.listener.poll_interval_ms, 1234)
        self.assertEqual(self.listener.error_backoff_seconds, 5)

