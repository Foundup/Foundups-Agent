#!/usr/bin/env python3
"""
Test Script for Emoji Response System
Tests the complete emoji trigger -> response pipeline using 0-1-2 sequences.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from unittest.mock import AsyncMock, MagicMock, patch

from modules.ai_intelligence.banter_engine import BanterEngine
from modules.communication.livechat.src.llm_bypass_engine import LLMBypassEngine
from modules.communication.livechat.src.livechat_core import LiveChatCore as LiveChatListener

def test_emoji_sequences():
    """Test all supported emoji sequences (0-1-2 system)"""
    print("=" * 60)
    print("[ROCKET] EMOJI RESPONSE SYSTEM TEST")
    print("=" * 60)
    
    # Initialize engines
    banter_engine = BanterEngine()
    llm_bypass = LLMBypassEngine()
    
    # Test sequences (0-1-2 mapping)
    test_cases = [
        ("[U+270A][U+270A][U+270A]", "0-0-0: Fully disconnected state"),
        ("[U+270A][U+270A][U+270B]", "0-0-1: First entangled shift"),  
        ("[U+270A][U+270A][U+1F590]️", "0-0-2: Glitched insight"),
        ("[U+270A][U+270B][U+270B]", "0-1-1: Seeking in shadow"),
        ("[U+270A][U+270B][U+1F590]️", "0-1-2: Awakening in progress"),
        ("[U+270B][U+270B][U+270B]", "1-1-1: Stable awareness"),
        ("[U+270B][U+270B][U+1F590]️", "1-1-2: Alignment nearing"),
        ("[U+270B][U+1F590]️[U+1F590]️", "1-2-2: Ready to dissolve"),
        ("[U+1F590]️[U+1F590]️[U+1F590]️", "2-2-2: Entangled realized / 02 state"),
    ]
    
    print(f"[U+1F9EA] Testing {len(test_cases)} emoji sequences...\n")
    
    for emoji_seq, description in test_cases:
        print(f"[TARGET] Testing: {emoji_seq} ({description})")
        
        # Test banter engine
        try:
            state_info, response = banter_engine.process_input(emoji_seq)
            if response and isinstance(response, str) and response.strip():
                print(f"  [OK] Banter Engine: {response}")
            else:
                print(f"  [U+26A0]️  Banter Engine: Empty response")
                
                # Try LLM bypass as fallback
                bypass_state, bypass_response = llm_bypass.process_input(emoji_seq)
                if bypass_response and isinstance(bypass_response, str) and bypass_response.strip():
                    print(f"  [REFRESH] LLM Bypass: {bypass_response}")
                else:
                    fallback = llm_bypass.get_fallback_response("TestUser")
                    print(f"  [U+1F6E1]️  Final Fallback: {fallback}")
                    
        except Exception as e:
            print(f"  [FAIL] Error: {e}")
            
        print()
    
    print("=" * 60)
    print("[OK] Emoji response test complete!")
    print("=" * 60)

def test_embedded_sequences():
    """Test emoji sequences embedded in longer messages"""
    print("\n[SEARCH] TESTING EMBEDDED SEQUENCES")
    print("-" * 40)
    
    banter_engine = BanterEngine()
    
    test_messages = [
        "Hello everyone [U+270A][U+270A][U+270A] what's happening?",
        "I'm feeling [U+270B][U+270B][U+270B] right now",
        "Check this out [U+270A][U+270B][U+1F590]️ amazing!",
        "Testing [U+1F590]️[U+1F590]️[U+1F590]️ mode",
        "Random text without triggers",
        "Multiple [U+270A][U+270A][U+270A] and [U+270B][U+270B][U+270B] in one message",
    ]
    
    for msg in test_messages:
        print(f"[NOTE] Message: '{msg}'")
        try:
            state_info, response = banter_engine.process_input(msg)
            if response and isinstance(response, str) and response.strip():
                print(f"  [OK] Response: {response}")
            else:
                print(f"  [U+27A1]️  No trigger detected")
        except Exception as e:
            print(f"  [FAIL] Error: {e}")
        print()

def test_sentiment_guidance():
    """Test sentiment information extraction for future LLM guidance"""
    print("\n[U+1F3AD] TESTING SENTIMENT GUIDANCE EXTRACTION")
    print("-" * 50)
    
    banter_engine = BanterEngine()
    
    sequences = ["[U+270A][U+270A][U+270A]", "[U+270B][U+270B][U+270B]", "[U+270A][U+270B][U+1F590]️", "[U+1F590]️[U+1F590]️[U+1F590]️"]
    
    for seq in sequences:
        try:
            state_info, response = banter_engine.process_input(seq)
            print(f"[TARGET] Sequence: {seq}")
            print(f"  [DATA] State: {state_info}")
            print(f"  [U+1F4AC] Response: {response}")
            
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
                
            print(f"  [AI] LLM Guidance: {guidance}")
            print()
            
        except Exception as e:
            print(f"  [FAIL] Error: {e}")

if __name__ == "__main__":
    test_emoji_sequences()
    test_embedded_sequences() 
    test_sentiment_guidance() 