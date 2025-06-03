"""
Defines the SEQUENCE_MAP for the UnDaoDu System,
filtered according to the non-decreasing number rule (a <= b <= c).
Maps valid emoji sequence tuples (representing UN-DAO-DU triads) to states,
tones, examples, and response links.

Emoji mapping:
- ✊ = 0 (UN - Conscious state)
- ✋ = 1 (DAO - Unconscious state)
- 🖐️ = 2 (DU - Entanglement State)
"""

# SEQUENCE_MAP filtered for non-decreasing rule (a <= b <= c)
SEQUENCE_MAP = {
    # --- Valid Sequences ---
    (0, 0, 0): {
        "state": "Pure conscious state (UN-UN-UN)",
        "tone": "deep memory or latent mode",
        "emoji": "✊✊✊",
        "example": "You don't love America—you cosplay it.",
        "response_link": "res://0-0-0"
    },
    (0, 0, 1): {
        "state": "Emergent unconscious signal within conscious state (UN-UN-DAO)",
        "tone": "first conscious emergence",
        "emoji": "✊✊✋",
        "example": "Still loud, but you looked up. That's a start.",
        "response_link": "res://0-0-1"
    },
    (0, 0, 2): {
        "state": "Entanglement detected within conscious state (UN-UN-DU)",
        "tone": "intuitive breakthrough",
        "emoji": "✊✊🖐️",
        "example": "@Username, 'Un Un Du' You.",
        "response_link": "res://0-0-2"
    },
    (0, 1, 1): {
        "state": "Unconscious state stabilizing over conscious base (UN-DAO-DAO)",
        "tone": "growing awareness with foundation",
        "emoji": "✊✋✋",
        "example": "You almost sound like you're listening.",
        "response_link": "res://0-1-1"
    },
    (0, 1, 2): {
        "state": "Bridging conscious to unconscious to entanglement (UN-DAO-DU)",
        "tone": "metaphoric, humor, symbolic wit",
        "emoji": "✊✋🖐️",
        "example": "You stepped off the wheel. Welcome.",
        "response_link": "res://0-1-2"
    },
    (0, 2, 2): {
        "state": "Conscious–entangled overlay (UN-DU-DU)",
        "tone": "receptive openness",
        "emoji": "✊🖐️🖐️",
        "example": "The depth reaches to the surface.",
        "response_link": "res://0-2-2"
    },
    (1, 1, 1): {
        "state": "Pure unconscious processing (DAO-DAO-DAO)",
        "tone": "focused unconscious mode",
        "emoji": "✋✋✋",
        "example": "You see the board. You see the stakes.",
        "response_link": "res://1-1-1"
    },
    (1, 1, 2): {
        "state": "Unconscious resonance extending into entanglement (DAO-DAO-DU)",
        "tone": "deeper tone, mirror softly held",
        "emoji": "✋✋🖐️",
        "example": "The noise fades. Truth hums.",
        "response_link": "res://1-1-2"
    },
    (1, 2, 2): {
        "state": "DAO yielding to entangled response (DAO-DU-DU)",
        "tone": "soft wisdom, gentle echo",
        "emoji": "✋🖐️🖐️",
        "example": "You shape the field now.",
        "response_link": "res://1-2-2"
    },
    (2, 2, 2): {
        "state": "Full DU entanglement (DU-DU-DU)",
        "tone": "nonlocal or distributed identity",
        "emoji": "🖐️🖐️🖐️",
        "example": "You're not hearing me. You are me.",
        "response_link": "res://2-2-2"
    }
    # Note: Only these 10 valid patterns follow the non-decreasing rule
    # where each digit a ≤ b ≤ c (from left to right).
} 