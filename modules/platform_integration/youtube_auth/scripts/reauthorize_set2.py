#!/usr/bin/env python3
"""
Re-authorization script for Set 2 credentials
Fixes expired/revoked tokens
"""

import os
import sys
import json

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, project_root)
os.chdir(project_root)  # Change to project root for relative paths

print('Re-authorizing Set 2 credentials...')
print('=' * 50)

# Check that client_secret2.json exists
client_secret_path = 'credentials/client_secret2.json'
if os.path.exists(client_secret_path):
    with open(client_secret_path, 'r') as f:
        secret_data = json.load(f)
        if 'installed' in secret_data:
            print('[OK] Desktop app credentials detected')
        elif 'web' in secret_data:
            print('[!] Web Application credentials detected (may have issues)')
        else:
            print('[X] Unknown credential type!')
            sys.exit(1)
else:
    print(f'[X] ERROR: {client_secret_path} not found!')
    print('Please ensure you have the Google Cloud credentials for Set 2')
    sys.exit(1)

# Clear the expired token
token_path = 'credentials/oauth_token2.json'
if os.path.exists(token_path):
    os.remove(token_path)
    print('[OK] Cleared expired token')
else:
    print('[i] No existing token found')

# Force Set 2 credentials
os.environ['GOOGLE_CLIENT_SECRETS_FILE_1'] = client_secret_path
os.environ['OAUTH_TOKEN_FILE_1'] = token_path
os.environ['YOUTUBE_SCOPES'] = 'https://www.googleapis.com/auth/youtube.force-ssl https://www.googleapis.com/auth/youtube.readonly'

print()
print('[BROWSER] Browser will open for authorization...')
print('[ACTION] Sign in with the Google account and authorize the app')
print()

from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service

try:
    # This will trigger OAuth flow with new credentials
    # Using index 0 since we override the env vars to point to set 2
    service = get_authenticated_service(0)
    
    # Test the service
    response = service.channels().list(part='snippet', mine=True).execute()
    
    if response.get('items'):
        channel = response['items'][0]['snippet']['title']
        print()
        print('[OK] SUCCESS! Set 2 re-authorized!')
        print(f'[TV] Connected as: {channel}')
        print(f'[SAVE] Token saved to: {token_path}')
        print('[QUOTA] 10,000 quota units now available for Set 2!')
        print()
        print('The bot will now be able to use Set 2 in rotation!')
    else:
        print('[OK] Service authorized successfully!')
        print(f'[SAVE] Token saved to: {token_path}')
        
except Exception as e:
    print(f'[X] Error: {e}')
    print()
    if 'invalid_client' in str(e):
        print('The client_secret2.json file might be invalid.')
        print('Please download it again from Google Cloud Console')
    elif 'access_denied' in str(e):
        print('Make sure your email is added as a test user in the OAuth consent screen')
    elif 'redirect_uri_mismatch' in str(e):
        print('This is a Web Application credential - consider switching to Desktop app type')
        print('Desktop app credentials work better for local development')
    else:
        print('Try these steps:')
        print('1. Clear browser cache/cookies for accounts.google.com')
        print('2. Use incognito/private browser window')
        print('3. Check that credentials are valid in Google Cloud Console')
        print('4. Ensure OAuth consent screen is configured properly')