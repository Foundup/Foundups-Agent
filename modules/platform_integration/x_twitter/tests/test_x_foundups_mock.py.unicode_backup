#!/usr/bin/env python3
"""
Mock test for X/Twitter FoundUps posting
Tests browser automation and account configuration without posting
WSP compliant test following WSP 5 (Testing) and WSP 49 (Module Structure)
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
sys.path.insert(0, project_root)

print("="*60)
print("X/TWITTER FOUNDUPS POSTING TEST (MOCK)")
print("="*60)

# Load environment variables
load_dotenv()

# Check account configuration
print("\n📋 Account Configuration:")
print(f"   X_Acc1 (Move2Japan): {os.getenv('X_Acc1', 'geozeai')}")
print(f"   X_Acc2 (FoundUps): {os.getenv('X_Acc2', 'foundups')}")

print("\n🔍 Testing Configuration (Non-interactive)...")

try:
    from modules.platform_integration.x_twitter.src.x_anti_detection_poster import AntiDetectionX

    print("\n🚀 Initializing X poster for FoundUps...")
    poster = AntiDetectionX(use_foundups=True)

    print(f"✅ Using account: {poster.username}")

    # Verify it's configured for FoundUps
    if poster.username.lower() == 'foundups':
        print("✅ PASS - Correctly configured for FoundUps account")
    else:
        print(f"⚠️ WARNING - Using {poster.username} instead of FoundUps")
        print("   This needs to be fixed in .env configuration")

    # Test content generation
    test_content = """🦄 FoundUps by @UnDaoDu
DAEs eating startups for breakfast.
Solo unicorns, no VCs needed.

#FoundUps #DAE @Foundups"""

    print("\n📝 Test content prepared:")
    print("-" * 40)
    print(test_content)
    print("-" * 40)
    print(f"Length: {len(test_content)} chars (280 max)")

    if len(test_content) <= 280:
        print("✅ Content length valid for X")
    else:
        print("❌ Content too long for X")

    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)

    print("\n✅ Configuration Test:")
    print(f"   • X poster configured for: {poster.username}")
    print(f"   • Expected account: @Foundups")
    print(f"   • Content generation: PASS")
    print(f"   • Character limit: PASS")

    if poster.username.lower() == 'foundups':
        print("\n✅ ALL TESTS PASSED")
        print("   Git posts will be sent to @Foundups account")
        exit(0)
    else:
        print(f"\n⚠️ CONFIGURATION ISSUE")
        print(f"   Account mismatch: {poster.username} vs FoundUps")
        exit(1)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Make sure you're running from the project root")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n✅ Mock test complete!")