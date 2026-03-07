"""
Diagnose YouTube Create button structure.
"""

import logging
import os
import sys
import time

sys.path.insert(0, "O:/Foundups-Agent")

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

CHROME_DEBUG_PORT = 9222


def main():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    opts = Options()
    opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_DEBUG_PORT}")

    driver = webdriver.Chrome(options=opts)
    logger.info(f"[URL] {driver.current_url}")

    # Go to YouTube if not there
    if "youtube.com" not in driver.current_url or "studio" in driver.current_url:
        logger.info("[NAV] Going to youtube.com...")
        driver.get("https://www.youtube.com")
        time.sleep(3)

    logger.info(f"[URL] {driver.current_url}")
    logger.info("")

    # Analyze all buttons
    analysis = driver.execute_script("""
        const results = {buttons: [], ytShapes: [], masthead: []};

        // All buttons
        document.querySelectorAll('button').forEach(btn => {
            const label = btn.getAttribute('aria-label') || '';
            const id = btn.id || '';
            const classes = btn.className || '';
            if (label || id) {
                results.buttons.push({
                    label: label.substring(0, 50),
                    id: id,
                    classes: classes.substring(0, 40),
                    visible: btn.offsetParent !== null
                });
            }
        });

        // yt-button-shape elements
        document.querySelectorAll('yt-button-shape, yt-icon-button').forEach(el => {
            const label = el.getAttribute('aria-label') || '';
            const id = el.id || '';
            const innerBtn = el.querySelector('button');
            const innerLabel = innerBtn ? innerBtn.getAttribute('aria-label') || '' : '';
            results.ytShapes.push({
                tag: el.tagName,
                id: id,
                label: label.substring(0, 50),
                innerLabel: innerLabel.substring(0, 50),
                visible: el.offsetParent !== null
            });
        });

        // Masthead elements (header)
        const masthead = document.querySelector('ytd-masthead, #masthead, #masthead-container');
        if (masthead) {
            masthead.querySelectorAll('button, yt-icon-button, ytd-button-renderer').forEach(el => {
                const label = el.getAttribute('aria-label') || '';
                const id = el.id || '';
                results.masthead.push({
                    tag: el.tagName,
                    id: id,
                    label: label.substring(0, 50),
                    text: (el.textContent || '').trim().substring(0, 30)
                });
            });
        }

        return results;
    """)

    logger.info("=== BUTTONS ===")
    for btn in analysis.get('buttons', [])[:15]:
        if btn.get('visible') and (btn.get('label') or btn.get('id')):
            logger.info(f"  {btn}")

    logger.info("")
    logger.info("=== YT-SHAPES ===")
    for shape in analysis.get('ytShapes', [])[:15]:
        logger.info(f"  {shape}")

    logger.info("")
    logger.info("=== MASTHEAD ELEMENTS ===")
    for el in analysis.get('masthead', [])[:20]:
        logger.info(f"  {el}")

    # Try to find Create specifically
    logger.info("")
    logger.info("=== SEARCH FOR CREATE ===")
    create_search = driver.execute_script("""
        const results = [];
        document.querySelectorAll('*').forEach(el => {
            const label = (el.getAttribute('aria-label') || '').toLowerCase();
            const text = (el.textContent || '').toLowerCase();
            const id = (el.id || '').toLowerCase();

            if ((label.includes('create') || text === 'create' || id.includes('create')) &&
                el.offsetParent !== null) {
                results.push({
                    tag: el.tagName,
                    id: el.id || '',
                    label: el.getAttribute('aria-label') || '',
                    text: (el.textContent || '').trim().substring(0, 30),
                    classes: (el.className || '').substring(0, 40)
                });
            }
        });
        return results.slice(0, 20);
    """)

    for el in create_search:
        logger.info(f"  {el}")


if __name__ == "__main__":
    main()
