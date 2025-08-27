#!/usr/bin/env python3
"""
Re-authorization script for Set 6 - Use UnDaoDu account!
"""

import os
import sys
import json

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, project_root)
os.chdir(project_root)

print('Re-authorizing Set 6 with UnDaoDu account...')
print('=' * 50)
print('[IMPORTANT] Use the UnDaoDu Google account!')
print('=' * 50)

# Check that client_secret6.json exists
client_secret_path = 'credentials/client_secret6.json'
if not os.path.exists(client_secret_path):
    print(f'[X] ERROR: {client_secret_path} not found!')
    sys.exit(1)

# Clear the existing token (wrong account)
token_path = 'credentials/oauth_token6.json'
if os.path.exists(token_path):
    os.remove(token_path)
    print('[OK] Cleared token from wrong account')

# Force Set 6 credentials
os.environ['GOOGLE_CLIENT_SECRETS_FILE_1'] = client_secret_path
os.environ['OAUTH_TOKEN_FILE_1'] = token_path
os.environ['YOUTUBE_SCOPES'] = 'https://www.googleapis.com/auth/youtube.force-ssl https://www.googleapis.com/auth/youtube.readonly'

print()
print('[BROWSER] Browser will open for authorization...')
print('[CRITICAL] Sign in with the UnDaoDu Google account!')
print('[WARNING] Do NOT use Mike Trout or any other account!')
print()

from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service

try:
    service = get_authenticated_service(0)
    response = service.channels().list(part='snippet', mine=True).execute()
    
    if response.get('items'):
        channel = response['items'][0]['snippet']['title']
        print()
        if 'UnDaoDu' in channel:
            print('[OK] SUCCESS! Set 6 re-authorized with correct account!')
        else:
            print(f'[WARNING] Authorized as: {channel}')
            print('[WARNING] This should be UnDaoDu!')
            print('Re-run this script and use the UnDaoDu account!')
        print(f'[TV] Connected as: {channel}')
        print(f'[SAVE] Token saved to: {token_path}')
        
except Exception as e:
    print(f'[X] Error: {e}')