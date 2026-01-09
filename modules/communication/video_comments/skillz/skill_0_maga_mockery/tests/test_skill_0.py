"""
Test Suite for Skill 0: MAGA Mockery
Phase 3O-3R Sprint 2 - Verify skill extraction and execution

WSP References:
- WSP 5 (Test Coverage)
- WSP 6 (Test Audit)
"""

import sys
import io
from pathlib import Path

# Fix Windows console encoding for emojis (WSP 90: UTF-8 enforcement)
if sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        pass

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Direct import from executor module
from modules.communication.video_comments.skillz.skill_0_maga_mockery.executor import (
    MagaMockerySkill,
    SkillContext
)


def test_grok_greeting_strategy():
    """Test 1: GrokGreetingGenerator response takes priority"""
    print("\n=== TEST 1: GrokGreetingGenerator Strategy ===")

    skill = MagaMockerySkill()

    # Context with maga_response (from GrokGreetingGenerator)
    context = SkillContext(
        user_id="test_troll_001",
        username="TestMAGATroll",
        comment_text="Make America Great Again!",
        classification="MAGA_TROLL",
        confidence=0.95,
        whack_count=3,
        maga_response="MAGA stuck at fist? Evolve: fist-hand-open_hand!",  # GrokGreetingGenerator
        troll_score=0.95
    )

    result = skill.execute(context)

    print(f"[TEST] Strategy: {result['strategy']}")
    print(f"[TEST] Reply: {result['reply_text']}")
    print(f"[TEST] Confidence: {result['confidence']}")

    if result['strategy'] == 'grok_greeting' and result['reply_text'] == context.maga_response:
        print("[OK] GrokGreetingGenerator strategy works!")
        return True
    else:
        print("[FAIL] Expected grok_greeting strategy")
        return False


def test_whack_a_maga_fallback():
    """Test 2: Whack-a-MAGA fallback when no GrokGreetingGenerator response"""
    print("\n=== TEST 2: Whack-a-MAGA Fallback ===")

    skill = MagaMockerySkill()

    # Context WITHOUT maga_response
    context = SkillContext(
        user_id="test_troll_002",
        username="AnotherTroll",
        comment_text="Trump 2024!",
        classification="MAGA_TROLL",
        confidence=0.80,
        whack_count=2,
        maga_response=None,  # No GrokGreetingGenerator response
        troll_score=0.80
    )

    result = skill.execute(context)

    print(f"[TEST] Strategy: {result['strategy']}")
    print(f"[TEST] Reply: {result['reply_text']}")
    print(f"[TEST] Confidence: {result['confidence']}")

    # Verify fallback used one of the TROLL_RESPONSES
    if (result['strategy'] == 'whack_a_maga_fallback' and
        result['reply_text'] in skill.TROLL_RESPONSES):
        print("[OK] Whack-a-MAGA fallback works!")
        return True
    else:
        print("[FAIL] Expected whack_a_maga_fallback strategy")
        return False


def test_response_variation():
    """Test 3: Verify responses vary (not always same fallback)"""
    print("\n=== TEST 3: Response Variation ===")

    skill = MagaMockerySkill()

    context = SkillContext(
        user_id="test_troll_003",
        username="VariationTroll",
        comment_text="MAGA!",
        classification="MAGA_TROLL",
        confidence=0.70,
        whack_count=1,
        maga_response=None,
        troll_score=0.70
    )

    # Execute 10 times, collect unique responses
    responses = set()
    for i in range(10):
        result = skill.execute(context)
        responses.add(result['reply_text'])

    print(f"[TEST] Unique responses: {len(responses)} out of 10 executions")

    if len(responses) > 1:
        print("[OK] Responses vary (randomized selection working)")
        return True
    else:
        print("[FAIL] All responses identical (random selection broken?)")
        return False


def test_context_validation():
    """Test 4: Verify skill handles all context fields"""
    print("\n=== TEST 4: Context Validation ===")

    skill = MagaMockerySkill()

    # Minimal context (only required fields)
    context = SkillContext(
        user_id="test_troll_004",
        username="MinimalTroll",
        comment_text="Test",
        classification="MAGA_TROLL",
        confidence=0.75,
        whack_count=1
        # Optional fields: maga_response=None, troll_score=None, etc.
    )

    try:
        result = skill.execute(context)
        print(f"[TEST] Strategy: {result['strategy']}")
        print(f"[TEST] Reply: {result['reply_text'][:50]}...")
        print("[OK] Skill handles minimal context!")
        return True
    except Exception as e:
        print(f"[FAIL] Skill crashed with minimal context: {e}")
        return False


def test_high_confidence_troll():
    """Test 5: Verify behavior with high-confidence troll (3+ whacks)"""
    print("\n=== TEST 5: High-Confidence Troll (3+ whacks) ===")

    skill = MagaMockerySkill()

    context = SkillContext(
        user_id="test_troll_005",
        username="ConfirmedTroll",
        comment_text="MAGA 2024!",
        classification="MAGA_TROLL",
        confidence=0.95,  # 3+ whacks = 0.95 confidence
        whack_count=5,
        maga_response=None,
        troll_score=0.95
    )

    result = skill.execute(context)

    print(f"[TEST] Whack count: {context.whack_count}")
    print(f"[TEST] Confidence: {context.confidence}")
    print(f"[TEST] Reply: {result['reply_text']}")

    if result['reply_text'] and result['confidence'] > 0:
        print("[OK] High-confidence troll handled correctly!")
        return True
    else:
        print("[FAIL] Response generation failed")
        return False


def run_all_tests():
    """Run all Skill 0 tests"""
    print("=" * 60)
    print("SKILL 0: MAGA MOCKERY TESTS - Sprint 2")
    print("=" * 60)

    tests = [
        ("GrokGreetingGenerator Strategy", test_grok_greeting_strategy),
        ("Whack-a-MAGA Fallback", test_whack_a_maga_fallback),
        ("Response Variation", test_response_variation),
        ("Context Validation", test_context_validation),
        ("High-Confidence Troll", test_high_confidence_troll),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"[ERROR] {test_name} crashed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print("\n ALL TESTS PASSED - Skill 0 ready for integration!")
        return True
    else:
        print(f"\n {failed} TEST(S) FAILED - Review failures above")
        return False


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
