"""
Unit tests for the LiveChatPoller class in live_chat_poller.py
"""

import unittest
from unittest.mock import patch, MagicMock
import logging
import googleapiclient.errors
from modules.live_chat_poller.src.live_chat_poller import LiveChatPoller

class TestLiveChatPoller(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        # Disable logging during tests
        logging.disable(logging.CRITICAL)
        
        # Create mock YouTube service
        self.mock_youtube = MagicMock()
        self.video_id = "test_video_id"
        self.live_chat_id = "test_live_chat_id"
        
        # Configure mock responses
        self.mock_video_response = {
            "items": [{
                "liveStreamingDetails": {
                    "activeLiveChatId": self.live_chat_id
                }
            }]
        }
        
        self.mock_chat_response = {
            "nextPageToken": "next_token",
            "pollingIntervalMillis": 2000,
            "items": [
                {"id": "msg1", "snippet": {"displayMessage": "Hello"}, 
                 "authorDetails": {"displayName": "User1"}},
                {"id": "msg2", "snippet": {"displayMessage": "World"}, 
                 "authorDetails": {"displayName": "User2"}}
            ]
        }
        
        # Set up YouTube API mock returns
        self.mock_youtube.videos().list.return_value.execute.return_value = self.mock_video_response
        self.mock_youtube.liveChatMessages().list.return_value.execute.return_value = self.mock_chat_response
        
        # Create the LiveChatPoller instance
        self.poller = LiveChatPoller(self.mock_youtube, self.video_id)
    
    def tearDown(self):
        """Tear down test fixtures."""
        logging.disable(logging.NOTSET)
    
    def test_init(self):
        """Test initialization of LiveChatPoller."""
        self.assertEqual(self.poller.youtube, self.mock_youtube)
        self.assertEqual(self.poller.video_id, self.video_id)
        self.assertIsNone(self.poller.live_chat_id)
        self.assertIsNone(self.poller.next_page_token)
    
    def test_get_live_chat_id_success(self):
        """Test successful retrieval of live chat ID."""
        chat_id = self.poller.get_live_chat_id()
        
        # Verify results
        self.assertEqual(chat_id, self.live_chat_id)
        self.assertEqual(self.poller.live_chat_id, self.live_chat_id)
        self.mock_youtube.videos().list.assert_called_once_with(
            part="liveStreamingDetails",
            id=self.video_id
        )
    
    def test_get_live_chat_id_no_video(self):
        """Test handling of missing video."""
        # Configure mock to return no items
        self.mock_youtube.videos().list.return_value.execute.return_value = {"items": []}
        
        # Call the method
        chat_id = self.poller.get_live_chat_id()
        
        # Verify results
        self.assertIsNone(chat_id)
        self.assertIsNone(self.poller.live_chat_id)
    
    def test_get_live_chat_id_no_details(self):
        """Test handling of missing live streaming details."""
        # Configure mock to return item without liveStreamingDetails
        self.mock_youtube.videos().list.return_value.execute.return_value = {
            "items": [{}]
        }
        
        # Call the method
        chat_id = self.poller.get_live_chat_id()
        
        # Verify results
        self.assertIsNone(chat_id)
        self.assertIsNone(self.poller.live_chat_id)
    
    def test_get_live_chat_id_no_chat_id(self):
        """Test handling of missing active chat ID."""
        # Configure mock to return empty liveStreamingDetails
        self.mock_youtube.videos().list.return_value.execute.return_value = {
            "items": [{"liveStreamingDetails": {}}]
        }
        
        # Call the method
        chat_id = self.poller.get_live_chat_id()
        
        # Verify results
        self.assertIsNone(chat_id)
        self.assertIsNone(self.poller.live_chat_id)
    
    def test_get_live_chat_id_exception(self):
        """Test exception handling in get_live_chat_id."""
        # Configure mock to raise an exception
        self.mock_youtube.videos().list.return_value.execute.side_effect = Exception("API Error")
        
        # Call the method
        chat_id = self.poller.get_live_chat_id()
        
        # Verify results
        self.assertIsNone(chat_id)
        self.assertIsNone(self.poller.live_chat_id)
    
    def test_poll_once_success(self):
        """Test successful polling of messages."""
        # Set chat ID to skip the get_live_chat_id call
        self.poller.live_chat_id = self.live_chat_id
        
        # Call the method
        messages, interval = self.poller.poll_once()
        
        # Verify results
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["id"], "msg1")
        self.assertEqual(messages[1]["id"], "msg2")
        self.assertEqual(interval, 2000)
        self.assertEqual(self.poller.next_page_token, "next_token")
        self.mock_youtube.liveChatMessages().list.assert_called_once_with(
            liveChatId=self.live_chat_id,
            part="snippet,authorDetails",
            pageToken=None
        )
    
    def test_poll_once_with_next_page_token(self):
        """Test polling with an existing next page token."""
        # Set chat ID and next page token
        self.poller.live_chat_id = self.live_chat_id
        self.poller.next_page_token = "current_token"
        
        # Call the method
        messages, interval = self.poller.poll_once()
        
        # Verify results
        self.assertEqual(len(messages), 2)
        self.assertEqual(self.poller.next_page_token, "next_token")
        self.mock_youtube.liveChatMessages().list.assert_called_once_with(
            liveChatId=self.live_chat_id,
            part="snippet,authorDetails",
            pageToken="current_token"
        )
    
    def test_poll_once_no_chat_id(self):
        """Test polling behavior when no chat ID is available."""
        # Set up a mock for get_live_chat_id
        with patch.object(self.poller, 'get_live_chat_id', return_value=None) as mock_get_id:
            # Call the method
            messages, interval = self.poller.poll_once()
            
            # Verify results
            self.assertEqual(messages, [])
            self.assertEqual(interval, 5000)
            mock_get_id.assert_called_once()
            self.mock_youtube.liveChatMessages().list.assert_not_called()
    
    def test_poll_once_empty_response(self):
        """Test handling of empty response."""
        # Set chat ID
        self.poller.live_chat_id = self.live_chat_id
        
        # Configure mock to return empty items
        self.mock_youtube.liveChatMessages().list.return_value.execute.return_value = {
            "nextPageToken": "next_token",
            "pollingIntervalMillis": 2000,
            "items": []
        }
        
        # Call the method
        messages, interval = self.poller.poll_once()
        
        # Verify results
        self.assertEqual(messages, [])
        self.assertEqual(interval, 2000)
        self.assertEqual(self.poller.next_page_token, "next_token")
    
    def test_poll_once_http_error_not_found(self):
        """Test handling of HTTP 404 error."""
        # Set chat ID
        self.poller.live_chat_id = self.live_chat_id
        
        # Configure mock to raise an HTTP error
        resp = MagicMock()
        resp.status = 404
        error = googleapiclient.errors.HttpError(resp, b"Not Found")
        self.mock_youtube.liveChatMessages().list.return_value.execute.side_effect = error
        
        # Call the method
        messages, interval = self.poller.poll_once()
        
        # Verify results
        self.assertEqual(messages, [])
        self.assertEqual(interval, 5000)
        self.assertIsNone(self.poller.live_chat_id)  # Chat ID should be reset on 404
    
    def test_poll_once_http_error_forbidden(self):
        """Test handling of HTTP 403 error."""
        # Set chat ID
        self.poller.live_chat_id = self.live_chat_id
        
        # Configure mock to raise an HTTP error
        resp = MagicMock()
        resp.status = 403
        error = googleapiclient.errors.HttpError(resp, b"Forbidden")
        self.mock_youtube.liveChatMessages().list.return_value.execute.side_effect = error
        
        # Call the method
        messages, interval = self.poller.poll_once()
        
        # Verify results
        self.assertEqual(messages, [])
        self.assertEqual(interval, 5000)
        self.assertIsNone(self.poller.live_chat_id)  # Chat ID should be reset on 403
    
    def test_poll_once_http_error_other(self):
        """Test handling of other HTTP errors."""
        # Set chat ID
        self.poller.live_chat_id = self.live_chat_id
        
        # Configure mock to raise an HTTP error
        resp = MagicMock()
        resp.status = 500
        error = googleapiclient.errors.HttpError(resp, b"Server Error")
        self.mock_youtube.liveChatMessages().list.return_value.execute.side_effect = error
        
        # Call the method
        messages, interval = self.poller.poll_once()
        
        # Verify results
        self.assertEqual(messages, [])
        self.assertEqual(interval, 5000)
        self.assertEqual(self.poller.live_chat_id, self.live_chat_id)  # Chat ID should NOT be reset
    
    def test_poll_once_generic_exception(self):
        """Test handling of general exceptions."""
        # Set chat ID
        self.poller.live_chat_id = self.live_chat_id
        
        # Configure mock to raise a generic exception
        self.mock_youtube.liveChatMessages().list.return_value.execute.side_effect = Exception("Generic Error")
        
        # Call the method
        messages, interval = self.poller.poll_once()
        
        # Verify results
        self.assertEqual(messages, [])
        self.assertEqual(interval, 5000)

if __name__ == '__main__':
    unittest.main() 