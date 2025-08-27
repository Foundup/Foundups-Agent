#!/usr/bin/env python
"""
Test .env File API Key Detection
Per WSP 50: Pre-action verification of .env file loading
"""

import os
from pathlib import Path

def load_env_file():
    """Load .env file and test API key detection."""
    print("🔍 Testing .env File API Key Detection")
    print("=" * 50)
    
    # Find .env file
    project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    env_file = project_root / ".env"
    
    print(f"🔍 Looking for .env file: {env_file}")
    
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    print(f"✅ .env file found")
    
    # Load .env file manually
    env_vars = {}
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        
        print(f"✅ Loaded {len(env_vars)} variables from .env")
        
    except Exception as e:
        print(f"❌ Error loading .env: {e}")
        return False
    
    # Test Grok/XAI related variables
    grok_vars = [
        'GROK_API_KEY',
        'XAI_API_KEY',
        'X_API_ACCESS_TOKEN',
        'X_BEARER_TOKEN'
    ]
    
    print(f"\n🔍 Grok/XAI Variables in .env:")
    for var in grok_vars:
        if var in env_vars:
            value = env_vars[var]
            print(f"✅ {var}: FOUND (length: {len(value)})")
            print(f"   Preview: {value[:10]}...")
        else:
            print(f"❌ {var}: NOT FOUND")
    
    # Clarify X vs Grok tokens
    print(f"\n📋 Token Usage Clarification:")
    print(f"  • GROK_API_KEY: For Grok4 API access")
    print(f"  • XAI_API_KEY: Alternative name for Grok4")
    print(f"  • X_API_ACCESS_TOKEN: For X/Twitter API (NOT Grok)")
    print(f"  • X_BEARER_TOKEN: For X/Twitter API (NOT Grok)")
    
    # Test setting environment variables from .env
    print(f"\n🔍 Testing Environment Variable Setting from .env:")
    if 'GROK_API_KEY' in env_vars:
        os.environ['GROK_API_KEY'] = env_vars['GROK_API_KEY']
        print(f"✅ Set GROK_API_KEY from .env")
        
        # Verify it's now available
        test_value = os.getenv('GROK_API_KEY')
        if test_value:
            print(f"✅ GROK_API_KEY now available in environment")
            return True
        else:
            print(f"❌ GROK_API_KEY still not available")
            return False
    else:
        print(f"❌ No GROK_API_KEY found in .env")
        return False

if __name__ == "__main__":
    if load_env_file():
        print(f"\n🎉 .env file loaded successfully!")
        print(f"Run: python src/run_multi_model_campaign.py")
    else:
        print(f"\n⚠️ .env file loading failed or no GROK_API_KEY found")
