"""
Edge Browser YouTube Studio Validation Test
============================================

Tests if Edge browser can access YouTube Studio with authentication.
This validates infrastructure BEFORE committing to architecture.

WSP 50: Pre-Action Verification - Test the infrastructure first!

Usage:
    python test_edge_youtube_studio.py
"""

import logging
import time
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def test_edge_youtube_studio():
    """
    Test Edge browser access to YouTube Studio.

    Validates:
    1. BrowserManager can create Edge browser
    2. Edge can navigate to YouTube Studio
    3. Authentication state persists
    4. Comments page accessible
    """
    logger.info("="*60)
    logger.info(" EDGE BROWSER YOUTUBE STUDIO VALIDATION TEST")
    logger.info("="*60)

    try:
        # Step 1: Import BrowserManager
        logger.info("\n[STEP 1] Importing BrowserManager...")
        from modules.infrastructure.foundups_selenium.src.browser_manager import (
            get_browser_manager
        )
        logger.info("✅ BrowserManager imported successfully")

        # Step 2: Create Edge browser instance
        logger.info("\n[STEP 2] Creating Edge browser instance...")
        browser_manager = get_browser_manager()

        # Use BrowserManager to get Edge browser
        browser = browser_manager.get_browser(
            browser_type='edge',
            profile_name='youtube_studio_test',
            options={}
        )
        logger.info("✅ Edge browser created successfully")

        # Step 3: Navigate to YouTube Studio
        logger.info("\n[STEP 3] Navigating to YouTube Studio...")
        channel_id = "UC-LSSlOZwpGIRIYihaz8zCw"  # Move2Japan
        studio_url = f"https://studio.youtube.com/channel/{channel_id}/comments/inbox"

        browser.get(studio_url)
        logger.info(f"✅ Navigated to: {studio_url}")

        # Wait for page load
        time.sleep(5)

        # Step 4: Check current URL (authentication check)
        logger.info("\n[STEP 4] Checking authentication...")
        current_url = browser.current_url
        logger.info(f"Current URL: {current_url}")

        if "accounts.google.com" in current_url:
            logger.warning("⚠️ AUTHENTICATION REQUIRED")
            logger.warning("Edge browser opened but requires Google login")
            logger.warning("Please sign in manually, then re-run test")
            result = "AUTH_REQUIRED"
        elif "studio.youtube.com" in current_url:
            logger.info("✅ AUTHENTICATED - YouTube Studio loaded!")
            logger.info(f"Page title: {browser.title}")
            result = "SUCCESS"
        else:
            logger.warning(f"⚠️ UNEXPECTED URL: {current_url}")
            result = "UNKNOWN"

        # Step 5: Check for comments page elements (if authenticated)
        if result == "SUCCESS":
            logger.info("\n[STEP 5] Checking for comments page...")
            try:
                # Wait a bit more for dynamic content
                time.sleep(3)

                # Check for comment thread elements
                comment_threads = browser.find_elements("css selector", "ytcp-comment-thread")
                logger.info(f"Found {len(comment_threads)} comment threads")

                if len(comment_threads) > 0:
                    logger.info("✅ Comments page loaded successfully!")
                    logger.info("✅ Edge browser can access YouTube Studio comments!")
                else:
                    logger.info("⚠️ No comments found (might be empty inbox)")
            except Exception as e:
                logger.warning(f"⚠️ Could not find comment elements: {e}")

        # Keep browser open for manual inspection
        logger.info("\n" + "="*60)
        logger.info(" TEST COMPLETE - Edge browser validation results:")
        logger.info("="*60)
        logger.info(f" Result: {result}")
        logger.info(f" Browser: Edge")
        logger.info(f" Profile: youtube_studio_test")
        logger.info(f" URL: {current_url}")
        logger.info("="*60)

        if result == "AUTH_REQUIRED":
            logger.info("\n⚠️ NEXT STEPS:")
            logger.info("1. Sign in to Google in the Edge browser window")
            logger.info("2. Re-run this test")
            logger.info("3. Edge should remember auth state via profile")
        elif result == "SUCCESS":
            logger.info("\n✅ VALIDATION SUCCESSFUL!")
            logger.info("Edge browser CAN access YouTube Studio")
            logger.info("Ready for Sprint 3.2 (BrowserManager integration)")

        logger.info("\nBrowser window left open for inspection.")
        logger.info("Press Ctrl+C to close and exit.")

        # Keep alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\nClosing browser...")
            browser.quit()
            logger.info("Browser closed.")

        return result

    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        logger.error("Is foundups_selenium module available?")
        return "IMPORT_ERROR"

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return "ERROR"


if __name__ == "__main__":
    result = test_edge_youtube_studio()

    # Exit codes for CI/CD
    exit_codes = {
        "SUCCESS": 0,
        "AUTH_REQUIRED": 1,
        "UNKNOWN": 2,
        "IMPORT_ERROR": 3,
        "ERROR": 4,
    }

    exit(exit_codes.get(result, 4))
