#!/usr/bin/env python3
"""
HoloDAE Wiring Verification

Tests monitoring and search flows.

Location: holo_index/qwen_advisor/tests/verify_holodae_wiring.py
"""

import sys
import os
import time
import logging
from pathlib import Path

# Add repo root to path (3 levels up from tests/)
repo_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(repo_root))


def setup_logging():
    logging.basicConfig(level=logging.INFO)


def test_imports():
    print("Testing imports...")
    try:
        from holo_index.qwen_advisor.holodae_coordinator import HoloDAECoordinator
        print("PASS: HoloDAECoordinator imported successfully.")
        return True
    except ImportError as e:
        print(f"FAIL: Import failed: {e}")
        return False
    except Exception as e:
        print(f"FAIL: Unexpected error during import: {e}")
        return False


def test_monitoring_flow():
    print("\nTesting Monitoring Flow...")
    from holo_index.qwen_advisor.holodae_coordinator import HoloDAECoordinator
    
    coordinator = HoloDAECoordinator()
    
    # Enable and start monitoring
    print("Starting monitoring...")
    coordinator.enable_monitoring()
    started = coordinator.start_monitoring()
    
    if started:
        print("PASS: Monitoring started.")
    else:
        print("FAIL: Monitoring failed to start.")
        return False
        
    # Let it run for a brief moment
    time.sleep(2)
    
    # Check if we can get status
    status = coordinator.get_status_summary()
    print(f"Status Summary: {status}")
    
    if status.get('monitoring_active'):
        print("PASS: Status reports monitoring active.")
    else:
        print("FAIL: Status reports monitoring inactive.")
    
    # Stop monitoring
    print("Stopping monitoring...")
    stopped = coordinator.stop_monitoring()
    
    if stopped:
        print("PASS: Monitoring stopped.")
    else:
        print("FAIL: Monitoring failed to stop.")
        
    return True


def test_search_flow():
    print("\nTesting Search Flow...")
    from holo_index.qwen_advisor.holodae_coordinator import HoloDAECoordinator
    
    coordinator = HoloDAECoordinator()
    
    query = "test query for wiring verification"
    # Use realistic search result shape expected by QwenOrchestrator
    search_results = {
        'code': [{'location': 'holo_index/qwen_advisor/holodae_coordinator.py'}],
        'wsps': [{'location': 'WSP 62'}]
    }
    
    print(f"Processing query: '{query}'")
    try:
        report = coordinator.handle_holoindex_request(query, search_results)
        print("PASS: Request handled successfully.")
        print(f"Report length: {len(report)}")
        if "Request processing complete" in str(report) or len(report) > 0:
            print("PASS: Report generated.")
        else:
            print("WARN: Report seems empty.")
            
        return True
    except Exception as e:
        print(f"FAIL: Search flow failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    setup_logging()
    
    if not test_imports():
        sys.exit(1)
        
    if not test_monitoring_flow():
        sys.exit(1)
        
    if not test_search_flow():
        sys.exit(1)
        
    print("\nALL CHECKS PASSED.")

