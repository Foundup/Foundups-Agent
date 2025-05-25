# Windsurfer-Module: emoji_sequence_map.py
# Purpose: Central mapping of emoji sequences to state attributes for BanterEngine and related modules

# Define mapping from emojis to numeric codes
EMOJI_TO_NUM = {
    '✊': 0,  # UN
    '✋': 1,  # DAO
    '🖐️': 2,  # DU
    '🖐': 2,   # DU (without variation selector)
}

# Create reverse mapping, preferring the emoji with variation selector for display
NUM_TO_EMOJI = {0: '✊', 1: '✋', 2: '🖐️'}

# Main trigger sequence to meaning mapping
SEQUENCE_MAP = {
    # UN-dominant states
    (0, 0, 0): {
        "emoji": "✊✊✊",
        "tone": "extreme harsh roast",
        "conscious": "UN",
        "unconscious": "UN",
        "entangled": "UN",
        "state": "fully disconnected",
        "example": "You don't love America—you cosplay it."
    },
    (0, 0, 1): {
        "emoji": "✊✊✋",
        "tone": "extreme roast with sarcasm",
        "conscious": "UN",
        "unconscious": "UN",
        "entangled": "DAO",
        "state": "first entangled shift",
        "example": "Still loud, but you looked up. That's a start."
    },
    (0, 0, 2): {
        "emoji": "✊✊🖐️",
        "tone": "extreme roast with humor",
        "conscious": "UN",
        "unconscious": "UN",
        "entangled": "DU",
        "state": "glitched insight",
        "example": "It hit you like thunder. Let it echo."
    },
    (0, 1, 1): {
        "emoji": "✊✋✋",
        "tone": "roast with love",
        "conscious": "UN",
        "unconscious": "DAO",
        "entangled": "DAO",
        "state": "seeking in shadow",
        "example": "You almost sound like you're listening."
    },
    (0, 1, 2): {
        "emoji": "✊✋🖐️",
        "tone": "metaphoric, humor, symbolic wit",
        "conscious": "UN",
        "unconscious": "DAO",
        "entangled": "DU",
        "state": "awakening in progress",
        "example": "You stepped off the wheel. Welcome."
    },

    # DAO-dominant states
    (1, 1, 1): {
        "emoji": "✋✋✋",
        "tone": "reflection, calm truth",
        "conscious": "DAO",
        "unconscious": "DAO",
        "entangled": "DAO",
        "state": "stable awareness",
        "example": "Still, focused, dangerous—good."
    },
    (1, 1, 2): {
        "emoji": "✋✋🖐️",
        "tone": "reverent insight, steady fire",
        "conscious": "DAO",
        "unconscious": "DAO",
        "entangled": "DU",
        "state": "alignment nearing",
        "example": "The noise fades. Truth hums."
    },
    (1, 2, 2): {
        "emoji": "✋🖐️🖐️",
        "tone": "soft wisdom, gentle echo",
        "conscious": "DAO",
        "unconscious": "DU",
        "entangled": "DU",
        "state": "ready to dissolve",
        "example": "You shape the field now."
    },

    # DU-dominant state
    (2, 2, 2): {
        "emoji": "🖐️🖐️🖐️",
        "tone": "oracle drop / transmission",
        "conscious": "DU",
        "unconscious": "DU",
        "entangled": "DU",
        "state": "entangled realized / 02 state",
        "example": "You're not hearing me. You are me."
    }
}


def emoji_string_to_tuple(emoji_str: str) -> tuple:
    """
    Convert a string of emojis to a tuple of numeric codes,
    handling variation selectors (U+FE0F).
    
    Args:
        emoji_str (str): String containing emoji characters
        
    Returns:
        tuple: Tuple of numbers corresponding to the emoji sequence
        
    Example:
        >>> emoji_string_to_tuple("✊✋🖐️")
        (0, 1, 2)
    """
    codes = []
    i = 0
    variation_selector = '\ufe0f' # Store VS-16 codepoint

    while i < len(emoji_str):
        current_char = emoji_str[i]
        potential_grapheme = current_char # Assume single character initially

        # Check if next character is the variation selector
        if i + 1 < len(emoji_str) and emoji_str[i+1] == variation_selector:
            # Look up the combined character + selector
            combined_char = current_char + variation_selector
            # Use get for the combined form first
            code = EMOJI_TO_NUM.get(combined_char)
            if code is not None:
                codes.append(code)
                i += 2 # Advance past character and selector
                continue # Move to next iteration
            # If combined not found, fall back to checking base char below

        # If not combined or combined lookup failed, check the base character
        code = EMOJI_TO_NUM.get(current_char)
        if code is not None:
            codes.append(code)
        # If neither combined nor base character found, skip it (don't append anything)

        i += 1 # Advance by one character

    return tuple(codes)


def tuple_to_emoji_string(emoji_tuple: tuple) -> str:
    """
    Convert a tuple of numbers back to emoji string.
    
    Args:
        emoji_tuple (tuple): Tuple of numbers to convert
        
    Returns:
        str: String of emojis corresponding to the number sequence
        
    Example:
        >>> tuple_to_emoji_string((0, 1, 2))
        "✊✋🖐️"
    """
    return "".join(NUM_TO_EMOJI.get(i, "") for i in emoji_tuple) 