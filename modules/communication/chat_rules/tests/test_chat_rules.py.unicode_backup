#!/usr/bin/env python3
"""
Test script for the modular chat rules system
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the chat rules modules
from modules.communication.chat_rules.src.user_classifier import UserClassifier, UserType, UserProfile
from modules.communication.chat_rules.src.commands import CommandProcessor
from modules.communication.chat_rules.src.whack_a_magat import WhackAMAGAtSystem, ActionType
from modules.communication.chat_rules.src.response_generator import ResponseGenerator
from modules.communication.chat_rules.src.chat_rules_engine import ChatRulesEngine

def test_user_classification():
    """Test user classification system"""
    print("\n" + "="*60)
    print("TESTING USER CLASSIFICATION")
    print("="*60)
    
    # Test different user types
    test_users = [
        {
            'channelId': 'owner123',
            'displayName': 'ChannelOwner',
            'isChatOwner': True,
            'isChatModerator': False,
            'isChatSponsor': False
        },
        {
            'channelId': 'mod456',
            'displayName': 'SuperMod',
            'isChatOwner': False,
            'isChatModerator': True,
            'isChatSponsor': False
        },
        {
            'channelId': 'member789',
            'displayName': 'PaidMember',
            'isChatOwner': False,
            'isChatModerator': False,
            'isChatSponsor': True
        },
        {
            'channelId': 'regular000',
            'displayName': 'RegularViewer',
            'isChatOwner': False,
            'isChatModerator': False,
            'isChatSponsor': False
        }
    ]
    
    for user_data in test_users:
        profile = UserClassifier.classify(user_data)
        print(f"\n{profile.display_name}:")
        print(f"  Type: {profile.user_type.value}")
        print(f"  Can use commands: {profile.can_use_commands}")
        print(f"  Can trigger emoji: {profile.can_trigger_emoji}")
        print(f"  Can receive responses: {profile.can_receive_responses}")

def test_whack_system():
    """Test WHACK-A-MAGAt point system"""
    print("\n" + "="*60)
    print("TESTING WHACK-A-MAGAt SYSTEM")
    print("="*60)
    
    whack_system = WhackAMAGAtSystem()
    
    # Simulate mod whacking MAGAs
    print("\n🔨 Simulating MAGA whacks:")
    
    result = whack_system.record_whack(
        mod_id="mod123",
        mod_name="SuperMod",
        target="MAGATroll1",
        reason="MAGA spam"
    )
    print(result)
    
    result = whack_system.record_whack(
        mod_id="mod123",
        mod_name="SuperMod",
        target="TrumpFan2024",
        reason="Trump 2024 spam"
    )
    print(result)
    
    result = whack_system.record_whack(
        mod_id="mod456",
        mod_name="EliteMod",
        target="StopTheSteal",
        reason="Election denial"
    )
    print(result)
    
    # Show leaderboard
    print("\n" + whack_system.get_leaderboard(limit=3))
    
    # Show stats
    print(whack_system.get_stats("mod123"))

def test_commands():
    """Test command processing"""
    print("\n" + "="*60)
    print("TESTING COMMAND PROCESSOR")
    print("="*60)
    
    processor = CommandProcessor()
    
    # Create test users
    member = UserProfile(
        user_id="member123",
        channel_id="member123",
        display_name="PaidMember",
        user_type=UserType.MEMBER_TIER_2,
        is_member=True
    )
    member._update_permissions()
    
    moderator = UserProfile(
        user_id="mod123",
        channel_id="mod123",
        display_name="SuperMod",
        user_type=UserType.MODERATOR
    )
    moderator._update_permissions()
    
    regular = UserProfile(
        user_id="regular123",
        channel_id="regular123",
        display_name="RegularViewer",
        user_type=UserType.REGULAR
    )
    
    # Test commands
    print("\n📝 Testing member commands:")
    print(processor.process("/leaders", member))
    print(processor.process("/stats", member))
    print(processor.process("/level", member))
    print(processor.process("/ask How do I reach 222 consciousness?", member))
    
    print("\n🔧 Testing moderator commands:")
    print(processor.process("/fullboard", moderator))
    print(processor.process("/daily", moderator))
    print(processor.process("/whack @MAGATroll spam", moderator))
    
    print("\n❌ Testing regular user (should fail):")
    print(processor.process("/leaders", regular))

def test_chat_engine():
    """Test the main chat rules engine"""
    print("\n" + "="*60)
    print("TESTING CHAT RULES ENGINE")
    print("="*60)
    
    engine = ChatRulesEngine()
    
    # Test message processing
    test_messages = [
        # Owner with emoji sequence
        {
            'authorDetails': {
                'channelId': 'owner123',
                'displayName': 'StreamOwner',
                'isChatOwner': True
            },
            'snippet': {
                'type': 'textMessageEvent',
                'textMessageDetails': {
                    'messageText': 'Testing 🖐🖐🖐'
                }
            }
        },
        # Member asking question
        {
            'authorDetails': {
                'channelId': 'member456',
                'displayName': 'EliteMember',
                'isChatSponsor': True
            },
            'snippet': {
                'type': 'textMessageEvent',
                'textMessageDetails': {
                    'messageText': '/ask What is consciousness?'
                }
            }
        },
        # MAGA message from regular user
        {
            'authorDetails': {
                'channelId': 'troll789',
                'displayName': 'MAGAFan2024'
            },
            'snippet': {
                'type': 'textMessageEvent',
                'textMessageDetails': {
                    'messageText': 'TRUMP 2024 MAGA!'
                }
            }
        },
        # Super Chat
        {
            'authorDetails': {
                'channelId': 'rich123',
                'displayName': 'GenerousViewer'
            },
            'snippet': {
                'type': 'superChatEvent',
                'superChatDetails': {
                    'amountMicros': 25000000,  # $25
                    'currency': 'USD',
                    'userComment': 'Love the stream!'
                }
            }
        },
        # Regular user (should get no response)
        {
            'authorDetails': {
                'channelId': 'regular999',
                'displayName': 'NormalViewer'
            },
            'snippet': {
                'type': 'textMessageEvent',
                'textMessageDetails': {
                    'messageText': 'Hello everyone!'
                }
            }
        }
    ]
    
    print("\n📨 Processing test messages:")
    for i, message in enumerate(test_messages, 1):
        author = message['authorDetails']['displayName']
        text = message['snippet'].get('textMessageDetails', {}).get('messageText', '')
        msg_type = message['snippet']['type']
        
        print(f"\n{i}. {author}: {text if text else msg_type}")
        
        response = engine.process_message(message)
        if response:
            print(f"   🤖 Bot: {response}")
        else:
            print(f"   ❌ No response (user not authorized)")

def test_response_generator():
    """Test response generation"""
    print("\n" + "="*60)
    print("TESTING RESPONSE GENERATOR")
    print("="*60)
    
    generator = ResponseGenerator({})
    
    # Create test users
    tier3_member = UserProfile(
        user_id="elite123",
        channel_id="elite123",
        display_name="EliteSupporter",
        user_type=UserType.MEMBER_TIER_3,
        is_member=True
    )
    tier3_member._update_permissions()
    
    # Test emoji response
    print("\n🎯 Testing emoji responses:")
    response = generator.generate_emoji_response("Hey 🖐🖐🖐", tier3_member)
    print(f"Tier 3 member: {response}")
    
    response = generator.generate_emoji_response("Check this ✊✊✊", tier3_member)
    print(f"Consciousness check: {response}")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print(" MODULAR CHAT RULES SYSTEM TEST SUITE")
    print("="*60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        test_user_classification()
        test_whack_system()
        test_commands()
        test_response_generator()
        test_chat_engine()
        
        print("\n" + "="*60)
        print(" ✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())