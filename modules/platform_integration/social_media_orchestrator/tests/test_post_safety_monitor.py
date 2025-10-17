#!/usr/bin/env python3
"""
Test PostSafetyMonitor cancellation detection functionality
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

import asyncio
from modules.platform_integration.social_media_orchestrator.src.post_safety_monitor import PostSafetyMonitor

def test_cancellation_detection():
    """Test that cancellation detection works correctly"""
    print("TESTING POST SAFETY MONITOR - CANCELLATION DETECTION")
    print("=" * 60)

    monitor = PostSafetyMonitor()

    # Test 1: Detect user cancellation
    print("\n1. Testing user cancellation detection:")
    video_id = "test_video_123"
    platform = "linkedin"
    error_msg = "User cancelled the operation"

    detected = monitor.detect_user_cancellation(video_id, platform, error_msg)
    print(f"   Cancellation detected: {detected}")

    if detected:
        print("   [PASS] User cancellation was correctly detected")
    else:
        print("   [FAIL] User cancellation was NOT detected")

    # Test 2: Auto-mark as posted
    print("\n2. Testing auto-mark as posted:")
    title = "Test Stream Title"
    marked = monitor.auto_mark_as_posted(video_id, platform, title)
    print(f"   Auto-marked as posted: {marked}")

    if marked:
        print("   [PASS] Video was correctly auto-marked as posted")
    else:
        print("   [FAIL] Video was NOT auto-marked as posted")

    # Test 3: Check database state
    print("\n3. Checking database state:")
    try:
        import json
        with open("memory/orchestrator_posted_streams.json", "r", encoding="utf-8") as f:
            posted_streams = json.load(f)

        if video_id in posted_streams:
            platforms_posted = posted_streams[video_id].get("platforms_posted", [])
            print(f"   Video {video_id} platforms: {platforms_posted}")
            if platform in platforms_posted:
                print("   [PASS] Platform correctly added to posted streams")
                return True
            else:
                print("   [FAIL] Platform NOT found in posted streams")
                return False
        else:
            print("   [FAIL] Video NOT found in posted streams database")
            return False

    except Exception as e:
        print(f"   [ERROR] Could not read database: {e}")
        return False

def test_intervention_logging():
    """Test that interventions are properly logged"""
    print("\n\nTESTING INTERVENTION LOGGING")
    print("=" * 60)

    monitor = PostSafetyMonitor()

    # Test intervention logging
    print("\n1. Testing intervention logging:")
    video_id = "test_video_456"
    platform = "x_twitter"

    # Simulate a cancellation and auto-correction
    detected = monitor.detect_user_cancellation(video_id, platform, "Browser window closed by user")
    if detected:
        marked = monitor.auto_mark_as_posted(video_id, platform, "Another Test Stream")

    # Check intervention log
    try:
        import json
        with open("memory/post_safety_interventions.json", "r", encoding="utf-8") as f:
            interventions = json.load(f)

        print(f"   Total interventions logged: {len(interventions)}")

        # Find our intervention
        our_intervention = None
        for intervention in interventions:
            if intervention.get("video_id") == video_id:
                our_intervention = intervention
                break

        if our_intervention:
            print("   [PASS] Intervention was correctly logged")
            print(f"   - Video ID: {our_intervention['video_id']}")
            print(f"   - Platform: {our_intervention['platform']}")
            print(f"   - Action: {our_intervention['action']}")
            return True
        else:
            print("   [FAIL] Intervention was NOT logged")
            return False

    except Exception as e:
        print(f"   [ERROR] Could not read intervention log: {e}")
        return False

if __name__ == "__main__":
    print("POST SAFETY MONITOR TEST")
    print("Testing cancellation detection and auto-correction")
    print("=" * 80)

    # Run tests
    test1_passed = test_cancellation_detection()
    test2_passed = test_intervention_logging()

    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"Cancellation Detection: {'PASS' if test1_passed else 'FAIL'}")
    print(f"Intervention Logging:   {'PASS' if test2_passed else 'FAIL'}")

    if test1_passed and test2_passed:
        print("\n[SUCCESS] All tests passed!")
        print("[OK] PostSafetyMonitor is working correctly")
        print("[OK] User cancellations will be detected and auto-corrected")
    else:
        print("\n[FAILURE] Some tests failed")
        print("[WARNING] PostSafetyMonitor may have issues")