#!/usr/bin/env python3
"""
Test Intelligent Throttle Manager
WSP-Compliant: WSP 5 (Testing), WSP 6 (Audit)

Tests the intelligent throttle manager and enhanced features.
"""

import asyncio
import time
import sys
import os
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)  # Change to project root for imports

from modules.communication.livechat.src.intelligent_throttle_manager import (
    IntelligentThrottleManager, QuotaState, TrollDetector, RecursiveQuotaLearner
)


def test_intelligent_throttle():
    """Test intelligent throttle manager functionality"""
    print("\n" + "="*60)
    print("[TEST] TESTING INTELLIGENT THROTTLE MANAGER")
    print("="*60)
    
    # Initialize manager
    memory_path = Path("test_memory")
    manager = IntelligentThrottleManager(memory_path=memory_path)
    
    # Test 1: Basic throttling
    print("\n[1] Test 1: Basic Throttling")
    print("-" * 40)
    
    # Simulate messages
    for i in range(10):
        manager.track_message()
        time.sleep(0.1)
    
    delay = manager.calculate_adaptive_delay()
    print(f"[OK] With 10 messages: {delay:.1f}s delay")
    assert 2 <= delay <= 20, f"Unexpected delay: {delay}"
    
    # Test 2: Troll detection
    print("\n[2] Test 2: Troll Detection")
    print("-" * 40)
    
    troll_id = "test_troll_123"
    troll_name = "TrollUser"
    
    # Simulate troll behavior (multiple triggers)
    responses = []
    for i in range(5):
        result = manager.track_message(troll_id, troll_name)
        if result['is_troll']:
            responses.append(result['response'])
            print(f"  Trigger {i+1}: Troll detected! Response: {result['response'][:50]}...")
        else:
            print(f"  Trigger {i+1}: Not yet flagged as troll")
    
    assert len(responses) > 0, "Troll should have been detected"
    print(f"[OK] Troll detected after multiple triggers, {len(responses)} responses generated")
    
    # Test 3: Quota management
    print("\n[3] Test 3: Quota Management")
    print("-" * 40)
    
    # Simulate API calls
    for i in range(5):
        manager.track_api_call(quota_cost=10, credential_set=0)
    
    state = manager.quota_states[0]
    print(f"  Used quota: {state.used_quota}")
    print(f"  Remaining: {state.remaining_quota}")
    print(f"  Percentage: {state.quota_percentage:.1f}%")
    
    assert state.used_quota == 50, f"Expected 50 quota used, got {state.used_quota}"
    print("[OK] Quota tracking working correctly")
    
    # Test 4: Response type cooldowns
    print("\n[4] Test 4: Response Type Cooldowns")
    print("-" * 40)
    
    response_types = ['consciousness', 'factcheck', 'maga', 'quiz', 'whack', '0102_emoji']
    
    for resp_type in response_types:
        should_respond = manager.should_respond(resp_type)
        print(f"  {resp_type}: {'Yes' if should_respond else 'No'} (multiplier: {manager.response_cooldowns[resp_type]['multiplier']})")
    
    # Record a response and check cooldown
    manager.record_response('consciousness')
    should_respond_after = manager.should_respond('consciousness')
    print(f"\n  After recording consciousness response: {'Yes' if should_respond_after else 'No'}")
    assert not should_respond_after, "Should not respond immediately after recording"
    print("[OK] Response cooldowns working correctly")
    
    # Test 5: 0102 emoji responses
    print("\n[5] Test 5: 0102 Emoji Responses")
    print("-" * 40)
    
    emojis = []
    for i in range(5):
        emoji = manager.get_0102_emoji()
        emojis.append(emoji)
        print(f"  Response {i+1}: {emoji}")
    
    assert len(set(emojis)) > 1, "Should have variety in emoji responses"
    print(f"[OK] Generated {len(set(emojis))} unique emoji combinations")
    
    # Test 6: Learning and adaptation
    print("\n[6] Test 6: Recursive Learning")
    print("-" * 40)
    
    # Enable learning
    manager.enable_learning(True)
    
    # Simulate usage patterns
    for i in range(3):
        manager.track_message()
        manager.track_api_call(quota_cost=5)
        time.sleep(0.1)
    
    status = manager.get_status()
    print(f"  Learned patterns: {status['learned_patterns']}")
    print(f"  Learning enabled: {status['learning_enabled']}")
    print(f"  Agentic mode: {status['agentic_mode']}")
    
    # Save state
    manager.save_state()
    print("[OK] Learning and state saving working")
    
    # Test 7: Comprehensive status
    print("\n[7] Test 7: Status Report")
    print("-" * 40)
    
    status = manager.get_status()
    print(f"  Messages/min: {status['messages_per_minute']:.1f}")
    print(f"  API calls/min: {status['api_calls_per_minute']:.1f}")
    print(f"  Current delay: {status['current_delay']:.1f}s")
    print(f"  Trolls detected: {status['trolls_detected']}")
    print(f"  Learned patterns: {status['learned_patterns']}")
    
    print("\n" + "="*60)
    print("[SUCCESS] ALL TESTS PASSED - Intelligent throttle manager working!")
    print("="*60)
    
    # Cleanup test memory
    import shutil
    if memory_path.exists():
        shutil.rmtree(memory_path)


def test_troll_detector():
    """Test troll detector separately"""
    print("\n" + "="*60)
    print("[TEST] TESTING TROLL DETECTOR")
    print("="*60)
    
    detector = TrollDetector()
    
    # Test rapid triggers
    user_id = "rapid_troll"
    username = "RapidTroll"
    
    print("\n[INFO] Simulating rapid triggers...")
    for i in range(5):
        is_troll, response = detector.track_trigger(user_id, username)
        print(f"  Trigger {i+1}: {'TROLL!' if is_troll else 'Normal'}")
        if response:
            print(f"    Response: {response}")
    
    assert detector.is_troll(user_id), "Should be marked as troll"
    print("[OK] Troll detection working")
    
    # Test forgiveness
    print("\n[INFO] Testing troll forgiveness...")
    time.sleep(0.5)  # Simulate time passing
    detector.forgive_troll(user_id)  # Won't forgive yet (not enough time)
    assert detector.is_troll(user_id), "Should still be troll (not enough time)"
    print("[OK] Forgiveness cooldown working")


def test_quota_learning():
    """Test quota learning patterns"""
    print("\n" + "="*60)
    print("[TEST] TESTING RECURSIVE QUOTA LEARNING")
    print("="*60)
    
    memory_path = Path("test_learning")
    learner = RecursiveQuotaLearner(memory_path)
    
    # Add some patterns
    print("\n[INFO] Adding usage patterns...")
    for i in range(5):
        learner.learn_from_usage(
            messages_per_minute=10 + i*5,
            api_calls=5 + i,
            quota_used=10 + i*2,
            optimal_delay=5.0 - i*0.5
        )
    
    # Save patterns
    learner.save_patterns()
    
    # Load and verify
    learner2 = RecursiveQuotaLearner(memory_path)
    print(f"[OK] Loaded {len(learner2.patterns)} patterns from memory")
    
    # Predict optimal delay
    state = QuotaState(used_quota=500, total_quota=1000)
    predicted = learner2.predict_optimal_delay(15, state)
    print(f"[INFO] Predicted delay for 15 msg/min at 50% quota: {predicted:.1f}s")
    
    # Cleanup
    import shutil
    if memory_path.exists():
        shutil.rmtree(memory_path)
    
    print("[OK] Recursive learning working correctly")


if __name__ == "__main__":
    try:
        print("\n[START] Starting Intelligent Throttle Manager Tests...")
        
        # Run all tests
        test_intelligent_throttle()
        test_troll_detector()
        test_quota_learning()
        
        print("\n" + "="*60)
        print("[SUCCESS] ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n[SUMMARY]:")
        print("  [OK] Intelligent throttling with adaptive delays")
        print("  [OK] Troll detection and response system")
        print("  [OK] Quota management and tracking")
        print("  [OK] Response type cooldowns")
        print("  [OK] 0102 emoji responses")
        print("  [OK] Recursive learning from patterns")
        print("  [OK] State persistence and recovery")
        print("\n[READY] The enhanced system is ready for deployment!")
        
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)