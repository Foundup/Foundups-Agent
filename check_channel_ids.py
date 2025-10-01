#!/usr/bin/env python3
"""
Check YouTube channel IDs for @MOVE2JAPAN and @UnDaoDu
"""
import requests
import re

def check_channel_id(handle):
    """Check channel ID for a given handle"""
    url = f'https://www.youtube.com/@{handle}'

    print(f"Checking channel ID for @{handle}...")
    print(f"URL: {url}")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            print("Successfully fetched channel page")

            # Look for channel ID in the response
            match = re.search(r'"channelId":"([^"]+)"', response.text)
            if match:
                channel_id = match.group(1)
                print(f"Found channel ID: {channel_id}")
                return channel_id
            else:
                print("Could not find channelId in page source")
                return None
        else:
            print(f"Failed to fetch channel page: HTTP {response.status_code}")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("=" * 60)
    print("YOUTUBE CHANNEL ID VERIFICATION")
    print("=" * 60)

    # Check both channels
    channels = ['MOVE2JAPAN', 'UnDaoDu']
    results = {}

    for handle in channels:
        print(f"\n{'='*40}")
        channel_id = check_channel_id(handle)
        results[handle] = channel_id
        print(f"{'='*40}")

    print(f"\n{'='*60}")
    print("SUMMARY:")
    print(f"{'='*60}")

    for handle, channel_id in results.items():
        if channel_id:
            print(f"{handle:12}: {channel_id}")
        else:
            print(f"{handle:12}: NOT FOUND")

    # Check current configuration
    print("\nCURRENT CONFIGURATION:")
    print("-" * 30)
    configured = {
        'Move2Japan': 'UCklMTNnu5POwRmQsg5JJumA',
        'UnDaoDu': 'UC-LSSlOZwpGIRIYihaz8zCw',
        'FoundUps': 'UCSNTUXjAgpd4sgWYP0xoJgw'
    }

    for name, config_id in configured.items():
        actual_id = None
        for handle, found_id in results.items():
            if found_id == config_id:
                actual_id = found_id
                break

        status = "MATCH" if actual_id else "NOT FOUND"
        print(f"{name:12}: {config_id} [{status}]")

if __name__ == "__main__":
    main()