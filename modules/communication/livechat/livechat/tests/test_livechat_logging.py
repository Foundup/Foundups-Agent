"""
Unit tests for the logging functionality of LiveChatListener class
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

class TestLiveChatListenerLogging(unittest.TestCase):
    """Test cases for logging functionality of LiveChatListener."""
    
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
        
    @patch("os.makedirs")
    def test_log_to_user_file(self, mock_makedirs):
        """Test logging to user file - success case."""
        # Mock file operations
        mock_file = mock_open()
        
        # Create test message
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "Test message"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "test_channel"
            }
        }
        
        # Test writing to file
        with patch("builtins.open", mock_file):
            self.listener._log_to_user_file(test_message)
            
        # Verify directory was created
        log_dir = os.path.join(self.listener.memory_dir, "chat_logs").replace("\\", "/")
        mock_makedirs.assert_called_once_with(log_dir, exist_ok=True)
        
        # Verify file was opened with correct path
        expected_path = os.path.join(log_dir, "TestUser.jsonl").replace("\\", "/")
        mock_file.assert_called_once_with(expected_path, 'a', encoding='utf-8')
        
        # Verify write operation
        handle = mock_file()
        self.assertTrue(handle.write.called)
        # Should write the message as JSON with a newline
        handle.write.assert_called_once_with(json.dumps(test_message) + "\n")
        
    def test_log_to_user_file_error(self):
        """Test _log_to_user_file error handling when file operations fail."""
        # Create test message
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "Test message"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "test_channel"
            }
        }
        
        # Mock directory creation
        with patch('os.makedirs') as mock_makedirs:
            # Mock file operations to fail
            with patch("builtins.open") as mock_open:
                mock_open.side_effect = IOError("File error")
                
                # Execute - should raise exception with our implementation
                with self.assertRaises(Exception):
                    self.listener._log_to_user_file(test_message)

                # Verify method calls
                mock_makedirs.assert_called_once()
                mock_open.assert_called_once()
                
    def test_log_to_user_file_mkdir_error(self):
        """Test logging to user file when directory creation fails."""
        # Create test message
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "Test message"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "test_channel"
            }
        }
        
        # Mock os.makedirs to raise an exception
        with patch('os.makedirs', side_effect=PermissionError("Access denied")) as mock_makedirs:
            # Execute - should raise the exception
            with self.assertRaises(Exception):
                self.listener._log_to_user_file(test_message)
                
            # Verify makedirs was called with correct path
            expected_path = os.path.join(self.listener.memory_dir, "chat_logs").replace("\\", "/")
            mock_makedirs.assert_called_once_with(expected_path, exist_ok=True)
            
    def test_log_to_user_file_json_error(self):
        """Test logging to user file when JSON serialization fails."""
        # Create test message with problematic content that can't be serialized
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "Test message"
            },
            "authorDetails": {
                "displayName": "TestUser",
                "channelId": "test_channel",
                "circular_ref": None  # Will be set to create circular reference
            }
        }
        # Create circular reference that will cause JSON serialization to fail
        test_message["authorDetails"]["circular_ref"] = test_message
        
        # Mock directory creation to succeed
        with patch('os.makedirs') as mock_makedirs:
            # Mock file operations
            mock_file = mock_open()
            with patch("builtins.open", mock_file):
                # Mock json.dumps to raise exception
                with patch('json.dumps', side_effect=TypeError("Circular reference")) as mock_dumps:
                    # Execute - should raise the exception
                    with self.assertRaises(Exception):
                        self.listener._log_to_user_file(test_message)
                    
                    # Verify calls
                    mock_makedirs.assert_called_once()
                    # The file is opened before the JSON serialization error occurs
                    mock_file.assert_called_once()
                    mock_dumps.assert_called_once_with(test_message)
                    
    def test_log_to_user_file_missing_author(self):
        """Test logging to user file when author details are missing."""
        # Create test message without author display name
        test_message = {
            "id": "test_id",
            "snippet": {
                "displayMessage": "Test message"
            },
            "authorDetails": {
                # Missing displayName
                "channelId": "test_channel"
            }
        }
        
        # The implementation should raise KeyError when displayName is missing
        with self.assertRaises(KeyError):
            self.listener._log_to_user_file(test_message) 