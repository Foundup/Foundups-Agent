#!/usr/bin/env python3
"""
Test that duplicate prevention works and browsers don't open for already-posted content.
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===


import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from modules.platform_integration.social_media_orchestrator.src.simple_posting_orchestrator import SimplePostingOrchestrator
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_duplicate_prevention():
    """Test that already-posted content doesn't open browsers"""

    print("="*80)
    print("TESTING DUPLICATE PREVENTION")
    print("="*80)

    orchestrator = SimplePostingOrchestrator()

    # Test with the current live stream that's already posted to LinkedIn
    video_url = "https://www.youtube.com/watch?v=vAkosSG-zp0"
    video_title = "Test - Already Posted Stream"

    print(f"\nTesting with video that's already posted to LinkedIn...")
    print(f"URL: {video_url}")

    # Check status first
    status = orchestrator.check_if_already_posted('vAkosSG-zp0')
    print(f"\nCurrent status:")
    print(f"  Already posted: {status['already_posted']}")
    print(f"  Platforms: {status['platforms_posted']}")

    print("\nAttempting to post (should skip LinkedIn, try X)...")
    print("-"*50)

    # Try to post - should skip LinkedIn since already posted
    response = await orchestrator.post_stream_notification(
        stream_title=video_title,
        stream_url=video_url
    )

    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)

    print(f"\nResponse summary:")
    print(f"  Success count: {response.success_count}")
    print(f"  Failure count: {response.failure_count}")

    print(f"\nPlatform results:")
    for result in response.results:
        print(f"  {result.platform.value}:")
        print(f"    Success: {result.success}")
        print(f"    Message: {result.message}")

    # Verify LinkedIn was skipped
    linkedin_results = [r for r in response.results if r.platform.value == 'linkedin']
    if linkedin_results:
        linkedin_result = linkedin_results[0]
        if "Already posted" in linkedin_result.message or "already posted" in linkedin_result.message.lower():
            print("\n[OK] SUCCESS: LinkedIn was correctly skipped (already posted)")
        else:
            print("\n[FAIL] FAILURE: LinkedIn was not properly skipped")
    else:
        print("\n[OK] SUCCESS: LinkedIn not in results (was skipped)")

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\nIf a browser opened for LinkedIn, that's a BUG.")
    print("Only X/Twitter browser should have opened (if not already posted).")

if __name__ == "__main__":
    asyncio.run(test_duplicate_prevention())