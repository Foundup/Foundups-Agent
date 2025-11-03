"""
Authorize OAuth credential set 1 for YouTube API
Run this directly: python authorize_set1.py
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
    """Authorize set 1"""
    
    client_secret_file = 'credentials/client_secret.json'
    token_file = 'credentials/oauth_token.json'
    
    print("\n" + "="*60)
    print("AUTHORIZING SET 1")
    print("="*60)
    print(f"Client Secret: {client_secret_file}")
    print(f"Token Output: {token_file}")
    
    # Check if client secret exists
    if not os.path.exists(client_secret_file):
        print(f"[FAIL] Client secret file not found: {client_secret_file}")
        return False
    
    print(f"\n[OK] Found client secret file")
    
    try:
        # Run the OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secret_file, SCOPES)
        
        print(f"\n[U+1F310] Opening browser for authorization...")
        print(f"   Port: 8080")
        print(f"\n[U+26A0]️ IMPORTANT: Use the FoundUps Google account")
        print(f"   This gives you access to FoundUps YouTube API quota")
        
        # Run local server on port 8080 for Set 1
        credentials = flow.run_local_server(port=8080)
        
        # Save the credentials
        with open(token_file, 'w', encoding="utf-8") as token:
            token.write(credentials.to_json())
        
        print(f"\n[OK] Successfully authorized Set 1!")
        print(f"[U+1F4BE] Token saved to: {token_file}")
        
        # Test the credentials
        print(f"\n[SEARCH] Testing credentials...")
        service = build('youtube', 'v3', credentials=credentials)
        request = service.channels().list(part='snippet', mine=True)
        response = request.execute()
        
        if 'items' in response and len(response['items']) > 0:
            channel_title = response['items'][0]['snippet']['title']
            print(f"[OK] Successfully connected to channel: {channel_title}")
            return True
        else:
            print(f"[U+26A0]️ Connected but no channel found. This is normal for some accounts.")
            return True
            
    except Exception as e:
        print(f"[FAIL] Failed to authorize: {e}")
        return False

if __name__ == '__main__':
    success = main()
    if success:
        print(f"\n[CELEBRATE] Set 1 authorization complete!")
    else:
        print(f"\n[U+1F4A5] Set 1 authorization failed!")
        sys.exit(1)