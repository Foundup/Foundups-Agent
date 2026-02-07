#!/usr/bin/env python3
import sys
sys.path.append('.')
from modules.platform_integration.stream_resolver.src.stream_resolver import StreamResolver

# Test the channel mapping fix
resolver = StreamResolver(None)  # No service to test mapping only

test_channels = {
    'UCSNTUXjAgpd4sgWYP0xoJgw': 'FoundUps',
    'UC-LSSlOZwpGIRIYihaz8zCw': 'Move2Japan',
    'UCklMTNnu5POwRmQsg5JJumA': 'Move2Japan'
}

print('Channel Mapping Verification:')
print('=' * 40)
for channel_id, expected in test_channels.items():
    display_name = resolver._get_channel_display_name(channel_id)
    status = 'OK' if expected in display_name else 'ERROR'
    # Remove emojis for clean output
    clean_name = display_name.encode('ascii', 'ignore').decode('ascii')
    print(f'{status}: {channel_id[:12]}... -> {clean_name}')
