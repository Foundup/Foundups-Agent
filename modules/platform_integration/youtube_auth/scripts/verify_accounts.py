#!/usr/bin/env python3
"""
Verify which Google account each credential set is using
"""

import os
import sys
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, project_root)
os.chdir(project_root)

print('=' * 60)
print('VERIFYING GOOGLE ACCOUNTS FOR ALL CREDENTIAL SETS')
print('=' * 60)

def check_account(index):
    """Check which account a credential set is using"""
    if index == 1:
        token_file = 'credentials/oauth_token.json'
    else:
        token_file = f'credentials/oauth_token{index}.json'
    
    if not os.path.exists(token_file):
        return None, "No token file"
    
    try:
        # Load credentials
        creds = Credentials.from_authorized_user_file(token_file, 
            ['https://www.googleapis.com/auth/youtube.force-ssl',
             'https://www.googleapis.com/auth/youtube.readonly'])
        
        # Build YouTube service
        youtube = build('youtube', 'v3', credentials=creds)
        
        # Get channel info
        response = youtube.channels().list(
            part='snippet',
            mine=True
        ).execute()
        
        if response.get('items'):
            channel = response['items'][0]
            channel_id = channel['id']
            channel_name = channel['snippet']['title']
            return channel_id, channel_name
        else:
            return None, "No channel found"
            
    except Exception as e:
        error_msg = str(e)
        if '403' in error_msg:
            return None, "403 Error (quota/permission issue)"
        elif 'quotaExceeded' in error_msg:
            return None, "Quota exceeded"
        else:
            return None, f"Error: {error_msg[:50]}"

# Check all sets
results = {}
for i in range(1, 8):
    print(f'\nChecking Set {i}...')
    channel_id, channel_name = check_account(i)
    results[i] = (channel_id, channel_name)
    if channel_id:
        print(f'  Channel ID: {channel_id}')
        print(f'  Channel Name: {channel_name}')
    else:
        print(f'  Status: {channel_name}')

# Summary
print('\n' + '=' * 60)
print('ACCOUNT SUMMARY')
print('=' * 60)

# Group by channel ID
accounts = {}
for set_num, (channel_id, channel_name) in results.items():
    if channel_id:
        if channel_id not in accounts:
            accounts[channel_id] = {'name': channel_name, 'sets': []}
        accounts[channel_id]['sets'].append(set_num)

if accounts:
    print(f'\nFound {len(accounts)} unique Google account(s):')
    for channel_id, info in accounts.items():
        sets_list = ', '.join(map(str, info['sets']))
        print(f'\n  {info["name"]} (ID: {channel_id})')
        print(f'    Used by Sets: {sets_list}')
else:
    print('\nNo working accounts found!')

# Check for issues
issues = [(set_num, channel_name) for set_num, (channel_id, channel_name) in results.items() if not channel_id]
if issues:
    print('\n' + '=' * 60)
    print('SETS WITH ISSUES')
    print('=' * 60)
    for set_num, status in issues:
        print(f'  Set {set_num}: {status}')