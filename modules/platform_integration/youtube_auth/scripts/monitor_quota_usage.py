#!/usr/bin/env python3
"""
Monitor quota usage across all credential sets
Tracks API calls and estimates remaining quota
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import os
import sys
import json
from datetime import datetime, timedelta
import time

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, project_root)
os.chdir(project_root)

from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service

# Quota costs for common YouTube API operations
QUOTA_COSTS = {
    'channels.list': 1,
    'search.list': 100,
    'videos.list': 1,
    'commentThreads.list': 1,
    'comments.list': 1,
    'comments.insert': 50,
    'commentThreads.insert': 50,
    'videos.insert': 1600,
    'liveChatMessages.list': 5,
    'liveChatMessages.insert': 5,
    'liveChatModerators.list': 1,
    'liveChatModerators.insert': 50,
    'liveChatModerators.delete': 50,
    'liveChatBans.insert': 200,
    'liveChatBans.delete': 50
}

def estimate_daily_usage():
    """Estimate daily quota usage based on bot operations"""
    
    print('=' * 60)
    print('ESTIMATED DAILY QUOTA USAGE')
    print('=' * 60)
    
    # Typical bot operations per hour
    operations_per_hour = {
        'Poll live chat (5 units each)': 60,  # Once per minute
        'Send chat message (5 units)': 10,    # 10 messages per hour
        'Ban/timeout user (200 units)': 2,    # 2 bans per hour
        'Check channel info (1 unit)': 1      # Once per hour
    }
    
    hourly_cost = 0
    for op, count in operations_per_hour.items():
        if 'live chat' in op.lower() and '5 units' in op:
            cost = count * 5
        elif 'message' in op and '5 units' in op:
            cost = count * 5
        elif 'ban' in op.lower() or 'timeout' in op.lower():
            cost = count * 200
        else:
            cost = count * 1
        
        print(f'{op}: {cost} units/hour')
        hourly_cost += cost
    
    daily_cost = hourly_cost * 24
    print(f'\nTotal hourly usage: {hourly_cost:,} units')
    print(f'Total daily usage: {daily_cost:,} units')
    print(f'Sets needed for 24/7 operation: {(daily_cost / 10000):.1f}')
    
    return daily_cost

def check_current_availability():
    """Check which sets have quota available right now"""
    
    print('\n' + '=' * 60)
    print('CURRENT QUOTA AVAILABILITY')
    print('=' * 60)
    
    available_sets = []
    exhausted_sets = []
    error_sets = []
    
    for i in range(1, 8):
        try:
            service = get_authenticated_service(i-1)
            # Simple test call (1 unit)
            response = service.channels().list(part='id', mine=True).execute()
            available_sets.append(i)
            print(f'Set {i}: [OK] Available')
        except Exception as e:
            if 'quotaExceeded' in str(e):
                exhausted_sets.append(i)
                print(f'Set {i}: [QUOTA] Exhausted')
            else:
                error_sets.append(i)
                print(f'Set {i}: [ERROR] {str(e)[:30]}...')
    
    print(f'\nAvailable now: {available_sets} ({len(available_sets) * 10000:,} units)')
    print(f'Exhausted: {exhausted_sets} (resets at midnight PT)')
    
    # Calculate time until midnight PT
    from datetime import timezone
    now = datetime.now(timezone.utc)
    # PT is UTC-7 or UTC-8 depending on DST
    pt_offset = timedelta(hours=7)  # Assuming PDT
    pt_now = now - pt_offset
    midnight_pt = pt_now.replace(hour=7, minute=0, second=0, microsecond=0)  # 7 UTC = midnight PT
    if pt_now.hour >= 7:
        midnight_pt += timedelta(days=1)
    
    time_until_reset = midnight_pt - now
    hours_until = time_until_reset.total_seconds() / 3600
    print(f'Time until quota reset: {hours_until:.1f} hours')
    
    return available_sets, exhausted_sets

def main():
    print('YOUTUBE API QUOTA MONITOR')
    print('=' * 60)
    
    # Check current availability
    available, exhausted = check_current_availability()
    
    # Estimate usage
    daily_usage = estimate_daily_usage()
    
    # Recommendations
    print('\n' + '=' * 60)
    print('RECOMMENDATIONS')
    print('=' * 60)
    
    current_capacity = len(available) * 10000
    if current_capacity >= daily_usage:
        print(f'[OK] Current capacity ({current_capacity:,} units) exceeds daily needs')
    else:
        deficit = daily_usage - current_capacity
        print(f'[WARNING] Need {deficit:,} more units for 24/7 operation')
        print(f'[INFO] {len(exhausted)} sets will provide {len(exhausted) * 10000:,} units at midnight PT')
    
    # Optimization tips
    print('\n' + '=' * 60)
    print('OPTIMIZATION TIPS')
    print('=' * 60)
    print('1. Reduce polling frequency during low-activity hours')
    print('2. Cache channel/video info (1 unit) instead of repeated lookups')
    print('3. Batch operations where possible')
    print('4. Use liveChatMessages.list sparingly (5 units each)')
    print('5. Consider webhook/push notifications instead of polling')

if __name__ == '__main__':
    main()