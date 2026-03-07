"""
Find and click YouTube Create button.
"""

import logging
import os
import sys
import time

sys.path.insert(0, "O:/Foundups-Agent")

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def main():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    opts = Options()
    opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    driver = webdriver.Chrome(options=opts)
    logger.info(f"[URL] {driver.current_url}")

    # Go to YouTube if not there
    if "youtube.com" not in driver.current_url or "studio" in driver.current_url:
        logger.info("[NAV] Going to youtube.com...")
        driver.get("https://www.youtube.com")
        time.sleep(4)

    logger.info(f"[URL] {driver.current_url}")

    # Check if logged in
    logged_in = driver.execute_script("""
        const avatar = document.querySelector('button#avatar-btn, #avatar-btn, img#img');
        return avatar !== null;
    """)
    logger.info(f"[LOGGED IN] {logged_in}")

    # Look for Create button (called "upload" or "create" in YouTube)
    logger.info("")
    logger.info("=== LOOKING FOR CREATE BUTTON ===")

    # In YouTube, Create is often a button with a + icon
    create_info = driver.execute_script("""
        const results = [];

        // Look for ytd-topbar-menu-button-renderer (common YouTube UI component)
        const menuButtons = document.querySelectorAll('ytd-topbar-menu-button-renderer');
        menuButtons.forEach((btn, i) => {
            results.push({
                type: 'menu-button',
                index: i,
                text: (btn.textContent || '').trim().substring(0, 30),
                ariaLabel: btn.getAttribute('aria-label') || ''
            });
        });

        // Look for buttons in #buttons container
        const buttonsContainer = document.querySelector('#buttons');
        if (buttonsContainer) {
            buttonsContainer.querySelectorAll('button, ytd-button-renderer').forEach((btn, i) => {
                results.push({
                    type: 'buttons-container',
                    index: i,
                    tag: btn.tagName,
                    text: (btn.textContent || '').trim().substring(0, 30),
                    ariaLabel: btn.getAttribute('aria-label') || ''
                });
            });
        }

        // Look for svg icons that might be the + icon
        const ytIcons = document.querySelectorAll('yt-icon');
        ytIcons.forEach((icon, i) => {
            const iconName = icon.getAttribute('icon') || '';
            const parent = icon.closest('button, ytd-button-renderer, yt-icon-button');
            if (iconName.includes('create') || iconName.includes('upload') || iconName.includes('plus')) {
                results.push({
                    type: 'yt-icon',
                    icon: iconName,
                    parentTag: parent ? parent.tagName : null,
                    parentLabel: parent ? parent.getAttribute('aria-label') : null
                });
            }
        });

        return results;
    """)

    for info in create_info:
        logger.info(f"  {info}")

    # Try clicking the first menu button (often Create)
    logger.info("")
    logger.info("=== TRYING TO CLICK MENU BUTTONS ===")

    click_result = driver.execute_script("""
        // Click the topbar menu button (usually Create)
        const menuButtons = document.querySelectorAll('ytd-topbar-menu-button-renderer');
        for (const btn of menuButtons) {
            const clickable = btn.querySelector('button') || btn;
            if (clickable) {
                clickable.click();
                return {clicked: true, text: (btn.textContent || '').trim().substring(0, 30)};
            }
        }
        return {clicked: false};
    """)
    logger.info(f"  Click result: {click_result}")

    if click_result.get('clicked'):
        time.sleep(1)

        # Look for dropdown items
        logger.info("")
        logger.info("=== DROPDOWN ITEMS ===")
        dropdown_items = driver.execute_script("""
            const items = [];
            document.querySelectorAll('tp-yt-paper-item, ytd-menu-service-item-renderer, a[role="menuitem"]').forEach(item => {
                items.push({
                    tag: item.tagName,
                    text: (item.textContent || '').trim().substring(0, 40),
                    href: item.href || null
                });
            });
            return items;
        """)

        for item in dropdown_items[:10]:
            logger.info(f"  {item}")

        # Try to click Go Live
        logger.info("")
        logger.info("=== CLICKING GO LIVE ===")
        go_live_result = driver.execute_script("""
            const items = document.querySelectorAll('tp-yt-paper-item, ytd-menu-service-item-renderer, a');
            for (const item of items) {
                const text = (item.textContent || '').toLowerCase();
                if (text.includes('go live')) {
                    item.click();
                    return {clicked: true, text: item.textContent.trim()};
                }
            }
            return {clicked: false};
        """)
        logger.info(f"  {go_live_result}")

        time.sleep(2)
        logger.info(f"[FINAL URL] {driver.current_url}")


if __name__ == "__main__":
    main()
