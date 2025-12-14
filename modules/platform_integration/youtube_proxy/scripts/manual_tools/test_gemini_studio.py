"""
Test Gemini Vision on YouTube Studio Comments
Goal: Find and click Like buttons on actual comments
"""
from pathlib import Path
import sys
import os

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)

import asyncio
import logging
from modules.infrastructure.foundups_selenium.src.foundups_driver import FoundUpsDriver
from modules.infrastructure.foundups_vision.src.gemini_vision_bridge import GeminiVisionBridge

logging.basicConfig(level=logging.INFO)

async def test_gemini_on_studio():
    """Test Gemini Vision finding Like buttons on YouTube Studio."""

    print("\n" + "="*80)
    print(" GEMINI VISION - YOUTUBE STUDIO LIKE BUTTONS")
    print("="*80)

    # 1. Connect to existing Chrome
    print("\n[1] Connecting to Chrome on port 9222...")
    driver = FoundUpsDriver(port=9222)
    print(f"    URL: {driver.current_url[:100]}")

    # 2. Initialize Gemini Vision
    print("\n[2] Initializing Gemini Vision Bridge...")
    bridge = GeminiVisionBridge(driver, feedback_mode=False)
    await bridge.connect()
    print("    Gemini Vision ready")

    # 3. First, let Gemini describe what it sees
    print("\n[3] Asking Gemini to describe the page...")
    print("="*80)

    from modules.infrastructure.foundups_vision.src.ui_tars_bridge import ActionResult

    # Test different descriptions to see which works
    test_descriptions = [
        "thumbs up button",
        "like icon",
        "action button with thumbs up",
        "gray button in comment toolbar",
    ]

    for desc in test_descriptions:
        print(f"\n[TESTING] '{desc}'")
        print("-"*80)

        try:
            result = await bridge.execute_action(
                action='click',
                description=desc,
                context={'test': True},
                timeout=30,
            )

            print(f"  Success: {result.success}")
            print(f"  Duration: {result.duration_ms}ms")
            print(f"  Confidence: {result.confidence}")
            if result.error:
                print(f"  Error: {result.error[:100]}")
            if result.metadata:
                coords = result.metadata.get('coordinates', {})
                print(f"  Coordinates: {coords}")

        except Exception as e:
            print(f"  Exception: {e}")

    print("\n" + "="*80)
    print(" GEMINI VISION TEST COMPLETE")
    print("="*80)
    print("\nNow let's try with a more specific description based on what works...")

if __name__ == "__main__":
    asyncio.run(test_gemini_on_studio())
