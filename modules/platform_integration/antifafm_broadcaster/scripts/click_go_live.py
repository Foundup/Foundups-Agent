"""
Click Create (+) -> Go Live on YouTube to start broadcast.
antifaFM channel is already active in browser.
"""

import logging
import os
import sys
import time

sys.path.insert(0, "O:/Foundups-Agent")

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

CHROME_DEBUG_PORT = int(os.getenv("FOUNDUPS_LIVECHAT_CHROME_PORT", "9222"))


def connect():
    """Connect to Chrome debug port."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    opts = Options()
    opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_DEBUG_PORT}")

    try:
        driver = webdriver.Chrome(options=opts)
        logger.info(f"[OK] Connected to Chrome")
        logger.info(f"[URL] {driver.current_url}")
        return driver
    except Exception as e:
        logger.error(f"[ERROR] {e}")
        return None


def go_to_youtube(driver):
    """Navigate to YouTube main page (not Studio)."""
    logger.info("[NAV] Going to youtube.com...")
    driver.get("https://www.youtube.com")
    time.sleep(3)
    logger.info(f"[URL] {driver.current_url}")


def click_create_button(driver):
    """Click the Create (+) button in YouTube header."""
    logger.info("[STEP 1] Clicking Create button...")

    result = driver.execute_script("""
        // Find Create button by aria-label
        const buttons = document.querySelectorAll('button');
        for (const btn of buttons) {
            const label = btn.getAttribute('aria-label') || '';
            if (label.toLowerCase().includes('create')) {
                btn.click();
                return {found: true, label: label};
            }
        }

        // Try by ID patterns
        const createBtn = document.querySelector('#create-button, yt-icon-button#create-icon');
        if (createBtn) {
            createBtn.click();
            return {found: true, method: 'id'};
        }

        // Try by yt-button-shape
        const ytBtns = document.querySelectorAll('yt-button-shape button');
        for (const btn of ytBtns) {
            const label = btn.getAttribute('aria-label') || '';
            if (label.includes('Create') || label.includes('Upload')) {
                btn.click();
                return {found: true, label: label, method: 'yt-button-shape'};
            }
        }

        return {found: false};
    """)

    logger.info(f"  Result: {result}")
    return result.get('found', False)


def click_go_live(driver):
    """Click 'Go live' in the dropdown menu."""
    logger.info("[STEP 2] Clicking 'Go live'...")

    result = driver.execute_script("""
        // Wait a moment for dropdown to render
        const items = document.querySelectorAll('tp-yt-paper-item, ytd-compact-link-renderer, ytd-menu-service-item-renderer, a');
        for (const item of items) {
            const text = (item.textContent || '').toLowerCase();
            if (text.includes('go live')) {
                item.click();
                return {found: true, text: item.textContent.trim().substring(0, 40)};
            }
        }

        // Try by aria-label
        const allClickable = document.querySelectorAll('[role="menuitem"], [role="option"], a, button');
        for (const el of allClickable) {
            const label = (el.getAttribute('aria-label') || '').toLowerCase();
            const text = (el.textContent || '').toLowerCase();
            if (label.includes('go live') || text.includes('go live')) {
                el.click();
                return {found: true, method: 'aria/text', text: el.textContent.trim().substring(0, 40)};
            }
        }

        return {found: false};
    """)

    logger.info(f"  Result: {result}")
    return result.get('found', False)


def main():
    logger.info("="*60)
    logger.info("YouTube Go Live Automation (antifaFM)")
    logger.info("="*60)

    driver = connect()
    if not driver:
        return

    # Navigate to YouTube (not Studio)
    go_to_youtube(driver)

    # Click Create
    if not click_create_button(driver):
        logger.error("[FAIL] Could not find Create button")
        return

    # Wait for dropdown
    time.sleep(1)

    # Click Go Live
    if not click_go_live(driver):
        logger.error("[FAIL] Could not find 'Go live' option")
        # Close any dropdown
        driver.execute_script("document.body.click();")
        return

    logger.info("[OK] Go Live clicked successfully!")
    time.sleep(2)
    logger.info(f"[FINAL URL] {driver.current_url}")


if __name__ == "__main__":
    main()
