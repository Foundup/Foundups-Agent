"""
Test Suite for Skill 2: Moderator Appreciation
Phase 3O-3R Sprint 3 (Enhanced) - Verify skill extraction and database integration

WSP References:
- WSP 5 (Test Coverage)
- WSP 6 (Test Audit)
- WSP 60 (Module Memory): Mod stats database integration
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
project_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Direct import from executor module
from modules.communication.video_comments.skillz.skill_2_moderator_appreciation.executor import (
    ModeratorAppreciationSkill,
    SkillContext
)


def test_template_appreciation():
    """Test 1: Template appreciation when stats unavailable"""
    print("\n=== TEST 1: Template Appreciation (No Stats) ===")

    skill = ModeratorAppreciationSkill()

    # Context WITHOUT mod stats (database empty)
    context = SkillContext(
        user_id="mod_nostats_001",
        username="TestMod",
        comment_text="Great stream!",
        classification="MODERATOR",
        confidence=1.0
    )

    result = skill.execute(context)

    print(f"[TEST] Strategy: {result['strategy']}")
    print(f"[TEST] Reply: {result['reply_text']}")
    print(f"[TEST] Confidence: {result['confidence']}")

    # Verify template strategy used
    if (result['strategy'] == 'template' and
        result['reply_text'] in skill.MOD_RESPONSES):
        print("[OK] Template appreciation works!")
        return True
    else:
        print("[FAIL] Expected template strategy")
        return False


def test_personalized_appreciation_mock():
    """Test 2: Personalized appreciation with mocked stats"""
    print("\n=== TEST 2: Personalized Appreciation (Mocked Stats) ===")

    skill = ModeratorAppreciationSkill()

    # Mock: Manually inject stats (simulates database query result)
    class MockContext(SkillContext):
        pass

    context = MockContext(
        user_id="mod_withstats_001",
        username="LegendMod",
        comment_text="Awesome content!",
        classification="MODERATOR",
        confidence=1.0
    )

    # Manually set what _get_mod_stats would return
    original_get_stats = skill._get_mod_stats
    skill._get_mod_stats = lambda ctx: {
        'whacks_count': 25,
        'level': 'LEGEND',
        'total_points': 5000,
        'combo_multiplier': 2.5
    }

    try:
        result = skill.execute(context)

        print(f"[TEST] Strategy: {result['strategy']}")
        print(f"[TEST] Reply: {result['reply_text']}")
        print(f"[TEST] Confidence: {result['confidence']}")

        # Verify personalized strategy with stats
        if (result['strategy'] == 'personalized_stats' and
            '25' in result['reply_text'] and
            'LEGEND' in result['reply_text']):
            print("[OK] Personalized appreciation works!")
            return True
        else:
            print(f"[FAIL] Expected personalized_stats strategy with '25' and 'LEGEND'")
            return False
    finally:
        # Restore original method
        skill._get_mod_stats = original_get_stats


def test_response_variation():
    """Test 3: Verify personalized responses vary (not always same template)"""
    print("\n=== TEST 3: Personalized Response Variation ===")

    skill = ModeratorAppreciationSkill()

    # Mock stats
    skill._get_mod_stats = lambda ctx: {
        'whacks_count': 15,
        'level': 'MVP',
        'total_points': 3000,
        'combo_multiplier': 1.8
    }

    context = SkillContext(
        user_id="mod_variation_001",
        username="MVPMod",
        comment_text="Test",
        classification="MODERATOR",
        confidence=1.0
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
    """Test 4: Verify skill handles minimal context"""
    print("\n=== TEST 4: Context Validation ===")

    skill = ModeratorAppreciationSkill()

    # Minimal context (only required fields)
    context = SkillContext(
        user_id="mod_minimal_001",
        username="MinimalMod",
        comment_text="Hi",
        classification="MODERATOR",
        confidence=1.0
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


def test_high_whack_count():
    """Test 5: Verify personalization with high whack count"""
    print("\n=== TEST 5: High Whack Count Moderator ===")

    skill = ModeratorAppreciationSkill()

    # Mock high-performing moderator
    skill._get_mod_stats = lambda ctx: {
        'whacks_count': 100,
        'level': 'ELITE',
        'total_points': 20000,
        'combo_multiplier': 5.0
    }

    context = SkillContext(
        user_id="mod_elite_001",
        username="EliteMod",
        comment_text="Keeping it clean!",
        classification="MODERATOR",
        confidence=1.0
    )

    result = skill.execute(context)

    print(f"[TEST] Strategy: {result['strategy']}")
    print(f"[TEST] Reply: {result['reply_text']}")

    # Verify whack count appears in response
    if '100' in result['reply_text'] and 'ELITE' in result['reply_text']:
        print("[OK] High whack count moderator handled correctly!")
        return True
    else:
        print("[FAIL] Stats not properly integrated into response")
        return False


def test_database_unavailable_fallback():
    """Test 6: Graceful fallback when database unavailable"""
    print("\n=== TEST 6: Database Unavailable Fallback ===")

    skill = ModeratorAppreciationSkill()

    # Force database error
    skill._chat_rules_db = None
    skill._get_mod_stats = lambda ctx: None  # Simulate database failure

    context = SkillContext(
        user_id="mod_dbfail_001",
        username="DBFailMod",
        comment_text="Test",
        classification="MODERATOR",
        confidence=1.0
    )

    result = skill.execute(context)

    print(f"[TEST] Strategy: {result['strategy']}")
    print(f"[TEST] Reply: {result['reply_text']}")

    # Should fallback to template
    if result['strategy'] == 'template':
        print("[OK] Graceful fallback to template appreciation!")
        return True
    else:
        print("[FAIL] Should fallback to template when database unavailable")
        return False


def run_all_tests():
    """Run all Skill 2 tests"""
    print("=" * 60)
    print("SKILL 2: MODERATOR APPRECIATION TESTS - Sprint 3 Enhanced")
    print("=" * 60)

    tests = [
        ("Template Appreciation (No Stats)", test_template_appreciation),
        ("Personalized Appreciation (Mocked Stats)", test_personalized_appreciation_mock),
        ("Personalized Response Variation", test_response_variation),
        ("Context Validation", test_context_validation),
        ("High Whack Count Moderator", test_high_whack_count),
        ("Database Unavailable Fallback", test_database_unavailable_fallback),
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
        print("\n ALL TESTS PASSED - Skill 2 ready for integration!")
        return True
    else:
        print(f"\n {failed} TEST(S) FAILED - Review failures above")
        return False


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
