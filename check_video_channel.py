#!/usr/bin/env python3
"""
Check which channel a specific video belongs to
"""
import requests
import re

def check_video_channel(video_id):
    """Check which channel a video belongs to"""
    url = f'https://www.youtube.com/watch?v={video_id}'

    print(f"Checking video: {video_id}")
    print(f"URL: {url}")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            print("Successfully fetched video page")

            # Look for channel information in the response
            # Try multiple patterns
            patterns = [
                r'"channelId":"([^"]+)"',
                r'"ownerChannelId":"([^"]+)"',
                r'channel/([^/?]+)',
                r'/@([^/?]+)'
            ]

            channel_info = {}

            for pattern in patterns:
                match = re.search(pattern, response.text)
                if match:
                    found = match.group(1)
                    pattern_name = pattern.split(':')[0].strip('"')
                    channel_info[pattern_name] = found
                    print(f"Found {pattern_name}: {found}")

            if channel_info:
                print("\nChannel information found:")
                for key, value in channel_info.items():
                    print(f"  {key}: {value}")
            else:
                print("No channel information found in page source")

            return channel_info
        else:
            print(f"Failed to fetch video page: HTTP {response.status_code}")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    # Check the specific video mentioned in the logs
    video_id = "nwLAJPmSin0"
    print("=" * 60)
    print(f"VIDEO CHANNEL VERIFICATION: {video_id}")
    print("=" * 60)

    channel_info = check_video_channel(video_id)

    if channel_info:
        print("\nVERIFICATION AGAINST CONFIGURATION:")
        print("-" * 40)

        configured_channels = {
            'Move2Japan': 'UCklMTNnu5POwRmQsg5JJumA',
            'UnDaoDu': 'UC-LSSlOZwpGIRIYihaz8zCw',
            'FoundUps': 'UCSNTUXjAgpd4sgWYP0xoJgw'
        }

        for name, config_id in configured_channels.items():
            if config_id in channel_info.values():
                print(f"MATCH: Video belongs to {name} channel")
                return
            else:
                print(f"NO MATCH: {name} ({config_id})")

        print("\nNo configured channel matches this video!")
    else:
        print("Could not determine video channel ownership")

if __name__ == "__main__":
    main()
