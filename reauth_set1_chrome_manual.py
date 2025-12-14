#!/usr/bin/env python3
"""
Re-authorization for Set 1 (UnDaoDu) - MANUAL CHROME VERSION
Prevents auto-browser launch so you can paste URL into Chrome manually
"""
import os
import sys

# Add project root
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.chdir(project_root)

print('='*70)
print('Re-authorizing Set 1 (UnDaoDu) - Chrome Manual Mode')
print('='*70)

# Clear old token
token_path = 'credentials/oauth_token.json'
if os.path.exists(token_path):
    os.remove(token_path)
    print('[OK] Cleared expired token\n')

# Set environment
os.environ['GOOGLE_CLIENT_SECRETS_FILE_1'] = 'credentials/client_secret.json'
os.environ['OAUTH_TOKEN_FILE_1'] = token_path

from google_auth_oauthlib.flow import InstalledAppFlow

# Create flow
flow = InstalledAppFlow.from_client_secrets_file(
    'credentials/client_secret.json',
    scopes=['https://www.googleapis.com/auth/youtube.force-ssl',
            'https://www.googleapis.com/auth/youtube.readonly']
)

print('='*70)
print('IMPORTANT: COPY THIS URL AND PASTE INTO **CHROME** (not Edge):')
print('='*70)
print()

# Run with manual browser (prints URL, waits for callback)
try:
    flow.run_local_server(port=0, open_browser=False)

    # Save credentials
    credentials = flow.credentials
    import json
    with open(token_path, 'w') as f:
        f.write(credentials.to_json())

    # Test connection
    from modules.platform_integration.youtube_auth.src.youtube_auth import build
    service = build('youtube', 'v3', credentials=credentials)
    response = service.channels().list(part='snippet', mine=True).execute()

    if response.get('items'):
        channel = response['items'][0]['snippet']['title']
        print()
        print('='*70)
        print(f'[OK] SUCCESS! Set 1 re-authorized!')
        print(f'[CHANNEL] Connected as: {channel}')
        print(f'[SAVE] Token saved to: {token_path}')
        print('[QUOTA] 10,000 quota units available!')
        print('='*70)
    else:
        print('[OK] Authorization successful!')

except Exception as e:
    print(f'\n[X] Error: {e}')
    sys.exit(1)
