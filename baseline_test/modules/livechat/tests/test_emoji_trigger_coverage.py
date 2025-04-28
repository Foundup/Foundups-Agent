import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from modules.livechat.src.livechat import LiveChatListener

class TestEmojiTriggerExtra:
    """Additional tests specifically targeting uncovered code in _handle_emoji_trigger."""
    
    @pytest.mark.asyncio
    async def test_handle_emoji_trigger_empty_banter_response(self):
        """Test handling of empty response from banter engine."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        
        # Mock banter engine to return an empty string
        listener.banter_engine = MagicMock()
        listener.banter_engine.get_random_banter.return_value = ""
        
        # Mock the is_rate_limited method to return False
        with patch.object(listener, '_is_rate_limited', return_value=False), \
             patch.object(listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch.object(listener, '_update_trigger_time') as mock_update:
            
            # Configure send_chat_message to succeed
            mock_send.return_value = True
            
            # Call the method
            result = await listener._handle_emoji_trigger(
                author_name="TestUser",
                author_id="user123",
                message_text="✊✋🖐️ Hello!"
            )
            
            # Verify results
            assert result is True
            # Should use fallback message due to empty response
            mock_send.assert_called_once()
            assert "Hey there" in mock_send.call_args[0][0]  # Should contain fallback text
            mock_update.assert_called_once_with("user123")
    
    @pytest.mark.asyncio
    async def test_handle_emoji_trigger_invalid_banter_not_string(self):
        """Test handling when banter engine returns a non-string response."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        
        # Mock banter engine to return a non-string value
        listener.banter_engine = MagicMock()
        listener.banter_engine.get_random_banter.return_value = 123  # Return a number instead of string
        
        # Mock the is_rate_limited method to return False
        with patch.object(listener, '_is_rate_limited', return_value=False), \
             patch.object(listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch.object(listener, '_update_trigger_time') as mock_update:
            
            # Configure send_chat_message to succeed
            mock_send.return_value = True
            
            # Call the method
            result = await listener._handle_emoji_trigger(
                author_name="TestUser",
                author_id="user123",
                message_text="✊✋🖐️ Hello!"
            )
            
            # Verify results
            assert result is True
            # Should use fallback message due to invalid type
            mock_send.assert_called_once()
            assert "Hey there" in mock_send.call_args[0][0]  # Should contain fallback text
            mock_update.assert_called_once_with("user123")
    
    @pytest.mark.asyncio
    async def test_handle_emoji_trigger_only_whitespace_response(self):
        """Test handling when banter engine returns only whitespace."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        
        # Mock banter engine to return only whitespace
        listener.banter_engine = MagicMock()
        listener.banter_engine.get_random_banter.return_value = "   \n\t   "
        
        # Mock the is_rate_limited method to return False
        with patch.object(listener, '_is_rate_limited', return_value=False), \
             patch.object(listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch.object(listener, '_update_trigger_time') as mock_update:
            
            # Configure send_chat_message to succeed
            mock_send.return_value = True
            
            # Call the method
            result = await listener._handle_emoji_trigger(
                author_name="TestUser",
                author_id="user123",
                message_text="✊✋🖐️ Hello!"
            )
            
            # Verify results
            assert result is True
            # Should use fallback message due to whitespace-only response
            mock_send.assert_called_once()
            assert "Hey there" in mock_send.call_args[0][0]  # Should contain fallback text
            mock_update.assert_called_once_with("user123")
    
    @pytest.mark.asyncio
    async def test_handle_emoji_trigger_send_failure(self):
        """Test handling when sending the chat message fails."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        
        # Mock banter engine to return a valid response
        listener.banter_engine = MagicMock()
        listener.banter_engine.get_random_banter.return_value = "Hello there!"
        
        # Mock the is_rate_limited method to return False
        with patch.object(listener, '_is_rate_limited', return_value=False), \
             patch.object(listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch.object(listener, '_update_trigger_time') as mock_update:
            
            # Configure send_chat_message to fail
            mock_send.return_value = False
            
            # Call the method
            result = await listener._handle_emoji_trigger(
                author_name="TestUser",
                author_id="user123",
                message_text="✊✋🖐️ Hello!"
            )
            
            # Verify results
            assert result is False  # Should return False when send fails
            mock_send.assert_called_once_with("Hello there!")
            mock_update.assert_not_called()  # Should not update trigger time on failure
    
    @pytest.mark.asyncio
    async def test_handle_emoji_trigger_banter_exception(self):
        """Test handling when banter engine raises an exception."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        
        # Mock banter engine to raise an exception
        listener.banter_engine = MagicMock()
        listener.banter_engine.get_random_banter.side_effect = Exception("Banter engine error")
        
        # Mock the is_rate_limited method to return False
        with patch.object(listener, '_is_rate_limited', return_value=False), \
             patch.object(listener, 'send_chat_message', new_callable=AsyncMock) as mock_send:
            
            # Call the method
            result = await listener._handle_emoji_trigger(
                author_name="TestUser",
                author_id="user123",
                message_text="✊✋🖐️ Hello!"
            )
            
            # Verify results
            assert result is False  # Should return False on exception
            mock_send.assert_not_called()  # Should not attempt to send
    
    @pytest.mark.asyncio
    async def test_handle_emoji_trigger_rate_limited(self):
        """Test handling when user is rate limited."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        
        # Mock the is_rate_limited method to return True (user is rate limited)
        with patch.object(listener, '_is_rate_limited', return_value=True), \
             patch.object(listener, 'send_chat_message', new_callable=AsyncMock) as mock_send, \
             patch.object(listener, '_update_trigger_time') as mock_update:
            
            # Call the method
            result = await listener._handle_emoji_trigger(
                author_name="TestUser",
                author_id="user123",
                message_text="✊✋🖐️ Hello!"
            )
            
            # Verify results
            assert result is False  # Should return False when rate limited
            mock_send.assert_not_called()  # Should not attempt to send
            mock_update.assert_not_called()  # Should not update trigger time 