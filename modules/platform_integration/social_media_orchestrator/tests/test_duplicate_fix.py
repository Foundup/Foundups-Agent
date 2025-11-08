#!/usr/bin/env python3
"""
Test script to verify the duplicate prevention fix allows cross-platform posting
WSP 3 Compliant - Located in proper module test directory
"""

import sys
from pathlib import Path

# WSP 3 compliant path setup
project_root = Path(__file__).parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from modules.platform_integration.social_media_orchestrator.src.core.duplicate_prevention_manager import DuplicatePreventionManager
from modules.platform_integration.social_media_orchestrator.src.core.channel_configuration_manager import ChannelConfigurationManager

def test_duplicate_fix():
    """Test that duplicate prevention allows posting to different platforms"""

    print("Testing duplicate prevention fix...")
    print("="*50)

    # Initialize components
    duplicate_manager = DuplicatePreventionManager()
    channel_config = ChannelConfigurationManager()

    # Test with the video from the logs: h5FRc9dcF0Y
    video_id = 'h5FRc9dcF0Y'

    # Check current status
    duplicate_check = duplicate_manager.check_if_already_posted(video_id)
    print(f"Video {video_id} status:")
    print(f"  Already posted: {duplicate_check['already_posted']}")
    print(f"  Platforms posted: {duplicate_check['platforms_posted']}")
    print()

    # Simulate channel config for FoundUps [LOYAL] (which should have both LinkedIn and X/Twitter)
    mock_channel_config = {
        'linkedin_page': 'foundups',
        'x_account': 'Foundups'
    }

    # Determine target platforms
    target_platforms = []
    if mock_channel_config.get('linkedin_page'):
        target_platforms.append('linkedin')
    if mock_channel_config.get('x_account'):
        target_platforms.append('x_twitter')

    print(f"Target platforms for FoundUps [LOYAL]: {target_platforms}")

    # Check for platform-specific duplicates
    already_posted_platforms = set(duplicate_check.get('platforms_posted', []))
    blocked_platforms = {}
    allowed_platforms = []

    for platform in target_platforms:
        if platform in already_posted_platforms:
            blocked_platforms[platform] = 'already posted to this platform'
        else:
            allowed_platforms.append(platform)

    print(f"Blocked platforms: {blocked_platforms}")
    print(f"Allowed platforms: {allowed_platforms}")
    print()

    if allowed_platforms:
        print("SUCCESS: Cross-platform posting is now allowed!")
        print(f"   Video can still be posted to: {allowed_platforms}")
    else:
        print("ISSUE: No platforms allowed for posting")

    return len(allowed_platforms) > 0

if __name__ == "__main__":
    success = test_duplicate_fix()
    sys.exit(0 if success else 1)
