#!/usr/bin/env python3

from modules.platform_integration.stream_resolver.src.no_quota_stream_checker import NoQuotaStreamChecker

def main():
    checker = NoQuotaStreamChecker()

    channels = [
        ('UC-LSSlOZwpGIRIYihaz8zCw', 'UnDaoDu'),
        ('UCSNTUXjAgpd4sgWYP0xoJgw', 'FoundUps'),
        ('UCklMTNnu5POwRmQsg5JJumA', 'Move2Japan')
    ]

    print("🔍 Checking for live streams on 3 channels:")
    print("=" * 50)

    for channel_id, name in channels:
        print(f'📺 Checking {name} ({channel_id[:12]}...)')
        try:
            result = checker.check_channel_for_live(channel_id, name)
            if result and result.get('live'):
                title = result.get('title', 'Unknown Title')
                print(f'  ✅ LIVE: {title}')
            else:
                print(f'  ❌ Not live')
        except Exception as e:
            print(f'  ⚠️ Error: {e}')
        print()

if __name__ == "__main__":
    main()
