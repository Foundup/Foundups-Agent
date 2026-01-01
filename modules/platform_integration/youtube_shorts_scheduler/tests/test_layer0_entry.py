#!/usr/bin/env python3
"""
Layer 0: Entry - Select first unlisted video from list.

Test Modes:
    --visual: Use browser subagent for visual validation (slow, reliable)
    --selenium: Use pure Selenium DOM automation (fast, requires verified selectors)

Usage:
    python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer0_entry
    python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer0_entry --selenium
"""

import argparse
import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))


def test_layer0_selenium():
    """Test Layer 0 with pure Selenium."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    print("\n[L0] Layer 0: Entry - Selenium Mode")
    print("=" * 60)

    # Connect to Chrome
    chrome_port = int(os.getenv("CHROME_PORT", "9222"))
    channel_id = os.getenv("CHANNEL_ID", "UC-LSSlOZwpGIRIYihaz8zCw")

    print(f"[CONNECT] Chrome port {chrome_port}")

    options = Options()
    options.add_experimental_option("debuggerAddress", f"localhost:{chrome_port}")

    try:
        driver = webdriver.Chrome(options=options)
        print(f"[OK] Connected to Chrome: {driver.title[:50]}...")
    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")
        print("[TIP] Start Chrome with: chrome.exe --remote-debugging-port=9222")
        return False

    # Navigate to unlisted shorts
    filter_param = '[{"name":"VISIBILITY","value":["UNLISTED"]}]'
    from urllib.parse import quote
    url = f"https://studio.youtube.com/channel/{channel_id}/videos/short?filter={quote(filter_param)}"

    print(f"[NAV] Navigating to unlisted shorts...")
    driver.get(url)
    time.sleep(3)

    # Wait for video rows
    try:
        rows = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ytcp-video-row"))
        )
        print(f"[OK] Found {len(rows)} unlisted videos")
    except Exception as e:
        print(f"[ERROR] No video rows found: {e}")
        return False

    # Click first video to open edit page
    try:
        first_video_link = rows[0].find_element(By.CSS_SELECTOR, "a[href*='/edit']")
        video_id = first_video_link.get_attribute("href").split("/video/")[1].split("/")[0]
        print(f"[CLICK] First video: {video_id}")

        first_video_link.click()
        time.sleep(2)

        # Verify we're on edit page
        if "/edit" in driver.current_url:
            print(f"[SUCCESS] Layer 0 complete! On edit page: {driver.current_url}")
            return True
        else:
            print(f"[ERROR] Not on edit page: {driver.current_url}")
            return False

    except Exception as e:
        print(f"[ERROR] Failed to click video: {e}")
        return False


def test_layer0_info():
    """Just show layer info without running."""
    print("\n[L0] Layer 0: Entry")
    print("=" * 60)
    print("Purpose: Navigate to unlisted shorts, select first video")
    print("")
    print("DOM Selectors:")
    print("  - URL Filter: ?filter=[{\"name\":\"VISIBILITY\",\"value\":[\"UNLISTED\"]}]")
    print("  - Video Rows: ytcp-video-row")
    print("  - Edit Link: a[href*='/edit']")
    print("")
    print("Validation:")
    print("  - Video row count > 0")
    print("  - URL contains /edit after click")
    print("")
    print("Usage:")
    print("  python -m ...test_layer0_entry --selenium")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Layer 0: Entry Test")
    parser.add_argument("--selenium", action="store_true", help="Run with pure Selenium")
    parser.add_argument("--info", action="store_true", help="Show layer info only")

    args = parser.parse_args()

    if args.info:
        test_layer0_info()
    elif args.selenium:
        success = test_layer0_selenium()
        sys.exit(0 if success else 1)
    else:
        test_layer0_info()
        print("\n[TIP] Add --selenium to run the test")
