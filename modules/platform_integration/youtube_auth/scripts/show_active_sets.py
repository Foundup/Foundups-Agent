#!/usr/bin/env python3
"""
Show which credential sets are currently active and working
"""

import os
import sys
import json
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, project_root)
os.chdir(project_root)

from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service

print('=' * 60)
print('ACTIVE CREDENTIAL SETS')
print('=' * 60)

working_sets = []
quota_exceeded = []
needs_fix = []

for i in range(1, 8):
    token_path = f'credentials/oauth_token{i if i > 1 else ""}.json'
    
    if not os.path.exists(token_path):
        needs_fix.append(f"Set {i}: No token file")
        continue
    
    try:
        service = get_authenticated_service(i-1)
        response = service.channels().list(part='snippet', mine=True).execute()
        
        if response.get('items'):
            channel = response['items'][0]['snippet']['title']
            working_sets.append(f"Set {i}: {channel} [10,000 units]")
    except Exception as e:
        error_str = str(e)
        if 'quotaExceeded' in error_str:
            quota_exceeded.append(f"Set {i}: Quota exhausted (resets at midnight PT)")
        elif 'has not been used in project' in error_str:
            needs_fix.append(f"Set {i}: API not enabled (wait for propagation)")
        else:
            needs_fix.append(f"Set {i}: {error_str[:50]}...")

print('\n[OK] WORKING SETS:')
for s in working_sets:
    print(f'  {s}')

if quota_exceeded:
    print('\n[WAIT] QUOTA EXCEEDED (resets daily):')
    for s in quota_exceeded:
        print(f'  {s}')

if needs_fix:
    print('\n[FIX] NEEDS ATTENTION:')
    for s in needs_fix:
        print(f'  {s}')

total_quota = len(working_sets) * 10000
print(f'\n[TOTAL] {total_quota:,} units available today')
print('=' * 60)