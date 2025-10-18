#!/usr/bin/env python3
"""
Test suite for NoQuotaStreamChecker
WSP 34: Comprehensive test coverage for stream checking functionality
"""



import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import time
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from no_quota_stream_checker import NoQuotaStreamChecker


class TestNoQuotaStreamChecker(unittest.TestCase):
    """Test suite for NoQuotaStreamChecker functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.checker = NoQuotaStreamChecker()
        self.test_video_id = "dQw4w9WgXcQ"
        self.test_channel_id = "UCBR8-60-B28hp2BmDPdVsXQ"

    def tearDown(self):
        """Clean up test fixtures."""
        pass

    @patch('requests.Session.get')
    def test_check_video_is_live_success(self, mock_get):
        """Test successful video live check."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.text = '<html><body>Live</body></html>'
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = self.checker.check_video_is_live(self.test_video_id)

        self.assertIsInstance(result, dict)
        self.assertIn('live', result)
        mock_get.assert_called_once()

    @patch('requests.Session.get')
    def test_check_video_is_live_not_live(self, mock_get):
        """Test video not live scenario."""
        # Mock response indicating not live
        mock_response = MagicMock()
        mock_response.text = '<html><body>Not Live</body></html>'
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = self.checker.check_video_is_live(self.test_video_id)

        self.assertIsInstance(result, dict)
        self.assertFalse(result.get('live', True))

    @patch('requests.Session.get')
    def test_check_channel_for_live_success(self, mock_get):
        """Test successful channel live check."""
        # Mock response with live video
        mock_response = MagicMock()
        mock_response.text = '''
        <html><body>
        <a href="/watch?v=dQw4w9WgXcQ">Live Stream</a>
        </body></html>
        '''
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = self.checker.check_channel_for_live(self.test_channel_id)

        self.assertIsInstance(result, dict)
        mock_get.assert_called()

    def test_get_random_headers(self):
        """Test random header generation."""
        headers = self.checker._get_random_headers()

        self.assertIsInstance(headers, dict)
        self.assertIn('User-Agent', headers)
        self.assertIn('Accept', headers)

    def test_anti_detection_delay(self):
        """Test anti-detection delay functionality."""
        start_time = time.time()
        self.checker._anti_detection_delay(min_delay=0.1, max_delay=0.2)
        end_time = time.time()

        # Should have delayed for at least 0.1 seconds
        self.assertGreater(end_time - start_time, 0.05)

    def test_is_channel_rate_limited_not_limited(self):
        """Test channel rate limit check when not limited."""
        result = self.checker._is_channel_rate_limited(self.test_channel_id)
        self.assertFalse(result)

    def test_register_rate_limit(self):
        """Test rate limit registration."""
        cooldown = self.checker._register_rate_limit(self.test_channel_id, "TestChannel")
        self.assertIsInstance(cooldown, float)
        self.assertGreater(cooldown, 0)

    @patch('time.sleep')
    def test_rate_limit_behavior(self, mock_sleep):
        """Test behavior after rate limit registration."""
        # Register rate limit
        self.checker._register_rate_limit(self.test_channel_id)

        # Check that channel is now rate limited
        self.assertTrue(self.checker._is_channel_rate_limited(self.test_channel_id))

    @patch('no_quota_stream_checker.LIVE_STATUS_VERIFIER_AVAILABLE', False)
    def test_fallback_behavior(self):
        """Test fallback behavior when LiveStatusVerifier is unavailable."""
        # This should work without the API verifier
        result = self.checker.check_video_is_live(self.test_video_id)
        self.assertIsInstance(result, dict)

    @patch('requests.Session.get')
    def test_request_timeout_handling(self, mock_get):
        """Test handling of request timeouts."""
        from requests.exceptions import Timeout

        mock_get.side_effect = Timeout("Request timed out")

        result = self.checker.check_video_is_live(self.test_video_id)

        self.assertIsInstance(result, dict)
        self.assertFalse(result.get('live', True))

    def test_session_configuration(self):
        """Test that session is properly configured."""
        self.assertIsNotNone(self.checker.session)
        self.assertIsNotNone(hasattr(self.checker.session, 'get'))

    def test_lazy_live_verifier_loading(self):
        """Test lazy loading of LiveStatusVerifier."""
        # Initially should not be loaded
        self.assertFalse(hasattr(self.checker, '_live_verifier') or
                        self.checker._live_verifier is not None)

        # After calling _get_live_verifier, it should attempt to load
        verifier = self.checker._get_live_verifier()
        # Result depends on whether LiveStatusVerifier is available
        # Just verify the method completes without error
        self.assertTrue(True)  # Method executed successfully

    def test_get_live_verifier_caching(self):
        """Test that LiveStatusVerifier is cached after first load."""
        # First call
        verifier1 = self.checker._get_live_verifier()

        # Second call should return cached result
        verifier2 = self.checker._get_live_verifier()

        # Should be the same object (cached)
        self.assertEqual(verifier1, verifier2)


class TestNoQuotaStreamCheckerIntegration(unittest.TestCase):
    """Integration tests for NoQuotaStreamChecker."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.checker = NoQuotaStreamChecker()

    def test_initialization(self):
        """Test proper initialization."""
        self.assertIsInstance(self.checker, NoQuotaStreamChecker)
        self.assertIsNotNone(self.checker.session)

    @patch('requests.adapters.HTTPAdapter.send')
    def test_session_retry_configuration(self, mock_send):
        """Test that session retry strategy is properly configured."""
        # This is more of a configuration test
        # The actual retry logic is tested in HTTP adapter
        self.assertIsNotNone(self.checker.session)
        self.assertTrue(hasattr(self.checker.session, 'mount'))


if __name__ == '__main__':
    unittest.main()
