"""
Edge Browser Comment Processing Test
======================================

Demonstrates that Edge browser CAN process YouTube comments
just like Chrome (Like + Heart + Reply actions).

This is a proof-of-concept for Sprint 3.2 (BrowserManager integration).
"""

import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def test_edge_comment_processing():
    """
    Test Edge browser comment processing capabilities.

    Validates:
    1. Edge can find comment threads
    2. Edge can click Like button
    3. Edge can click Heart button
    4. Edge can open reply box and type
    """
    logger.info("="*60)
    logger.info(" EDGE BROWSER COMMENT PROCESSING TEST")
    logger.info("="*60)

    try:
        # Step 1: Get existing Edge browser instance
        logger.info("\n[STEP 1] Connecting to Edge browser...")
        from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager

        browser_manager = get_browser_manager()

        # Get the existing Edge browser (from validation test)
        browser = browser_manager.get_browser(
            browser_type='edge',
            profile_name='youtube_studio_test',
            options={}
        )
        logger.info(f"✅ Connected to Edge: {browser.current_url[:80]}")

        # Step 2: Check current page
        logger.info("\n[STEP 2] Verifying YouTube Studio page...")
        current_url = browser.current_url

        if "studio.youtube.com" not in current_url:
            logger.error(f"❌ Not on YouTube Studio: {current_url}")
            logger.error("Please navigate Edge to YouTube Studio comments page")
            return "NOT_ON_STUDIO"

        logger.info(f"✅ On YouTube Studio: {current_url[:80]}")

        # Step 3: Find comment threads
        logger.info("\n[STEP 3] Finding comment threads...")
        time.sleep(2)  # Wait for page load

        comment_threads = browser.find_elements(By.CSS_SELECTOR, "ytcp-comment-thread")
        logger.info(f"Found {len(comment_threads)} comment threads")

        if len(comment_threads) == 0:
            logger.warning("⚠️ No comments found (empty inbox)")
            return "NO_COMMENTS"

        # Step 4: Process first comment (Like + Heart + Reply)
        logger.info(f"\n[STEP 4] Processing first comment thread...")
        first_thread = comment_threads[0]

        try:
            # Find Like button
            like_button = first_thread.find_element(By.CSS_SELECTOR, "#like-button")
            like_aria = like_button.get_attribute("aria-pressed")
            logger.info(f"  Like button state: {like_aria}")

            if like_aria == "false":
                like_button.click()
                logger.info("  ✅ Clicked Like button")
                time.sleep(0.5)
            else:
                logger.info("  ✓ Already liked")

            # Find Heart button (Creator Heart)
            heart_button = first_thread.find_element(By.CSS_SELECTOR, "#creator-heart-button")
            heart_aria = heart_button.get_attribute("aria-pressed")
            logger.info(f"  Heart button state: {heart_aria}")

            if heart_aria == "false":
                heart_button.click()
                logger.info("  ✅ Clicked Heart button")
                time.sleep(0.5)
            else:
                logger.info("  ✓ Already hearted")

            # Find Reply button
            reply_button = first_thread.find_element(By.CSS_SELECTOR, "#reply-button")
            reply_button.click()
            logger.info("  ✅ Clicked Reply button")
            time.sleep(1)

            # Find reply textarea
            reply_box = first_thread.find_element(By.CSS_SELECTOR, "#contenteditable-textarea")
            reply_box.clear()
            reply_box.send_keys("✅ Edge browser test - 0102 validation")
            logger.info("  ✅ Typed reply text")
            time.sleep(0.5)

            # Find Submit button
            submit_button = first_thread.find_element(By.CSS_SELECTOR, "#submit-button")
            submit_button.click()
            logger.info("  ✅ Clicked Submit button")
            time.sleep(2)

            logger.info("\n✅ COMMENT PROCESSED SUCCESSFULLY WITH EDGE!")
            logger.info("Edge browser CAN process YouTube comments!")

        except Exception as e:
            logger.error(f"❌ Error processing comment: {e}")
            return "PROCESSING_ERROR"

        # Summary
        logger.info("\n" + "="*60)
        logger.info(" VALIDATION RESULTS")
        logger.info("="*60)
        logger.info("✅ Edge browser: OPERATIONAL")
        logger.info("✅ YouTube Studio access: SUCCESS")
        logger.info("✅ Comment detection: SUCCESS")
        logger.info("✅ Like action: SUCCESS")
        logger.info("✅ Heart action: SUCCESS")
        logger.info("✅ Reply action: SUCCESS")
        logger.info("="*60)
        logger.info("\n✅ EDGE CAN DO THE WORK!")
        logger.info("Ready for Sprint 3.2 (BrowserManager integration)")

        logger.info("\nBrowser window left open for inspection.")
        logger.info("Press Ctrl+C to close and exit.")

        # Keep alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\nClosing browser...")
            # Don't close - leave for inspection
            logger.info("Browser left open.")

        return "SUCCESS"

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return "ERROR"


if __name__ == "__main__":
    result = test_edge_comment_processing()

    # Exit codes
    exit_codes = {
        "SUCCESS": 0,
        "NOT_ON_STUDIO": 1,
        "NO_COMMENTS": 2,
        "PROCESSING_ERROR": 3,
        "ERROR": 4,
    }

    exit(exit_codes.get(result, 4))
