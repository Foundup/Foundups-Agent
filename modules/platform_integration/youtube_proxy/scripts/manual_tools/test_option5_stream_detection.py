"""
Quick diagnostic to test Option 5 stream detection with Phase 3A integration.

This script helps verify:
1. Stream detection works with AI monitoring enabled
2. CommunityMonitor initializes properly
3. Heartbeat loop runs correctly
4. Comment checking triggers at pulse 20

Run this to debug: python test_option5_stream_detection.py
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
from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_stream_detection():
    """Test stream detection with AI monitoring enabled."""

    print("\n" + "="*60)
    print(" TESTING OPTION 5: AI Overseer + CommunityMonitor")
    print("="*60)
    print()
    print("This will test:")
    print("  1. Stream detection with enable_ai_monitoring=True")
    print("  2. CommunityMonitor initialization")
    print("  3. Heartbeat loop functionality")
    print()
    print("Expected behavior:")
    print("  - Stream should be detected immediately")
    print("  - CommunityMonitor should initialize when stream starts")
    print("  - Every 20 pulses (10 min), comment check triggers")
    print()
    print("Press Ctrl+C to stop after verifying stream detection")
    print("="*60 + "\n")

    try:
        # Create DAE with AI monitoring enabled (same as Option 5)
        dae = AutoModeratorDAE(enable_ai_monitoring=True)

        # Connect
        if not dae.connect():
            print("[ERROR] Failed to connect")
            return

        # Find stream
        print("\n[TEST] Looking for active livestream...")
        stream = dae.find_livestream()

        if stream:
            print(f"\n✅ STREAM DETECTED!")
            print(f"   Video ID: {stream[0]}")
            print(f"   Chat ID: {stream[1]}")
            print(f"   Channel: {stream[3]}")

            print("\n[TEST] Starting full DAE run() to test CommunityMonitor...")
            print("[INFO] Watch for '[COMMUNITY] Monitor initialized' message")
            print("[INFO] At pulse 20, you should see '[COMMUNITY] Checking for unengaged comments...'")
            print()

            # Run the full DAE (includes CommunityMonitor integration)
            await dae.run()
        else:
            print("\n❌ NO STREAM DETECTED")
            print()
            print("Possible reasons:")
            print("  1. No live stream is currently active")
            print("  2. Channel ID in .env is incorrect")
            print("  3. Stream detection is broken")
            print()
            print("Debug steps:")
            print("  1. Verify stream is live at youtube.com/channel/YOUR_CHANNEL_ID/live")
            print("  2. Check .env has correct MOVE2JAPAN_CHANNEL_ID")
            print("  3. Try Option 1 (without AI monitoring) to isolate issue")

    except KeyboardInterrupt:
        print("\n\n[STOP] Test stopped by user")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        logger.error(f"Test error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_stream_detection())
