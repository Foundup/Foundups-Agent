#!/usr/bin/env python3
"""
Test script for stream_resolver.py
Validates idle detection, quota handling, and credential rotation.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from utils.logging_config import setup_logging
from modules.stream_resolver.src.stream_resolver import (
    get_active_livestream_video_id,
    calculate_dynamic_delay,
    search_livestreams,
    check_video_details
)
from modules.stream_resolver.src.stream_resolver import FORCE_DEV_DELAY
from utils.oauth_manager import get_authenticated_service_with_fallback

# Disable dev delay for realistic testing
FORCE_DEV_DELAY = False

def test_dynamic_delay():
    """Test delay calculation with various scenarios."""
    print("\nTesting dynamic delay calculation:")
    
    # Test with no previous delay
    delay = calculate_dynamic_delay()
    print(f"Initial delay: {delay:.1f}s")
    
    # Test with consecutive failures
    for i in range(1, 6):
        delay = calculate_dynamic_delay(consecutive_failures=i)
        print(f"Delay with {i} consecutive failures: {delay:.1f}s")
    
    # Test with different user counts
    for users in [0, 10, 100, 1000]:
        delay = calculate_dynamic_delay(active_users=users)
        print(f"Delay with {users} active users: {delay:.1f}s")

def test_stream_resolver():
    """Test main stream resolver functionality."""
    print("\nTesting stream resolver:")
    
    # Get authenticated service
    service = get_authenticated_service_with_fallback()
    if not service:
        print("❌ Failed to get authenticated service")
        return
    
    print("✅ Successfully authenticated")
    
    # Get channel ID from environment
    channel_id = os.getenv("CHANNEL_ID")
    if not channel_id:
        print("❌ CHANNEL_ID not set in environment")
        return
    
    print(f"Using channel ID: {channel_id}")
    
    # Test video ID override
    video_id = os.getenv("YOUTUBE_VIDEO_ID")
    if video_id:
        print(f"\nTesting with YOUTUBE_VIDEO_ID override: {video_id}")
        result = check_video_details(service, video_id)
        if result:
            print("✅ Successfully verified video details")
        else:
            print("❌ Failed to verify video details")
    
    # Test livestream search
    print("\nSearching for active livestreams...")
    result = search_livestreams(service, event_type="live")
    if result:
        print(f"✅ Found active livestream: {result}")
    else:
        print("ℹ️ No active livestream found")
    
    # Test upcoming streams
    print("\nSearching for upcoming streams...")
    result = search_livestreams(service, event_type="upcoming")
    if result:
        print(f"✅ Found upcoming stream: {result}")
    else:
        print("ℹ️ No upcoming streams found")
    
    # Test main function
    print("\nTesting get_active_livestream_video_id...")
    result = get_active_livestream_video_id(service, channel_id)
    if result:
        video_id, chat_id = result
        print(f"✅ Found stream: Video ID: {video_id}, Chat ID: {chat_id}")
    else:
        print("ℹ️ No active stream found")

def main():
    """Main test runner."""
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    setup_logging()
    
    print("Starting stream resolver tests...")
    
    # Run tests
    test_dynamic_delay()
    test_stream_resolver()
    
    print("\nTest suite completed.")

if __name__ == "__main__":
    main() 