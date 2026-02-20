#!/usr/bin/env python3
"""
Selenium Navigation Test - Visual Browser Operations

This test demonstrates visible browser navigation for 012 to observe.
Uses Chrome (port 9222) to navigate YouTube and show video operations.

What 012 Should See:
1. Chrome browser opens to YouTube
2. Navigates to UnDaoDu channel
3. Scrolls through videos (visible scrolling)
4. Clicks on oldest video
5. Video starts playing
6. Browser shows video info

Prerequisites:
    Chrome must be running with remote debugging:
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" ^
        --remote-debugging-port=9222 ^
        --user-data-dir="%LOCALAPPDATA%\\Google\\Chrome\\User Data"

Usage:
    python modules/ai_intelligence/video_indexer/tests/test_selenium_navigation.py
"""

import time
from datetime import datetime


def visible_selenium_demo():
    """
    Run visible Selenium browser operations.

    012 will see:
    - Browser window navigate
    - Pages loading
    - Scrolling
    - Video playing
    """
    print("\n" + "=" * 70)
    print("  SELENIUM VISIBLE NAVIGATION DEMO")
    print("  Watch Chrome browser - it will navigate visibly!")
    print("=" * 70)
    print(f"  Started: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 70)

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        print("[ERROR] Selenium not installed: pip install selenium")
        return False

    # Connect to Chrome
    print("\n[STEP 1] Connecting to Chrome on port 9222...")
    try:
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=options)
        print(f"[OK] Connected - Current page: {driver.title[:50]}...")
    except Exception as e:
        print(f"[ERROR] Could not connect to Chrome: {e}")
        print("\n[TIP] Start Chrome with:")
        print('  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" ^')
        print('      --remote-debugging-port=9222 ^')
        print('      --user-data-dir="%LOCALAPPDATA%\\Google\\Chrome\\User Data"')
        return False

    # Step 2: Navigate to YouTube
    print("\n[STEP 2] Navigating to YouTube... (WATCH THE BROWSER)")
    driver.get("https://www.youtube.com")
    time.sleep(2)
    print(f"[OK] Now at: {driver.title}")

    # Step 3: Navigate to UnDaoDu channel
    print("\n[STEP 3] Navigating to UnDaoDu channel... (WATCH THE BROWSER)")
    undaodu_url = "https://www.youtube.com/@undaodu/videos"
    driver.get(undaodu_url)
    time.sleep(3)
    print(f"[OK] Now at: {driver.title}")

    # Step 4: Scroll down to load more videos (VISIBLE SCROLLING)
    print("\n[STEP 4] Scrolling through videos... (WATCH THE BROWSER SCROLL)")
    for i in range(3):
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(0.8)
        print(f"  Scrolling... {i + 1}/3")

    print("[OK] Scrolled through video list")

    # Step 5: Navigate to oldest video (2009)
    print("\n[STEP 5] Navigating to oldest video (2009)... (WATCH THE BROWSER)")
    oldest_video_id = "8_DUQaqY6Tc"
    oldest_video_url = f"https://www.youtube.com/watch?v={oldest_video_id}"
    driver.get(oldest_video_url)
    time.sleep(3)
    print(f"[OK] Video loaded: {driver.title}")

    # Step 6: Show video info
    print("\n[STEP 6] Extracting video info...")
    try:
        # Try to get video title
        title_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.ytd-watch-metadata, h1.title"))
        )
        video_title = title_element.text
        print(f"  Title: {video_title[:60]}...")
    except:
        print("  Title: (could not extract)")

    # Get video ID from URL
    current_url = driver.current_url
    if "v=" in current_url:
        vid_id = current_url.split("v=")[1].split("&")[0]
        print(f"  Video ID: {vid_id}")

    # Step 7: Scroll comments section (VISIBLE)
    print("\n[STEP 7] Scrolling to comments... (WATCH THE BROWSER)")
    driver.execute_script("window.scrollBy(0, 600);")
    time.sleep(2)
    print("[OK] Scrolled to comments section")

    print("\n" + "=" * 70)
    print("  SELENIUM DEMO COMPLETE")
    print("=" * 70)
    print(f"  Browser is now showing: {driver.title[:50]}...")
    print(f"  Video ID: {oldest_video_id}")
    print(f"  Completed: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 70)
    print("\n[OK] 012 should have seen all browser navigation!")

    return True


def run_with_ui_tars():
    """
    Run with UI-TARS integration if available.

    UI-TARS provides vision-based browser automation.
    """
    print("\n[CHECK] Looking for UI-TARS integration...")

    try:
        from modules.infrastructure.foundups_vision.src.ui_tars_bridge import UITARSBridge
        print("[OK] UI-TARS bridge found")

        # Note: UI-TARS integration would go here
        # For now, we use standard Selenium which is sufficient

    except ImportError:
        print("[INFO] UI-TARS not available, using standard Selenium")

    return visible_selenium_demo()


if __name__ == "__main__":
    # Run the visible demo
    success = run_with_ui_tars()

    if success:
        print("\n[SUCCESS] Browser navigation demo completed")
        print("[INFO] 012 should have observed visible browser operations")
    else:
        print("\n[FAILED] Browser navigation demo failed")
        print("[TIP] Ensure Chrome is running with remote debugging")
