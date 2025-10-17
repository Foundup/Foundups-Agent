#!/usr/bin/env python3
"""
Test Suite for No-Quota Stream Checker Anti-Rate-Limiting Features
WSP 87: Comprehensive tests for enhanced anti-detection measures
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import unittest
from unittest.mock import Mock, patch, MagicMock, call
import requests
import time
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.no_quota_stream_checker import NoQuotaStreamChecker


class TestAntiRateLimiting(unittest.TestCase):
    """Test anti-rate-limiting features of NoQuotaStreamChecker"""

    def setUp(self):
        """Set up test fixtures"""
        self.checker = NoQuotaStreamChecker()

    def test_user_agent_rotation(self):
        """Test that User-Agent rotates randomly"""
        # Get multiple headers
        headers_list = [self.checker._get_random_headers() for _ in range(10)]
        user_agents = [h['User-Agent'] for h in headers_list]

        # Should have multiple different User-Agents
        unique_agents = set(user_agents)
        self.assertGreater(len(unique_agents), 1, "User-Agent should rotate")

        # All should be from our pool
        for agent in unique_agents:
            self.assertIn(agent, self.checker.USER_AGENTS)

    def test_headers_completeness(self):
        """Test that all required headers are present"""
        headers = self.checker._get_random_headers()

        # Check all required headers
        required_headers = [
            'User-Agent', 'Accept', 'Accept-Language', 'Accept-Encoding',
            'DNT', 'Connection', 'Upgrade-Insecure-Requests',
            'Sec-Fetch-Dest', 'Sec-Fetch-Mode', 'Sec-Fetch-Site',
            'Cache-Control'
        ]

        for header in required_headers:
            self.assertIn(header, headers, f"Missing required header: {header}")

    def test_anti_detection_delay(self):
        """Test that delays are properly randomized"""
        delays = []

        # Mock time.sleep to capture delays
        with patch('time.sleep') as mock_sleep:
            for _ in range(10):
                self.checker._anti_detection_delay()

            # Get all delay values
            delays = [call[0][0] for call in mock_sleep.call_args_list]

        # All delays should be between 2.0 and 5.0 seconds
        for delay in delays:
            self.assertGreaterEqual(delay, 2.0, "Delay too short")
            self.assertLessEqual(delay, 5.0, "Delay too long")

        # Delays should vary (not all the same)
        unique_delays = set(delays)
        self.assertGreater(len(unique_delays), 5, "Delays should be randomized")

    def test_retry_strategy_setup(self):
        """Test that retry strategy is properly configured"""
        # Check that HTTPAdapter is mounted
        self.assertIsNotNone(self.checker.session.adapters)

        # Check both http and https adapters
        http_adapter = self.checker.session.get_adapter('http://example.com')
        https_adapter = self.checker.session.get_adapter('https://example.com')

        self.assertIsNotNone(http_adapter)
        self.assertIsNotNone(https_adapter)

        # Check retry configuration
        self.assertIsNotNone(http_adapter.max_retries)
        self.assertEqual(http_adapter.max_retries.total, 3)
        self.assertIn(429, http_adapter.max_retries.status_forcelist)

    @patch('requests.Session.get')
    def test_check_video_with_anti_detection(self, mock_get):
        """Test that video checking uses anti-detection measures"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
            <html>
                <title>Test Video - YouTube</title>
                <script>var ytInitialData = {"contents": {}};</script>
            </html>
        '''
        mock_get.return_value = mock_response

        # Mock the delay
        with patch.object(self.checker, '_anti_detection_delay') as mock_delay:
            result = self.checker.check_video_is_live('test_video_id')

            # Delay should be called
            mock_delay.assert_called_once()

            # Headers should be set
            call_args = mock_get.call_args
            self.assertIn('headers', call_args[1])
            headers = call_args[1]['headers']
            self.assertIn('User-Agent', headers)

    @patch('requests.Session.get')
    def test_rate_limit_handling(self, mock_get):
        """Test handling of 429 rate limit errors"""
        # Mock 429 response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = requests.HTTPError("429")
        mock_get.return_value = mock_response

        with patch.object(self.checker, '_anti_detection_delay'):
            result = self.checker.check_video_is_live('test_video_id')

            # Should handle error gracefully
            self.assertFalse(result['live'])
            self.assertIn('error', result)
            self.assertIn('429', result['error'])

    @patch('requests.Session.get')
    def test_channel_check_with_delays(self, mock_get):
        """Test that channel checking adds delays between video checks"""
        # Mock channel page with multiple videos
        channel_response = Mock()
        channel_response.status_code = 200
        channel_response.url = 'https://www.youtube.com/channel/test/streams'
        channel_response.text = '''
            "videoId":"video1"
            "videoId":"video2"
            "videoId":"video3"
        '''

        # Mock video responses (all not live)
        video_response = Mock()
        video_response.status_code = 200
        video_response.text = '<html><title>Video - YouTube</title></html>'

        mock_get.side_effect = [channel_response, video_response, video_response, video_response]

        with patch.object(self.checker, '_anti_detection_delay') as mock_delay:
            result = self.checker.check_channel_for_live('test_channel_id')

            # Should call delay at least twice (channel check + streams check)
            # Additional delays depend on implementation details
            self.assertGreaterEqual(mock_delay.call_count, 2)

    def test_cookie_persistence(self):
        """Test that cookies are persisted in session"""
        # Check cookie jar exists
        self.assertIsNotNone(self.checker.session.cookies)
        self.assertIsInstance(self.checker.session.cookies, requests.cookies.RequestsCookieJar)

    def test_timeout_values(self):
        """Test that timeout values are appropriate"""
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = '<html></html>'
            mock_get.return_value = mock_response

            with patch.object(self.checker, '_anti_detection_delay'):
                self.checker.check_video_is_live('test_id')

                # Check timeout is 15 seconds
                call_args = mock_get.call_args
                self.assertEqual(call_args[1]['timeout'], 15)

    @patch('requests.Session.get')
    def test_exponential_backoff_on_errors(self, mock_get):
        """Test that exponential backoff works for repeated errors"""
        # This is handled by urllib3.util.retry.Retry internally
        # We can verify the configuration
        adapter = self.checker.session.get_adapter('https://youtube.com')
        retry = adapter.max_retries

        # Check backoff factor
        self.assertEqual(retry.backoff_factor, 2)
        self.assertTrue(retry.respect_retry_after_header)

        # Check status codes that trigger retry
        self.assertIn(429, retry.status_forcelist)
        self.assertIn(500, retry.status_forcelist)
        self.assertIn(502, retry.status_forcelist)
        self.assertIn(503, retry.status_forcelist)
        self.assertIn(504, retry.status_forcelist)


class TestLiveStreamDetection(unittest.TestCase):
    """Test live stream detection logic"""

    def setUp(self):
        """Set up test fixtures"""
        self.checker = NoQuotaStreamChecker()

    @patch('requests.Session.get')
    def test_live_stream_detection(self, mock_get):
        """Test detection of actually live streams"""
        # Mock response with live indicators
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
            <html>
                <title>LIVE NOW - Test Stream - YouTube</title>
                <script>
                    "isLiveNow":true
                    "BADGE_STYLE_TYPE_LIVE_NOW"
                    "watching now</span>"
                    "label":"LIVE"
                    var ytInitialData = {"contents": {}};
                </script>
            </html>
        '''
        mock_get.return_value = mock_response

        with patch.object(self.checker, '_anti_detection_delay'):
            result = self.checker.check_video_is_live('live_video_id')

            # Should detect as live
            self.assertTrue(result['live'], "Should detect live stream")

    @patch('requests.Session.get')
    def test_ended_stream_detection(self, mock_get):
        """Test detection of ended streams"""
        # Mock response with ended indicators
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
            <html>
                <title>Was Live - Test Stream - YouTube</title>
                <script>
                    "isLiveContent":false
                    "liveBroadcastDetails":{"hasDisplayedEndscreen":true
                    var ytInitialData = {"contents": {}};
                </script>
            </html>
        '''
        mock_get.return_value = mock_response

        with patch.object(self.checker, '_anti_detection_delay'):
            result = self.checker.check_video_is_live('ended_video_id')

            # Should detect as not live
            self.assertFalse(result['live'], "Should detect ended stream")


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""

    @patch('requests.Session.get')
    def test_full_stream_check_workflow(self, mock_get):
        """Test complete workflow from channel to live detection"""
        checker = NoQuotaStreamChecker()

        # Mock channel redirects to live video
        channel_response = Mock()
        channel_response.status_code = 200
        channel_response.url = 'https://www.youtube.com/watch?v=live123'

        # Mock live video response
        video_response = Mock()
        video_response.status_code = 200
        video_response.text = '''
            <html>
                <title>LIVE - Stream - YouTube</title>
                <script>
                    "isLiveNow":true
                    "BADGE_STYLE_TYPE_LIVE_NOW"
                    "watching now</span>"
                </script>
            </html>
        '''

        mock_get.side_effect = [channel_response, video_response]

        with patch.object(checker, '_anti_detection_delay'):
            result = checker.check_channel_for_live('test_channel')

            # Should find live stream
            self.assertIsNotNone(result)
            self.assertTrue(result['live'])
            self.assertEqual(result['video_id'], 'live123')


def run_tests():
    """Run all tests with detailed output"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAntiRateLimiting))
    suite.addTests(loader.loadTestsFromTestCase(TestLiveStreamDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return success status
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)