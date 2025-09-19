#!/usr/bin/env python3
"""
Test social media posting in NO-QUOTA mode
Verifies that LinkedIn/X posting works when stream is detected without API credentials
"""

import unittest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from modules.communication.livechat.src.livechat_core import LiveChatCore


class TestSocialMediaPosting(unittest.TestCase):
    """Test that social media posting works in NO-QUOTA mode"""

    def setUp(self):
        """Set up test fixtures"""
        self.video_id = "test_video_123"
        self.live_chat_id = None  # NO-QUOTA mode

    @patch('modules.communication.livechat.src.livechat_core.SimplePostingOrchestrator')
    @patch('modules.communication.livechat.src.livechat_core.logger')
    async def test_post_stream_to_linkedin_in_no_quota_mode(self, mock_logger, mock_orchestrator_class):
        """Test that _post_stream_to_linkedin works in NO-QUOTA mode"""

        # Mock the orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator

        # Create mock response
        mock_response = Mock()
        mock_response.success_count = 2
        mock_response.results = [
            Mock(success=True, platform=Mock(value='LinkedIn'), message='Posted successfully'),
            Mock(success=True, platform=Mock(value='X'), message='Posted successfully')
        ]

        # Make post_stream_notification async
        mock_orchestrator.post_stream_notification = AsyncMock(return_value=mock_response)

        # Create LiveChatCore instance without YouTube service (NO-QUOTA mode)
        livechat = LiveChatCore(
            youtube_service=None,  # NO-QUOTA mode
            video_id=self.video_id,
            live_chat_id=self.live_chat_id
        )

        # Mock session manager with stream title
        livechat.session_manager = Mock()
        livechat.session_manager.stream_title = "Test Stream Title"

        # Call the method
        await livechat._post_stream_to_linkedin()

        # Verify orchestrator was called
        mock_orchestrator_class.assert_called_once()
        mock_orchestrator.post_stream_notification.assert_called_once()

        # Verify correct parameters were passed
        call_args = mock_orchestrator.post_stream_notification.call_args
        self.assertEqual(call_args[1]['stream_title'], "Test Stream Title")
        self.assertEqual(call_args[1]['stream_url'], f"https://www.youtube.com/watch?v={self.video_id}")

        # Verify logging
        mock_logger.info.assert_any_call("[SOCIAL] Posting stream to social media platforms...")
        mock_logger.info.assert_any_call("[ORCHESTRATOR] Posting complete: 2/2 successful")

    @patch('modules.communication.livechat.src.livechat_core.record_success')
    @patch('modules.communication.livechat.src.livechat_core.SimplePostingOrchestrator')
    async def test_initialize_triggers_social_posting_no_quota(self, mock_orchestrator_class, mock_record):
        """Test that initialization triggers social posting in NO-QUOTA mode"""

        # Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_response = Mock(success_count=2, results=[])
        mock_orchestrator.post_stream_notification = AsyncMock(return_value=mock_response)

        # Create LiveChatCore instance
        livechat = LiveChatCore(
            youtube_service=None,  # NO-QUOTA mode
            video_id=self.video_id,
            live_chat_id=None
        )

        # Mock dependencies
        livechat.session_manager = AsyncMock()
        livechat.session_manager.initialize_session = AsyncMock(return_value=True)
        livechat.session_manager.send_greeting = AsyncMock()
        livechat.session_manager.live_chat_id = None
        livechat.session_manager.stream_title = "Test Stream"

        # Initialize
        result = await livechat.initialize()

        # Should return True even in NO-QUOTA mode
        self.assertTrue(result)

        # Verify social posting was triggered
        mock_orchestrator.post_stream_notification.assert_called_once()

    def test_no_quota_mode_detection(self):
        """Test that NO-QUOTA mode is properly detected"""

        # Create instance without YouTube service
        livechat = LiveChatCore(
            youtube_service=None,
            video_id=self.video_id,
            live_chat_id=None
        )

        # Should have no YouTube service
        self.assertIsNone(livechat.youtube)
        self.assertIsNone(livechat.live_chat_id)

        # But should have video_id for social posting
        self.assertEqual(livechat.video_id, self.video_id)

    @patch('modules.communication.livechat.src.livechat_core.SimplePostingOrchestrator')
    async def test_social_posting_with_duplicate_prevention(self, mock_orchestrator_class):
        """Test that duplicate posting prevention works"""

        # Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator

        # Create response indicating duplicate
        mock_response = Mock()
        mock_response.success_count = 0
        mock_response.results = [
            Mock(success=False, platform=Mock(value='LinkedIn'),
                 message='Already posted this stream')
        ]

        mock_orchestrator.post_stream_notification = AsyncMock(return_value=mock_response)

        # Create LiveChatCore instance
        livechat = LiveChatCore(
            youtube_service=None,
            video_id=self.video_id,
            live_chat_id=None
        )

        livechat.session_manager = Mock()
        livechat.session_manager.stream_title = "Test Stream"

        # Call the method
        await livechat._post_stream_to_linkedin()

        # Should handle duplicate gracefully
        mock_orchestrator.post_stream_notification.assert_called_once()


def run_async_test(coro):
    """Helper to run async tests"""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


if __name__ == '__main__':
    # Run the tests
    print("Testing social media posting in NO-QUOTA mode...")
    print("=" * 60)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSocialMediaPosting)

    # Run tests with verbosity
    runner = unittest.TextTestRunner(verbosity=2)

    # Wrap async tests
    for test in suite:
        if asyncio.iscoroutinefunction(test._testMethodName):
            original_test = getattr(test, test._testMethodName)
            wrapped = lambda self, orig=original_test: run_async_test(orig(self))
            setattr(test, test._testMethodName, wrapped)

    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("ALL TESTS PASSED!")
        print("Social media posting works correctly in NO-QUOTA mode")
    else:
        print("SOME TESTS FAILED")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")

    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)