from pathlib import Path
import sys
import os

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)

"""Direct test of UI-TARS protocol matching"""
import asyncio
import logging
from modules.infrastructure.browser_actions.src.action_router import ActionRouter

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

async def test_ui_tars():
    """Test UI-TARS with native protocol."""

    print("\n" + "="*80)
    print(" UI-TARS NATIVE PROTOCOL TEST")
    print("="*80)

    # Create router (will connect to existing Chrome on port 9222)
    router = ActionRouter(profile='youtube_move2japan')

    # Test action: Find a simple element
    print("\n[1] Testing LIKE button detection...")
    result = await router.execute(
        action='like_comment',
        params={'description': 'gray thumbs up icon in the comment action bar'},
        timeout=90,
    )

    print(f"\n[RESULT]")
    print(f"  Success: {result.success}")
    print(f"  Driver: {result.driver_used}")
    print(f"  Duration: {result.duration_ms}ms")
    print(f"  Error: {result.error}")
    if result.result_data:
        print(f"  Coordinates: {result.result_data.get('coordinates')}")
        print(f"  Confidence: {result.result_data.get('confidence')}")

    print("\n" + "="*80)
    print(" TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_ui_tars())
