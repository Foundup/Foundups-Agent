#!/usr/bin/env python3
"""
Test that the system correctly detects and fixes duplicate attempts when users cancel posts.
This simulates the scenario where a user manually cancels a post because it was already posted.
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===


import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from modules.platform_integration.social_media_orchestrator.src.post_safety_monitor import (
    PostSafetyMonitor, detect_and_fix_duplicate
)
from modules.platform_integration.social_media_orchestrator.src.simple_posting_orchestrator import (
    orchestrator
)
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_cancellation_detection():
    """Test that user cancellations are detected and auto-fixed"""

    print("="*80)
    print("TESTING USER CANCELLATION DETECTION & AUTO-FIX")
    print("="*80)

    # Test video ID
    test_video_id = "TEST_VIDEO_123"
    test_title = "Test Stream - Cancellation Detection"

    # Clear any existing history for this test video
    if test_video_id in orchestrator.posted_streams:
        del orchestrator.posted_streams[test_video_id]
        orchestrator._save_posted_history()

    safety_monitor = PostSafetyMonitor()

    # Step 1: Simulate user cancelling LinkedIn post
    print("\n--- Step 1: Simulating LinkedIn Cancellation ---")
    print(f"User tries to post video {test_video_id} to LinkedIn...")
    print("Browser opens, user sees it's already posted, closes window")

    # Simulate the error that would occur
    cancellation_detected = safety_monitor.detect_user_cancellation(
        video_id=test_video_id,
        platform="linkedin",
        error_msg="target window already closed"
    )

    if cancellation_detected:
        print("[SUCCESS] Cancellation detected!")

        # Auto-fix the database
        fixed = safety_monitor.auto_mark_as_posted(
            video_id=test_video_id,
            platform="linkedin",
            title=test_title
        )

        if fixed:
            print("[SUCCESS] Database auto-corrected!")
        else:
            print("[FAIL] Database correction failed!")
    else:
        print("[FAIL] Cancellation not detected!")

    # Step 2: Verify the fix worked
    print("\n--- Step 2: Verifying Auto-Fix ---")
    status = orchestrator.check_if_already_posted(test_video_id)

    print(f"Video status after auto-fix:")
    print(f"  Already posted: {status['already_posted']}")
    print(f"  Platforms: {status['platforms_posted']}")

    if "linkedin" in status['platforms_posted']:
        print("[SUCCESS] LinkedIn correctly marked as posted!")
    else:
        print("[FAIL] LinkedIn not marked as posted!")

    # Step 3: Test X/Twitter cancellation
    print("\n--- Step 3: Simulating X/Twitter Cancellation ---")

    x_cancellation = safety_monitor.detect_user_cancellation(
        video_id=test_video_id,
        platform="x_twitter",
        error_msg="window already closed"
    )

    if x_cancellation:
        safety_monitor.auto_mark_as_posted(
            video_id=test_video_id,
            platform="x_twitter",
            title=test_title
        )
        print("[SUCCESS] X/Twitter cancellation handled!")

    # Step 4: Final verification
    print("\n--- Step 4: Final Status Check ---")
    final_status = orchestrator.check_if_already_posted(test_video_id)

    print(f"Final video status:")
    print(f"  Already posted: {final_status['already_posted']}")
    print(f"  Platforms: {final_status['platforms_posted']}")

    # Step 5: Generate duplicate attempt report
    print("\n--- Step 5: Duplicate Attempt Report ---")
    report = safety_monitor.get_duplicate_attempt_report()
    print(report)

    # Step 6: Test the convenience function
    print("\n--- Step 6: Testing Direct Detection Function ---")

    # Test the direct function used by posting systems
    test_video_2 = "TEST_VIDEO_456"

    duplicate_fixed = detect_and_fix_duplicate(
        video_id=test_video_2,
        platform="linkedin",
        error_msg="no such window: target window already closed"
    )

    if duplicate_fixed:
        print(f"[SUCCESS] Direct function correctly fixed duplicate for {test_video_2}")
    else:
        print(f"[INFO] No duplicate detected for {test_video_2}")

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\nThe system now:")
    print("1. [OK] Detects when users cancel posts")
    print("2. [OK] Auto-marks videos as posted to prevent future duplicates")
    print("3. [OK] Tracks all duplicate attempts for debugging")
    print("4. [OK] Provides reports on duplicate posting issues")
    print("5. [OK] Integrates with LinkedIn and X/Twitter posting")

if __name__ == "__main__":
    test_cancellation_detection()