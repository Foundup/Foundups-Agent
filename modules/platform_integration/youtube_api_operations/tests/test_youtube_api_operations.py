#!/usr/bin/env python3
"""
YouTube API Operations Test Suite
WSP 13: Comprehensive test coverage for YouTube API operations
"""

import unittest
from unittest.mock import MagicMock, patch, call
import sys
import os

# Add module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from modules.platform_integration.youtube_api_operations.src.youtube_api_operations import YouTubeAPIOperations


class TestYouTubeAPIOperations(unittest.TestCase):
    """Test suite for YouTubeAPIOperations class."""

    def setUp(self):
        """Set up test fixtures."""
        self.api_ops = YouTubeAPIOperations()
        self.mock_youtube = MagicMock()
        self.mock_circuit_breaker = MagicMock()

        # Create instance with circuit breaker
        self.api_ops_with_cb = YouTubeAPIOperations(circuit_breaker=self.mock_circuit_breaker)

    def test_initialization_without_circuit_breaker(self):
        """Test initialization without circuit breaker."""
        api_ops = YouTubeAPIOperations()
        self.assertIsNone(api_ops.circuit_breaker)

    def test_initialization_with_circuit_breaker(self):
        """Test initialization with circuit breaker."""
        circuit_breaker = MagicMock()
        api_ops = YouTubeAPIOperations(circuit_breaker=circuit_breaker)
        self.assertEqual(api_ops.circuit_breaker, circuit_breaker)

    def test_check_video_details_enhanced_success(self):
        """Test successful video details checking."""
        # Mock successful API response
        mock_response = {
            'items': [{
                'snippet': {
                    'title': 'Test Stream',
                    'channelId': 'UC123456789',
                    'liveBroadcastContent': 'live'
                },
                'liveStreamingDetails': {
                    'activeLiveChatId': 'CHAT123'
                },
                'status': {'privacyStatus': 'public'}
            }]
        }

        self.mock_youtube.videos.return_value.list.return_value.execute.return_value = mock_response

        # Mock circuit breaker call
        self.mock_circuit_breaker.call.return_value = mock_response

        result = self.api_ops_with_cb.check_video_details_enhanced(self.mock_youtube, 'VIDEO_ID')

        # Verify circuit breaker was called
        self.mock_circuit_breaker.call.assert_called_once()

        # Verify result structure
        self.assertIsNotNone(result)
        self.assertEqual(result['title'], 'Test Stream')
        self.assertEqual(result['channel_id'], 'UC123456789')
        self.assertEqual(result['live_status'], 'live')

    def test_check_video_details_enhanced_no_items(self):
        """Test video details checking when no items returned."""
        mock_response = {'items': []}
        self.mock_youtube.videos.return_value.list.return_value.execute.return_value = mock_response
        self.mock_circuit_breaker.call.return_value = mock_response

        result = self.api_ops_with_cb.check_video_details_enhanced(self.mock_youtube, 'VIDEO_ID')

        self.assertIsNone(result)

    def test_check_video_details_enhanced_invalid_params(self):
        """Test video details checking with invalid parameters."""
        result = self.api_ops.check_video_details_enhanced(None, None)
        self.assertIsNone(result)

        result = self.api_ops.check_video_details_enhanced(self.mock_youtube, None)
        self.assertIsNone(result)

    def test_check_video_details_enhanced_circuit_breaker_failure(self):
        """Test video details checking when circuit breaker fails."""
        self.mock_circuit_breaker.call.side_effect = Exception("Circuit breaker open")

        result = self.api_ops_with_cb.check_video_details_enhanced(self.mock_youtube, 'VIDEO_ID')

        self.assertIsNone(result)

    def test_search_livestreams_enhanced_success(self):
        """Test successful livestream search."""
        mock_response = {
            'items': [{
                'id': {'videoId': 'VIDEO123'},
                'snippet': {
                    'title': 'Live Stream',
                    'publishedAt': '2025-01-01T00:00:00Z'
                }
            }]
        }

        self.mock_youtube.search.return_value.list.return_value.execute.return_value = mock_response
        self.mock_circuit_breaker.call.return_value = mock_response

        result = self.api_ops_with_cb.search_livestreams_enhanced(self.mock_youtube, 'CHANNEL_ID')

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['video_id'], 'VIDEO123')
        self.assertEqual(result[0]['title'], 'Live Stream')

    def test_search_livestreams_enhanced_empty_results(self):
        """Test livestream search with no results."""
        mock_response = {'items': []}
        self.mock_youtube.search.return_value.list.return_value.execute.return_value = mock_response
        self.mock_circuit_breaker.call.return_value = mock_response

        result = self.api_ops_with_cb.search_livestreams_enhanced(self.mock_youtube, 'CHANNEL_ID')

        self.assertEqual(result, [])

    def test_search_livestreams_enhanced_invalid_params(self):
        """Test livestream search with invalid parameters."""
        result = self.api_ops.search_livestreams_enhanced(None, None)
        self.assertEqual(result, [])

        result = self.api_ops.search_livestreams_enhanced(self.mock_youtube, None)
        self.assertEqual(result, [])

    def test_get_active_livestream_video_id_enhanced_success(self):
        """Test successful active livestream detection."""
        # Mock search response
        search_response = {
            'items': [{
                'id': {'videoId': 'VIDEO123'},
                'snippet': {'title': 'Live Stream'}
            }]
        }

        # Mock video details response
        video_response = {
            'items': [{
                'snippet': {'liveBroadcastContent': 'live'},
                'liveStreamingDetails': {'activeLiveChatId': 'CHAT123'}
            }]
        }

        self.mock_youtube.search.return_value.list.return_value.execute.return_value = search_response
        self.mock_youtube.videos.return_value.list.return_value.execute.return_value = video_response

        # Mock circuit breaker calls
        self.mock_circuit_breaker.call.side_effect = [search_response, video_response]

        result = self.api_ops_with_cb.get_active_livestream_video_id_enhanced(self.mock_youtube, 'CHANNEL_ID')

        self.assertEqual(result, ('VIDEO123', 'CHAT123'))

    def test_get_active_livestream_video_id_enhanced_no_live_streams(self):
        """Test active livestream detection when no live streams found."""
        # Mock search response with non-live video
        search_response = {
            'items': [{
                'id': {'videoId': 'VIDEO123'},
                'snippet': {'title': 'Past Stream'}
            }]
        }

        video_response = {
            'items': [{
                'snippet': {'liveBroadcastContent': 'none'}
            }]
        }

        self.mock_youtube.search.return_value.list.return_value.execute.return_value = search_response
        self.mock_youtube.videos.return_value.list.return_value.execute.return_value = video_response

        self.mock_circuit_breaker.call.side_effect = [search_response, video_response]

        result = self.api_ops_with_cb.get_active_livestream_video_id_enhanced(self.mock_youtube, 'CHANNEL_ID')

        self.assertIsNone(result)

    def test_get_active_livestream_video_id_enhanced_live_no_chat(self):
        """Test active livestream detection when live but no chat."""
        search_response = {
            'items': [{
                'id': {'videoId': 'VIDEO123'},
                'snippet': {'title': 'Live Stream'}
            }]
        }

        video_response = {
            'items': [{
                'snippet': {'liveBroadcastContent': 'live'},
                'liveStreamingDetails': {}  # No chat ID
            }]
        }

        self.mock_youtube.search.return_value.list.return_value.execute.return_value = search_response
        self.mock_youtube.videos.return_value.list.return_value.execute.return_value = video_response

        self.mock_circuit_breaker.call.side_effect = [search_response, video_response]

        result = self.api_ops_with_cb.get_active_livestream_video_id_enhanced(self.mock_youtube, 'CHANNEL_ID')

        self.assertEqual(result, ('VIDEO123', None))

    def test_get_active_livestream_video_id_enhanced_invalid_params(self):
        """Test active livestream detection with invalid parameters."""
        result = self.api_ops.get_active_livestream_video_id_enhanced(None, None)
        self.assertIsNone(result)

        result = self.api_ops.get_active_livestream_video_id_enhanced(self.mock_youtube, None)
        self.assertIsNone(result)

    def test_execute_api_fallback_search_success(self):
        """Test complete API fallback search execution."""
        # Mock the individual method calls
        with patch.object(self.api_ops, 'get_active_livestream_video_id_enhanced') as mock_get_active:
            mock_get_active.return_value = ('VIDEO123', 'CHAT123')

            result = self.api_ops.execute_api_fallback_search(self.mock_youtube, 'CHANNEL_ID')

            mock_get_active.assert_called_once_with(self.mock_youtube, 'CHANNEL_ID')
            self.assertEqual(result, ('VIDEO123', 'CHAT123'))

    def test_execute_api_fallback_search_no_service(self):
        """Test API fallback search with no YouTube service."""
        result = self.api_ops.execute_api_fallback_search(None, 'CHANNEL_ID')
        self.assertIsNone(result)

    def test_execute_api_fallback_search_failure(self):
        """Test API fallback search when method fails."""
        with patch.object(self.api_ops, 'get_active_livestream_video_id_enhanced') as mock_get_active:
            mock_get_active.side_effect = Exception("API Error")

            with self.assertRaises(Exception):
                self.api_ops.execute_api_fallback_search(self.mock_youtube, 'CHANNEL_ID')

    def test_circuit_breaker_integration(self):
        """Test that circuit breaker is properly integrated."""
        # Test without circuit breaker
        api_ops_no_cb = YouTubeAPIOperations()
        self.assertIsNone(api_ops_no_cb.circuit_breaker)

        # Test with circuit breaker
        self.assertEqual(self.api_ops_with_cb.circuit_breaker, self.mock_circuit_breaker)

    def test_error_handling_api_exceptions(self):
        """Test error handling for API exceptions."""
        # Mock API exception
        self.mock_youtube.videos.return_value.list.return_value.execute.side_effect = Exception("API Error")
        self.mock_circuit_breaker.call.side_effect = Exception("API Error")

        result = self.api_ops_with_cb.check_video_details_enhanced(self.mock_youtube, 'VIDEO_ID')

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
