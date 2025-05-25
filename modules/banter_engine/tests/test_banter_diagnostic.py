#!/usr/bin/env python3

"""
WSP-Compliant Diagnostic Script for Banter Engine
Tests emoji sequence detection and response generation in isolation
"""

import sys
import os

# Add project root to sys.path for module imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

# Import the banter engine and supporting modules
from modules.banter_engine.src.banter_engine import BanterEngine
from modules.banter_engine.src.emoji_sequence_map import SEQUENCE_MAP, emoji_string_to_tuple

def test_sequence_map_integrity():
    """Test that the SEQUENCE_MAP is properly loaded and accessible"""
    print("🔍 Testing SEQUENCE_MAP integrity...")
    
    print(f"  📊 Total sequences in map: {len(SEQUENCE_MAP)}")
    
    for seq_tuple, info in SEQUENCE_MAP.items():
        print(f"  🎯 {seq_tuple} -> {info.get('emoji', 'N/A')}")
        print(f"      State: {info.get('state', 'N/A')}")
        print(f"      Tone: {info.get('tone', 'N/A')}")
        print(f"      Example: {info.get('example', 'N/A')}")
        print()

def test_emoji_string_conversion():
    """Test emoji string to tuple conversion"""
    print("🔄 Testing emoji string conversion...")
    
    test_cases = [
        "✊✊✊",
        "✋✋✋", 
        "✊✋🖐️",
        "🖐️🖐️🖐️",
        "✊✋✋",
        "✋🖐️🖐️"
    ]
    
    for emoji_str in test_cases:
        tuple_result = emoji_string_to_tuple(emoji_str)
        print(f"  '{emoji_str}' -> {tuple_result}")
        
        if tuple_result in SEQUENCE_MAP:
            info = SEQUENCE_MAP[tuple_result]
            print(f"      ✅ Found in map: {info.get('example', 'No example')}")
        else:
            print(f"      ❌ Not found in map")
        print()

def test_banter_engine_initialization():
    """Test banter engine initialization and internal state"""
    print("🚀 Testing BanterEngine initialization...")
    
    try:
        engine = BanterEngine()
        print("  ✅ BanterEngine initialized successfully")
        
        print(f"  📊 sequence_map_data loaded: {len(engine.sequence_map_data)} entries")
        print(f"  🎨 Available themes: {list(engine._themes.keys())}")
        
        # Test a few themes
        for theme in ["extreme harsh roast", "reflection, calm truth", "default"]:
            if theme in engine._themes:
                responses = engine._themes[theme]
                print(f"  🎯 Theme '{theme}': {len(responses)} responses")
                if responses:
                    print(f"      Example: {responses[0]}")
            else:
                print(f"  ❌ Theme '{theme}' not found")
        
        return engine
        
    except Exception as e:
        print(f"  ❌ Failed to initialize BanterEngine: {e}")
        return None

def test_banter_engine_processing():
    """Test banter engine input processing with known sequences"""
    print("🧪 Testing BanterEngine processing...")
    
    engine = BanterEngine()
    
    test_messages = [
        "✊✊✊",  # Should return: "You don't love America—you cosplay it."
        "✋✋✋",  # Should return: "Still, focused, dangerous—good."
        "✊✋🖐️", # Should return: "You stepped off the wheel. Welcome."
        "🖐️🖐️🖐️", # Should return: "You're not hearing me. You are me."
        "✊✋✋",  # Should return: "You almost sound like you're listening."
        "Random message with ✊✊✊ embedded",
        "No emojis here",
        "",
        "   "
    ]
    
    for message in test_messages:
        print(f"\n  📝 Input: '{message}'")
        try:
            result = engine.process_input(message)
            print(f"  📤 Output type: {type(result)}")
            print(f"  📤 Output: {result}")
            
            if isinstance(result, tuple) and len(result) == 2:
                state_info, response = result
                print(f"      📊 State Info: {state_info}")
                print(f"      💬 Response: {response}")
                
                if response is None or response == "":
                    print("      ⚠️  WARNING: Empty response!")
                elif not isinstance(response, str):
                    print(f"      ⚠️  WARNING: Non-string response: {type(response)}")
                else:
                    print("      ✅ Valid response")
            else:
                print(f"      ❌ Unexpected format: {result}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
            import traceback
            traceback.print_exc()

def test_sequence_extraction():
    """Test the internal _extract_emoji_sequence method"""
    print("🔍 Testing emoji sequence extraction...")
    
    engine = BanterEngine()
    
    test_cases = [
        "✊✊✊",
        "Hello ✊✊✊ world", 
        "✋✋✋",
        "Mixed ✊✋🖐️ sequence",
        "Only two ✊✋",
        "Four emojis ✊✊✊✊",
        "Different order ✋✊🖐️✊",
        "No emojis",
        ""
    ]
    
    for test_input in test_cases:
        extracted = engine._extract_emoji_sequence(test_input)
        print(f"  '{test_input}' -> {extracted}")

def main():
    """Main diagnostic function"""
    print("=" * 60)
    print("🔧 BANTER ENGINE DIAGNOSTIC SCRIPT")
    print("=" * 60)
    
    test_sequence_map_integrity()
    print("\n" + "=" * 60)
    
    test_emoji_string_conversion()
    print("\n" + "=" * 60)
    
    engine = test_banter_engine_initialization()
    if not engine:
        print("❌ Cannot continue - BanterEngine failed to initialize")
        return
    
    print("\n" + "=" * 60)
    
    test_sequence_extraction()
    print("\n" + "=" * 60)
    
    test_banter_engine_processing()
    print("\n" + "=" * 60)
    print("🏁 Diagnostic complete!")

if __name__ == "__main__":
    main() 