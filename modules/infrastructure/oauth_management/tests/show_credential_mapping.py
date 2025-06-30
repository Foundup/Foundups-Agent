#!/usr/bin/env python3
"""
Show credential set to YouTube channel mapping.
"""

import os
import sys
import json

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

def show_credential_mapping():
    """Show which credential set maps to which YouTube channel."""
    
    print("🔑 FoundUps Agent - Credential Set Mapping")
    print("=" * 50)
    
    try:
        from utils.oauth_manager import get_authenticated_service
        
        # Test each credential set
        for i in range(4):
            credential_set = f"set_{i+1}"
            print(f"\n🧪 Testing {credential_set}...")
            
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
                        print(f"✅ {credential_set}: {channel_title}")
                        print(f"   Channel ID: {channel_id[:8]}...{channel_id[-4:]}")
                    else:
                        print(f"❌ {credential_set}: No channel found")
                else:
                    print(f"❌ {credential_set}: Authentication failed")
                    
            except FileNotFoundError:
                print(f"❌ {credential_set}: Credential files not found")
            except Exception as e:
                print(f"❌ {credential_set}: Error - {str(e)[:50]}...")
    
    except Exception as e:
        print(f"❌ Failed to load authentication system: {e}")

def show_current_session_info():
    """Show information about the current session."""
    
    print("\n📊 Current Session Information")
    print("=" * 50)
    
    # Check environment variables
    forced_set = os.getenv("FORCE_CREDENTIAL_SET")
    if forced_set:
        print(f"🎯 FORCED credential set: set_{forced_set}")
    else:
        print("🔄 Using automatic credential rotation")
    
    # Check session cache
    session_cache_file = "memory/session_cache.json"
    if os.path.exists(session_cache_file):
        try:
            with open(session_cache_file, 'r') as f:
                cache = json.load(f)
            
            video_id = cache.get('video_id', 'Unknown')
            stream_title = cache.get('stream_title', 'Unknown')
            timestamp = cache.get('timestamp', 'Unknown')
            
            print(f"💾 Session cache found:")
            print(f"   Video ID: {video_id}")
            print(f"   Stream: {stream_title}")
            print(f"   Cached: {timestamp}")
        except Exception as e:
            print(f"⚠️ Session cache exists but couldn't read: {e}")
    else:
        print("📭 No session cache found")

if __name__ == "__main__":
    show_credential_mapping()
    show_current_session_info()
    
    print("\n" + "=" * 50)
    print("💡 Tips:")
    print("  - Use FORCE_CREDENTIAL_SET=2 to force set_2 (Move2Japan)")
    print("  - Use FORCE_CREDENTIAL_SET=1 to force set_1 (UnDaoDu)")
    print("  - Remove environment variable for automatic rotation") 