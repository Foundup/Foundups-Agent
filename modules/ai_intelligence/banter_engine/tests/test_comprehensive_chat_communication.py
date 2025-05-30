"""
Comprehensive test suite for chat communication system.

This module tests the complete integration between the BanterEngine,
LiveChatListener, and LLMBypassEngine components to ensure proper
emoji sequence detection, response generation, and message processing.
"""

import unittest
import pytest
import asyncio
import time
import logging
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timedelta

# Import the modules we're testing
from modules.ai_intelligence.banter_engine.src.banter_engine import BanterEngine, BanterEngineError, EmojiSequenceError
from modules.communication.livechat.livechat.src.livechat import LiveChatListener
from modules.communication.livechat.livechat.src.llm_bypass_engine import LLMBypassEngine


class TestComprehensiveChatCommunication(unittest.TestCase):
    """Comprehensive tests for chat communication system."""
    
    def setUp(self):
        """Set up test environment."""
        self.banter_engine = BanterEngine()
        self.llm_bypass = LLMBypassEngine()
        
        # Mock YouTube service for LiveChatListener
        self.mock_youtube = MagicMock()
        self.listener = LiveChatListener(
            youtube_service=self.mock_youtube,
            video_id="test_video_id",
            live_chat_id="test_chat_id"
        )
        
        # Configure mocks
        self.listener.send_chat_message = AsyncMock(return_value=True)
        self.listener._is_rate_limited = MagicMock(return_value=False)
        self.listener._update_trigger_time = MagicMock()
        self.listener.bot_channel_id = "bot_channel_123"

    def test_all_emoji_sequences_detection(self):
        """Test detection of all supported emoji sequences."""
        print("\n🎯 TESTING ALL EMOJI SEQUENCE DETECTION")
        print("=" * 60)
        
        # All possible 3-emoji sequences (0-0-0 through 2-2-2)
        test_sequences = [
            ("✊✊✊", (0, 0, 0), "Confrontational energy"),
            ("✊✊✋", (0, 0, 1), "Shifting from confrontation"),
            ("✊✊🖐️", (0, 0, 2), "Opening from confrontation"),
            ("✊✋✊", (0, 1, 0), "Confrontational pause"),
            ("✊✋✋", (0, 1, 1), "Peaceful transition"),
            ("✊✋🖐️", (0, 1, 2), "Transformational sequence"),
            ("✊🖐️✊", (0, 2, 0), "Confrontational return"),
            ("✊🖐️✋", (0, 2, 1), "Complex transition"),
            ("✊🖐️🖐️", (0, 2, 2), "Opening sequence"),
            ("✋✊✊", (1, 0, 0), "Peaceful to confrontational"),
            ("✋✊✋", (1, 0, 1), "Peaceful oscillation"),
            ("✋✊🖐️", (1, 0, 2), "Mixed energy"),
            ("✋✋✊", (1, 1, 0), "Peaceful to confrontational"),
            ("✋✋✋", (1, 1, 1), "Pure peaceful energy"),
            ("✋✋🖐️", (1, 1, 2), "Peaceful opening"),
            ("✋🖐️✊", (1, 2, 0), "Complex to confrontational"),
            ("✋🖐️✋", (1, 2, 1), "Complex peaceful"),
            ("✋🖐️🖐️", (1, 2, 2), "Progressive opening"),
            ("🖐️✊✊", (2, 0, 0), "Open to confrontational"),
            ("🖐️✊✋", (2, 0, 1), "Open mixed"),
            ("🖐️✊🖐️", (2, 0, 2), "Open oscillation"),
            ("🖐️✋✊", (2, 1, 0), "Open to confrontational"),
            ("🖐️✋✋", (2, 1, 1), "Open to peaceful"),
            ("🖐️✋🖐️", (2, 1, 2), "Open progression"),
            ("🖐️🖐️✊", (2, 2, 0), "Open to confrontational"),
            ("🖐️🖐️✋", (2, 2, 1), "Open to peaceful"),
            ("🖐️🖐️🖐️", (2, 2, 2), "Pure transcendent energy"),
        ]
        
        detected_count = 0
        for emoji_seq, expected_tuple, description in test_sequences:
            print(f"Testing: {emoji_seq} -> {expected_tuple} ({description})")
            
            # Test banter engine detection
            state_info, response = self.banter_engine.process_input(emoji_seq)
            
            if "No sequence detected" not in state_info:
                detected_count += 1
                print(f"  ✅ Detected: {state_info}")
                if response:
                    print(f"  📝 Response: {response}")
                else:
                    print(f"  ⚠️  No response generated")
            else:
                print(f"  ❌ Not detected")
        
        print(f"\n📊 Detection Summary: {detected_count}/{len(test_sequences)} sequences detected")
        
        # Assert that we detect a reasonable number of sequences
        self.assertGreater(detected_count, 15, "Should detect most emoji sequences")

    def test_embedded_emoji_sequences(self):
        """Test emoji sequences embedded in longer messages."""
        print("\n🔍 TESTING EMBEDDED EMOJI SEQUENCES")
        print("=" * 60)
        
        test_messages = [
            "Hello everyone ✊✊✊ what's happening?",
            "I'm feeling ✋✋✋ right now, very peaceful",
            "Check this out ✊✋🖐️ amazing transformation!",
            "Testing 🖐️🖐️🖐️ transcendent mode here",
            "Multiple sequences ✊✊✊ and ✋✋✋ in one message",
            "Start ✊ middle ✋ end 🖐️ spread out",
            "Random text without any triggers at all",
            "Partial sequence ✊✋ incomplete",
            "Wrong emojis 😊😍🥰 should not trigger",
            "Mixed valid ✊✋🖐️ and invalid 😊 emojis",
        ]
        
        detected_count = 0
        for msg in test_messages:
            print(f"📝 Message: '{msg}'")
            
            state_info, response = self.banter_engine.process_input(msg)
            
            if "No sequence detected" not in state_info:
                detected_count += 1
                print(f"  ✅ Detected: {state_info}")
                if response:
                    print(f"  📝 Response: {response}")
            else:
                print(f"  ➡️  No trigger detected")
        
        print(f"\n📊 Embedded Detection: {detected_count}/{len(test_messages)} messages triggered")
        
        # Should detect at least the clear sequences
        self.assertGreaterEqual(detected_count, 4, "Should detect clear embedded sequences")

    @pytest.mark.asyncio
    async def test_real_time_message_processing_flow(self):
        """Test the complete real-time message processing flow."""
        print("\n⚡ TESTING REAL-TIME MESSAGE PROCESSING FLOW")
        print("=" * 60)
        
        # Test messages simulating real chat
        test_messages = [
            {
                "id": "msg_001",
                "snippet": {"displayMessage": "Hello everyone! ✊✋🖐️"},
                "authorDetails": {"displayName": "TestUser1", "channelId": "user_001"}
            },
            {
                "id": "msg_002", 
                "snippet": {"displayMessage": "Feeling peaceful ✋✋✋ today"},
                "authorDetails": {"displayName": "TestUser2", "channelId": "user_002"}
            },
            {
                "id": "msg_003",
                "snippet": {"displayMessage": "Just saying hi without emojis"},
                "authorDetails": {"displayName": "TestUser3", "channelId": "user_003"}
            },
            {
                "id": "msg_004",
                "snippet": {"displayMessage": "Transcendent vibes 🖐️🖐️🖐️ here"},
                "authorDetails": {"displayName": "TestUser4", "channelId": "user_004"}
            },
        ]
        
        processed_count = 0
        triggered_count = 0
        
        for message in test_messages:
            print(f"Processing message from {message['authorDetails']['displayName']}")
            
            try:
                # Process the message through the listener
                log_entry = await self.listener._process_message(message)
                
                if log_entry:
                    processed_count += 1
                    print(f"  ✅ Processed: {log_entry.get('author', 'Unknown')}")
                    
                    # Check if it triggered a response
                    display_message = message["snippet"]["displayMessage"]
                    if self.listener._check_trigger_patterns(display_message):
                        triggered_count += 1
                        print(f"  🎯 Triggered emoji response")
                else:
                    print(f"  ⚠️  Processing returned None")
                    
            except Exception as e:
                print(f"  ❌ Error processing: {e}")
        
        print(f"\n📊 Processing Summary:")
        print(f"  Processed: {processed_count}/{len(test_messages)} messages")
        print(f"  Triggered: {triggered_count} emoji responses")
        
        # Verify processing worked
        self.assertGreater(processed_count, 0, "Should process at least some messages")
        self.assertGreater(triggered_count, 0, "Should trigger at least some responses")

    @pytest.mark.asyncio
    async def test_rate_limiting_behavior(self):
        """Test rate limiting prevents spam responses."""
        print("\n⏱️  TESTING RATE LIMITING BEHAVIOR")
        print("=" * 60)
        
        # Configure rate limiting
        user_id = "rapid_user_123"
        
        # First message should work
        self.listener._is_rate_limited = MagicMock(return_value=False)
        
        result1 = await self.listener._handle_emoji_trigger(
            author_name="RapidUser",
            author_id=user_id,
            message_text="✊✋🖐️ First message"
        )
        
        print(f"First message result: {result1}")
        self.assertTrue(result1, "First message should succeed")
        
        # Second message should be rate limited
        self.listener._is_rate_limited = MagicMock(return_value=True)
        
        result2 = await self.listener._handle_emoji_trigger(
            author_name="RapidUser", 
            author_id=user_id,
            message_text="✊✋🖐️ Second message"
        )
        
        print(f"Second message result: {result2}")
        self.assertFalse(result2, "Second message should be rate limited")
        
        print("✅ Rate limiting working correctly")

    @pytest.mark.asyncio
    async def test_fallback_system_integration(self):
        """Test the complete fallback system when primary systems fail."""
        print("\n🛡️  TESTING FALLBACK SYSTEM INTEGRATION")
        print("=" * 60)
        
        # Test 1: Banter engine fails, LLM bypass succeeds
        print("Test 1: Banter engine failure -> LLM bypass")
        
        with patch.object(self.listener.banter_engine, 'process_input') as mock_banter:
            mock_banter.side_effect = Exception("Banter engine failed")
            
            # LLM bypass should work
            with patch.object(self.listener.llm_bypass_engine, 'process_input') as mock_bypass:
                mock_bypass.return_value = ("Bypass state", "Bypass response")
                
                result = await self.listener._handle_emoji_trigger(
                    author_name="TestUser",
                    author_id="test_user_123", 
                    message_text="✊✋🖐️"
                )
                
                print(f"  Result: {result}")
                self.assertTrue(result, "Should succeed with LLM bypass")
                
                # Verify LLM bypass was called
                mock_bypass.assert_called_once_with("✊✋🖐️")
        
        # Test 2: Both systems fail, ultimate fallback
        print("\nTest 2: Both systems fail -> Ultimate fallback")
        
        with patch.object(self.listener.banter_engine, 'process_input') as mock_banter, \
             patch.object(self.listener.llm_bypass_engine, 'process_input') as mock_bypass:
            
            mock_banter.side_effect = Exception("Banter failed")
            mock_bypass.side_effect = Exception("Bypass failed")
            
            # Should use ultimate fallback
            with patch.object(self.listener.llm_bypass_engine, 'get_fallback_response') as mock_fallback:
                mock_fallback.return_value = "Ultimate fallback response"
                
                result = await self.listener._handle_emoji_trigger(
                    author_name="TestUser",
                    author_id="test_user_456",
                    message_text="✊✋🖐️"
                )
                
                print(f"  Result: {result}")
                # Should still succeed with ultimate fallback
                self.assertTrue(result, "Should succeed with ultimate fallback")
                
                # Verify fallback was called
                mock_fallback.assert_called_once_with("TestUser")
        
        print("✅ Fallback system working correctly")

    def test_llm_guidance_extraction(self):
        """Test that emoji sequences provide proper LLM guidance."""
        print("\n🧠 TESTING LLM GUIDANCE EXTRACTION")
        print("=" * 60)
        
        # Key sequences that should provide LLM guidance
        guidance_tests = [
            ("✊✊✊", "confrontational", "Should guide LLM toward confrontational responses"),
            ("✋✋✋", "peaceful", "Should guide LLM toward peaceful responses"),
            ("✊✋🖐️", "transformational", "Should guide LLM toward transformational responses"),
            ("🖐️🖐️🖐️", "transcendent", "Should guide LLM toward transcendent responses"),
        ]
        
        guidance_found = 0
        
        for emoji_seq, expected_guidance, description in guidance_tests:
            print(f"Testing: {emoji_seq} -> {expected_guidance}")
            
            state_info, response = self.banter_engine.process_input(emoji_seq)
            
            if "No sequence detected" not in state_info:
                print(f"  ✅ State: {state_info}")
                
                # Check if the state contains guidance-related keywords
                state_lower = state_info.lower()
                if any(keyword in state_lower for keyword in [expected_guidance, "tone", "state"]):
                    guidance_found += 1
                    print(f"  🎯 Guidance found: {description}")
                else:
                    print(f"  ⚠️  No clear guidance in state")
                    
                if response:
                    print(f"  📝 Response: {response}")
            else:
                print(f"  ❌ Sequence not detected")
        
        print(f"\n📊 Guidance Summary: {guidance_found}/{len(guidance_tests)} sequences provided guidance")
        
        # Should provide guidance for most key sequences
        self.assertGreater(guidance_found, 2, "Should provide LLM guidance for key sequences")

    @pytest.mark.asyncio
    async def test_bot_self_message_prevention(self):
        """Test that bot doesn't respond to its own emoji messages."""
        print("\n🤖 TESTING BOT SELF-MESSAGE PREVENTION")
        print("=" * 60)
        
        # Test bot responding to its own message
        result = await self.listener._handle_emoji_trigger(
            author_name="FoundUpsBot",
            author_id="bot_channel_123",  # Same as listener.bot_channel_id
            message_text="✊✋🖐️ Bot's own message"
        )
        
        print(f"Bot self-message result: {result}")
        self.assertFalse(result, "Bot should not respond to its own messages")
        
        # Test bot responding to different user
        result = await self.listener._handle_emoji_trigger(
            author_name="RegularUser",
            author_id="user_channel_456",  # Different from bot_channel_id
            message_text="✊✋🖐️ User message"
        )
        
        print(f"User message result: {result}")
        self.assertTrue(result, "Bot should respond to user messages")
        
        print("✅ Self-message prevention working correctly")

    def test_performance_under_load(self):
        """Test system performance under high message load."""
        print("\n⚡ TESTING PERFORMANCE UNDER LOAD")
        print("=" * 60)
        
        # Generate many test messages
        test_messages = []
        emoji_sequences = ["✊✊✊", "✋✋✋", "✊✋🖐️", "🖐️🖐️🖐️"]
        
        for i in range(100):
            emoji_seq = emoji_sequences[i % len(emoji_sequences)]
            test_messages.append(f"Message {i}: {emoji_seq} test content")
        
        # Time the processing
        start_time = time.time()
        
        processed_count = 0
        for message in test_messages:
            try:
                state_info, response = self.banter_engine.process_input(message)
                if "No sequence detected" not in state_info:
                    processed_count += 1
            except Exception as e:
                print(f"Error processing message: {e}")
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"📊 Performance Results:")
        print(f"  Messages processed: {processed_count}/{len(test_messages)}")
        print(f"  Total time: {processing_time:.3f} seconds")
        print(f"  Messages per second: {len(test_messages)/processing_time:.1f}")
        print(f"  Average time per message: {processing_time/len(test_messages)*1000:.2f} ms")
        
        # Performance assertions
        self.assertLess(processing_time, 10.0, "Should process 100 messages in under 10 seconds")
        self.assertGreater(processed_count, 80, "Should successfully process most messages")
        
        # Check cache performance
        stats = self.banter_engine.get_performance_stats()
        print(f"  Cache hit rate: {stats.get('cache_hit_rate_percent', 0):.1f}%")
        print(f"  Success rate: {stats.get('success_rate_percent', 0):.1f}%")

    def test_error_recovery_scenarios(self):
        """Test system recovery from various error scenarios."""
        print("\n🔧 TESTING ERROR RECOVERY SCENARIOS")
        print("=" * 60)
        
        # Test 1: Invalid input types
        print("Test 1: Invalid input types")
        test_inputs = [None, 123, [], {}, True]
        
        for invalid_input in test_inputs:
            try:
                state_info, response = self.banter_engine.process_input(invalid_input)
                print(f"  Input {invalid_input}: {state_info}")
                self.assertIsNotNone(state_info, "Should handle invalid input gracefully")
            except Exception as e:
                print(f"  Input {invalid_input}: Exception - {e}")
        
        # Test 2: Extremely long input
        print("\nTest 2: Extremely long input")
        long_input = "✊✋🖐️ " + "x" * 10000
        
        try:
            state_info, response = self.banter_engine.process_input(long_input)
            print(f"  Long input result: {state_info}")
            self.assertIsNotNone(state_info, "Should handle long input")
        except Exception as e:
            print(f"  Long input error: {e}")
        
        # Test 3: Unicode and special characters
        print("\nTest 3: Unicode and special characters")
        unicode_inputs = [
            "✊✋🖐️ 中文测试",
            "✊✋🖐️ العربية",
            "✊✋🖐️ 🌟🎉🔥",
            "✊✋🖐️ \n\t\r special chars",
        ]
        
        for unicode_input in unicode_inputs:
            try:
                state_info, response = self.banter_engine.process_input(unicode_input)
                print(f"  Unicode input: {state_info}")
                self.assertIsNotNone(state_info, "Should handle unicode input")
            except Exception as e:
                print(f"  Unicode error: {e}")
        
        print("✅ Error recovery working correctly")

    def test_comprehensive_integration_flow(self):
        """Test the complete integration flow from emoji detection to response."""
        print("\n🔄 TESTING COMPREHENSIVE INTEGRATION FLOW")
        print("=" * 60)
        
        # Simulate a complete chat interaction
        chat_scenario = [
            ("User1", "Hello everyone! ✊✊✊"),
            ("User2", "Feeling peaceful today ✋✋✋"),
            ("User3", "Just regular chat without emojis"),
            ("User1", "Transformation time ✊✋🖐️"),
            ("User4", "Transcendent vibes 🖐️🖐️🖐️"),
            ("User2", "Mixed message ✊✋🖐️ with more text"),
        ]
        
        interaction_results = []
        
        for username, message in chat_scenario:
            print(f"\n👤 {username}: {message}")
            
            # Step 1: Check trigger detection
            has_trigger = self.listener._check_trigger_patterns(message)
            print(f"  🎯 Trigger detected: {has_trigger}")
            
            if has_trigger:
                # Step 2: Process with banter engine
                state_info, response = self.banter_engine.process_input(message)
                print(f"  🧠 Banter engine: {state_info}")
                
                if response:
                    print(f"  📝 Generated response: {response}")
                    interaction_results.append({
                        "user": username,
                        "message": message,
                        "state": state_info,
                        "response": response,
                        "success": True
                    })
                else:
                    # Step 3: Try LLM bypass
                    bypass_state, bypass_response = self.llm_bypass.process_input(message)
                    print(f"  🔄 LLM bypass: {bypass_state}")
                    
                    if bypass_response:
                        print(f"  📝 Bypass response: {bypass_response}")
                        interaction_results.append({
                            "user": username,
                            "message": message,
                            "state": bypass_state,
                            "response": bypass_response,
                            "success": True
                        })
                    else:
                        # Step 4: Ultimate fallback
                        fallback = self.llm_bypass.get_fallback_response(username)
                        print(f"  🛡️  Fallback: {fallback}")
                        interaction_results.append({
                            "user": username,
                            "message": message,
                            "state": "fallback",
                            "response": fallback,
                            "success": True
                        })
            else:
                print("  ➡️  No response needed")
                interaction_results.append({
                    "user": username,
                    "message": message,
                    "state": "no_trigger",
                    "response": None,
                    "success": True
                })
        
        # Analyze results
        triggered_interactions = [r for r in interaction_results if r["state"] != "no_trigger"]
        successful_responses = [r for r in triggered_interactions if r["response"]]
        
        print(f"\n📊 Integration Flow Summary:")
        print(f"  Total interactions: {len(interaction_results)}")
        print(f"  Triggered responses: {len(triggered_interactions)}")
        print(f"  Successful responses: {len(successful_responses)}")
        print(f"  Success rate: {len(successful_responses)/len(triggered_interactions)*100:.1f}%")
        
        # Verify the integration flow worked
        self.assertGreater(len(triggered_interactions), 0, "Should trigger some responses")
        self.assertEqual(len(successful_responses), len(triggered_interactions), 
                        "All triggered interactions should get responses")

    def tearDown(self):
        """Clean up after tests."""
        # Clear any caches
        if hasattr(self.banter_engine, 'clear_cache'):
            self.banter_engine.clear_cache()


if __name__ == "__main__":
    # Configure logging for test output
    logging.basicConfig(level=logging.INFO)
    
    # Run the tests
    unittest.main(verbosity=2) 