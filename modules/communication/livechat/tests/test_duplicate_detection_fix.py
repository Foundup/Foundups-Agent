#!/usr/bin/env python3
"""
Test the duplicate detection fix to ensure 2nd duplicate is caught
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

import time
from modules.infrastructure.system_health_monitor.src.system_health_analyzer import SystemHealthAnalyzer

def test_duplicate_detection_with_threshold_2():
    """Test that duplicate detection triggers on 2nd occurrence"""
    print("TESTING DUPLICATE DETECTION WITH THRESHOLD = 2")
    print("=" * 60)

    analyzer = SystemHealthAnalyzer()

    # First message - should be fine
    test_message = "[U+2615] 012 detector online! Drop [U+270A][U+270B][U+1F590] if you're ready to escape the simulation. MAGA still sleeping Speaking of unconscious patterns... (Morning consciousness check!)"

    print("\n1. Sending first message (should be OK):")
    issues1 = analyzer.analyze_message(test_message)
    print(f"   Issues detected: {len(issues1)}")
    for issue in issues1:
        print(f"   - {issue.issue_type}: {issue.description}")

    # Small delay
    time.sleep(0.1)

    # Second message (duplicate) - should be blocked
    print("\n2. Sending second identical message (should be BLOCKED):")
    issues2 = analyzer.analyze_message(test_message)
    print(f"   Issues detected: {len(issues2)}")
    for issue in issues2:
        print(f"   - {issue.issue_type}: {issue.description}")

    # Verify the fix worked
    if len(issues2) > 0 and any(issue.issue_type == 'duplicate' for issue in issues2):
        print("\n[OK] SUCCESS: Duplicate detection is working!")
        print("   The second identical message was correctly identified as duplicate")
        return True
    else:
        print("\n[FAIL] FAILED: Duplicate detection not working")
        print("   The second identical message was NOT detected as duplicate")
        return False

def test_duplicate_detection_different_messages():
    """Test that different messages don't trigger duplicate detection"""
    print("\n\nTESTING DIFFERENT MESSAGES (SHOULD NOT TRIGGER)")
    print("=" * 60)

    analyzer = SystemHealthAnalyzer()

    message1 = "Hello world test message 1"
    message2 = "Hello world test message 2"

    print("\n1. Sending first message:")
    issues1 = analyzer.analyze_message(message1)
    print(f"   Issues detected: {len(issues1)}")

    print("\n2. Sending different message:")
    issues2 = analyzer.analyze_message(message2)
    print(f"   Issues detected: {len(issues2)}")

    if len(issues2) == 0:
        print("\n[OK] SUCCESS: Different messages don't trigger duplicate detection")
        return True
    else:
        print("\n[FAIL] FAILED: Different messages incorrectly flagged as duplicates")
        return False

if __name__ == "__main__":
    print("DUPLICATE DETECTION FIX TEST")
    print("Testing the fix for 0102 duplicate chat posting issue")
    print("=" * 80)

    # Test duplicate detection
    test1_passed = test_duplicate_detection_with_threshold_2()
    test2_passed = test_duplicate_detection_different_messages()

    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"Duplicate Detection Test: {'PASS' if test1_passed else 'FAIL'}")
    print(f"Different Messages Test:  {'PASS' if test2_passed else 'FAIL'}")

    if test1_passed and test2_passed:
        print("\n[CELEBRATE] ALL TESTS PASSED!")
        print("[OK] Duplicate detection fix is working correctly")
        print("[OK] 0102 will no longer post duplicate messages in chat")
    else:
        print("\n[FAIL] SOME TESTS FAILED")
        print("[U+26A0]️  Duplicate detection may still have issues")