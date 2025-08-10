#!/usr/bin/env python3
"""
Direct test of emoji sequence processing
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from modules.ai_intelligence.banter_engine.src.banter_engine import BanterEngine

def test_emoji_sequence():
    """Test that ✊✋🖐️ triggers the correct response"""
    
    print("[INFO] Initializing BanterEngine...")
    engine = BanterEngine()
    
    # Test sequences
    test_inputs = [
        "✊✋🖐️",  # Should trigger (0,1,2) response
        "Hello ✊✋🖐️ there",  # With text
        "✊✊✊",  # Should trigger (0,0,0) response
        "Test message with no emojis"
    ]
    
    for input_text in test_inputs:
        print(f"\n[TEST] Input: '{input_text}'")
        
        # Process input
        state, response = engine.process_input(input_text)
        
        print(f"[RESULT] State: {state}")
        print(f"[RESULT] Response: {response}")
        
        # Check if the expected response for ✊✋🖐️ is triggered
        if "✊✋🖐️" in input_text:
            expected = "You stepped off the wheel. Welcome."
            if expected in str(response):
                print(f"[OK] Correct response for ✊✋🖐️ sequence!")
            else:
                print(f"[WARN] Expected '{expected}' in response")

if __name__ == "__main__":
    test_emoji_sequence()