"""
Authorize OAuth credential set 8 for YouTube API
Run this directly: python authorize_set8.py
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# YouTube API scopes
SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/youtube.readonly'
]

def main():
    """Authorize set 8"""
    
    client_secret_file = 'credentials/client_secret8.json'
    token_file = 'credentials/oauth_token8.json'
    
    print("\n" + "="*60)
    print("AUTHORIZING SET 8")
    print("="*60)
    print(f"Client Secret: {client_secret_file}")
    print(f"Token Output: {token_file}")
    
    # Check if client secret exists
    if not os.path.exists(client_secret_file):
        print(f"\n❌ ERROR: Client secret not found!")
        print(f"   Expected location: {os.path.abspath(client_secret_file)}")
        print("\nPlease ensure client_secret8.json is in the credentials/ folder")
        return False
    
    print(f"\n✅ Found client secret file")
    
    try:
        # Run OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
        
        print("\n🌐 Opening browser for authorization...")
        print("   Port: 8088")
        print("\n⚠️ IMPORTANT: Use a DIFFERENT Google account than sets 1-7")
        print("   This gives you an additional 10,000 API units per day")
        
        creds = flow.run_local_server(port=8088)
        
        # Save the credentials
        with open(token_file, 'w', encoding="utf-8") as token:
            token.write(creds.to_json())
        
        print(f"\n✅ Successfully authorized Set 8!")
        print(f"💾 Token saved to: {token_file}")
        
        # Test the credentials
        print("\n🔍 Testing credentials...")
        service = build('youtube', 'v3', credentials=creds)
        response = service.channels().list(part='snippet', mine=True).execute()
        if response.get('items'):
            channel = response['items'][0]['snippet']['title']
            print(f"✨ Authenticated as channel: {channel}")
        
        print("\n" + "="*60)
        print("SUCCESS! Set 8 is ready to use")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to authorize: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)