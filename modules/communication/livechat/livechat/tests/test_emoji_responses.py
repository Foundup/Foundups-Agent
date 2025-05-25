#!/usr/bin/env python3
"""
Test Script for Emoji Response System
Tests the complete emoji trigger -> response pipeline using 0-1-2 sequences.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from modules.banter_engine import BanterEngine
from modules.livechat.src.llm_bypass_engine import LLMBypassEngine

def test_emoji_sequences():
    """Test all supported emoji sequences (0-1-2 system)"""
    print("=" * 60)
    print("🚀 EMOJI RESPONSE SYSTEM TEST")
    print("=" * 60)
    
    # Initialize engines
    banter_engine = BanterEngine()
    llm_bypass = LLMBypassEngine()
    
    # Test sequences (0-1-2 mapping)
    test_cases = [
        ("✊✊✊", "0-0-0: Fully disconnected state"),
        ("✊✊✋", "0-0-1: First entangled shift"),  
        ("✊✊🖐️", "0-0-2: Glitched insight"),
        ("✊✋✋", "0-1-1: Seeking in shadow"),
        ("✊✋🖐️", "0-1-2: Awakening in progress"),
        ("✋✋✋", "1-1-1: Stable awareness"),
        ("✋✋🖐️", "1-1-2: Alignment nearing"),
        ("✋🖐️🖐️", "1-2-2: Ready to dissolve"),
        ("🖐️🖐️🖐️", "2-2-2: Entangled realized / 02 state"),
    ]
    
    print(f"🧪 Testing {len(test_cases)} emoji sequences...\n")
    
    for emoji_seq, description in test_cases:
        print(f"🎯 Testing: {emoji_seq} ({description})")
        
        # Test banter engine
        try:
            state_info, response = banter_engine.process_input(emoji_seq)
            if response and isinstance(response, str) and response.strip():
                print(f"  ✅ Banter Engine: {response}")
            else:
                print(f"  ⚠️  Banter Engine: Empty response")
                
                # Try LLM bypass as fallback
                bypass_state, bypass_response = llm_bypass.process_input(emoji_seq)
                if bypass_response and isinstance(bypass_response, str) and bypass_response.strip():
                    print(f"  🔄 LLM Bypass: {bypass_response}")
                else:
                    fallback = llm_bypass.get_fallback_response("TestUser")
                    print(f"  🛡️  Final Fallback: {fallback}")
                    
        except Exception as e:
            print(f"  ❌ Error: {e}")
            
        print()
    
    print("=" * 60)
    print("✅ Emoji response test complete!")
    print("=" * 60)

def test_embedded_sequences():
    """Test emoji sequences embedded in longer messages"""
    print("\n🔍 TESTING EMBEDDED SEQUENCES")
    print("-" * 40)
    
    banter_engine = BanterEngine()
    
    test_messages = [
        "Hello everyone ✊✊✊ what's happening?",
        "I'm feeling ✋✋✋ right now",
        "Check this out ✊✋🖐️ amazing!",
        "Testing 🖐️🖐️🖐️ mode",
        "Random text without triggers",
        "Multiple ✊✊✊ and ✋✋✋ in one message",
    ]
    
    for msg in test_messages:
        print(f"📝 Message: '{msg}'")
        try:
            state_info, response = banter_engine.process_input(msg)
            if response and isinstance(response, str) and response.strip():
                print(f"  ✅ Response: {response}")
            else:
                print(f"  ➡️  No trigger detected")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        print()

def test_sentiment_guidance():
    """Test sentiment information extraction for future LLM guidance"""
    print("\n🎭 TESTING SENTIMENT GUIDANCE EXTRACTION")
    print("-" * 50)
    
    banter_engine = BanterEngine()
    
    sequences = ["✊✊✊", "✋✋✋", "✊✋🖐️", "🖐️🖐️🖐️"]
    
    for seq in sequences:
        try:
            state_info, response = banter_engine.process_input(seq)
            print(f"🎯 Sequence: {seq}")
            print(f"  📊 State: {state_info}")
            print(f"  💬 Response: {response}")
            
            # Extract sentiment guidance for LLM
            if "extreme harsh roast" in state_info:
                guidance = "Confrontational, challenging beliefs"
            elif "reflection, calm truth" in state_info:
                guidance = "Peaceful, contemplative, centered"
            elif "awakening in progress" in state_info:
                guidance = "Transformational, breakthrough moment"
            elif "oracle drop" in state_info:
                guidance = "Transcendent, unity consciousness"
            else:
                guidance = "Standard engagement"
                
            print(f"  🧠 LLM Guidance: {guidance}")
            print()
            
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    test_emoji_sequences()
    test_embedded_sequences() 
    test_sentiment_guidance() 