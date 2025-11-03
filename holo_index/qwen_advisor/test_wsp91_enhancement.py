#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io

"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

Test WSP 91 Enhancement to ChainOfThoughtLogger
Validates that wsps_followed parameter works correctly
"""

import sys
import os

# Redirect stdout to avoid Unicode errors on Windows
class SafeWriter:
    def write(self, text):
        try:
            sys.__stdout__.write(text)
        except UnicodeEncodeError:
            sys.__stdout__.write(text.encode('ascii', 'ignore').decode('ascii'))

    def flush(self):
        sys.__stdout__.flush()

sys.stdout = SafeWriter()

# Import the logger
from chain_of_thought_logger import (
    ChainOfThoughtLogger,
    start_cot_logging,
    log_cot_decision,
    log_cot_analysis,
    log_cot_action,
    log_cot_improvement,
    end_cot_logging
)

def test_wsp91_tracking():
    """Test that WSP tracking works correctly"""

    print("\n" + "="*60)
    print("WSP 91 ENHANCEMENT TEST")
    print("="*60)

    # Start session
    session_id = start_cot_logging("Test WSP 91 compliance tracking", slow_mode=False)
    print(f"\nSession started: {session_id}")

    # Test 1: Analysis with WSP tracking
    print("\n[TEST 1] Analysis with WSP tracking")
    log_cot_analysis(
        "wsp_protocol_check",
        {"protocols": ["WSP 50", "WSP 84", "WSP 91"]},
        "Verifying WSP compliance before operation",
        0.95,
        wsps_followed=["WSP 50", "WSP 84", "WSP 91"]
    )

    # Test 2: Decision with WSP tracking
    print("\n[TEST 2] Decision with WSP tracking")
    log_cot_decision(
        "use_existing_logger",
        ["Create new logger", "Enhance existing logger"],
        "Following WSP 84: Remember existing code, don't compute new",
        0.98,
        wsps_followed=["WSP 84", "WSP 50", "WSP 64"]
    )

    # Test 3: Action with WSP tracking
    print("\n[TEST 3] Action with WSP tracking")
    log_cot_action(
        "enhance_ChainOfThoughtLogger",
        "chain_of_thought_logger.py",
        "Add wsps_followed parameter to all logging methods",
        "Enhancing existing code per WSP 84",
        0.92,
        wsps_followed=["WSP 84", "WSP 91"]
    )

    # Test 4: Improvement with WSP tracking
    print("\n[TEST 4] Recursive improvement with WSP tracking")
    log_cot_improvement(
        "vibecoding_prevention",
        "Created duplicate logger (vibecoding)",
        "Enhanced existing logger (proper WSP compliance)",
        "Learned to enhance existing code instead of duplicating",
        wsps_followed=["WSP 48", "WSP 84", "WSP 91"]
    )

    # End session
    summary = end_cot_logging("WSP 91 enhancement validated", 0.96)

    # Validate results
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"Session ID: {summary['session_id']}")
    print(f"Total Steps: {summary['steps']}")
    print(f"Effectiveness: {summary['effectiveness']:.2f}")
    print(f"Duration: {summary['duration']:.2f}s")

    # Check that WSP tracking worked
    logger = ChainOfThoughtLogger(log_file="test_wsp91.log", slow_mode=False)
    logger.current_session = None  # Get from history

    print("\n[VALIDATION] Checking WSP tracking in session history...")

    # Get the logger instance that ran the test
    from chain_of_thought_logger import get_chain_of_thought_logger
    test_logger = get_chain_of_thought_logger()

    if test_logger.session_history:
        last_session = test_logger.session_history[-1]
        wsp_tracked_steps = [
            step for step in last_session.thought_chain
            if step.wsps_followed
        ]

        print(f"Steps with WSP tracking: {len(wsp_tracked_steps)} / {len(last_session.thought_chain)}")

        # Show which WSPs were tracked
        all_wsps = set()
        for step in wsp_tracked_steps:
            all_wsps.update(step.wsps_followed)

        print(f"WSPs tracked: {', '.join(sorted(all_wsps))}")

        if len(wsp_tracked_steps) >= 4:  # We logged 4 steps with WSPs
            print("\n[SUCCESS] WSP 91 compliance tracking is working correctly!")
            print("[SUCCESS] ChainOfThoughtLogger enhancement complete!")
            return True
        else:
            print("\n[ERROR] WSP tracking not found in all expected steps")
            return False
    else:
        print("\n[ERROR] No session history found")
        return False

if __name__ == "__main__":
    success = test_wsp91_tracking()
    sys.exit(0 if success else 1)
