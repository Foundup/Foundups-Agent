"""
Test timeout announcement format locally
"""

import time
from modules.gamification.whack_a_magat.src.timeout_announcer import TimeoutManager

# Create timeout manager
manager = TimeoutManager()

# Simulate a timeout from UnDaoDu
result = manager.record_timeout(
    mod_id="mod_123",
    mod_name="UnDaoDu",
    target_id="target_456",
    target_name="TestMAGAT",
    duration=300,
    reason="Test timeout",
    timestamp=None
)

print("=" * 60)
print("TIMEOUT RESULT:")
print("=" * 60)
print(f"Announcement: {result.get('announcement')}")
print(f"Points: {result.get('points_gained')}")
print(f"Stats: {result.get('stats')}")
print("=" * 60)

# Test rapid fire mockery
time.sleep(0.1)
result2 = manager.record_timeout(
    mod_id="mod_123",
    mod_name="UnDaoDu", 
    target_id="target_789",
    target_name="AnotherMAGAT",
    duration=300,
    reason="Test timeout 2",
    timestamp=None
)

print("\nRAPID FIRE RESULT:")
print("=" * 60)
print(f"Announcement: {result2.get('announcement')}")
print("=" * 60)