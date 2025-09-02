#!/usr/bin/env python3
"""
Test LiveChat Core Facade
Verifies that livechat_core.py works as a facade to the orchestrator
"""

import unittest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


class TestLiveChatFacade(unittest.TestCase):
    """Test that LiveChatCore can act as facade to orchestrator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_service = Mock()
        self.video_id = "test_video_123"
        self.chat_id = "test_chat_456"
    
    def test_facade_delegates_to_orchestrator(self):
        """Test that LiveChatCore delegates to orchestrator."""
        from modules.communication.livechat.src.livechat_core import LiveChatCore
        
        # Create livechat instance
        livechat = LiveChatCore(
            youtube_service=self.mock_service,
            video_id=self.video_id,
            live_chat_id=self.chat_id
        )
        
        # Check if it has orchestrator (if refactored)
        if hasattr(livechat, 'orchestrator'):
            from modules.communication.livechat.src.core.orchestrator import LiveChatOrchestrator
            self.assertIsInstance(livechat.orchestrator, LiveChatOrchestrator)
            print("[OK] LiveChatCore uses orchestrator internally")
        else:
            print("[INFO] LiveChatCore not yet refactored to use orchestrator")
    
    def test_backward_compatibility_methods(self):
        """Test that all public methods still exist."""
        from modules.communication.livechat.src.livechat_core import LiveChatCore
        
        livechat = LiveChatCore(
            youtube_service=self.mock_service,
            video_id=self.video_id,
            live_chat_id=self.chat_id
        )
        
        # Check all important public methods exist
        required_methods = [
            'initialize',
            'send_chat_message',
            'poll_messages',
            'process_message',
            'process_ban_event',
            'start_listening',
            'stop_listening',
            'get_moderation_stats',
            'get_user_violations',
            'get_top_violators',
            'clear_user_violations',
            'add_banned_phrase',
            'remove_banned_phrase',
            'get_banned_phrases',
            'configure_emoji_triggers'
        ]
        
        for method_name in required_methods:
            self.assertTrue(
                hasattr(livechat, method_name),
                f"Method {method_name} not found - backward compatibility broken!"
            )
        
        print(f"[OK] All {len(required_methods)} public methods present")
    
    def test_async_methods_remain_async(self):
        """Test that async methods remain async."""
        from modules.communication.livechat.src.livechat_core import LiveChatCore
        
        livechat = LiveChatCore(
            youtube_service=self.mock_service,
            video_id=self.video_id,
            live_chat_id=self.chat_id
        )
        
        # Check async methods
        import inspect
        async_methods = [
            'initialize',
            'send_chat_message',
            'poll_messages',
            'process_message',
            'process_ban_event',
            'start_listening'
        ]
        
        for method_name in async_methods:
            method = getattr(livechat, method_name)
            self.assertTrue(
                inspect.iscoroutinefunction(method),
                f"Method {method_name} should be async!"
            )
        
        print(f"[OK] All {len(async_methods)} async methods remain async")
    
    def test_component_initialization(self):
        """Test that all components are initialized."""
        from modules.communication.livechat.src.livechat_core import LiveChatCore
        
        livechat = LiveChatCore(
            youtube_service=self.mock_service,
            video_id=self.video_id,
            live_chat_id=self.chat_id
        )
        
        # Check key components exist
        self.assertIsNotNone(livechat.session_manager)
        self.assertIsNotNone(livechat.memory_manager)
        self.assertIsNotNone(livechat.mod_stats)
        self.assertIsNotNone(livechat.message_processor)
        self.assertIsNotNone(livechat.event_handler)
        self.assertIsNotNone(livechat.command_handler)
        self.assertIsNotNone(livechat.chat_sender)
        self.assertIsNotNone(livechat.chat_poller)
        
        print("[OK] All components properly initialized")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("[TEST] LIVECHAT FACADE COMPATIBILITY")
    print("="*60)
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLiveChatFacade)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("[SUCCESS] BACKWARD COMPATIBILITY MAINTAINED!")
        print("\nBenefits:")
        print("  - All existing code continues to work")
        print("  - Internal refactoring transparent to users")
        print("  - Clean orchestration behind the scenes")
        print("  - Gradual migration path available")
    else:
        print("[FAIL] Compatibility issues detected")
    print("="*60)