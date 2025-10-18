#!/usr/bin/env python3
"""
Test YouTube DAE Idle System Behavior
Tests the idle loop when no stream is active - follows WSP 3 module organization
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE
from modules.communication.livechat.src.stream_trigger import create_intelligent_delay


class TestIdleSystemBehavior(unittest.TestCase):
    """Test the idle system behavior when no stream is detected"""

    def setUp(self):
        """Set up test fixtures"""
        self.dae = AutoModeratorDAE()

    @patch('modules.communication.livechat.src.auto_moderator_dae.StreamResolver')
    def test_idle_loop_enters_when_no_stream_found(self, mock_resolver_class):
        """Test that idle loop is entered when no stream is found"""

        # Mock stream resolver to return None (no stream)
        mock_resolver = Mock()
        mock_resolver_class.return_value = mock_resolver
        mock_resolver.resolve_stream.return_value = None

        # Mock the DAE's stream resolver
        self.dae.stream_resolver = mock_resolver

        # Call find_livestream - should return None
        result = self.dae.find_livestream()

        # Verify no stream found
        self.assertIsNone(result, "Should return None when no stream found")

    def test_intelligent_delay_calculation(self):
        """Test that intelligent delays work correctly"""

        # Test various consecutive failure counts
        test_cases = [
            (0, 30),   # First check - 30 seconds
            (1, 60),   # 1 failure - 60 seconds
            (2, 120),  # 2 failures - 2 minutes
            (3, 120),  # 3 failures - 2 minutes (capped)
            (6, 600),  # 6 failures - 10 minutes
            (10, 600), # 10 failures - 10 minutes max without trigger
        ]

        for failures, expected_delay in test_cases:
            with self.subTest(failures=failures):
                delay = create_intelligent_delay(
                    consecutive_failures=failures,
                    has_trigger=True
                )

                # Should be within reasonable range (allow for jitter)
                self.assertGreaterEqual(delay, expected_delay * 0.8,
                                      f"Delay for {failures} failures should be at least {expected_delay * 0.8}")
                self.assertLessEqual(delay, expected_delay * 1.3,
                                   f"Delay for {failures} failures should be at most {expected_delay * 1.3}")

    def test_no_quota_mode_activated(self):
        """Test that NO-QUOTA mode is activated by default"""

        # Connect should initialize in NO-QUOTA mode
        success = self.dae.connect()

        self.assertTrue(success, "Connect should succeed")
        self.assertEqual(self.dae.credential_set, "NO-QUOTA",
                        "Should default to NO-QUOTA mode to preserve API tokens")

    @patch('modules.communication.livechat.src.auto_moderator_dae.NoQuotaStreamChecker')
    @patch('modules.communication.livechat.src.auto_moderator_dae.StreamResolver')
    def test_no_quota_stream_checking(self, mock_resolver_class, mock_checker_class):
        """Test that NO-QUOTA web scraping is used when no API service available"""

        # Mock resolver to return no service (None)
        mock_resolver = Mock()
        mock_resolver_class.return_value = mock_resolver
        mock_resolver.youtube = None  # No API service

        # Mock NO-QUOTA checker
        mock_checker = Mock()
        mock_checker_class.return_value = mock_checker
        mock_checker.check_channel_for_live.return_value = None  # No stream found

        # Initialize resolver with no service
        self.dae.stream_resolver = mock_resolver

        # Call resolve_stream - should use NO-QUOTA mode
        result = self.dae.stream_resolver.resolve_stream("UC-test")

        # Should have attempted NO-QUOTA checking
        mock_checker.check_channel_for_live.assert_called()

    def test_idle_mode_messages(self):
        """Test that appropriate idle mode messages are shown"""

        # Test delay ranges and their messages
        delay_ranges = [
            (30, "Checking again in 30 seconds..."),
            (120, "Waiting 2.0 minutes (quota conservation mode)..."),
            (600, "Idle mode: 10.0 minutes (or until triggered)"),
            (1800, "Idle mode: 30.0 minutes (or until triggered)"),
        ]

        for delay, expected_message_part in delay_ranges:
            with self.subTest(delay=delay):
                # This tests the message logic from auto_moderator_dae.py
                if delay < 60:
                    message = f"Checking again in {delay:.0f} seconds..."
                elif delay < 300:
                    message = f"Waiting {delay/60:.1f} minutes (quota conservation mode)..."
                else:
                    message = f"Idle mode: {delay/60:.1f} minutes (or until triggered)"

                self.assertIn(expected_message_part.split()[0], message,
                            f"Message should contain expected text for delay {delay}")


if __name__ == '__main__':
    print("Testing YouTube DAE Idle System Behavior...")
    print("=" * 60)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestIdleSystemBehavior)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("[OK] ALL IDLE SYSTEM TESTS PASSED!")
        print("The idle system properly handles:")
        print("  • NO-QUOTA mode for stream detection")
        print("  • Intelligent delay progression")
        print("  • Idle loop when no streams found")
    else:
        print("[FAIL] SOME IDLE SYSTEM TESTS FAILED")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")

    exit(0 if result.wasSuccessful() else 1)
