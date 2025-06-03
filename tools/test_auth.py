#!/usr/bin/env python3
"""
Simple OAuth Token Test - Verify tokens work

Usage:
    python tools/test_auth.py
"""

import sys
import os
sys.path.append('.')

from modules.infrastructure.oauth_management.oauth_management.src.oauth_manager import get_authenticated_service_with_fallback

def test_authentication():
    """Test if our OAuth tokens work."""
    print("🧪 Testing OAuth authentication...")
    
    try:
        auth_result = get_authenticated_service_with_fallback()
        if auth_result:
            service, credentials, credential_set = auth_result
            print(f"✅ Authentication successful with {credential_set}")
            
            # Test API call
            try:
                response = service.channels().list(part='snippet', mine=True).execute()
                if response.get('items'):
                    channel_title = response['items'][0]['snippet']['title']
                    print(f"✅ API test successful - Channel: {channel_title}")
                    return True
                else:
                    print("⚠️ Authentication works but no channel data returned")
                    return False
            except Exception as api_e:
                print(f"❌ API test failed: {api_e}")
                return False
        else:
            print("❌ Authentication failed completely")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == '__main__':
    success = test_authentication()
    if success:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("💥 Tests failed!")
        sys.exit(1) 