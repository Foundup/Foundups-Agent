import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from modules.livechat.src.livechat import LiveChatListener

class TestProcessMessageExtra:
    """Additional tests specifically targeting uncovered code in _process_message."""
    
    @pytest.mark.asyncio
    async def test_process_message_trigger_pattern_detected_rate_limited_failure(self):
        """Test process_message when emoji trigger is detected but fails due to rate limiting."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        
        # Create test message with emoji trigger
        test_message = {
            "id": "msg123",
            "snippet": {
                "displayMessage": "Hello ✊✋🖐️ world!"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "user123"
            }
        }
        
        # Mock _extract_message_metadata
        with patch.object(listener, '_extract_message_metadata') as mock_extract, \
             patch.object(listener, '_check_trigger_patterns') as mock_check, \
             patch.object(listener, '_handle_emoji_trigger', new_callable=AsyncMock) as mock_handle, \
             patch.object(listener, '_is_rate_limited') as mock_rate_limited, \
             patch.object(listener, '_create_log_entry') as mock_create, \
             patch.object(listener, '_log_to_user_file') as mock_log:
            
            # Configure mocks
            mock_extract.return_value = ("msg123", "Hello ✊✋🖐️ world!", "TestUser", "user123")
            mock_check.return_value = True  # Trigger pattern detected
            mock_handle.return_value = False  # Handling failed
            mock_rate_limited.return_value = True  # User is rate limited
            
            # Call the method
            result = await listener._process_message(test_message)
            
            # Verify results
            assert result is None  # Should return None when rate limited
            mock_extract.assert_called_once_with(test_message)
            mock_check.assert_called_once_with("Hello ✊✋🖐️ world!")
            mock_handle.assert_called_once_with("TestUser", "user123", "Hello ✊✋🖐️ world!")
            mock_rate_limited.assert_called_once_with("user123")
            mock_create.assert_not_called()  # Should not create log entry
            mock_log.assert_not_called()  # Should not log to file
    
    @pytest.mark.asyncio
    async def test_process_message_logging_fails_but_continues(self):
        """Test that process_message continues even if logging to file fails."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        
        # Create test message
        test_message = {
            "id": "msg123",
            "snippet": {
                "displayMessage": "Regular message"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "user123"
            }
        }
        
        # Create expected log entry
        expected_log = {
            "id": "msg123",
            "author": "TestUser",
            "message": "Regular message",
            "timestamp": "2023-01-01T12:00:00"  # Mock timestamp
        }
        
        # Mock _extract_message_metadata and datetime
        with patch.object(listener, '_extract_message_metadata') as mock_extract, \
             patch.object(listener, '_check_trigger_patterns') as mock_check, \
             patch.object(listener, '_create_log_entry') as mock_create, \
             patch.object(listener, '_log_to_user_file') as mock_log, \
             patch('modules.livechat.src.livechat.datetime') as mock_datetime:
            
            # Configure mocks
            mock_extract.return_value = ("msg123", "Regular message", "TestUser", "user123")
            mock_check.return_value = False  # No trigger pattern
            mock_create.return_value = expected_log
            mock_log.side_effect = Exception("File write error")  # Logging fails
            mock_now = MagicMock()
            mock_now.isoformat.return_value = "2023-01-01T12:00:00"
            mock_datetime.now.return_value = mock_now
            
            # Call the method
            result = await listener._process_message(test_message)
            
            # Verify results
            assert result == expected_log  # Should still return valid log entry
            mock_extract.assert_called_once_with(test_message)
            mock_check.assert_called_once_with("Regular message")
            mock_create.assert_called_once_with("msg123", "TestUser", "Regular message")
            mock_log.assert_called_once_with(test_message)  # Logging was attempted
    
    @pytest.mark.asyncio
    async def test_process_message_with_extraction_error(self):
        """Test process_message when message metadata extraction fails."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        
        # Create test message with missing fields
        test_message = {
            "id": "msg123"
            # Missing required fields
        }
        
        # Mock datetime
        with patch.object(listener, '_extract_message_metadata') as mock_extract, \
             patch('modules.livechat.src.livechat.datetime') as mock_datetime:
            
            # Configure mocks
            mock_extract.side_effect = KeyError("Missing required field")  # Extraction fails
            mock_now = MagicMock()
            mock_now.isoformat.return_value = "2023-01-01T12:00:00"
            mock_datetime.now.return_value = mock_now
            
            # Call the method
            result = await listener._process_message(test_message)
            
            # Verify results
            assert isinstance(result, dict)
            assert "error" in result
            assert "Missing required field" in result["error"]
            assert result["timestamp"] == "2023-01-01T12:00:00"
            mock_extract.assert_called_once_with(test_message)
    
    @pytest.mark.asyncio
    async def test_process_message_with_unexpected_error(self):
        """Test process_message handling of unexpected errors during processing."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        
        # Create test message
        test_message = {
            "id": "msg123",
            "snippet": {
                "displayMessage": "Regular message"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "user123"
            }
        }
        
        # Mock various methods to trigger an unexpected error
        with patch.object(listener, '_extract_message_metadata') as mock_extract, \
             patch.object(listener, '_check_trigger_patterns') as mock_check, \
             patch('modules.livechat.src.livechat.datetime') as mock_datetime:
            
            # Configure mocks
            mock_extract.return_value = ("msg123", "Regular message", "TestUser", "user123")
            mock_check.side_effect = Exception("Unexpected error during pattern check")  # Unexpected error
            mock_now = MagicMock()
            mock_now.isoformat.return_value = "2023-01-01T12:00:00"
            mock_datetime.now.return_value = mock_now
            
            # Call the method
            result = await listener._process_message(test_message)
            
            # Verify results
            assert isinstance(result, dict)
            assert "error" in result
            assert "Unexpected error during pattern check" in result["error"]
            assert result["timestamp"] == "2023-01-01T12:00:00"
            mock_extract.assert_called_once_with(test_message)
            mock_check.assert_called_once_with("Regular message")
    
    @pytest.mark.asyncio
    async def test_process_message_trigger_failure_not_rate_limited(self):
        """Test process_message when emoji trigger fails but user is not rate limited."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        
        # Create test message with emoji trigger
        test_message = {
            "id": "msg123",
            "snippet": {
                "displayMessage": "Hello ✊✋🖐️ world!"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "user123"
            }
        }
        
        # Create expected log entry
        expected_log = {
            "id": "msg123",
            "author": "TestUser",
            "message": "Hello ✊✋🖐️ world!",
            "timestamp": "2023-01-01T12:00:00"  # Mock timestamp
        }
        
        # Mock _extract_message_metadata and other methods
        with patch.object(listener, '_extract_message_metadata') as mock_extract, \
             patch.object(listener, '_check_trigger_patterns') as mock_check, \
             patch.object(listener, '_handle_emoji_trigger', new_callable=AsyncMock) as mock_handle, \
             patch.object(listener, '_is_rate_limited') as mock_rate_limited, \
             patch.object(listener, '_create_log_entry') as mock_create, \
             patch.object(listener, '_log_to_user_file') as mock_log, \
             patch('modules.livechat.src.livechat.datetime') as mock_datetime:
            
            # Configure mocks
            mock_extract.return_value = ("msg123", "Hello ✊✋🖐️ world!", "TestUser", "user123")
            mock_check.return_value = True  # Trigger pattern detected
            mock_handle.return_value = False  # Handling failed
            mock_rate_limited.return_value = False  # User is NOT rate limited
            mock_create.return_value = expected_log
            mock_now = MagicMock()
            mock_now.isoformat.return_value = "2023-01-01T12:00:00"
            mock_datetime.now.return_value = mock_now
            
            # Call the method
            result = await listener._process_message(test_message)
            
            # Verify results
            assert result == expected_log  # Should return log entry since not rate limited
            mock_extract.assert_called_once_with(test_message)
            mock_check.assert_called_once_with("Hello ✊✋🖐️ world!")
            mock_handle.assert_called_once_with("TestUser", "user123", "Hello ✊✋🖐️ world!")
            mock_rate_limited.assert_called_once_with("user123")
            mock_create.assert_called_once_with("msg123", "TestUser", "Hello ✊✋🖐️ world!")
            mock_log.assert_called_once_with(test_message) 