#!/usr/bin/env python3

"""
Quick test script to verify banter engine integration with livechat module
"""

import sys
import os

import sys
from modules.banter_engine import BanterEngine

def test_banter_response_format():
    """Test that banter engine returns the expected tuple format"""
    print("🧪 Testing banter engine response format...")
    
    engine = BanterEngine()
    
    # Test various emoji sequences
    test_sequences = ["✊✊✊", "✋✋✋", "✊✋🖐️", "🖐️🖐️🖐️", "✋✊✊"]
    
    for sequence in test_sequences:
        print(f"\n🔍 Testing sequence: {sequence}")
        try:
            result = engine.process_input(sequence)
            print(f"  Result type: {type(result)}")
            print(f"  Result: {result}")
            
            if isinstance(result, tuple) and len(result) == 2:
                state_info, response = result
                print(f"  ✅ Correct tuple format!")
                print(f"  📊 State: {state_info}")
                print(f"  💬 Response: {response}")
            else:
                print(f"  ❌ Unexpected format: {result}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")

def test_livechat_fix():
    """Test the fix for livechat banter integration"""
    print("\n🔧 Testing livechat fix simulation...")
    
    engine = BanterEngine()
    
    # Simulate the fixed livechat handling
    emoji_sequence = "✊✊✊"
    print(f"Processing emoji sequence: {emoji_sequence}")
    
    try:
        # This is how it should work in the fixed livechat
        state_info, response = engine.process_input(emoji_sequence)
        print(f"✅ Fixed format - State: {state_info}, Response: {response}")
        
        # Check if response is valid
        if response and isinstance(response, str) and response.strip():
            print(f"✅ Valid response: '{response}'")
        else:
            print(f"⚠️  Response needs fallback: {response}")
            fallback_response = "Hey there! Thanks for the gesture! 窓"
            print(f"   Using fallback: '{fallback_response}'")
            
    except Exception as e:
        print(f"❌ Error in processing: {e}")

if __name__ == "__main__":
    print("🚀 Banter Engine Live Test")
    print("=" * 50)
    
    test_banter_response_format()
    test_livechat_fix()
    
    print("\n✨ Test complete!") 