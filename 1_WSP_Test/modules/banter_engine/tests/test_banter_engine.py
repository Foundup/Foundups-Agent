import logging
# Updated import path for BanterEngine (now in src)
from ..src.banter_engine import BanterEngine
# Updated import path for SEQUENCE_MAP (now one level above src)
from ..sequence_responses import SEQUENCE_MAP

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

    # Test cases
    test_cases = {
        "Hey everyone ✊": ("No sequence detected", None),
        "Sequence ✊✋🖐️ here": ("State: awakening in progress, Tone: metaphoric, humor, symbolic wit", "You stepped off the wheel. Welcome."),
        "Mixed text ✋✋✋ and emojis": ("State: stable awareness, Tone: reflection, calm truth", "You see the board. You see the stakes."),
        "Invalid sequence ✊✊✊✊": ("State: fully disconnected, Tone: extreme harsh roast", "You don't love America—you cosplay it."), # Maps to 1,1,1
        "What up ✋": ("No sequence detected", None),
        "Stream is live 🖐": ("No sequence detected", None),
        "Fully disconnected example: ✊✊✊": ("State: fully disconnected, Tone: extreme harsh roast", "You don't love America—you cosplay it."),
        "Awakening example: ✊✋🖐️": ("State: awakening in progress, Tone: metaphoric, humor, symbolic wit", "You stepped off the wheel. Welcome."),
        "Stable example: ✋✋✋": ("State: stable awareness, Tone: reflection, calm truth", "You see the board. You see the stakes."),
        "Entangled example: 🖐️🖐️🖐️": ("State: entangled realized / 02 state, Tone: oracle drop / transmission", "You're not hearing me. You are me."),
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