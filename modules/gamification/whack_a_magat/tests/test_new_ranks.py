#!/usr/bin/env python3
"""
Test the new MAGADOOM rank system
"""

import sys
import os
sys.path.insert(0, os.getcwd())

from modules.gamification.whack_a_magat.src.whack import get_profile, _update_rank_and_level

def test_rank_progression():
    print("🎮 MAGADOOM RANK PROGRESSION TEST")
    print("="*60)
    
    # Test scores with expected ranks
    test_cases = [
        (0, "COVFEFE CADET"),
        (50, "COVFEFE CADET"),
        (100, "QANON QUASHER"),
        (250, "QANON QUASHER"),
        (300, "MAGA MAULER"),
        (500, "MAGA MAULER"),
        (600, "TROLL TERMINATOR"),
        (900, "TROLL TERMINATOR"),
        (1000, "REDHAT RIPPER"),
        (1400, "REDHAT RIPPER"),
        (1500, "COUP CRUSHER"),
        (2000, "COUP CRUSHER"),
        (2500, "PATRIOT PULVERIZER"),
        (4500, "PATRIOT PULVERIZER"),
        (5000, "FASCIST FRAGGER"),
        (9000, "FASCIST FRAGGER"),
        (10000, "ORANGE OBLITERATOR"),
        (15000, "ORANGE OBLITERATOR"),
        (20000, "MAGA DOOMSLAYER"),
        (40000, "MAGA DOOMSLAYER"),
        (50000, "DEMOCRACY DEFENDER"),
        (100000, "DEMOCRACY DEFENDER"),
    ]
    
    for score, expected_rank in test_cases:
        # Create test profile
        test_profile = get_profile(f"test_user_{score}")
        test_profile.score = score
        _update_rank_and_level(test_profile)
        
        # Check if rank matches expectation
        status = "✅" if test_profile.rank == expected_rank else "❌"
        print(f"{status} {score:6d} XP → {test_profile.rank:20s} (Level {test_profile.level})")
        
        if test_profile.rank != expected_rank:
            print(f"   EXPECTED: {expected_rank}")
    
    print("="*60)
    print("💀 MAGADOOM rank system test complete!")

if __name__ == "__main__":
    test_rank_progression()