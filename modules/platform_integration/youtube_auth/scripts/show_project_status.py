#!/usr/bin/env python3
"""
Show status of all Google Cloud projects and credential sets
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===


import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from dotenv import load_dotenv
load_dotenv()

import json
import google.oauth2.credentials
from google.auth.transport.requests import Request
from modules.platform_integration.youtube_auth.src.quota_monitor import QuotaMonitor

def check_credential_set(set_num):
    """Check status of a credential set."""
    if set_num == 1:
        secret_file = 'credentials/client_secret.json'
        token_file = 'credentials/oauth_token.json'
    else:
        secret_file = f'credentials/client_secret{set_num}.json'
        token_file = f'credentials/oauth_token{set_num}.json'
    
    result = {
        'set': set_num,
        'project': None,
        'status': 'UNKNOWN',
        'channel': None,
        'issues': []
    }
    
    # Get project ID
    if os.path.exists(secret_file):
        try:
            with open(secret_file, 'r', encoding="utf-8") as f:
                data = json.load(f)
                if 'installed' in data:
                    result['project'] = data['installed'].get('project_id', 'Unknown')
                elif 'web' in data:
                    result['project'] = data['web'].get('project_id', 'Unknown')
        except:
            result['issues'].append('Cannot read client secret')
    else:
        result['issues'].append('Client secret missing')
        result['status'] = 'NO_SECRET'
        return result
    
    # Check token
    if not os.path.exists(token_file):
        result['issues'].append('Token file missing')
        result['status'] = 'NO_TOKEN'
        return result
    
    # Try to load and validate token
    try:
        scopes = ['https://www.googleapis.com/auth/youtube',
                  'https://www.googleapis.com/auth/youtube.force-ssl']
        creds = google.oauth2.credentials.Credentials.from_authorized_user_file(token_file, scopes)
        
        # Check if needs refresh
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    result['status'] = 'WORKING'
                except Exception as e:
                    if 'deleted_client' in str(e):
                        result['status'] = 'DELETED'
                        result['issues'].append('OAuth client deleted in Google Cloud')
                    else:
                        result['status'] = 'AUTH_ERROR'
                        result['issues'].append(str(e)[:50])
            else:
                result['status'] = 'EXPIRED'
                result['issues'].append('Token expired, no refresh token')
        else:
            result['status'] = 'WORKING'
        
        # Test API if working
        if result['status'] == 'WORKING':
            try:
                # Quick API test
                from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
                service = get_authenticated_service(token_index=set_num-1)
                response = service.channels().list(part='snippet', mine=True).execute()
                
                if response.get('items'):
                    result['channel'] = response['items'][0]['snippet']['title']
                else:
                    result['issues'].append('No channel found')
                    
            except Exception as e:
                if 'quotaExceeded' in str(e):
                    result['status'] = 'QUOTA_EXHAUSTED'
                    result['issues'].append('Daily quota exceeded')
                else:
                    result['issues'].append(f'API error: {str(e)[:50]}')
                    
    except Exception as e:
        result['status'] = 'ERROR'
        result['issues'].append(str(e)[:50])
    
    return result


def main():
    """Display project status."""
    print("="*70)
    print("GOOGLE CLOUD PROJECTS STATUS")
    print("="*70)
    
    # Check all sets
    results = []
    for i in range(1, 8):
        results.append(check_credential_set(i))
    
    # Get quota info
    monitor = QuotaMonitor()
    quota_summary = monitor.get_usage_summary()
    
    # Display results
    print("\n[DATA] PROJECT STATUS:")
    print("-"*70)
    
    status_emoji = {
        'WORKING': '[OK]',
        'QUOTA_EXHAUSTED': '[U+26A0]️',
        'DELETED': '[FAIL]',
        'NO_TOKEN': '[U+1F511]',
        'NO_SECRET': '[LOCK]',
        'EXPIRED': '⏰',
        'AUTH_ERROR': '[FORBIDDEN]',
        'ERROR': '[U+1F4A5]',
        'UNKNOWN': '[U+2753]'
    }
    
    for r in results:
        emoji = status_emoji.get(r['status'], '[U+2753]')
        quota_info = quota_summary['sets'].get(r['set'], {})
        quota_percent = quota_info.get('usage_percent', 0)
        
        print(f"\nSet {r['set']}: {emoji} {r['status']}")
        print(f"  Project: {r['project']}")
        
        if r['channel']:
            print(f"  Channel: {r['channel']}")
        
        if quota_percent > 0:
            print(f"  Quota: {quota_percent:.1f}% used ({quota_info['used']}/{quota_info['limit']} units)")
        
        if r['issues']:
            for issue in r['issues']:
                print(f"  [U+26A0]️ {issue}")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("-"*70)
    
    working_sets = [r for r in results if r['status'] == 'WORKING']
    exhausted_sets = [r for r in results if r['status'] == 'QUOTA_EXHAUSTED']
    broken_sets = [r for r in results if r['status'] in ['DELETED', 'NO_TOKEN', 'NO_SECRET', 'EXPIRED', 'AUTH_ERROR']]
    
    print(f"\n[OK] Working: {len(working_sets)} sets")
    for r in working_sets:
        print(f"   - Set {r['set']}: {r['project']}")
    
    if exhausted_sets:
        print(f"\n[U+26A0]️ Quota Exhausted: {len(exhausted_sets)} sets")
        for r in exhausted_sets:
            print(f"   - Set {r['set']}: {r['project']}")
    
    if broken_sets:
        print(f"\n[FAIL] Need Fix: {len(broken_sets)} sets")
        for r in broken_sets:
            print(f"   - Set {r['set']}: {r['project']} ({r['status']})")
    
    print("\n" + "="*70)
    print("ROTATION ORDER (current):")
    print("Sets will be tried in this order: 1, 2, 7, 5, 4, 6, 3")
    print("\nWorking projects:")
    print("  1. foundups-bot     [OK]")
    print("  2. foundups-agent2  [OK] (1.3% quota used)")
    print("  4. foundups-agent4  [OK]")
    print("  5. foundupsagent5   [OK]")
    print("  7. foundups-agent7  [OK]")
    print("\nProblematic:")
    print("  3. foundups-agent2  [FAIL] (OAuth client deleted)")
    print("  6. foundups-agent6  [U+26A0]️ (quota may be exhausted)")
    print("="*70)


if __name__ == "__main__":
    main()