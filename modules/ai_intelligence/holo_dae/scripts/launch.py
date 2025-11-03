#!/usr/bin/env python3
"""
HoloDAE Launch Script
Extracted from main.py per WSP 62 Large File Refactoring Protocol

Purpose: Launch HoloDAE - Code Intelligence & Monitoring System
Domain: ai_intelligence
Module: holo_dae
"""

import sys
import time
import logging

logger = logging.getLogger(__name__)


def run_holodae():
    """Run HoloDAE (Code Intelligence & Monitoring)."""
    print("[HOLODAE] Starting HoloDAE - Code Intelligence & Monitoring System...")

    # HOLO-DAE INSTANCE LOCKING (First Principles: Resource Protection & Consistency)
    from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock
    lock = get_instance_lock("holodae_monitor")

    # Check for duplicates and acquire lock
    duplicates = lock.check_duplicates()
    if duplicates:
        logger.warning("[REC] Duplicate HoloDAE Instances Detected!")
        print("\n[REC] Duplicate HoloDAE Instances Detected!")
        print(f"\n  Found {len(duplicates)} instances of HoloDAE running:")
        for i, pid in enumerate(duplicates, 1):
            print(f"\n  {i}. PID {pid} - [Checking process details...]")
        print("\n  Current instance will exit to prevent conflicts.")
        print("  Use --no-lock to disable instance locking.")
        return  # Exit if duplicates found

    # Acquire lock for this instance
    if not lock.acquire():
        logger.error("*EFailed to acquire HoloDAE instance lock - another instance is running")
        print("\n*EFailed to acquire HoloDAE instance lock!")
        print("   Another HoloDAE instance is already running.")
        print("   Only one instance can run at a time to prevent index conflicts.")
        print("   Use --no-lock to disable instance locking.")
        return  # Exit if lock acquisition failed

    try:
        from holo_index.qwen_advisor.autonomous_holodae import AutonomousHoloDAE
        holodae = AutonomousHoloDAE()

        # Log successful instance acquisition
        instance_summary = lock.get_instance_summary()
        total_instances = instance_summary["total_instances"]
        current_pid = instance_summary["current_pid"]
        logger.info(f"[INFO]HoloDAE SINGLE INSTANCE: PID {current_pid} - No other HoloDAEs detected")

        holodae.start_autonomous_monitoring()

        print("[HOLODAE] Autonomous monitoring active. Press Ctrl+C to stop.")

        # Keep the process running
        try:
            while holodae.active:
                time.sleep(1)
        except KeyboardInterrupt:
            print("[HOLODAE] Stopping autonomous monitoring...")
            holodae.stop_autonomous_monitoring()
            print("[HOLODAE] HoloDAE stopped successfully")

    except Exception as e:
        print(f"[HOLODAE-ERROR] Failed to start: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Release the instance lock when done
        lock.release()
        logger.info("[LOCK] HoloDAE monitor instance lock released")


if __name__ == "__main__":
    run_holodae()
