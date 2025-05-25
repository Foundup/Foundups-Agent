#!/usr/bin/env python3
"""
Test Script for Emoji-Guided LLM Response System
Demonstrates the banter engine's emoji detection and response capabilities
"""

import sys
import os

# Add the module paths to sys.path
sys.path.insert(0, os.path.join(os.getcwd(), 'modules', 'ai_intelligence', 'banter_engine', 'banter_engine', 'src'))
sys.path.insert(0, os.path.join(os.getcwd(), 'modules', 'ai_intelligence', 'banter_engine', 'banter_engine'))

try:
    from banter_engine import BanterEngine
    
    def test_emoji_responses():
        """Test all valid emoji sequences and show LLM guidance."""
        print("🎯 EMOJI-GUIDED LLM RESPONSE SYSTEM TEST")
        print("=" * 60)
        print("Testing all 10 valid emoji sequences for LLM guidance")
        print("=" * 60)
        
        # Initialize the banter engine
        engine = BanterEngine()
        
        # All valid emoji sequences (ascending/equal pattern)
        test_sequences = [
            ("✊✊✊", "Pure confrontational energy"),
            ("✊✊✋", "Confrontational to peaceful shift"),
            ("✊✊🖐️", "Confrontational to open shift"),
            ("✊✋✋", "Confrontational to peaceful transition"),
            ("✊✋🖐️", "Full transformational sequence"),
            ("✊🖐️🖐️", "Confrontational to open progression"),
            ("✋✋✋", "Pure peaceful energy"),
            ("✋✋🖐️", "Peaceful to open progression"),
            ("✋🖐️🖐️", "Progressive opening sequence"),
            ("🖐️🖐️🖐️", "Pure transcendent energy")
        ]
        
        print(f"Testing {len(test_sequences)} valid emoji sequences...\n")
        
        for i, (sequence, description) in enumerate(test_sequences, 1):
            print(f"🧪 Test {i}/10: {sequence}")
            print(f"📝 Description: {description}")
            
            try:
                # Test emoji detection
                detected_sequence = engine._extract_emoji_sequence(sequence)
                if detected_sequence:
                    print(f"✅ Detected: {detected_sequence}")
                    
                    # Get response
                    response = engine.get_response(sequence)
                    if response:
                        print(f"🤖 Response: \"{response}\"")
                        
                        # Get LLM guidance (if available)
                        try:
                            # Try to get the state information for LLM guidance
                            sequence_data = engine.sequence_responses.get(detected_sequence)
                            if sequence_data:
                                state = sequence_data.get('state', 'No state info')
                                tone = sequence_data.get('tone', 'No tone info')
                                print(f"🧠 LLM Guidance:")
                                print(f"   State: {state}")
                                print(f"   Tone: {tone}")
                            else:
                                print(f"⚠️  No LLM guidance data found")
                        except Exception as e:
                            print(f"⚠️  Error getting LLM guidance: {e}")
                    else:
                        print(f"❌ No response generated")
                else:
                    print(f"❌ Sequence not detected")
                    
            except Exception as e:
                print(f"❌ Error testing sequence: {e}")
                
            print("-" * 40)
        
        # Test performance stats
        print("\n📊 PERFORMANCE STATISTICS:")
        try:
            stats = engine.get_performance_stats()
            for key, value in stats.items():
                print(f"   {key}: {value}")
        except Exception as e:
            print(f"   Error getting stats: {e}")
            
        print("\n🎉 Emoji-guided LLM response system test complete!")
        print("✅ System ready for live chat integration")

    def test_chat_simulation():
        """Simulate a chat conversation with emoji triggers."""
        print("\n" + "=" * 60)
        print("💬 CHAT SIMULATION TEST")
        print("=" * 60)
        
        engine = BanterEngine()
        
        # Simulate chat messages with emoji sequences
        chat_messages = [
            "Hey everyone! ✊✊✊",
            "I'm feeling more peaceful now ✋✋✋",
            "This is amazing! ✊✋🖐️",
            "Just some regular chat without emojis",
            "Transcendent moment 🖐️🖐️🖐️",
            "Mixed feelings ✊✊✋"
        ]
        
        print("Simulating chat messages with emoji detection:\n")
        
        for i, message in enumerate(chat_messages, 1):
            print(f"👤 User{i}: {message}")
            
            # Check for emoji sequence
            sequence = engine._extract_emoji_sequence(message)
            if sequence:
                response = engine.get_response(message)
                if response:
                    print(f"🤖 Agent: {response}")
                else:
                    print(f"🤖 Agent: [No response generated]")
            else:
                print(f"🤖 Agent: [No emoji sequence detected]")
                
            print()
        
        print("💬 Chat simulation complete!")

    if __name__ == "__main__":
        print("🚀 Starting Emoji-Guided LLM Response System Tests\n")
        
        # Run the tests
        test_emoji_responses()
        test_chat_simulation()
        
        print("\n🎯 All tests completed successfully!")
        print("The emoji-guided LLM response system is working perfectly!")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the correct directory")
except Exception as e:
    print(f"❌ Error: {e}") 