"""
Unit tests for emoji_sequence_map.py module.
"""

import unittest
from unittest.mock import patch, MagicMock
import logging
from modules.banter_engine.src.emoji_sequence_map import (
    EMOJI_TO_NUM,
    NUM_TO_EMOJI,
    SEQUENCE_MAP,
    emoji_string_to_tuple,
    tuple_to_emoji_string
)

class TestEmojiMappings(unittest.TestCase):
    """Test suite for emoji mappings."""

    def test_emoji_to_num_mapping(self):
        """Test the EMOJI_TO_NUM mapping is correctly defined."""
        self.assertEqual(EMOJI_TO_NUM['✊'], 1)
        self.assertEqual(EMOJI_TO_NUM['✋'], 2)
        self.assertEqual(EMOJI_TO_NUM['🖐️'], 3)
        self.assertEqual(EMOJI_TO_NUM['🖐'], 3)  # Test both with and without variation selector
        self.assertGreaterEqual(len(EMOJI_TO_NUM), 3)  # At least 3 emojis are mapped

    def test_num_to_emoji_mapping(self):
        """Test the NUM_TO_EMOJI mapping is correctly defined and is inverse of EMOJI_TO_NUM."""
        self.assertEqual(NUM_TO_EMOJI[1], '✊')
        self.assertEqual(NUM_TO_EMOJI[2], '✋')
        self.assertEqual(NUM_TO_EMOJI[3], '🖐️')  # We prefer the variation selector version
        self.assertEqual(len(NUM_TO_EMOJI), 3)  # Ensure only 3 numbers are mapped
        
        # Test lookup direction: all numbers should map to their emoji
        for num, emoji in NUM_TO_EMOJI.items():
            self.assertIn(emoji, EMOJI_TO_NUM)
            self.assertEqual(EMOJI_TO_NUM[emoji], num)

class TestSequenceMap(unittest.TestCase):
    """Test suite for the sequence mapping."""

    def test_sequence_map_structure(self):
        """Test that all sequence map entries have the required keys."""
        required_keys = ["emoji", "tone", "conscious", "unconscious", 
                         "entangled", "state", "example"]
        
        for sequence, attributes in SEQUENCE_MAP.items():
            for key in required_keys:
                self.assertIn(key, attributes, 
                             f"Key '{key}' missing from sequence {sequence}")
    
    def test_sequence_map_tuples(self):
        """Test that all keys in SEQUENCE_MAP are valid 3-element tuples."""
        for sequence in SEQUENCE_MAP.keys():
            self.assertIsInstance(sequence, tuple)
            self.assertEqual(len(sequence), 3)
            for num in sequence:
                self.assertIn(num, [1, 2, 3])  # Only valid emoji codes
    
    def test_sequence_map_emoji_consistency(self):
        """Test that the emoji field matches the tuple key."""
        for sequence, attributes in SEQUENCE_MAP.items():
            expected_emoji = "".join(NUM_TO_EMOJI[num] for num in sequence)
            self.assertEqual(attributes["emoji"], expected_emoji)

class TestEmojiStringToTuple(unittest.TestCase):
    """Test suite for emoji_string_to_tuple function."""

    def test_basic_conversion(self):
        """Test basic emoji string to tuple conversion."""
        self.assertEqual(emoji_string_to_tuple("✊✋🖐️"), (1, 2, 3))
        self.assertEqual(emoji_string_to_tuple("✊✊✊"), (1, 1, 1))
        self.assertEqual(emoji_string_to_tuple("✋✋✋"), (2, 2, 2))
        self.assertEqual(emoji_string_to_tuple("🖐️🖐️🖐️"), (3, 3, 3))
    
    def test_variation_selector(self):
        """Test handling of variation selectors."""
        # Test with variation selector
        self.assertEqual(emoji_string_to_tuple("🖐️"), (3,))
        # Test without variation selector (should still work)
        self.assertEqual(emoji_string_to_tuple("🖐"), (3,))
    
    def test_mixed_sequence(self):
        """Test mixed emoji sequence."""
        self.assertEqual(emoji_string_to_tuple("✊✋✊"), (1, 2, 1))
        self.assertEqual(emoji_string_to_tuple("🖐️✋✊"), (3, 2, 1))
    
    def test_unknown_emoji(self):
        """Test behavior with unknown emoji."""
        # Unknown emoji should map to 0
        self.assertEqual(emoji_string_to_tuple("👍"), (0,))
        # Mix of known and unknown
        self.assertEqual(emoji_string_to_tuple("✊👍✋"), (1, 0, 2))

class TestTupleToEmojiString(unittest.TestCase):
    """Test suite for tuple_to_emoji_string function."""

    def test_basic_conversion(self):
        """Test basic tuple to emoji string conversion."""
        self.assertEqual(tuple_to_emoji_string((1, 2, 3)), "✊✋🖐️")
        self.assertEqual(tuple_to_emoji_string((1, 1, 1)), "✊✊✊")
        self.assertEqual(tuple_to_emoji_string((2, 2, 2)), "✋✋✋")
        self.assertEqual(tuple_to_emoji_string((3, 3, 3)), "🖐️🖐️🖐️")
    
    def test_unknown_num(self):
        """Test behavior with unknown numbers."""
        # Unknown numbers should map to empty string
        self.assertEqual(tuple_to_emoji_string((4,)), "")
        # Mix of known and unknown
        self.assertEqual(tuple_to_emoji_string((1, 4, 2)), "✊✋")

class TestBidirectionalConversion(unittest.TestCase):
    """Test suite for bidirectional conversion between emoji strings and tuples."""

    def test_round_trip(self):
        """Test that converting from emoji to tuple and back preserves the original."""
        for emoji_sequence in ["✊✋🖐️", "✊✊✊", "✋✋✋", "🖐️🖐️🖐️"]:
            tuple_rep = emoji_string_to_tuple(emoji_sequence)
            emoji_again = tuple_to_emoji_string(tuple_rep)
            self.assertEqual(emoji_sequence, emoji_again)
    
    def test_sequence_map_lookups(self):
        """Test looking up sequences in the SEQUENCE_MAP via string conversion."""
        for sequence, attributes in SEQUENCE_MAP.items():
            emoji_string = attributes["emoji"]
            converted_tuple = emoji_string_to_tuple(emoji_string)
            self.assertEqual(converted_tuple, sequence)
            self.assertIn(converted_tuple, SEQUENCE_MAP)

if __name__ == "__main__":
    unittest.main() 