"""
Go directly to YouTube Studio Live Streaming page for antifaFM.
"""

import logging
import os
import sys
import time

sys.path.insert(0, "O:/Foundups-Agent")

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# antifaFM channel ID
ANTIFAFM_CHANNEL_ID = "UCVSmg5aOhP4tnQ9KFUg97qA"
LIVE_STREAM_URL = f"https://studio.youtube.com/channel/{ANTIFAFM_CHANNEL_ID}/livestreaming/stream"


def main():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    opts = Options()
    opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    driver = webdriver.Chrome(options=opts)
    logger.info(f"[CURRENT URL] {driver.current_url}")

    # Navigate directly to live streaming page
    logger.info(f"[NAV] Going to Live Streaming page...")
    logger.info(f"[URL] {LIVE_STREAM_URL}")
    driver.get(LIVE_STREAM_URL)
    time.sleep(5)

    logger.info(f"[FINAL URL] {driver.current_url}")
    logger.info(f"[TITLE] {driver.title}")

    # Check if on live streaming page
    on_live_page = "livestreaming" in driver.current_url
    logger.info(f"[ON LIVE PAGE] {on_live_page}")

    if on_live_page:
        # Look for "Go Live" button on the live streaming page
        logger.info("")
        logger.info("=== LOOKING FOR GO LIVE BUTTON ===")

        buttons = driver.execute_script("""
            const results = [];
            document.querySelectorAll('button, ytcp-button').forEach(btn => {
                const text = (btn.textContent || '').trim();
                const label = btn.getAttribute('aria-label') || '';
                if (text || label) {
                    results.push({
                        tag: btn.tagName,
                        text: text.substring(0, 40),
                        label: label.substring(0, 40),
                        disabled: btn.disabled
                    });
                }
            });
            return results;
        """)

        for btn in buttons[:15]:
            logger.info(f"  {btn}")

        # Try to click "Go live" button
        logger.info("")
        logger.info("=== CLICKING GO LIVE ===")
        click_result = driver.execute_script("""
            const buttons = document.querySelectorAll('button, ytcp-button');
            for (const btn of buttons) {
                const text = (btn.textContent || '').toLowerCase().trim();
                if (text === 'go live' || text.includes('go live')) {
                    btn.click();
                    return {clicked: true, text: btn.textContent.trim()};
                }
            }
            return {clicked: false};
        """)
        logger.info(f"  Result: {click_result}")

        if click_result.get('clicked'):
            time.sleep(3)
            logger.info(f"[FINAL URL] {driver.current_url}")
        else:
            # Maybe the stream is already set up - check for stream controls
            logger.info("")
            logger.info("=== CHECKING STREAM STATUS ===")
            status = driver.execute_script("""
                // Look for stream status indicators
                const results = {
                    streamControls: false,
                    startButton: false,
                    endButton: false
                };

                // Check for stream control panel
                const controls = document.querySelector('[role="main"], #stream-panel, .stream-controls');
                if (controls) results.streamControls = true;

                // Look for Start/End streaming buttons
                document.querySelectorAll('button').forEach(btn => {
                    const text = (btn.textContent || '').toLowerCase();
                    if (text.includes('start streaming')) results.startButton = true;
                    if (text.includes('end stream')) results.endButton = true;
                });

                return results;
            """)
            logger.info(f"  Status: {status}")


if __name__ == "__main__":
    main()
