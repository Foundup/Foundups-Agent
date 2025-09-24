#!/usr/bin/env python3
"""Test the Pattern Coach intelligent coaching system"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from holo_index.qwen_advisor.pattern_coach import PatternCoach

def test_search_frustration():
    """Test that multiple failed searches trigger coaching"""
    coach = PatternCoach()
    print("Testing search frustration pattern...")

    # Simulate 3 failed searches
    messages = []
    for i in range(4):
        result = coach.observe_action('search', {'results': 0})
        if result:
            messages.append(f"Attempt {i+1}: Got coaching!")
            print(f"Attempt {i+1}: Coaching triggered!")
            # Remove emojis for safe printing
            safe_msg = result.encode('ascii', 'ignore').decode('ascii')
            print(f"Message preview: {safe_msg[:100]}...")
        else:
            messages.append(f"Attempt {i+1}: No coaching yet")
            print(f"Attempt {i+1}: No coaching yet")

    return any("Got coaching" in msg for msg in messages)

def test_creation_without_search():
    """Test that file creation without search triggers coaching"""
    coach = PatternCoach()
    print("\nTesting file creation without search...")

    # Simulate intent to create file without searching
    coach.observe_action("file_creation_intent", {"filename": "new_auth.py"})
    result = coach.observe_action("no_recent_search")

    if result:
        print("Coaching triggered for no-search pattern!")
        safe_msg = result.encode('ascii', 'ignore').decode('ascii')
        print(f"Message preview: {safe_msg[:100]}...")
        return True
    else:
        print("No coaching triggered")
        return False

def test_good_compliance():
    """Test that good WSP compliance gets positive reinforcement"""
    coach = PatternCoach()
    print("\nTesting good WSP compliance pattern...")

    # Simulate good behavior
    coach.observe_action("holoindex_search", {"query": "authentication"})
    coach.observe_action("navigation_check")
    result = coach.observe_action("enhance_existing", {"file": "auth.py"})

    if result:
        print("Positive reinforcement triggered!")
        safe_msg = result.encode('ascii', 'ignore').decode('ascii')
        print(f"Message preview: {safe_msg[:100]}...")
        return True
    else:
        print("No positive reinforcement")
        return False

def test_situational_advice():
    """Test situational advice based on query"""
    coach = PatternCoach()
    print("\nTesting situational advice...")

    queries = [
        "create new module for logging",
        "fix bug in authentication",
        "test the chat system"
    ]

    advice_given = False
    for query in queries:
        advice = coach.get_situational_advice(query)
        if advice:
            print(f"Query: '{query}' -> Got advice!")
            safe_msg = advice.encode('ascii', 'ignore').decode('ascii')
            print(f"Advice preview: {safe_msg[:80]}...")
            advice_given = True

    return advice_given

if __name__ == "__main__":
    print("=" * 60)
    print("Pattern Coach Integration Tests")
    print("=" * 60)

    tests_passed = 0
    total_tests = 4

    if test_search_frustration():
        tests_passed += 1
        print("[PASS] Search frustration test passed")
    else:
        print("[FAIL] Search frustration test failed")

    if test_creation_without_search():
        tests_passed += 1
        print("[PASS] No-search creation test passed")
    else:
        print("[FAIL] No-search creation test failed")

    if test_good_compliance():
        tests_passed += 1
        print("[PASS] Good compliance test passed")
    else:
        print("[FAIL] Good compliance test failed")

    if test_situational_advice():
        tests_passed += 1
        print("[PASS] Situational advice test passed")
    else:
        print("[FAIL] Situational advice test failed")

    print("\n" + "=" * 60)
    print(f"Results: {tests_passed}/{total_tests} tests passed")
    print("=" * 60)

    # Show coaching summary
    coach = PatternCoach()
    print("\n" + coach.get_coaching_summary())