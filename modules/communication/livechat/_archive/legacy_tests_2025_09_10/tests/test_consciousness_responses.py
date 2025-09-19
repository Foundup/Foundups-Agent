#!/usr/bin/env python3
"""
Test the enhanced consciousness response system
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.communication.livechat.src.consciousness_handler import ConsciousnessHandler
from modules.communication.livechat.src.agentic_chat_engine import AgenticChatEngine
from modules.ai_intelligence.banter_engine.src.agentic_sentiment_0102 import AgenticSentiment0102

def test_consciousness_responses():
    print("🔬 Testing Enhanced Consciousness Responses\n")
    
    # Initialize components
    sentiment = AgenticSentiment0102()
    consciousness = ConsciousnessHandler(sentiment, None)  # No Grok for testing
    agentic = AgenticChatEngine("memory", consciousness)
    
    # Test cases
    test_messages = [
        ("ModUser1", "✊✋🖐️", "MOD"),
        ("User2", "✊✋🖐️ hello world", "USER"),
        ("ModUser3", "✊✋🖐️ FC @MAGAtroll", "MOD"),
        ("User4", "✊✋🖐️FC @TrumpFan2024", "USER"),
        ("ModUser5", "✊✋🖐️ what do you think about consciousness?", "MOD"),
        ("User6", "hey ✊✋🖐️ this is a test message", "USER"),
        ("ModUser7", "✊✊✊ and then some text", "MOD"),
        ("User8", "🖐️🖐️🖐️ maximum consciousness", "USER"),
    ]
    
    print("=" * 60)
    for username, message, role in test_messages:
        print(f"\n📥 Message from {username} ({role}):")
        print(f"   \"{message}\"")
        
        # Test consciousness detection
        has_consciousness = consciousness.has_consciousness_emojis(message)
        print(f"   Has consciousness emojis: {has_consciousness}")
        
        if has_consciousness:
            # Extract components
            emoji_seq = consciousness.extract_emoji_sequence(message)
            creative_req = consciousness.extract_creative_request(message)
            target = consciousness.extract_target_user(message)
            cmd_type = consciousness.determine_command_type(message)
            
            print(f"   Emoji sequence: {emoji_seq}")
            print(f"   Message after: {creative_req}")
            print(f"   Target user: {target}")
            print(f"   Command type: {cmd_type}")
        
        # Generate response
        response = agentic.generate_agentic_response(username, message, role)
        if response:
            print(f"\n📤 0102 Response:")
            print(f"   {response}")
        else:
            print(f"\n📤 No response generated")
        
        print("-" * 60)
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_consciousness_responses()