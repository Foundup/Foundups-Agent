"""
Test YouTube Studio Account Switcher - Phase 4H Hybrid Validation
===================================================================

Tests the hybrid DOM + UI-TARS training pattern for account switching.

Test Scenarios:
1. Switch M2J → UnDaoDu (verify channel_id change + training recorded)
2. Switch UnDaoDu → M2J (verify channel_id change + training recorded)
3. Verify training data export to JSONL
4. Check UI-TARS format conversion (1000x1000 coordinates)

Usage:
    # Manual test (requires Chrome debugging on port 9222)
    python -m pytest modules/infrastructure/foundups_vision/tests/test_account_switcher.py -v -s

    # Or run directly
    python modules/infrastructure/foundups_vision/tests/test_account_switcher.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_switch_to_undaodu():
    """Test switching from M2J to UnDaoDu."""
    from modules.infrastructure.foundups_vision.src.studio_account_switcher import get_account_switcher

    logger.info("\n" + "=" * 80)
    logger.info("TEST 1: Switch M2J → UnDaoDu")
    logger.info("=" * 80)

    switcher = get_account_switcher()

    # Perform switch
    result = await switcher.switch_to_account("UnDaoDu")

    # Validate
    assert result.get("success") == True, f"Switch failed: {result}"
    assert result.get("account") == "UnDaoDu", f"Wrong account: {result}"
    assert result.get("steps_completed") == 3, f"Incomplete: {result}"
    assert result.get("training_recorded") == 3, f"Training missing: {result}"

    logger.info("✅ Test 1 PASSED: Successfully switched to UnDaoDu")
    logger.info(f"   Steps completed: {result['steps_completed']}")
    logger.info(f"   Training examples: {result['training_recorded']}")

    return result


async def test_switch_to_m2j():
    """Test switching from UnDaoDu to M2J."""
    from modules.infrastructure.foundups_vision.src.studio_account_switcher import get_account_switcher

    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Switch UnDaoDu → M2J")
    logger.info("=" * 80)

    switcher = get_account_switcher()

    # Perform switch
    result = await switcher.switch_to_account("Move2Japan")

    # Validate
    assert result.get("success") == True, f"Switch failed: {result}"
    assert result.get("account") == "Move2Japan", f"Wrong account: {result}"
    assert result.get("steps_completed") == 3, f"Incomplete: {result}"
    assert result.get("training_recorded") == 3, f"Training missing: {result}"

    logger.info("✅ Test 2 PASSED: Successfully switched to Move2Japan")
    logger.info(f"   Steps completed: {result['steps_completed']}")
    logger.info(f"   Training examples: {result['training_recorded']}")

    return result


async def test_training_stats():
    """Test training data collection statistics."""
    from modules.infrastructure.foundups_vision.src.studio_account_switcher import get_account_switcher

    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Verify Training Data Collection")
    logger.info("=" * 80)

    switcher = get_account_switcher()
    stats = switcher.get_training_stats()

    logger.info(f"Training stats: {stats}")

    # Validate
    assert stats.get("enabled") == True, "Training disabled!"
    assert stats.get("total_examples", 0) >= 6, f"Expected >= 6 examples, got {stats.get('total_examples')}"

    logger.info("✅ Test 3 PASSED: Training data collection verified")
    logger.info(f"   Total examples: {stats['total_examples']}")
    logger.info(f"   Session examples: {stats.get('session_examples', 0)}")

    return stats


async def test_training_export():
    """Test JSONL export for UI-TARS fine-tuning."""
    from modules.infrastructure.foundups_vision.src.studio_account_switcher import get_account_switcher

    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: Export Training Data to JSONL")
    logger.info("=" * 80)

    switcher = get_account_switcher()

    # Export training data
    output_path = switcher.export_training_data()

    # Validate
    assert output_path is not None, "Export failed!"
    assert Path(output_path).exists(), f"JSONL file not found: {output_path}"

    # Read and validate format
    import json
    with open(output_path, 'r') as f:
        lines = f.readlines()

    assert len(lines) > 0, "JSONL file empty!"

    # Validate first example
    example = json.loads(lines[0])
    assert "image" in example, "Missing screenshot!"
    assert "conversations" in example, "Missing conversations!"
    assert len(example["conversations"]) == 2, "Wrong conversation format!"

    # Validate UI-TARS format
    user_msg = example["conversations"][0]
    assistant_msg = example["conversations"][1]

    assert user_msg["role"] == "user", "Wrong role!"
    assert "Click the" in user_msg["content"], "Wrong user content!"
    assert assistant_msg["role"] == "assistant", "Wrong role!"
    assert "<|box_start|>" in assistant_msg["content"], "Missing box coordinates!"

    logger.info("✅ Test 4 PASSED: JSONL export validated")
    logger.info(f"   Output: {output_path}")
    logger.info(f"   Examples exported: {len(lines)}")
    logger.info(f"   Sample: {example['conversations'][0]['content'][:60]}...")

    return output_path


async def run_all_tests():
    """Run all account switcher tests."""
    logger.info("\n" + "=" * 80)
    logger.info("YouTube Studio Account Switcher Test Suite")
    logger.info("Phase 4H: HYBRID (DOM + UI-TARS Training)")
    logger.info("=" * 80)

    try:
        # Test 1: Switch to UnDaoDu
        result1 = await test_switch_to_undaodu()

        # Wait 3s between switches (human-like)
        logger.info("\n⏳ Waiting 3s before next switch...")
        await asyncio.sleep(3)

        # Test 2: Switch to M2J
        result2 = await test_switch_to_m2j()

        # Test 3: Training stats
        stats = await test_training_stats()

        # Test 4: Export training data
        export_path = await test_training_export()

        logger.info("\n" + "=" * 80)
        logger.info("✅ ALL TESTS PASSED!")
        logger.info("=" * 80)
        logger.info(f"Total account switches: 2")
        logger.info(f"Training examples recorded: {stats.get('session_examples', 0)}")
        logger.info(f"JSONL export: {export_path}")
        logger.info("\nNext steps:")
        logger.info("1. Review training data in JSONL file")
        logger.info("2. Fine-tune UI-TARS model with collected data")
        logger.info("3. Test vision-based account switching (Phase 5)")

        return True

    except AssertionError as e:
        logger.error(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run tests
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
