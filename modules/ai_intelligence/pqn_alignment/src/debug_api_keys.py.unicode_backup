#!/usr/bin/env python
"""
Debug Script for API Key Detection
Per WSP 50: Pre-action verification of environment variables
Per WSP 84: Uses existing detection patterns

Troubleshoots Grok4 API key detection issue
"""

import os
import sys
from pathlib import Path

def debug_api_key_detection():
    """Debug API key detection for all models."""
    print("🔍 API Key Detection Debug")
    print("=" * 50)
    
    # Test all possible Grok/XAI environment variables
    grok_vars = [
        'GROK_API_KEY',
        'XAI_API_KEY', 
        'GROK_API',
        'XAI_API',
        'GROK_KEY',
        'XAI_KEY'
    ]
    
    print("\n🔍 Testing Grok/XAI Environment Variables:")
    for var in grok_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: FOUND (length: {len(value)})")
            # Show first few characters for verification
            print(f"   Preview: {value[:10]}...")
        else:
            print(f"❌ {var}: NOT FOUND")
    
    # Test all model API keys
    all_api_keys = {
        'ANTHROPIC_API_KEY': 'Claude',
        'OPENAI_API_KEY': 'GPT',
        'GEMINI_API_KEY': 'Gemini',
        'GROK_API_KEY': 'Grok',
        'XAI_API_KEY': 'XAI'
    }
    
    print(f"\n🔍 All Model API Keys:")
    for var, model in all_api_keys.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var} ({model}): FOUND")
        else:
            print(f"❌ {var} ({model}): NOT FOUND")
    
    # Test the exact detection logic from multi-model runner
    print(f"\n🔍 Testing Multi-Model Detection Logic:")
    
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
    
    # Test campaign config loading
    print(f"\n🔍 Testing Campaign Config Loading:")
    try:
        config_path = Path(__file__).parent.parent / "campaigns" / "campaign_3_entrainment.yml"
        if config_path.exists():
            print(f"✅ Config file exists: {config_path}")
            
            # Try to load and parse
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            models = config.get('models', [])
            print(f"✅ Config loaded successfully with {len(models)} models")
            
            print(f"\n🔍 Models in Config:")
            for model in models:
                name = model.get('name', 'Unknown')
                api = model.get('api', 'Unknown')
                print(f"  - {name} (API: {api})")
                
        else:
            print(f"❌ Config file not found: {config_path}")
    except Exception as e:
        print(f"❌ Error loading config: {e}")
    
    # Test environment variable setting
    print(f"\n🔍 Testing Environment Variable Setting:")
    test_var = "TEST_GROK_DEBUG"
    os.environ[test_var] = "test_value"
    retrieved = os.getenv(test_var)
    if retrieved == "test_value":
        print(f"✅ Environment variable setting works")
    else:
        print(f"❌ Environment variable setting failed")
    
    # Clean up test variable
    if test_var in os.environ:
        del os.environ[test_var]

if __name__ == "__main__":
    debug_api_key_detection()
