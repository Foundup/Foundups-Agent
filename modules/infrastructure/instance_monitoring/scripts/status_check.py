#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
import os
from pathlib import Path

# Ensure repo root is on sys.path when running as a script
repo_root = Path(__file__).resolve().parents[4]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

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


def _env_truthy(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "y", "on")


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

        auto_clean = _env_truthy("INSTANCE_LOCK_AUTO_CLEAN_STALE", "true")

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
                    if auto_clean:
                        cleaned = lock.cleanup_stale_lockfile()
                        if cleaned:
                            print("   Action: [OK]Removed stale lock file")

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

        # Check local automation dependencies (Chrome debug + LM Studio)
        print("\n" + "-"*40)
        print("[DEPS] LOCAL AUTOMATION DEPENDENCIES")
        print("-"*40)
        try:
            from modules.infrastructure.dependency_launcher.src.dae_dependencies import (
                get_dependency_status,
            )

            deps = get_dependency_status()
            chrome_port = int(os.getenv("FOUNDUPS_CHROME_PORT", "9222"))
            lm_port = int(os.getenv("LM_STUDIO_PORT", "1234"))

            print(f"   Chrome debug (port {chrome_port}): {'RUNNING' if deps.get('chrome') else 'NOT RUNNING'}")
            print(f"   LM Studio API (port {lm_port}): {'RUNNING' if deps.get('lm_studio') else 'NOT RUNNING'}")
        except Exception as e:
            print(f"[WARN] Dependency status unavailable: {e}")

        # Feature switches (env flags) - helps isolate startup behavior
        print("\n" + "-"*40)
        print("[SWITCHBOARD] FEATURE FLAGS")
        print("-"*40)
        auto_clean = _env_truthy("INSTANCE_LOCK_AUTO_CLEAN_STALE", "true")

        switches = {
            "FOUNDUPS_ENABLE_WRE": _env_truthy("FOUNDUPS_ENABLE_WRE", "true"),
            "FOUNDUPS_ENABLE_WRE_MONITOR": _env_truthy("FOUNDUPS_ENABLE_WRE_MONITOR", "true"),
            "FOUNDUPS_ENABLE_QWEN": _env_truthy("FOUNDUPS_ENABLE_QWEN", "true"),
            "FOUNDUPS_ENABLE_PATTERN_MEMORY": _env_truthy("FOUNDUPS_ENABLE_PATTERN_MEMORY", "true"),
            "FOUNDUPS_ENABLE_SELF_IMPROVEMENT": _env_truthy("FOUNDUPS_ENABLE_SELF_IMPROVEMENT", "true"),
            "FOUNDUPS_ENABLE_SHORTS_COMMANDS": _env_truthy("FOUNDUPS_ENABLE_SHORTS_COMMANDS", "true") and not _env_truthy("FOUNDUPS_DISABLE_SHORTS_COMMANDS", "false"),
            "FOUNDUPS_ENABLE_KEY_HYGIENE": _env_truthy("FOUNDUPS_ENABLE_KEY_HYGIENE", "true"),
            "HOLO_SKIP_MODEL": _env_truthy("HOLO_SKIP_MODEL", "false"),
            "HOLO_SILENT": _env_truthy("HOLO_SILENT", "false"),
        }
        print(json.dumps(switches, indent=2, sort_keys=True))

        # YouTube automation gates snapshot (single source of truth)
        print("\n" + "-"*40)
        print("[SWITCHBOARD] YT AUTOMATION GATES")
        print("-"*40)
        try:
            from modules.communication.livechat.src.automation_gates import gate_snapshot

            print(json.dumps(gate_snapshot(), indent=2, sort_keys=True))
        except Exception as e:
            print(f"[WARN] Automation gate snapshot unavailable: {e}")

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
                        if auto_clean:
                            cleaned = holodae_lock.cleanup_stale_lockfile()
                            if cleaned:
                                print("   Action: [OK]Removed stale lock file")

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
