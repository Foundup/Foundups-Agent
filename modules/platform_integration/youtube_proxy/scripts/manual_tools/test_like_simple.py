"""
Simple test: Just LIKE comments using Gemini Vision
No 012 feedback - just try to click
"""
from pathlib import Path
import sys
import os

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)

import asyncio
import sys
from pathlib import Path

repo_root = REPO_ROOT

from modules.infrastructure.browser_actions.src.action_router import ActionRouter, DriverType
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

async def test_simple_like():
    print("\n" + "="*80)
    print(" SIMPLE LIKE TEST - GEMINI VISION + SELENIUM")
    print("="*80)

    # 1. Connect to existing Chrome
    print("\n[1] Connecting to Chrome on port 9222...")
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        print(f"[OK] Connected to Chrome")
        print(f"    URL: {driver.current_url[:100]}")

        # Find Studio tab
        tabs = driver.window_handles
        print(f"\n[2] Found {len(tabs)} tabs...")
        for tab in tabs:
            driver.switch_to.window(tab)
            if "studio.youtube.com" in driver.current_url:
                print(f"[OK] Switched to Studio tab")
                break

    except Exception as e:
        print(f"[ERROR] Cannot connect: {e}")
        return

    # 2. Create ActionRouter with Gemini Vision
    print("\n[3] Creating ActionRouter with Gemini Vision...")
    router = ActionRouter(
        profile="youtube_move2japan",
        selenium_driver=driver,
        fallback_enabled=True,
        feedback_mode=False  # NO 012 feedback
    )
    print("[OK] Router ready")

    # 3. Try different descriptions for LIKE button
    descriptions = [
        "thumbs up button",
        "like button",
        "gray thumbs up icon in the comment toolbar",
        "thumbs up icon next to reply count",
    ]

    print("\n[4] Testing different descriptions for LIKE button...")
    print("="*80)

    for i, desc in enumerate(descriptions, 1):
        print(f"\n[Test {i}/4] Description: '{desc}'")
        print("-"*80)

        try:
            result = await router.execute(
                "click_element",
                {"description": desc},
                driver=DriverType.VISION,
                timeout=30,
            )

            print(f"  Success: {result.success}")
            print(f"  Driver used: {result.driver_used}")
            print(f"  Duration: {result.duration_ms}ms")
            if result.error:
                print(f"  Error: {result.error[:100]}")
            if result.result_data:
                print(f"  Confidence: {result.result_data.get('confidence', 'N/A')}")
                print(f"  Tier: {result.result_data.get('tier', 'N/A')}")

            if result.success:
                print(f"\n  SUCCESS! This description worked: '{desc}'")
                break

        except Exception as e:
            print(f"  Exception: {e}")

        # Pause between attempts
        if i < len(descriptions):
            print("  Waiting 3s before next attempt...")
            await asyncio.sleep(3)

    print("\n" + "="*80)
    print(" TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_simple_like())
