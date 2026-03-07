"""
Debug script for YouTube Studio account switching.
Diagnoses why dropdown menu items aren't appearing after avatar click.
"""

import asyncio
import logging
import os
import sys
import time

# Add project root to path
sys.path.insert(0, "O:/Foundups-Agent")

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger(__name__)

# Use Chrome debug port (9222) - Edge has version issues
CHROME_DEBUG_PORT = int(os.getenv("FOUNDUPS_LIVECHAT_CHROME_PORT", "9222"))


def connect_to_browser():
    """Connect to existing Chrome session on debug port."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    opts = Options()
    opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_DEBUG_PORT}")

    try:
        driver = webdriver.Chrome(options=opts)
        logger.info(f"[OK] Connected to Chrome on port {CHROME_DEBUG_PORT}")
        logger.info(f"[URL] {driver.current_url}")
        logger.info(f"[TITLE] {driver.title}")
        return driver
    except Exception as e:
        logger.error(f"[ERROR] Connection failed: {e}")
        return None


def navigate_to_studio(driver):
    """Navigate to YouTube Studio FoundUps channel."""
    foundups_studio = "https://studio.youtube.com/channel/UCSNTUXjAgpd4sgWYP0xoJgw"

    if "studio.youtube.com" not in driver.current_url:
        logger.info(f"[NAV] Going to FoundUps Studio...")
        driver.get(foundups_studio)
        time.sleep(3)

    logger.info(f"[URL] {driver.current_url}")
    logger.info(f"[TITLE] {driver.title}")

    # Check if logged in
    avatar_exists = driver.execute_script("""
        return document.querySelector('button#avatar-btn') !== null ||
               document.querySelector('#avatar-btn') !== null;
    """)
    logger.info(f"[LOGIN] Avatar exists: {avatar_exists}")
    return avatar_exists


def diagnose_avatar_dropdown(driver):
    """Click avatar and diagnose the dropdown structure."""
    logger.info("\n" + "="*60)
    logger.info("STEP 1: Click Avatar Button")
    logger.info("="*60)

    # Click avatar
    avatar_clicked = driver.execute_script("""
        const btn = document.querySelector('button#avatar-btn') ||
                    document.querySelector('#avatar-btn');
        if (btn) {
            btn.click();
            return {clicked: true, tagName: btn.tagName, id: btn.id};
        }
        return {clicked: false};
    """)
    logger.info(f"[CLICK] Avatar: {avatar_clicked}")

    # Wait for dropdown to render
    time.sleep(2)

    logger.info("\n" + "="*60)
    logger.info("STEP 2: Analyze Dropdown Structure")
    logger.info("="*60)

    # Check for all possible dropdown/menu elements
    dropdown_analysis = driver.execute_script("""
        const results = {};

        // Check for paper items
        const paperItems = document.querySelectorAll('tp-yt-paper-item');
        results.paper_items = paperItems.length;
        results.paper_item_texts = [];
        paperItems.forEach(item => {
            const text = item.textContent.trim().substring(0, 50);
            if (text) results.paper_item_texts.push(text);
        });

        // Check for ytcp-ve (YouTube Creator Studio elements)
        const ytcpVe = document.querySelectorAll('ytcp-ve');
        results.ytcp_ve = ytcpVe.length;

        // Check for any visible menus
        const menus = document.querySelectorAll('[role="menu"], [role="listbox"]');
        results.menus = menus.length;

        // Check for dropdown/popup elements
        const dropdowns = document.querySelectorAll('tp-yt-paper-listbox, ytcp-popup-container');
        results.dropdowns = dropdowns.length;

        // Check for account-related elements
        const accountItems = document.querySelectorAll('ytd-account-item-renderer, ytcp-account-item-renderer');
        results.account_items = accountItems.length;

        // Check for any element containing "Switch"
        const allElements = document.querySelectorAll('*');
        results.switch_elements = 0;
        for (const el of allElements) {
            if (el.textContent && el.textContent.includes('Switch account')) {
                results.switch_elements++;
            }
        }

        // Check for iron-dropdown
        const ironDropdown = document.querySelectorAll('iron-dropdown');
        results.iron_dropdown = ironDropdown.length;

        // Check for ytcp-text-menu
        const textMenu = document.querySelectorAll('ytcp-text-menu, ytcp-popup-container');
        results.text_menu = textMenu.length;

        return results;
    """)

    for key, value in dropdown_analysis.items():
        logger.info(f"  {key}: {value}")

    logger.info("\n" + "="*60)
    logger.info("STEP 3: Try Direct Switch Account Click")
    logger.info("="*60)

    # Try multiple selectors for Switch account
    switch_result = driver.execute_script("""
        // Strategy 1: tp-yt-paper-item with Switch account text
        const items1 = document.querySelectorAll('tp-yt-paper-item');
        for (const item of items1) {
            if (item.textContent.includes('Switch account')) {
                item.click();
                return {found: true, selector: 'tp-yt-paper-item', text: item.textContent.trim()};
            }
        }

        // Strategy 2: ytcp-ve with Switch account
        const items2 = document.querySelectorAll('ytcp-ve');
        for (const item of items2) {
            if (item.textContent.includes('Switch account')) {
                item.click();
                return {found: true, selector: 'ytcp-ve', text: item.textContent.trim()};
            }
        }

        // Strategy 3: Any clickable element with Switch
        const items3 = document.querySelectorAll('a, button, [role="menuitem"], [role="option"]');
        for (const item of items3) {
            if (item.textContent && item.textContent.includes('Switch')) {
                item.click();
                return {found: true, selector: 'role/link', text: item.textContent.trim().substring(0, 50)};
            }
        }

        return {found: false};
    """)
    logger.info(f"[SWITCH] {switch_result}")

    if switch_result.get('found'):
        time.sleep(2)

        logger.info("\n" + "="*60)
        logger.info("STEP 4: Look for Account Selection")
        logger.info("="*60)

        accounts = driver.execute_script("""
            const results = [];

            // Look for account items
            const items = document.querySelectorAll('ytd-account-item-renderer, ytcp-account-item-renderer, tp-yt-paper-item');
            for (const item of items) {
                const text = item.textContent.trim();
                if (text.includes('antifaFM') || text.includes('FoundUps') ||
                    text.includes('UnDaoDu') || text.includes('Move2Japan')) {
                    results.push({text: text.substring(0, 60), tag: item.tagName});
                }
            }

            return results;
        """)
        logger.info(f"[ACCOUNTS] Found: {len(accounts)}")
        for acc in accounts:
            logger.info(f"  - {acc}")

    return dropdown_analysis


def try_click_antifafm(driver):
    """Attempt to click antifaFM account."""
    logger.info("\n" + "="*60)
    logger.info("STEP 5: Click antifaFM")
    logger.info("="*60)

    result = driver.execute_script("""
        const items = document.querySelectorAll('*');
        for (const item of items) {
            const text = item.textContent || '';
            if (text.includes('antifaFM') && item.offsetParent !== null) {
                // Check if clickable
                if (item.tagName === 'A' || item.tagName === 'BUTTON' ||
                    item.getAttribute('role') === 'option' || item.getAttribute('role') === 'menuitem' ||
                    item.tagName.includes('RENDERER') || item.tagName.includes('ITEM')) {
                    item.click();
                    return {clicked: true, tag: item.tagName, text: text.substring(0, 60)};
                }
            }
        }
        return {clicked: false};
    """)
    logger.info(f"[ANTIFAFM] {result}")

    if result.get('clicked'):
        time.sleep(3)
        logger.info(f"[NEW URL] {driver.current_url}")

    return result


async def main():
    logger.info("="*60)
    logger.info("YouTube Studio Account Switching Diagnostics")
    logger.info("="*60)

    driver = connect_to_browser()
    if not driver:
        return

    if not navigate_to_studio(driver):
        logger.error("[ERROR] Not logged in to YouTube Studio")
        return

    diagnose_avatar_dropdown(driver)
    try_click_antifafm(driver)

    logger.info("\n" + "="*60)
    logger.info("FINAL STATE")
    logger.info("="*60)
    logger.info(f"[URL] {driver.current_url}")
    logger.info(f"[TITLE] {driver.title}")


if __name__ == "__main__":
    asyncio.run(main())
