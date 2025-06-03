"""
Unit tests for the message processing functionality of LiveChatListener class
"""

import unittest
from unittest.mock import patch, MagicMock, AsyncMock, mock_open
import asyncio
import logging
import time
from datetime import datetime
import os
import json
import pytest
import googleapiclient.errors
from googleapiclient.errors import HttpError
import httplib2
from modules.communication.livechat.livechat.src.livechat import LiveChatListener
from modules.ai_intelligence.banter_engine import BanterEngine

class TestLiveChatListenerMessageProcessing(unittest.TestCase):
    """Test cases for message processing functionality of LiveChatListener."""
    
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
    
    # Tests for message processing methods
    
    @pytest.mark.asyncio
    async def test_process_message_trigger_pattern_detected_rate_limited_failure(self):
        """Test process_message when emoji trigger is detected but fails due to rate limiting."""
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
        with patch.object(self.listener, '_extract_message_metadata') as mock_extract, \
             patch.object(self.listener, '_check_trigger_patterns') as mock_check, \
             patch.object(self.listener, '_handle_emoji_trigger', new_callable=AsyncMock) as mock_handle, \
             patch.object(self.listener, '_is_rate_limited') as mock_rate_limited, \
             patch.object(self.listener, '_create_log_entry') as mock_create, \
             patch.object(self.listener, '_log_to_user_file') as mock_log:
            
            # Configure mocks
            mock_extract.return_value = ("msg123", "Hello ✊✋🖐️ world!", "TestUser", "user123", "user")
            mock_check.return_value = True  # Trigger pattern detected
            mock_handle.return_value = False  # Handling failed
            mock_rate_limited.return_value = True  # User is rate limited
            
            # Call the method
            result = await self.listener._process_message(test_message)
            
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
        with patch.object(self.listener, '_extract_message_metadata') as mock_extract, \
             patch.object(self.listener, '_check_trigger_patterns') as mock_check, \
             patch.object(self.listener, '_create_log_entry') as mock_create, \
             patch.object(self.listener, '_log_to_user_file') as mock_log, \
             patch('modules.livechat.src.livechat.datetime') as mock_datetime:
            
            # Configure mocks
            mock_extract.return_value = ("msg123", "Regular message", "TestUser", "user123", "user")
            mock_check.return_value = False  # No trigger pattern
            mock_create.return_value = expected_log
            mock_log.side_effect = Exception("File write error")  # Logging fails
            mock_now = MagicMock()
            mock_now.isoformat.return_value = "2023-01-01T12:00:00"
            mock_datetime.now.return_value = mock_now
            
            # Call the method
            result = await self.listener._process_message(test_message)
            
            # Verify results
            assert result == expected_log  # Should still return valid log entry
            mock_extract.assert_called_once_with(test_message)
            mock_check.assert_called_once_with("Regular message")
            mock_create.assert_called_once_with("msg123", "TestUser", "Regular message")
            mock_log.assert_called_once_with(test_message)  # Logging was attempted
    
    @pytest.mark.asyncio
    async def test_process_message_with_extraction_error(self):
        """Test process_message when message metadata extraction fails."""
        # Create test message with missing fields
        test_message = {
            "id": "msg123"
            # Missing required fields
        }
        
        # Mock datetime
        with patch.object(self.listener, '_extract_message_metadata') as mock_extract, \
             patch('modules.livechat.src.livechat.datetime') as mock_datetime:
            
            # Configure mocks
            mock_extract.side_effect = KeyError("Missing required field")  # Extraction fails
            mock_now = MagicMock()
            mock_now.isoformat.return_value = "2023-01-01T12:00:00"
            mock_datetime.now.return_value = mock_now
            
            # Call the method
            result = await self.listener._process_message(test_message)
            
            # Verify results
            assert isinstance(result, dict)
            assert "error" in result
            assert "Missing required field" in result["error"]
            assert result["timestamp"] == "2023-01-01T12:00:00"
            mock_extract.assert_called_once_with(test_message)
    
    @pytest.mark.asyncio
    async def test_process_message_with_unexpected_error(self):
        """Test process_message handling of unexpected errors during processing."""
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
        with patch.object(self.listener, '_extract_message_metadata') as mock_extract, \
             patch.object(self.listener, '_check_trigger_patterns') as mock_check, \
             patch('modules.livechat.src.livechat.datetime') as mock_datetime:
            
            # Configure mocks
            mock_extract.return_value = ("msg123", "Regular message", "TestUser", "user123", "user")
            mock_check.side_effect = Exception("Unexpected error during pattern check")  # Unexpected error
            mock_now = MagicMock()
            mock_now.isoformat.return_value = "2023-01-01T12:00:00"
            mock_datetime.now.return_value = mock_now
            
            # Call the method
            result = await self.listener._process_message(test_message)
            
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
        with patch.object(self.listener, '_extract_message_metadata') as mock_extract, \
             patch.object(self.listener, '_check_trigger_patterns') as mock_check, \
             patch.object(self.listener, '_handle_emoji_trigger', new_callable=AsyncMock) as mock_handle, \
             patch.object(self.listener, '_is_rate_limited') as mock_rate_limited, \
             patch.object(self.listener, '_create_log_entry') as mock_create, \
             patch.object(self.listener, '_log_to_user_file') as mock_log, \
             patch('modules.livechat.src.livechat.datetime') as mock_datetime:
            
            # Configure mocks
            mock_extract.return_value = ("msg123", "Hello ✊✋🖐️ world!", "TestUser", "user123", "user")
            mock_check.return_value = True  # Trigger pattern detected
            mock_handle.return_value = False  # Handling failed
            mock_rate_limited.return_value = False  # User is NOT rate limited
            mock_create.return_value = expected_log
            mock_now = MagicMock()
            mock_now.isoformat.return_value = "2023-01-01T12:00:00"
            mock_datetime.now.return_value = mock_now
            
            # Call the method
            result = await self.listener._process_message(test_message)
            
            # Verify results
            assert result == expected_log  # Should return log entry since not rate limited
            mock_extract.assert_called_once_with(test_message)
            mock_check.assert_called_once_with("Hello ✊✋🖐️ world!")
            mock_handle.assert_called_once_with("TestUser", "user123", "Hello ✊✋🖐️ world!")
            mock_rate_limited.assert_called_once_with("user123")
            mock_create.assert_called_once_with("msg123", "TestUser", "Hello ✊✋🖐️ world!")
            mock_log.assert_called_once_with(test_message)
    
    @pytest.mark.asyncio
    async def test_extract_message_metadata_standard_message(self):
        """Test _extract_message_metadata with a standard message."""
        test_message = {
            "id": "msg123",
            "snippet": {
                "displayMessage": "Hello world!"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "user123"
                # No role flags, defaults to 'user'
            }
        }
        
        expected_result = ("msg123", "Hello world!", "TestUser", "user123", "user") # Added "user" role
        
        # Call the method
        result = self.listener._extract_message_metadata(test_message)
        
        # Verify results
        self.assertEqual(result, expected_result)
    
    @pytest.mark.asyncio
    async def test_extract_message_metadata_chat_owner(self):
        """Test _extract_message_metadata when the author is the chat owner."""
        test_message = {
            "id": "msg-owner",
            "snippet": {"displayMessage": "Owner message"},
            "authorDetails": {
                "displayName": "ChannelOwner",
                "channelId": "owner123",
                "isChatOwner": True,
                "isChatModerator": False # Explicitly set other flags to ensure owner takes precedence
            }
        }
        expected_result = ("msg-owner", "Owner message", "ChannelOwner", "owner123", "owner")
        result = self.listener._extract_message_metadata(test_message)
        self.assertEqual(result, expected_result)
    
    @pytest.mark.asyncio
    async def test_extract_message_metadata_chat_moderator(self):
        """Test _extract_message_metadata when the author is a chat moderator (default to standard_mod if not in user_tiers)."""
        # Simulate listener.user_tiers being empty or not containing this user
        self.listener.user_tiers = {}
        test_message = {
            "id": "msg-mod",
            "snippet": {"displayMessage": "Moderator message"},
            "authorDetails": {
                "displayName": "ChatMod",
                "channelId": "mod123",
                "isChatOwner": False,
                "isChatModerator": True
            }
        }
        expected_result = ("msg-mod", "Moderator message", "ChatMod", "mod123", "standard_mod") # Expect standard_mod
        result = self.listener._extract_message_metadata(test_message)
        self.assertEqual(result, expected_result)

    @pytest.mark.asyncio
    async def test_extract_message_metadata_managing_moderator(self):
        """Test _extract_message_metadata for a managing moderator defined in user_tiers."""
        self.listener.user_tiers = {"managing_mod_id": "managing_mod"}
        test_message = {
            "id": "msg-managing-mod",
            "snippet": {"displayMessage": "Managing moderator message"},
            "authorDetails": {
                "displayName": "ManagingMod",
                "channelId": "managing_mod_id",
                "isChatOwner": False,
                "isChatModerator": True
            }
        }
        expected_result = ("msg-managing-mod", "Managing moderator message", "ManagingMod", "managing_mod_id", "managing_mod")
        result = self.listener._extract_message_metadata(test_message)
        self.assertEqual(result, expected_result)

    @pytest.mark.asyncio
    async def test_extract_message_metadata_standard_moderator_from_config(self):
        """Test _extract_message_metadata for a standard moderator explicitly defined in user_tiers."""
        self.listener.user_tiers = {"standard_mod_id": "standard_mod"}
        test_message = {
            "id": "msg-standard-mod-config",
            "snippet": {"displayMessage": "Standard moderator message (from config)"},
            "authorDetails": {
                "displayName": "StandardModConfig",
                "channelId": "standard_mod_id",
                "isChatOwner": False,
                "isChatModerator": True
            }
        }
        expected_result = ("msg-standard-mod-config", "Standard moderator message (from config)", "StandardModConfig", "standard_mod_id", "standard_mod")
        result = self.listener._extract_message_metadata(test_message)
        self.assertEqual(result, expected_result)

    @pytest.mark.asyncio
    async def test_extract_message_metadata_moderator_unknown_tier_in_config(self):
        """Test _extract_message_metadata for a moderator with an unrecognized tier in user_tiers (should default to standard_mod)."""
        self.listener.user_tiers = {"unknown_tier_mod_id": "super_mod"} # "super_mod" is not 'managing_mod'
        test_message = {
            "id": "msg-unknown-tier-mod",
            "snippet": {"displayMessage": "Moderator with unknown tier"},
            "authorDetails": {
                "displayName": "UnknownTierMod",
                "channelId": "unknown_tier_mod_id",
                "isChatOwner": False,
                "isChatModerator": True
            }
        }
        # Expect standard_mod as fallback because "super_mod" isn't "managing_mod"
        expected_result = ("msg-unknown-tier-mod", "Moderator with unknown tier", "UnknownTierMod", "unknown_tier_mod_id", "standard_mod")
        result = self.listener._extract_message_metadata(test_message)
        self.assertEqual(result, expected_result)

    @pytest.mark.asyncio
    async def test_extract_message_metadata_owner_in_user_tiers_as_managing_mod(self):
        """Test owner role when user is also in user_tiers as managing_mod (isChatOwner should take precedence)."""
        self.listener.user_tiers = {"owner_id_in_config": "managing_mod"}
        test_message = {
            "id": "msg-owner-in-config",
            "snippet": {"displayMessage": "Owner message (in config as managing_mod)"},
            "authorDetails": {
                "displayName": "OwnerInConfig",
                "channelId": "owner_id_in_config",
                "isChatOwner": True, # This should override the tier from config
                "isChatModerator": True # Also a moderator
            }
        }
        expected_result = ("msg-owner-in-config", "Owner message (in config as managing_mod)", "OwnerInConfig", "owner_id_in_config", "owner")
        result = self.listener._extract_message_metadata(test_message)
        self.assertEqual(result, expected_result)
    
    @pytest.mark.asyncio
    async def test_extract_message_metadata_regular_user(self):
        """Test _extract_message_metadata for a regular user with no special flags."""
        test_message = {
            "id": "msg-user",
            "snippet": {"displayMessage": "User message"},
            "authorDetails": {
                "displayName": "RegularUser",
                "channelId": "user789",
                "isChatOwner": False, # Explicitly false
                "isChatModerator": False # Explicitly false
            }
        }
        expected_result = ("msg-user", "User message", "RegularUser", "user789", "user")
        result = self.listener._extract_message_metadata(test_message)
        self.assertEqual(result, expected_result)

    @pytest.mark.asyncio
    async def test_extract_message_metadata_user_with_no_role_flags_present(self):
        """Test _extract_message_metadata for a user where role flags are not present in authorDetails."""
        test_message = {
            "id": "msg-noroleflags",
            "snippet": {"displayMessage": "User message with no role flags"},
            "authorDetails": {
                "displayName": "NoFlagsUser",
                "channelId": "user000"
                # isChatOwner and isChatModerator keys are entirely missing
            }
        }
        expected_result = ("msg-noroleflags", "User message with no role flags", "NoFlagsUser", "user000", "user")
        result = self.listener._extract_message_metadata(test_message)
        self.assertEqual(result, expected_result)

    @pytest.mark.asyncio
    async def test_extract_message_metadata_owner_overrides_moderator(self):
        """Test _extract_message_metadata ensures owner role takes precedence if both flags are true."""
        test_message = {
            "id": "msg-owner-mod-conflict",
            "snippet": {"displayMessage": "Owner but also mod flagged"},
            "authorDetails": {
                "displayName": "OwnerModConflict",
                "channelId": "conflict123",
                "isChatOwner": True,
                "isChatModerator": True # Both true, owner should win
            }
        }
        expected_result = ("msg-owner-mod-conflict", "Owner but also mod flagged", "OwnerModConflict", "conflict123", "owner")
        result = self.listener._extract_message_metadata(test_message)
        self.assertEqual(result, expected_result)

    @pytest.mark.asyncio
    async def test_check_trigger_patterns_match(self):
        """Test that trigger patterns are correctly detected."""
        # Set trigger emojis
        self.listener.trigger_emojis = ["✊", "✋", "🖐️"]
        
        # Test with message containing the emoji sequence
        result = self.listener._check_trigger_patterns("Hello ✊✋🖐️ world!")
        
        # Verify result
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_trigger_patterns_no_match(self):
        """Test that non-matching messages are correctly identified."""
        # Set trigger emojis
        self.listener.trigger_emojis = ["✊", "✋", "🖐️"]
        
        # Test with message not containing the sequence
        result = self.listener._check_trigger_patterns("Hello world!")
        
        # Verify result
        assert result is False
    
    @pytest.mark.asyncio
    async def test_create_log_entry_format(self):
        """Test that log entries are created in the correct format."""
        # Mock datetime
        with patch('modules.livechat.src.livechat.datetime') as mock_datetime:
            mock_now = MagicMock()
            mock_now.isoformat.return_value = "2023-01-01T12:00:00"
            mock_datetime.now.return_value = mock_now
            
            # Call the method
            log_entry = self.listener._create_log_entry("msg123", "TestUser", "Hello world!")
            
            # Verify result
            assert log_entry == {
                "id": "msg123",
                "author": "TestUser",
                "message": "Hello world!",
                "timestamp": "2023-01-01T12:00:00"
            }
    
    @pytest.mark.asyncio
    async def test_log_to_user_file_success(self):
        """Test successful logging to a user file."""
        # Create test message
        test_message = {
            "id": "msg123",
            "snippet": {
                "displayMessage": "Hello world!"
            },
            "authorDetails": {
                "displayName": "TestUser"
            }
        }
        
        # Mock os.makedirs and open
        with patch('os.makedirs') as mock_makedirs, \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('json.dumps') as mock_dumps:
            
            # Configure mocks
            mock_dumps.return_value = '{"id": "msg123", "message": "Hello world!"}'
            
            # Call the method
            self.listener._log_to_user_file(test_message)
            
            # Verify results
            mock_makedirs.assert_called_once()
            mock_file.assert_called_once()
            mock_dumps.assert_called_once_with(test_message)
            mock_file().write.assert_called_once_with('{"id": "msg123", "message": "Hello world!"}\n')
    
    @pytest.mark.asyncio
    async def test_log_to_user_file_failure(self):
        """Test handling of errors during file logging."""
        # Create test message
        test_message = {
            "id": "msg123",
            "snippet": {
                "displayMessage": "Hello world!"
            },
            "authorDetails": {
                "displayName": "TestUser"
            }
        }
        
        # Mock os.makedirs to raise an exception
        with patch('os.makedirs') as mock_makedirs:
            mock_makedirs.side_effect = PermissionError("Cannot create directory")
            
            # Call the method should raise the exception
            with pytest.raises(Exception):
                self.listener._log_to_user_file(test_message)
    
    @pytest.mark.asyncio
    async def test_process_message_batch_empty(self):
        """Test _process_message_batch with an empty list."""
        # Mock _process_message
        with patch.object(self.listener, '_process_message', new_callable=AsyncMock) as mock_process:
            # Call the method with empty list
            await self.listener._process_message_batch([])
            
            # Verify results
            mock_process.assert_not_called()  # Should not be called with empty list
    
    @pytest.mark.asyncio
    async def test_process_message_batch_processing_exception(self):
        """Test _process_message_batch when _process_message raises an exception."""
        # Mock _process_message to raise an exception
        with patch.object(self.listener, '_process_message', new_callable=AsyncMock) as mock_process:
            mock_process.side_effect = Exception("Processing failed")
            
            # Call the method
            await self.listener._process_message_batch([{"id": "msg1"}])
            
            # Verify results
            mock_process.assert_called_once()  # Should be called once
            # Method should not raise the exception - it should be caught and logged
    
    @pytest.mark.asyncio
    async def test_process_message_batch_with_multiple_messages(self):
        """Test processing multiple messages in a batch."""
        # Create test messages
        messages = [
            {"id": "msg1", "content": "First message"},
            {"id": "msg2", "content": "Second message"},
            {"id": "msg3", "content": "Third message"}
        ]
        
        # Mock _process_message
        with patch.object(self.listener, '_process_message', new_callable=AsyncMock) as mock_process:
            # Call the method
            await self.listener._process_message_batch(messages)
            
            # Verify results
            assert mock_process.call_count == 3  # Should be called for each message
            mock_process.assert_any_call(messages[0])
            mock_process.assert_any_call(messages[1])
            mock_process.assert_any_call(messages[2])
    
    @pytest.mark.asyncio
    async def test_process_message_batch_with_mixed_exceptions(self):
        """Test _process_message_batch with a mix of successful and failing messages."""
        # Create test messages
        messages = [
            {"id": "msg1", "content": "First message"},
            {"id": "msg2", "content": "Second message"},
            {"id": "msg3", "content": "Third message"},
            {"id": "msg4", "content": "Fourth message"}
        ]
        
        # Mock _process_message to succeed for some messages and fail for others
        async def process_side_effect(message):
            if message["id"] in ["msg2", "msg4"]:
                raise Exception(f"Processing error for {message['id']}")
            return {"processed": True, "id": message["id"]}
        
        with patch.object(self.listener, '_process_message', new_callable=AsyncMock) as mock_process, \
             patch('modules.communication.livechat.livechat.src.livechat.logger') as mock_logger:
            
            mock_process.side_effect = process_side_effect
            
            # Call the method
            await self.listener._process_message_batch(messages)
            
            # Verify results
            assert mock_process.call_count == 4  # Should be called for all messages
            for msg in messages:
                mock_process.assert_any_call(msg)
            
            # Verify error logging for failed messages
            assert mock_logger.error.call_count == 2
            mock_logger.error.assert_any_call(f"Error during message processing: Processing error for msg2")
            mock_logger.error.assert_any_call(f"Error during message processing: Processing error for msg4")
    
    @pytest.mark.asyncio
    async def test_process_message_batch_execution_order(self):
        """Test that messages are processed in the order they appear in the list."""
        # Create test messages
        messages = [
            {"id": "msg1", "content": "First message"},
            {"id": "msg2", "content": "Second message"},
            {"id": "msg3", "content": "Third message"}
        ]
        
        # Keep track of processing order
        processed_order = []
        
        async def track_processing_order(message):
            processed_order.append(message["id"])
            return {"processed": True, "id": message["id"]}
        
        # Mock _process_message to track the order
        with patch.object(self.listener, '_process_message', new_callable=AsyncMock) as mock_process:
            mock_process.side_effect = track_processing_order
            
            # Call the method
            await self.listener._process_message_batch(messages)
            
            # Verify results
            assert mock_process.call_count == 3
            # Verify messages were processed in the same order they appear in the list
            assert processed_order == ["msg1", "msg2", "msg3"]
    
    @pytest.mark.asyncio
    async def test_process_message_batch_with_None_message(self):
        """Test _process_message_batch when the message list contains None values."""
        # Create test messages with a None value
        messages = [
            {"id": "msg1", "content": "First message"},
            None,  # This should be handled gracefully
            {"id": "msg3", "content": "Third message"}
        ]
        
        # Mock _process_message
        with patch.object(self.listener, '_process_message', new_callable=AsyncMock) as mock_process:
            # Call the method
            await self.listener._process_message_batch(messages)
            
            # Verify results
            assert mock_process.call_count == 2  # Should be called for non-None messages
            mock_process.assert_any_call(messages[0])
            mock_process.assert_any_call(messages[2])
            
            # Verify it was not called with None
            mock_process.assert_not_called_with(None)
    
    @pytest.mark.asyncio
    async def test_process_message_batch_returns_none(self):
        """Test that _process_message_batch returns None as specified in its signature."""
        # Create test messages
        messages = [
            {"id": "msg1", "content": "Test message"}
        ]
        
        # Mock _process_message
        with patch.object(self.listener, '_process_message', new_callable=AsyncMock) as mock_process:
            # Call the method and store the result
            result = await self.listener._process_message_batch(messages)
            
            # Verify _process_message was called
            mock_process.assert_called_once_with(messages[0])
            
            # Verify _process_message_batch returns None
            assert result is None
    
    @pytest.mark.asyncio
    async def test_process_message_success_no_triggers(self):
        """Test the happy path of processing a message without trigger patterns."""
        # Create test message
        test_message = {
            "id": "msg123",
            "snippet": {
                "displayMessage": "Regular message without triggers"
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
            "message": "Regular message without triggers",
            "timestamp": "2023-01-01T12:00:00"  # Mock timestamp
        }
        
        # Mock all the dependencies
        with patch.object(self.listener, '_extract_message_metadata') as mock_extract, \
             patch.object(self.listener, '_check_trigger_patterns') as mock_check, \
             patch.object(self.listener, '_create_log_entry') as mock_create, \
             patch.object(self.listener, '_log_to_user_file') as mock_log, \
             patch('modules.livechat.src.livechat.datetime') as mock_datetime:
            
            # Configure mocks
            mock_extract.return_value = ("msg123", "Regular message without triggers", "TestUser", "user123", "user")
            mock_check.return_value = False  # No trigger patterns detected
            mock_create.return_value = expected_log
            mock_now = MagicMock()
            mock_now.isoformat.return_value = "2023-01-01T12:00:00"
            mock_datetime.now.return_value = mock_now
            
            # Call the method
            result = await self.listener._process_message(test_message)
            
            # Verify results
            self.assertEqual(result, expected_log)
            mock_extract.assert_called_once_with(test_message)
            mock_check.assert_called_once_with("Regular message without triggers")
            mock_create.assert_called_once_with("msg123", "TestUser", "Regular message without triggers")
            mock_log.assert_called_once_with(test_message)
    
    @pytest.mark.asyncio
    async def test_process_message_trigger_success(self):
        """Test processing a message with successful trigger handling."""
        # Create test message with trigger pattern
        test_message = {
            "id": "msg123",
            "snippet": {
                "displayMessage": "Message with trigger ✊✋🖐️"
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
            "message": "Message with trigger ✊✋🖐️",
            "timestamp": "2023-01-01T12:00:00"  # Mock timestamp
        }
        
        # Mock all the dependencies
        with patch.object(self.listener, '_extract_message_metadata') as mock_extract, \
             patch.object(self.listener, '_check_trigger_patterns') as mock_check, \
             patch.object(self.listener, '_handle_emoji_trigger', new_callable=AsyncMock) as mock_handle, \
             patch.object(self.listener, '_create_log_entry') as mock_create, \
             patch.object(self.listener, '_log_to_user_file') as mock_log, \
             patch('modules.livechat.src.livechat.datetime') as mock_datetime:
            
            # Configure mocks
            mock_extract.return_value = ("msg123", "Message with trigger ✊✋🖐️", "TestUser", "user123", "user")
            mock_check.return_value = True  # Trigger patterns detected
            mock_handle.return_value = True  # Trigger handling was successful
            mock_create.return_value = expected_log
            mock_now = MagicMock()
            mock_now.isoformat.return_value = "2023-01-01T12:00:00"
            mock_datetime.now.return_value = mock_now
            
            # Call the method
            result = await self.listener._process_message(test_message)
            
            # Verify results
            self.assertEqual(result, expected_log)
            mock_extract.assert_called_once_with(test_message)
            mock_check.assert_called_once_with("Message with trigger ✊✋🖐️")
            mock_handle.assert_called_once_with("TestUser", "user123", "Message with trigger ✊✋🖐️")
            mock_create.assert_called_once_with("msg123", "TestUser", "Message with trigger ✊✋🖐️")
            mock_log.assert_called_once_with(test_message)
    
    @pytest.mark.asyncio
    async def test_process_message_log_entry_creation(self):
        """Test specifically focuses on the creation and return of a log entry."""
        # Create test message
        test_message = {
            "id": "msg123",
            "snippet": {
                "displayMessage": "Test message"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "user123"
            }
        }
        
        # Mock _extract_message_metadata, _check_trigger_patterns and _create_log_entry
        with patch.object(self.listener, '_extract_message_metadata') as mock_extract, \
             patch.object(self.listener, '_check_trigger_patterns') as mock_check, \
             patch.object(self.listener, '_create_log_entry') as mock_create, \
             patch.object(self.listener, '_log_to_user_file') as mock_log:
            
            # Configure mocks
            mock_extract.return_value = ("msg123", "Test message", "TestUser", "user123", "user")
            mock_check.return_value = False  # No trigger patterns
            
            # Create a custom log entry that we can specifically check for
            custom_log_entry = {
                "id": "msg123",
                "author": "TestUser",
                "message": "Test message",
                "timestamp": "2023-01-01T12:00:00",
                "custom_field": "This field is used to verify the exact log entry is returned"
            }
            mock_create.return_value = custom_log_entry
            
            # Call the method
            result = await self.listener._process_message(test_message)
            
            # Verify that the exact log entry created by _create_log_entry is returned
            self.assertIs(result, custom_log_entry)  # Check identity, not just equality
            mock_create.assert_called_once_with("msg123", "TestUser", "Test message")
            mock_log.assert_called_once_with(test_message)
    
    @pytest.mark.asyncio
    async def test_process_message_exception_handling_and_minimal_log(self):
        """Test the exception handling path that creates a minimal error log entry."""
        # Create test message
        test_message = {
            "id": "msg123",
            "snippet": {
                "displayMessage": "Test message"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "user123"
            }
        }
        
        # Setup to simulate a generic exception during processing
        general_exception = Exception("General processing error")
        
        # Mock dependencies and force exception
        with patch.object(self.listener, '_extract_message_metadata') as mock_extract, \
             patch('modules.communication.livechat.livechat.src.livechat.logger') as mock_logger, \
             patch('modules.livechat.src.livechat.datetime') as mock_datetime:
            
            # Configure mocks to trigger the exception path
            mock_extract.side_effect = general_exception
            
            # Mock datetime.now() to get a predictable timestamp
            mock_now = MagicMock()
            mock_now.isoformat.return_value = "2023-01-01T12:00:00"
            mock_datetime.now.return_value = mock_now
            
            # Call the method
            result = await self.listener._process_message(test_message)
            
            # Verify the error is logged
            mock_logger.error.assert_called_once_with(f"Error processing message: {str(general_exception)}")
            
            # Verify a minimal log entry with error info is returned
            self.assertIn("error", result)
            self.assertEqual(result["error"], str(general_exception))
            self.assertEqual(result["timestamp"], "2023-01-01T12:00:00")
    
    @pytest.mark.asyncio
    async def test_process_message_log_entry_specific_format_lines_292_319(self):
        """Test that the log entry format created in lines 292-319 is correct."""
        # Create test message
        test_message = {
            "id": "msg123",
            "snippet": {
                "displayMessage": "Test message for log entry format"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "user123"
            }
        }
        
        # Mock the necessary methods but use the actual _create_log_entry to test its integration
        with patch.object(self.listener, '_extract_message_metadata') as mock_extract, \
             patch.object(self.listener, '_check_trigger_patterns') as mock_check, \
             patch.object(self.listener, '_log_to_user_file') as mock_log, \
             patch('modules.livechat.src.livechat.datetime') as mock_datetime:
            
            # Configure mocks
            mock_extract.return_value = ("msg123", "Test message for log entry format", "TestUser", "user123", "user")
            mock_check.return_value = False  # No trigger patterns
            
            # Mock datetime for consistent timestamp
            mock_now = MagicMock()
            mock_now.isoformat.return_value = "2023-01-01T12:00:00"
            mock_datetime.now.return_value = mock_now
            
            # Call the method but don't mock _create_log_entry to test the actual implementation
            result = await self.listener._process_message(test_message)
            
            # Verify the log entry format is correct
            self.assertEqual(result["id"], "msg123")
            self.assertEqual(result["author"], "TestUser")
            self.assertEqual(result["message"], "Test message for log entry format")
            self.assertEqual(result["timestamp"], "2023-01-01T12:00:00")
            
            # Verify logging was attempted
            mock_log.assert_called_once_with(test_message)
    
    @pytest.mark.asyncio
    async def test_process_message_logging_exception_details_lines_292_319(self):
        """Test specific exception handling for _log_to_user_file failures (lines 292-319)."""
        # Create test message
        test_message = {
            "id": "msg123",
            "snippet": {
                "displayMessage": "Test message for log exception handling"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "user123"
            }
        }
        
        # Create specific exception for logging
        log_exception = PermissionError("Cannot write to log file")
        
        # Mock methods
        with patch.object(self.listener, '_extract_message_metadata') as mock_extract, \
             patch.object(self.listener, '_check_trigger_patterns') as mock_check, \
             patch.object(self.listener, '_create_log_entry') as mock_create, \
             patch.object(self.listener, '_log_to_user_file') as mock_log, \
             patch('modules.communication.livechat.livechat.src.livechat.logger') as mock_logger:
            
            # Configure mocks
            mock_extract.return_value = ("msg123", "Test message for log exception handling", "TestUser", "user123", "user")
            mock_check.return_value = False
            test_log_entry = {"id": "msg123", "author": "TestUser", "message": "Test message for log exception handling"}
            mock_create.return_value = test_log_entry
            mock_log.side_effect = log_exception  # Simulate logging failure
            
            # Call the method
            result = await self.listener._process_message(test_message)
            
            # Verify that despite logging failure, processing continues and returns the log entry
            self.assertEqual(result, test_log_entry)
            
            # Verify that the exception was logged with the specific error message
            mock_logger.error.assert_called_once_with(f"Failed to log message: {log_exception}")
    
    @pytest.mark.asyncio
    async def test_process_message_create_log_entry_called_with_correct_params_lines_292_319(self):
        """Test that _create_log_entry is called with the correct parameters extracted from the message."""
        # Create test message
        test_message = {
            "id": "unique_msg_id_123",
            "snippet": {
                "displayMessage": "Test message content for parameter verification"
            },
            "authorDetails": {
                "displayName": "TestAuthor",
                "channelId": "channel_123"
            }
        }
        
        # Mock methods
        with patch.object(self.listener, '_extract_message_metadata') as mock_extract, \
             patch.object(self.listener, '_check_trigger_patterns') as mock_check, \
             patch.object(self.listener, '_create_log_entry') as mock_create, \
             patch.object(self.listener, '_log_to_user_file'):
            
            # Configure mocks
            expected_msg_id = "unique_msg_id_123"
            expected_msg_content = "Test message content for parameter verification"
            expected_author = "TestAuthor"
            expected_channel = "channel_123"
            
            mock_extract.return_value = (expected_msg_id, expected_msg_content, expected_author, expected_channel, "user")
            mock_check.return_value = False
            mock_create.return_value = {"dummy": "log entry"}
            
            # Call the method
            await self.listener._process_message(test_message)
            
            # Verify _create_log_entry was called with exactly the right parameters
            mock_create.assert_called_once_with(
                expected_msg_id, 
                expected_author, 
                expected_msg_content
            )
    
    @pytest.mark.asyncio
    async def test_process_message_sequential_execution_lines_292_319(self):
        """Test the sequential execution flow in lines 292-319 of _process_message."""
        # Create test message
        test_message = {
            "id": "msg123",
            "snippet": {
                "displayMessage": "Test sequential execution"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "user123"
            }
        }
        
        # Mock the method calls to track execution order
        with patch.object(self.listener, '_extract_message_metadata') as mock_extract, \
             patch.object(self.listener, '_check_trigger_patterns') as mock_check, \
             patch.object(self.listener, '_create_log_entry') as mock_create, \
             patch.object(self.listener, '_log_to_user_file') as mock_log:
            
            # Configure mocks
            mock_extract.return_value = ("msg123", "Test sequential execution", "TestUser", "user123", "user")
            mock_check.return_value = False
            test_log_entry = {"test": "log entry"}
            mock_create.return_value = test_log_entry
            
            # Use a list to track execution order
            execution_order = []
            
            # Override mock side effects to track order
            def track_create(*args, **kwargs):
                execution_order.append('create_log_entry')
                return test_log_entry
            
            def track_log(*args, **kwargs):
                execution_order.append('log_to_user_file')
            
            mock_create.side_effect = track_create
            mock_log.side_effect = track_log
            
            # Call the method
            result = await self.listener._process_message(test_message)
            
            # Verify the execution order matches the sequential flow in lines 292-319
            self.assertEqual(execution_order, ['create_log_entry', 'log_to_user_file'])
            
            # Verify the result is the log entry
            self.assertEqual(result, test_log_entry) 