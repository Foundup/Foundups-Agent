#!/usr/bin/env python3
"""
Authorize Set 5 OAuth credentials
Run this to set up oauth_token5.json
"""

import os
import sys

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force Set 5 credentials
os.environ['GOOGLE_CLIENT_SECRETS_FILE_1'] = 'credentials/client_secret5.json'
os.environ['OAUTH_TOKEN_FILE_1'] = 'credentials/oauth_token5.json'
os.environ['YOUTUBE_SCOPES'] = 'https://www.googleapis.com/auth/youtube.force-ssl https://www.googleapis.com/auth/youtube.readonly'

print('Authorizing Set 5 (foundups-agent5)...')
print('=' * 50)
print()
print('A browser window will open.')
print('Sign in with your Google account and authorize the app.')
print()

from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service

try:
    # This will trigger OAuth flow
    service = get_authenticated_service(0)
    
    # Test the service
    response = service.channels().list(part='snippet', mine=True).execute()
    
    if response.get('items'):
        channel = response['items'][0]['snippet']['title']
        print(f'SUCCESS! Set 5 authorized!')
        print(f'Connected as: {channel}')
        print(f'Token saved to: credentials/oauth_token5.json')
        print(f'Fresh 10,000 quota now available!')
    else:
        print('Service authorized successfully!')
        
except Exception as e:
    print(f'Error: {e}')
    print()
    print('Make sure:')
    print('1. client_secret5.json is a Desktop app type')
    print('2. You authorized in the browser')
    print('3. The browser redirect completed')