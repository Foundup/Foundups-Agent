#!/usr/bin/env python3
"""
Test stream detection without chat_id
Verifies the fix for quota exhaustion scenarios
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE


class TestStreamDetectionNoChatId(unittest.TestCase):
    """Test that stream detection works even without chat_id"""

    def setUp(self):
        """Set up test fixtures"""
        # No need to patch SingleInstanceEnforcer since it's not imported in auto_moderator_dae
        # Just create the DAE directly
        self.dae = AutoModeratorDAE()

    @patch('modules.communication.livechat.src.auto_moderator_dae.StreamResolver')
    def test_find_livestream_accepts_stream_without_chatid(self, mock_resolver_class):
        """Test that find_livestream accepts streams even when chat_id is None"""

        # Mock the stream resolver instance
        mock_resolver = Mock()
        mock_resolver_class.return_value = mock_resolver

        # Simulate scenario: scraping found stream but no chat_id (quota exhausted)
        mock_resolver.resolve_stream.return_value = ('video123', None)

        # Initialize stream resolver
        self.dae.stream_resolver = mock_resolver

        # Call find_livestream
        result = self.dae.find_livestream()

        # Should return the stream even without chat_id
        self.assertIsNotNone(result, "Should accept stream without chat_id")
        self.assertEqual(result[0], 'video123', "Should return video_id")
        self.assertIsNone(result[1], "Chat_id should be None")

    @patch('modules.communication.livechat.src.auto_moderator_dae.StreamResolver')
    def test_find_livestream_still_requires_video_id(self, mock_resolver_class):
        """Test that find_livestream still requires video_id"""

        # Mock the stream resolver instance
        mock_resolver = Mock()
        mock_resolver_class.return_value = mock_resolver

        # Simulate scenario: no stream found
        mock_resolver.resolve_stream.return_value = None

        # Initialize stream resolver
        self.dae.stream_resolver = mock_resolver

        # Call find_livestream
        result = self.dae.find_livestream()

        # Should return None when no stream
        self.assertIsNone(result, "Should return None when no stream found")

    @patch('modules.communication.livechat.src.auto_moderator_dae.StreamResolver')
    def test_find_livestream_with_both_ids(self, mock_resolver_class):
        """Test that find_livestream still works with both video_id and chat_id"""

        # Mock the stream resolver instance
        mock_resolver = Mock()
        mock_resolver_class.return_value = mock_resolver

        # Simulate scenario: both IDs available
        mock_resolver.resolve_stream.return_value = ('video123', 'chat456')

        # Initialize stream resolver
        self.dae.stream_resolver = mock_resolver

        # Call find_livestream
        result = self.dae.find_livestream()

        # Should return both IDs
        self.assertIsNotNone(result, "Should accept stream with both IDs")
        self.assertEqual(result[0], 'video123', "Should return video_id")
        self.assertEqual(result[1], 'chat456', "Should return chat_id")

    @patch('modules.communication.livechat.src.auto_moderator_dae.logger')
    @patch('modules.communication.livechat.src.auto_moderator_dae.StreamResolver')
    def test_logging_when_chatid_missing(self, mock_resolver_class, mock_logger):
        """Test that appropriate log message appears when chat_id is missing"""

        # Mock the stream resolver instance
        mock_resolver = Mock()
        mock_resolver_class.return_value = mock_resolver

        # Simulate scenario: scraping found stream but no chat_id
        mock_resolver.resolve_stream.return_value = ('video123', None)

        # Initialize stream resolver
        self.dae.stream_resolver = mock_resolver

        # Call find_livestream
        result = self.dae.find_livestream()

        # Check that the appropriate log was called
        log_calls = [str(call) for call in mock_logger.info.call_args_list]

        # Should log that chat_id is not available
        chatid_log_found = any('Not available' in str(call) or 'quota exhausted' in str(call)
                               for call in log_calls)
        self.assertTrue(chatid_log_found, "Should log that chat_id is not available")


if __name__ == '__main__':
    # Run the tests
    print("Testing stream detection without chat_id...")
    print("=" * 60)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStreamDetectionNoChatId)

    # Run tests with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("ALL TESTS PASSED!")
        print("Stream detection will work even when quota is exhausted")
    else:
        print("SOME TESTS FAILED")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")

    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)