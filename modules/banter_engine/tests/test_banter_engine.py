import logging
import sys
import os
import unittest
import locale
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent.parent.parent)
sys.path.insert(0, project_root)

from modules.banter_engine.banter_engine import BanterEngine
from modules.banter_engine.emoji_sequence_map import (
    EmojiSequenceMap,
    EMOJI_TO_NUM,
    NUM_TO_EMOJI,
    SEQUENCE_MAP,
    emoji_string_to_tuple,
    tuple_to_emoji_string
)

class TestBanterEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Try to set UTF-8 locale, but don't fail if it's not available
        try:
            if sys.platform == 'win32':
                locale.setlocale(locale.LC_ALL, 'English_United States.1252')
            else:
                locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except locale.Error:
            # If locale setting fails, continue with default locale
            pass

    def setUp(self):
        self.engine = BanterEngine()
        self.esm = EmojiSequenceMap()
        self.logger = logging.getLogger(__name__)
        # Only log warnings and errors by default
        logging.basicConfig(level=logging.WARNING)

    def test_greeting_banter(self):
        """Test BanterEngine's greeting theme functionality"""
        line = self.engine.get_random_banter(theme="greeting")
        self.assertIsInstance(line, str, "Banter line should be a string")
        self.assertTrue(len(line) > 0, "Banter line should not be empty")

    def test_theme_list(self):
        """Test BanterEngine's theme list functionality"""
        themes = self.engine.list_themes()
        self.assertIn("greeting", themes, "Missing 'greeting' theme")

    def test_esm_mapping(self):
        """Test ESM mapping validation for BanterEngine."""
        # Step 1: Validate basic emoji-to-number mapping
        self.assertEqual(EMOJI_TO_NUM['✊'], 1, "✊ should map to 1 (UN)")
        self.assertEqual(EMOJI_TO_NUM['✋'], 2, "✋ should map to 2 (DAO)")
        self.assertEqual(EMOJI_TO_NUM['🖐️'], 3, "🖐️ should map to 3 (DU)")

        # Step 2: Test known emoji combinations
        test_sequences = [
            ("✊✊✊", (1, 1, 1)),
            ("✊✋🖐️", (1, 2, 3)),
            ("✋✋✋", (2, 2, 2)),
            ("🖐️🖐️🖐️", (3, 3, 3))
        ]
        for emoji_str, expected_tuple in test_sequences:
            with self.subTest(emoji_str=emoji_str):
                result = emoji_string_to_tuple(emoji_str)
                self.assertEqual(result, expected_tuple, f"Failed to map {emoji_str} to {expected_tuple}")

        # Step 3: Validate sequence map entries
        test_states = [
            ((1, 1, 1), "fully disconnected", "extreme harsh roast"),
            ((1, 2, 3), "awakening in progress", "metaphoric, humor, symbolic wit"),
            ((2, 2, 2), "stable awareness", "reflection, calm truth"),
            ((3, 3, 3), "entangled realized / 02 state", "oracle drop / transmission")
        ]
        for sequence, expected_state, expected_tone in test_states:
            with self.subTest(sequence=sequence):
                state_info = SEQUENCE_MAP.get(sequence)
                self.assertIsNotNone(state_info, f"Sequence {sequence} not found in SEQUENCE_MAP")
                if state_info:
                    self.assertEqual(state_info.get("state"), expected_state, f"State mismatch for {sequence}")
                    self.assertEqual(state_info.get("tone"), expected_tone, f"Tone mismatch for {sequence}")

        # Step 4: Test reverse mapping
        for emoji_str, expected_tuple in test_sequences:
            with self.subTest(expected_tuple=expected_tuple):
                result = tuple_to_emoji_string(expected_tuple)
                self.assertEqual(result, emoji_str, f"Failed to map {expected_tuple} back to {emoji_str}")

    def test_esm_edge_cases(self):
        """Test edge cases for ESM mapping functionality."""
        # Test empty string
        self.assertEqual(emoji_string_to_tuple(""), (), "Empty string should return empty tuple")

        # Test string with no valid emojis
        self.assertEqual(emoji_string_to_tuple("Hello World"), (), "String with no valid emojis should return empty tuple")

        # Test string with mixed valid and invalid emojis
        mixed_input = "✊Hello✋World🖐️"
        expected = (1, 2, 3)  # Only valid emojis should be mapped
        self.assertEqual(emoji_string_to_tuple(mixed_input), expected, 
                        "Mixed input should only map valid emojis")

        # Test string with non-EMOJI_TO_NUM emojis
        other_emojis = "😊😍🥰"
        self.assertEqual(emoji_string_to_tuple(other_emojis), (), 
                        "Non-EMOJI_TO_NUM emojis should be ignored")

        # Test unknown sequence mapping
        unknown_sequence = "✊✊✋"  # (1,1,2) not in SEQUENCE_MAP
        result = self.esm.map_sequence(unknown_sequence)
        self.assertEqual(result, "Unknown sequence", 
                        "Unknown sequence should return 'Unknown sequence'")

    def test_banter_engine_edge_cases(self):
        """Test edge cases for BanterEngine functionality."""
        # Test invalid theme
        invalid_theme_result = self.engine.get_random_banter(theme="invalid_theme")
        self.assertEqual(invalid_theme_result, "", 
                        "Invalid theme should return empty string")

        # Test empty input processing
        empty_result = self.engine.process_input("")
        self.assertEqual(empty_result, "", 
                        "Empty input should return empty string")

        # Test input with no emojis
        no_emoji_result = self.engine.process_input("Hello World")
        self.assertEqual(no_emoji_result, "Unknown sequence", 
                        "Input with no emojis should return 'Unknown sequence'")

        # Test known sequence processing
        known_sequence = "✊✊✊"  # (1,1,1) -> "fully disconnected"
        known_result = self.engine.process_input(known_sequence)
        expected_result = "State: fully disconnected, Tone: extreme harsh roast"
        self.assertEqual(known_result, expected_result,
                        "Known sequence should return exact state and tone format")

    def test_emoji_sequence_mapping(self):
        """Test the EmojiSequenceMap functionality"""
        # Test basic emoji sequence
        test_sequence = "😊😍🥰"
        mapped_sequence = self.esm.map_sequence(test_sequence)
        self.assertIsInstance(mapped_sequence, str)
        self.assertTrue(len(mapped_sequence) > 0)

        # Test empty sequence
        empty_sequence = ""
        mapped_empty = self.esm.map_sequence(empty_sequence)
        self.assertEqual(mapped_empty, "")

        # Test mixed sequence
        mixed_sequence = "Hello 😊 World"
        mapped_mixed = self.esm.map_sequence(mixed_sequence)
        self.assertIsInstance(mapped_mixed, str)
        self.assertTrue(len(mapped_mixed) > 0)

    def test_banter_engine_initialization(self):
        """Test BanterEngine initialization"""
        self.assertIsInstance(self.engine, BanterEngine)
        self.assertIsNotNone(self.engine.esm)

    def test_banter_engine_emoji_handling(self):
        """Test BanterEngine's emoji handling capabilities"""
        # Test basic emoji handling
        test_input = "😊😍🥰"
        result = self.engine.process_input(test_input)
        self.assertEqual(result, "Unknown sequence",
                        "Non-mappable emojis should return 'Unknown sequence'")

        # Test known sequence handling
        known_input = "✊✋🖐️"  # (1,2,3) -> "awakening in progress"
        known_result = self.engine.process_input(known_input)
        expected_result = "State: awakening in progress, Tone: metaphoric, humor, symbolic wit"
        self.assertEqual(known_result, expected_result,
                        "Known sequence should return exact state and tone format")

if __name__ == '__main__':
    unittest.main() 