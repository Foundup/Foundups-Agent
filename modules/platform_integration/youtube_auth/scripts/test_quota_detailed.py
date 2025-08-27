#!/usr/bin/env python3
"""
Detailed quota and API testing for all credential sets
Tests actual API calls and reports exact errors
"""

import os
import sys
import json
from datetime import datetime
import traceback

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, project_root)
os.chdir(project_root)

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def test_credential_set(set_num):
    """Test a single credential set with detailed error reporting"""
    
    # Determine file paths
    if set_num == 1:
        secret_path = 'credentials/client_secret.json'
        token_path = 'credentials/oauth_token.json'
    else:
        secret_path = f'credentials/client_secret{set_num}.json'
        token_path = f'credentials/oauth_token{set_num}.json'
    
    result = {
        'set': set_num,
        'secret_exists': os.path.exists(secret_path),
        'token_exists': os.path.exists(token_path),
        'project_id': None,
        'token_valid': False,
        'api_enabled': False,
        'quota_available': False,
        'channel_name': None,
        'channel_id': None,
        'error': None,
        'error_type': None
    }
    
    # Check secret file
    if not result['secret_exists']:
        result['error'] = 'No client secret file'
        return result
    
    # Get project ID
    try:
        with open(secret_path, 'r') as f:
            secret_data = json.load(f)
            result['project_id'] = secret_data.get('installed', {}).get('project_id', 'Unknown')
    except Exception as e:
        result['error'] = f'Cannot read secret: {e}'
        return result
    
    # Check token file
    if not result['token_exists']:
        result['error'] = 'No token file - needs authorization'
        return result
    
    # Load and test credentials
    try:
        with open(token_path, 'r') as f:
            creds_data = json.load(f)
        
        creds = Credentials.from_authorized_user_info(creds_data)
        
        # Check if expired
        if creds.expired:
            if creds.refresh_token:
                try:
                    creds.refresh(Request())
                    result['token_valid'] = True
                    # Save refreshed token
                    with open(token_path, 'w') as f:
                        f.write(creds.to_json())
                except Exception as e:
                    result['error'] = f'Token refresh failed: {e}'
                    result['error_type'] = 'TOKEN_REFRESH_FAILED'
                    return result
            else:
                result['error'] = 'Token expired, no refresh token'
                result['error_type'] = 'TOKEN_EXPIRED'
                return result
        else:
            result['token_valid'] = True
        
        # Build service and test API
        service = build('youtube', 'v3', credentials=creds)
        
        # Test 1: Simple API call (costs 1 unit)
        try:
            response = service.channels().list(
                part='snippet',
                mine=True
            ).execute()
            
            result['api_enabled'] = True
            result['quota_available'] = True
            
            if response.get('items'):
                channel = response['items'][0]
                result['channel_name'] = channel['snippet']['title']
                result['channel_id'] = channel['id']
        
        except HttpError as e:
            error_content = json.loads(e.content.decode('utf-8'))
            error_reason = error_content.get('error', {}).get('errors', [{}])[0].get('reason', '')
            error_message = error_content.get('error', {}).get('message', str(e))
            
            if 'quotaExceeded' in error_reason:
                result['api_enabled'] = True
                result['quota_available'] = False
                result['error'] = 'Quota exceeded for today'
                result['error_type'] = 'QUOTA_EXCEEDED'
            elif 'accessNotConfigured' in error_reason:
                result['api_enabled'] = False
                result['error'] = 'YouTube Data API v3 not enabled in project'
                result['error_type'] = 'API_NOT_ENABLED'
            elif 'forbidden' in error_reason.lower() or e.resp.status == 403:
                result['error'] = f'403 Forbidden: {error_message}'
                result['error_type'] = 'FORBIDDEN'
            elif 'invalid_grant' in str(e):
                result['error'] = 'Invalid grant - token needs re-authorization'
                result['error_type'] = 'INVALID_GRANT'
            else:
                result['error'] = f'API Error: {error_message}'
                result['error_type'] = f'HTTP_{e.resp.status}'
    
    except Exception as e:
        result['error'] = f'Unexpected error: {str(e)}'
        result['error_type'] = 'UNEXPECTED'
        result['traceback'] = traceback.format_exc()
    
    return result

def main():
    print('=' * 80)
    print('YOUTUBE API CREDENTIAL SET DIAGNOSTIC')
    print('=' * 80)
    print()
    
    # Test all 7 sets
    results = []
    for i in range(1, 8):
        print(f'Testing Set {i}...', end=' ')
        result = test_credential_set(i)
        results.append(result)
        
        if result['quota_available']:
            print('[OK] Working')
        elif result['error_type'] == 'QUOTA_EXCEEDED':
            print('[QUOTA] Exceeded')
        elif result['error_type'] == 'API_NOT_ENABLED':
            print('[API] Not enabled')
        elif result['error_type'] == 'TOKEN_EXPIRED' or result['error_type'] == 'INVALID_GRANT':
            print('[AUTH] Needs re-auth')
        else:
            print(f'[ERROR] {result["error_type"]}')
    
    print()
    print('=' * 80)
    print('DETAILED RESULTS')
    print('=' * 80)
    
    for r in results:
        print(f'\nSet {r["set"]} (Project: {r["project_id"]}):')
        print(f'  Files: Secret={r["secret_exists"]} Token={r["token_exists"]}')
        
        if r['channel_name']:
            print(f'  [OK] Channel: {r["channel_name"]} (ID: {r["channel_id"]})')
            print(f'  [OK] Quota available')
        elif r['error']:
            print(f'  [X] {r["error"]}')
            if r['error_type'] == 'QUOTA_EXCEEDED':
                print(f'  [INFO] Will reset at midnight Pacific Time')
            elif r['error_type'] == 'API_NOT_ENABLED':
                print(f'  [FIX] Enable YouTube Data API v3 in Google Cloud Console')
            elif r['error_type'] in ['TOKEN_EXPIRED', 'INVALID_GRANT']:
                print(f'  [FIX] Run: reauthorize_set{r["set"]}.py')
    
    print()
    print('=' * 80)
    print('SUMMARY')
    print('=' * 80)
    
    working = [r for r in results if r['quota_available']]
    quota_exceeded = [r for r in results if r['error_type'] == 'QUOTA_EXCEEDED']
    api_disabled = [r for r in results if r['error_type'] == 'API_NOT_ENABLED']
    needs_auth = [r for r in results if r['error_type'] in ['TOKEN_EXPIRED', 'INVALID_GRANT', None] and not r['token_exists']]
    other_errors = [r for r in results if r['error'] and r['error_type'] not in ['QUOTA_EXCEEDED', 'API_NOT_ENABLED', 'TOKEN_EXPIRED', 'INVALID_GRANT']]
    
    print(f'\n[OK] Working sets: {[r["set"] for r in working]}')
    print(f'     Total quota available: {len(working) * 10000:,} units/day')
    
    if quota_exceeded:
        print(f'\n[QUOTA] Exceeded (reset at midnight PT): {[r["set"] for r in quota_exceeded]}')
    
    if api_disabled:
        print(f'\n[API] Not enabled in project: {[r["set"] for r in api_disabled]}')
        for r in api_disabled:
            print(f'      Set {r["set"]}: Enable API in project {r["project_id"]}')
    
    if needs_auth:
        print(f'\n[AUTH] Need authorization: {[r["set"] for r in needs_auth]}')
    
    if other_errors:
        print(f'\n[ERROR] Other issues: {[r["set"] for r in other_errors]}')
        for r in other_errors:
            print(f'        Set {r["set"]}: {r["error_type"]} - {r["error"][:50]}...')

if __name__ == '__main__':
    main()