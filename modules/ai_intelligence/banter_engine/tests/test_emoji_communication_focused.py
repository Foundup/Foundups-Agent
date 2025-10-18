"""
Focused Emoji Communication Tests for Banter Engine
Following WSP Guidelines for Test-to-Main Refactoring

This test suite focuses specifically on the banter engine's emoji detection
and response capabilities without complex module dependencies.

WSP Compliance:
- Tests ensure emoji detection works for all sequences
- Validates LLM guidance extraction from emoji patterns
- Confirms agent responds appropriately to emoji triggers
"""

import unittest
import time
from unittest.mock import Mock, MagicMock

# Import only what we need from the banter engine
from ..src.banter_engine import BanterEngine, BanterEngineError, EmojiSequenceError


class TestEmojiCommunicationFocused(unittest.TestCase):
    """Focused tests for emoji communication in the banter engine."""
    
    def setUp(self):
        """Set up test environment."""
        self.banter_engine = BanterEngine()

    def test_all_emoji_sequences_detection_comprehensive(self):
        """Test detection of all 27 possible emoji sequences (0-0-0 through 2-2-2)."""
        print("\n[TARGET] TESTING ALL 27 EMOJI SEQUENCE DETECTION")
        print("=" * 70)
        
        # All possible 3-emoji sequences (0-0-0 through 2-2-2)
        test_sequences = [
            ("[U+270A][U+270A][U+270A]", (0, 0, 0), "Pure confrontational energy"),
            ("[U+270A][U+270A][U+270B]", (0, 0, 1), "Confrontational to peaceful shift"),
            ("[U+270A][U+270A][U+1F590]️", (0, 0, 2), "Confrontational to open shift"),
            ("[U+270A][U+270B][U+270A]", (0, 1, 0), "Confrontational with peaceful pause"),
            ("[U+270A][U+270B][U+270B]", (0, 1, 1), "Confrontational to peaceful transition"),
            ("[U+270A][U+270B][U+1F590]️", (0, 1, 2), "Full transformational sequence"),
            ("[U+270A][U+1F590]️[U+270A]", (0, 2, 0), "Confrontational with open pause"),
            ("[U+270A][U+1F590]️[U+270B]", (0, 2, 1), "Complex transition pattern"),
            ("[U+270A][U+1F590]️[U+1F590]️", (0, 2, 2), "Confrontational to open progression"),
            ("[U+270B][U+270A][U+270A]", (1, 0, 0), "Peaceful to confrontational shift"),
            ("[U+270B][U+270A][U+270B]", (1, 0, 1), "Peaceful-confrontational oscillation"),
            ("[U+270B][U+270A][U+1F590]️", (1, 0, 2), "Mixed energy progression"),
            ("[U+270B][U+270B][U+270A]", (1, 1, 0), "Peaceful to confrontational"),
            ("[U+270B][U+270B][U+270B]", (1, 1, 1), "Pure peaceful energy"),
            ("[U+270B][U+270B][U+1F590]️", (1, 1, 2), "Peaceful to open progression"),
            ("[U+270B][U+1F590]️[U+270A]", (1, 2, 0), "Complex to confrontational"),
            ("[U+270B][U+1F590]️[U+270B]", (1, 2, 1), "Complex peaceful pattern"),
            ("[U+270B][U+1F590]️[U+1F590]️", (1, 2, 2), "Progressive opening sequence"),
            ("[U+1F590]️[U+270A][U+270A]", (2, 0, 0), "Open to confrontational shift"),
            ("[U+1F590]️[U+270A][U+270B]", (2, 0, 1), "Open to mixed energy"),
            ("[U+1F590]️[U+270A][U+1F590]️", (2, 0, 2), "Open-confrontational oscillation"),
            ("[U+1F590]️[U+270B][U+270A]", (2, 1, 0), "Open to confrontational via peaceful"),
            ("[U+1F590]️[U+270B][U+270B]", (2, 1, 1), "Open to peaceful progression"),
            ("[U+1F590]️[U+270B][U+1F590]️", (2, 1, 2), "Open progression via peaceful"),
            ("[U+1F590]️[U+1F590]️[U+270A]", (2, 2, 0), "Open to confrontational"),
            ("[U+1F590]️[U+1F590]️[U+270B]", (2, 2, 1), "Open to peaceful"),
            ("[U+1F590]️[U+1F590]️[U+1F590]️", (2, 2, 2), "Pure transcendent energy"),
        ]
        
        detected_count = 0
        response_count = 0
        guidance_count = 0
        
        for emoji_seq, expected_tuple, description in test_sequences:
            print(f"\nTesting: {emoji_seq} -> {expected_tuple}")
            print(f"  Description: {description}")
            
            # Test banter engine detection
            state_info, response = self.banter_engine.process_input(emoji_seq)
            
            if "No sequence detected" not in state_info:
                detected_count += 1
                print(f"  [OK] Detected: {state_info}")
                
                # Check for LLM guidance in the state
                if any(keyword in state_info.lower() for keyword in ["state:", "tone:", "confrontational", "peaceful", "transcendent"]):
                    guidance_count += 1
                    print(f"  [AI] LLM Guidance: Available")
                
                if response and isinstance(response, str) and response.strip():
                    response_count += 1
                    print(f"  [NOTE] Response: {response}")
                else:
                    print(f"  [U+26A0]️  No response generated")
            else:
                print(f"  [FAIL] Not detected")
        
        print(f"\n[DATA] COMPREHENSIVE DETECTION SUMMARY:")
        print(f"  Total sequences tested: {len(test_sequences)}")
        print(f"  Sequences detected: {detected_count}/{len(test_sequences)} ({detected_count/len(test_sequences)*100:.1f}%)")
        print(f"  Responses generated: {response_count}/{detected_count} ({response_count/detected_count*100:.1f}% of detected)")
        print(f"  LLM guidance provided: {guidance_count}/{detected_count} ({guidance_count/detected_count*100:.1f}% of detected)")
        
        # WSP Assertions - ensure high detection rate for emoji-guided LLM system
        self.assertGreater(detected_count, 20, "Should detect most emoji sequences (>20/27)")
        self.assertGreater(response_count, detected_count * 0.8, "Should generate responses for most detected sequences")
        self.assertGreater(guidance_count, detected_count * 0.7, "Should provide LLM guidance for most sequences")

    def test_embedded_emoji_sequences_in_chat_messages(self):
        """Test emoji sequences embedded in realistic chat messages."""
        print("\n[SEARCH] TESTING EMBEDDED EMOJI SEQUENCES IN CHAT")
        print("=" * 70)
        
        realistic_chat_messages = [
            "Hello everyone [U+270A][U+270A][U+270A] what's happening in the stream?",
            "I'm feeling really [U+270B][U+270B][U+270B] right now, very peaceful vibes",
            "Check this out [U+270A][U+270B][U+1F590]️ amazing transformation happening!",
            "Testing the transcendent mode [U+1F590]️[U+1F590]️[U+1F590]️ here in chat",
            "Multiple sequences [U+270A][U+270A][U+270A] and [U+270B][U+270B][U+270B] in one message wow",
            "Start [U+270A] middle [U+270B] end [U+1F590]️ spread out across message",
            "Random chat without any triggers at all, just talking",
            "Partial sequence [U+270A][U+270B] incomplete, should not trigger",
            "Wrong emojis [U+1F60A][U+1F60D][U+1F970] should definitely not trigger anything",
            "Mixed valid [U+270A][U+270B][U+1F590]️ and invalid [U+1F60A] emojis together",
            "Hey streamer! [U+270A][U+270A][U+270A] Love the content today!",
            "Peaceful energy [U+270B][U+270B][U+270B] sending good vibes to everyone",
            "Transformation time [U+270A][U+270B][U+1F590]️ let's see what happens next",
            "Ultimate transcendence [U+1F590]️[U+1F590]️[U+1F590]️ achieved in this moment",
            "Quick [U+270A][U+270B][U+1F590]️ trigger in the middle of longer text here",
        ]
        
        detected_count = 0
        total_messages = len(realistic_chat_messages)
        
        for i, msg in enumerate(realistic_chat_messages, 1):
            print(f"\n[NOTE] Message {i}: '{msg}'")
            
            state_info, response = self.banter_engine.process_input(msg)
            
            if "No sequence detected" not in state_info:
                detected_count += 1
                print(f"  [OK] Detected: {state_info}")
                if response:
                    print(f"  [NOTE] Response: {response}")
                    
                    # Verify response is appropriate for chat context
                    self.assertIsInstance(response, str, "Response should be a string")
                    self.assertGreater(len(response.strip()), 0, "Response should not be empty")
                    self.assertLess(len(response), 200, "Response should be chat-appropriate length")
            else:
                print(f"  [U+27A1]️  No trigger detected (expected for some messages)")
        
        print(f"\n[DATA] EMBEDDED SEQUENCE SUMMARY:")
        print(f"  Total messages: {total_messages}")
        print(f"  Triggered responses: {detected_count}")
        print(f"  Trigger rate: {detected_count/total_messages*100:.1f}%")
        
        # Should detect clear embedded sequences (at least 8 out of 15 have clear triggers)
        self.assertGreaterEqual(detected_count, 8, "Should detect clear embedded sequences")

    def test_llm_guidance_extraction_for_integration(self):
        """Test that emoji sequences provide proper guidance for future LLM integration."""
        print("\n[AI] TESTING LLM GUIDANCE EXTRACTION")
        print("=" * 70)
        
        # Key sequences that should provide specific LLM guidance
        guidance_test_cases = [
            ("[U+270A][U+270A][U+270A]", ["confrontational", "challenging", "aggressive"], "Should guide toward confrontational responses"),
            ("[U+270B][U+270B][U+270B]", ["peaceful", "calm", "centered"], "Should guide toward peaceful responses"),
            ("[U+270A][U+270B][U+1F590]️", ["transformational", "breakthrough", "change"], "Should guide toward transformational responses"),
            ("[U+1F590]️[U+1F590]️[U+1F590]️", ["transcendent", "unity", "elevated"], "Should guide toward transcendent responses"),
            ("[U+270A][U+270B][U+270B]", ["transition", "peaceful"], "Should guide toward transitional responses"),
            ("[U+270B][U+1F590]️[U+1F590]️", ["opening", "expansion"], "Should guide toward opening responses"),
        ]
        
        guidance_results = []
        
        for emoji_seq, expected_keywords, description in guidance_test_cases:
            print(f"\nTesting: {emoji_seq}")
            print(f"  Expected guidance: {expected_keywords}")
            
            state_info, response = self.banter_engine.process_input(emoji_seq)
            
            if "No sequence detected" not in state_info:
                print(f"  [OK] State: {state_info}")
                
                # Extract guidance information
                state_lower = state_info.lower()
                found_keywords = [kw for kw in expected_keywords if kw in state_lower]
                
                guidance_quality = len(found_keywords) / len(expected_keywords)
                guidance_results.append({
                    "sequence": emoji_seq,
                    "state": state_info,
                    "expected": expected_keywords,
                    "found": found_keywords,
                    "quality": guidance_quality,
                    "description": description
                })
                
                if found_keywords:
                    print(f"  [TARGET] Guidance found: {found_keywords}")
                    print(f"  [DATA] Quality: {guidance_quality*100:.1f}%")
                else:
                    print(f"  [U+26A0]️  No specific guidance keywords found")
                    
                if response:
                    print(f"  [NOTE] Response: {response}")
            else:
                print(f"  [FAIL] Sequence not detected")
                guidance_results.append({
                    "sequence": emoji_seq,
                    "state": "not_detected",
                    "quality": 0,
                    "description": description
                })
        
        # Analyze guidance quality
        detected_guidance = [r for r in guidance_results if r["state"] != "not_detected"]
        avg_quality = sum(r["quality"] for r in detected_guidance) / len(detected_guidance) if detected_guidance else 0
        
        print(f"\n[DATA] LLM GUIDANCE ANALYSIS:")
        print(f"  Sequences with guidance: {len(detected_guidance)}/{len(guidance_test_cases)}")
        print(f"  Average guidance quality: {avg_quality*100:.1f}%")
        
        # WSP Assertion - ensure good LLM guidance for integration
        self.assertGreater(len(detected_guidance), 4, "Should provide guidance for most key sequences")
        self.assertGreater(avg_quality, 0.3, "Should provide meaningful guidance keywords")

    def test_performance_and_caching_under_load(self):
        """Test system performance and caching under realistic chat load."""
        print("\n[LIGHTNING] TESTING PERFORMANCE UNDER CHAT LOAD")
        print("=" * 70)
        
        # Generate realistic chat load
        emoji_patterns = ["[U+270A][U+270A][U+270A]", "[U+270B][U+270B][U+270B]", "[U+270A][U+270B][U+1F590]️", "[U+1F590]️[U+1F590]️[U+1F590]️"]
        chat_templates = [
            "Hey everyone {emoji} great stream!",
            "Feeling {emoji} right now",
            "Check this {emoji} out",
            "{emoji} vibes in the chat",
            "Message with {emoji} in the middle",
        ]
        
        test_messages = []
        for i in range(200):  # Simulate 200 chat messages
            emoji = emoji_patterns[i % len(emoji_patterns)]
            template = chat_templates[i % len(chat_templates)]
            message = template.format(emoji=emoji)
            test_messages.append(message)
        
        # Clear cache to start fresh
        if hasattr(self.banter_engine, 'clear_cache'):
            self.banter_engine.clear_cache()
        
        # Time the processing
        start_time = time.time()
        
        processed_count = 0
        response_count = 0
        
        for i, message in enumerate(test_messages):
            try:
                state_info, response = self.banter_engine.process_input(message)
                if "No sequence detected" not in state_info:
                    processed_count += 1
                    if response:
                        response_count += 1
                        
                # Print progress every 50 messages
                if (i + 1) % 50 == 0:
                    print(f"  Processed {i + 1}/{len(test_messages)} messages...")
                    
            except Exception as e:
                print(f"  Error processing message {i}: {e}")
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Get performance statistics
        stats = self.banter_engine.get_performance_stats()
        
        print(f"\n[DATA] PERFORMANCE RESULTS:")
        print(f"  Messages processed: {processed_count}/{len(test_messages)}")
        print(f"  Responses generated: {response_count}")
        print(f"  Total time: {processing_time:.3f} seconds")
        print(f"  Messages per second: {len(test_messages)/processing_time:.1f}")
        print(f"  Average time per message: {processing_time/len(test_messages)*1000:.2f} ms")
        print(f"  Cache hit rate: {stats.get('cache_hit_rate_percent', 0):.1f}%")
        print(f"  Success rate: {stats.get('success_rate_percent', 0):.1f}%")
        
        # Performance assertions for chat responsiveness
        self.assertLess(processing_time, 20.0, "Should process 200 messages in under 20 seconds")
        self.assertGreater(processed_count, 150, "Should successfully process most messages")
        self.assertGreater(stats.get('cache_hit_rate_percent', 0), 10, "Should benefit from caching")

    def test_error_recovery_and_robustness(self):
        """Test system recovery from various error scenarios in chat context."""
        print("\n[TOOL] TESTING ERROR RECOVERY IN CHAT CONTEXT")
        print("=" * 70)
        
        # Test various problematic inputs that might occur in real chat
        problematic_inputs = [
            (None, "None input"),
            ("", "Empty string"),
            ("   ", "Whitespace only"),
            (123, "Integer input"),
            ([], "List input"),
            ({}, "Dict input"),
            ("[U+270A]" * 1000, "Extremely long emoji sequence"),
            ("[U+270A][U+270B][U+1F590]️" + "x" * 5000, "Valid sequence with very long text"),
            ("[U+270A]\n[U+270B]\n[U+1F590]️", "Sequence with newlines"),
            ("[U+270A]\t[U+270B]\t[U+1F590]️", "Sequence with tabs"),
            ("[U+270A][U+270B][U+1F590]️ 中文测试", "Unicode text"),
            ("[U+270A][U+270B][U+1F590]️ العربية", "Arabic text"),
            ("[U+270A][U+270B][U+1F590]️ [U+1F31F][CELEBRATE][U+1F525][U+1F4AF]", "Mixed emojis"),
            ("[U+270A][U+270B]", "Incomplete sequence"),
            ("[U+1F60A][U+1F60D][U+1F970]", "Wrong emojis"),
            ("[U+270A][U+270B][U+1F590]️\x00\x01\x02", "Control characters"),
        ]
        
        recovery_count = 0
        error_count = 0
        
        for test_input, description in problematic_inputs:
            print(f"\nTesting: {description}")
            print(f"  Input: {repr(test_input)}")
            
            try:
                state_info, response = self.banter_engine.process_input(test_input)
                recovery_count += 1
                print(f"  [OK] Recovered: {state_info}")
                
                # Verify graceful handling
                self.assertIsNotNone(state_info, "Should return some state info")
                self.assertIsInstance(state_info, str, "State info should be string")
                
                if response:
                    self.assertIsInstance(response, str, "Response should be string if provided")
                    print(f"  [NOTE] Response: {response}")
                    
            except Exception as e:
                error_count += 1
                print(f"  [FAIL] Error: {e}")
        
        print(f"\n[DATA] ERROR RECOVERY SUMMARY:")
        print(f"  Total problematic inputs: {len(problematic_inputs)}")
        print(f"  Successful recoveries: {recovery_count}")
        print(f"  Unhandled errors: {error_count}")
        print(f"  Recovery rate: {recovery_count/len(problematic_inputs)*100:.1f}%")
        
        # WSP Assertion - should handle most problematic inputs gracefully
        self.assertGreater(recovery_count, len(problematic_inputs) * 0.8, 
                          "Should gracefully handle most problematic inputs")

    def test_agent_response_appropriateness(self):
        """Test that agent responses are appropriate for chat context."""
        print("\n[BOT] TESTING AGENT RESPONSE APPROPRIATENESS")
        print("=" * 70)
        
        # Test sequences that should generate responses
        response_test_cases = [
            ("[U+270A][U+270A][U+270A]", "confrontational"),
            ("[U+270B][U+270B][U+270B]", "peaceful"),
            ("[U+270A][U+270B][U+1F590]️", "transformational"),
            ("[U+1F590]️[U+1F590]️[U+1F590]️", "transcendent"),
        ]
        
        appropriate_responses = 0
        total_responses = 0
        
        for emoji_seq, expected_tone in response_test_cases:
            print(f"\nTesting response for: {emoji_seq} (expected: {expected_tone})")
            
            state_info, response = self.banter_engine.process_input(emoji_seq)
            
            if response and isinstance(response, str) and response.strip():
                total_responses += 1
                print(f"  [NOTE] Response: {response}")
                
                # Check response appropriateness
                response_checks = {
                    "length": 10 <= len(response) <= 200,
                    "not_empty": response.strip() != "",
                    "is_string": isinstance(response, str),
                    "no_control_chars": all(ord(c) >= 32 or c in '\n\t' for c in response),
                    "has_content": any(c.isalnum() for c in response),
                }
                
                passed_checks = sum(response_checks.values())
                appropriateness_score = passed_checks / len(response_checks)
                
                print(f"  [DATA] Appropriateness: {appropriateness_score*100:.1f}%")
                print(f"    Length appropriate: {response_checks['length']}")
                print(f"    Has content: {response_checks['has_content']}")
                print(f"    Clean format: {response_checks['no_control_chars']}")
                
                if appropriateness_score >= 0.8:
                    appropriate_responses += 1
                    print(f"  [OK] Response deemed appropriate")
                else:
                    print(f"  [U+26A0]️  Response needs improvement")
            else:
                print(f"  [FAIL] No valid response generated")
        
        print(f"\n[DATA] RESPONSE APPROPRIATENESS SUMMARY:")
        print(f"  Total responses generated: {total_responses}")
        print(f"  Appropriate responses: {appropriate_responses}")
        print(f"  Appropriateness rate: {appropriate_responses/total_responses*100:.1f}%" if total_responses > 0 else "No responses to evaluate")
        
        # WSP Assertion - responses should be appropriate for chat
        self.assertGreater(total_responses, 2, "Should generate responses for key sequences")
        if total_responses > 0:
            self.assertGreater(appropriate_responses/total_responses, 0.7, 
                              "Most responses should be appropriate for chat")

    def tearDown(self):
        """Clean up after tests."""
        # Clear any caches
        if hasattr(self.banter_engine, 'clear_cache'):
            self.banter_engine.clear_cache()


if __name__ == "__main__":
    # Configure logging for test output
    import logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise during tests
    
    # Run the tests
    unittest.main(verbosity=2) 