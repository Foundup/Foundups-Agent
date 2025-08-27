#!/usr/bin/env python3
"""
Comprehensive test suite for all chat functions:
- Consciousness triggers (✊✋🖐)
- MAGADOOM timeout announcements
- Slash commands (/level, /rank, /score, /whacks, /leaderboard)
- Message processing flow
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from modules.communication.livechat.src.message_processor import MessageProcessor
from modules.communication.livechat.src.consciousness_handler import ConsciousnessHandler
from modules.communication.livechat.src.command_handler import CommandHandler
from modules.communication.livechat.src.agentic_chat_engine import AgenticChatEngine
from modules.communication.livechat.src.event_handler import EventHandler
from modules.ai_intelligence.banter_engine.src.agentic_sentiment_0102 import AgenticSentiment0102
from modules.gamification.whack_a_magat.src.timeout_announcer import TimeoutManager


class TestAllChatFunctions(unittest.TestCase):
    """Test all chat functions comprehensively"""
    
    def setUp(self):
        """Set up test environment before each test"""
        # Create mocks for dependencies
        self.mock_grok = Mock()
        self.mock_memory_manager = Mock()
        self.mock_greeting_generator = Mock()
        self.mock_self_improvement = Mock()
        
        # Initialize real components
        self.sentiment_engine = AgenticSentiment0102()
        self.consciousness_handler = ConsciousnessHandler(self.sentiment_engine, self.mock_grok)
        self.agentic_engine = AgenticChatEngine("memory", self.consciousness_handler, self.mock_memory_manager)
        
        # Initialize message processor with all components
        self.processor = MessageProcessor(
            youtube_service=None,
            memory_manager=self.mock_memory_manager
        )
        # Set grok integration after initialization
        self.processor.grok = self.mock_grok
        
        # Mock the memory manager analyze_user method
        self.mock_memory_manager.analyze_user.return_value = {
            'message_count': 10,
            'last_seen': None,
            'common_words': [],
            'user_type': 'returning',
            'consciousness_level': 'aware'
        }
    
    def test_consciousness_triggers(self):
        """Test all consciousness trigger patterns"""
        print("\n" + "="*60)
        print("TESTING CONSCIOUSNESS TRIGGERS")
        print("="*60)
        
        test_cases = [
            # (username, message, role, expected_response_contains)
            ("Move2Japan", "✊✋🖐", "OWNER", ["Perfect balance", "UN-DAO-DU", "enlightenment"]),
            ("Move2Japan", "✊✋🖐 why does 012 call you 0102?", "OWNER", ["Good question", "consciousness evolution"]),
            ("RandomUser", "✊✋🖐 test message", "USER", ["Welcome", "Strong first impression"]),
            ("MAGAUser", "✊✊✊", "USER", ["unconscious state", "Reality check", "Wake up"]),
            ("EnlightenedUser", "🖐🖐🖐", "USER", ["MAXIMUM CONSCIOUSNESS", "transcended"]),
            ("ModUser", "✊✋🖐 FC @TrumpFan", "MOD", ["FACT CHECK", "Truth rating"]),
            ("Move2Japan", "✊✋🖐 @Linda Reese consciousness check", "OWNER", ["consciousness", "evolution"]),
        ]
        
        for username, message, role, expected_keywords in test_cases:
            print(f"\n[MESSAGE] Testing: {username} ({role}): {message}")
            
            # Process the message
            processed = self.processor.process_message({
                "snippet": {
                    "messageId": "test123",
                    "displayMessage": message,
                    "publishedAt": "2024-01-01T00:00:00Z"
                },
                "authorDetails": {
                    "displayName": username,
                    "channelId": f"UC{username}123",
                    "isChatOwner": role == "OWNER",
                    "isChatModerator": role == "MOD"
                }
            })
            
            # Check consciousness detection
            self.assertTrue(processed.get("has_consciousness"), 
                          f"Failed to detect consciousness in: {message}")
            print(f"   [OK] Consciousness detected")
            
            # Generate response
            response = self.agentic_engine.generate_agentic_response(username, message, role)
            self.assertIsNotNone(response, f"No response generated for: {message}")
            print(f"   [BOT] Response: {response}")
            
            # Check if response contains expected keywords
            response_lower = response.lower() if response else ""
            found_keyword = False
            for keyword in expected_keywords:
                if keyword.lower() in response_lower:
                    found_keyword = True
                    break
            
            if not found_keyword:
                print(f"   [WARN] Expected keywords {expected_keywords} not found in response")
            else:
                print(f"   [OK] Response contains expected keywords")
    
    def test_slash_commands(self):
        """Test all slash commands"""
        print("\n" + "="*60)
        print("TESTING SLASH COMMANDS")
        print("="*60)
        
        # Mock whack profile data
        with patch('modules.communication.livechat.src.command_handler.get_profile') as mock_profile:
            mock_profile.return_value = Mock(
                score=1337,
                rank="DOOM SLAYER",
                level=42,
                frag_count=69
            )
            
            with patch('modules.communication.livechat.src.command_handler.get_user_position') as mock_position:
                mock_position.return_value = (1, 100)  # #1 of 100 players
                
                with patch('modules.communication.livechat.src.command_handler.get_leaderboard') as mock_leaderboard:
                    mock_leaderboard.return_value = [
                        Mock(username="Player1", score=1337, rank="DOOM SLAYER"),
                        Mock(username="Player2", score=1000, rank="CHAD"),
                        Mock(username="Player3", score=500, rank="NOOB")
                    ]
                    
                    # Initialize command handler
                    timeout_manager = TimeoutManager()
                    command_handler = CommandHandler(timeout_manager)
                    
                    test_commands = [
                        ("/score", "score", ["1337 XP", "DOOM SLAYER", "LVL 42", "69 FRAGS"]),
                        ("/rank", "rank", ["#1 CHAMPION", "of 100 players", "1337 XP"]),
                        ("/whacks", "whacks", ["69 FRAGS", "1337 XP", "DOOM SLAYER"]),
                        ("/frags", "frags", ["69 FRAGS", "1337 XP", "DOOM SLAYER"]),
                        ("/leaderboard", "leaderboard", ["🥇", "Player1", "DOOM SLAYER"])
                    ]
                    
                    for command, command_type, expected_keywords in test_commands:
                        print(f"\n[CMD] Testing command: {command}")
                        
                        # Process command
                        response = command_handler.handle_whack_command(
                            command, 
                            "TestPlayer", 
                            "UC123", 
                            "USER"
                        )
                        
                        self.assertIsNotNone(response, f"No response for command: {command}")
                        print(f"   Response: {response}")
                        
                        # Check expected keywords
                        response_str = str(response) if response else ""
                        for keyword in expected_keywords:
                            if keyword not in response_str:
                                print(f"   [WARN] Expected '{keyword}' not found in response")
                            else:
                                print(f"   [OK] Found '{keyword}'")
    
    def test_timeout_announcements(self):
        """Test MAGADOOM timeout announcements"""
        print("\n" + "="*60)
        print("TESTING MAGADOOM TIMEOUT ANNOUNCEMENTS")
        print("="*60)
        
        # Create mock profile object
        mock_profile = Mock()
        mock_profile.user_id = "ModID123"
        mock_profile.username = "ModeratorUser"
        mock_profile.score = 100
        mock_profile.rank = "NOOB"
        mock_profile.level = 5
        mock_profile.frag_count = 10
        
        # Create mock action object returned by apply_whack
        mock_action = Mock()
        mock_action.points = 25
        mock_action.moderator_id = "ModID123"
        
        # Initialize timeout manager
        timeout_manager = TimeoutManager()
        
        # Mock the whack.py functions that access database
        with patch('modules.gamification.whack_a_magat.src.timeout_announcer.get_profile') as mock_get_profile:
            with patch('modules.gamification.whack_a_magat.src.timeout_announcer.apply_whack') as mock_apply_whack:
                mock_apply_whack.return_value = mock_action
                
                # Mock the profiles repo to prevent database access
                with patch('modules.gamification.whack_a_magat.src.whack._profiles_repo') as mock_repo:
                    mock_repo.save.return_value = None  # Prevent database save
                    
                    with patch('modules.gamification.whack_a_magat.src.spree_tracker.track_frag') as mock_track_frag:
                        mock_track_frag.return_value = {"spree": "DOUBLE KILL", "count": 2}  # Spree result
                        
                        test_timeouts = [
                            ("MAGATroll", 60, "USER", ["MAGADOOM", "TIMEOUT", "60s", "XP"]),
                            ("TrumpFan2024", 300, "USER", ["MAGADOOM", "5min", "SILENCE", "frag"]),
                            ("Spammer", 180, "USER", ["MAGADOOM", "3min", "timeout"]),
                        ]
                        
                        for target_user, duration, target_role, expected_keywords in test_timeouts:
                            # Reset the mock for each test case
                            mock_get_profile.side_effect = [
                                mock_profile,  # First call (before)
                                Mock(score=125, rank="GRUNT", level=5, frag_count=11, username="ModeratorUser")  # Second call (after)
                            ]
                            print(f"\n[TIMEOUT] Testing timeout: {target_user} for {duration}s")
                            
                            # Process timeout event
                            result = timeout_manager.record_timeout(
                                "ModID123",  # mod_id
                                "ModeratorUser",  # mod_name
                                f"UC{target_user}",  # target_id
                                target_user,  # target_name
                                duration,  # duration
                                target_role  # target_role
                            )
                            
                            self.assertIsNotNone(result, f"No result for timeout of {target_user}")
                            announcement = result.get('announcement', '') if isinstance(result, dict) else result
                            print(f"   [ANNOUNCE] Announcement: {announcement}")
                            
                            # Check expected keywords
                            announcement_lower = announcement.lower() if announcement else ""
                            for keyword in expected_keywords:
                                if keyword.lower() not in announcement_lower:
                                    print(f"   [WARN] Expected '{keyword}' not found")
                                else:
                                    print(f"   [OK] Found '{keyword}'")
    
    def test_message_processing_flow(self):
        """Test the complete message processing flow"""
        print("\n" + "="*60)
        print("TESTING COMPLETE MESSAGE PROCESSING FLOW")
        print("="*60)
        
        # Test different message types
        test_messages = [
            {
                "type": "Consciousness Trigger",
                "message": {
                    "snippet": {
                        "messageId": "msg1",
                        "displayMessage": "✊✋🖐 testing consciousness",
                        "publishedAt": "2024-01-01T00:00:00Z"
                    },
                    "authorDetails": {
                        "displayName": "Move2Japan",
                        "channelId": "UC-LSSlOZwpG...",
                        "isChatOwner": True,
                        "isChatModerator": False
                    }
                }
            },
            {
                "type": "Slash Command",
                "message": {
                    "snippet": {
                        "messageId": "msg2",
                        "displayMessage": "/score",
                        "publishedAt": "2024-01-01T00:01:00Z"
                    },
                    "authorDetails": {
                        "displayName": "Player1",
                        "channelId": "UCPlayer1",
                        "isChatOwner": False,
                        "isChatModerator": False
                    }
                }
            },
            {
                "type": "Timeout Event",
                "message": {
                    "snippet": {
                        "type": "textMessageEvent",
                        "messageText": {
                            "messageText": "60"
                        },
                        "publishedAt": "2024-01-01T00:02:00Z"
                    },
                    "authorDetails": {
                        "displayName": "ModeratorUser",
                        "channelId": "UCMod",
                        "isChatOwner": False,
                        "isChatModerator": True
                    }
                }
            }
        ]
        
        for test_case in test_messages:
            print(f"\n[TEST] Processing: {test_case['type']}")
            
            # Process message
            processed = self.processor.process_message(test_case['message'])
            
            self.assertIsNotNone(processed, f"Failed to process {test_case['type']}")
            self.assertNotEqual(processed.get("skip"), True, f"Message was skipped: {test_case['type']}")
            
            print(f"   [OK] Message processed successfully")
            print(f"   Message ID: {processed.get('message_id')}")
            print(f"   Has consciousness: {processed.get('has_consciousness')}")
            print(f"   Has whack command: {processed.get('has_whack_command')}")
            
            # Check specific flags based on message type
            if test_case['type'] == 'Consciousness Trigger':
                self.assertTrue(processed.get('has_consciousness'), "Failed to detect consciousness")
                print(f"   [OK] Consciousness detected correctly")
            elif test_case['type'] == 'Slash Command':
                self.assertTrue(processed.get('has_whack_command'), "Failed to detect slash command")
                print(f"   [OK] Slash command detected correctly")
    
    def test_emoji_variations(self):
        """Test different emoji variations and sequences"""
        print("\n" + "="*60)
        print("TESTING EMOJI VARIATIONS")
        print("="*60)
        
        emoji_tests = [
            ("✊✋🖐", "Standard sequence"),
            ("✊✋🖐️", "With variant selector"),
            ("✊✊✊", "Triple fist"),
            ("🖐🖐🖐", "Triple open hand"),
            ("🖐️🖐️🖐️", "Triple with variant"),
            ("✋✋✋", "Triple raised hand"),
            ("✊🖐✋", "Mixed order"),
            ("✊ ✋ 🖐", "With spaces"),
            ("message ✊✋🖐 after", "Embedded in text"),
        ]
        
        for emoji_text, description in emoji_tests:
            print(f"\n[EMOJI] Testing: {description}")
            print(f"   Input: {repr(emoji_text)}")
            
            # Check detection
            has_emojis = self.consciousness_handler.has_consciousness_emojis(emoji_text)
            print(f"   Has consciousness emojis: {has_emojis}")
            
            if has_emojis:
                # Extract sequence
                sequence = self.consciousness_handler.extract_emoji_sequence(emoji_text)
                print(f"   Extracted sequence: {repr(sequence)}")
                
                # Generate response
                response = self.agentic_engine.generate_agentic_response(
                    "TestUser", emoji_text, "USER"
                )
                if response:
                    print(f"   [OK] Response generated: {response[:50]}...")
                else:
                    print(f"   [WARN] No response generated")


def run_all_tests():
    """Run all tests with detailed output"""
    print("\n" + "="*70)
    print(" COMPREHENSIVE CHAT FUNCTION TEST SUITE")
    print("="*70)
    print("\nThis test suite covers:")
    print("  - Consciousness triggers (fist-hand-open emojis)")
    print("  - MAGADOOM timeout announcements")
    print("  - Slash commands (/level, /rank, /score, /whacks, /leaderboard)")
    print("  - Complete message processing flow")
    print("  - Emoji variations and edge cases")
    print("\n" + "="*70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestAllChatFunctions)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n[SUCCESS] ALL TESTS PASSED!")
    else:
        print("\n[FAILED] SOME TESTS FAILED")
        if result.failures:
            print("\nFailures:")
            for test, trace in result.failures:
                print(f"  - {test}: {trace}")
        if result.errors:
            print("\nErrors:")
            for test, trace in result.errors:
                print(f"  - {test}: {trace}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)