#!/usr/bin/env python3
"""
Test MAGADOOM XP and announcements from timeout events
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.communication.livechat.src.event_handler import EventHandler
from modules.gamification.whack_a_magat import get_profile

def test_magadoom_xp():
    print("🎮 Testing MAGADOOM XP System\n")
    print("=" * 60)
    
    # Initialize event handler
    event_handler = EventHandler("memory")
    
    # Test moderator IDs
    test_mod_id = "mod_test_123"
    test_mod_name = "TestModerator"
    
    # Get initial profile
    initial_profile = get_profile(test_mod_id, test_mod_name)
    print(f"📊 Initial Profile for {test_mod_name}:")
    print(f"   Score: {initial_profile.score} XP")
    print(f"   Rank: {initial_profile.rank}")
    print(f"   Level: {initial_profile.level}")
    print(f"   Frags: {initial_profile.frag_count}")
    print()
    
    # Simulate timeout events
    test_events = [
        {
            "type": "timeout_event",
            "target_name": "MAGATroll1",
            "target_channel_id": "troll1",
            "moderator_name": test_mod_name,
            "moderator_id": test_mod_id,
            "duration_seconds": 10,
            "deleted_text": "MAGA 2024!"
        },
        {
            "type": "ban_event",
            "target_name": "TrumpFan2024",
            "target_channel_id": "fan2024",
            "moderator_name": test_mod_name,
            "moderator_id": test_mod_id,
            "duration_seconds": 300,
            "is_permanent": False
        },
        {
            "type": "timeout_event",
            "target_name": "QAnonBeliever",
            "target_channel_id": "qanon1",
            "moderator_name": test_mod_name,
            "moderator_id": test_mod_id,
            "duration_seconds": 60
        }
    ]
    
    print("🔨 Processing timeout/ban events:\n")
    
    for i, event in enumerate(test_events, 1):
        print(f"Event {i}: {event['type']} - {event['target_name']} ({event['duration_seconds']}s)")
        
        # Process the event
        if event["type"] == "timeout_event":
            result = event_handler.handle_timeout_event(event)
        else:
            result = event_handler.handle_ban_event(event)
        
        # Show announcement
        if result.get("announcement"):
            print(f"📢 Announcement: {result['announcement']}")
        
        if result.get("level_up"):
            print(f"🆙 Level up: {result['level_up']}")
        
        # Get updated profile
        updated_profile = get_profile(test_mod_id, test_mod_name)
        print(f"📈 Updated stats: {updated_profile.score} XP | {updated_profile.rank} | Level {updated_profile.level} | {updated_profile.frag_count} frags")
        print()
    
    # Final summary
    final_profile = get_profile(test_mod_id, test_mod_name)
    print("=" * 60)
    print(f"📊 Final Profile for {test_mod_name}:")
    print(f"   Score: {final_profile.score} XP (gained {final_profile.score - initial_profile.score})")
    print(f"   Rank: {final_profile.rank}")
    print(f"   Level: {final_profile.level}")
    print(f"   Frags: {final_profile.frag_count} (gained {final_profile.frag_count - initial_profile.frag_count})")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_magadoom_xp()