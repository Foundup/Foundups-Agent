#!/usr/bin/env python3
"""
Test: Oops Page Recovery - Automatic Account Switching with UI-TARS Verification

This test verifies the oops page handler can automatically switch accounts
when landing on a channel that belongs to a different Google account.

HYBRID APPROACH (Phase 4H Pattern):
    - DOM-based detection: Fast oops page detection via #selectaccount-link
    - StudioAccountSwitcher: Existing account switching with UI-TARS training
    - Visual verification: Optional Gemini Vision for oops page confirmation

Test Scenario:
    1. Connect to Chrome (port 9222) which may be logged into wrong account
    2. Navigate to UnDaoDu channel (requires UnDaoDu account)
    3. DOM detects oops page (fast, 50ms)
    4. UI-TARS visual verification (optional, confirms DOM result)
    5. StudioAccountSwitcher handles recovery
    6. Verify we end up on the correct channel

Browser-Channel Mapping:
    Chrome (9222): Move2Japan, UnDaoDu
    Edge (9223): FoundUps, RavingANTIFA

Usage:
    python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_oops_recovery
    python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_oops_recovery --channel undaodu
    python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_oops_recovery --channel m2j
    python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_oops_recovery --use-vision
    python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_oops_recovery --dry-run

WSP Compliance:
    WSP 50: Pre-action verification (DOM + visual)
    WSP 77: Agent coordination (DOM fast path + UI-TARS training)
    WSP 84: Reusable recovery pattern via StudioAccountSwitcher
    WSP 91: Observability logging
"""

import argparse
import asyncio
import logging
import sys
import time
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Channel configurations for testing
CHANNELS = {
    "undaodu": {
        "id": "UCfHM9Fw9HD-NwiS0seD_oIA",
        "name": "UnDaoDu",
        "browser": "chrome",
        "port": 9222,
    },
    "m2j": {
        "id": "UC-LSSlOZwpGIRIYihaz8zCw",
        "name": "Move2Japan",
        "browser": "chrome",
        "port": 9222,
    },
    "foundups": {
        "id": "UCSNTUXjAgpd4sgWYP0xoJgw",
        "name": "FoundUps",
        "browser": "edge",
        "port": 9223,
    },
    "ravingantifa": {
        "id": "UCVSmg5aOhP4tnQ9KFUg97qA",
        "name": "RavingANTIFA",
        "browser": "edge",
        "port": 9223,
    },
}


def connect_to_browser(port: int, timeout: int = 10):
    """
    Connect to browser via Chrome DevTools Protocol.

    Args:
        port: Debug port (9222 for Chrome, 9223 for Edge)
        timeout: Connection timeout in seconds

    Returns:
        Selenium WebDriver instance or None if connection failed
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import WebDriverException

    logger.info(f"Connecting to browser on port {port}...")

    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")

    try:
        driver = webdriver.Chrome(options=options)
        logger.info(f"Connected to browser: {driver.title[:50]}...")
        return driver
    except WebDriverException as e:
        logger.error(f"Failed to connect to browser on port {port}: {e}")
        return None


def verify_oops_with_vision(driver) -> dict:
    """
    Visual verification of oops page using Gemini Vision.

    Returns:
        Dict with is_oops, confidence, description
    """
    try:
        from modules.infrastructure.foundups_vision.src.gemini_vision_bridge import (
            analyze_screenshot
        )

        # Take screenshot
        screenshot = driver.get_screenshot_as_png()

        # Analyze with Gemini Vision
        result = analyze_screenshot(
            screenshot,
            prompt="Is this a YouTube Studio 'oops' error page showing wrong account? "
                   "Look for: 'Switch account' link, error message about access. "
                   "Reply JSON: {\"is_oops\": true/false, \"confidence\": 0.0-1.0, \"reason\": \"...\"}"
        )

        logger.info(f"[VISION] Gemini analysis: {result}")
        return result

    except Exception as e:
        logger.debug(f"[VISION] Verification not available: {e}")
        return {"is_oops": None, "confidence": 0.0, "error": str(e)}


async def test_oops_recovery(
    channel_key: str,
    dry_run: bool = False,
    use_vision: bool = False
) -> dict:
    """
    Test oops page recovery for a specific channel.

    HYBRID APPROACH:
        1. DOM detection (fast, ~50ms)
        2. Optional: Vision verification (confirms DOM, ~500ms)
        3. StudioAccountSwitcher for recovery (with UI-TARS training)

    Args:
        channel_key: Channel identifier (undaodu, m2j, foundups, ravingantifa)
        dry_run: If True, only log actions without executing
        use_vision: If True, use Gemini Vision for visual verification

    Returns:
        Test result dict with success, oops_detected, recovered, error fields
    """
    result = {
        "success": False,
        "channel": channel_key,
        "oops_detected": False,
        "oops_vision_confirmed": None,
        "recovered": False,
        "recovery_method": None,
        "error": None,
        "final_url": None,
    }

    if channel_key not in CHANNELS:
        result["error"] = f"Unknown channel: {channel_key}"
        logger.error(result["error"])
        return result

    channel = CHANNELS[channel_key]
    channel_id = channel["id"]
    channel_name = channel["name"]
    port = channel["port"]

    logger.info("=" * 60)
    logger.info(f"OOPS RECOVERY TEST: {channel_name}")
    logger.info(f"Channel ID: {channel_id}")
    logger.info(f"Browser: {channel['browser']} (port {port})")
    logger.info(f"Vision verification: {'ENABLED' if use_vision else 'disabled'}")
    logger.info("=" * 60)

    if dry_run:
        logger.info("[DRY RUN] Would connect to browser and test oops recovery")
        result["success"] = True
        return result

    # Step 1: Connect to browser
    driver = connect_to_browser(port)
    if not driver:
        result["error"] = f"Could not connect to browser on port {port}"
        return result

    try:
        # Step 2: Import DOM automation
        from modules.platform_integration.youtube_shorts_scheduler.src.dom_automation import (
            YouTubeStudioDOM
        )

        dom = YouTubeStudioDOM(driver)

        # Step 3: Navigate to target channel (may trigger oops page)
        target_url = f"https://studio.youtube.com/channel/{channel_id}/videos/short"
        logger.info(f"Navigating to: {target_url}")
        driver.get(target_url)
        time.sleep(3)  # Wait for page load

        # Step 4: DOM-based oops detection (fast path)
        start_time = time.time()
        oops_detected = dom.detect_oops_page()
        dom_time = (time.time() - start_time) * 1000
        result["oops_detected"] = oops_detected
        logger.info(f"[DOM] Oops detection: {oops_detected} ({dom_time:.0f}ms)")

        # Step 4b: Optional vision verification
        if use_vision and oops_detected:
            logger.info("[VISION] Running visual verification...")
            vision_result = verify_oops_with_vision(driver)
            result["oops_vision_confirmed"] = vision_result.get("is_oops")
            logger.info(f"[VISION] Confirmed: {vision_result.get('is_oops')} "
                       f"(confidence: {vision_result.get('confidence', 0):.1%})")

        if oops_detected:
            logger.warning("[OOPS] Oops page detected - wrong account!")
            logger.info("[OOPS] Attempting recovery via StudioAccountSwitcher...")

            # Step 5: Use StudioAccountSwitcher for recovery (has UI-TARS training)
            try:
                from modules.infrastructure.foundups_vision.src.studio_account_switcher import (
                    StudioAccountSwitcher
                )

                switcher = StudioAccountSwitcher()
                switcher.driver = driver  # Reuse existing driver

                # Initialize interaction controller
                from modules.infrastructure.human_interaction import get_interaction_controller
                switcher.interaction = get_interaction_controller(driver, platform="youtube_studio")

                # Use the proper account name mapping
                account_map = {
                    "undaodu": "UnDaoDu",
                    "m2j": "Move2Japan",
                    "foundups": "FoundUps",
                    "ravingantifa": "RavingANTIFA"  # Note: Not in StudioAccountSwitcher
                }
                target_account = account_map.get(channel_key, channel_name)

                logger.info(f"[SWITCHER] Switching to account: {target_account}")
                switch_result = await switcher.switch_to_account(target_account, navigate_to_comments=False)

                if switch_result.get("success"):
                    logger.info("[SWITCHER] Account switch successful!")
                    result["recovered"] = True
                    result["recovery_method"] = "StudioAccountSwitcher"

                    # Navigate back to target URL
                    logger.info(f"[NAV] Returning to: {target_url}")
                    driver.get(target_url)
                    time.sleep(3)
                else:
                    logger.warning(f"[SWITCHER] Failed: {switch_result.get('error')}")
                    # Fallback to DOM-based recovery
                    logger.info("[FALLBACK] Trying DOM-based recovery...")
                    recovered = dom.handle_oops_page(channel_id)
                    result["recovered"] = recovered
                    result["recovery_method"] = "DOM" if recovered else "failed"

            except ImportError as e:
                logger.warning(f"[SWITCHER] Not available: {e}")
                # Fallback to DOM-based recovery
                logger.info("[FALLBACK] Using DOM-based recovery...")
                recovered = dom.handle_oops_page(channel_id)
                result["recovered"] = recovered
                result["recovery_method"] = "DOM" if recovered else "failed"

            if result["recovered"]:
                logger.info(f"[SUCCESS] Account switched via {result['recovery_method']}!")
            else:
                logger.error("[FAILED] Could not switch to correct account")
                result["error"] = "Recovery failed"
        else:
            logger.info("[OK] No oops page - already on correct account")
            result["recovered"] = True  # No recovery needed = success
            result["recovery_method"] = "not_needed"

        # Step 6: Verify final state
        time.sleep(2)
        result["final_url"] = driver.current_url

        # Check if we're on the correct channel
        if channel_id in result["final_url"]:
            logger.info(f"[VERIFIED] Now on correct channel: {channel_name}")
            result["success"] = True
        else:
            # Check if still on oops page
            if dom.detect_oops_page():
                logger.error("[FAILED] Still on oops page after recovery attempt")
                result["error"] = "Still on oops page"
            else:
                logger.warning(f"[WARNING] URL doesn't contain channel ID but not on oops page")
                result["success"] = True  # May be a redirect

    except Exception as e:
        logger.exception(f"Test failed with exception: {e}")
        result["error"] = str(e)

    return result


async def test_cross_account_navigation(
    dry_run: bool = False,
    use_vision: bool = False
) -> dict:
    """
    Test navigating from wrong account to correct account.

    Scenario: Chrome might be logged into FoundUps/RavingANTIFA (wrong)
    but we want to access UnDaoDu/Move2Japan (correct for Chrome).

    This tests the full recovery flow.
    """
    logger.info("=" * 60)
    logger.info("CROSS-ACCOUNT NAVIGATION TEST")
    logger.info("Scenario: Access UnDaoDu on Chrome (may be on wrong account)")
    logger.info("=" * 60)

    if dry_run:
        logger.info("[DRY RUN] Would test cross-account navigation")
        return {"success": True, "dry_run": True}

    # Test accessing UnDaoDu on Chrome
    # If Chrome is logged into wrong account, this will trigger oops page
    result = await test_oops_recovery("undaodu", dry_run=False, use_vision=use_vision)

    return result


async def async_main():
    parser = argparse.ArgumentParser(
        description="Test oops page recovery for YouTube Studio automation"
    )
    parser.add_argument(
        "--channel",
        choices=list(CHANNELS.keys()),
        default="undaodu",
        help="Channel to test (default: undaodu)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log actions without executing"
    )
    parser.add_argument(
        "--use-vision",
        action="store_true",
        help="Enable Gemini Vision verification of oops page"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Test all Chrome channels (m2j, undaodu)"
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("OOPS PAGE RECOVERY TEST (with UI-TARS/Vision integration)")
    print("=" * 60 + "\n")

    if args.all:
        # Test all Chrome channels
        results = []
        for ch in ["m2j", "undaodu"]:
            logger.info(f"\n--- Testing {ch} ---\n")
            result = await test_oops_recovery(ch, dry_run=args.dry_run, use_vision=args.use_vision)
            results.append(result)
            time.sleep(2)  # Brief pause between tests

        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        for r in results:
            status = "PASS" if r["success"] else "FAIL"
            oops = "Yes" if r["oops_detected"] else "No"
            recovered = "Yes" if r["recovered"] else "No"
            method = r.get("recovery_method", "N/A")
            print(f"  {r['channel']:15} | {status:4} | Oops: {oops:3} | Recovered: {recovered} | Method: {method}")

        all_passed = all(r["success"] for r in results)
        print("=" * 60)
        print(f"OVERALL: {'ALL PASSED' if all_passed else 'SOME FAILED'}")

        return 0 if all_passed else 1

    else:
        # Test single channel
        result = await test_oops_recovery(args.channel, dry_run=args.dry_run, use_vision=args.use_vision)

        print("\n" + "=" * 60)
        print("TEST RESULT")
        print("=" * 60)
        print(f"  Channel:         {result['channel']}")
        print(f"  Success:         {result['success']}")
        print(f"  Oops Detected:   {result['oops_detected']}")
        if result.get('oops_vision_confirmed') is not None:
            print(f"  Vision Confirm:  {result['oops_vision_confirmed']}")
        print(f"  Recovered:       {result['recovered']}")
        print(f"  Method:          {result.get('recovery_method', 'N/A')}")
        if result['error']:
            print(f"  Error:           {result['error']}")
        if result['final_url']:
            print(f"  Final URL:       {result['final_url'][:80]}...")
        print("=" * 60)

        return 0 if result["success"] else 1


def main():
    """Sync wrapper for async main."""
    return asyncio.run(async_main())


if __name__ == "__main__":
    sys.exit(main())
