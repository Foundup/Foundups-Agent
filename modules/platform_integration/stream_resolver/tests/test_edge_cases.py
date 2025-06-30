"""
Additional tests for stream_resolver to target edge cases and increase coverage.
"""

import unittest
import os
from unittest.mock import patch, MagicMock
import pytest
import googleapiclient.errors
from googleapiclient.errors import HttpError
from modules.platform_integration.stream_resolver.src.stream_resolver import (
    search_livestreams,
    check_video_details,
    QuotaExceededError,
    get_active_livestream_video_id
)


class TestStreamResolverEdgeCases(unittest.TestCase):
    """Additional tests for edge cases in stream_resolver.py."""

    @patch('modules.platform_integration.stream_resolver.src.stream_resolver.time.sleep')  # Skip sleeps
    def test_search_livestreams_max_retries_quota_exceeded(self, mock_sleep):
        """Test search_livestreams when quota is exceeded and max retries is reached."""
        mock_client = MagicMock()
        mock_search = MagicMock()
        mock_list = MagicMock()
        
        # Mock HTTP error for quota exceeded
        resp = MagicMock()
        resp.status = 403
        quota_error = HttpError(resp, b'{"error": {"errors": [{"reason": "quotaExceeded"}]}}')
        mock_list.execute.side_effect = quota_error
        
        mock_client.search.return_value = mock_search
        mock_search.list.return_value = mock_list
        
        # Mock the error to contain "quotaExceeded" in its string representation
        quota_error_with_text = HttpError(resp, b'{"error": {"errors": [{"reason": "quotaExceeded"}]}}')
        mock_list.execute.side_effect = quota_error_with_text
        
        # Set max retries to 0 to immediately trigger the max retries path
        with patch('modules.platform_integration.stream_resolver.src.stream_resolver.MAX_RETRIES', 0):
            with pytest.raises(QuotaExceededError):
                search_livestreams(mock_client, retry_count=0)
    
    @patch('modules.platform_integration.stream_resolver.src.stream_resolver.time.sleep')  # Skip sleeps
    def test_check_video_details_keyboard_interrupt_during_quota_delay(self, mock_sleep):
        """Test check_video_details with a KeyboardInterrupt during the quota delay."""
        mock_client = MagicMock()
        mock_videos = MagicMock()
        mock_list = MagicMock()
        
        # Mock HTTP error for quota exceeded
        resp = MagicMock()
        resp.status = 403
        quota_error = HttpError(resp, b'{"error": {"errors": [{"reason": "quotaExceeded"}]}}')
        mock_list.execute.side_effect = quota_error
        
        mock_client.videos.return_value = mock_videos
        mock_videos.list.return_value = mock_list
        
        # Make sleep raise KeyboardInterrupt
        mock_sleep.side_effect = KeyboardInterrupt()
        
        # Mock the error to contain "quotaExceeded" in its string representation
        quota_error_with_text = HttpError(resp, b'{"error": {"errors": [{"reason": "quotaExceeded"}]}}')
        mock_list.execute.side_effect = quota_error_with_text
        
        result = check_video_details(mock_client, "test_video_id")
        
        # Verify result is None when interrupted
        self.assertIsNone(result)
    
    @patch('modules.platform_integration.stream_resolver.src.stream_resolver.time.sleep')  # Skip sleeps
    def test_search_livestreams_quota_exceeded_max_retries_reached(self, mock_sleep):
        """Test search_livestreams with quota exceeded when max retries is reached."""
        mock_client = MagicMock()
        mock_search = MagicMock()
        mock_list = MagicMock()
        
        # Mock HTTP error for quota exceeded
        resp = MagicMock()
        resp.status = 403
        quota_error = HttpError(resp, b'{"error": {"errors": [{"reason": "quotaExceeded"}]}}')
        mock_list.execute.side_effect = quota_error
        
        mock_client.search.return_value = mock_search
        mock_search.list.return_value = mock_list
        
        # Mock the error to contain "quotaExceeded" in its string representation
        quota_error_with_text = HttpError(resp, b'{"error": {"errors": [{"reason": "quotaExceeded"}]}}')
        mock_list.execute.side_effect = quota_error_with_text
        
        # Test with MAX_RETRIES=3 but retry_count already at 3
        with patch('modules.platform_integration.stream_resolver.src.stream_resolver.MAX_RETRIES', 3):
            with pytest.raises(QuotaExceededError):
                search_livestreams(mock_client, retry_count=3)
    
    @patch('modules.platform_integration.stream_resolver.src.stream_resolver.time.sleep')  # Skip sleeps
    @patch('modules.platform_integration.stream_resolver.src.stream_resolver.get_env_variable')
    def test_check_video_details_no_fallback_key(self, mock_get_env, mock_sleep):
        """Test check_video_details with quota exceeded and no fallback key."""
        mock_client = MagicMock()
        mock_videos = MagicMock()
        mock_list = MagicMock()
        
        # Mock HTTP error for quota exceeded
        resp = MagicMock()
        resp.status = 403
        quota_error = HttpError(resp, b'{"error": {"errors": [{"reason": "quotaExceeded"}]}}')
        mock_list.execute.side_effect = quota_error
        
        mock_client.videos.return_value = mock_videos
        mock_videos.list.return_value = mock_list
        mock_client._developerKey = "test_key"
        
        # Set up environment variable to return None for the fallback key
        mock_get_env.return_value = None
        
        # Mock the error to contain "quotaExceeded" in its string representation  
        quota_error_with_text = HttpError(resp, b'{"error": {"errors": [{"reason": "quotaExceeded"}]}}')
        mock_list.execute.side_effect = quota_error_with_text
        
        result = check_video_details(mock_client, "test_video_id")
        
        # Verify result is None when no fallback key is available
        self.assertIsNone(result)
    
    @patch('modules.platform_integration.stream_resolver.src.stream_resolver.time.sleep')  # Skip sleeps
    @patch('modules.platform_integration.stream_resolver.src.stream_resolver.search_livestreams')
    @patch('modules.platform_integration.stream_resolver.src.stream_resolver.check_video_details')
    def test_get_active_livestream_video_id_with_exception(self, mock_check_details, mock_search, mock_sleep):
        """Test get_active_livestream_video_id with an exception during search."""
        mock_client = MagicMock()
        
        # Make search raise an exception
        mock_search.side_effect = Exception("Test exception")
        
        # Set MAX_CONSECUTIVE_FAILURES low to speed up test
        with patch('modules.platform_integration.stream_resolver.src.stream_resolver.MAX_CONSECUTIVE_FAILURES', 2):
            result = get_active_livestream_video_id(mock_client, "test_channel_id")
        
        # Verify result is None after failures
        self.assertIsNone(result)
    
    @patch('modules.platform_integration.stream_resolver.src.stream_resolver.time.sleep')  # Skip sleeps
    def test_search_livestreams_other_http_error_retry_exceeded(self, mock_sleep):
        """Test search_livestreams with a non-quota HTTP error and max retries exceeded."""
        mock_client = MagicMock()
        mock_search = MagicMock()
        mock_list = MagicMock()
        
        # Mock HTTP error
        resp = MagicMock()
        resp.status = 500
        error = HttpError(resp, b'{"error": {"errors": [{"reason": "backendError"}]}}')
        mock_list.execute.side_effect = error
        
        mock_client.search.return_value = mock_search
        mock_search.list.return_value = mock_list
        
        # Set up retry count to test max retries path
        with patch('modules.platform_integration.stream_resolver.src.stream_resolver.MAX_RETRIES', 3):
            with patch('modules.platform_integration.stream_resolver.src.stream_resolver.CHANNEL_ID', 'test_channel_id'):
                result = search_livestreams(mock_client, retry_count=3)
        
        # Verify result is None when max retries exceeded
        self.assertIsNone(result) 