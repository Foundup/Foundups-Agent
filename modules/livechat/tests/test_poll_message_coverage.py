import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import httplib2
import googleapiclient.errors
import time
from modules.livechat.src.livechat import LiveChatListener

class TestPollMessagesExtra:
    """Additional tests specifically targeting uncovered code in _poll_chat_messages."""
    
    @pytest.mark.asyncio
    async def test_poll_chat_messages_dynamic_delay_calculation(self):
        """Test that dynamic delay calculation is properly applied during polling."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        listener.viewer_count = 1000  # Set a high viewer count to test dynamic delay
        
        # Mock YouTube API response
        youtube_service.liveChatMessages().list.return_value.execute.return_value = {
            "pollingIntervalMillis": 5000,  # Server suggests 5 seconds
            "nextPageToken": "next_token",
            "items": [{"id": "msg1"}]
        }
        
        # Mock the dynamic delay calculation to return a specific value
        with patch('modules.livechat.src.livechat.calculate_dynamic_delay') as mock_calc:
            mock_calc.return_value = 15.0  # Dynamic delay of 15 seconds
            
            # Execute the method
            result = await listener._poll_chat_messages()
            
            # Verify results
            assert result == [{"id": "msg1"}]
            assert listener.next_page_token == "next_token"
            assert listener.poll_interval_ms == 15000  # Should use the larger value (dynamic delay)
            mock_calc.assert_called_once_with(1000)  # Should be called with the viewer count
    
    @pytest.mark.asyncio
    async def test_poll_chat_messages_server_interval_higher(self):
        """Test when server polling interval is higher than calculated dynamic delay."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        listener.viewer_count = 100  # Set a lower viewer count
        
        # Mock YouTube API response with a high polling interval
        youtube_service.liveChatMessages().list.return_value.execute.return_value = {
            "pollingIntervalMillis": 20000,  # Server suggests 20 seconds
            "nextPageToken": "next_token",
            "items": [{"id": "msg1"}]
        }
        
        # Mock the dynamic delay calculation to return a lower value
        with patch('modules.livechat.src.livechat.calculate_dynamic_delay') as mock_calc:
            mock_calc.return_value = 5.0  # Dynamic delay of 5 seconds
            
            # Execute the method
            result = await listener._poll_chat_messages()
            
            # Verify results
            assert result == [{"id": "msg1"}]
            assert listener.next_page_token == "next_token"
            assert listener.poll_interval_ms == 20000  # Should use the server value
            mock_calc.assert_called_once_with(100)
    
    @pytest.mark.asyncio
    async def test_poll_chat_messages_error_backoff_reset(self):
        """Test that error backoff is reset on successful API call."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        listener.error_backoff_seconds = 30  # Set a high backoff value initially
        
        # Mock YouTube API response
        youtube_service.liveChatMessages().list.return_value.execute.return_value = {
            "pollingIntervalMillis": 10000,
            "nextPageToken": "next_token",
            "items": []
        }
        
        # Execute the method
        await listener._poll_chat_messages()
        
        # Verify the error backoff was reset
        assert listener.error_backoff_seconds == 5  # Should be reset to default
    
    @pytest.mark.asyncio
    async def test_poll_chat_messages_unexpected_error_backoff(self):
        """Test exponential backoff handling for unexpected errors during polling."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        listener.error_backoff_seconds = 5  # Initial backoff
        
        # Mock YouTube API to raise an unexpected error
        youtube_service.liveChatMessages().list.return_value.execute.side_effect = Exception("Unexpected server error")
        
        # Mock time.sleep to avoid waiting
        with patch('time.sleep') as mock_sleep:
            # Execute the method
            result = await listener._poll_chat_messages()
            
            # Verify results
            assert result == []  # Should return empty list on error
            mock_sleep.assert_called_once_with(5)  # Should sleep for 5 seconds
            assert listener.error_backoff_seconds == 10  # Should double to 10 seconds
            
            # Call again to test the exponential increase
            youtube_service.liveChatMessages().list.return_value.execute.side_effect = Exception("Another error")
            result = await listener._poll_chat_messages()
            
            # Verify backoff increased
            assert mock_sleep.call_count == 2
            mock_sleep.assert_called_with(10)  # Should sleep for 10 seconds
            assert listener.error_backoff_seconds == 20  # Should double to 20 seconds
    
    @pytest.mark.asyncio
    async def test_poll_chat_messages_backoff_max_limit(self):
        """Test that error backoff has a maximum cap of 60 seconds."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        listener.error_backoff_seconds = 40  # Start close to the limit
        
        # Mock YouTube API to raise an unexpected error
        youtube_service.liveChatMessages().list.return_value.execute.side_effect = Exception("Network error")
        
        # Mock time.sleep to avoid waiting
        with patch('time.sleep') as mock_sleep:
            # Execute the method
            result = await listener._poll_chat_messages()
            
            # Verify backoff was capped
            assert listener.error_backoff_seconds == 60  # Should be capped at 60 seconds
            
            # Call again to verify it stays at max
            result = await listener._poll_chat_messages()
            assert listener.error_backoff_seconds == 60  # Should stay at 60 seconds
    
    @pytest.mark.asyncio
    async def test_poll_chat_messages_with_no_response_items(self):
        """Test polling when the API response contains no items field."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        
        # Mock YouTube API response with missing items field
        youtube_service.liveChatMessages().list.return_value.execute.return_value = {
            "pollingIntervalMillis": 10000,
            "nextPageToken": "next_token"
            # No items field
        }
        
        # Execute the method
        result = await listener._poll_chat_messages()
        
        # Verify results
        assert result == []  # Should return empty list when no items
    
    @pytest.mark.asyncio
    async def test_poll_chat_messages_with_no_polling_interval(self):
        """Test polling when the API response contains no pollingIntervalMillis field."""
        # Setup
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id", live_chat_id="test_chat_id")
        
        # Mock YouTube API response with missing pollingIntervalMillis field
        youtube_service.liveChatMessages().list.return_value.execute.return_value = {
            # No pollingIntervalMillis field
            "nextPageToken": "next_token",
            "items": [{"id": "msg1"}]
        }
        
        # Mock the dynamic delay calculation
        with patch('modules.livechat.src.livechat.calculate_dynamic_delay') as mock_calc:
            mock_calc.return_value = 5.0  # Dynamic delay of 5 seconds
            
            # Execute the method
            result = await listener._poll_chat_messages()
            
            # Verify results
            assert result == [{"id": "msg1"}]
            # Should use default of 10000 ms from code
            assert listener.poll_interval_ms == max(10000, 5000) 