#!/usr/bin/env python3
"""
Fresh authorization for Set 5 with new Desktop app credentials
"""

import os
import sys
import json

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print('Authorizing Set 5 with NEW Desktop app credentials...')
print('=' * 50)

# Check that the new client_secret5.json exists and is Desktop type
client_secret_path = 'credentials/client_secret5.json'
if os.path.exists(client_secret_path):
    with open(client_secret_path, 'r') as f:
        secret_data = json.load(f)
        if 'installed' in secret_data:
            print('OK: Desktop app credentials detected')
        else:
            print('ERROR: This is still a Web Application type!')
            print('Please download the Desktop app credentials')
            sys.exit(1)
else:
    print('ERROR: client_secret5.json not found!')
    sys.exit(1)

# Clear any old cached token
token_path = 'credentials/oauth_token5.json'
if os.path.exists(token_path):
    os.remove(token_path)
    print('Cleared old token')

# Force Set 5 credentials
os.environ['GOOGLE_CLIENT_SECRETS_FILE_1'] = client_secret_path
os.environ['OAUTH_TOKEN_FILE_1'] = token_path
os.environ['YOUTUBE_SCOPES'] = 'https://www.googleapis.com/auth/youtube.force-ssl https://www.googleapis.com/auth/youtube.readonly'

print()
print('Browser will open for authorization...')
print('Sign in and authorize the app')
print()

from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service

try:
    # This will trigger OAuth flow with new credentials
    service = get_authenticated_service(0)
    
    # Test the service
    response = service.channels().list(part='snippet', mine=True).execute()
    
    if response.get('items'):
        channel = response['items'][0]['snippet']['title']
        print('SUCCESS! Set 5 authorized!')
        print(f'Connected as: {channel}')
        print(f'Token saved to: {token_path}')
        print('Fresh 10,000 quota now available!')
        print()
        print('The bot will now use Set 5 first!')
    else:
        print('Service authorized successfully!')
        print(f'Token saved to: {token_path}')
        
except Exception as e:
    print(f'Error: {e}')
    print()
    if 'invalid_client' in str(e):
        print('The client_secret5.json file might be invalid.')
        print('Please download it again from Google Cloud Console')
    elif 'access_denied' in str(e):
        print('Make sure your email is added as a test user')
    else:
        print('Try these steps:')
        print('1. Clear browser cache/cookies for accounts.google.com')
        print('2. Use incognito/private browser window')
        print('3. Make sure you download Desktop app (not Web) credentials')