"""
Authorize OAuth credential set 2 for YouTube API
USE THIS FOR MOVE2JAPAN CHANNEL

Run this directly: python authorize_set2.py
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
    """Authorize set 2 for Move2Japan channel"""

    client_secret_file = 'credentials/client_secret.json'
    token_file = 'credentials/oauth_token2.json'

    print("\n" + "="*60)
    print("AUTHORIZING SET 2 - MOVE2JAPAN CHANNEL")
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
        print(f"   Port: 8081")
        print(f"\n[U+26A0]️  IMPORTANT: Log in with MOVE2JAPAN Google account")
        print(f"   NOT the UnDaoDu account!")
        print(f"   This will give access to Move2Japan YouTube channel")

        # Run local server on port 8081 for Set 2 (different from Set 1's 8080)
        credentials = flow.run_local_server(port=8081)

        # Save the credentials
        with open(token_file, 'w', encoding="utf-8") as token:
            token.write(credentials.to_json())

        print(f"\n[OK] Successfully authorized Set 2!")
        print(f"[U+1F4BE] Token saved to: {token_file}")

        # Test the credentials
        print(f"\n[SEARCH] Testing credentials...")
        service = build('youtube', 'v3', credentials=credentials)
        request = service.channels().list(part='snippet', mine=True)
        response = request.execute()

        if 'items' in response and len(response['items']) > 0:
            channel_title = response['items'][0]['snippet']['title']
            channel_id = response['items'][0]['id']
            print(f"[OK] Successfully connected to channel: {channel_title}")
            print(f"   Channel ID: {channel_id}")

            # Verify it's Move2Japan
            if "move2japan" in channel_title.lower() or "move 2 japan" in channel_title.lower():
                print(f"\n[CELEBRATE] CORRECT! This is the Move2Japan channel!")
            else:
                print(f"\n[U+26A0]️  WARNING: Channel name is '{channel_title}', not Move2Japan")
                print(f"   Did you log in with the wrong account?")

            return True
        else:
            print(f"[U+26A0]️ Connected but no channel found. This is normal for some accounts.")
            return True

    except Exception as e:
        print(f"[FAIL] Failed to authorize: {e}")
        return False

if __name__ == '__main__':
    print("\n" + "="*60)
    print("[U+1F3AC] MOVE2JAPAN CHANNEL AUTHORIZATION")
    print("="*60)
    print("\nThis will create Set 2 credentials for the Move2Japan channel.")
    print("Make sure you log in with the MOVE2JAPAN Google account!")
    print()

    success = main()

    if success:
        print(f"\n[CELEBRATE] Set 2 (Move2Japan) authorization complete!")
        print(f"\nNext steps:")
        print(f"  1. YouTube uploader will now use Move2Japan channel")
        print(f"  2. All Shorts will post to Move2Japan")
        print(f"  3. Test with: python modules/communication/youtube_shorts/tests/upload_test_video.py")
    else:
        print(f"\n[U+1F4A5] Set 2 authorization failed!")
        sys.exit(1)
