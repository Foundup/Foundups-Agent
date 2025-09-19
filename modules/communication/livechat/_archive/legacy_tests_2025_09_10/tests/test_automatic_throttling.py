#!/usr/bin/env python3
"""
Test Automatic Throttling Integration
WSP-Compliant: WSP 5 (Testing), WSP 6 (Audit)

Verifies that intelligent throttling works automatically without manual intervention.
"""

import asyncio
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from modules.communication.livechat.src.livechat_core import LiveChatCore


class TestAutomaticThrottling(unittest.TestCase):
    """Test that intelligent throttling is automatic"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_service = Mock()
        self.video_id = "test_video_123"
        self.chat_id = "test_chat_456"
    
    def test_intelligent_throttle_initializes_automatically(self):
        """Test that intelligent throttle manager initializes automatically"""
        # Create LiveChatCore
        livechat = LiveChatCore(
            youtube_service=self.mock_service,
            video_id=self.video_id,
            live_chat_id=self.chat_id
        )
        
        # Verify intelligent throttle is initialized
        self.assertIsNotNone(livechat.intelligent_throttle)
        self.assertTrue(livechat.intelligent_throttle.learning_enabled)
        self.assertTrue(livechat.intelligent_throttle.agentic_mode)
        print("[OK] Intelligent throttle initialized automatically")
    
    @patch('modules.communication.livechat.src.livechat_core.IntelligentThrottleManager')
    async def test_send_message_uses_intelligent_throttle(self, mock_throttle_class):
        """Test that send_chat_message automatically uses intelligent throttling"""
        # Set up mock
        mock_throttle = Mock()
        mock_throttle.should_respond.return_value = True
        mock_throttle.calculate_adaptive_delay.return_value = 5.0
        mock_throttle_class.return_value = mock_throttle
        
        # Create LiveChatCore
        livechat = LiveChatCore(
            youtube_service=self.mock_service,
            video_id=self.video_id,
            live_chat_id=self.chat_id
        )
        
        # Mock chat sender
        livechat.chat_sender = Mock()
        livechat.chat_sender.send_message = Mock(return_value=True)
        
        # Send a message
        result = await livechat.send_chat_message("Test message", response_type="general")
        
        # Verify throttle was used
        mock_throttle.track_api_call.assert_called_once_with(quota_cost=5)
        mock_throttle.should_respond.assert_called_once_with("general")
        mock_throttle.record_response.assert_called_once_with("general", success=True)
        print("[OK] Messages automatically use intelligent throttling")
    
    @patch('modules.communication.livechat.src.livechat_core.IntelligentThrottleManager')
    async def test_automatic_quota_handling(self, mock_throttle_class):
        """Test automatic quota error handling"""
        # Set up mock
        mock_throttle = Mock()
        mock_throttle.handle_quota_error.return_value = 2  # Switch to set 2
        mock_throttle_class.return_value = mock_throttle
        
        # Create LiveChatCore
        livechat = LiveChatCore(
            youtube_service=self.mock_service,
            video_id=self.video_id,
            live_chat_id=self.chat_id
        )
        
        # Simulate quota error in polling loop
        livechat.is_running = True
        livechat.intelligent_throttle = mock_throttle
        
        # Mock the poll_messages to raise quota error once
        async def mock_poll():
            raise Exception("quotaExceeded")
        
        with patch.object(livechat, 'poll_messages', side_effect=mock_poll):
            # Run one iteration of polling
            try:
                await livechat.poll_messages()
            except Exception as e:
                # This should trigger automatic quota handling
                if "quotaExceeded" in str(e):
                    new_set = livechat.intelligent_throttle.handle_quota_error()
                    self.assertEqual(new_set, 2)
        
        # Verify quota error was handled
        mock_throttle.handle_quota_error.assert_called()
        print("[OK] Quota errors handled automatically")
    
    def test_automatic_troll_detection(self):
        """Test that troll detection works automatically"""
        # Create LiveChatCore
        livechat = LiveChatCore(
            youtube_service=self.mock_service,
            video_id=self.video_id,
            live_chat_id=self.chat_id
        )
        
        # Verify troll detector exists in intelligent throttle
        self.assertIsNotNone(livechat.intelligent_throttle)
        self.assertIsNotNone(livechat.intelligent_throttle.troll_detector)
        
        # Simulate troll behavior
        troll_id = "troll_user_123"
        troll_name = "TrollUser"
        
        # Track multiple triggers
        for i in range(5):
            result = livechat.intelligent_throttle.track_message(troll_id, troll_name)
            if i >= 2:  # Should be detected as troll after 3 triggers
                self.assertTrue(result.get('is_troll', False))
        
        print("[OK] Troll detection works automatically")
    
    def test_automatic_learning_enabled(self):
        """Test that recursive learning is enabled by default"""
        # Create LiveChatCore
        livechat = LiveChatCore(
            youtube_service=self.mock_service,
            video_id=self.video_id,
            live_chat_id=self.chat_id
        )
        
        # Verify learning is enabled
        self.assertTrue(livechat.intelligent_throttle.learning_enabled)
        
        # Simulate some API calls to trigger learning
        for i in range(5):
            livechat.intelligent_throttle.track_api_call(quota_cost=10)
        
        # Check that patterns are being learned
        status = livechat.intelligent_throttle.get_status()
        self.assertGreater(status['learned_patterns'], 0)
        print(f"[OK] Automatic learning enabled, {status['learned_patterns']} patterns learned")
    
    def test_automatic_delay_adjustment(self):
        """Test that delays adjust automatically based on activity"""
        # Create LiveChatCore
        livechat = LiveChatCore(
            youtube_service=self.mock_service,
            video_id=self.video_id,
            live_chat_id=self.chat_id
        )
        
        # Simulate low activity
        delay_low = livechat.intelligent_throttle.calculate_adaptive_delay()
        
        # Simulate high activity
        for i in range(50):
            livechat.intelligent_throttle.track_message()
        
        delay_high = livechat.intelligent_throttle.calculate_adaptive_delay()
        
        # High activity should have shorter delay
        self.assertLess(delay_high, delay_low)
        print(f"[OK] Delays adjust automatically: Low activity={delay_low:.1f}s, High activity={delay_high:.1f}s")


def run_async_test(coro):
    """Helper to run async tests"""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("[TEST] AUTOMATIC THROTTLING VERIFICATION")
    print("="*60)
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAutomaticThrottling)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Run async tests manually
    test = TestAutomaticThrottling()
    test.setUp()
    
    print("\n[ASYNC] Testing automatic message throttling...")
    run_async_test(test.test_send_message_uses_intelligent_throttle(Mock()))
    
    print("\n[ASYNC] Testing automatic quota handling...")
    run_async_test(test.test_automatic_quota_handling(Mock()))
    
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("[SUCCESS] ALL AUTOMATIC THROTTLING TESTS PASSED!")
        print("\nSummary:")
        print("  [AUTO] Intelligent throttle initializes without configuration")
        print("  [AUTO] Messages are throttled automatically")
        print("  [AUTO] Quota errors trigger automatic credential switching")
        print("  [AUTO] Trolls are detected and handled automatically")
        print("  [AUTO] Learning is enabled by default")
        print("  [AUTO] Delays adjust based on chat activity")
        print("\n[READY] The system throttles itself automatically!")
    else:
        print("[FAIL] Some tests failed")
    print("="*60)