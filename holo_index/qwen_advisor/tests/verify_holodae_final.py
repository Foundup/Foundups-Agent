#!/usr/bin/env python3
"""
HoloDAE Final Verification

Verifies HoloDAECoordinator initialization and service delegation.

Location: holo_index/qwen_advisor/tests/verify_holodae_final.py
"""

import sys
import os
import logging
from pathlib import Path

# Add repo root to path (3 levels up from tests/)
repo_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(repo_root))

# Configure logging
logging.basicConfig(level=logging.INFO)

print("=== HoloDAE Final Verification ===")

try:
    print("\n1. Importing HoloDAECoordinator...")
    from holo_index.qwen_advisor.holodae_coordinator import HoloDAECoordinator
    print("   [OK] Import successful")

    print("\n2. Importing Legacy Functions...")
    from holo_index.qwen_advisor import (
        start_holodae,
        stop_holodae,
        get_holodae_status,
        show_holodae_menu
    )
    print("   [OK] Legacy functions imported")

    print("\n3. Initializing Coordinator...")
    coordinator = HoloDAECoordinator()
    print("   [OK] Initialization successful")

    print("\n4. Checking Service Delegation...")
    # Check if services are initialized (using hasattr for safety)
    services = [
        ('pid_detective', 'pid_detective'),
        ('telemetry_formatter', 'telemetry_formatter'),
        ('module_metrics', 'module_metrics'),
        ('monitoring_loop', 'monitoring_loop'),
        ('skill_executor', 'skill_executor')
    ]
    
    for name, attr in services:
        if hasattr(coordinator, attr) and getattr(coordinator, attr):
            print(f"   [OK] Service '{name}' initialized")
        else:
            print(f"   [WARN] Service '{name}' NOT initialized (may be optional)")

    print("\n5. Checking WRE Integration...")
    if hasattr(coordinator, 'skill_executor') and coordinator.skill_executor:
        print("   [OK] SkillExecutor present")
        # Check if LibidoMonitor is wired (if available)
        if hasattr(coordinator.skill_executor, 'libido_monitor'):
            if coordinator.skill_executor.libido_monitor:
                print("   [OK] LibidoMonitor wired in SkillExecutor")
            else:
                print("   [WARN] LibidoMonitor NOT wired (Module missing or bypass mode)")
    else:
        print("   [WARN] SkillExecutor missing (may be optional)")

    print("\n=== Verification Complete ===")

except Exception as e:
    print(f"\n[ERROR] Verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

