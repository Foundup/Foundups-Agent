#!/usr/bin/env python3
"""
Fix Set 3 - Re-authorize with UnDaoDu account
Currently using wrong account: Foundups Decentralized Startups
"""

import os
import sys
import json

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, project_root)
os.chdir(project_root)

print('=' * 60)
print('FIXING SET 3 - Wrong Account Issue')
print('=' * 60)
print('[PROBLEM] Set 3 is using: Foundups Decentralized Startups')
print('[NEEDED] Should be using: UnDaoDu')
print('=' * 60)

# Clear the wrong account token
token_path = 'credentials/oauth_token3.json'
if os.path.exists(token_path):
    os.remove(token_path)
    print('[OK] Cleared token from wrong account')

# Force Set 3 credentials
os.environ['GOOGLE_CLIENT_SECRETS_FILE_1'] = 'credentials/client_secret3.json'
os.environ['OAUTH_TOKEN_FILE_1'] = token_path
os.environ['YOUTUBE_SCOPES'] = 'https://www.googleapis.com/auth/youtube.force-ssl https://www.googleapis.com/auth/youtube.readonly'

print()
print('[BROWSER] Browser will open for authorization...')
print('[CRITICAL] You MUST sign in with the UnDaoDu account!')
print('[WARNING] Do NOT use "Foundups Decentralized Startups" account!')
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
            print('[OK] SUCCESS! Set 3 now using correct account!')
        else:
            print(f'[WARNING] Wrong account! Got: {channel}')
            print('[ACTION] Please re-run and select UnDaoDu account!')
            print('[TIP] You may need to:')
            print('  1. Sign out of all Google accounts')
            print('  2. Use incognito/private browser')
            print('  3. Sign in ONLY with UnDaoDu account')
        
        print(f'[TV] Connected as: {channel}')
        print(f'[ID] Channel ID: {channel_id}')
        print(f'[SAVE] Token saved to: {token_path}')
        
except Exception as e:
    print(f'[X] Error: {e}')