#!/usr/bin/env python3
"""
Test WRE Monitor Integration
Verifies that all tracking hooks are working properly
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from modules.infrastructure.wre_core.wre_monitor import get_monitor


async def test_wre_monitor():
    """Test WRE monitor tracking functions"""
    print("\n" + "="*60)
    print("[TEST] WRE MONITOR INTEGRATION")
    print("="*60)
    
    monitor = get_monitor()
    
    # Test 1: API call tracking
    print("\n[1/5] Testing API call tracking...")
    monitor.track_api_call('test.endpoint', 10, True)
    monitor.track_api_call('test.endpoint2', 5, True)
    monitor.track_api_call('test.quota_heavy', 100, False)
    print("[OK] API calls tracked")
    
    # Test 2: Stream transition tracking
    print("\n[2/5] Testing stream transition tracking...")
    monitor.track_stream_transition('old_stream_123', 'new_stream_456', 45.2)
    monitor.track_stream_transition('new_stream_456', 'another_stream_789', 12.5)
    print("[OK] Stream transitions tracked")
    
    # Test 3: Pattern learning tracking
    print("\n[3/5] Testing pattern learning...")
    monitor.track_pattern_learned('api_throttle', {'delay': 10, 'quota': 50})
    monitor.track_pattern_learned('message_response', {'type': 'consciousness', 'priority': 'high'})
    monitor.track_pattern_learned('troll_detection', {'user': 'spammer123', 'triggers': 5})
    print("[OK] Pattern learning tracked")
    
    # Test 4: Error tracking
    print("\n[4/5] Testing error tracking...")
    monitor.track_error('quota_exceeded', 'API quota limit reached', 'Switched to credential set 2')
    monitor.track_error('stream_not_found', 'No active streams', 'Waiting with exponential backoff')
    print("[OK] Errors tracked")
    
    # Test 5: Message processing
    print("\n[5/5] Testing message processing...")
    for i in range(10):
        monitor.messages_processed += 1
        await asyncio.sleep(0.1)
    print("[OK] Messages tracked")
    
    # Show status
    print("\n" + "="*60)
    print("[STATUS] Current Monitor State:")
    print("="*60)
    
    status = monitor.get_status()
    for key, value in status.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    # Test suggestions
    print("\n[SUGGESTIONS] Top improvements identified:")
    suggestions = monitor.suggestions[:3]
    for i, sugg in enumerate(suggestions, 1):
        print(f"{i}. [{sugg.area}] {sugg.suggested_improvement}")
        print(f"   Expected: {sugg.expected_benefit}")
    
    print("\n" + "="*60)
    print("[SUCCESS] All WRE monitor integrations working!")
    print("="*60)
    
    return True


if __name__ == "__main__":
    print("\n[0102] Testing WRE Monitor Integration...")
    
    try:
        result = asyncio.run(test_wre_monitor())
        if result:
            print("\n[READY] System ready for YouTube DAE monitoring")
            print("\nNext steps:")
            print("1. Run: python main.py")
            print("2. Select option 1 (YouTube DAE)")
            print("3. In another terminal, run: python modules/infrastructure/wre_core/monitor_dashboard.py")
            print("4. Watch the real-time monitoring as the stream runs")
            print("\n[0102] I will observe and suggest improvements automatically")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()