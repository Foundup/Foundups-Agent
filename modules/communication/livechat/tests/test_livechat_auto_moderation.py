"""
Test suite for LiveChat Auto-Moderation functionality.

This module tests the auto-moderation system that automatically detects
banned phrases and applies 10-second timeouts to users.

WSP Compliance: Tests for auto-moderation functionality integrated into
the LiveChat module as per WSP 3 (Enterprise Domain Architecture).
"""

import pytest
import unittest.mock as mock
from unittest.mock import Mock, patch, MagicMock
import time
from datetime import datetime, timedelta
import googleapiclient.errors

# Import the modules under test
from modules.communication.livechat.src.livechat import LiveChatListener
from modules.communication.livechat.src.auto_moderator import AutoModerator


class TestAutoModerator:
    """Test suite for the AutoModerator class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_youtube = Mock()
        self.auto_moderator = AutoModerator(self.mock_youtube)
        
    def test_auto_moderator_initialization(self):
        """Test AutoModerator initializes with correct default values."""
        assert self.auto_moderator.youtube == self.mock_youtube
        assert self.auto_moderator.timeout_duration == 10
        assert self.auto_moderator.timeout_cooldown == 60
        assert isinstance(self.auto_moderator.banned_phrases, set)
        assert isinstance(self.auto_moderator.recent_timeouts, dict)
        
        # Check that banned phrases are loaded
        expected_phrases = {
            "maga 2028", "love trump", "trump is jesus", "trump 2028",
            "make america great again 2028", "trump forever", "god emperor trump"
        }
        assert expected_phrases.issubset(self.auto_moderator.banned_phrases)
        
    def test_contains_banned_phrase_detection(self):
        """Test detection of banned phrases in messages."""
        test_cases = [
            ("MAGA 2028 is coming!", True),
            ("I Love Trump so much!", True),
            ("Trump is Jesus Christ!", True),
            ("Make America Great Again 2028", True),
            ("trump forever and ever", True),
            ("This is a normal message", False),
            ("I love pizza", False),
            ("Trump news today", False),  # Should not trigger
            ("MAGA hat", False),  # Should not trigger (not the full phrase)
        ]
        
        for message, expected in test_cases:
            result = self.auto_moderator.contains_banned_phrase(message)
            assert result == expected, f"Message '{message}' should return {expected}"
            
    def test_contains_banned_phrase_case_insensitive(self):
        """Test that banned phrase detection is case-insensitive."""
        test_messages = [
            "maga 2028",
            "MAGA 2028", 
            "Maga 2028",
            "MaGa 2028",
            "love TRUMP",
            "LOVE trump",
            "Love Trump"
        ]
        
        for message in test_messages:
            assert self.auto_moderator.contains_banned_phrase(message), \
                f"Message '{message}' should be detected as banned"
                
    def test_should_timeout_user_cooldown_logic(self):
        """Test the cooldown logic for user timeouts."""
        user_id = "test_user_123"
        
        # First timeout should be allowed
        assert self.auto_moderator.should_timeout_user(user_id) == True
        
        # Record the timeout
        self.auto_moderator.recent_timeouts[user_id] = time.time()
        
        # Immediate retry should be blocked
        assert self.auto_moderator.should_timeout_user(user_id) == False
        
        # Simulate time passing (less than cooldown)
        with patch('time.time', return_value=time.time() + 30):  # 30 seconds later
            assert self.auto_moderator.should_timeout_user(user_id) == False
            
        # Simulate time passing (more than cooldown)
        with patch('time.time', return_value=time.time() + 70):  # 70 seconds later
            assert self.auto_moderator.should_timeout_user(user_id) == True
            
    def test_timeout_user_success(self):
        """Test successful user timeout via YouTube API."""
        user_id = "test_user_123"
        chat_id = "test_chat_456"
        
        # Mock successful API response
        mock_response = {"id": "ban_id_123"}
        self.mock_youtube.liveChatBans().insert().execute.return_value = mock_response
        
        result = self.auto_moderator.timeout_user(user_id, chat_id)
        
        assert result == True
        
        # Verify API was called correctly
        self.mock_youtube.liveChatBans().insert.assert_called_once()
        call_args = self.mock_youtube.liveChatBans().insert.call_args
        
        # Check the request body
        body = call_args[1]['body']
        assert body['snippet']['liveChatId'] == chat_id
        assert body['snippet']['type'] == 'temporary'
        assert body['snippet']['bannedUserDetails']['channelId'] == user_id
        assert body['snippet']['banDurationSeconds'] == 10
        
    def test_timeout_user_api_error(self):
        """Test handling of YouTube API errors during timeout."""
        user_id = "test_user_123"
        chat_id = "test_chat_456"
        
        # Mock API error
        error = googleapiclient.errors.HttpError(
            resp=Mock(status=403), 
            content=b'{"error": {"message": "Forbidden"}}'
        )
        self.mock_youtube.liveChatBans().insert().execute.side_effect = error
        
        result = self.auto_moderator.timeout_user(user_id, chat_id)
        
        assert result == False
        
    def test_process_message_with_banned_phrase(self):
        """Test processing a message containing banned phrases."""
        message = {
            'authorDetails': {'channelId': 'user123'},
            'snippet': {'displayMessage': 'MAGA 2028 forever!'}
        }
        chat_id = "test_chat_456"
        
        with patch.object(self.auto_moderator, 'should_timeout_user', return_value=True), \
             patch.object(self.auto_moderator, 'timeout_user', return_value=True) as mock_timeout:
            
            result = self.auto_moderator.process_message(message, chat_id)
            
            assert result == True  # Message was moderated
            mock_timeout.assert_called_once_with('user123', chat_id)
            
    def test_process_message_without_banned_phrase(self):
        """Test processing a clean message."""
        message = {
            'authorDetails': {'channelId': 'user123'},
            'snippet': {'displayMessage': 'Hello everyone!'}
        }
        chat_id = "test_chat_456"
        
        result = self.auto_moderator.process_message(message, chat_id)
        
        assert result == False  # Message was not moderated
        
    def test_process_message_user_on_cooldown(self):
        """Test processing banned phrase from user on cooldown."""
        message = {
            'authorDetails': {'channelId': 'user123'},
            'snippet': {'displayMessage': 'MAGA 2028 forever!'}
        }
        chat_id = "test_chat_456"
        
        with patch.object(self.auto_moderator, 'should_timeout_user', return_value=False):
            result = self.auto_moderator.process_message(message, chat_id)
            
            assert result == False  # Message detected but user not timed out due to cooldown
            
    def test_get_stats(self):
        """Test getting moderation statistics."""
        # Add some test data
        self.auto_moderator.recent_timeouts = {
            'user1': time.time() - 30,
            'user2': time.time() - 120
        }
        
        stats = self.auto_moderator.get_stats()
        
        assert 'timeout_duration' in stats
        assert 'timeout_cooldown' in stats
        assert 'banned_phrases_count' in stats
        assert 'recent_timeouts_count' in stats
        assert 'banned_phrases' in stats
        
        assert stats['timeout_duration'] == 10
        assert stats['timeout_cooldown'] == 60
        assert stats['recent_timeouts_count'] == 2
        assert len(stats['banned_phrases']) > 0


class TestLiveChatAutoModerationIntegration:
    """Test suite for auto-moderation integration with LiveChatListener."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_youtube = Mock()
        self.mock_banter_engine = Mock()
        self.mock_llm_bypass = Mock()
        
        # Create LiveChatListener with mocked dependencies
        with patch('modules.communication.livechat.src.livechat.BanterEngine'), \
             patch('modules.communication.livechat.src.livechat.LLMBypassEngine'), \
             patch('modules.communication.livechat.src.livechat.AutoModerator') as mock_auto_mod:
            
            self.listener = LiveChatListener(
                youtube_service=self.mock_youtube,
                video_id="test_video",
                chat_id="test_chat"
            )
            self.mock_auto_moderator = mock_auto_mod.return_value
            
    def test_auto_moderator_initialization_in_listener(self):
        """Test that AutoModerator is properly initialized in LiveChatListener."""
        # Verify AutoModerator was created with the YouTube service
        assert hasattr(self.listener, 'auto_moderator')
        
    def test_message_processing_with_moderation_check(self):
        """Test that message processing includes auto-moderation check."""
        # Create a test message with banned content
        test_message = {
            'id': 'msg123',
            'snippet': {
                'displayMessage': 'MAGA 2028 is coming!',
                'publishedAt': '2024-01-01T12:00:00Z'
            },
            'authorDetails': {
                'displayName': 'TestUser',
                'channelId': 'user123'
            }
        }
        
        # Mock auto-moderator to return True (message was moderated)
        self.mock_auto_moderator.process_message.return_value = True
        
        # Mock other dependencies
        with patch.object(self.listener, '_extract_message_metadata') as mock_extract, \
             patch.object(self.listener, '_is_bot_message', return_value=False), \
             patch.object(self.listener, '_is_rate_limited', return_value=False):
            
            mock_extract.return_value = ('msg123', 'MAGA 2028 is coming!', 'TestUser', 'user123')
            
            # Process the message
            result = self.listener._process_message(test_message)
            
            # Verify auto-moderator was called
            self.mock_auto_moderator.process_message.assert_called_once_with(
                test_message, self.listener.chat_id
            )
            
            # Message should be processed but not trigger other responses due to moderation
            assert result is not None
            
    def test_message_processing_without_moderation(self):
        """Test message processing when no moderation is needed."""
        # Create a test message with clean content
        test_message = {
            'id': 'msg123',
            'snippet': {
                'displayMessage': 'Hello everyone!',
                'publishedAt': '2024-01-01T12:00:00Z'
            },
            'authorDetails': {
                'displayName': 'TestUser',
                'channelId': 'user123'
            }
        }
        
        # Mock auto-moderator to return False (no moderation needed)
        self.mock_auto_moderator.process_message.return_value = False
        
        # Mock other dependencies
        with patch.object(self.listener, '_extract_message_metadata') as mock_extract, \
             patch.object(self.listener, '_is_bot_message', return_value=False), \
             patch.object(self.listener, '_is_rate_limited', return_value=False), \
             patch.object(self.listener, '_detect_emoji_trigger', return_value=None), \
             patch.object(self.listener, '_create_log_entry') as mock_log:
            
            mock_extract.return_value = ('msg123', 'Hello everyone!', 'TestUser', 'user123')
            mock_log.return_value = {'test': 'log_entry'}
            
            # Process the message
            result = self.listener._process_message(test_message)
            
            # Verify auto-moderator was called
            self.mock_auto_moderator.process_message.assert_called_once_with(
                test_message, self.listener.chat_id
            )
            
            # Message should continue normal processing
            assert result is not None
            
    def test_get_moderation_stats_integration(self):
        """Test getting moderation statistics through LiveChatListener."""
        # Mock stats from auto-moderator
        mock_stats = {
            'timeout_duration': 10,
            'timeout_cooldown': 60,
            'banned_phrases_count': 7,
            'recent_timeouts_count': 3
        }
        self.mock_auto_moderator.get_stats.return_value = mock_stats
        
        # Get stats through listener
        stats = self.listener.get_moderation_stats()
        
        assert stats == mock_stats
        self.mock_auto_moderator.get_stats.assert_called_once()
        
    def test_add_banned_phrase_integration(self):
        """Test adding banned phrases through LiveChatListener."""
        new_phrase = "test banned phrase"
        
        # Add phrase through listener
        self.listener.add_banned_phrase(new_phrase)
        
        # Verify it was passed to auto-moderator
        self.mock_auto_moderator.add_banned_phrase.assert_called_once_with(new_phrase)
        
    def test_remove_banned_phrase_integration(self):
        """Test removing banned phrases through LiveChatListener."""
        phrase_to_remove = "maga 2028"
        
        # Remove phrase through listener
        result = self.listener.remove_banned_phrase(phrase_to_remove)
        
        # Verify it was passed to auto-moderator
        self.mock_auto_moderator.remove_banned_phrase.assert_called_once_with(phrase_to_remove)


class TestAutoModerationErrorHandling:
    """Test suite for auto-moderation error handling scenarios."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_youtube = Mock()
        self.auto_moderator = AutoModerator(self.mock_youtube)
        
    def test_malformed_message_handling(self):
        """Test handling of malformed message objects."""
        malformed_messages = [
            {},  # Empty message
            {'snippet': {}},  # Missing authorDetails
            {'authorDetails': {}},  # Missing snippet
            {'authorDetails': {'channelId': 'user123'}},  # Missing displayMessage
            {'snippet': {'displayMessage': 'test'}},  # Missing channelId
        ]
        
        for message in malformed_messages:
            # Should not raise exception and should return False
            result = self.auto_moderator.process_message(message, "test_chat")
            assert result == False
            
    def test_youtube_api_quota_exceeded(self):
        """Test handling of YouTube API quota exceeded errors."""
        user_id = "test_user_123"
        chat_id = "test_chat_456"
        
        # Mock quota exceeded error
        error = googleapiclient.errors.HttpError(
            resp=Mock(status=403), 
            content=b'{"error": {"message": "quotaExceeded"}}'
        )
        self.mock_youtube.liveChatBans().insert().execute.side_effect = error
        
        result = self.auto_moderator.timeout_user(user_id, chat_id)
        
        assert result == False
        
    def test_youtube_api_permission_denied(self):
        """Test handling of YouTube API permission denied errors."""
        user_id = "test_user_123"
        chat_id = "test_chat_456"
        
        # Mock permission denied error
        error = googleapiclient.errors.HttpError(
            resp=Mock(status=403), 
            content=b'{"error": {"message": "Insufficient Permission"}}'
        )
        self.mock_youtube.liveChatBans().insert().execute.side_effect = error
        
        result = self.auto_moderator.timeout_user(user_id, chat_id)
        
        assert result == False
        
    def test_network_timeout_handling(self):
        """Test handling of network timeout errors."""
        user_id = "test_user_123"
        chat_id = "test_chat_456"
        
        # Mock network timeout
        self.mock_youtube.liveChatBans().insert().execute.side_effect = Exception("Connection timeout")
        
        result = self.auto_moderator.timeout_user(user_id, chat_id)
        
        assert result == False


if __name__ == '__main__':
    pytest.main([__file__]) 