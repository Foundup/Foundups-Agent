#!/usr/bin/env python
"""
Test Grok4 API Key Setup
Per WSP 50: Pre-action verification after environment setup
"""

import os

def test_grok_setup():
    """Test if Grok4 API key is properly set."""
    print("🧪 Testing Grok4 API Key Setup")
    print("=" * 40)
    
    grok_key = os.getenv('GROK_API_KEY')
    xai_key = os.getenv('XAI_API_KEY')
    
    if grok_key:
        print(f"✅ GROK_API_KEY: FOUND (length: {len(grok_key)})")
        print(f"   Preview: {grok_key[:10]}...")
        return True
    elif xai_key:
        print(f"✅ XAI_API_KEY: FOUND (length: {len(xai_key)})")
        print(f"   Preview: {xai_key[:10]}...")
        return True
    else:
        print("❌ No Grok/XAI API key found")
        print("\nTo set the API key:")
        print("  PowerShell: $env:GROK_API_KEY = 'your_key_here'")
        print("  Or create .env file with: GROK_API_KEY=your_key_here")
        return False

if __name__ == "__main__":
    if test_grok_setup():
        print("\n🎉 Grok4 API key is ready!")
        print("Run: python src/run_multi_model_campaign.py")
    else:
        print("\n⚠️ Please set GROK_API_KEY and try again")
