"""
Dump YouTube header/masthead DOM structure.
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

    # Dump the masthead HTML
    logger.info("")
    logger.info("=== MASTHEAD INNER HTML (truncated) ===")

    masthead_html = driver.execute_script("""
        const masthead = document.querySelector('ytd-masthead, #masthead, #container.ytd-masthead');
        if (masthead) {
            return masthead.innerHTML.substring(0, 3000);
        }
        return 'MASTHEAD NOT FOUND';
    """)
    logger.info(masthead_html[:2000])

    # Find all clickable elements in the header/end area
    logger.info("")
    logger.info("=== END AREA ELEMENTS (right side of header) ===")

    end_elements = driver.execute_script("""
        const results = [];

        // Look for #end or #buttons in masthead
        const endArea = document.querySelector('#end, #buttons, ytd-masthead #end');
        if (endArea) {
            endArea.querySelectorAll('*').forEach(el => {
                if (el.tagName && el.offsetParent !== null) {
                    results.push({
                        tag: el.tagName,
                        id: el.id || '',
                        ariaLabel: el.getAttribute('aria-label') || '',
                        ariaHaspopup: el.getAttribute('aria-haspopup') || '',
                        text: (el.textContent || '').trim().substring(0, 20)
                    });
                }
            });
        }

        return results.slice(0, 30);
    """)

    for el in end_elements:
        if el.get('ariaLabel') or el.get('id') or el.get('ariaHaspopup'):
            logger.info(f"  {el}")

    # Try to directly find upload/create icon
    logger.info("")
    logger.info("=== SEARCHING FOR UPLOAD/CREATE ICON ===")

    icon_search = driver.execute_script("""
        const results = [];

        // Look for any element with upload, create, plus in attributes
        const allElements = document.querySelectorAll('#end *, ytd-masthead *');
        for (const el of allElements) {
            const attrs = el.getAttributeNames ? el.getAttributeNames() : [];
            for (const attr of attrs) {
                const val = el.getAttribute(attr) || '';
                if (val.toLowerCase().includes('upload') ||
                    val.toLowerCase().includes('create') ||
                    val.toLowerCase().includes('plus')) {
                    results.push({
                        tag: el.tagName,
                        attr: attr,
                        value: val.substring(0, 50),
                        id: el.id || ''
                    });
                    break;
                }
            }
        }

        return results.slice(0, 15);
    """)

    for el in icon_search:
        logger.info(f"  {el}")

    # Try clicking by position - Upload button is usually 3rd from right
    logger.info("")
    logger.info("=== TRYING POSITION-BASED CLICK ===")

    # Get all visible buttons/clickable in #end area
    click_attempt = driver.execute_script("""
        const endArea = document.querySelector('#end, #buttons');
        if (!endArea) return {found: false, reason: 'no #end area'};

        // Get all button-like elements
        const buttons = endArea.querySelectorAll('button, yt-icon-button, ytd-button-renderer, [role="button"]');
        const visible = Array.from(buttons).filter(b => b.offsetParent !== null);

        if (visible.length === 0) return {found: false, reason: 'no visible buttons'};

        // Usually: [Notifications] [Upload/Create] [Avatar]
        // Try clicking the one before avatar
        if (visible.length >= 2) {
            const target = visible[visible.length - 2];  // Second from right
            const innerBtn = target.querySelector('button') || target;
            innerBtn.click();
            return {found: true, index: visible.length - 2, tag: target.tagName, label: target.getAttribute('aria-label')};
        }

        return {found: false, reason: 'not enough buttons'};
    """)

    logger.info(f"  Result: {click_attempt}")

    if click_attempt.get('found'):
        time.sleep(1.5)

        # Check for dropdown
        logger.info("")
        logger.info("=== DROPDOWN CONTENT ===")
        dropdown = driver.execute_script("""
            const results = [];
            // Look for visible dropdowns/menus
            const menus = document.querySelectorAll('tp-yt-paper-listbox, ytd-menu-popup-renderer, [role="menu"], [role="listbox"]');
            menus.forEach(menu => {
                if (menu.offsetParent !== null) {
                    menu.querySelectorAll('*').forEach(item => {
                        const text = (item.textContent || '').trim();
                        if (text && text.length > 2 && text.length < 50) {
                            results.push({tag: item.tagName, text: text});
                        }
                    });
                }
            });
            return results.slice(0, 15);
        """)

        for item in dropdown:
            logger.info(f"  {item}")


if __name__ == "__main__":
    main()
