"""
Authorize OAuth credential for antifaFM YouTube channel.

IMPORTANT: Before running this script:
1. Open Edge browser
2. Go to youtube.com
3. Click avatar -> Switch account -> Select "antifaFM"
4. Verify you see "antifaFM" in the account switcher

Then run: python modules/platform_integration/youtube_auth/scripts/authorize_antifafm.py
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        pass
# === END UTF-8 ENFORCEMENT ===

import os
import sys
import webbrowser
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# YouTube API scopes
SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/youtube.readonly'
]

# antifaFM channel ID for verification
ANTIFAFM_CHANNEL_ID = "UCVSmg5aOhP4tnQ9KFUg97qA"


def _pick_edge_browser() -> str:
    edge_paths = [
        os.getenv("EDGE_PATH"),
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    for path in edge_paths:
        if path and os.path.exists(path):
            webbrowser.register("edge", None, webbrowser.BackgroundBrowser(path))
            return "edge"
    return None


def verify_channel(youtube_service) -> dict:
    """Verify the authenticated channel is antifaFM."""
    try:
        response = youtube_service.channels().list(
            part="snippet",
            mine=True
        ).execute()

        if response.get("items"):
            channel = response["items"][0]
            channel_id = channel["id"]
            channel_title = channel["snippet"]["title"]
            return {
                "channel_id": channel_id,
                "channel_title": channel_title,
                "is_antifafm": channel_id == ANTIFAFM_CHANNEL_ID
            }
    except Exception as e:
        return {"error": str(e)}
    return {"error": "No channel found"}


def main():
    """Authorize antifaFM credential set."""

    # Use set 10's client secret (same Google Cloud project)
    client_secret_file = 'credentials/client_secret10.json'
    token_file = 'credentials/oauth_token_antifafm.json'

    print("\n" + "=" * 60)
    print("AUTHORIZING ANTIFAFM OAUTH TOKEN")
    print("=" * 60)
    print(f"Client Secret: {client_secret_file}")
    print(f"Token Output: {token_file}")
    print(f"Expected Channel: antifaFM ({ANTIFAFM_CHANNEL_ID})")
    print("=" * 60)

    print("\n*** IMPORTANT ***")
    print("Before continuing, make sure you:")
    print("1. Have Edge browser open")
    print("2. Are logged into YouTube as antifaFM")
    print("   (Click avatar -> Switch account -> antifaFM)")
    print("")
    input("Press Enter when ready to authorize...")

    # Check if client secret exists
    if not os.path.exists(client_secret_file):
        print(f"\n[ERROR] Client secret not found: {client_secret_file}")
        print("Copy your OAuth client secret JSON to this location.")
        return False

    # Try to use Edge browser
    browser_name = _pick_edge_browser()
    if browser_name:
        print(f"\n[INFO] Using Edge browser for OAuth flow")

    # Run OAuth flow
    print("\n[AUTH] Starting OAuth flow...")
    print("[AUTH] A browser window will open. Select the antifaFM account!")

    flow = InstalledAppFlow.from_client_secrets_file(
        client_secret_file,
        scopes=SCOPES
    )

    credentials = flow.run_local_server(
        port=8080,
        prompt='consent',  # Force consent screen to show account selector
        open_browser=True
    )

    # Build service and verify channel
    print("\n[VERIFY] Checking which channel was authorized...")
    youtube = build('youtube', 'v3', credentials=credentials)
    channel_info = verify_channel(youtube)

    if channel_info.get("error"):
        print(f"\n[ERROR] Could not verify channel: {channel_info['error']}")
        return False

    channel_id = channel_info["channel_id"]
    channel_title = channel_info["channel_title"]
    is_antifafm = channel_info["is_antifafm"]

    print(f"\n[RESULT] Authorized channel: {channel_title} ({channel_id})")

    if not is_antifafm:
        print(f"\n[WARNING] This is NOT the antifaFM channel!")
        print(f"  Expected: {ANTIFAFM_CHANNEL_ID}")
        print(f"  Got:      {channel_id}")
        print("\nThe token will NOT be saved.")
        print("Please switch to antifaFM in YouTube and try again.")
        return False

    # Save credentials
    print(f"\n[SUCCESS] Verified antifaFM channel!")
    print(f"[SAVE] Saving token to: {token_file}")

    token_data = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
        # Metadata for verification
        '_channel_id': channel_id,
        '_channel_title': channel_title,
    }

    with open(token_file, 'w') as f:
        json.dump(token_data, f, indent=2)

    print(f"\n[DONE] antifaFM OAuth token saved!")
    print(f"\nNext steps:")
    print(f"1. Add to .env: ANTIFAFM_YOUTUBE_TOKEN_FILE=credentials/oauth_token_antifafm.json")
    print(f"2. Or copy to: credentials/oauth_token9.json and set ANTIFAFM_YOUTUBE_TOKEN_SET=9")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
