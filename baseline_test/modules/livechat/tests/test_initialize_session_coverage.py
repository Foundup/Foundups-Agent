import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from modules.livechat.src.livechat import LiveChatListener

class TestInitializeSessionExtra:
    """Additional tests specifically targeting uncovered code in _initialize_chat_session and _send_greeting_message."""
    
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