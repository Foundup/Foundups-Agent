"""
Test multi-whack detection with rapid timeouts
"""

import time
from datetime import datetime
from modules.gamification.whack_a_magat.src.timeout_announcer import TimeoutManager

# Create timeout manager
manager = TimeoutManager()

print("=" * 60)
print("TESTING RAPID MULTI-WHACK DETECTION")
print("=" * 60)

# Simulate 4 rapid timeouts from UnDaoDu
targets = ["MAGAT1", "MAGAT2", "MAGAT3", "MAGAT4"]
base_time = time.time()

for i, target in enumerate(targets):
    # Use timestamps that are 2 seconds apart (within multi-whack window)
    event_timestamp = datetime.fromtimestamp(base_time + (i * 2)).isoformat()
    
    print(f"\n--- TIMEOUT #{i+1} at +{i*2}s ---")
    result = manager.record_timeout(
        mod_id="mod_undaodu",
        mod_name="UnDaoDu",
        target_id=f"target_{i}",
        target_name=target,
        duration=300,
        reason="Test timeout",
        timestamp=event_timestamp
    )
    
    print(f"Target: {target}")
    print(f"Announcement: {result.get('announcement')}")
    print(f"Points: {result.get('points_gained')}")
    if result.get('stats'):
        stats = result['stats']
        print(f"Multi-whack: {stats.get('is_multi_whack', False)}")
        print(f"Combo: x{stats.get('combo_multiplier', 1)}")
    
    # Small delay to simulate processing
    time.sleep(0.1)

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)