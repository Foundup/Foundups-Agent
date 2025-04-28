"""
Unit tests for the emoji trigger functionality of LiveChatListener class
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
from modules.livechat.src.livechat import LiveChatListener
from modules.banter_engine import BanterEngine

class TestLiveChatListenerEmojiTriggers(unittest.TestCase):
    """Test cases for emoji trigger functionality of LiveChatListener."""
    
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
        
    def test_check_trigger_patterns_exact_match(self):
        """Test detection of exact emoji pattern matches."""
        # Set trigger emojis
        self.listener.trigger_emojis = ["✊", "✋", "🖐️"]
        
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
        """Test that non-matching messages are correctly identified."""
        # Set trigger emojis
        self.listener.trigger_emojis = ["✊", "✋", "🖐️"]
        
        # Test messages with no matching emoji sequence
        test_cases = [
            "Message with no emojis",
            "Message with different emojis 😀😁😂",
            "Partial sequence ✊✋ only",
            "Reversed sequence 🖐️✋✊"
        ]
        
        # Verify all test cases return False
        for test_case in test_cases:
            self.assertFalse(self.listener._check_trigger_patterns(test_case))
    
    def test_check_trigger_patterns_with_whitespace(self):
        """Test pattern detection with whitespace in the message."""
        # Set trigger emojis
        self.listener.trigger_emojis = ["✊", "✋", "🖐️"]
        
        # Test messages with whitespace around/between emojis
        # Current implementation requires exact sequence with no whitespace between emojis
        test_cases = [
            "Message with spaced emojis ✊ ✋ 🖐️", # Should not match (spaces between)
            "Message with newlines ✊\n✋\n🖐️"     # Should not match (newlines between)
        ]
        
        # Verify all test cases return False (current implementation requires exact sequence)
        for test_case in test_cases:
            self.assertFalse(self.listener._check_trigger_patterns(test_case))
    
    def test_check_trigger_patterns_different_sequences(self):
        """Test different valid emoji sequences."""
        # Test different sequences
        test_sequences = [
            ["🎮", "🎲", "🎯"],  # Gaming emojis
            ["🌟", "⭐", "✨"],   # Star emojis
            ["🐶", "🐱", "🐭"]    # Animal emojis
        ]
        
        # For each sequence, set it as the trigger and test a matching message
        for sequence in test_sequences:
            self.listener.trigger_emojis = sequence
            joined_sequence = "".join(sequence)
            test_message = f"Message with sequence {joined_sequence}"
            
            # Should match
            self.assertTrue(self.listener._check_trigger_patterns(test_message))
    
    @pytest.mark.asyncio
    async def test_handle_emoji_trigger_success(self):
        """Test successful handling of emoji triggers."""
        # Mock rate limiting to return False (user not rate limited)
        with patch.object(self.listener, '_is_rate_limited', return_value=False), \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch.object(self.listener, '_update_trigger_time') as mock_update:
            
            # Configure send_chat_message to succeed
            mock_send.return_value = True
            
            # Call the method
            result = await self.listener._handle_emoji_trigger(
                author_name="TestUser",
                author_id="user123",
                message_text="✊✋🖐️ Hello!"
            )
            
            # Verify results
            self.assertTrue(result)
            mock_send.assert_called_once_with("Hello there!")  # Default from mock_banter_engine
            mock_update.assert_called_once_with("user123")
    
    @pytest.mark.asyncio
    async def test_handle_emoji_trigger_empty_banter_response(self):
        """Test handling of empty response from banter engine."""
        # Mock banter engine to return an empty string
        self.listener.banter_engine.get_random_banter.return_value = ""
        
        # Mock the is_rate_limited method to return False
        with patch.object(self.listener, '_is_rate_limited', return_value=False), \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch.object(self.listener, '_update_trigger_time') as mock_update:
            
            # Configure send_chat_message to succeed
            mock_send.return_value = True
            
            # Call the method
            result = await self.listener._handle_emoji_trigger(
                author_name="TestUser",
                author_id="user123",
                message_text="✊✋🖐️ Hello!"
            )
            
            # Verify results
            self.assertTrue(result)
            # Should use fallback message due to empty response
            mock_send.assert_called_once()
            self.assertIn("Hey there", mock_send.call_args[0][0])  # Should contain fallback text
            mock_update.assert_called_once_with("user123")
    
    @pytest.mark.asyncio
    async def test_handle_emoji_trigger_invalid_banter_not_string(self):
        """Test handling when banter engine returns a non-string response."""
        # Mock banter engine to return a non-string value
        self.listener.banter_engine.get_random_banter.return_value = 123  # Return a number instead of string
        
        # Mock the is_rate_limited method to return False
        with patch.object(self.listener, '_is_rate_limited', return_value=False), \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch.object(self.listener, '_update_trigger_time') as mock_update:
            
            # Configure send_chat_message to succeed
            mock_send.return_value = True
            
            # Call the method
            result = await self.listener._handle_emoji_trigger(
                author_name="TestUser",
                author_id="user123",
                message_text="✊✋🖐️ Hello!"
            )
            
            # Verify results
            self.assertTrue(result)
            # Should use fallback message due to invalid type
            mock_send.assert_called_once()
            self.assertIn("Hey there", mock_send.call_args[0][0])  # Should contain fallback text
            mock_update.assert_called_once_with("user123")
    
    @pytest.mark.asyncio
    async def test_handle_emoji_trigger_only_whitespace_response(self):
        """Test handling when banter engine returns only whitespace."""
        # Mock banter engine to return only whitespace
        self.listener.banter_engine.get_random_banter.return_value = "   \n\t   "
        
        # Mock the is_rate_limited method to return False
        with patch.object(self.listener, '_is_rate_limited', return_value=False), \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch.object(self.listener, '_update_trigger_time') as mock_update:
            
            # Configure send_chat_message to succeed
            mock_send.return_value = True
            
            # Call the method
            result = await self.listener._handle_emoji_trigger(
                author_name="TestUser",
                author_id="user123",
                message_text="✊✋🖐️ Hello!"
            )
            
            # Verify results
            self.assertTrue(result)
            # Should use fallback message due to whitespace-only response
            mock_send.assert_called_once()
            self.assertIn("Hey there", mock_send.call_args[0][0])  # Should contain fallback text
            mock_update.assert_called_once_with("user123")
    
    @pytest.mark.asyncio
    async def test_handle_emoji_trigger_banter_exception(self):
        """Test handling when banter engine raises an exception."""
        # Mock banter engine to raise an exception
        self.listener.banter_engine.get_random_banter.side_effect = Exception("Banter engine error")
        
        # Mock the is_rate_limited method to return False
        with patch.object(self.listener, '_is_rate_limited', return_value=False), \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send:
            
            # Call the method
            result = await self.listener._handle_emoji_trigger(
                author_name="TestUser",
                author_id="user123",
                message_text="✊✋🖐️ Hello!"
            )
            
            # Verify results
            self.assertFalse(result)  # Should return False on exception
            mock_send.assert_not_called()  # Should not attempt to send 
    
    @pytest.mark.asyncio
    async def test_handle_emoji_trigger_rate_limited_user(self):
        """Test handling of emoji triggers when user is rate limited."""
        # Mock _is_rate_limited to return True (user is rate limited)
        with patch.object(self.listener, '_is_rate_limited', return_value=True), \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch.object(self.listener, '_update_trigger_time') as mock_update:
            
            # Call the method
            result = await self.listener._handle_emoji_trigger(
                author_name="RateLimitedUser",
                author_id="limited123",
                message_text="✊✋🖐️ Hello!"
            )
            
            # Verify results
            self.assertFalse(result)  # Should return False when rate limited
            mock_send.assert_not_called()  # Should not attempt to send message
            mock_update.assert_not_called()  # Should not update trigger time
    
    @pytest.mark.asyncio
    async def test_handle_emoji_trigger_send_failure(self):
        """Test handling of emoji triggers when send_chat_message fails."""
        # Mock dependencies
        with patch.object(self.listener, '_is_rate_limited', return_value=False), \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch.object(self.listener, '_update_trigger_time') as mock_update:
            
            # Configure send_chat_message to fail
            mock_send.return_value = False
            
            # Call the method
            result = await self.listener._handle_emoji_trigger(
                author_name="TestUser",
                author_id="user123",
                message_text="✊✋🖐️ Hello!"
            )
            
            # Verify results
            self.assertFalse(result)  # Should return False when sending fails
            mock_send.assert_called_once_with("Hello there!")  # Should attempt to send
            mock_update.assert_not_called()  # Should not update trigger time on failure
    
    @pytest.mark.asyncio
    async def test_handle_emoji_trigger_fallback_response_emoji(self):
        """Test that fallback response includes the required emoji."""
        # Mock banter engine to return None
        self.listener.banter_engine.get_random_banter.return_value = None
        
        # Mock dependencies
        with patch.object(self.listener, '_is_rate_limited', return_value=False), \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch.object(self.listener, '_update_trigger_time') as mock_update:
            
            # Configure send_chat_message to succeed
            mock_send.return_value = True
            
            # Call the method
            result = await self.listener._handle_emoji_trigger(
                author_name="TestUser",
                author_id="user123",
                message_text="✊✋🖐️ Hello!"
            )
            
            # Verify results
            self.assertTrue(result)
            # Should use fallback message with the required emoji (窓)
            mock_send.assert_called_once()
            self.assertIn("Hey there", mock_send.call_args[0][0])  # Should contain fallback text
            self.assertIn("窓", mock_send.call_args[0][0])  # Should contain the specific emoji
            mock_update.assert_called_once_with("user123")
    
    @pytest.mark.asyncio
    async def test_handle_emoji_trigger_logging_calls(self):
        """Test that _handle_emoji_trigger makes appropriate logging calls."""
        # Mock logger to track calls
        with patch('modules.livechat.src.livechat.logger') as mock_logger, \
             patch.object(self.listener, '_is_rate_limited', return_value=False), \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch.object(self.listener, '_update_trigger_time'):
            
            # Configure send_chat_message to succeed
            mock_send.return_value = True
            
            # Setup test data
            author_name = "TestUser"
            author_id = "user123"
            message_text = "✊✋🖐️ Hello!"
            banter_response = "Hello there!"
            
            # Call the method
            await self.listener._handle_emoji_trigger(
                author_name=author_name,
                author_id=author_id,
                message_text=message_text
            )
            
            # Verify logging calls
            mock_logger.info.assert_any_call(f"Emoji sequence detected in message from {author_name}: {message_text}")
            mock_logger.debug.assert_any_call(f"Generated banter response for {author_name}: {banter_response}")
            mock_logger.info.assert_any_call(f"Successfully queued banter response for {author_name}")
    
    @pytest.mark.asyncio
    async def test_handle_emoji_trigger_logging_failure(self):
        """Test that _handle_emoji_trigger logs errors when send_chat_message fails."""
        # Mock logger to track calls
        with patch('modules.livechat.src.livechat.logger') as mock_logger, \
             patch.object(self.listener, '_is_rate_limited', return_value=False), \
             patch.object(self.listener, 'send_chat_message', new_callable=AsyncMock) as mock_send:
            
            # Configure send_chat_message to fail
            mock_send.return_value = False
            
            # Setup test data
            author_name = "TestUser"
            author_id = "user123"
            message_text = "✊✋🖐️ Hello!"
            
            # Call the method
            await self.listener._handle_emoji_trigger(
                author_name=author_name,
                author_id=author_id,
                message_text=message_text
            )
            
            # Verify logging calls
            mock_logger.info.assert_any_call(f"Emoji sequence detected in message from {author_name}: {message_text}")
            mock_logger.error.assert_any_call(f"Failed to queue banter response for {author_name}") 