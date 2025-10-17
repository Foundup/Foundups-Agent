#!/usr/bin/env python3
"""
Check status of all 5 credential sets
Shows which are working, expired, or missing
"""

import os
import sys
import json
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, project_root)
os.chdir(project_root)

print('=' * 60)
print('CREDENTIAL SET STATUS CHECK')
print('=' * 60)

def check_credential_set(index):
    """Check a single credential set"""
    if index == 1:
        # Set 1 uses default names
        secret_file = 'credentials/client_secret.json'
        token_file = 'credentials/oauth_token.json'
    else:
        secret_file = f'credentials/client_secret{index}.json'
        token_file = f'credentials/oauth_token{index}.json'
    
    print(f'\nSet {index}:')
    print(f'   Secret: {secret_file}')
    print(f'   Token:  {token_file}')
    
    # Check if files exist
    if not os.path.exists(secret_file):
        print(f'   ❌ Missing client secret file!')
        return 'missing_secret'
    
    if not os.path.exists(token_file):
        print(f'   ⚠️ No token file (needs authorization)')
        return 'needs_auth'
    
    # Load and check token
    try:
        creds = Credentials.from_authorized_user_file(token_file, 
            ['https://www.googleapis.com/auth/youtube.force-ssl',
             'https://www.googleapis.com/auth/youtube.readonly'])
        
        # Check expiration
        if creds.expired:
            print(f'   🔄 Token expired, attempting refresh...')
            try:
                creds.refresh(Request())
                # Save refreshed token
                with open(token_file, 'w', encoding="utf-8") as token:
                    token.write(creds.to_json())
                print(f'   ✅ Token refreshed successfully!')
                
                # Test the refreshed credentials
                youtube = build('youtube', 'v3', credentials=creds)
                response = youtube.channels().list(part='snippet', mine=True).execute()
                if response.get('items'):
                    channel_name = response['items'][0]['snippet']['title']
                    print(f'   [TV] Connected as: {channel_name}')
                    return 'active'
                    
            except Exception as e:
                error_msg = str(e)
                if 'invalid_grant' in error_msg:
                    print(f'   ❌ Token expired/revoked - needs re-authorization!')
                    print(f'      Run: python modules/platform_integration/youtube_auth/scripts/reauthorize_set{index}.py')
                    return 'expired'
                elif 'quotaExceeded' in error_msg:
                    print(f'   ⚠️ Quota exceeded but token is valid')
                    return 'quota_exceeded'
                else:
                    print(f'   ❌ Refresh failed: {error_msg[:100]}')
                    return 'refresh_failed'
        else:
            # Token not expired, test it
            print(f'   ✅ Token valid (not expired)')
            try:
                youtube = build('youtube', 'v3', credentials=creds)
                response = youtube.channels().list(part='snippet', mine=True).execute()
                if response.get('items'):
                    channel_name = response['items'][0]['snippet']['title']
                    print(f'   [TV] Connected as: {channel_name}')
                    
                    # Check quota with a test call
                    try:
                        # Small test to check quota
                        youtube.search().list(part='snippet', maxResults=1, q='test').execute()
                        print(f'   📊 Quota available')
                        return 'active'
                    except HttpError as e:
                        if 'quotaExceeded' in str(e):
                            print(f'   ⚠️ Quota exhausted for today')
                            return 'quota_exceeded'
                        raise
                            
            except Exception as e:
                print(f'   ❌ Test failed: {str(e)[:100]}')
                return 'test_failed'
                
    except Exception as e:
        print(f'   ❌ Error loading credentials: {str(e)[:100]}')
        return 'load_failed'

# Check all 7 sets
results = {}
for i in range(1, 8):
    results[i] = check_credential_set(i)

# Summary
print('\n' + '=' * 60)
print('SUMMARY')
print('=' * 60)

active_sets = [i for i, status in results.items() if status == 'active']
expired_sets = [i for i, status in results.items() if status in ['expired', 'refresh_failed']]
needs_auth_sets = [i for i, status in results.items() if status == 'needs_auth']
quota_exceeded_sets = [i for i, status in results.items() if status == 'quota_exceeded']

print(f'\n✅ Active sets: {active_sets if active_sets else "None"}')
print(f'⚠️ Quota exceeded: {quota_exceeded_sets if quota_exceeded_sets else "None"}')
print(f'❌ Expired/Need refresh: {expired_sets if expired_sets else "None"}')
print(f'🔑 Need authorization: {needs_auth_sets if needs_auth_sets else "None"}')

print('\n' + '=' * 60)
print('RECOMMENDED ACTIONS')
print('=' * 60)

if expired_sets:
    print('\n🔧 Fix expired tokens:')
    for set_num in expired_sets:
        print(f'   python modules/platform_integration/youtube_auth/scripts/reauthorize_set{set_num}.py')

if needs_auth_sets:
    print('\n🔑 Authorize new sets:')
    for set_num in needs_auth_sets:
        print(f'   python modules/platform_integration/youtube_auth/scripts/authorize_set{set_num}.py')

if not active_sets and not quota_exceeded_sets:
    print('\n⚠️ NO ACTIVE CREDENTIAL SETS!')
    print('The bot will not be able to connect to YouTube.')
    print('Please authorize at least one credential set.')

print('\nTotal available quota: ~{} units/day'.format(len(active_sets) * 10000))