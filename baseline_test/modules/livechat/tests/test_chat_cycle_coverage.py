import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from modules.livechat.src.livechat import LiveChatListener

class TestChatCycleExtra:
    """Additional tests specifically targeting uncovered code in chat polling cycle methods."""
    
    @pytest.mark.asyncio
    async def test_poll_chat_cycle_null_messages_critical_failure(self):
        """Test _poll_chat_cycle when _poll_chat_messages returns None (critical failure)."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        
        # Mock required methods
        with patch.object(listener, '_update_viewer_count') as mock_update, \
             patch.object(listener, '_poll_chat_messages', new_callable=AsyncMock) as mock_poll, \
             patch.object(listener, '_process_message_batch', new_callable=AsyncMock) as mock_process:
            
            # Configure _poll_chat_messages to return None (critical failure)
            mock_poll.return_value = None
            
            # Call the method
            result = await listener._poll_chat_cycle()
            
            # Verify results
            assert result is True  # Should indicate critical failure
            mock_update.assert_called_once()
            mock_poll.assert_called_once()
            mock_process.assert_not_called()  # Should not attempt to process messages on critical failure
    
    @pytest.mark.asyncio
    async def test_poll_chat_cycle_with_messages(self):
        """Test _poll_chat_cycle with successful polling returning messages."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        
        # Mock required methods
        with patch.object(listener, '_update_viewer_count') as mock_update, \
             patch.object(listener, '_poll_chat_messages', new_callable=AsyncMock) as mock_poll, \
             patch.object(listener, '_process_message_batch', new_callable=AsyncMock) as mock_process:
            
            # Configure _poll_chat_messages to return messages
            messages = [{"id": "msg1"}, {"id": "msg2"}]
            mock_poll.return_value = messages
            
            # Call the method
            result = await listener._poll_chat_cycle()
            
            # Verify results
            assert result is False  # Should indicate no critical failure
            mock_update.assert_called_once()
            mock_poll.assert_called_once()
            mock_process.assert_called_once_with(messages)
    
    @pytest.mark.asyncio
    async def test_process_message_batch_empty(self):
        """Test _process_message_batch with an empty list."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        
        # Mock _process_message
        with patch.object(listener, '_process_message', new_callable=AsyncMock) as mock_process:
            # Call the method with empty list
            await listener._process_message_batch([])
            
            # Verify results
            mock_process.assert_not_called()  # Should not be called with empty list
    
    @pytest.mark.asyncio
    async def test_process_message_batch_processing_exception(self):
        """Test _process_message_batch when _process_message raises an exception."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        
        # Mock _process_message to raise an exception
        with patch.object(listener, '_process_message', new_callable=AsyncMock) as mock_process:
            mock_process.side_effect = Exception("Processing failed")
            
            # Call the method
            await listener._process_message_batch([{"id": "msg1"}])
            
            # Verify results
            mock_process.assert_called_once()  # Should be called once
            # Method should not raise the exception - it should be caught and logged
    
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
            assert mock_init.call_count == 1
            assert mock_greet.call_count == 1
            assert mock_poll.call_count == 2  # Should be called twice
            assert mock_sleep.call_count == 1  # Should be called once (after first successful poll)
            # Should be False at the end (shutdown due to critical failure)
            assert listener.is_running is False
    
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
            assert mock_init.call_count == 1
            assert mock_greet.call_count == 1
            # Verify is_running state at the end
            assert listener.is_running is False
    
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
            assert mock_init.call_count == 1
            assert mock_greet.call_count == 1
            assert mock_poll.call_count == 1
            # Should be False at the end (shutdown due to exception)
            assert listener.is_running is False 