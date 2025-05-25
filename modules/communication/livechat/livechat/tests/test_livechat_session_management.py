"""
Unit tests for the session management functionality of LiveChatListener class
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
from modules.ai_intelligence.banter_engine.banter_engine import BanterEngine

class TestLiveChatListenerSessionManagement(unittest.TestCase):
    """Test cases for session management functionality of LiveChatListener."""
    
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
    
    def test_get_live_chat_id_success(self):
        """Test successful retrieval of live chat ID."""
        # Setup
        expected_chat_id = "test_chat_id_123"
        self.mock_youtube.videos().list.return_value.execute.return_value = {
            "items": [
                {
                    "liveStreamingDetails": {
                        "activeLiveChatId": expected_chat_id
                    }
                }
            ]
        }
        
        # Reset live_chat_id to None to test retrieval
        self.listener.live_chat_id = None
        
        # Call the method
        result = self.listener._get_live_chat_id()
        
        # Verify
        self.assertEqual(result, expected_chat_id)
        self.assertEqual(self.listener.live_chat_id, expected_chat_id)
        self.mock_youtube.videos().list.assert_called_once_with(
            part="liveStreamingDetails",
            id=self.video_id
        )
    
    def test_get_live_chat_id_no_items(self):
        """Test handling when no video items are returned."""
        # Setup - empty items list
        self.mock_youtube.videos().list.return_value.execute.return_value = {
            "items": []
        }
        
        # Call the method - should raise ValueError
        with self.assertRaises(ValueError) as context:
            self.listener._get_live_chat_id()
        
        # Verify error message
        self.assertIn("Video not found", str(context.exception))
    
    def test_get_live_chat_id_no_streaming_details(self):
        """Test handling when no live streaming details are found."""
        # Setup - missing liveStreamingDetails
        self.mock_youtube.videos().list.return_value.execute.return_value = {
            "items": [
                {
                    # No liveStreamingDetails key
                }
            ]
        }
        
        # Call the method - should raise ValueError
        with self.assertRaises(ValueError) as context:
            self.listener._get_live_chat_id()
        
        # Verify error message
        self.assertIn("No active live chat", str(context.exception))
    
    def test_get_live_chat_id_no_chat_id(self):
        """Test handling when no active live chat ID is found."""
        # Setup - empty activeLiveChatId
        self.mock_youtube.videos().list.return_value.execute.return_value = {
            "items": [
                {
                    "liveStreamingDetails": {
                        # No activeLiveChatId key or it's None/empty
                    }
                }
            ]
        }
        
        # Call the method - should raise ValueError
        with self.assertRaises(ValueError) as context:
            self.listener._get_live_chat_id()
        
        # Verify error message
        self.assertIn("No active live chat", str(context.exception))
    
    def test_get_live_chat_id_http_error(self):
        """Test handling of HTTP errors during retrieval."""
        # Setup - YouTube API HTTP error
        http_error = HttpError(
            resp=httplib2.Response({"status": 500}),
            content=b"Server error"
        )
        self.mock_youtube.videos().list.return_value.execute.side_effect = http_error
        
        # Call the method - should propagate the HTTP error
        with self.assertRaises(HttpError):
            self.listener._get_live_chat_id()
    
    def test_get_live_chat_id_generic_error(self):
        """Test handling of unexpected errors during retrieval."""
        # Setup - generic Python exception
        generic_error = Exception("Some unexpected error")
        self.mock_youtube.videos().list.return_value.execute.side_effect = generic_error
        
        # Call the method - should wrap in ValueError
        with self.assertRaises(ValueError) as context:
            self.listener._get_live_chat_id()
        
        # Verify error message contains original error
        self.assertIn("Failed to get live chat ID", str(context.exception))
        self.assertIn("Some unexpected error", str(context.exception))
    
    @pytest.mark.asyncio
    async def test_initialize_chat_session_with_existing_id(self):
        """Test initializing chat session when live_chat_id already exists."""
        # Setup - existing chat ID
        self.listener.live_chat_id = "existing_chat_id"
        
        # Call the method
        result = await self.listener._initialize_chat_session()
        
        # Verify
        self.assertTrue(result)
        # Should not attempt to get a new ID
        self.mock_youtube.videos().list.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_initialize_chat_session_fetches_id(self):
        """Test initializing chat session by fetching a new live_chat_id."""
        # Setup
        self.listener.live_chat_id = None
        expected_chat_id = "fetched_chat_id"
        self.mock_youtube.videos().list.return_value.execute.return_value = {
            "items": [
                {
                    "liveStreamingDetails": {
                        "activeLiveChatId": expected_chat_id
                    }
                }
            ]
        }
        
        # Call the method
        result = await self.listener._initialize_chat_session()
        
        # Verify
        self.assertTrue(result)
        self.assertEqual(self.listener.live_chat_id, expected_chat_id)
    
    @pytest.mark.asyncio
    async def test_initialize_chat_session_fetch_failure(self):
        """Test initializing chat session when fetching ID fails with ValueErrors."""
        # Setup
        self.listener.live_chat_id = None
        self.mock_youtube.videos().list.return_value.execute.return_value = {
            "items": []  # Empty items will cause ValueError
        }
        
        # Call the method
        result = await self.listener._initialize_chat_session()
        
        # Verify
        self.assertFalse(result)  # Should return False on fetch failure
    
    @pytest.mark.asyncio
    async def test_initialize_chat_session_fetch_exception(self):
        """Test initializing chat session when fetching ID raises an exception."""
        # Setup
        self.listener.live_chat_id = None
        self.mock_youtube.videos().list.return_value.execute.side_effect = Exception("API error")
        
        # Call the method
        result = await self.listener._initialize_chat_session()
        
        # Verify
        self.assertFalse(result)  # Should return False on exception
    
    @pytest.mark.asyncio
    async def test_initialize_chat_session_get_id_returns_none(self):
        """Test initializing when _get_live_chat_id returns None (which shouldn't happen but we test it)."""
        # Setup - mock _get_live_chat_id to return None
        self.listener.live_chat_id = None
        with patch.object(self.listener, '_get_live_chat_id', return_value=None):
            
            # Call the method
            result = await self.listener._initialize_chat_session()
            
            # Verify
            self.assertFalse(result)  # Should return False when ID is None 
    
    def test_get_live_chat_id_empty_response(self):
        """Test handling when API returns an empty response dictionary."""
        # Setup - completely empty response
        self.mock_youtube.videos().list.return_value.execute.return_value = {}
        
        # Call the method - should raise ValueError
        with self.assertRaises(ValueError) as context:
            self.listener._get_live_chat_id()
        
        # Verify error message
        self.assertIn("Video not found", str(context.exception))
        
    def test_get_live_chat_id_with_logging(self):
        """Test that _get_live_chat_id logs the appropriate messages."""
        # Setup
        expected_chat_id = "test_chat_id_123"
        self.mock_youtube.videos().list.return_value.execute.return_value = {
            "items": [
                {
                    "liveStreamingDetails": {
                        "activeLiveChatId": expected_chat_id
                    }
                }
            ]
        }
        
        # Mock the logger to capture log messages
        with patch('modules.livechat.src.livechat.logger') as mock_logger:
            # Call the method
            result = self.listener._get_live_chat_id()
            
            # Verify log messages
            mock_logger.info.assert_any_call(f"Fetching livestream details for video ID: {self.video_id}")
            mock_logger.info.assert_any_call(f"Retrieved live chat ID: {expected_chat_id}")
            
            # Verify result
            self.assertEqual(result, expected_chat_id)
    
    def test_get_live_chat_id_when_already_set(self):
        """Test that _get_live_chat_id sets and returns a new ID even if one is already set."""
        # Setup
        self.listener.live_chat_id = "existing_chat_id"
        expected_chat_id = "new_chat_id_123"
        self.mock_youtube.videos().list.return_value.execute.return_value = {
            "items": [
                {
                    "liveStreamingDetails": {
                        "activeLiveChatId": expected_chat_id
                    }
                }
            ]
        }
        
        # Call the method
        result = self.listener._get_live_chat_id()
        
        # Verify that existing live_chat_id was overwritten and the new value returned
        self.assertEqual(result, expected_chat_id)
        self.assertEqual(self.listener.live_chat_id, expected_chat_id)
    
    def test_get_live_chat_id_all_error_conditions(self):
        """Test handling when all error conditions occur (empty items, details, and chat ID)."""
        # Test each error condition in sequence
        error_responses = [
            # 1. Empty response
            {},
            # 2. Empty items list
            {"items": []},
            # 3. No liveStreamingDetails
            {"items": [{}]},
            # 4. Empty liveStreamingDetails
            {"items": [{"liveStreamingDetails": {}}]},
            # 5. Null activeLiveChatId
            {"items": [{"liveStreamingDetails": {"activeLiveChatId": None}}]},
            # 6. Empty string activeLiveChatId
            {"items": [{"liveStreamingDetails": {"activeLiveChatId": ""}}]}
        ]
        
        for response in error_responses:
            # Setup for this test case
            self.mock_youtube.videos().list.return_value.execute.return_value = response
            
            # Call the method - should raise ValueError
            with self.assertRaises(ValueError):
                self.listener._get_live_chat_id()
    
    def test_get_live_chat_id_auth_error(self):
        """Test handling of authentication HTTP errors during retrieval."""
        # Setup - YouTube API HTTP auth error (401)
        auth_error = HttpError(
            resp=httplib2.Response({"status": 401}),
            content=b"Authentication error"
        )
        self.mock_youtube.videos().list.return_value.execute.side_effect = auth_error
        
        # Call the method - should propagate the HTTP error
        with self.assertRaises(HttpError) as context:
            self.listener._get_live_chat_id()
        
        # Verify the error status
        self.assertEqual(context.exception.resp.status, 401)
        
        # Now test with 403 Forbidden
        forbidden_error = HttpError(
            resp=httplib2.Response({"status": 403}),
            content=b"Forbidden"
        )
        self.mock_youtube.videos().list.return_value.execute.side_effect = forbidden_error
        
        # Call the method again - should propagate the HTTP error
        with self.assertRaises(HttpError) as context:
            self.listener._get_live_chat_id()
        
        # Verify the error status
        self.assertEqual(context.exception.resp.status, 403)
    
    def test_get_live_chat_id_comprehensive(self):
        """A comprehensive test that exercises the entire _get_live_chat_id method with minimal mocking."""
        
        # 1. Setup - Reset internal state and prepare responses
        self.listener.live_chat_id = None
        expected_chat_id = "comprehensive_test_chat_id"
        
        # Prepare the mock response from YouTube API
        self.mock_youtube.videos().list.return_value.execute.return_value = {
            "items": [
                {
                    "liveStreamingDetails": {
                        "activeLiveChatId": expected_chat_id
                    }
                }
            ]
        }
        
        # 2. Execute the method directly - this should execute lines 114-152
        result = self.listener._get_live_chat_id()
        
        # 3. Verify successful execution and return value
        self.assertEqual(result, expected_chat_id)
        self.assertEqual(self.listener.live_chat_id, expected_chat_id)
        
        # 4. Verify API call was made with correct parameters
        self.mock_youtube.videos().list.assert_called_with(
            part="liveStreamingDetails",
            id=self.video_id
        )
        
        # 5. Now test exception paths directly
        # 5.1 Test HttpError
        http_error = HttpError(
            resp=httplib2.Response({"status": 500}),
            content=b"Server error"
        )
        self.mock_youtube.videos().list.return_value.execute.side_effect = http_error
        
        with self.assertRaises(HttpError):
            self.listener._get_live_chat_id()
            
        # 5.2 Test ValueError propagation (empty items)
        self.mock_youtube.videos().list.return_value.execute.side_effect = None
        self.mock_youtube.videos().list.return_value.execute.return_value = {"items": []}
        
        with self.assertRaises(ValueError) as context:
            self.listener._get_live_chat_id()
        self.assertIn("Video not found", str(context.exception))
        
        # 5.3 Test ValueError propagation (no streaming details)
        self.mock_youtube.videos().list.return_value.execute.return_value = {
            "items": [{}]  # Item without liveStreamingDetails
        }
        
        with self.assertRaises(ValueError) as context:
            self.listener._get_live_chat_id()
        self.assertIn("No active live chat", str(context.exception))
        
        # 5.4 Test ValueError propagation (empty chat ID)
        self.mock_youtube.videos().list.return_value.execute.return_value = {
            "items": [{"liveStreamingDetails": {}}]  # Empty liveStreamingDetails
        }
        
        with self.assertRaises(ValueError) as context:
            self.listener._get_live_chat_id()
        self.assertIn("No active live chat", str(context.exception))
        
        # 5.5 Test generic exception handling
        generic_error = Exception("Generic error")
        self.mock_youtube.videos().list.return_value.execute.side_effect = generic_error
        
        with self.assertRaises(ValueError) as context:
            self.listener._get_live_chat_id()
        self.assertIn("Failed to get live chat ID", str(context.exception))
        
        # Reset side effect for other tests
        self.mock_youtube.videos().list.return_value.execute.side_effect = None 

    # New tests specifically targeting lines 114-152 of livechat.py
    def test_get_live_chat_id_explicit_none_activeLiveChatId(self):
        """Test handling when activeLiveChatId is explicitly None."""
        # Setup - activeLiveChatId is explicitly None
        self.mock_youtube.videos().list.return_value.execute.return_value = {
            "items": [
                {
                    "liveStreamingDetails": {
                        "activeLiveChatId": None
                    }
                }
            ]
        }
        
        # Call the method - should raise ValueError (line 136-138)
        with self.assertRaises(ValueError) as context:
            self.listener._get_live_chat_id()
        
        # Verify error message
        self.assertIn("No active live chat", str(context.exception))
    
    def test_get_live_chat_id_empty_string_activeLiveChatId(self):
        """Test handling when activeLiveChatId is an empty string."""
        # Setup - activeLiveChatId is empty string
        self.mock_youtube.videos().list.return_value.execute.return_value = {
            "items": [
                {
                    "liveStreamingDetails": {
                        "activeLiveChatId": ""
                    }
                }
            ]
        }
        
        # Call the method - should raise ValueError (line 136-138)
        with self.assertRaises(ValueError) as context:
            self.listener._get_live_chat_id()
        
        # Verify error message
        self.assertIn("No active live chat", str(context.exception))
    
    def test_get_live_chat_id_exact_error_propagation(self):
        """Test that ValueErrors are propagated exactly in the except block (lines 144-145)."""
        # Setup - create a specific ValueError
        specific_error = ValueError("Specific value error")
        self.mock_youtube.videos().list.return_value.execute.side_effect = specific_error
        
        # Call the method - should propagate the ValueError without wrapping
        with self.assertRaises(ValueError) as context:
            self.listener._get_live_chat_id()
        
        # Verify the exact error is propagated (not wrapped)
        self.assertEqual(str(context.exception), "Specific value error")
    
    def test_get_live_chat_id_error_wrapping(self):
        """Test that non-HttpError, non-ValueError exceptions are wrapped (lines 146-148)."""
        # Test various exception types
        test_exceptions = [
            TypeError("Type error"),
            KeyError("Key error"),
            AttributeError("Attribute error"),
            IndexError("Index error")
        ]
        
        for exception in test_exceptions:
            # Setup for this test case
            self.mock_youtube.videos().list.return_value.execute.side_effect = exception
            
            # Call the method - should wrap in ValueError
            with self.assertRaises(ValueError) as context:
                self.listener._get_live_chat_id()
            
            # Verify error contains both the message and the exception type
            self.assertIn("Failed to get live chat ID", str(context.exception))
            self.assertIn(str(exception), str(context.exception))
    
    def test_get_live_chat_id_http_status_codes(self):
        """Test handling of specific HTTP error status codes."""
        # Test various HTTP status codes
        status_codes = [400, 401, 403, 404, 429, 500, 503]
        
        for status_code in status_codes:
            # Setup - HTTP error with specific status code
            http_error = HttpError(
                resp=httplib2.Response({"status": status_code}),
                content=f"HTTP {status_code} error".encode()
            )
            self.mock_youtube.videos().list.return_value.execute.side_effect = http_error
            
            # Call the method - should propagate the HttpError (line 142)
            with self.assertRaises(HttpError) as context:
                self.listener._get_live_chat_id()
            
            # Verify the error has the correct status code
            self.assertEqual(context.exception.resp.status, status_code)
    
    def test_get_live_chat_id_return_exact_chat_id(self):
        """Test that the method returns the exact chat ID from the response (line 141)."""
        # Setup - various valid chat IDs
        test_chat_ids = [
            "valid_chat_id",
            "1234567890",
            "chat-id-with-special-chars_-",
            "verylongchatidverylongchatidverylongchatidverylongchatid"
        ]
        
        for chat_id in test_chat_ids:
            # Prepare response with this chat ID
            self.mock_youtube.videos().list.return_value.execute.return_value = {
                "items": [
                    {
                        "liveStreamingDetails": {
                            "activeLiveChatId": chat_id
                        }
                    }
                ]
            }
            
            # Call the method
            result = self.listener._get_live_chat_id()
            
            # Verify returned value matches exact chat ID and is set as property
            self.assertEqual(result, chat_id)
            self.assertEqual(self.listener.live_chat_id, chat_id)
    
    def test_get_live_chat_id_line_trace(self):
        """Diagnostic test to trace which lines are executed in _get_live_chat_id method."""
        import sys
        import traceback
        
        executed_lines = set()
        
        def trace_lines(frame, event, arg):
            if event == 'line':
                # Get filename and line number
                filename = frame.f_code.co_filename
                lineno = frame.f_lineno
                
                # If we're in livechat.py, record the line number
                if 'livechat.py' in filename:
                    executed_lines.add(lineno)
            return trace_lines
            
        # Set up a successful response
        expected_chat_id = "traced_chat_id"
        self.mock_youtube.videos().list.return_value.execute.return_value = {
            "items": [
                {
                    "liveStreamingDetails": {
                        "activeLiveChatId": expected_chat_id
                    }
                }
            ]
        }
        
        # Enable line tracing
        sys.settrace(trace_lines)
        
        try:
            # Call the method
            result = self.listener._get_live_chat_id()
            
            # Output traced lines for debugging
            print("\nExecuted lines in livechat.py for _get_live_chat_id:")
            for line in sorted(executed_lines):
                if 55 <= line <= 95:  # Focus on the target range for _get_live_chat_id
                    print(f"Line {line} executed")
                    
            # Verify result for completeness
            self.assertEqual(result, expected_chat_id)
            
        finally:
            # Disable tracing
            sys.settrace(None)
            
        # Verify we hit at least some lines in the target range
        lines_in_target_range = [line for line in executed_lines if 59 <= line <= 93]
        self.assertTrue(len(lines_in_target_range) > 0, 
                        f"No lines executed in target range 59-93. Executed: {sorted(executed_lines)}")

    def test_get_live_chat_id_initialization_coverage(self):
        """Test to specifically target lines 41-58 of the _get_live_chat_id method."""
        # Create a completely new instance to ensure initialization code is covered
        mock_youtube = MagicMock()
        video_id = "special_test_video_id"
        
        # Set up mock response for initialization
        mock_youtube.videos().list.return_value.execute.return_value = {
            "items": [{
                "liveStreamingDetails": {
                    "activeLiveChatId": "special_test_chat_id"
                },
                "statistics": {
                    "viewCount": "100"
                }
            }]
        }
        
        # Create a new instance with explicit values
        listener = LiveChatListener(
            youtube_service=mock_youtube,
            video_id=video_id,
            live_chat_id=None  # Force it to fetch the chat ID
        )
        
        # Now call the method on this fresh instance
        with patch('modules.livechat.src.livechat.logger') as mock_logger:
            result = listener._get_live_chat_id()
            
            # Verify the logger calls that should happen in this method
            mock_logger.info.assert_any_call(f"Fetching livestream details for video ID: {video_id}")
            mock_logger.info.assert_any_call(f"Retrieved live chat ID: {result}")
            
        # Verify the expected result
        self.assertEqual(result, "special_test_chat_id")
        self.assertEqual(listener.live_chat_id, "special_test_chat_id")
        
        # Verify the API call
        mock_youtube.videos().list.assert_called_once_with(
            part="liveStreamingDetails",
            id=video_id
        )
        
        # Now test error paths by modifying the mock
        # 1. Test when API returns empty response
        mock_youtube.videos().list.return_value.execute.return_value = {}
        with self.assertRaises(ValueError) as context:
            listener._get_live_chat_id()
        self.assertIn("Video not found", str(context.exception))
        
        # 2. Test error handling
        mock_youtube.videos().list.return_value.execute.side_effect = Exception("Test error")
        with self.assertRaises(ValueError) as context:
            listener._get_live_chat_id()
        self.assertIn("Failed to get live chat ID", str(context.exception))
        
    # New tests focusing specifically on lines 389-403 of livechat.py (_initialize_chat_session method)
    
    @pytest.mark.asyncio
    async def test_initialize_chat_session_logging_lines_389_403(self):
        """Test that _initialize_chat_session logs appropriate messages (lines 389-403)."""
        # Test case 1: When live_chat_id is None
        self.listener.live_chat_id = None
        
        # Setup for get_live_chat_id to succeed
        expected_chat_id = "new_chat_id_for_logging_test"
        self.mock_youtube.videos().list.return_value.execute.return_value = {
            "items": [
                {
                    "liveStreamingDetails": {
                        "activeLiveChatId": expected_chat_id
                    }
                }
            ]
        }
        
        # Mock logger to capture log messages
        with patch('modules.livechat.src.livechat.logger') as mock_logger:
            # Call the method
            result = await self.listener._initialize_chat_session()
            
            # Verify logged messages
            mock_logger.info.assert_any_call("No live_chat_id provided, attempting to fetch it...")
            mock_logger.info.assert_any_call(f"Successfully connected to chat ID: {expected_chat_id}")
            
            # Verify result
            self.assertTrue(result)
            self.assertEqual(self.listener.live_chat_id, expected_chat_id)
            
        # Test case 2: When live_chat_id is already set
        self.listener.live_chat_id = "existing_id_for_logging_test"
        
        # Mock logger again
        with patch('modules.livechat.src.livechat.logger') as mock_logger:
            # Call the method
            result = await self.listener._initialize_chat_session()
            
            # Verify logged messages
            mock_logger.info.assert_any_call(f"Using provided live chat ID: existing_id_for_logging_test")
            mock_logger.info.assert_any_call(f"Successfully connected to chat ID: existing_id_for_logging_test")
            
            # Verify result
            self.assertTrue(result)
    
    @pytest.mark.asyncio
    async def test_initialize_chat_session_empty_string_chat_id_lines_389_403(self):
        """Test initializing chat session when live_chat_id is an empty string (lines 389-403)."""
        # Setup - set chat ID to empty string
        self.listener.live_chat_id = ""
        
        # Mock logger
        with patch('modules.livechat.src.livechat.logger') as mock_logger:
            # Call the method
            result = await self.listener._initialize_chat_session()
            
            # Verify behavior - should attempt to fetch a new ID
            mock_logger.info.assert_any_call("No live_chat_id provided, attempting to fetch it...")
            
            # Verify the result matches the expected outcome:
            # Given how the method is written, an empty string evaluates to False
            # in the condition, so it should try to fetch a new ID
            self.assertFalse(result)  # Will be False because our mock setup doesn't provide a valid response
    
    @pytest.mark.asyncio
    async def test_initialize_chat_session_success_message_line_402(self):
        """Test that the success message is logged on line 402 when initialization succeeds."""
        # Setup - valid chat ID
        test_chat_id = "test_for_success_message"
        self.listener.live_chat_id = test_chat_id
        
        # Mock logger
        with patch('modules.livechat.src.livechat.logger') as mock_logger:
            # Call the method
            result = await self.listener._initialize_chat_session()
            
            # Verify the exact success message from line 402 is logged
            mock_logger.info.assert_called_with(f"Successfully connected to chat ID: {test_chat_id}")
            
            # Verify successful result
            self.assertTrue(result)
    
    @pytest.mark.asyncio
    async def test_initialize_chat_session_error_logging_lines_389_403(self):
        """Test error logging in lines 389-403 when _get_live_chat_id fails."""
        # Setup - chat ID is None, _get_live_chat_id will raise error
        self.listener.live_chat_id = None
        
        # Create custom error
        custom_error = ValueError("Custom fetch error")
        
        # Mock _get_live_chat_id to raise error
        with patch.object(self.listener, '_get_live_chat_id', side_effect=custom_error), \
             patch('modules.livechat.src.livechat.logger') as mock_logger:
            
            # Call the method
            result = await self.listener._initialize_chat_session()
            
            # Verify error logging
            mock_logger.error.assert_called_once_with(f"Failed to fetch live chat ID: {custom_error}")
            
            # Verify method returns False
            self.assertFalse(result)
    
    @pytest.mark.asyncio
    async def test_initialize_chat_session_detailed_branch_coverage_lines_389_403(self):
        """Thorough test covering all branches in the _initialize_chat_session method (lines 389-403)."""
        # Branch 1: live_chat_id is None - attempt to fetch and succeed
        self.listener.live_chat_id = None
        expected_chat_id = "branch_coverage_test_id"
        
        # Setup for get_live_chat_id to succeed
        with patch.object(self.listener, '_get_live_chat_id', return_value=expected_chat_id):
            result = await self.listener._initialize_chat_session()
            self.assertTrue(result)
            self.assertEqual(self.listener.live_chat_id, expected_chat_id)
        
        # Branch 2: live_chat_id is None - attempt to fetch but get None back
        self.listener.live_chat_id = None
        
        # Setup for get_live_chat_id to return None (unusual but possible case)
        with patch.object(self.listener, '_get_live_chat_id', return_value=None):
            result = await self.listener._initialize_chat_session()
            self.assertFalse(result)  # Should fail when chat ID is None
        
        # Branch 3: live_chat_id is None - attempt to fetch but exception occurs
        self.listener.live_chat_id = None
        
        # Setup for get_live_chat_id to raise exception
        with patch.object(self.listener, '_get_live_chat_id', side_effect=Exception("Test exception")):
            result = await self.listener._initialize_chat_session()
            self.assertFalse(result)  # Should fail on exception
        
        # Branch 4: live_chat_id is already set - use existing ID
        self.listener.live_chat_id = "existing_test_id"
        
        # Should not attempt to fetch
        with patch.object(self.listener, '_get_live_chat_id') as mock_get_id:
            result = await self.listener._initialize_chat_session()
            self.assertTrue(result)  # Should succeed with existing ID
            mock_get_id.assert_not_called()  # Should not call _get_live_chat_id 