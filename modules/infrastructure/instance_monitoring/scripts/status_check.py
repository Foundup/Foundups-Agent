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

Instance Status Checker
Extracted from main.py per WSP 62 Large File Refactoring Protocol

Purpose: Check status and health of running instances
Domain: infrastructure
Module: instance_monitoring

Function:
- check_instance_status: Check status of YouTube monitor and HoloDAE instances
"""

import json


def check_instance_status():
    """Check the status and health of running instances."""
    print("\n" + "="*60)
    print("[INFO] INSTANCE STATUS CHECK")
    print("="*60)

    try:
        from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock

        lock = get_instance_lock("youtube_monitor")

        # Check for running instances
        duplicates = lock.check_duplicates()

        if duplicates:
            print(f"[ERROR]Found {len(duplicates)} duplicate instances running")
            return
        else:
            print("[INFO]No duplicate instances detected")

        # Check lock file status
        if lock.lock_file.exists():
            print("[INFO] Lock file exists:")
            try:
                with open(lock.lock_file, 'r') as f:
                    lock_data = json.load(f)
                pid = lock_data.get('pid')
                heartbeat = lock_data.get('heartbeat', 'Unknown')
                start_time = lock_data.get('start_time', 'Unknown')

                print(f"   PID: {pid}")
                print(f"   Started: {start_time}")
                print(f"   Last heartbeat: {heartbeat}")

                # Check if process is actually running
                if lock._is_process_running(pid):
                    print("   Status: [INFO]RUNNING")
                else:
                    print("   Status: [ERROR]PROCESS NOT FOUND (stale lock)")

            except Exception as e:
                print(f"   Error reading lock file: {e}")
        else:
            print("[LOCK] No lock file found (no instances running)")

        # Check health status
        health = lock.get_health_status()
        print("\n[INFO] Health Status:")
        print(f"   Status: {health.get('status', 'unknown')}")
        print(f"   Message: {health.get('message', 'no data')}")
        if 'timestamp' in health:
            print(f"   Last update: {health['timestamp']}")

        # Check HoloDAE instances
        print("\n" + "-"*40)
        print("[MENU]HOLO-DAE STATUS")
        print("-"*40)

        try:
            holodae_lock = get_instance_lock("holodae_monitor")

            # Check for running HoloDAE instances
            holodae_duplicates = holodae_lock.check_duplicates()

            if holodae_duplicates:
                print(f"[ERROR]Found {len(holodae_duplicates)} HoloDAE instances running")
                return
            else:
                print("[INFO]No duplicate HoloDAE instances detected")

            # Check HoloDAE lock file status
            if holodae_lock.lock_file.exists():
                print("[INFO] HoloDAE Lock file exists:")
                try:
                    with open(holodae_lock.lock_file, 'r') as f:
                        lock_data = json.load(f)
                    pid = lock_data.get('pid')
                    heartbeat = lock_data.get('heartbeat', 'Unknown')
                    start_time = lock_data.get('start_time', 'Unknown')

                    print(f"   PID: {pid}")
                    print(f"   Started: {start_time}")
                    print(f"   Last heartbeat: {heartbeat}")

                    # Check if process is actually running
                    if holodae_lock._is_process_running(pid):
                        print("   Status: [INFO]RUNNING")
                    else:
                        print("   Status: [ERROR]PROCESS NOT FOUND (stale lock)")

                except Exception as e:
                    print(f"   Error reading lock file: {e}")
            else:
                print("[LOCK] No HoloDAE lock file found (no instances running)")

            # Check HoloDAE health status
            holodae_health = holodae_lock.get_health_status()
            print("\n[INFO] HoloDAE Health Status:")
            print(f"   Status: {holodae_health.get('status', 'unknown')}")
            print(f"   Message: {holodae_health.get('message', 'no data')}")
            if 'timestamp' in holodae_health:
                print(f"   Last update: {holodae_health['timestamp']}")

        except Exception as e:
            print(f"[ERROR]Error checking HoloDAE status: {e}")

    except Exception as e:
        print(f"[ERROR]Error checking status: {e}")

    print()


if __name__ == "__main__":
    check_instance_status()
