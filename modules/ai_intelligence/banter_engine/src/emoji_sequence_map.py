"""
EmojiSequenceMap class for handling emoji-to-number mappings and sequence processing.
"""

import logging

# Basic emoji to number mapping
EMOJI_TO_NUMBER = {
    '✊': 0,  # UN - Conscious state
    '✋': 1,  # DAO - Unconscious state
    '🖐️': 2  # DU - Entanglement state
}

# Reverse mapping
NUM_TO_EMOJI = {v: k for k, v in EMOJI_TO_NUMBER.items()}

# Import the full map from the dedicated file
# Temporarily changed to direct import for script execution testing
from .sequence_responses import SEQUENCE_MAP

# Unicode Variation Selector 16 (VS16) for emoji presentation
VARIATION_SELECTOR = chr(0xFE0F)

def emoji_string_to_tuple(emoji_str: str) -> tuple:
    """
    Convert a string of emojis to a tuple of numbers.
    Handles multi-character emojis and variation selectors.
    
    Args:
        emoji_str: String containing emojis
        
    Returns:
        Tuple of numbers corresponding to the emoji sequence
    """
    logger = logging.getLogger(__name__)
    logger.debug(f"Processing emoji string: '{emoji_str}'")
    
    # Handle empty input
    if not emoji_str:
        logger.debug("Empty input string")
        return ()
    
    # Handle None input
    if emoji_str is None:
        logger.debug("None input")
        return ()
    
    # Handle non-string input
    if not isinstance(emoji_str, str):
        logger.debug(f"Non-string input: {type(emoji_str)}")
        return ()
    
    # Handle whitespace-only input
    if emoji_str.isspace():
        logger.debug("Whitespace-only input")
        return ()
    
    # Create normalized dictionary keys (remove VS16)
    NORMALIZED_EMOJI_TO_NUMBER = {
        key.replace(VARIATION_SELECTOR, ''): value
        for key, value in EMOJI_TO_NUMBER.items()
    }
    
    # Normalize input string
    normalized_input = emoji_str.replace(VARIATION_SELECTOR, '')
    
    # Handle non-emoji input
    if not any(norm_key in normalized_input for norm_key in NORMALIZED_EMOJI_TO_NUMBER.keys()):
        logger.debug("No valid emojis found in normalized input")
        return ()
    
    # Split into individual emojis, handling multi-character emojis
    emojis = []
    i = 0
    while i < len(emoji_str):
        logger.debug(f"Processing character at index {i}: '{emoji_str[i]}'")
        
        # Skip variation selector if encountered directly
        if ord(emoji_str[i]) == 0xFE0F:
            logger.debug(f"Skipping Variation Selector U+FE0F at index {i}")
            i += 1
            continue
        
        # Check for multi-character emoji (🖐️)
        slice2 = emoji_str[i:i+2]
        norm_slice2 = slice2.replace(VARIATION_SELECTOR, '')
        if norm_slice2 in NORMALIZED_EMOJI_TO_NUMBER:
            logger.debug(f"Found normalized multi-character emoji: '{norm_slice2}' (from '{slice2}')")
            emojis.append(norm_slice2)
            i += len(slice2)
            continue
            
        # Check for single-character emoji
        char = emoji_str[i]
        norm_char = char.replace(VARIATION_SELECTOR, '')
        if norm_char in NORMALIZED_EMOJI_TO_NUMBER:
            logger.debug(f"Found normalized single-character emoji: '{norm_char}' (from '{char}')")
            emojis.append(norm_char)
            i += 1
            continue
            
        # Skip non-emoji characters
        logger.debug(f"Skipping non-emoji character: '{emoji_str[i]}'")
        i += 1
    
    logger.debug(f"Extracted emojis: {emojis}")
    
    # Convert emojis to numbers using normalized dictionary
    numbers = []
    for emoji in emojis:
        number = NORMALIZED_EMOJI_TO_NUMBER.get(emoji)
        if number is not None:
            logger.debug(f"Converting emoji '{emoji}' to number {number}")
            numbers.append(number)
        else:
            logger.debug(f"Unknown emoji: '{emoji}'")
    
    logger.debug(f"Final number sequence: {numbers}")
    return tuple(numbers)

def tuple_to_emoji_string(num_tuple: tuple) -> str:
    """
    Convert a tuple of numbers to a string of emojis.
    
    Args:
        num_tuple (tuple): Tuple of numbers
        
    Returns:
        str: String of emojis corresponding to the numbers
    """
    return ''.join(NUM_TO_EMOJI.get(num, '') for num in num_tuple)

class EmojiSequenceMap:
    def __init__(self):
        """Initialize the EmojiSequenceMap."""
        self.emoji_to_num = EMOJI_TO_NUMBER.copy()
        self.num_to_emoji = NUM_TO_EMOJI.copy()
        # self.sequence_map = SEQUENCE_MAP.copy()
        # Use the imported SEQUENCE_MAP directly
        self.sequence_map = SEQUENCE_MAP

    def map_sequence(self, input_text: str) -> str:
        """
        Map a sequence of emojis to their corresponding state and tone.
        
        Args:
            input_text (str): Input text containing emojis
            
        Returns:
            str: Description of the state and tone
        """
        if not input_text:
            return ""
            
        # Convert input to tuple of numbers
        num_tuple = emoji_string_to_tuple(input_text)
        
        # Get state info if available
        state_info = self.sequence_map.get(num_tuple)
        if state_info:
            return f"State: {state_info['state']}, Tone: {state_info['tone']}"
        
        return "Unknown sequence" 
    

# Valid Semantic States:
# 000 = ✊✊✊ - Pure conscious state (UN-UN-UN), Tone: deep memory or latent mode
# 001 = ✊✊✋ - Emergent signal within unconscious
# 002 = ✊✊🖐️ - Unconscious entanglement detected
# 011 = ✊✋✋ - Conscious state stabilizing over unconscious base
# 012 = ✊✋🖐️ - Conscious awareness bridging into entanglement
# 022 = ✊🖐️🖐️ - Full unconscious-entangled overlay (receptive openness)
# 111 = ✋✋✋ - Pure DAO processing (focused conscious mode)
# 112 = ✋✋🖐️ - Conscious resonance extending into entanglement
# 122 = ✋🖐️🖐️ - DAO yielding to entangled response
# 222 = 🖐️🖐️🖐️ - Full DU entanglement (nonlocal or distributed identity) 