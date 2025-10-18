#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io

"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

Simple OAuth Token Test - Verify tokens work

Usage:
    python tools/test_auth.py
"""

import sys
import os
sys.path.append('.')

from modules.infrastructure.oauth_management.src.oauth_manager import get_authenticated_service_with_fallback

def test_authentication():
    """Test if our OAuth tokens work."""
    print("[U+1F9EA] Testing OAuth authentication...")
    
    try:
        auth_result = get_authenticated_service_with_fallback()
        if auth_result:
            service, credentials, credential_set = auth_result
            print(f"[OK] Authentication successful with {credential_set}")
            
            # Test API call
            try:
                response = service.channels().list(part='snippet', mine=True).execute()
                if response.get('items'):
                    channel_title = response['items'][0]['snippet']['title']
                    print(f"[OK] API test successful - Channel: {channel_title}")
                    return True
                else:
                    print("[U+26A0]️ Authentication works but no channel data returned")
                    return False
            except Exception as api_e:
                print(f"[FAIL] API test failed: {api_e}")
                return False
        else:
            print("[FAIL] Authentication failed completely")
            return False
            
    except Exception as e:
        print(f"[FAIL] Test failed: {e}")
        return False

if __name__ == '__main__':
    success = test_authentication()
    if success:
        print("[CELEBRATE] All tests passed!")
        sys.exit(0)
    else:
        print("[U+1F4A5] Tests failed!")
        sys.exit(1) 