#!/usr/bin/env python3
"""
Test the duplicate posting prevention system.
This verifies that the orchestrator correctly checks the database
before attempting to post to social media.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from modules.platform_integration.social_media_orchestrator.src.simple_posting_orchestrator import SimplePostingOrchestrator
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_duplicate_check():
    """Test the duplicate prevention check system"""

    print("="*80)
    print("TESTING DUPLICATE POSTING PREVENTION SYSTEM")
    print("="*80)

    # Initialize orchestrator
    orchestrator = SimplePostingOrchestrator()

    # Test videos
    test_videos = [
        ("vAkosSG-zp0", "Current live stream (should be posted)"),
        ("riWxmxOozVA", "Previous stream (should be posted)"),
        ("NEW_VIDEO_123", "New video (not posted)")
    ]

    print("\nChecking posting status for test videos:")
    print("-"*50)

    for video_id, description in test_videos:
        print(f"\n[VIDEO] {video_id}")
        print(f"   Description: {description}")

        # Check if already posted
        status = orchestrator.check_if_already_posted(video_id)

        if status['already_posted']:
            print(f"   [POSTED] YES - Already posted")
            print(f"   Platforms: {status['platforms_posted']}")
            print(f"   Time: {status['timestamp']}")
        else:
            print(f"   [POSTED] NO - Not posted yet")

    print("\n" + "="*80)
    print("DATABASE CHECK COMPLETE")
    print("="*80)

    # Show database statistics
    print(f"\nTotal streams in database: {len(orchestrator.posted_streams)}")
    print("\nAll posted streams:")
    for vid_id, info in orchestrator.posted_streams.items():
        platforms = info.get('platforms_posted', [])
        title = info.get('title', 'Unknown')[:50]
        print(f"  • {vid_id}: {platforms} - {title}...")

if __name__ == "__main__":
    test_duplicate_check()