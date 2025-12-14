import asyncio
import sys
import logging
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(repo_root))

from modules.infrastructure.browser_actions.src.action_router import ActionRouter, DriverType

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_integrated_click():
    print("\n" + "="*60)
    print("INTEGRATED GEMINI VISION TEST - ActionRouter")
    print("="*60 + "\n")

    # 1. Initialize Router (uses 'youtube_move2japan' profile)
    print("[1] Initializing ActionRouter...")
    router = ActionRouter(profile='youtube_move2japan')
    
    try:
        # 2. Navigate (Selenium Action)
        url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
        print(f"[2] Navigating to: {url}")
        await router.execute('navigate', {'url': url})
        
        print("[2.5] Waiting for page load (6s)...")
        await asyncio.sleep(6)

        # 3. Execute Vision Action (Gemini Bridge)
        print(f"\n[3] Executing 'click_by_description' via Gemini Vision...")
        description = "CREATOR HEART button (5th element in action bar, outline heart between thumbs down and menu)"
        
        result = await router.execute(
            'click_by_description', 
            {'description': description},
            driver=DriverType.VISION  # Force Vision to test the bridge
        )

        print(f"\n[4] Execution Result:")
        print(f"    Success: {result.success}")
        print(f"    Driver: {result.driver_used}")
        print(f"    Duration: {result.duration_ms}ms")
        
        if result.success:
            print("[PASS] Successfully clicked element via Gemini Vision Bridge!")
        else:
            print(f"[FAIL] Error: {result.error}")

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n[5] Closing router...")
        router.close()

if __name__ == "__main__":
    asyncio.run(test_integrated_click())
