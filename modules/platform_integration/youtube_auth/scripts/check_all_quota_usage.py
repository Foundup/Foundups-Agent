#!/usr/bin/env python3
"""
Check API quota usage for all Google Cloud projects
Shows both local tracking and tests actual API availability
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from dotenv import load_dotenv
load_dotenv()

import json
import time
from datetime import datetime
from modules.platform_integration.youtube_auth.src.quota_monitor import QuotaMonitor
from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service

def test_api_call(set_num):
    """Test API call to check if quota is available."""
    try:
        service = get_authenticated_service(token_index=set_num-1)
        
        # Make a minimal API call (costs 1 unit)
        start = time.time()
        response = service.channels().list(
            part='snippet',
            mine=True,
            maxResults=1
        ).execute()
        elapsed = (time.time() - start) * 1000
        
        if response.get('items'):
            return {
                'available': True,
                'response_time_ms': elapsed,
                'channel': response['items'][0]['snippet']['title']
            }
        else:
            return {
                'available': False,
                'error': 'No channel found',
                'response_time_ms': elapsed
            }
    except Exception as e:
        if 'quotaExceeded' in str(e):
            return {
                'available': False,
                'error': 'QUOTA_EXHAUSTED',
                'message': 'Daily quota exceeded'
            }
        else:
            return {
                'available': False,
                'error': str(e)[:100]
            }

def get_project_info(set_num):
    """Get project ID from client secret file."""
    if set_num == 1:
        secret_file = 'credentials/client_secret.json'
    else:
        secret_file = f'credentials/client_secret{set_num}.json'
    
    try:
        with open(secret_file, 'r', encoding="utf-8") as f:
            data = json.load(f)
            if 'installed' in data:
                return data['installed'].get('project_id', 'Unknown')
            elif 'web' in data:
                return data['web'].get('project_id', 'Unknown')
    except:
        return 'Unknown'
    return 'Unknown'

def main():
    print("="*80)
    print("GOOGLE CLOUD PROJECTS - API QUOTA USAGE REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Get local quota tracking
    monitor = QuotaMonitor()
    quota_summary = monitor.get_usage_summary()
    
    # Test each credential set
    results = []
    total_used = 0
    total_available = 0
    
    print("\n📊 TESTING EACH PROJECT:")
    print("-"*80)
    
    for set_num in range(1, 8):
        project_id = get_project_info(set_num)
        print(f"\nSet {set_num}: {project_id}")
        
        # Get local tracking data
        local_data = quota_summary['sets'].get(set_num, {})
        local_used = local_data.get('used', 0)
        local_limit = local_data.get('limit', 10000)
        local_percent = local_data.get('usage_percent', 0)
        
        # Test actual API
        api_test = test_api_call(set_num)
        
        # Compile results
        result = {
            'set': set_num,
            'project': project_id,
            'local_used': local_used,
            'local_limit': local_limit,
            'local_percent': local_percent,
            'api_available': api_test['available'],
            'api_error': api_test.get('error'),
            'response_time': api_test.get('response_time_ms', 0)
        }
        results.append(result)
        
        # Display results
        if api_test['available']:
            print(f"  ✅ API Status: AVAILABLE")
            print(f"  📊 Usage: {local_used:,}/{local_limit:,} units ({local_percent:.1f}%)")
            print(f"  ⚡ Response: {api_test['response_time_ms']:.0f}ms")
            print(f"  👤 Connected as: {api_test.get('channel', 'Unknown')}")
            total_available += (local_limit - local_used)
            total_used += local_used
        else:
            if api_test.get('error') == 'QUOTA_EXHAUSTED':
                print(f"  ⚠️ API Status: QUOTA EXHAUSTED")
                print(f"  📊 Usage: {local_limit:,}/{local_limit:,} units (100%)")
                total_used += local_limit
            else:
                print(f"  ❌ API Status: ERROR")
                print(f"  📊 Usage: {local_used:,}/{local_limit:,} units ({local_percent:.1f}%)")
                print(f"  ⚠️ Error: {api_test.get('error', 'Unknown')}")
    
    # Summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("-"*80)
    
    working_projects = [r for r in results if r['api_available']]
    exhausted_projects = [r for r in results if not r['api_available'] and r.get('api_error') == 'QUOTA_EXHAUSTED']
    error_projects = [r for r in results if not r['api_available'] and r.get('api_error') != 'QUOTA_EXHAUSTED']
    
    print(f"\n✅ Working Projects: {len(working_projects)}/7")
    for r in working_projects:
        bar_length = 20
        filled = int(bar_length * r['local_percent'] / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"   {r['set']}. {r['project']:20} [{bar}] {r['local_percent']:5.1f}% ({r['local_used']:,}/{r['local_limit']:,})")
    
    if exhausted_projects:
        print(f"\n⚠️ Quota Exhausted: {len(exhausted_projects)}/7")
        for r in exhausted_projects:
            print(f"   {r['set']}. {r['project']:20} [████████████████████] 100.0%")
    
    if error_projects:
        print(f"\n❌ Errors: {len(error_projects)}/7")
        for r in error_projects:
            print(f"   {r['set']}. {r['project']:20} - {r['api_error'][:50]}")
    
    # Aggregate statistics
    print("\n" + "="*80)
    print("AGGREGATE QUOTA STATISTICS")
    print("-"*80)
    
    total_limit = 70000  # 7 projects * 10,000 units each
    total_percent = (total_used / total_limit * 100) if total_limit > 0 else 0
    
    print(f"\n📊 Total Quota Pool: {total_limit:,} units/day")
    print(f"📈 Total Used: {total_used:,} units ({total_percent:.1f}%)")
    print(f"📉 Total Available: {total_available:,} units")
    
    # Usage breakdown by project
    print("\n📋 Detailed Usage by Project:")
    print("-"*40)
    
    # Sort by usage percentage
    sorted_results = sorted(results, key=lambda x: x['local_percent'], reverse=True)
    
    for r in sorted_results:
        if r['local_used'] > 0:
            print(f"{r['project']:20} - {r['local_used']:,} units ({r['local_percent']:.1f}%)")
    
    # Recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("-"*80)
    
    if len(working_projects) == 7:
        print("✅ All projects operational - maximum redundancy achieved!")
    elif len(working_projects) >= 5:
        print("✅ Good redundancy - multiple projects available")
    elif len(working_projects) >= 3:
        print("⚠️ Moderate redundancy - consider fixing error projects")
    else:
        print("🚨 Low redundancy - urgent attention needed!")
    
    if total_percent < 20:
        print("✅ Quota usage is healthy - plenty of capacity")
    elif total_percent < 50:
        print("✅ Quota usage is moderate - normal operations")
    elif total_percent < 80:
        print("⚠️ Quota usage is high - monitor closely")
    else:
        print("🚨 Quota usage is critical - may hit limits soon")
    
    # Best project for next use
    if working_projects:
        best = min(working_projects, key=lambda x: x['local_percent'])
        print(f"\n🎯 Best project for next use: Set {best['set']} ({best['project']}) - {best['local_percent']:.1f}% used")
    
    print("="*80)

if __name__ == "__main__":
    main()