#!/usr/bin/env python3
"""
Sprint 1 Phase 1B: Automated Account Switching Test
Test YouTube account switching using 012's verified DOM coordinates
"""

import asyncio
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

async def navigate_to_studio():
    """Navigate to YouTube Studio if not already there."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    import os

    try:
        port = int(os.getenv("FOUNDUPS_LIVECHAT_CHROME_PORT", "9222"))
        opts = Options()
        opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
        driver = webdriver.Chrome(options=opts)

        current_url = driver.current_url
        logger.info(f"Current URL: {current_url}")

        if "studio.youtube.com" not in current_url:
            logger.info("Navigating to YouTube Studio...")
            driver.get("https://studio.youtube.com")
            import time
            time.sleep(3)  # Wait for Studio to load
            logger.info("✅ Navigated to YouTube Studio")
        else:
            logger.info("✅ Already on YouTube Studio")

        return True
    except Exception as e:
        logger.error(f"Failed to navigate to Studio: {e}")
        return False


async def test_switch_to_undaodu():
    """Test switching from Move2Japan to UnDaoDu."""
    logger.info("="*60)
    logger.info("TEST 1: Switch Move2Japan → UnDaoDu")
    logger.info("="*60)

    try:
        from modules.infrastructure.foundups_vision.src.studio_account_switcher import switch_studio_account

        logger.info("Starting switch to UnDaoDu...")
        result = await switch_studio_account("UnDaoDu")

        if result["success"]:
            logger.info("✅ SUCCESS: Switched to UnDaoDu")
            logger.info(f"   Channel ID: {result['channel_id']}")
            logger.info(f"   Steps completed: {result['steps_completed']}/3")
            logger.info(f"   Training examples: {result['training_recorded']}")
        else:
            logger.error(f"❌ FAILED: {result.get('error')}")
            logger.error(f"   Steps completed: {result.get('steps_completed', 0)}/3")

        return result

    except Exception as e:
        logger.error(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


async def test_switch_to_move2japan():
    """Test switching from UnDaoDu to Move2Japan."""
    logger.info("\n" + "="*60)
    logger.info("TEST 2: Switch UnDaoDu → Move2Japan")
    logger.info("="*60)

    try:
        from modules.infrastructure.foundups_vision.src.studio_account_switcher import switch_studio_account

        logger.info("Starting switch to Move2Japan...")
        result = await switch_studio_account("Move2Japan")

        if result["success"]:
            logger.info("✅ SUCCESS: Switched to Move2Japan")
            logger.info(f"   Channel ID: {result['channel_id']}")
            logger.info(f"   Steps completed: {result['steps_completed']}/3")
            logger.info(f"   Training examples: {result['training_recorded']}")
        else:
            logger.error(f"❌ FAILED: {result.get('error')}")
            logger.error(f"   Steps completed: {result.get('steps_completed', 0)}/3")

        return result

    except Exception as e:
        logger.error(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


async def check_training_data():
    """Check that training data was recorded."""
    logger.info("\n" + "="*60)
    logger.info("TRAINING DATA CHECK")
    logger.info("="*60)

    try:
        from modules.infrastructure.foundups_vision.src.studio_account_switcher import get_account_switcher

        switcher = get_account_switcher()
        stats = switcher.get_training_stats()

        logger.info(f"Training enabled: {stats.get('enabled', False)}")
        logger.info(f"Session examples: {stats.get('session_examples', 0)}")
        logger.info(f"Total examples: {stats.get('total_examples', 0)}")

        # Check for training data files
        training_dir = Path("modules/infrastructure/foundups_vision/training_data")
        if training_dir.exists():
            screenshots = list(training_dir.glob("*.png"))
            metadata_files = list(training_dir.glob("*.jsonl"))

            logger.info(f"Screenshots found: {len(screenshots)}")
            logger.info(f"Metadata files: {len(metadata_files)}")

            if screenshots:
                logger.info("Recent screenshots:")
                for img in screenshots[-3:]:  # Show last 3
                    logger.info(f"   - {img.name}")
        else:
            logger.warning("Training data directory not found")

        return stats

    except Exception as e:
        logger.error(f"Failed to check training data: {e}")
        return {}


async def main():
    """Run all switching tests."""
    logger.info("\n" + "="*70)
    logger.info("SPRINT 1 PHASE 1B: AUTOMATED ACCOUNT SWITCHING TEST")
    logger.info("="*70)
    logger.info("")
    logger.info("Prerequisites:")
    logger.info("  1. Chrome running on port 9222")
    logger.info("  2. YouTube Studio open")
    logger.info("  3. Currently logged into Move2Japan account")
    logger.info("")
    logger.info("Starting automated tests in 3 seconds...")
    await asyncio.sleep(3)

    # Navigate to YouTube Studio first
    logger.info("\n" + "="*60)
    logger.info("PREREQUISITE: Navigate to YouTube Studio")
    logger.info("="*60)
    nav_success = await navigate_to_studio()
    if not nav_success:
        logger.error("❌ FAILED: Could not navigate to YouTube Studio")
        return 1

    results = []

    # Test 1: Move2Japan → UnDaoDu
    result1 = await test_switch_to_undaodu()
    results.append(("Move2Japan → UnDaoDu", result1))

    if result1.get("success"):
        logger.info("\n⏳ Waiting 3 seconds before next test...")
        await asyncio.sleep(3)

        # Test 2: UnDaoDu → Move2Japan
        result2 = await test_switch_to_move2japan()
        results.append(("UnDaoDu → Move2Japan", result2))
    else:
        logger.error("Skipping reverse test due to first test failure")

    # Check training data
    await check_training_data()

    # Summary
    logger.info("\n" + "="*70)
    logger.info("TEST SUMMARY")
    logger.info("="*70)

    success_count = sum(1 for _, r in results if r.get("success"))
    total_count = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result.get("success") else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
        if not result.get("success"):
            logger.info(f"   Error: {result.get('error', 'Unknown')}")

    logger.info("")
    logger.info(f"Results: {success_count}/{total_count} tests passed")

    if success_count == total_count:
        logger.info("\n🎉 ALL TESTS PASSED - Sprint 1 Phase 1B COMPLETE!")
        logger.info("")
        logger.info("Next Steps:")
        logger.info("  1. Review training data screenshots")
        logger.info("  2. Proceed to Phase 1C (Comment Engagement Integration)")
        logger.info("  3. Update Sprint 1 summary with metrics")
        return 0
    else:
        logger.error(f"\n⚠️ {total_count - success_count} TEST(S) FAILED")
        logger.error("")
        logger.error("Troubleshooting:")
        logger.error("  1. Check Chrome is running on port 9222")
        logger.error("  2. Verify YouTube Studio is open")
        logger.error("  3. Check starting account is Move2Japan")
        logger.error("  4. Review error logs above")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
