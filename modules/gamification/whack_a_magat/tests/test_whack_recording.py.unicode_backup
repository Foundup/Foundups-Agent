#!/usr/bin/env python3
"""
Test if the whack recording system works manually
"""

import sys
import os
sys.path.insert(0, os.getcwd())

from modules.gamification.whack_a_magat.src.whack import apply_whack, get_profile
from datetime import datetime

def test_whack_system():
    print("🎯 Testing MAGADOOM whack recording system...")
    
    # Test moderator
    mod_id = "UC99a5bqC4Uc634yB-72VRbw"  # 1PissedOffVeteran's actual ID
    target_id = "test_target"
    
    # Check initial state
    initial_profile = get_profile(mod_id)
    print(f"Initial state: {initial_profile.frag_count} frags, {initial_profile.score} XP")
    
    # Record a whack
    print("\n🔥 Recording a whack...")
    action = apply_whack(
        moderator_id=mod_id,
        target_id=target_id,
        duration_sec=300,  # 5 minute timeout
        now=datetime.now()
    )
    print(f"Action recorded: {action.points} points awarded")
    
    # Check updated state  
    updated_profile = get_profile(mod_id)
    print(f"Updated state: {updated_profile.frag_count} frags, {updated_profile.score} XP")
    print(f"Rank: {updated_profile.rank}, Level: {updated_profile.level}")
    
    # Verify the change
    frag_increase = updated_profile.frag_count - initial_profile.frag_count
    xp_increase = updated_profile.score - initial_profile.score
    
    print(f"\n📊 Results:")
    print(f"Frag increase: {frag_increase}")
    print(f"XP increase: {xp_increase}")
    
    if frag_increase > 0 and xp_increase > 0:
        print("✅ Whack recording system is working!")
    else:
        print("❌ Whack recording system has issues!")
        
    return frag_increase > 0 and xp_increase > 0

if __name__ == "__main__":
    test_whack_system()