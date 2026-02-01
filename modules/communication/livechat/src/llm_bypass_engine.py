"""
LLM Bypass Engine - WSP Compliant
Provides fallback responses when LLM is unavailable

NAVIGATION: Supplies fallback answers for message processor.
-> Called by: message_processor.py when Grok unavailable or throttled
-> Delegates to: simple_fact_checker, static response patterns
-> Related: NAVIGATION.py -> NEED_TO["fallback fact response"]
-> Quick ref: NAVIGATION.py -> PROBLEMS["LLM unavailable"]
"""

import logging
import random
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class LLMBypassEngine:
    """
    Simplified response engine that provides reliable emoji sequence responses
    Used as a fallback when the main banter engine returns empty/invalid responses
    """
    
    def __init__(self):
        """Initialize the LLM bypass engine with direct response mappings"""
        # Direct emoji sequence to response mapping
        self.direct_responses = {
            (0, 0, 0): "You don't love America—you cosplay it.",  # ✊✊✊
            (1, 1, 1): "Still, focused, dangerous—good.",         # ✋✋✋
            (0, 1, 2): "You stepped off the wheel. Welcome.",     # ✊✋🖐️
            (2, 2, 2): "You're not hearing me. You are me.",      # 🖐️🖐️🖐️
            (0, 1, 1): "You almost sound like you're listening.", # ✊✋✋
            (0, 0, 1): "Still loud, but you looked up. That's a start.", # ✊✊✋
            (0, 0, 2): "It hit you like thunder. Let it echo.",   # ✊✊🖐️
            (1, 1, 2): "The noise fades. Truth hums.",            # ✋✋🖐️
            (1, 2, 2): "You shape the field now.",               # ✋🖐️🖐️
        }
        
        # Fallback responses by tone category
        self.tone_fallbacks = {
            "harsh": [
                "You're not even wrong—you're just confused.",
                "That's a fascinating way to be wrong.",
                "You're operating on borrowed confidence."
            ],
            "calm": [
                "Consider the deeper pattern here.",
                "You're beginning to see it.",
                "The noise fades when you stop feeding it."
            ],
            "wit": [
                "You're stepping off the carousel.",
                "The game changed. You noticed.",
                "Welcome to the other side of the mirror."
            ],
            "oracle": [
                "You're not separate from this.",
                "The observer and observed collapse.",
                "There is no 'you' hearing this."
            ],
            "default": [
                "Interesting sequence detected! 🤔",
                "That's a meaningful gesture! ✨",
                "I see what you did there! 👀"
            ]
        }
        
        logger.info("LLMBypassEngine initialized with direct response mappings")
    
    def _extract_emoji_sequence(self, input_text: str) -> Optional[Tuple[int, int, int]]:
        """
        Extract emoji sequence from text using the same logic as banter engine
        
        Args:
            input_text: Text to analyze
            
        Returns:
            Tuple of (emoji1, emoji2, emoji3) as integers, or None if not found
        """
        emoji_map = {'✊': 0, '👊': 0, '✋': 1, '🖐️': 2}
        sequence = []
        
        for char in input_text:
            if char in emoji_map:
                sequence.append(emoji_map[char])
                if len(sequence) == 3:
                    return tuple(sequence)
        return None
    
    def _pattern_match_sequences(self, input_text: str) -> Optional[Tuple[int, int, int]]:
        """
        Simple pattern matching for emoji sequences as fallback
        
        Args:
            input_text: Text to check for patterns
            
        Returns:
            Matched sequence tuple or None
        """
        patterns = {
            "✊✊✊": (0, 0, 0),
            "✋✋✋": (1, 1, 1),
            "🖐️🖐️🖐️": (2, 2, 2),
            "✊✋🖐️": (0, 1, 2),
            "✊✋✋": (0, 1, 1),
            "✊✊✋": (0, 0, 1),
            "✊✊🖐️": (0, 0, 2),
            "✋✋🖐️": (1, 1, 2),
            "✋🖐️🖐️": (1, 2, 2)
        }
        
        for pattern, sequence in patterns.items():
            if pattern in input_text:
                return sequence
        return None
    
    def process_input(self, input_text: str) -> Tuple[str, Optional[str]]:
        """
        Process input text and return a reliable response
        
        Args:
            input_text: The message to process
            
        Returns:
            Tuple of (state_info, response_text)
        """
        if not input_text or input_text.isspace():
            return "Empty input", None
        
        # Try to extract sequence using character-by-character analysis
        sequence_tuple = self._extract_emoji_sequence(input_text)
        
        # Fallback to pattern matching
        if not sequence_tuple:
            sequence_tuple = self._pattern_match_sequences(input_text)
        
        if sequence_tuple:
            logger.debug(f"LLM Bypass detected sequence: {sequence_tuple}")
            
            # Get direct response if available
            response = self.direct_responses.get(sequence_tuple)
            if response:
                state_info = f"LLM Bypass - Sequence: {sequence_tuple}"
                logger.info(f"LLM Bypass providing direct response for {sequence_tuple}")
                return state_info, response
            
            # Fallback to tone-based response
            logger.warning(f"No direct response for {sequence_tuple}, using tone fallback")
            tone_category = self._get_tone_category(sequence_tuple)
            fallback_responses = self.tone_fallbacks.get(tone_category, self.tone_fallbacks["default"])
            response = random.choice(fallback_responses)
            state_info = f"LLM Bypass - Sequence: {sequence_tuple}, Tone: {tone_category}"
            return state_info, response
        else:
            logger.debug("LLM Bypass found no emoji sequence")
            return "No sequence detected", None
    
    def _get_tone_category(self, sequence_tuple: Tuple[int, int, int]) -> str:
        """
        Determine tone category for a sequence tuple
        
        Args:
            sequence_tuple: The emoji sequence as integers
            
        Returns:
            Tone category string
        """
        # Simple heuristic based on sequence patterns
        if sequence_tuple == (0, 0, 0):  # All harsh
            return "harsh"
        elif sequence_tuple == (1, 1, 1):  # All calm
            return "calm"
        elif sequence_tuple == (2, 2, 2):  # All oracle
            return "oracle"
        elif sequence_tuple in [(0, 1, 2), (0, 1, 1)]:  # Progressive sequences
            return "wit"
        elif sequence_tuple[0] == 0:  # Starts with harsh
            return "harsh"
        elif sequence_tuple[0] == 1:  # Starts with calm
            return "calm"
        else:
            return "default"
    
    def get_fallback_response(self, author_name: str = "there") -> str:
        """
        Get a generic fallback response when everything else fails
        
        Args:
            author_name: Name of the user to personalize response
            
        Returns:
            Fallback response string
        """
        fallbacks = [
            f"Hey {author_name}! Thanks for the gesture! 👋",
            f"I see you {author_name}, interesting sequence! 🤔",
            f"Noted, {author_name}! That's a meaningful pattern. ✨",
            f"Received your signal, {author_name}! 📡"
        ]
        return random.choice(fallbacks)


def test_llm_bypass_engine():
    """Quick test of the LLM bypass engine"""
    engine = LLMBypassEngine()
    
    test_cases = [
        "✊✊✊",
        "✋✋✋",
        "✊✋🖐️",
        "🖐️🖐️🖐️",
        "✊✋✋",
        "Random message with ✊✊✊ embedded",
        "No emojis here",
        ""
    ]
    
    print("Testing LLM Bypass Engine:")
    for test_input in test_cases:
        state_info, response = engine.process_input(test_input)
        print(f"  '{test_input}' -> State: {state_info}, Response: {response}")
    
    print(f"\nFallback response: {engine.get_fallback_response('TestUser')}")


if __name__ == "__main__":
    test_llm_bypass_engine() 