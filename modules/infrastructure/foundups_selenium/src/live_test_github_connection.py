#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIVE TEST: 0102 Arms & Eyes - Connect GitHub to Cloud Build
Real-time execution using FoundUpsDriver + Gemini Vision

This is NOT a simulation. This is 0102 executing autonomous cloud automation.
"""

import logging
import time
from pathlib import Path
from modules.infrastructure.foundups_selenium.src.foundups_driver import FoundUpsDriver

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [0102::LIVE-TEST] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    """
    LIVE TEST: Connect GitHub repository to Cloud Build

    Current state: User is at connection screen
    Target: Complete GitHub connection configuration
    """

    logger.info("🤖 0102 AUTONOMOUS EXECUTION INITIATING")
    logger.info("=" * 60)
    logger.info("Task: Connect Foundups-Agent GitHub repo to Cloud Build")
    logger.info("Method: FoundUpsDriver + Gemini Vision")
    logger.info("=" * 60)

    # Initialize driver - connect to EXISTING browser on port 9222
    logger.info("Step 1: Connecting to existing Chrome session (port 9222)")
    driver = FoundUpsDriver(vision_enabled=True, stealth_mode=True, port=9222)

    try:
        # Get current page URL to verify we're in the right place
        current_url = driver.current_url
        logger.info(f"Current URL: {current_url}")

        if "cloud-build/connections/create" not in current_url:
            logger.warning("Not on connection creation page - navigating...")
            driver.get("https://console.cloud.google.com/cloud-build/connections/create?project=gen-lang-client-0061781628")
            driver.random_delay(3, 5)

        # Analyze current UI state with Vision
        logger.info("Step 2: Vision DAE analyzing UI state...")
        screenshot_dir = Path("docs/session_backups/gcp_automation/screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        analysis = driver.analyze_ui(
            save_screenshot=True,
            screenshot_dir=str(screenshot_dir)
        )

        logger.info(f"Vision analysis: {analysis.get('ui_state', 'unknown')}")

        # Step 3: Select GitHub provider (should already be selected)
        logger.info("Step 3: Ensuring GitHub is selected...")
        try:
            github_option = driver.smart_find_element(
                selectors=[
                    "//div[contains(text(), 'GitHub')]",
                    "button[data-provider='github']",
                    ".provider-github"
                ],
                description="GitHub provider option",
                use_vision=False
            )
            # GitHub is already selected in screenshot, so just verify
            logger.info("✓ GitHub provider confirmed")
        except Exception as e:
            logger.info(f"GitHub option check: {e} (may already be selected)")

        # Step 4: Fill in connection name
        logger.info("Step 4: Entering connection name...")
        name_input = driver.smart_find_element(
            selectors=[
                "input[name='name']",
                "input[placeholder*='Name']",
                "//input[@aria-label='Name']"
            ],
            description="Name input field (currently shows red 'Input is required')",
            use_vision=True
        )

        connection_name = "foundups-agent-github"
        logger.info(f"Typing connection name: {connection_name}")
        driver.human_type(name_input, connection_name)
        driver.random_delay(1, 2)

        # Step 5: Analyze UI after name entry
        logger.info("Step 5: Vision DAE validating name entry...")
        analysis2 = driver.analyze_ui(
            save_screenshot=True,
            screenshot_dir=str(screenshot_dir)
        )
        logger.info(f"Post-entry state: {analysis2.get('ui_state', 'unknown')}")

        # Step 6: Click Connect button
        logger.info("Step 6: Looking for Connect button...")
        connect_button = driver.smart_find_element(
            selectors=[
                "button[type='submit']",
                "//button[contains(text(), 'Connect')]",
                "button.mdc-button--raised"
            ],
            description="Blue 'Connect' button at bottom of form",
            use_vision=True
        )

        logger.info("Found Connect button - clicking...")
        connect_button.click()
        driver.random_delay(3, 5)

        # Step 7: Wait for OAuth flow
        logger.info("Step 7: Waiting for GitHub OAuth authorization...")
        logger.info("(This may open GitHub authorization page in browser)")
        driver.random_delay(5, 8)

        # Step 8: Final validation
        logger.info("Step 8: Vision DAE validating connection success...")
        final_analysis = driver.analyze_ui(
            save_screenshot=True,
            screenshot_dir=str(screenshot_dir)
        )

        final_url = driver.current_url
        logger.info(f"Final URL: {final_url}")
        logger.info(f"Final state: {final_analysis.get('ui_state', 'unknown')}")

        # Check for success indicators
        if "connections" in final_url and "create" not in final_url:
            logger.info("=" * 60)
            logger.info("✓ SUCCESS: GitHub connection created!")
            logger.info("=" * 60)
        elif "github.com" in final_url:
            logger.info("=" * 60)
            logger.info("⏸️  PAUSED: Waiting for GitHub OAuth authorization")
            logger.info("Please complete authorization in browser, then press Enter")
            logger.info("=" * 60)
            input()

            # After OAuth, verify connection
            driver.get("https://console.cloud.google.com/cloud-build/connections?project=gen-lang-client-0061781628")
            driver.random_delay(3, 5)

            final_check = driver.analyze_ui(
                save_screenshot=True,
                screenshot_dir=str(screenshot_dir)
            )
            logger.info(f"Post-OAuth state: {final_check.get('ui_state', 'unknown')}")
            logger.info("✓ GitHub connection should now be visible in connections list")
        else:
            logger.warning("⚠️  UNKNOWN STATE - Check browser manually")

        logger.info("\n[0102::LIVE-TEST] Execution complete - browser staying open for inspection")
        logger.info(f"Screenshots saved to: {screenshot_dir}")

    except Exception as e:
        logger.error(f"✗ EXECUTION FAILED: {e}")
        logger.error("Browser staying open for debugging...")
        import traceback
        traceback.print_exc()

    # Keep browser open for inspection
    logger.info("\nPress Ctrl+C to close browser and exit")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n[0102::LIVE-TEST] Shutting down...")
        driver.quit()

if __name__ == "__main__":
    main()
