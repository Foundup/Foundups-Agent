#!/usr/bin/env python3
"""
Test the timeout-based point system with anti-gaming mechanics
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from modules.communication.chat_rules.src.whack_a_magat import WhackAMAGAtSystem, TimeoutDuration

def main():
    print("\n" + "="*60)
    print(" TESTING TIMEOUT POINT SYSTEM")
    print("="*60)
    
    # Initialize system
    system = WhackAMAGAtSystem()
    print("[OK] System initialized with WSP-compliant data location")
    
    # Test 1: Regular timeout progression
    print("\n[TEST 1] Regular timeout progression (no gaming):")
    
    # 10 second timeout - minimal points
    result = system.record_timeout(
        mod_id="mod123",
        mod_name="TestMod",
        target_id="troll1",
        target_name="Troll1",
        duration_seconds=10,
        reason="Minor spam"
    )
    print(f"10 sec timeout result:\n{result}")
    
    # 60 second timeout
    print("\n60 sec timeout:")
    result = system.record_timeout(
        mod_id="mod123",
        mod_name="TestMod",
        target_id="troll2",
        target_name="Troll2",
        duration_seconds=60,
        reason="MAGA spam"
    )
    print(result)
    
    # 5 minute timeout
    print("\n5 min timeout:")
    result = system.record_timeout(
        mod_id="mod123",
        mod_name="TestMod",
        target_id="troll3",
        target_name="Troll3",
        duration_seconds=300,
        reason="Harassment"
    )
    print(result)
    
    # Test 2: Gaming detection - same user repeatedly
    print("\n[TEST 2] Gaming detection - timing out same user:")
    result = system.record_timeout(
        mod_id="mod123",
        mod_name="TestMod",
        target_id="troll1",  # Same user as before
        target_name="Troll1",
        duration_seconds=10,
        reason="Trying to farm points"
    )
    print(f"Same user timeout (should have penalty):\n{result}")
    
    # Test 3: 10-second spam detection
    print("\n[TEST 3] Testing 10-second spam limit:")
    for i in range(6):
        result = system.record_timeout(
            mod_id="mod456",
            mod_name="SpamMod",
            target_id=f"user{i}",
            target_name=f"User{i}",
            duration_seconds=10,
            reason="Quick timeout"
        )
        if i == 5:  # Should trigger penalty on 6th timeout
            print(f"6th 10-sec timeout (should have penalty):\n{result}")
    
    # Test 4: High-value timeout (24 hour ban)
    print("\n[TEST 4] High-value 24-hour ban:")
    result = system.record_timeout(
        mod_id="mod789",
        mod_name="EliteMod",
        target_id="megatroll",
        target_name="MegaTroll",
        duration_seconds=86400,  # 24 hours
        reason="Severe violation - hate speech"
    )
    print(f"24-hour ban result:\n{result}")
    
    # Test 5: Show moderator score
    print("\n[TEST 5] Moderator scores:")
    for mod_id, mod in system.moderators.items():
        print(f"\n{mod.display_name}:")
        print(f"  Total Points: {mod.total_points}")
        print(f"  Level: {mod.level.value[1]}")
        print(f"  Timeouts: 10s:{mod.timeouts_10s}, 60s:{mod.timeouts_60s}, "
              f"5m:{mod.timeouts_5m}, 10m:{mod.timeouts_10m}, "
              f"1h:{mod.timeouts_1h}, 24h:{mod.timeouts_24h}")
    
    # Show point structure
    print("\n" + "="*60)
    print(" POINT STRUCTURE SUMMARY")
    print("="*60)
    print("TIMEOUT DURATIONS & BASE POINTS:")
    for duration in TimeoutDuration:
        print(f"  {duration.description:20} | {duration.seconds:6}s | "
              f"{duration.base_points:3} pts | "
              f"{duration.cooldown_minutes:4}m cooldown")
    
    print("\nANTI-GAMING MECHANICS:")
    print("  - Same user within 30 min: 50% penalty")
    print("  - Same severity on cooldown: 70% penalty")
    print("  - >5 10-sec timeouts in 10 min: 80% penalty")
    print("  - >50 timeouts per day: 90% penalty")
    print("  - Penalties stack and reduce combo multiplier")
    
    print("\nCOMBO SYSTEM:")
    print("  - Actions within 60 seconds increase combo")
    print("  - Max combo multiplier: 2.0x")
    print("  - Gaming penalties disable combo")
    
    return 0

if __name__ == "__main__":
    exit(main())