"""
Test UI-TARS Desktop - YouTube Studio Heart Button
Uses Tier 1 Vision (most precise)
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.infrastructure.foundups_vision.src.ui_tars_bridge import UITarsBridge
from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager

async def test_ui_tars_heart():
    print("\n" + "="*60)
    print("UI-TARS - YouTube Studio Heart Button Test")
    print("="*60 + "\n")

    # Step 1: Get browser (reuse existing session)
    print("[1] Connecting to browser...")
    browser_manager = get_browser_manager()
    browser = browser_manager.get_browser(
        browser_type='chrome',
        profile_name='youtube_move2japan'
    )

    # Step 2: Navigate to Studio
    url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
    print(f"[2] Navigating to: {url}")
    browser.get(url)
    await asyncio.sleep(6)

    # Step 3: Connect to UI-TARS
    print(f"[3] Connecting to UI-TARS (port 9222)...")
    ui_tars = UITarsBridge()
    connected = await ui_tars.connect()

    if not connected:
        print(f"[ERROR] UI-TARS connection failed!")
        return

    print(f"[OK] UI-TARS connected!")

    # Step 4: Use UI-TARS to click heart button
    print(f"\n[4] Using UI-TARS Vision to find and click HEART button...")
    print(f"    Description: Gray outlined heart icon in comment action bar")
    print(f"    Position: Between thumbs down and three-dot menu")

    result = await ui_tars.click(
        description="gray outlined heart icon in the comment action bar, located between thumbs down and three-dot menu",
        context={"page": "YouTube Studio comments", "target": "creator heart button"}
    )

    # Step 5: Check result
    print(f"\n[5] UI-TARS Result:")
    print(f"    Success: {result.success}")
    print(f"    Action: {result.action}")
    print(f"    Description: {result.description}")
    print(f"    Duration: {result.duration_ms}ms")
    print(f"    Confidence: {result.confidence}")

    if result.error:
        print(f"    Error: {result.error}")

    if result.screenshot_before:
        print(f"    Screenshot Before: {result.screenshot_before}")
    if result.screenshot_after:
        print(f"    Screenshot After: {result.screenshot_after}")

    # Step 6: Verify heart turned red
    print(f"\n[6] Verification:")
    if result.success:
        print(f"    ✓ UI-TARS successfully clicked the element")
        print(f"    → Check if heart button is now RED ❤️")
        await asyncio.sleep(3)
    else:
        print(f"    ✗ UI-TARS could not complete the action")

    print(f"\n[DONE] Browser staying open for verification.")
    input("Press Enter to exit...")

if __name__ == "__main__":
    asyncio.run(test_ui_tars_heart())
