"""
Unit tests for the message sending functionality of LiveChatListener class
"""

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import logging
import httplib2
import pytest
import googleapiclient.errors
from modules.communication.livechat.livechat.src.livechat import LiveChatListener

class TestLiveChatListenerMessageSending(unittest.TestCase):
    """Test cases for message sending functionality of LiveChatListener."""
    
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
        
        # Mock the BanterEngine
        self.mock_banter_engine = MagicMock()
        self.mock_banter_engine.get_random_banter.return_value = "Hello there!"
        self.listener.banter_engine = self.mock_banter_engine

    def tearDown(self):
        """Tear down test fixtures."""
        logging.disable(logging.NOTSET)
    
    # Basic message sending tests
    
    @pytest.mark.asyncio
    async def test_send_chat_message_success(self):
        """Test sending a chat message successfully."""
        # Set up mock response
        self.mock_youtube.liveChatMessages().insert.return_value.execute.return_value = {"success": True}
        
        # Call the method
        result = await self.listener.send_chat_message("Hello, world!")
        
        # Verify results
        self.assertTrue(result)
        self.mock_youtube.liveChatMessages().insert.assert_called_once_with(
            part="snippet",
            body={
                "snippet": {
                    "liveChatId": self.live_chat_id,
                    "type": "textMessageEvent",
                    "textMessageDetails": {
                        "messageText": "Hello, world!"
                    }
                }
            }
        )
    
    @pytest.mark.asyncio
    async def test_send_chat_message_no_chat_id(self):
        """Test sending a chat message when no live_chat_id is set."""
        # Setup - remove chat ID
        self.listener.live_chat_id = None
        
        # Call the method
        result = await self.listener.send_chat_message("This should fail")
        
        # Verify results
        self.assertFalse(result)
        self.mock_youtube.liveChatMessages().insert.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_send_chat_message_too_long(self):
        """Test sending a chat message that exceeds the maximum length."""
        # Create a message that's too long (over 200 characters)
        long_message = "A" * 250
        
        # Set up mock response
        self.mock_youtube.liveChatMessages().insert.return_value.execute.return_value = {"success": True}
        
        # Call the method
        result = await self.listener.send_chat_message(long_message)
        
        # Verify results
        self.assertTrue(result)
        # Verify message was truncated
        truncated_message = "A" * 197 + "..."
        self.mock_youtube.liveChatMessages().insert.assert_called_once()
        call_args = self.mock_youtube.liveChatMessages().insert.call_args[1]
        self.assertEqual(call_args["body"]["snippet"]["textMessageDetails"]["messageText"], truncated_message)
    
    @pytest.mark.asyncio
    async def test_send_chat_message_api_error(self):
        """Test handling of API errors when sending a chat message."""
        # Setup API error
        self.mock_youtube.liveChatMessages().insert.return_value.execute.side_effect = \
            googleapiclient.errors.HttpError(
                resp=httplib2.Response({"status": 500}),
                content=b"Server error"
            )
        
        # Mock the auth error handler to return False (unhandled)
        with patch.object(self.listener, '_handle_auth_error', new_callable=AsyncMock, return_value=False) as mock_handle:
            # Call the method
            result = await self.listener.send_chat_message("Test message")
            
            # Verify results
            self.assertFalse(result)
            mock_handle.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_chat_message_auth_error_handled(self):
        """Test handling of authentication errors when sending a chat message."""
        # Setup auth error
        auth_error = googleapiclient.errors.HttpError(
            resp=httplib2.Response({"status": 401}),
            content=b"Auth error"
        )
        self.mock_youtube.liveChatMessages().insert.return_value.execute.side_effect = auth_error
        
        # Mock the auth error handler to return True (handled)
        with patch.object(self.listener, '_handle_auth_error', new_callable=AsyncMock, return_value=True) as mock_handle:
            # Call the method
            result = await self.listener.send_chat_message("Test message")
            
            # Verify results
            self.assertFalse(result)  # Even with handled auth error, this attempt still failed
            mock_handle.assert_called_once_with(auth_error)
    
    @pytest.mark.asyncio
    async def test_send_chat_message_unexpected_error(self):
        """Test handling of unexpected errors when sending a chat message."""
        # Setup unexpected error
        self.mock_youtube.liveChatMessages().insert.return_value.execute.side_effect = Exception("Unexpected error")
        
        # Call the method
        result = await self.listener.send_chat_message("Test message")
        
        # Verify results
        self.assertFalse(result)
    
    # Integration tests
    
    @pytest.mark.asyncio
    async def test_emoji_trigger_send_message(self):
        """Test that emoji triggers properly send chat messages."""
        # Setup test message with emoji trigger
        test_message = {
            "id": "msg123",
            "snippet": {
                "displayMessage": "Hello with ✊✋🖐️ emojis"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "user123"
            }
        }
        
        # Mock dependencies
        with patch.object(self.listener, '_is_rate_limited', return_value=False) as mock_rate_limited, \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock, return_value=True) as mock_send, \
             patch.object(self.listener, '_update_trigger_time') as mock_update_time, \
             patch.object(self.listener, '_log_to_user_file') as mock_log:
            
            # Call process_message which should trigger send_chat_message
            await self.listener._process_message(test_message)
            
            # Verify send_chat_message was called with banter response
            mock_send.assert_called_once_with("Hello there!")
            mock_update_time.assert_called_once_with("user123")
    
    @pytest.mark.asyncio
    async def test_emoji_trigger_send_failure(self):
        """Test emoji trigger handling when send_chat_message fails."""
        # Setup test message with emoji trigger
        test_message = {
            "id": "msg123",
            "snippet": {
                "displayMessage": "Hello with ✊✋🖐️ emojis"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "user123"
            }
        }
        
        # Mock dependencies
        with patch.object(self.listener, '_is_rate_limited', return_value=False) as mock_rate_limited, \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock, return_value=False) as mock_send, \
             patch.object(self.listener, '_update_trigger_time') as mock_update_time, \
             patch.object(self.listener, '_log_to_user_file') as mock_log:
            
            # Call process_message
            await self.listener._process_message(test_message)
            
            # Verify send_chat_message was called but _update_trigger_time was not
            # (should not update trigger time if sending fails)
            mock_send.assert_called_once_with("Hello there!")
            mock_update_time.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_send_greeting_message(self):
        """Test sending of greeting message during initialization."""
        # Setup greeting message
        self.listener.greeting_message = "Hello, everyone!"
        
        # Mock send_chat_message
        with patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock, return_value=True) as mock_send:
            # Call the method
            await self.listener._send_greeting_message()
            
            # Verify results
            mock_send.assert_called_once_with("Hello, everyone!")
    
    @pytest.mark.asyncio
    async def test_send_greeting_message_failure(self):
        """Test handling of failures when sending greeting message."""
        # Setup greeting message
        self.listener.greeting_message = "Hello, everyone!"
        
        # Mock send_chat_message to fail
        with patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock, return_value=False) as mock_send:
            # Call the method
            await self.listener._send_greeting_message()
            
            # Verify results
            mock_send.assert_called_once_with("Hello, everyone!")
            # Method should complete without raising exception
    
    @pytest.mark.asyncio
    async def test_send_greeting_message_no_greeting(self):
        """Test behavior when no greeting message is configured."""
        # Setup no greeting message
        self.listener.greeting_message = ""
        
        # Mock send_chat_message
        with patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send:
            # Call the method
            await self.listener._send_greeting_message()
            
            # Verify results
            mock_send.assert_not_called()  # Should not attempt to send empty greeting
    
    @pytest.mark.asyncio
    async def test_send_greeting_message_none(self):
        """Test behavior when greeting message is None."""
        # Setup greeting message as None
        self.listener.greeting_message = None
        
        # Mock send_chat_message
        with patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send:
            # Call the method
            await self.listener._send_greeting_message()
            
            # Verify results
            mock_send.assert_not_called()  # Should not attempt to send None greeting
    
    @pytest.mark.asyncio
    async def test_send_greeting_message_exception(self):
        """Test handling of exceptions when sending greeting message."""
        # Setup greeting message
        self.listener.greeting_message = "Hello, world!"
        
        # Mock send_chat_message to raise an exception
        with patch.object(self.listener, 'send_chat_message', 
                         new_callable=AsyncMock, 
                         side_effect=Exception("Test exception")) as mock_send, \
             patch('logging.error') as mock_log_error:
            
            # Call the method - should not raise exception
            await self.listener._send_greeting_message()
            
            # Verify results
            mock_send.assert_called_once_with("Hello, world!")
            mock_log_error.assert_called_once()  # Should log the error
    
    @pytest.mark.asyncio
    async def test_send_greeting_message_verify_sleep(self):
        """Test that asyncio.sleep is called after sending greeting message."""
        # Setup greeting message
        self.listener.greeting_message = "Hello, everyone!"
        
        # Mock send_chat_message and asyncio.sleep
        with patch.object(self.listener, 'send_chat_message', 
                          new_callable=AsyncMock, 
                          return_value=True) as mock_send, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            
            # Call the method
            await self.listener._send_greeting_message()
            
            # Verify results
            mock_send.assert_called_once_with("Hello, everyone!")
            mock_sleep.assert_called_once_with(2)  # Should pause for 2 seconds
    
    # Edge cases
    
    @pytest.mark.asyncio
    async def test_send_chat_message_empty_message(self):
        """Test sending an empty chat message."""
        # Set up mock response
        self.mock_youtube.liveChatMessages().insert.return_value.execute.return_value = {"success": True}
        
        # Call the method with empty message
        result = await self.listener.send_chat_message("")
        
        # Verify results - should still attempt to send
        self.assertTrue(result)
        self.mock_youtube.liveChatMessages().insert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_chat_message_special_characters(self):
        """Test sending a chat message with special characters."""
        # Message with special characters
        special_message = "Hello! 😊 Special characters: 👋 🌟 ñ é Ü"
        
        # Set up mock response
        self.mock_youtube.liveChatMessages().insert.return_value.execute.return_value = {"success": True}
        
        # Call the method
        result = await self.listener.send_chat_message(special_message)
        
        # Verify results
        self.assertTrue(result)
        call_args = self.mock_youtube.liveChatMessages().insert.call_args[1]
        self.assertEqual(call_args["body"]["snippet"]["textMessageDetails"]["messageText"], special_message)
    
    @pytest.mark.asyncio
    async def test_send_chat_message_exactly_max_length(self):
        """Test sending a chat message that is exactly the maximum length."""
        # Create a message that's exactly 200 characters
        exact_message = "A" * 200
        
        # Set up mock response
        self.mock_youtube.liveChatMessages().insert.return_value.execute.return_value = {"success": True}
        
        # Call the method
        result = await self.listener.send_chat_message(exact_message)
        
        # Verify results
        self.assertTrue(result)
        call_args = self.mock_youtube.liveChatMessages().insert.call_args[1]
        self.assertEqual(call_args["body"]["snippet"]["textMessageDetails"]["messageText"], exact_message)
        # Verify no truncation occurred
        self.assertEqual(len(call_args["body"]["snippet"]["textMessageDetails"]["messageText"]), 200)
    
    @pytest.mark.asyncio
    async def test_send_chat_message_with_specific_api_construction_lines_342_380(self):
        """Test specific API request construction logic in send_chat_message (lines 342-380)."""
        # Set up mock response
        insert_mock = MagicMock()
        self.mock_youtube.liveChatMessages.return_value.insert.return_value = insert_mock
        insert_mock.execute.return_value = {"id": "test_message_id"}
        
        # Call the method
        result = await self.listener.send_chat_message("Test API construction")
        
        # Verify the specific API construction steps
        self.mock_youtube.liveChatMessages.assert_called_once()
        self.mock_youtube.liveChatMessages().insert.assert_called_once_with(
            part="snippet",
            body={
                "snippet": {
                    "liveChatId": self.live_chat_id,
                    "type": "textMessageEvent",
                    "textMessageDetails": {
                        "messageText": "Test API construction"
                    }
                }
            }
        )
        insert_mock.execute.assert_called_once()
        self.assertTrue(result)
    
    @pytest.mark.asyncio
    async def test_send_chat_message_max_length_boundary_cases_lines_342_380(self):
        """Test boundary cases for message length truncation logic (lines 342-380)."""
        # Set up mock response
        self.mock_youtube.liveChatMessages().insert.return_value.execute.return_value = {"success": True}
        
        # Test cases: 
        # 1. Message exactly at max_len - 3 (197 chars) - should not be truncated
        # 2. Message at max_len - 2 (198 chars) - should be truncated
        # 3. Message at max_len - 1 (199 chars) - should be truncated
        # 4. Message at max_len (200 chars) - should be truncated
        
        test_cases = [
            {"length": 197, "should_truncate": False},
            {"length": 198, "should_truncate": True},
            {"length": 199, "should_truncate": True},
            {"length": 200, "should_truncate": True}
        ]
        
        for case in test_cases:
            message = "A" * case["length"]
            expected = message if not case["should_truncate"] else "A" * 197 + "..."
            
            # Reset mock
            self.mock_youtube.liveChatMessages().insert.reset_mock()
            
            # Call the method
            result = await self.listener.send_chat_message(message)
            
            # Verify results
            self.assertTrue(result)
            call_args = self.mock_youtube.liveChatMessages().insert.call_args[1]
            actual_message = call_args["body"]["snippet"]["textMessageDetails"]["messageText"]
            self.assertEqual(actual_message, expected, 
                            f"Failed for length {case['length']}: expected {'truncation' if case['should_truncate'] else 'no truncation'}")
    
    @pytest.mark.asyncio
    async def test_send_chat_message_http_error_with_retry_lines_342_380(self):
        """Test HTTP error handling with retry logic in send_chat_message (lines 342-380)."""
        # Setup HTTP error
        http_error = googleapiclient.errors.HttpError(
            resp=httplib2.Response({"status": 500}),
            content=b"Server error"
        )
        self.mock_youtube.liveChatMessages().insert.return_value.execute.side_effect = http_error
        
        # Setup auth handler to suggest retry
        with patch.object(self.listener, '_handle_auth_error', new_callable=AsyncMock) as mock_auth_handler:
            # First test: auth handler says no retry
            mock_auth_handler.return_value = False
            
            result = await self.listener.send_chat_message("Test retry logic")
            self.assertFalse(result)
            mock_auth_handler.assert_called_once_with(http_error)
            mock_auth_handler.reset_mock()
            
            # Second test: auth handler says retry (though actual retry not implemented)
            mock_auth_handler.return_value = True
            
            result = await self.listener.send_chat_message("Test retry logic with retry suggested")
            self.assertFalse(result)  # Still False because no actual retry is implemented
            mock_auth_handler.assert_called_once_with(http_error)
            
            # Verify message in logs about retry possibility
            # (This would require mocking the logger which we'll skip for simplicity)
    
    @pytest.mark.asyncio
    async def test_send_chat_message_general_exception_handling_lines_342_380(self):
        """Test the general exception handling block in send_chat_message (lines 342-380)."""
        # Setup various exception types that might occur
        exception_types = [
            ValueError("Invalid value"),
            RuntimeError("Runtime error"),
            ConnectionError("Network issue"),
            TimeoutError("Request timed out")
        ]
        
        for exception in exception_types:
            # Reset mock and set side effect
            self.mock_youtube.liveChatMessages().insert.return_value.execute.reset_mock()
            self.mock_youtube.liveChatMessages().insert.return_value.execute.side_effect = exception
            
            # Call the method
            result = await self.listener.send_chat_message(f"Test with {type(exception).__name__}")
            
            # Verify results
            self.assertFalse(result)  # Should fail gracefully for any exception
    
    @pytest.mark.asyncio
    async def test_send_chat_message_youtube_api_request_structure_lines_342_380(self):
        """Test the exact structure of the YouTube API request in lines 342-380."""
        # Mock response for checking request structure
        self.mock_youtube.liveChatMessages().insert.return_value.execute.return_value = {"success": True}
        
        # Call the method with a simple message
        test_message = "Testing API structure"
        await self.listener.send_chat_message(test_message)
        
        # Verify the exact structure of the constructed request
        # 1. Check the part parameter is correctly specified
        self.assertEqual(
            self.mock_youtube.liveChatMessages().insert.call_args[1]["part"],
            "snippet"
        )
        
        # 2. Check body structure is exactly as expected
        expected_body = {
            "snippet": {
                "liveChatId": self.live_chat_id,
                "type": "textMessageEvent",
                "textMessageDetails": {
                    "messageText": test_message
                }
            }
        }
        
        self.assertEqual(
            self.mock_youtube.liveChatMessages().insert.call_args[1]["body"],
            expected_body
        ) 