#!/usr/bin/env python3
"""
Test timeout announcement system - simulates timeouts to verify announcements work
"""

import asyncio
import time
from datetime import datetime
from modules.gamification.whack_a_magat.src.timeout_announcer import TimeoutManager

def test_timeout_announcements():
    """Test various timeout scenarios"""
    
    print("=" * 60)
    print("TESTING TIMEOUT ANNOUNCEMENT SYSTEM")
    print("=" * 60)
    
    # Initialize timeout manager  
    import os
    test_dir = "./test_memory"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    manager = TimeoutManager(memory_dir=test_dir)
    
    # Test scenarios
    test_cases = [
        # Single timeout (first blood)
        {
            "name": "First Blood (Single Timeout)",
            "timeouts": [
                {"mod_id": "owner", "mod_name": "Move2Japan", "target": "MAGA1", "duration": 300}
            ],
            "delay": 0
        },
        
        # Double whack (2 timeouts within 10 seconds)
        {
            "name": "Double Whack (2 timeouts in 10 sec)",
            "timeouts": [
                {"mod_id": "owner", "mod_name": "Move2Japan", "target": "MAGA2", "duration": 300},
                {"mod_id": "owner", "mod_name": "Move2Japan", "target": "MAGA3", "duration": 300}
            ],
            "delay": 2  # 2 seconds between timeouts
        },
        
        # Triple whack (3 timeouts within 10 seconds)
        {
            "name": "Triple Whack (3 timeouts in 10 sec)",
            "timeouts": [
                {"mod_id": "owner", "mod_name": "Move2Japan", "target": "MAGA4", "duration": 300},
                {"mod_id": "owner", "mod_name": "Move2Japan", "target": "MAGA5", "duration": 300},
                {"mod_id": "owner", "mod_name": "Move2Japan", "target": "MAGA6", "duration": 300}
            ],
            "delay": 3  # 3 seconds between timeouts
        },
        
        # Mega whack (4 timeouts within 10 seconds)
        {
            "name": "Mega Whack (4 timeouts in 10 sec)",
            "timeouts": [
                {"mod_id": "owner", "mod_name": "Move2Japan", "target": "MAGA7", "duration": 300},
                {"mod_id": "owner", "mod_name": "Move2Japan", "target": "MAGA8", "duration": 300},
                {"mod_id": "owner", "mod_name": "Move2Japan", "target": "MAGA9", "duration": 300},
                {"mod_id": "owner", "mod_name": "Move2Japan", "target": "MAGA10", "duration": 300}
            ],
            "delay": 2  # 2 seconds between timeouts
        },
        
        # Test timeout window expiry (>10 seconds)
        {
            "name": "Window Expiry (>10 sec gap resets multi-whack)",
            "timeouts": [
                {"mod_id": "owner", "mod_name": "Move2Japan", "target": "MAGA11", "duration": 300},
                {"mod_id": "owner", "mod_name": "Move2Japan", "target": "MAGA12", "duration": 300}
            ],
            "delay": 11  # 11 seconds - should reset multi-whack counter
        },
        
        # Humiliation (10 second timeout)
        {
            "name": "Humiliation (10 sec timeout)",
            "timeouts": [
                {"mod_id": "owner", "mod_name": "Move2Japan", "target": "Troll1", "duration": 10}
            ],
            "delay": 0
        },
        
        # Brutal Hammer (1 hour timeout)
        {
            "name": "Brutal Hammer (1 hour timeout)",
            "timeouts": [
                {"mod_id": "owner", "mod_name": "Move2Japan", "target": "BadActor", "duration": 3600}
            ],
            "delay": 0
        },
        
        # Building a kill streak
        {
            "name": "Kill Streak Building (5 timeouts = KILLING SPREE)",
            "timeouts": [
                {"mod_id": "owner", "mod_name": "Move2Japan", "target": f"MAGA{i}", "duration": 300}
                for i in range(13, 18)  # 5 timeouts
            ],
            "delay": 12  # 12 seconds between each (within 15 sec streak window)
        }
    ]
    
    # Run test cases
    for test in test_cases:
        print(f"\n[U+1F9EA] TEST: {test['name']}")
        print("-" * 40)
        
        for i, timeout in enumerate(test['timeouts']):
            if i > 0 and test['delay'] > 0:
                print(f"   ⏱️ Waiting {test['delay']} seconds...")
                time.sleep(test['delay'])
            
            result = manager.record_timeout(
                mod_id=timeout['mod_id'],
                mod_name=timeout['mod_name'],
                target_id=f"channel_{timeout['target']}",
                target_name=timeout['target'],
                duration=timeout['duration'],
                reason="Testing"
            )
            
            print(f"\n   Timeout #{i+1}: {timeout['target']} for {timeout['duration']}s")
            if result['announcement']:
                print(f"   [U+1F4E2] ANNOUNCEMENT: {result['announcement']}")
            if result['level_up']:
                print(f"   [CELEBRATE] LEVEL UP: {result['level_up']}")
            if result['points_gained'] > 0:
                print(f"   [UP] Points: +{result['points_gained']}")
            if result['stats']:
                stats = result['stats']
                print(f"   [DATA] Stats: {stats['title']} | {stats['rank']} | Level {stats['level']} | Score: {stats['score']}")
    
    print("\n" + "=" * 60)
    print("[OK] ANNOUNCEMENT SYSTEM TEST COMPLETE")
    print("=" * 60)
    
    # Show final stats
    print("\n[DATA] FINAL MODERATOR STATS:")
    final_stats = manager.get_player_stats("owner")
    if final_stats:
        print(f"   {final_stats['title']}")
        print(f"   Rank: {final_stats['rank']}")
        print(f"   Level: {final_stats['level']}")
        print(f"   Total Score: {final_stats['score']}")
        print(f"   Current Streak: {manager.kill_streaks.get('owner', 0)}")
    
    print("\n[IDEA] NOTES:")
    print("   - Multi-whack window is 10 seconds (for YouTube's slow UI)")
    print("   - Kill streak window is 15 seconds")
    print("   - YouTube API limitation: Can't detect which mod performed timeout")
    print("   - All timeouts appear to come from stream owner")

if __name__ == "__main__":
    test_timeout_announcements()