#!/usr/bin/env python3
"""
Re-authorize Set 5 with UnDaoDu account
Current issue: 403 errors despite valid token
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, project_root)
os.chdir(project_root)

print('=' * 60)
print('RE-AUTHORIZING SET 5')
print('=' * 60)
print('[INFO] Set 5 showing 403 errors')
print('[ACTION] Will clear token and re-authorize')
print('=' * 60)

# Clear the existing token
token_path = 'credentials/oauth_token5.json'
if os.path.exists(token_path):
    os.remove(token_path)
    print('[OK] Cleared existing token')

# Force Set 5 credentials
os.environ['GOOGLE_CLIENT_SECRETS_FILE_1'] = 'credentials/client_secret5.json'
os.environ['OAUTH_TOKEN_FILE_1'] = token_path
os.environ['YOUTUBE_SCOPES'] = 'https://www.googleapis.com/auth/youtube.force-ssl https://www.googleapis.com/auth/youtube.readonly'

print()
print('[BROWSER] Browser will open for authorization...')
print('[IMPORTANT] Sign in with the UnDaoDu account!')
print()

from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service

try:
    service = get_authenticated_service(0)
    response = service.channels().list(part='snippet', mine=True).execute()
    
    if response.get('items'):
        channel = response['items'][0]['snippet']['title']
        channel_id = response['items'][0]['id']
        print()
        
        if 'UnDaoDu' in channel or channel_id == 'UCfHM9Fw9HD-NwiS0seD_oIA':
            print('[OK] SUCCESS! Set 5 authorized with correct account!')
        else:
            print(f'[WARNING] Wrong account! Got: {channel}')
            print('[ACTION] Please re-run and select UnDaoDu account!')
        
        print(f'[TV] Connected as: {channel}')
        print(f'[ID] Channel ID: {channel_id}')
        print(f'[SAVE] Token saved to: {token_path}')
        
except Exception as e:
    print(f'[X] Error: {e}')