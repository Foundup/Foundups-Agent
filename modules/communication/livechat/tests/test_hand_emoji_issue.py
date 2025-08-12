"""
Test specifically for the 🖐🖐🖐 emoji sequence issue
This tests the exact scenario where the user types three hand emojis without variation selector
"""

import unittest
from modules.communication.livechat.src.livechat import LiveChatListener
from modules.ai_intelligence.banter_engine.src.banter_engine import BanterEngine
from unittest.mock import MagicMock, patch
import logging

class TestHandEmojiIssue(unittest.TestCase):
    """Test the specific issue with 🖐🖐🖐 emoji sequence detection"""
    
    def setUp(self):
        """Set up test fixtures"""
        logging.disable(logging.CRITICAL)
        
        # Create mock YouTube service
        self.mock_youtube = MagicMock()
        self.video_id = "test_video_id"
        self.live_chat_id = "test_live_chat_id"
        
        # Create LiveChatListener instance
        self.listener = LiveChatListener(
            youtube_service=self.mock_youtube,
            video_id=self.video_id,
            live_chat_id=self.live_chat_id
        )
        
        # Create real BanterEngine to test integration
        self.real_banter = BanterEngine()
    
    def test_hand_emoji_without_variation_selector(self):
        """Test that 🖐🖐🖐 (without variation selector) is detected"""
        # Test the exact string the user would type
        user_message = "🖐🖐🖐"
        
        # Check if the trigger is detected
        result = self.listener._check_trigger_patterns(user_message)
        self.assertTrue(result, "Failed to detect 🖐🖐🖐 without variation selector")
        
    def test_hand_emoji_with_variation_selector(self):
        """Test that 🖐️🖐️🖐️ (with variation selector) is also detected"""
        # Test with variation selector
        user_message = "🖐️🖐️🖐️"
        
        # Check if the trigger is detected  
        result = self.listener._check_trigger_patterns(user_message)
        self.assertTrue(result, "Failed to detect 🖐️🖐️🖐️ with variation selector")
        
    def test_hand_emoji_in_sentence(self):
        """Test detection when emoji sequence is embedded in text"""
        test_messages = [
            "Hey everyone 🖐🖐🖐",
            "🖐🖐🖐 what's up",
            "Check this out 🖐🖐🖐 cool right?"
        ]
        
        for msg in test_messages:
            with self.subTest(msg=msg):
                result = self.listener._check_trigger_patterns(msg)
                self.assertTrue(result, f"Failed to detect emoji in: {msg}")
    
    def test_banter_engine_processes_hand_emoji(self):
        """Test that BanterEngine can process the hand emoji sequence"""
        # Test with real BanterEngine
        test_message = "Hey 🖐🖐🖐"
        
        # Process the input
        result, response = self.real_banter.process_input(test_message)
        
        # Check that a valid response was generated
        self.assertIsNotNone(response, "BanterEngine returned None for 🖐🖐🖐")
        self.assertTrue(isinstance(response, str), "Response should be a string")
        self.assertTrue(len(response) > 0, "Response should not be empty")
        
        # The exact response will vary, but it should be one of the valid responses
        print(f"BanterEngine response for '🖐🖐🖐': {response}")
        
    def test_mixed_emoji_sequences(self):
        """Test various emoji sequences including the problematic one"""
        sequences_to_test = [
            ("✊✊✊", True),
            ("✋✋✋", True),
            ("🖐🖐🖐", True),  # The problematic one without variation selector
            ("🖐️🖐️🖐️", True),  # With variation selector
            ("✊✋🖐", True),  # Mixed sequence without selector
            ("✊✋🖐️", True),  # Mixed sequence with selector on last
            ("👍👍👍", False),  # Different emoji, should not trigger
            ("🖐🖐", False),  # Only two hands, should not trigger
        ]
        
        for sequence, should_trigger in sequences_to_test:
            with self.subTest(sequence=sequence):
                result = self.listener._check_trigger_patterns(sequence)
                if should_trigger:
                    self.assertTrue(result, f"Should have detected: {sequence}")
                else:
                    self.assertFalse(result, f"Should not have detected: {sequence}")

if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)