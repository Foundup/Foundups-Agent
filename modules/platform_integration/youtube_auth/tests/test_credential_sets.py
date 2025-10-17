#!/usr/bin/env python3
"""
Test the YouTube OAuth credential sets configuration.
Verifies that only sets 1 (UnDaoDu) and 10 (Foundups) are configured and working.

WSP Compliant: Testing existing OAuth system per WSP 84
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service, get_credentials_for_index
from modules.platform_integration.youtube_auth.src.quota_monitor import QuotaMonitor, get_available_credential_sets
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_credential_configuration():
    """Test that only sets 1 and 10 are configured"""

    print("="*80)
    print("TESTING YOUTUBE OAUTH CREDENTIAL CONFIGURATION")
    print("="*80)

    # Check available credential sets
    available_sets = get_available_credential_sets()
    print(f"\nDetected credential sets: {available_sets}")

    # Verify only sets 1 and 10
    expected_sets = [1, 10]
    if sorted(available_sets) == sorted(expected_sets):
        print("[SUCCESS] Correct credential sets configured: 1 (UnDaoDu) and 10 (Foundups)")
    else:
        print(f"[WARNING] Expected sets {expected_sets}, but found {available_sets}")

    # Check each set individually
    print("\nChecking credential files:")
    print("-"*50)

    for i in range(1, 11):
        creds = get_credentials_for_index(i)
        if creds:
            client_secrets, token_file = creds
            print(f"Set {i}: CONFIGURED")
            print(f"  Client secrets: {client_secrets}")
            print(f"  Token file: {token_file}")

            # Check if files exist
            if os.path.exists(token_file):
                print(f"  Token status: EXISTS")
            else:
                print(f"  Token status: NOT FOUND (needs authorization)")
        else:
            if i not in [2, 3, 4, 5, 6, 7, 8, 9]:
                print(f"Set {i}: NOT CONFIGURED")

    print("\n" + "="*80)
    print("QUOTA MONITOR CONFIGURATION")
    print("="*80)

    # Test quota monitor
    monitor = QuotaMonitor()

    print(f"\nConfigured quota limits:")
    for set_num, limit in monitor.daily_limits.items():
        set_name = "UnDaoDu" if set_num == 1 else "Foundups" if set_num == 10 else "Unknown"
        print(f"  Set {set_num} ({set_name}): {limit:,} units/day")

    # Get usage summary
    summary = monitor.get_usage_summary()
    print(f"\nTotal daily quota available: {summary['total_available']:,} units")
    print(f"Total quota used today: {summary['total_used']:,} units")

    print("\nPer-set status:")
    for set_num, data in summary['sets'].items():
        set_name = "UnDaoDu" if set_num == 1 else "Foundups"
        print(f"  Set {set_num} ({set_name}):")
        print(f"    Used: {data['used']:,}/{data['limit']:,} ({data['usage_percent']:.1f}%)")
        print(f"    Status: {data['status']}")

    # Test authentication
    print("\n" + "="*80)
    print("TESTING AUTHENTICATION")
    print("="*80)

    print("\nAttempting to get authenticated service...")
    try:
        service = get_authenticated_service()
        if service:
            credential_set = getattr(service, '_credential_set', 'Unknown')
            print(f"[SUCCESS] Authenticated with credential set: {credential_set}")

            # Try a simple API call to verify it works
            try:
                result = service.channels().list(
                    part="snippet",
                    mine=True
                ).execute()

                if 'items' in result and result['items']:
                    channel = result['items'][0]['snippet']
                    print(f"[SUCCESS] API working - Channel: {channel.get('title', 'Unknown')}")
            except Exception as e:
                print(f"[ERROR] API call failed: {e}")
        else:
            print("[ERROR] Failed to get authenticated service")
    except Exception as e:
        print(f"[ERROR] Authentication failed: {e}")

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_credential_configuration()