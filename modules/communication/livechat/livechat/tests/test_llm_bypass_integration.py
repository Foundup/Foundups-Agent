#!/usr/bin/env python3

"""
WSP-Compliant LLM Bypass Integration Test
Tests direct LLM integration for emoji sequence responses
"""

import sys
import os
import logging

# Add project root to sys.path for module imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

# Import required modules
from modules.ai_intelligence.banter_engine.banter_engine.emoji_sequence_map import SEQUENCE_MAP, emoji_string_to_tuple

logger = logging.getLogger(__name__)

class LLMBypassEngine:
    """
    Simple LLM bypass engine that provides direct responses for emoji sequences
    This can be used as a fallback when the banter engine fails
    """
    
    def __init__(self):
        """Initialize the LLM bypass engine"""
        self.sequence_map = SEQUENCE_MAP
        self.fallback_responses = {
            "extreme harsh roast": [
                "You're operating on borrowed confidence.",
                "That's a fascinating way to be wrong.",
                "You're not even wrong—you're just confused."
            ],
            "reflection, calm truth": [
                "Consider the deeper pattern here.",
                "You're beginning to see it.",
                "The noise fades when you stop feeding it."
            ],
            "metaphoric, humor, symbolic wit": [
                "You're stepping off the carousel.",
                "The game changed. You noticed.",
                "Welcome to the other side of the mirror."
            ],
            "oracle drop / transmission": [
                "You're not separate from this.",
                "The observer and observed collapse.",
                "There is no 'you' hearing this."
            ],
            "default": [
                "Interesting sequence detected! 🤔",
                "That's a meaningful gesture! ✨",
                "I see what you did there! 👀"
            ]
        }
        
    def _extract_emoji_sequence(self, input_text: str) -> tuple:
        """Extract emoji sequence from text (same logic as banter engine)"""
        emoji_map = {'✊': 0, '✋': 1, '🖐️': 2}
        sequence = []
        for char in input_text:
            if char in emoji_map:
                sequence.append(emoji_map[char])
                if len(sequence) == 3:
                    return tuple(sequence)
        return None
        
    def process_input(self, input_text: str) -> tuple:
        """
        Process input and return response using direct mapping or LLM-style fallback
        
        Args:
            input_text: The message to process
            
        Returns:
            Tuple of (state_info, response)
        """
        if not input_text or input_text.isspace():
            return "Empty input", None
            
        # Extract sequence
        sequence_tuple = self._extract_emoji_sequence(input_text)
        
        # Try simple pattern matching as fallback
        if not sequence_tuple:
            if "✊✊✊" in input_text:
                sequence_tuple = (0, 0, 0)
            elif "✋✋✋" in input_text:
                sequence_tuple = (1, 1, 1)
            elif "🖐️🖐️🖐️" in input_text:
                sequence_tuple = (2, 2, 2)
            elif "✊✋🖐️" in input_text:
                sequence_tuple = (0, 1, 2)
            elif "✊✋✋" in input_text:
                sequence_tuple = (0, 1, 1)
                
        if sequence_tuple and sequence_tuple in self.sequence_map:
            # Direct mapping approach
            sequence_info = self.sequence_map[sequence_tuple]
            state = sequence_info.get("state", "Unknown State")
            tone = sequence_info.get("tone", "default")
            state_info = f"State: {state}, Tone: {tone}"
            
            # Get direct example first
            response = sequence_info.get("example")
            if response:
                return state_info, response
                
            # Fallback to tone-based response
            import random
            tone_responses = self.fallback_responses.get(tone, self.fallback_responses["default"])
            response = random.choice(tone_responses)
            return state_info, response
        else:
            return "No sequence detected", None
            
    def generate_llm_style_response(self, sequence_tuple: tuple, context: str = "") -> str:
        """
        Generate an LLM-style contextual response for a given sequence
        This simulates what an LLM might generate based on the sequence meaning
        """
        if sequence_tuple not in self.sequence_map:
            return "I notice your gesture, but I'm not sure how to respond to that pattern."
            
        sequence_info = self.sequence_map[sequence_tuple]
        state = sequence_info.get("state", "")
        tone = sequence_info.get("tone", "")
        
        # LLM-style contextual responses based on state and tone
        llm_responses = {
            (0, 0, 0): [  # fully disconnected
                f"I see you're expressing something intense. The pattern suggests you might be feeling disconnected or frustrated. {context}",
                f"That gesture carries weight. Sometimes when we're fully engaged in one mode, we miss other perspectives. {context}",
                f"Strong signal received. That energy suggests you're locked into a particular way of seeing things. {context}"
            ],
            (1, 1, 1): [  # stable awareness  
                f"I sense a calm, focused energy in that sequence. You seem present and aware. {context}",
                f"That's a centered gesture. There's something grounded about that pattern. {context}",
                f"Interesting - that sequence suggests stability and clear perception. {context}"
            ],
            (0, 1, 2): [  # awakening in progress
                f"That's a dynamic sequence - it suggests movement, transition, maybe awakening to something new. {context}",
                f"I see progression in that pattern. Like you're moving through different states of understanding. {context}",
                f"Fascinating gesture - it carries a sense of evolution, of stepping into something different. {context}"
            ]
        }
        
        import random
        responses = llm_responses.get(sequence_tuple, [
            f"I notice that sequence represents '{state}' with a '{tone}' quality. {context}",
            f"That pattern suggests you're in a '{state}' mode. {context}"
        ])
        
        return random.choice(responses)

def test_llm_bypass_basic():
    """Test basic LLM bypass functionality"""
    print("🧪 Testing LLM Bypass Engine - Basic Functionality")
    
    engine = LLMBypassEngine()
    
    test_cases = [
        "✊✊✊",
        "✋✋✋", 
        "✊✋🖐️",
        "🖐️🖐️🖐️",
        "✊✋✋",
        "Random message with ✊✊✊ embedded",
        "No emojis here",
        ""
    ]
    
    for test_input in test_cases:
        print(f"\n  📝 Input: '{test_input}'")
        state_info, response = engine.process_input(test_input)
        print(f"  📊 State: {state_info}")
        print(f"  💬 Response: {response}")
        
        if response:
            print("  ✅ Valid response generated")
        else:
            print("  ⚠️  No response (expected for some cases)")

def test_llm_bypass_contextual():
    """Test LLM-style contextual responses"""
    print("\n🤖 Testing LLM Bypass Engine - Contextual Responses")
    
    engine = LLMBypassEngine()
    
    test_sequences = [
        ((0, 0, 0), "The user seems frustrated about politics"),
        ((1, 1, 1), "The user is asking about meditation"),  
        ((0, 1, 2), "The user is questioning their beliefs"),
        ((2, 2, 2), "The user is having a spiritual experience")
    ]
    
    for sequence_tuple, context in test_sequences:
        print(f"\n  🎯 Sequence: {sequence_tuple}")
        print(f"  📝 Context: {context}")
        response = engine.generate_llm_style_response(sequence_tuple, context)
        print(f"  🤖 LLM Response: {response}")

def test_integration_with_livechat():
    """Test how this could integrate with the livechat module"""
    print("\n🔗 Testing Integration with LiveChat Module")
    
    engine = LLMBypassEngine()
    
    # Simulate the livechat flow
    def simulate_emoji_trigger_with_bypass(message_text: str, author_name: str) -> str:
        """Simulate the _handle_emoji_trigger method using LLM bypass"""
        print(f"  📨 Processing message from {author_name}: {message_text}")
        
        # Check if it contains our trigger emojis (simplified check)
        trigger_emojis = ['✊', '✋', '🖐️']
        emoji_count = sum(1 for char in message_text if char in trigger_emojis)
        
        if emoji_count >= 3:
            print(f"  🎯 Emoji trigger detected ({emoji_count} emojis)")
            
            # Try banter engine first (simulate failure)
            print("  ⚠️  Banter engine returned empty response, using LLM bypass...")
            
            # Use LLM bypass
            state_info, response = engine.process_input(message_text)
            
            if response:
                print(f"  ✅ LLM Bypass generated response: {response}")
                return response
            else:
                # Final fallback
                fallback = f"Hey {author_name}! Thanks for the gesture! 👋"
                print(f"  🛡️  Using final fallback: {fallback}")
                return fallback
        else:
            print("  ➡️  No emoji trigger detected")
            return None
    
    # Test cases simulating real livechat messages
    test_messages = [
        ("✊✊✊", "Move2Japan"),
        ("Hello ✋✋✋ everyone", "UnDaoDu"),
        ("✊✋🖐️ what's happening", "Antony Hurst"),
        ("Just a normal message", "TestUser"),
        ("🖐️🖐️🖐️", "SpiritualSeeker")
    ]
    
    for message, author in test_messages:
        print(f"\n  " + "="*50)
        response = simulate_emoji_trigger_with_bypass(message, author)
        if response:
            print(f"  📤 Would send to chat: {response}")

def main():
    """Main test function"""
    print("=" * 60)
    print("🚀 LLM BYPASS INTEGRATION TEST")
    print("=" * 60)
    
    test_llm_bypass_basic()
    test_llm_bypass_contextual()
    test_integration_with_livechat()
    
    print("\n" + "=" * 60)
    print("🏁 LLM Bypass test complete!")
    print("💡 This engine can be integrated as a fallback when banter engine fails")

if __name__ == "__main__":
    main() 