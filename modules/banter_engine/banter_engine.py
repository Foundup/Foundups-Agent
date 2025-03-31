"""
BanterEngine class for processing chat messages and generating responses.
"""

import logging
from typing import Optional, Dict, Tuple
from .emoji_sequence_map import EmojiSequenceMap

class BanterEngine:
    def __init__(self):
        """Initialize the BanterEngine."""
        self.sequence_map = EmojiSequenceMap()
        self.logger = logging.getLogger(__name__)

    def process_input(self, input_text: str) -> Tuple[str, Optional[str]]:
        """
        Process input text and return state/tone info and response message.
        
        Args:
            input_text: Input text to process
            
        Returns:
            Tuple of (state/tone string, response message or None)
        """
        if not input_text:
            return "Unknown sequence", None
            
        # Get sequence mapping result
        result = self.sequence_map.map_sequence(input_text)
        
        # If it's an unknown sequence, return early
        if result == "Unknown sequence":
            return result, None
            
        # Extract tone from result (e.g., "metaphoric, humor, symbolic wit")
        tone = result.split("Tone: ")[1].strip()
        
        # Get a themed response based on the tone
        response = self.get_random_banter(theme=tone)
        
        return result, response

    def get_random_banter(self, theme: str = "default") -> str:
        """
        Get a random banter message for a given theme.
        
        Args:
            theme: Theme to get banter for
            
        Returns:
            Random banter message
        """
        # Example themed responses
        themed_responses = {
            "greeting": [
                "Hey there! 👋",
                "Hello! How's it going? 😊",
                "Welcome! Great to see you! 🌟",
                "Hi! Ready for some fun? 🎉"
            ],
            "metaphoric, humor, symbolic wit": [
                "Ah, I see you're speaking in riddles! 🎭",
                "Your emoji poetry is quite profound! ✨",
                "The symbols speak volumes! 🎯"
            ],
            "extreme harsh roast": [
                "Oh, you're trying to roast me? How cute! 🔥",
                "Your emoji game needs work! 😏",
                "Nice try, but I've seen better! 💅"
            ],
            "reflection, calm truth": [
                "Your message resonates deeply. 🌊",
                "The truth flows through your emojis. 🌟",
                "A moment of clarity in the chat. ✨"
            ],
            "oracle drop / transmission": [
                "The prophecy unfolds! 🔮",
                "Ancient wisdom flows through your message. 🌌",
                "The cosmic signals are clear! 🌠"
            ],
            "default": [
                "Interesting sequence! 🤔",
                "Your emoji game is strong! 💪",
                "I see what you did there! 👀"
            ]
        }
        
        # Get responses for theme or default
        responses = themed_responses.get(theme, themed_responses["default"])
        
        # Return a random response
        import random
        return random.choice(responses)

    def list_themes(self) -> list:
        """
        Get a list of available themes.
        
        Returns:
            list: List of available theme names
        """
        return list(self._themes.keys()) 