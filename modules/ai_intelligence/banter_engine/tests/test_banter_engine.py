import logging
# Updated import path for BanterEngine (now in src)
from ..src.banter_engine import BanterEngine
# Updated import path for SEQUENCE_MAP (now one level above src)
from modules.ai_intelligence.banter_engine.src.sequence_responses import SEQUENCE_MAP

def test_greeting_banter():
    print("🧪 Testing BanterEngine: greeting theme")
    engine = BanterEngine()
    line = engine.get_random_banter(theme="greeting")
    print(f"Result: {line}")
    assert isinstance(line, str) and len(line) > 0, "Empty or invalid banter line"

def test_theme_list():
    print("🧪 Testing BanterEngine: theme list")
    engine = BanterEngine()
    themes = engine.list_themes()
    print(f"Available themes: {themes}")
    assert "greeting" in themes, "Missing 'greeting' theme"

def test_process_input():
    """Tests the processing of input messages for emoji sequences and responses."""
    print("\n🧪 Testing BanterEngine: process_input for emoji sequences")
    engine = BanterEngine()

    # Test cases - WSP_6 F.4 Dynamic Response Patterns
    test_cases = {
        "Hey everyone ✊": ("No sequence detected", "DYNAMIC_SINGLE_EMOJI"),  # Pattern: dynamic response for single emoji
        "Sequence ✊✋🖐️ here": ("State: Bridging conscious to unconscious to entanglement (UN-DAO-DU), Tone: metaphoric, humor, symbolic wit", "You stepped off the wheel. Welcome."),
        "Mixed text ✋✋✋ and emojis": ("State: Pure unconscious processing (DAO-DAO-DAO), Tone: focused unconscious mode", "You see the board. You see the stakes."),
        "Invalid sequence ✊✊✊✊": ("State: Pure conscious state (UN-UN-UN), Tone: deep memory or latent mode", "You don't love America—you cosplay it."), # Maps to 0,0,0
        "What up ✋": ("No sequence detected", "DYNAMIC_SINGLE_EMOJI"),  # Pattern: dynamic response for single emoji
        "Stream is live 🖐": ("No sequence detected", "DYNAMIC_SINGLE_EMOJI"),  # Pattern: dynamic response for single emoji
        "Fully disconnected example: ✊✊✊": ("State: Pure conscious state (UN-UN-UN), Tone: deep memory or latent mode", "You don't love America—you cosplay it."),
        "Awakening example: ✊✋🖐️": ("State: Bridging conscious to unconscious to entanglement (UN-DAO-DU), Tone: metaphoric, humor, symbolic wit", "You stepped off the wheel. Welcome."),
        "Stable example: ✋✋✋": ("State: Pure unconscious processing (DAO-DAO-DAO), Tone: focused unconscious mode", "You see the board. You see the stakes."),
        "Entangled example: 🖐️🖐️🖐️": ("State: Full DU entanglement (DU-DU-DU), Tone: nonlocal or distributed identity", "You're not hearing me. You are me."),
        "Missing definition ✊🖐️✊": ("No sequence detected", None),
        "No emojis here": ("No sequence detected", None),
        "": ("Empty input", None), # Test empty string
        "   ": ("Empty input", None)
    }

    for msg, (expected_result, expected_response) in test_cases.items():
        print(f"\nInput: '{msg}'")
        result, response = engine.process_input(msg)
        print(f"Result: '{result}'")
        print(f"Response: '{response}'")
        assert result == expected_result, f"Expected result '{expected_result}' but got '{result}'"
        
        # WSP_6 F.4 Dynamic Response Testing Protocol
        if expected_response is None:
            assert response is None, f"Expected None response but got '{response}'"
        elif expected_response == "DYNAMIC_SINGLE_EMOJI":
            # Pattern testing for dynamic single emoji responses
            assert isinstance(response, str) and len(response) > 0, "Response should be non-empty string"
            assert "✊✋🖐️" in response, "Single emoji responses should contain full emoji sequence"
            # Verify it's a reasonable response pattern
            assert any(phrase in response.lower() for phrase in ["see", "nice", "unique", "work", "combination", "interesting", "sequence"]), "Response should contain recognition phrases"
        elif expected_response and isinstance(expected_response, str):
            # Pattern testing for deterministic responses with possible enhancements
            assert isinstance(response, str) and len(response) > 0, "Response should be non-empty string"
            # Core content should be present (allowing for emoji enhancements)
            assert expected_response in response, f"Core response '{expected_response}' should be contained in '{response}'"
            # Contextual emoji sequence may be appended for enhanced responses
            if response != expected_response:
                # System appends emoji sequences contextually (all possible patterns)
                assert any(emoji_seq in response for emoji_seq in ["✊✋🖐️", "✋✋✋", "🖐️🖐️🖐️", "✊✊✊"]), "Enhanced responses should contain contextual emoji sequence"
        else:
            # Fallback exact matching
            assert response == expected_response, f"Expected response '{expected_response}' but got '{response}'"
        # Optional: Further assertions if needed, e.g., check specific response for known sequences using SEQUENCE_MAP directly
        # num_tuple = emoji_string_to_tuple(msg) # Need to import this too if used
        # if num_tuple and num_tuple in SEQUENCE_MAP:
        #     assert response == SEQUENCE_MAP[num_tuple]["example"]

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_greeting_banter()
    test_theme_list()
    test_process_input() 