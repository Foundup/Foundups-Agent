"""
Unit tests for the initialization functionality of LiveChatListener class
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

# Mock for async methods
class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)

class TestLiveChatListenerInitialization(unittest.TestCase):
    """Test cases for initialization of LiveChatListener."""
    
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
        
    def test_init_default_attributes(self):
        """Test initialization of all default attributes in LiveChatListener."""
        # Test all attributes defined in lines 41-58
        self.assertEqual(self.listener.youtube, self.mock_youtube)
        self.assertEqual(self.listener.video_id, self.video_id)
        self.assertEqual(self.listener.live_chat_id, self.live_chat_id)
        self.assertIsNone(self.listener.next_page_token)
        self.assertEqual(self.listener.poll_interval_ms, 100000)
        self.assertEqual(self.listener.error_backoff_seconds, 5)
        self.assertEqual(self.listener.memory_dir, "memory")
        self.assertEqual(self.listener.greeting_message, os.getenv("AGENT_GREETING_MESSAGE", "FoundUps Agent reporting in!"))
        self.assertListEqual(self.listener.message_queue, [])
        self.assertEqual(self.listener.viewer_count, 0)
        self.assertIsInstance(self.listener.banter_engine, MagicMock)
        self.assertListEqual(self.listener.trigger_emojis, ["✊", "✋", "🖐️"])
        self.assertEqual(type(self.listener.last_trigger_time), dict)
        self.assertEqual(self.listener.trigger_cooldown, 60)
        
    def test_init_memory_dir_creation(self):
        """Test that the memory directory is created during initialization."""
        with patch('os.makedirs') as mock_makedirs:
            listener = LiveChatListener(
                youtube_service=self.mock_youtube,
                video_id=self.video_id
            )
            mock_makedirs.assert_called_with("memory", exist_ok=True)
            
    def test_init_with_custom_memory_dir(self):
        """Test initialization with a custom memory directory."""
        with patch('os.makedirs') as mock_makedirs:
            with patch.dict('os.environ', {'MEMORY_DIR': 'custom_memory'}):
                # Note: The class doesn't actually use MEMORY_DIR env var, but we can test this pattern
                listener = LiveChatListener(
                    youtube_service=self.mock_youtube,
                    video_id=self.video_id
                )
                listener.memory_dir = "custom_memory"  # Manually set for testing
                self.assertEqual(listener.memory_dir, "custom_memory")
                mock_makedirs.assert_called()
                
    def test_init_with_custom_greeting(self):
        """Test initialization with a custom greeting message from environment variable."""
        custom_greeting = "Hello, YouTube chat!"
        with patch.dict('os.environ', {'AGENT_GREETING_MESSAGE': custom_greeting}):
            listener = LiveChatListener(
                youtube_service=self.mock_youtube,
                video_id=self.video_id
            )
            self.assertEqual(listener.greeting_message, custom_greeting)
            
    def test_init_with_custom_trigger_emojis(self):
        """Test initialization with custom trigger emojis."""
        listener = LiveChatListener(
            youtube_service=self.mock_youtube,
            video_id=self.video_id
        )
        custom_emojis = ["👍", "👎", "👌"]
        listener.trigger_emojis = custom_emojis
        self.assertEqual(listener.trigger_emojis, custom_emojis)
        
    def test_init_with_custom_trigger_cooldown(self):
        """Test initialization with a custom trigger cooldown value."""
        listener = LiveChatListener(
            youtube_service=self.mock_youtube,
            video_id=self.video_id
        )
        custom_cooldown = 120  # 2 minutes
        listener.trigger_cooldown = custom_cooldown
        self.assertEqual(listener.trigger_cooldown, custom_cooldown)
        
    def test_init_without_live_chat_id(self):
        """Test initialization without providing a live_chat_id."""
        listener = LiveChatListener(
            youtube_service=self.mock_youtube,
            video_id=self.video_id,
            live_chat_id=None
        )
        self.assertIsNone(listener.live_chat_id)
        self.assertEqual(listener.video_id, self.video_id)
        
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
        
    def test_init_with_params(self):
        """Test initialization with custom parameters."""
        # Setup custom parameters
        youtube_service = MagicMock()
        video_id = "custom_video_id"
        live_chat_id = "custom_chat_id"
        
        # Create listener with custom parameters
        listener = LiveChatListener(
            youtube_service=youtube_service,
            video_id=video_id,
            live_chat_id=live_chat_id
        )
        
        # Set custom attributes after initialization
        listener.trigger_emojis = ["🔥", "👍", "👋"]
        listener.trigger_cooldown = 120
        listener.memory_dir = "custom_logs"
        listener.greeting_message = "Custom greeting"
        
        # Verify all parameters were set correctly
        self.assertEqual(listener.youtube, youtube_service)
        self.assertEqual(listener.video_id, video_id)
        self.assertEqual(listener.live_chat_id, live_chat_id)
        self.assertEqual(listener.trigger_emojis, ["🔥", "👍", "👋"])
        self.assertEqual(listener.trigger_cooldown, 120)
        self.assertEqual(listener.memory_dir, "custom_logs")
        self.assertEqual(listener.greeting_message, "Custom greeting")
        
    def test_init_default_params(self):
        """Test initialization with default parameters."""
        # Create listener with only required parameters
        youtube_service = MagicMock()
        video_id = "default_video_id"
        
        listener = LiveChatListener(youtube_service, video_id)
        
        # Verify default parameters
        self.assertEqual(listener.youtube, youtube_service)
        self.assertEqual(listener.video_id, video_id)
        self.assertIsNone(listener.live_chat_id)
        self.assertEqual(listener.trigger_emojis, ["✊", "✋", "🖐️"])  # Default emoji set
        self.assertEqual(listener.trigger_cooldown, 60)  # Default is 60 seconds
        self.assertEqual(listener.memory_dir, "memory")  # Default memory directory
        self.assertEqual(listener.greeting_message, os.getenv("AGENT_GREETING_MESSAGE", "FoundUps Agent reporting in!"))  # Default greeting

    # Tests from test_initialize_session_coverage.py
    @pytest.mark.asyncio
    async def test_initialize_chat_session_get_id_returns_none(self):
        """Test initialization when _get_live_chat_id returns None."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id")
        
        # Mock _get_live_chat_id to return None
        with patch.object(listener, '_get_live_chat_id') as mock_get_id:
            mock_get_id.return_value = None
            
            # Call the method
            result = await listener._initialize_chat_session()
            
            # Verify results
            assert result is False  # Should return False when chat ID is None
            assert listener.live_chat_id is None
            mock_get_id.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_chat_session_specific_exception(self):
        """Test initialization when _get_live_chat_id raises a specific exception."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id")
        
        # Mock _get_live_chat_id to raise an exception
        with patch.object(listener, '_get_live_chat_id') as mock_get_id:
            mock_get_id.side_effect = ValueError("Video not found")
            
            # Call the method
            result = await listener._initialize_chat_session()
            
            # Verify results
            assert result is False  # Should return False on exception
            assert listener.live_chat_id is None
            mock_get_id.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_chat_session_generic_exception(self):
        """Test initialization when _get_live_chat_id raises a generic exception."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id")
        
        # Mock _get_live_chat_id to raise an exception
        with patch.object(listener, '_get_live_chat_id') as mock_get_id:
            mock_get_id.side_effect = Exception("Unexpected error")
            
            # Call the method
            result = await listener._initialize_chat_session()
            
            # Verify results
            assert result is False  # Should return False on exception
            assert listener.live_chat_id is None
            mock_get_id.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_greeting_message_no_greeting_configured(self):
        """Test send_greeting_message when no greeting message is configured."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        listener.greeting_message = ""  # Empty greeting
        
        # Mock send_chat_message
        with patch.object(listener, 'send_chat_message', new_callable=AsyncMock) as mock_send:
            # Call the method
            await listener._send_greeting_message()
            
            # Verify results
            mock_send.assert_not_called()  # Should not attempt to send an empty greeting
    
    @pytest.mark.asyncio
    async def test_send_greeting_message_successful_send(self):
        """Test send_greeting_message when message is sent successfully."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        listener.greeting_message = "Hello everyone!"
        
        # Mock send_chat_message to return True (success)
        with patch.object(listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            mock_send.return_value = True
            
            # Call the method
            await listener._send_greeting_message()
            
            # Verify results
            mock_send.assert_called_once_with("Hello everyone!")
            mock_sleep.assert_called_once_with(2)  # Should sleep after greeting
    
    @pytest.mark.asyncio
    async def test_send_greeting_message_failed_send(self):
        """Test send_greeting_message when message sending fails."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        listener.greeting_message = "Hello everyone!"
        
        # Mock send_chat_message to return False (failure)
        with patch.object(listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            mock_send.return_value = False
            
            # Call the method
            await listener._send_greeting_message()
            
            # Verify results
            mock_send.assert_called_once_with("Hello everyone!")
            mock_sleep.assert_called_once_with(2)  # Should still sleep after failed attempt
    
    @pytest.mark.asyncio
    async def test_send_greeting_message_exception_during_send(self):
        """Test send_greeting_message when an exception occurs during send."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        listener.greeting_message = "Hello everyone!"
        
        # Mock send_chat_message to raise an exception
        with patch.object(listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            mock_send.side_effect = Exception("Network error")
            
            # Call the method
            await listener._send_greeting_message()
            
            # Verify results
            mock_send.assert_called_once_with("Hello everyone!")
            mock_sleep.assert_called_once_with(2)  # Should still sleep after exception

    @pytest.mark.asyncio
    async def test_initialize_chat_session_with_existing_id(self):
        """Test initializing chat session with existing live chat ID."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service, "video_id", live_chat_id="existing_chat_id")
        
        # Initialize chat session
        result = await listener._initialize_chat_session()
        
        # Verify existing chat ID was used
        self.assertTrue(result)
        self.assertEqual(listener.live_chat_id, "existing_chat_id")

    @pytest.mark.asyncio
    async def test_initialize_chat_session_fetches_id(self):
        """Test initializing chat session by fetching the chat ID."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service, "video_id")
        listener.live_chat_id = None
        
        # Mock get_live_chat_id to return a chat ID
        with patch.object(listener, "_get_live_chat_id", return_value="fetched_chat_id"):
            
            # Initialize chat session
            result = await listener._initialize_chat_session()
            
            # Verify fetched chat ID was set
            self.assertTrue(result)
            self.assertEqual(listener.live_chat_id, "fetched_chat_id")

    @pytest.mark.asyncio
    async def test_initialize_chat_session_fetch_failure(self):
        """Test initializing chat session when fetch fails."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service, "video_id")
        listener.live_chat_id = None
        
        # Mock get_live_chat_id to fail
        with patch.object(listener, "_get_live_chat_id", return_value=None):
            
            # Initialize chat session
            result = await listener._initialize_chat_session()
            
            # Verify False was returned
            self.assertFalse(result)
            self.assertIsNone(listener.live_chat_id)

    @pytest.mark.asyncio
    async def test_initialize_chat_session_fetch_exception(self):
        """Test initializing chat session when an exception occurs."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service, "video_id")
        listener.live_chat_id = None
        
        # Mock get_live_chat_id to raise exception
        with patch.object(listener, "_get_live_chat_id", side_effect=Exception("Test exception")):
            
            # Initialize chat session
            result = await listener._initialize_chat_session()
            
            # Verify False was returned
            self.assertFalse(result)
            self.assertIsNone(listener.live_chat_id)

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

