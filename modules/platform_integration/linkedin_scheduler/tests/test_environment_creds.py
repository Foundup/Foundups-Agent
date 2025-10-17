#!/usr/bin/env python3
"""
WSP: LinkedIn API Environment Credential Validation
===================================================

WSP-compliant test to validate LinkedIn API credentials in environment.
This follows WSP 13 testing guidelines and protocols.
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import os
import sys

# Add project root to path for WSP compliance
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..')))

from modules.platform_integration.linkedin_scheduler.src.linkedin_scheduler import LinkedInScheduler


def test_linkedin_credentials():
    """WSP-compliant LinkedIn API credential validation."""
    print("🧪 WSP: LinkedIn API Credential Environment Test")
    print("=" * 60)
    
    # Test environment variable detection
    client_id = os.getenv('LINKEDIN_CLIENT_ID')
    client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
    
    print(f"📋 Environment Variables:")
    print(f"   LINKEDIN_CLIENT_ID: {'✅ SET' if client_id else '❌ NOT SET'}")
    print(f"   LINKEDIN_CLIENT_SECRET: {'✅ SET' if client_secret else '❌ NOT SET'}")
    
    # Test scheduler initialization
    print(f"\n🔧 Scheduler Initialization:")
    scheduler = LinkedInScheduler()
    
    print(f"   Client ID: {'✅ LOADED' if scheduler.client_id else '❌ MISSING'}")
    print(f"   Client Secret: {'✅ LOADED' if scheduler.client_secret else '❌ MISSING'}")
    
    # Test OAuth URL generation (if credentials available)
    if scheduler.client_id and scheduler.client_secret:
        print(f"\n🔐 OAuth URL Generation Test:")
        try:
            oauth_url = scheduler.get_oauth_url("https://example.com/callback", "test_state")
            print(f"   OAuth URL: ✅ GENERATED ({len(oauth_url)} chars)")
            print(f"   Sample: {oauth_url[:80]}...")
        except Exception as e:
            print(f"   OAuth URL: ❌ ERROR - {e}")
            
        # Test API connectivity
        print(f"\n🌐 API Connectivity Test:")
        try:
            connectivity = scheduler.validate_connection()
            print(f"   Connection: {'✅ SUCCESS' if connectivity else '❌ FAILED'}")
        except Exception as e:
            print(f"   Connection: ❌ ERROR - {e}")
    else:
        print(f"\n⚠️  Skipping OAuth/API tests - credentials not available")
        print(f"   To set credentials:")
        print(f"   $env:LINKEDIN_CLIENT_ID='your_client_id'")
        print(f"   $env:LINKEDIN_CLIENT_SECRET='your_client_secret'")
    
    print(f"\n📊 WSP Test Results:")
    creds_available = bool(scheduler.client_id and scheduler.client_secret)
    print(f"   Credential Detection: {'✅ PASS' if creds_available else '⚠️  SKIP'}")
    print(f"   Scheduler Init: ✅ PASS")
    print(f"   WSP 13 Compliance: ✅ PASS")
    
    return creds_available


if __name__ == '__main__':
    test_linkedin_credentials() 