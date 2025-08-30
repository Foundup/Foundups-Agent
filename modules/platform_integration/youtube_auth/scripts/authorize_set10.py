"""
Authorize OAuth credential set 10 for YouTube API
Run this directly: python authorize_set10.py
"""

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
    """Authorize set 10"""
    
    client_secret_file = 'credentials/client_secret10.json'
    token_file = 'credentials/oauth_token10.json'
    
    print("\n" + "="*60)
    print("AUTHORIZING SET 10")
    print("="*60)
    print(f"Client Secret: {client_secret_file}")
    print(f"Token Output: {token_file}")
    
    # Check if client secret exists
    if not os.path.exists(client_secret_file):
        print(f"\n❌ ERROR: Client secret not found!")
        print(f"   Expected location: {os.path.abspath(client_secret_file)}")
        print("\nPlease ensure client_secret10.json is in the credentials/ folder")
        return False
    
    print(f"\n✅ Found client secret file")
    
    try:
        # Run OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
        
        print("\n🌐 Opening browser for authorization...")
        print("   Port: 8090")
        print("\n⚠️ IMPORTANT: Use a DIFFERENT Google account than sets 1-9")
        print("   This gives you an additional 10,000 API units per day")
        
        creds = flow.run_local_server(port=8090)
        
        # Save the credentials
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
        
        print(f"\n✅ Successfully authorized Set 10!")
        print(f"💾 Token saved to: {token_file}")
        
        # Test the credentials
        print("\n🔍 Testing credentials...")
        service = build('youtube', 'v3', credentials=creds)
        response = service.channels().list(part='snippet', mine=True).execute()
        if response.get('items'):
            channel = response['items'][0]['snippet']['title']
            print(f"✨ Authenticated as channel: {channel}")
        
        print("\n" + "="*60)
        print("SUCCESS! Set 10 is ready to use")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to authorize: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)