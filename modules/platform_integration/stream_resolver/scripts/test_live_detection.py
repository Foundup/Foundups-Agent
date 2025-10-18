#!/usr/bin/env python3
"""
Standalone YouTube Live Stream Detection Test
WSP-compliant: Tests stream detection before integration
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


import requests
import re
import json
from typing import Dict, Optional, Any

def test_live_detection(channel_handle: str = "@MOVE2JAPAN") -> Dict[str, Any]:
    """
    Test if a YouTube channel has a live stream.

    Args:
        channel_handle: YouTube channel handle (e.g., @MOVE2JAPAN)

    Returns:
        Dict with live stream info if found
    """
    results = {
        "channel": channel_handle,
        "live_url_tested": f"https://www.youtube.com/{channel_handle}/live",
        "checks": {},
        "video_found": None,
        "is_live": False
    }

    # Step 1: Get the /live page
    url = f"https://www.youtube.com/{channel_handle}/live"
    print(f"\n[SEARCH] Testing: {url}")
    print("="*60)

    try:
        response = requests.get(url, timeout=10)
        results["checks"]["status_code"] = response.status_code
        results["checks"]["final_url"] = response.url

        print(f"[OK] Status Code: {response.status_code}")
        print(f"[OK] Final URL: {response.url}")

        # Step 2: Check for redirect to video
        if "/watch?v=" in response.url:
            video_id = response.url.split("v=")[1].split("&")[0]
            print(f"[OK] Redirected to video: {video_id}")
            results["video_found"] = video_id
            results["is_live"] = True

        # Step 3: Check page content for live indicators
        content = response.text

        # Check various live indicators
        indicators = {
            "isLiveNow": '"isLiveNow":true' in content,
            "LIVE_badge": 'BADGE_STYLE_TYPE_LIVE_NOW' in content,
            "watching_now": 'watching now' in content,
            "LIVE_text": '>LIVE<' in content or '"text":"LIVE"' in content,
            "liveStreamability": '"liveStreamability"' in content
        }

        results["checks"]["indicators"] = indicators

        print("\n[INFO] Live Indicators Found:")
        for key, value in indicators.items():
            print(f"  - {key}: {value}")

        # Step 4: Extract video IDs if not redirected
        if not results["video_found"]:
            video_ids = re.findall(r'"videoId":"([^"]+)"', content)
            if video_ids:
                print(f"\n[VIDEO] Found {len(video_ids)} video IDs in page")
                print(f"  - First video ID: {video_ids[0]}")

                # If we have live indicators, use the first video ID
                if any(indicators.values()):
                    results["video_found"] = video_ids[0]
                    results["is_live"] = True

        # Step 5: Verify the video is actually live
        if results["video_found"]:
            print(f"\n[VERIFY] Verifying video {results['video_found']} is live...")
            video_url = f"https://www.youtube.com/watch?v={results['video_found']}"
            video_response = requests.get(video_url, timeout=10)

            video_is_live = '"isLiveNow":true' in video_response.text
            print(f"  - Video isLiveNow: {video_is_live}")

            if video_is_live:
                # Extract title if possible
                title_match = re.search(r'"title":"([^"]+)"', video_response.text)
                if title_match:
                    results["title"] = title_match.group(1)
                    print(f"  - Title: {results['title']}")

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        results["error"] = str(e)

    # Final summary
    print("\n" + "="*60)
    if results["is_live"]:
        print(f"[SUCCESS] LIVE STREAM DETECTED!")
        print(f"  - Video ID: {results['video_found']}")
        print(f"  - URL: https://www.youtube.com/watch?v={results['video_found']}")
    else:
        print("[FAIL] No live stream found")

    return results


def test_direct_video(video_id: str = "vAkosSG-zp0") -> Dict[str, Any]:
    """
    Test if a specific video is live.

    Args:
        video_id: YouTube video ID

    Returns:
        Dict with video status
    """
    results = {
        "video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "is_live": False,
        "indicators": {}
    }

    print(f"\n[VIDEO] Testing video: {video_id}")
    print("="*60)

    try:
        response = requests.get(results["url"], timeout=10)
        content = response.text

        # Check live indicators
        results["indicators"] = {
            "isLiveNow": '"isLiveNow":true' in content,
            "watching_now": 'watching now' in content,
            "liveStreamability": '"liveStreamability"' in content,
            "LIVE_badge": 'BADGE_STYLE_TYPE_LIVE_NOW' in content
        }

        results["is_live"] = results["indicators"]["isLiveNow"]

        print("[STATUS] Video Status:")
        for key, value in results["indicators"].items():
            print(f"  - {key}: {value}")

        # Extract title
        title_match = re.search(r'"title":"([^"]+)"', content)
        if title_match:
            results["title"] = title_match.group(1)
            print(f"  - Title: {results['title']}")

        print("\n" + "="*60)
        if results["is_live"]:
            print("[SUCCESS] VIDEO IS LIVE!")
        else:
            print("[FAIL] Video is not live")

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        results["error"] = str(e)

    return results


def main():
    """Run all tests"""
    print("YouTube Live Stream Detection Test")
    print("="*80)

    # Test 1: Check @MOVE2JAPAN channel
    channel_result = test_live_detection("@MOVE2JAPAN")

    # Test 2: Check specific video
    if channel_result.get("video_found"):
        video_result = test_direct_video(channel_result["video_found"])
    else:
        # Test with known video ID
        video_result = test_direct_video("vAkosSG-zp0")

    # Summary
    print("\n" + "="*80)
    print("FINAL RESULTS:")
    print(f"  - Channel has live: {channel_result['is_live']}")
    if channel_result.get("video_found"):
        print(f"  - Live video ID: {channel_result['video_found']}")
        print(f"  - Stream URL: https://www.youtube.com/watch?v={channel_result['video_found']}")

    # Save results for debugging
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "channel": channel_result,
            "video": video_result
        }, f, indent=2)
    print("\n[SAVED] Results saved to test_results.json")


if __name__ == "__main__":
    main()