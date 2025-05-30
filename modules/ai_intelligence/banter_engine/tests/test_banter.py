import logging

# Configure logging (optional, but helpful for seeing engine logs)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Updated import path for the new location
from ..src.banter_engine import BanterEngine

if __name__ == "__main__":
    # Test the BanterEngine
    print("🧪 Testing BanterEngine from root script...")

    # Create a test instance
    engine_default = BanterEngine()

    # Test getting random banter
    print("\n🧪 Testing random banter generation:")
    for _ in range(3):
        line = engine_default.get_random_banter(theme="greeting")
        print(f"Generated: {line}")

    # Test emoji sequence processing
    print("\n🧪 Testing emoji sequence processing:")
    test_messages = [
        "Hey everyone ✊",
        "Sequence ✊✋🖐️ here",
        "Mixed text ✋✋✋ and emojis",
        "Invalid sequence ✊✊✊✊", # Should map to 1,1,1 -> example
        "What up ✋",
        "Stream is live 🖐",
        "Fully disconnected example: ✊✊✊",
        "Awakening example: ✊✋🖐️",
        "Stable example: ✋✋✋",
        "Entangled example: 🖐️🖐️🖐️",
        "Missing definition ✊🖐️✊", # Test a placeholder
        "No emojis here"
    ]

    for msg in test_messages:
        print(f"\nInput: {msg}")
        # engine_default._log_individual_emojis(msg) # Optionally log individual emojis too
        result, response = engine_default.process_input(msg)
        print(f"Result: {result}")
        if response:
            print(f"Response: {response}") # Changed label from Placeholder 