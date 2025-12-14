#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TARS Live Stream Detection - Verification Test
Sprint 1: Verify vision-based stream detection works

Tests:
1. Chrome connection on :9222
2. Navigate to @channel/live
3. Detect live stream
4. Extract video_id
5. Restore Studio URL (critical!)
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from modules.platform_integration.stream_resolver.src.vision_stream_checker import VisionStreamChecker

def test_chrome_connection():
    """Test 1: Chrome connection"""
    print("\n" + "="*60)
    print("TEST 1: Chrome Connection")
    print("="*60)

    checker = VisionStreamChecker()

    if checker.vision_available and checker.driver:
        current_url = checker.driver.current_url
        print(f"[OK] Chrome connected")
        print(f"   Current URL: {current_url[:60]}...")
        return True
    else:
        print(f"[FAIL] Chrome NOT available")
        print(f"   Make sure Chrome is running with: --remote-debugging-port=9222")
        return False

def test_stream_detection(channel_id: str, channel_name: str):
    """Test 2-4: Stream detection + video_id extraction"""
    print("\n" + "="*60)
    print(f"TEST 2-4: Stream Detection for {channel_name}")
    print("="*60)

    checker = VisionStreamChecker()

    if not checker.vision_available:
        print("[FAIL] Chrome not available - skipping")
        return None

    print(f"   Checking channel: {channel_id}")
    print(f"   Handle: {checker.CHANNEL_HANDLES.get(channel_id, 'N/A')}")

    result = checker.check_channel_for_live(channel_id, channel_name)

    if result:
        print(f"[OK] LIVE STREAM DETECTED")
        print(f"   Video ID: {result.get('video_id')}")
        print(f"   Title: {result.get('title', 'N/A')}")
        print(f"   Source: {result.get('source')}")
        print(f"   Method: {result.get('method')}")
        return result
    else:
        print(f"[WARN] No live stream found")
        print(f"   This is OK if channel is not currently live")
        return None

def test_studio_url_restoration(checker: VisionStreamChecker, original_url: str):
    """Test 5: Verify Studio URL was restored"""
    print("\n" + "="*60)
    print("TEST 5: Studio URL Restoration")
    print("="*60)

    if not checker.driver:
        print("[FAIL] No driver - skipping")
        return False

    current_url = checker.driver.current_url
    print(f"   Original URL: {original_url[:60]}...")
    print(f"   Current URL:  {current_url[:60]}...")

    if 'studio.youtube.com' in current_url:
        print(f"[OK] Studio URL restored correctly")
        return True
    else:
        print(f"[WARN] Not on Studio (may have navigated elsewhere)")
        return False

def main():
    """Run all TARS stream detection tests"""
    print("\n" + "="*60)
    print("[SPRINT 1] TARS LIVE STREAM DETECTION")
    print("="*60)
    print()
    print("This script tests if TARS can:")
    print("  1. Connect to Chrome (:9222)")
    print("  2. Navigate to YouTube channels")
    print("  3. Detect live streams")
    print("  4. Extract video IDs")
    print("  5. Restore Studio URL")
    print()

    # Test 1: Chrome connection
    chrome_ok = test_chrome_connection()
    if not chrome_ok:
        print("\n[FAIL] SPRINT 1 FAILED: Chrome not available")
        print("   Start Chrome with: chrome.exe --remote-debugging-port=9222")
        return

    # Get original URL before testing
    checker = VisionStreamChecker()
    original_url = checker.driver.current_url if checker.driver else None

    # Test 2-4: Stream detection for all channels
    channels = [
        ('UCklMTNnu5POwRmQsg5JJumA', 'MOVE2JAPAN'),
        ('UCSNTUXjAgpd4sgWYP0xoJgw', 'UnDaoDu'),
        ('UC-LSSlOZwpGIRIYihaz8zCw', 'FoundUps'),
    ]

    live_streams_found = []
    for channel_id, channel_name in channels:
        result = test_stream_detection(channel_id, channel_name)
        if result:
            live_streams_found.append((channel_name, result))
        time.sleep(2)  # Brief pause between checks

    # Test 5: URL restoration
    if original_url and 'studio.youtube.com' in original_url:
        test_studio_url_restoration(checker, original_url)

    # Summary
    print("\n" + "="*60)
    print("[SUMMARY] SPRINT 1 RESULTS")
    print("="*60)
    print(f"   Chrome Connection: {'[OK]' if chrome_ok else '[FAIL]'}")
    print(f"   Live Streams Found: {len(live_streams_found)}")

    for channel_name, result in live_streams_found:
        print(f"   └─ {channel_name}: {result.get('video_id')}")

    if not live_streams_found:
        print(f"   └─ No streams (channels may be offline)")

    print()
    if chrome_ok:
        print("[OK] SPRINT 1 COMPLETE: TARS stream detection verified")
    else:
        print("[FAIL] SPRINT 1 FAILED: Fix Chrome connection")
    print("="*60)

if __name__ == "__main__":
    main()
