"""
BanterEngine class for processing chat messages and generating responses.
"""

import logging
from typing import Optional, Dict, Tuple, List
# Correct import for sequence_responses (one level up)
from ..sequence_responses import SEQUENCE_MAP
# Removed: from .emoji_sequence_map import EmojiSequenceMap

class BanterEngine:
    def __init__(self):
        """Initialize the BanterEngine."""
        # Use the imported SEQUENCE_MAP directly
        self.sequence_map_data = SEQUENCE_MAP
        self.logger = logging.getLogger(__name__)
        # Store themes derived from tones
        self._themes = {info.get("tone", "default"): [] for info in self.sequence_map_data.values()}
        self._populate_themed_responses() # Populate responses based on map

    def _populate_themed_responses(self):
        """Populate themed responses based on SEQUENCE_MAP examples (TEMPORARY)."""
        # TODO: Replace with actual response link resolution
        default_responses = [
            "Interesting sequence! 🤔",
            "Your emoji game is strong! 💪",
            "I see what you did there! 👀"
        ]
        greeting_responses = [
            "Hey there! 👋",
            "Hello! How's it going? 😊",
            "Welcome! Great to see you! 🌟",
            "Hi! Ready for some fun? 🎉"
        ]

        self._themes["default"] = default_responses
        self._themes["greeting"] = greeting_responses
        
        for seq, info in self.sequence_map_data.items():
            tone = info.get("tone")
            example = info.get("example")
            if tone and example:
                if tone not in self._themes:
                    self._themes[tone] = []
                # Add example to the theme's response list if not already present
                if example not in self._themes[tone]:
                     self._themes[tone].append(example)
            # Add some generic responses too, perhaps?
            if tone and tone not in ["default", "greeting"]:
                 self._themes[tone].extend([f"Feeling the {tone} vibes!", f"That's some {tone} energy."])

    # --- Helper to extract emoji sequence ---
    def _extract_emoji_sequence(self, input_text: str) -> Optional[Tuple[int, int, int]]:
        """Extracts the first sequence of 3 known emojis (✊✋🖐️) from text."""
        emoji_map = {'✊': 0, '✋': 1, '🖐️': 2}
        sequence = []
        for char in input_text:
            if char in emoji_map:
                sequence.append(emoji_map[char])
                if len(sequence) == 3:
                    return tuple(sequence) # type: ignore
        return None # Return None if fewer than 3 emojis are found

    def process_input(self, input_text: str) -> Tuple[str, Optional[str]]:
        """
        Process input text, find the first 3-emoji sequence (✊✋🖐️), and return state/tone info and the specific example response.
        
        Args:
            input_text: Input text to process
            
        Returns:
            Tuple of (state/tone string, response message or None)
        """
        if not input_text:
            return "Empty input", None

        # Use the _extract_emoji_sequence method to detect emoji sequences
        sequence_tuple = self._extract_emoji_sequence(input_text)

        # If no sequence detected through extraction, try simple pattern matching
        if not sequence_tuple:
            # Example: Simulate finding a sequence based on keywords (VERY basic)
            if "✊✋🖐️" in input_text:
                 sequence_tuple = (0, 1, 2)
            elif "✊✊✊" in input_text:
                 sequence_tuple = (0, 0, 0)
            elif "✋✋✋" in input_text:
                 sequence_tuple = (1, 1, 1)
            elif "🖐️🖐️🖐️" in input_text:
                 sequence_tuple = (2, 2, 2)

        if sequence_tuple and sequence_tuple in self.sequence_map_data:
            sequence_info = self.sequence_map_data[sequence_tuple]
            state = sequence_info.get("state", "Unknown State")
            tone = sequence_info.get("tone", "default")
            result_str = f"State: {state}, Tone: {tone}"
            response = sequence_info.get("example", None)
            if response is None:
                self.logger.warning(f"No example found for sequence {sequence_tuple}, falling back to random banter for tone '{tone}'.")
                response = self.get_random_banter(theme=tone)
            return result_str, response
        else:
            if not input_text or input_text.isspace():
                return "Empty input", None
            else:
                return "No sequence detected", None

    def get_random_banter(self, theme: str = "default") -> str:
        """
        Get a random banter message for a given theme.
        
        Args:
            theme: Theme to get banter for
            
        Returns:
            Random banter message
        """
        # Get responses for theme or default
        responses = self._themes.get(theme, self._themes["default"])
        
        # Return a random response
        import random
        # Ensure responses list is not empty before choosing
        return random.choice(responses) if responses else "No response available for this theme."

    def list_themes(self) -> List[str]:
        """
        Get a list of available themes.
        
        Returns:
            list: List of available theme names
        """
        return list(self._themes.keys()) 