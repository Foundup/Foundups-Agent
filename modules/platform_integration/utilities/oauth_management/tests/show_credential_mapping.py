#!/usr/bin/env python3
"""
Show credential set to YouTube channel mapping.
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===


import os
import sys
import json

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

def show_credential_mapping():
    """Show which credential set maps to which YouTube channel."""
    
    print("[U+1F511] FoundUps Agent - Credential Set Mapping")
    print("=" * 50)
    
    try:
        from utils.oauth_manager import get_authenticated_service
        
        # Test each credential set
        for i in range(4):
            credential_set = f"set_{i+1}"
            print(f"\n[U+1F9EA] Testing {credential_set}...")
            
            try:
                auth_result = get_authenticated_service(i)
                if auth_result:
                    service, creds = auth_result
                    
                    # Get channel information
                    response = service.channels().list(part='snippet', mine=True).execute()
                    items = response.get('items', [])
                    
                    if items:
                        channel_title = items[0]['snippet']['title']
                        channel_id = items[0]['id']
                        print(f"[OK] {credential_set}: {channel_title}")
                        print(f"   Channel ID: {channel_id[:8]}...{channel_id[-4:]}")
                    else:
                        print(f"[FAIL] {credential_set}: No channel found")
                else:
                    print(f"[FAIL] {credential_set}: Authentication failed")
                    
            except FileNotFoundError:
                print(f"[FAIL] {credential_set}: Credential files not found")
            except Exception as e:
                print(f"[FAIL] {credential_set}: Error - {str(e)[:50]}...")
    
    except Exception as e:
        print(f"[FAIL] Failed to load authentication system: {e}")

def show_current_session_info():
    """Show information about the current session."""
    
    print("\n[DATA] Current Session Information")
    print("=" * 50)
    
    # Check environment variables
    forced_set = os.getenv("FORCE_CREDENTIAL_SET")
    if forced_set:
        print(f"[TARGET] FORCED credential set: set_{forced_set}")
    else:
        print("[REFRESH] Using automatic credential rotation")
    
    # Check session cache
    session_cache_file = "memory/session_cache.json"
    if os.path.exists(session_cache_file):
        try:
            with open(session_cache_file, 'r', encoding="utf-8") as f:
                cache = json.load(f)
            
            video_id = cache.get('video_id', 'Unknown')
            stream_title = cache.get('stream_title', 'Unknown')
            timestamp = cache.get('timestamp', 'Unknown')
            
            print(f"[U+1F4BE] Session cache found:")
            print(f"   Video ID: {video_id}")
            print(f"   Stream: {stream_title}")
            print(f"   Cached: {timestamp}")
        except Exception as e:
            print(f"[U+26A0]️ Session cache exists but couldn't read: {e}")
    else:
        print("[U+1F4ED] No session cache found")

if __name__ == "__main__":
    show_credential_mapping()
    show_current_session_info()
    
    print("\n" + "=" * 50)
    print("[IDEA] Tips:")
    print("  - Use FORCE_CREDENTIAL_SET=2 to force set_2 (Move2Japan)")
    print("  - Use FORCE_CREDENTIAL_SET=1 to force set_1 (UnDaoDu)")
    print("  - Remove environment variable for automatic rotation") 