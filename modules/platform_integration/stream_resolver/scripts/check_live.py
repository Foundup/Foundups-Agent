
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

#!/usr/bin/env python3

from modules.platform_integration.stream_resolver.src.no_quota_stream_checker import NoQuotaStreamChecker

def main():
    checker = NoQuotaStreamChecker()

    channels = [
        ('UC-LSSlOZwpGIRIYihaz8zCw', 'UnDaoDu'),
        ('UCSNTUXjAgpd4sgWYP0xoJgw', 'FoundUps'),
        ('UCklMTNnu5POwRmQsg5JJumA', 'Move2Japan')
    ]

    print("[SEARCH] Checking for live streams on 3 channels:")
    print("=" * 50)

    for channel_id, name in channels:
        print(f'[U+1F4FA] Checking {name} ({channel_id[:12]}...)')
        try:
            result = checker.check_channel_for_live(channel_id, name)
            if result and result.get('live'):
                title = result.get('title', 'Unknown Title')
                print(f'  [OK] LIVE: {title}')
            else:
                print(f'  [FAIL] Not live')
        except Exception as e:
            print(f'  [U+26A0]️ Error: {e}')
        print()

if __name__ == "__main__":
    main()
