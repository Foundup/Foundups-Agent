#!/usr/bin/env python
"""
Test CLAUDE_API_KEY Detection
Per WSP 50: Pre-action verification of Claude API key
"""

import os
from pathlib import Path

def test_claude_key():
    """Test CLAUDE_API_KEY detection."""
    print("🧪 Testing CLAUDE_API_KEY Detection")
    print("=" * 40)
    
    # Test all possible Claude environment variables
    claude_vars = [
        'CLAUDE_API_KEY',
        'ANTHROPIC_API_KEY',
        'CLAUDE_API',
        'ANTHROPIC_API'
    ]
    
    print(f"\n🔍 Claude Environment Variables:")
    for var in claude_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: FOUND (length: {len(value)})")
            print(f"   Preview: {value[:10]}...")
        else:
            print(f"❌ {var}: NOT FOUND")
    
    # Test the exact detection logic from multi-model runner
    print(f"\n🔍 Multi-Model Detection Logic:")
    
    api_key_env = {
        'anthropic': 'ANTHROPIC_API_KEY',
        'xai': 'GROK_API_KEY',
        'google': 'GEMINI_API_KEY',
        'openai': 'OPENAI_API_KEY'
    }
    
    for provider, env_key in api_key_env.items():
        value = os.getenv(env_key)
        if value:
            print(f"✅ {provider} ({env_key}): AVAILABLE")
        else:
            print(f"❌ {provider} ({env_key}): NOT AVAILABLE")
    
    # Test if we need to update the detection logic
    claude_key = os.getenv('CLAUDE_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    print(f"\n🔍 Claude Key Analysis:")
    if claude_key and not anthropic_key:
        print(f"✅ CLAUDE_API_KEY found but ANTHROPIC_API_KEY missing")
        print(f"⚠️ Multi-model runner needs update to detect CLAUDE_API_KEY")
        return True
    elif anthropic_key:
        print(f"✅ ANTHROPIC_API_KEY found - multi-model runner will work")
        return True
    else:
        print(f"❌ No Claude API key found")
        return False

if __name__ == "__main__":
    if test_claude_key():
        print(f"\n🎉 Claude API key detected!")
        print(f"Run: python src/run_multi_model_campaign.py")
    else:
        print(f"\n⚠️ No Claude API key found")
