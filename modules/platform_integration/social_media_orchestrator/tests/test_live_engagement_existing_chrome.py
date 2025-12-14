"""
AUTONOMOUS LIVE ENGAGEMENT TEST - Connects to EXISTING Chrome on 9222
Uses ActionRouter with pre-connected driver (no new Chrome launch)
"""
import asyncio
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root))

from modules.infrastructure.browser_actions.src.action_router import ActionRouter, DriverType
from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

async def test_existing_chrome_engagement():
    print("\n" + "=" * 70)
    print(" AUTONOMOUS LIVE ENGAGEMENT - Existing Chrome on 9222")
    print(" 0102-Driven | Zero Manual Intervention")
    print("=" * 70 + "\n")

    # Step 1: Connect to EXISTING Chrome on 9222
    print("[1] Connecting to existing Chrome on port 9222...")
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    try:
        # Get FoundUps driver connected to existing Chrome
        browser_manager = get_browser_manager()

        # Option A: Use plain Selenium connection (no Gemini Vision, but works)
        driver = webdriver.Chrome(options=chrome_options)
        print(f"[OK] Connected to Chrome")
        print(f"    Current URL: {driver.current_url}")

        # Find Studio tab
        tabs = driver.window_handles
        print(f"\n[2] Found {len(tabs)} tabs - switching to YouTube Studio...")

        for tab in tabs:
            driver.switch_to.window(tab)
            if "studio.youtube.com" in driver.current_url:
                print(f"[OK] Switched to Studio tab")
                break

    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")
        sys.exit(1)

    # Step 2: Pass connected driver to ActionRouter
    print("\n[3] Creating ActionRouter with pre-connected driver...")
    router = ActionRouter(
        profile="youtube_move2japan",
        selenium_driver=driver,  # Pass our existing connection!
        fallback_enabled=False
    )
    print("[OK] ActionRouter initialized with existing Chrome")

    try:
        # Step 3: Execute engagement actions WITHOUT launching new Chrome

        # Like (Thumbs Up)
        print("\n[4] Executing LIKE (Thumbs Up) via Gemini Vision...")
        like_desc = (
            "gray thumbs up icon in the comment action bar, located between the "
            "replies counter and thumbs down icon"
        )
        like_result = await router.execute(
            "click_element",
            {"description": like_desc},
            driver=DriverType.VISION,
        )
        print(f"    Like Result: {like_result.success}")
        await asyncio.sleep(2)

        # Heart (Creator Heart)
        print("\n[5] Executing HEART (Creator Heart) via Gemini Vision...")
        heart_desc = (
            "gray outlined heart icon in the comment action bar, located between "
            "thumbs down and three-dot menu"
        )
        heart_result = await router.execute(
            "click_element",
            {"description": heart_desc},
            driver=DriverType.VISION,
        )
        print(f"    Heart Result: {heart_result.success}")
        await asyncio.sleep(2)

        # Reply
        print("\n[6] Opening REPLY box via Gemini Vision...")
        reply_desc = "Reply button in the comment action bar"
        reply_result = await router.execute(
            "click_element",
            {"description": reply_desc},
            driver=DriverType.VISION,
        )
        print(f"    Reply Result: {reply_result.success}")

        print("\n" + "=" * 70)
        print("[SUCCESS] All engagement actions executed!")
        print("=" * 70)
        print("\nCheck browser - likes/hearts should be visible")

        # Keep browser open
        print("\n[7] Browser staying open for 30 seconds...")
        await asyncio.sleep(30)

    except Exception as e:
        print(f"[ERROR] Engagement failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await router.close()
        driver.quit()
        print("\nTest complete.")

if __name__ == "__main__":
    asyncio.run(test_existing_chrome_engagement())
