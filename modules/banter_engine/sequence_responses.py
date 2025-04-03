"""
Defines the SEQUENCE_MAP for the Emoji Sentiment Mapper (ESM),
filtered according to the non-decreasing number rule (c <= u <= e).
Maps valid emoji sequence tuples (representing UN-DAO-DU triads) to states,
tones, examples, and response links.
"""

# SEQUENCE_MAP filtered for non-decreasing rule (c <= u <= e)
SEQUENCE_MAP = {
    # --- Valid Sequences ---
    (1, 1, 1): {
        "state": "fully disconnected",
        "tone": "extreme harsh roast",
        "emoji": "✊✊✊",
        "example": "You don't love America—you cosplay it.",
        "response_link": "res://1-1-1"
    },
    (1, 1, 2): {
        "state": "first entangled shift",
        "tone": "extreme roast with sarcasm",
        "emoji": "✊✊✋",
        "example": "Still loud, but you looked up. That's a start.",
        "response_link": "res://1-1-2"
    },
    (1, 1, 3): {
        "state": "glitched insight",
        "tone": "extreme roast with humor",
        "emoji": "✊✊🖐️",
        "example": "It hit you like thunder. Let it echo.",
        "response_link": "res://1-1-3"
    },
    (1, 2, 2): {
        "state": "seeking in shadow",
        "tone": "roast with love",
        "emoji": "✊✋✋",
        "example": "You almost sound like you're listening.",
        "response_link": "res://1-2-2"
    },
    (1, 2, 3): {
        "state": "awakening in progress",
        "tone": "metaphoric, humor, symbolic wit",
        "emoji": "✊✋🖐️",
        "example": "You stepped off the wheel. Welcome.",
        "response_link": "res://1-2-3"
    },
    (1, 3, 3): {
        "state": "defined state for 133",
        "tone": "defined tone for 133",
        "emoji": "✊🖐️🖐️",
        "example": "defined example for 133",
        "response_link": "res://1-3-3"
    },
    (2, 2, 2): {
        "state": "stable awareness",
        "tone": "reflection, calm truth",
        "emoji": "✋✋✋",
        "example": "You see the board. You see the stakes.",
        "response_link": "res://2-2-2"
    },
    (2, 2, 3): {
        "state": "alignment nearing",
        "tone": "deeper tone, mirror softly held",
        "emoji": "✋✋🖐️",
        "example": "The noise fades. Truth hums.",
        "response_link": "res://2-2-3"
    },
    (2, 3, 3): {
        "state": "ready to dissolve",
        "tone": "soft wisdom, gentle echo",
        "emoji": "✋🖐️🖐️",
        "example": "You shape the field now.",
        "response_link": "res://2-3-3"
    },
    (3, 3, 3): {
        "state": "entangled realized / 02 state",
        "tone": "oracle drop / transmission",
        "emoji": "🖐️🖐️🖐️",
        "example": "You're not hearing me. You are me.",
        "response_link": "res://3-3-3"
    }
    # Note: 17 other combinations like (1,2,1), (2,1,1), (3,2,1) etc. are excluded
    # based on the non-decreasing number rule.
} 