#!/usr/bin/env python3
"""
Test WRE autonomous flow manually

This script tests the complete WRE trigger -> execute -> git commit -> social post flow
"""

import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root))

from holo_index.qwen_advisor.holodae_coordinator import HoloDAECoordinator

def test_wre_triggers():
    """Test WRE trigger detection and execution"""
    print("\n[TEST] Initializing HoloDAECoordinator...")
    coordinator = HoloDAECoordinator()

    print("\n[TEST] Checking git health...")
    git_health = coordinator.check_git_health()
    print(f"  Uncommitted changes: {git_health.get('uncommitted_changes', 0)}")
    print(f"  Time since last commit: {git_health.get('time_since_last_commit', 0)} seconds")
    print(f"  Trigger skill: {git_health.get('trigger_skill')}")
    print(f"  Healthy: {git_health.get('healthy')}")

    if not git_health.get('trigger_skill'):
        print("\n[TEST] No WRE triggers detected. Exiting.")
        return

    print("\n[TEST] Running monitoring cycle to get triggers...")
    result = coordinator._run_monitoring_cycle()

    print(f"  Changes detected: {len(result.changes_detected)}")
    print(f"  Actionable: {result.has_actionable_events()}")

    print("\n[TEST] Checking WRE triggers...")
    triggers = coordinator._check_wre_triggers(result)
    print(f"  Triggers found: {len(triggers)}")

    for i, trigger in enumerate(triggers, 1):
        print(f"\n  Trigger {i}:")
        print(f"    Skill: {trigger['skill_name']}")
        print(f"    Agent: {trigger['agent']}")
        print(f"    Reason: {trigger['trigger_reason']}")
        print(f"    Priority: {trigger['priority']}")

    if not triggers:
        print("\n[TEST] No WRE triggers generated. Exiting.")
        return

    print("\n[TEST] Executing WRE skills...")
    coordinator._execute_wre_skills(triggers)

    print("\n[TEST] WRE flow test complete!")

if __name__ == "__main__":
    test_wre_triggers()
