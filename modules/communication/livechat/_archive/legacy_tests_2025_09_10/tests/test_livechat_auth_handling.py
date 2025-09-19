"""
Unit tests for the authentication handling functionality of LiveChatListener class
"""

import unittest
from unittest.mock import patch, MagicMock, AsyncMock, mock_open, PropertyMock
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

class TestLiveChatListenerAuthHandling(unittest.TestCase):
    """Test cases for authentication handling functionality of LiveChatListener."""
    
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
        
    @pytest.mark.asyncio
    async def test_handle_auth_error_non_http_error(self):
        """Test the simplest path in _handle_auth_error with a non-HTTP error."""
        # Create a minimal LiveChatListener instance
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id")
        
        # Create a standard ValueError
        standard_error = ValueError("Simple non-HTTP error for diagnosis")
        
        # Direct call to the method - minimal code path
        result = await listener._handle_auth_error(standard_error)
        
        # Simple verification
        self.assertFalse(result)  # Should return False for non-HTTP errors
        
    @pytest.mark.asyncio
    async def test_handle_auth_error_auth_error(self):
        """Test _handle_auth_error with an auth error (401)."""
        # Create a minimal LiveChatListener instance
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id")
        
        # Create a 401 auth error
        mock_response = httplib2.Response({'status': 401})
        auth_error = googleapiclient.errors.HttpError(
            resp=mock_response,
            content=b'Authentication error'
        )
        
        # Mock the token manager and auth service
        with patch('modules.livechat.src.livechat.token_manager.rotate_tokens', new_callable=AsyncMock) as mock_rotate, \
             patch('modules.livechat.src.livechat.get_authenticated_service') as mock_auth:
            
            # Set up mock returns
            mock_rotate.return_value = 1  # Successfully rotated to token index 1
            mock_auth.return_value = MagicMock()  # New service
            
            # Call the method directly
            result = await listener._handle_auth_error(auth_error)
            
            # Verify
            self.assertTrue(result)
            mock_rotate.assert_awaited_once()
            mock_auth.assert_called_once_with(1)
            self.assertEqual(listener.youtube, mock_auth.return_value)

    @pytest.mark.asyncio
    async def test_handle_auth_error_rotation_failure(self):
        """Test _handle_auth_error when token rotation fails."""
        # Create a minimal LiveChatListener instance
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id")
        
        # Create a 401 auth error
        mock_response = httplib2.Response({'status': 401})
        auth_error = googleapiclient.errors.HttpError(
            resp=mock_response,
            content=b'Authentication error'
        )
        
        # Mock the token manager to return None (rotation failed)
        with patch('modules.livechat.src.livechat.token_manager.rotate_tokens', new_callable=AsyncMock) as mock_rotate:
            mock_rotate.return_value = None
            
            # Call the method directly
            result = await listener._handle_auth_error(auth_error)
            
            # Verify
            self.assertFalse(result)  # Should return False when rotation fails
            mock_rotate.assert_awaited_once()
            
    @pytest.mark.asyncio
    async def test_handle_auth_error_reauth_failure(self):
        """Test _handle_auth_error when re-authentication fails."""
        # Create a minimal LiveChatListener instance
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id")
        
        # Create a 401 auth error
        mock_response = httplib2.Response({'status': 401})
        auth_error = googleapiclient.errors.HttpError(
            resp=mock_response,
            content=b'Authentication error'
        )
        
        # Mock token manager and authentication service
        with patch('modules.livechat.src.livechat.token_manager.rotate_tokens', new_callable=AsyncMock) as mock_rotate, \
             patch('modules.livechat.src.livechat.get_authenticated_service') as mock_auth:
            
            # Configure mocks - rotation succeeds but auth fails
            mock_rotate.return_value = 2
            mock_auth.side_effect = Exception("Auth error in test")
            
            # Call the method directly
            result = await listener._handle_auth_error(auth_error)
            
            # Verify
            self.assertFalse(result)  # Should return False when re-auth fails
            mock_rotate.assert_awaited_once()
            mock_auth.assert_called_once_with(2)
            
    @pytest.mark.asyncio
    async def test_handle_auth_error_non_auth_http_error(self):
        """Test _handle_auth_error with a non-auth HTTP error (500)."""
        # Create a minimal LiveChatListener instance
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id")
        
        # Create a non-auth HTTP error (500)
        mock_response = httplib2.Response({'status': 500})
        non_auth_error = googleapiclient.errors.HttpError(
            resp=mock_response,
            content=b'Server error'
        )
        
        # Call the method directly
        result = await listener._handle_auth_error(non_auth_error)
        
        # Verify
        self.assertFalse(result)  # Should return False for non-auth HTTP errors
        
    @pytest.mark.asyncio
    async def test_handle_auth_error_basic(self):
        """Test _handle_auth_error directly to diagnose coverage issues."""
        # Create a minimal LiveChatListener instance
        youtube_service = MagicMock()
        listener = LiveChatListener(youtube_service=youtube_service, video_id="test_id")
        
        # Create a 401 auth error
        mock_response = httplib2.Response({'status': 401})
        auth_error = googleapiclient.errors.HttpError(
            resp=mock_response,
            content=b'Authentication error'
        )
        
        # Mock the token manager and auth service
        with patch('modules.livechat.src.livechat.token_manager.rotate_tokens', new_callable=AsyncMock) as mock_rotate, \
             patch('modules.livechat.src.livechat.get_authenticated_service') as mock_auth:
            
            # Set up mock returns
            mock_rotate.return_value = 1  # Successfully rotated to token index 1
            mock_auth.return_value = MagicMock()  # New service
            
            # Call the method directly
            result = await listener._handle_auth_error(auth_error)
            
            # Verify
            self.assertTrue(result)
            mock_rotate.assert_awaited_once()
            mock_auth.assert_called_once_with(1)
            self.assertEqual(listener.youtube, mock_auth.return_value) 