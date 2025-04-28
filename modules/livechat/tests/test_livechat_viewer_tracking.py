"""
Unit tests for the viewer tracking functionality of LiveChatListener class
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

class TestLiveChatListenerViewerTracking(unittest.TestCase):
    """Test cases for viewer tracking functionality of LiveChatListener."""
    
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
        
    def test_update_viewer_count_success(self):
        """Test that _update_viewer_count correctly updates the viewer count from a successful API response."""
        # Set up the mock response with a specific view count
        mock_response = {
            "items": [{
                "statistics": {
                    "viewCount": "500"
                }
            }]
        }
        
        # Configure mock to return our custom response
        self.mock_youtube.videos().list.return_value.execute.return_value = mock_response
        
        # Initial viewer count should be 0
        self.listener.viewer_count = 0
        
        # Call the method
        self.listener._update_viewer_count()
        
        # Verify viewer count was updated to 500
        self.assertEqual(self.listener.viewer_count, 500)
        
        # Verify API call was made with correct parameters
        self.mock_youtube.videos().list.assert_called_once_with(
            part="statistics",
            id=self.video_id
        )
    
    def test_update_viewer_count_api_error(self):
        """Test that _update_viewer_count handles API errors gracefully."""
        # Set up the mock to raise an HttpError
        self.mock_youtube.videos().list.return_value.execute.side_effect = HttpError(
            resp=httplib2.Response({"status": 500}),
            content=b"Server error"
        )
        
        # Set an initial viewer count
        self.listener.viewer_count = 250
        
        # Call the method - should not raise an exception
        self.listener._update_viewer_count()
        
        # Viewer count should remain unchanged
        self.assertEqual(self.listener.viewer_count, 250)
        
        # Verify API call was attempted
        self.mock_youtube.videos().list.assert_called_once()
    
    def test_update_viewer_count_general_exception(self):
        """Test that _update_viewer_count handles general exceptions gracefully."""
        # Set up the mock to raise a general exception
        self.mock_youtube.videos().list.return_value.execute.side_effect = Exception("Unexpected error")
        
        # Set an initial viewer count
        self.listener.viewer_count = 100
        
        # Call the method - should not raise an exception
        self.listener._update_viewer_count()
        
        # Viewer count should remain unchanged
        self.assertEqual(self.listener.viewer_count, 100)
        
        # Verify API call was attempted
        self.mock_youtube.videos().list.assert_called_once()
    
    def test_update_viewer_count_missing_items(self):
        """Test that _update_viewer_count handles a response with missing 'items' key."""
        # Set up the mock response with missing 'items'
        mock_response = {}  # No 'items' key
        
        # Configure mock to return our custom response
        self.mock_youtube.videos().list.return_value.execute.return_value = mock_response
        
        # Set an initial viewer count
        self.listener.viewer_count = 150
        
        # Call the method
        self.listener._update_viewer_count()
        
        # Viewer count should remain unchanged
        self.assertEqual(self.listener.viewer_count, 150)
    
    def test_update_viewer_count_empty_items(self):
        """Test that _update_viewer_count handles a response with empty 'items' list."""
        # Set up the mock response with empty 'items' list
        mock_response = {
            "items": []  # Empty list
        }
        
        # Configure mock to return our custom response
        self.mock_youtube.videos().list.return_value.execute.return_value = mock_response
        
        # Set an initial viewer count
        self.listener.viewer_count = 75
        
        # Call the method
        self.listener._update_viewer_count()
        
        # Viewer count should remain unchanged
        self.assertEqual(self.listener.viewer_count, 75)
    
    def test_update_viewer_count_missing_statistics(self):
        """Test that _update_viewer_count handles a response with missing 'statistics' key."""
        # Set up the mock response with missing 'statistics'
        mock_response = {
            "items": [{
                # No 'statistics' key
            }]
        }
        
        # Configure mock to return our custom response
        self.mock_youtube.videos().list.return_value.execute.return_value = mock_response
        
        # Set an initial viewer count
        self.listener.viewer_count = 200
        
        # Call the method
        self.listener._update_viewer_count()
        
        # Viewer count should remain unchanged
        self.assertEqual(self.listener.viewer_count, 200)
    
    def test_update_viewer_count_missing_view_count(self):
        """Test that _update_viewer_count handles a response with missing 'viewCount' field."""
        # Set up the mock response with missing 'viewCount'
        mock_response = {
            "items": [{
                "statistics": {
                    # No 'viewCount' key
                }
            }]
        }
        
        # Configure mock to return our custom response
        self.mock_youtube.videos().list.return_value.execute.return_value = mock_response
        
        # Set an initial viewer count
        self.listener.viewer_count = 300
        
        # Call the method
        self.listener._update_viewer_count()
        
        # Viewer count should default to 0 since the get call defaults to 0
        self.assertEqual(self.listener.viewer_count, 0)
    
    def test_update_viewer_count_concurrent_viewers(self):
        """Test that _update_viewer_count correctly handles the 'viewCount' field."""
        # Set up the mock response with viewCount
        mock_response = {
            "items": [{
                "statistics": {
                    "viewCount": "1234"
                }
            }]
        }
        
        # Configure mock to return our custom response
        self.mock_youtube.videos().list.return_value.execute.return_value = mock_response
        
        # Reset viewer count
        self.listener.viewer_count = 0
        
        # Call the method
        self.listener._update_viewer_count()
        
        # Verify viewer count was correctly parsed from the response
        self.assertEqual(self.listener.viewer_count, 1234) 