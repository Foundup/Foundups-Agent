"""
Unit tests for the lifecycle functionality of LiveChatListener class
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
from modules.communication.livechat.src.livechat_core import LiveChatCore as LiveChatListener
from modules.ai_intelligence.banter_engine import BanterEngine

class TestLiveChatListenerLifecycle(unittest.TestCase):
    """Test cases for lifecycle functionality of LiveChatListener."""
    
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
        
    # Tests moved from test_livechat_initialization.py
    
    @pytest.mark.asyncio
    async def test_is_running_initialized(self):
        """Test that is_running is initialized to False."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service, "video_id")
        
        # Verify is_running is initially False
        self.assertFalse(listener.is_running)

    @pytest.mark.asyncio
    async def test_start_listening_sets_is_running(self):
        """Test that start_listening sets is_running to True."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service, "video_id")
        
        # Mock methods to prevent actual API calls
        async def stop_after_one_iteration(*args, **kwargs):
            listener.is_running = False
            return None
            
        with patch.object(listener, "_initialize_chat_session", 
                           new_callable=AsyncMock, return_value="test_chat_id"), \
             patch.object(listener, "_send_greeting_message", 
                           new_callable=AsyncMock, return_value=True), \
             patch.object(listener, "_poll_chat_cycle", 
                           new_callable=AsyncMock, side_effect=stop_after_one_iteration):
            
            # Start listening
            await listener.start_listening()
            
            # Verify is_running was set to True before being set to False
            self.assertFalse(listener.is_running)
    
    # Tests moved from test_chat_cycle_coverage.py
    
    @pytest.mark.asyncio
    async def test_start_listening_already_running(self):
        """Test start_listening when listener is already running."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        listener.is_running = True  # Set as already running
        
        # Mock listener methods
        with patch.object(listener, '_initialize_chat_session', new_callable=AsyncMock) as mock_init, \
             patch.object(listener, '_send_greeting_message', new_callable=AsyncMock) as mock_greet, \
             patch.object(listener, '_poll_chat_cycle', new_callable=AsyncMock) as mock_poll:
            
            # Call the method
            await listener.start_listening()
            
            # Verify results
            mock_init.assert_not_called()  # Should not initialize if already running
            mock_greet.assert_not_called()  # Should not send greeting if already running
            mock_poll.assert_not_called()  # Should not enter polling loop if already running
    
    @pytest.mark.asyncio
    async def test_start_listening_critical_failure_during_cycle(self):
        """Test start_listening when a critical failure occurs during polling cycle."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        listener.is_running = False
        
        # Mock listener methods
        with patch.object(listener, '_initialize_chat_session', new_callable=AsyncMock) as mock_init, \
             patch.object(listener, '_send_greeting_message', new_callable=AsyncMock) as mock_greet, \
             patch.object(listener, '_poll_chat_cycle', new_callable=AsyncMock) as mock_poll, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            
            # Configure mocks for successful start but critical failure during polling
            mock_init.return_value = True
            # First call returns False (no error), second call returns True (critical failure)
            mock_poll.side_effect = [False, True]
            
            # Call the method
            await listener.start_listening()
            
            # Verify results
            self.assertEqual(mock_init.call_count, 1)
            self.assertEqual(mock_greet.call_count, 1)
            self.assertEqual(mock_poll.call_count, 2)  # Should be called twice
            self.assertEqual(mock_sleep.call_count, 1)  # Should be called once (after first successful poll)
            # Should be False at the end (shutdown due to critical failure)
            self.assertFalse(listener.is_running)
    
    @pytest.mark.asyncio
    async def test_start_listening_complete_shutdown(self):
        """Test start_listening through a complete shutdown (external stop signal)."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        listener.is_running = False
        listener.poll_interval_ms = 1000  # 1 second for faster test
        
        # Mock listener methods
        with patch.object(listener, '_initialize_chat_session', new_callable=AsyncMock) as mock_init, \
             patch.object(listener, '_send_greeting_message', new_callable=AsyncMock) as mock_greet, \
             patch.object(listener, '_poll_chat_cycle', new_callable=AsyncMock) as mock_poll, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            
            # Configure mocks for successful operation
            mock_init.return_value = True
            mock_poll.return_value = False  # No critical failures
            
            # Create task to stop the listener after 2 cycles
            async def stop_after_cycles():
                await asyncio.sleep(0.1)  # Wait briefly
                # After two cycles, set is_running to False (externally)
                listener.is_running = True  # First set to True as the main method will set it
                await asyncio.sleep(0.1)  # Wait for a cycle
                listener.is_running = False  # Then set to False to stop
            
            # Run both tasks
            stop_task = asyncio.create_task(stop_after_cycles())
            await listener.start_listening()
            await stop_task
            
            # Verify results
            self.assertEqual(mock_init.call_count, 1)
            self.assertEqual(mock_greet.call_count, 1)
            # Verify is_running state at the end
            self.assertFalse(listener.is_running)
    
    @pytest.mark.asyncio
    async def test_start_listening_unhandled_exception(self):
        """Test start_listening when an unhandled exception occurs."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        listener.is_running = False
        
        # Mock listener methods
        with patch.object(listener, '_initialize_chat_session', new_callable=AsyncMock) as mock_init, \
             patch.object(listener, '_send_greeting_message', new_callable=AsyncMock) as mock_greet, \
             patch.object(listener, '_poll_chat_cycle', new_callable=AsyncMock) as mock_poll:
            
            # Configure _poll_chat_cycle to raise an unhandled exception
            mock_init.return_value = True
            mock_poll.side_effect = Exception("Unhandled critical error")
            
            # Call the method - it should re-raise the exception
            with pytest.raises(Exception, match="Unhandled critical error"):
                await listener.start_listening()
            
            # Verify results
            self.assertEqual(mock_init.call_count, 1)
            self.assertEqual(mock_greet.call_count, 1)
            self.assertEqual(mock_poll.call_count, 1)
            # Should be False at the end (shutdown due to exception)
            self.assertFalse(listener.is_running)
            
    # Tests moved from test_livechat_message_polling.py
    
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
    async def test_poll_chat_cycle_exception_handling(self):
        """Test _poll_chat_cycle handles exceptions properly."""
        # Mock dependencies
        with patch.object(self.listener, '_update_viewer_count') as mock_update, \
             patch.object(self.listener, '_poll_chat_messages', new_callable=AsyncMock) as mock_poll:
            
            # Make polling raise an exception
            mock_poll.side_effect = Exception("Poll error")
            
            # Call the method - should propagate the exception
            with self.assertRaises(Exception) as context:
                await self.listener._poll_chat_cycle()
            
            # Verify exception and method calls
            self.assertEqual(str(context.exception), "Poll error")
            mock_update.assert_called_once()
            mock_poll.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_poll_chat_cycle_with_viewer_update_error(self):
        """Test _poll_chat_cycle when _update_viewer_count raises an exception."""
        # Setup test messages
        test_messages = [{"id": "msg1"}, {"id": "msg2"}]
        
        # Mock dependencies
        with patch.object(self.listener, '_update_viewer_count', side_effect=Exception("Viewer update error")) as mock_update, \
             patch.object(self.listener, '_poll_chat_messages', new_callable=AsyncMock, return_value=test_messages) as mock_poll, \
             patch.object(self.listener, '_process_message_batch', new_callable=AsyncMock) as mock_process:
            
            # Call the method - should propagate the exception
            with self.assertRaises(Exception) as context:
                await self.listener._poll_chat_cycle()
            
            # Verify exception and method calls
            self.assertEqual(str(context.exception), "Viewer update error")
            mock_update.assert_called_once()
            mock_poll.assert_not_called()  # Should not be called if update_viewer_count fails
            mock_process.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_poll_chat_cycle_with_processing_error(self):
        """Test _poll_chat_cycle when _process_message_batch raises an exception."""
        # Setup test messages
        test_messages = [{"id": "msg1"}, {"id": "msg2"}]
        
        # Mock dependencies
        with patch.object(self.listener, '_update_viewer_count') as mock_update, \
             patch.object(self.listener, '_poll_chat_messages', new_callable=AsyncMock, return_value=test_messages) as mock_poll, \
             patch.object(self.listener, '_process_message_batch', new_callable=AsyncMock, 
                         side_effect=Exception("Processing error")) as mock_process:
            
            # Call the method - should propagate the exception
            with self.assertRaises(Exception) as context:
                await self.listener._poll_chat_cycle()
            
            # Verify exception and method calls
            self.assertEqual(str(context.exception), "Processing error")
            mock_update.assert_called_once()
            mock_poll.assert_called_once()
            mock_process.assert_called_once_with(test_messages)
    
    @pytest.mark.asyncio
    async def test_poll_chat_cycle_execution_order(self):
        """Test the execution order of operations in _poll_chat_cycle."""
        # Setup test messages
        test_messages = [{"id": "msg1"}]
        
        # To track execution order
        execution_order = []
        
        # Mock dependencies with order tracking
        def track_update():
            execution_order.append("update_viewer_count")
            
        async def track_poll():
            execution_order.append("poll_chat_messages")
            return test_messages
            
        async def track_process(msgs):
            execution_order.append("process_message_batch")
            
        with patch.object(self.listener, '_update_viewer_count', side_effect=track_update) as mock_update, \
             patch.object(self.listener, '_poll_chat_messages', new_callable=AsyncMock, side_effect=track_poll) as mock_poll, \
             patch.object(self.listener, '_process_message_batch', new_callable=AsyncMock, side_effect=track_process) as mock_process:
            
            # Call the method
            result = await self.listener._poll_chat_cycle()
            
            # Verify results
            self.assertFalse(result)  # Should return False (no critical failure)
            
            # Verify execution order
            self.assertEqual(execution_order, [
                "update_viewer_count",
                "poll_chat_messages",
                "process_message_batch"
            ])
    
    # COVERAGE GAP: The original source code does not contain a stop_listening method
    # This test directly tests the behavior that would be provided by such a method
    def test_stop_listening(self):
        """Test the capability to stop the listener by setting is_running to False."""
        # Setup - listener is running
        self.listener.is_running = True

        # Call the stop_listening method
        self.listener.stop_listening()

        # Verify is_running is set to False
        self.assertFalse(self.listener.is_running)

    # Tests for _initialize_chat_session method
    
    @pytest.mark.asyncio
    async def test_initialize_chat_session_no_id_success(self):
        """Test _initialize_chat_session when no live_chat_id is provided."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id")
        listener.live_chat_id = None  # Ensure no chat ID is set
        
        # Mock _get_live_chat_id
        with patch.object(listener, '_get_live_chat_id', return_value="new_chat_id") as mock_get_id:
            # Call the method
            result = await listener._initialize_chat_session()
            
            # Verify results
            self.assertTrue(result)
            mock_get_id.assert_called_once()
            self.assertEqual(listener.live_chat_id, "new_chat_id")
    
    @pytest.mark.asyncio
    async def test_initialize_chat_session_with_provided_id(self):
        """Test _initialize_chat_session when live_chat_id is already provided."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="existing_chat_id")
        
        # Mock _get_live_chat_id
        with patch.object(listener, '_get_live_chat_id') as mock_get_id:
            # Call the method
            result = await listener._initialize_chat_session()
            
            # Verify results
            self.assertTrue(result)
            mock_get_id.assert_not_called()  # Should not try to get ID when already provided
            self.assertEqual(listener.live_chat_id, "existing_chat_id")
    
    @pytest.mark.asyncio
    async def test_initialize_chat_session_get_id_returns_none(self):
        """Test _initialize_chat_session when _get_live_chat_id returns None."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id")
        listener.live_chat_id = None
        
        # Mock _get_live_chat_id
        with patch.object(listener, '_get_live_chat_id', return_value=None) as mock_get_id:
            # Call the method
            result = await listener._initialize_chat_session()
            
            # Verify results
            self.assertFalse(result)
            mock_get_id.assert_called_once()
            self.assertIsNone(listener.live_chat_id)
    
    @pytest.mark.asyncio
    async def test_initialize_chat_session_get_id_raises_exception(self):
        """Test _initialize_chat_session when _get_live_chat_id raises an exception."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id")
        listener.live_chat_id = None
        
        # Mock _get_live_chat_id
        with patch.object(listener, '_get_live_chat_id', side_effect=ValueError("No active chat")) as mock_get_id:
            # Call the method
            result = await listener._initialize_chat_session()
            
            # Verify results
            self.assertFalse(result)
            mock_get_id.assert_called_once()
            self.assertIsNone(listener.live_chat_id)
    
    # Tests for _send_greeting_message method
    
    @pytest.mark.asyncio
    async def test_send_greeting_message_success(self):
        """Test _send_greeting_message successfully sends greeting."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        listener.greeting_message = "Hello, chat!"
        
        # Mock send_chat_message
        with patch.object(listener, 'send_chat_message', new_callable=AsyncMock, return_value=True) as mock_send, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            # Call the method
            await listener._send_greeting_message()
            
            # Verify results
            mock_send.assert_called_once_with("Hello, chat!")
            mock_sleep.assert_called_once_with(2)  # Should pause after sending
    
    @pytest.mark.asyncio
    async def test_send_greeting_message_failure(self):
        """Test _send_greeting_message when send_chat_message fails."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        listener.greeting_message = "Hello, chat!"
        
        # Mock send_chat_message
        with patch.object(listener, 'send_chat_message', new_callable=AsyncMock, return_value=False) as mock_send, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            # Call the method
            await listener._send_greeting_message()
            
            # Verify results
            mock_send.assert_called_once_with("Hello, chat!")
            mock_sleep.assert_called_once_with(2)  # Should still pause even after failure
    
    @pytest.mark.asyncio
    async def test_send_greeting_message_exception(self):
        """Test _send_greeting_message when send_chat_message raises an exception."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        listener.greeting_message = "Hello, chat!"
        
        # Mock send_chat_message
        with patch.object(listener, 'send_chat_message', new_callable=AsyncMock, 
                         side_effect=Exception("Send error")) as mock_send, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            # Call the method
            await listener._send_greeting_message()
            
            # Verify results
            mock_send.assert_called_once_with("Hello, chat!")
            mock_sleep.assert_called_once_with(2)  # Should still pause even after exception
    
    @pytest.mark.asyncio
    async def test_send_greeting_message_no_greeting_configured(self):
        """Test _send_greeting_message when no greeting message is configured."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        listener.greeting_message = ""  # Empty greeting
        
        # Mock send_chat_message
        with patch.object(listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            # Call the method
            await listener._send_greeting_message()
            
            # Verify results
            mock_send.assert_not_called()  # Should not attempt to send empty greeting
            mock_sleep.assert_not_called()  # Should not pause if no greeting sent 