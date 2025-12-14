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

Instance Lock Manager - prevents multiple YouTube monitor instances.
"""

import json
import logging
import os
from pathlib import Path
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

import psutil

logger = logging.getLogger(__name__)

EPOCH_ISO = datetime.fromtimestamp(0).isoformat()

class InstanceLock:
    """Manage a single running instance via PID lock file and heartbeats with enhanced monitoring."""

    def __init__(self, lock_name: str = "youtube_monitor", ttl_minutes: int = 10):
        self.lock_name = lock_name
        self.lock_file = Path("memory") / f"{lock_name}.lock"
        self.health_file = Path("memory") / f"{lock_name}_health.json"
        self.pid = os.getpid()
        self.ttl_minutes = ttl_minutes
        self.heartbeat_interval = 30
        self.health_check_interval = 60  # Check health every minute
        self.heartbeat_thread: Optional[threading.Thread] = None
        self.health_thread: Optional[threading.Thread] = None
        self.running = False
        self.last_health_update = datetime.now()

    @staticmethod
    def _normalize_lock_data(raw_data) -> Dict[str, Optional[str]]:
        """Normalize legacy lock file formats into a dictionary."""
        if isinstance(raw_data, dict):
            return raw_data
        if isinstance(raw_data, int):
            return {
                "pid": raw_data,
                "heartbeat": EPOCH_ISO
            }
        if isinstance(raw_data, str):
            cleaned = raw_data.strip()
            try:
                pid_value = int(cleaned)
            except ValueError:
                logger.warning("Legacy lock string not convertible to PID: %s", cleaned)
                return {}
            return {
                "pid": pid_value,
                "heartbeat": EPOCH_ISO
            }
        logger.warning("Unsupported lock file format: %s", type(raw_data))
        return {}

    def acquire(self, auto_cleanup: bool = True) -> bool:
        """Attempt to acquire the lock. Returns True when successful."""
        if auto_cleanup:
            self._cleanup_stale_processes()

        if self.lock_file.exists():
            try:
                with open(self.lock_file, "r", encoding="utf-8") as handle:
                    raw_data = json.load(handle)
                lock_data = self._normalize_lock_data(raw_data)
            except (OSError, json.JSONDecodeError, UnicodeDecodeError) as error:
                logger.warning("Invalid lock file detected (%s); recreating.", error)
                lock_data = {}
            pid = lock_data.get("pid")
            heartbeat_iso = lock_data.get("heartbeat", EPOCH_ISO)
            try:
                last_heartbeat = datetime.fromisoformat(heartbeat_iso)
            except ValueError:
                last_heartbeat = datetime.fromtimestamp(0)

            if pid and self._is_process_running(pid):
                if datetime.now() - last_heartbeat > timedelta(minutes=self.ttl_minutes):
                    if self._is_our_process(pid):
                        logger.warning("Lock expired; terminating stale process %s", pid)
                        self._kill_process(pid)
                    else:
                        logger.info("Lock held by unrelated process; removing stale file")
                        self.lock_file.unlink(missing_ok=True)
                else:
                    if self._is_our_process(pid):
                        logger.warning("YouTube monitor already running (PID %s)", pid)
                        logger.warning("Kill duplicates with: taskkill /F /PID %s", pid)
                        return False
            else:
                logger.info("Previous PID %s not active; reusing lock", pid)

        self._write_lock_file()
        self._start_heartbeat()
        logger.info("Instance lock acquired (PID %s)", self.pid)
        return True

    def release(self) -> None:
        """Stop heartbeat and remove lock if we own it."""
        try:
            self._stop_heartbeat()
            if self.lock_file.exists():
                lock_pid = None
                try:
                    with open(self.lock_file, "r", encoding="utf-8") as handle:
                        raw_data = json.load(handle)
                    lock_pid = self._normalize_lock_data(raw_data).get("pid")
                except (OSError, json.JSONDecodeError, UnicodeDecodeError) as error:
                    logger.warning("Could not read lock file on release: %s", error)

                if lock_pid == self.pid or lock_pid is None:
                    self.lock_file.unlink(missing_ok=True)
                    logger.info("Instance lock released (PID %s)", self.pid)
                else:
                    logger.warning("Lock owned by PID %s; not removing", lock_pid)
        except Exception as error:
            logger.error("Error releasing lock: %s", error)

    def _write_lock_file(self) -> None:
        lock_data: Dict[str, Optional[str]] = {
            "pid": self.pid,
            "heartbeat": datetime.now().isoformat(),
            "start_time": datetime.now().isoformat()
        }
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.lock_file, "w", encoding="utf-8") as handle:
            json.dump(lock_data, handle, indent=2)

    def _start_heartbeat(self) -> None:
        """Start heartbeat thread (health monitoring disabled for stability)."""
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            return
        self.running = True

        # Start heartbeat thread
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()

        # Health monitoring temporarily disabled due to os.stat issues
        # self.health_thread = threading.Thread(target=self._health_monitor_loop, daemon=True)
        # self.health_thread.start()
        # self._update_health_status("healthy", "Instance started successfully")

    def _stop_heartbeat(self) -> None:
        """Stop heartbeat thread."""
        self.running = False

        # Stop heartbeat thread
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=2)
            self.heartbeat_thread = None

        # Health monitoring disabled
        # if self.health_thread:
        #     self.health_thread.join(timeout=2)
        #     self.health_thread = None

    def _heartbeat_loop(self) -> None:
        while self.running:
            time.sleep(self.heartbeat_interval)
            if not self.running:
                break
            try:
                if self.lock_file.exists():
                    with open(self.lock_file, "r", encoding="utf-8") as handle:
                        raw_data = json.load(handle)
                    lock_data = self._normalize_lock_data(raw_data)
                    lock_data["heartbeat"] = datetime.now().isoformat()
                    with open(self.lock_file, "w", encoding="utf-8") as handle:
                        json.dump(lock_data, handle, indent=2)
            except Exception as error:
                logger.warning("Failed to update heartbeat: %s", error)
                self._update_health_status("warning", f"Heartbeat update failed: {error}")

    def _health_monitor_loop(self) -> None:
        """Monitor instance health and clean up stale resources."""
        while self.running:
            try:
                time.sleep(self.health_check_interval)

                if not self.running:
                    break

                # Check if our process is still healthy
                if not self._is_process_running(self.pid):
                    logger.critical("Instance process died unexpectedly!")
                    self._update_health_status("critical", "Process died unexpectedly")
                    break

                # Update health status
                self._update_health_status("healthy", "Instance running normally")
                self.last_health_update = datetime.now()

                # Clean up any stale processes or locks
                self._cleanup_stale_processes()

            except Exception as error:
                logger.error("Health monitor error: %s", error)
                self._update_health_status("error", f"Health monitor error: {error}")

    def _update_health_status(self, status: str, message: str) -> None:
        """Update the health status file."""
        # Calculate uptime safely
        uptime_seconds = 0
        try:
            if self.lock_file.exists():
                # Get creation time of lock file as approximate start time
                start_time = os.path.getctime(str(self.lock_file))
                uptime_seconds = time.time() - start_time
        except Exception:
            # If we can't calculate uptime, use 0
            uptime_seconds = 0

        health_data = {
            "pid": self.pid,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "last_heartbeat": datetime.now().isoformat(),
            "uptime_seconds": uptime_seconds
        }

        try:
            self.health_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.health_file, "w", encoding="utf-8") as handle:
                json.dump(health_data, handle, indent=2)
        except Exception as error:
            logger.warning("Failed to update health status: %s", error)

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status (disabled for stability)."""
        return {
            "status": "disabled",
            "message": "Health monitoring temporarily disabled due to os.stat issues",
            "timestamp": datetime.now().isoformat()
        }

    def cleanup_browser_windows(self) -> int:
        """Find and close any stale browser windows from social media posting.
        Returns the number of browser processes closed."""
        closed_count = 0
        browser_names = ["chrome.exe", "msedge.exe", "msedgedriver.exe", "chromedriver.exe"]

        logger.info("[SEARCH] Checking for stale browser windows...")

        for process in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                process_name = process.info.get("name", "").lower()
                cmdline = process.info.get("cmdline") or []
                cmdline_str = " ".join(cmdline).lower()

                # Check if it's a browser process
                if any(browser in process_name for browser in browser_names):
                    # Check if it's related to our automation (look for specific profiles)
                    if any(marker in cmdline_str for marker in [
                        "edge_profile_foundups",
                        "chrome_profile",
                        "linkedin_agent",
                        "x_twitter",
                        "--remote-debugging",
                        "user-data-dir"
                    ]):
                        pid = process.info.get("pid")
                        logger.warning(f"[ALERT] Found stale browser: {process_name} (PID: {pid})")
                        try:
                            process.terminate()
                            closed_count += 1
                            logger.info(f"[OK] Terminated {process_name} (PID: {pid})")
                        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                            logger.warning(f"Could not terminate {process_name}: {e}")

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if closed_count > 0:
            logger.info(f"[U+1F9F9] Cleaned up {closed_count} stale browser window(s)")
        else:
            logger.info("[OK] No stale browser windows found")

        return closed_count

    def _cleanup_stale_processes(self) -> None:
        # First cleanup any stale browser windows
        self.cleanup_browser_windows()

        # Also cleanup any orphaned Python processes from previous sessions
        # This includes background shells that weren't properly terminated
        stale_pids = []
        for process in psutil.process_iter(["pid", "cmdline", "create_time", "name"]):
            pid = process.info.get("pid")
            if pid == self.pid:
                continue

            # Check for Python processes
            process_name = process.info.get("name", "").lower()
            cmdline = process.info.get("cmdline") or []

            # Kill any Python process that looks like our monitor or orphaned background process
            if "python" in process_name:
                # Check if it's our monitor process
                if self._looks_like_monitor(cmdline):
                    create_time = process.info.get("create_time")
                    if create_time is None:
                        continue
                    age_minutes = (datetime.now() - datetime.fromtimestamp(create_time)).total_seconds() / 60
                    if age_minutes > self.ttl_minutes:
                        # FIX: Check if this process has an active heartbeat before killing
                        if self._has_active_heartbeat(pid):
                            logger.info("Monitor %s is old (%.1f min) but heartbeat active - keeping alive", pid, age_minutes)
                            continue
                        stale_pids.append(pid)
                        logger.warning("Found stale monitor process %s (age: %.1f minutes)", pid, age_minutes)
                # Also check for orphaned main.py processes that aren't the current one
                elif any("main.py" in str(arg) for arg in cmdline):
                    create_time = process.info.get("create_time")
                    if create_time:
                        age_minutes = (datetime.now() - datetime.fromtimestamp(create_time)).total_seconds() / 60
                        # Kill if older than 1 minute and not the current process
                        if age_minutes > 1:
                            stale_pids.append(pid)
                            logger.warning("Found orphaned main.py process %s (age: %.1f minutes)", pid, age_minutes)

        for pid in stale_pids:
            logger.warning("Killing stale process %s", pid)
            self._kill_process(pid)

    @staticmethod
    def _kill_process(pid: int) -> None:
        try:
            process = psutil.Process(pid)
            process.terminate()
            try:
                process.wait(timeout=3)
            except psutil.TimeoutExpired:
                process.kill()
        except Exception as error:
            logger.error("Failed to kill process %s: %s", pid, error)

    @staticmethod
    def _is_process_running(pid: int) -> bool:
        try:
            proc = psutil.Process(pid)
            return proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return False

    def _is_our_process(self, pid: int) -> bool:
        try:
            process = psutil.Process(pid)
            return self._looks_like_monitor(process.cmdline())
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return False

    def _has_active_heartbeat(self, pid: int) -> bool:
        """Check if a process has an active heartbeat (updated within TTL)."""
        if not self.lock_file.exists():
            return False

        try:
            with open(self.lock_file, "r", encoding="utf-8") as handle:
                raw_data = json.load(handle)
            lock_data = self._normalize_lock_data(raw_data)

            # Check if this PID owns the lock
            lock_pid = lock_data.get("pid")
            if lock_pid != pid:
                return False

            # Check heartbeat timestamp
            heartbeat_iso = lock_data.get("heartbeat", EPOCH_ISO)
            try:
                last_heartbeat = datetime.fromisoformat(heartbeat_iso)
            except ValueError:
                return False

            # Heartbeat is active if updated within TTL
            age_minutes = (datetime.now() - last_heartbeat).total_seconds() / 60
            return age_minutes <= self.ttl_minutes

        except (OSError, json.JSONDecodeError, UnicodeDecodeError, KeyError):
            return False

    @staticmethod
    def _looks_like_monitor(cmdline) -> bool:
        if not cmdline:
            return False
        lowered = [part.lower() for part in cmdline]
        # Look for main.py script OR auto_moderator_dae direct invocation
        has_main_py = any("main.py" in part for part in lowered)
        has_auto_moderator = any("auto_moderator_dae" in part for part in lowered)
        # Accept any main.py process OR auto_moderator_dae invocation as a DAE instance
        return has_main_py or has_auto_moderator

    @staticmethod
    def _is_python_process_info(process_info: dict) -> bool:
        """
        Best-effort check that the OS process is a Python interpreter.

        On Windows it's common to see parent shells (e.g. bash.exe) whose cmdline
        *contains* "python main.py ...". Those shells must NOT be treated as DAE
        instances; only the actual python.exe/pythonw.exe process counts.
        """
        if not process_info:
            return False

        name = (process_info.get("name") or "").lower()
        exe = (process_info.get("exe") or "").lower()
        cmdline = process_info.get("cmdline") or []
        cmd0 = str(cmdline[0]).lower() if cmdline else ""

        if "python" in name:
            return True

        # Common interpreter executables across platforms
        if exe.endswith(("python.exe", "pythonw.exe", "python", "python3", "python3.exe")):
            return True

        # Some process listings expose the interpreter in argv[0]
        if cmd0.endswith(("python.exe", "pythonw.exe", "python", "python3", "python3.exe")):
            return True

        # Fallback: argv[0] can be a full path; check substring
        return "python" in cmd0

    def check_duplicates(self, quiet: bool = False) -> list[int]:
        duplicates = []
        current_pid = os.getpid()
        duplicate_details = []

        for process in psutil.process_iter(["pid", "name", "cmdline", "create_time", "exe"]):
            pid = process.info.get("pid")
            if pid == current_pid:
                continue

            cmdline = process.info.get("cmdline")
            if not cmdline:
                continue

            # Only count actual Python interpreter processes. This prevents false
            # positives from parent shells (bash/cmd/powershell) that *contain*
            # a python invocation in their argv.
            if not self._is_python_process_info(process.info):
                continue

            # Only detect duplicates if they're actually running the YouTube DAE
            # Check for --youtube flag or asyncio.run(monitor_youtube in the command
            is_youtube_dae = False
            cmdline_str = " ".join(str(arg) for arg in cmdline).lower()

            # Check if this is actually running YouTube DAE (not just the menu)
            if self._looks_like_monitor(cmdline):
                # Additional check: must have --youtube flag OR be running auto_moderator_dae
                if "--youtube" in cmdline_str or "auto_moderator_dae" in cmdline_str:
                    is_youtube_dae = True
                # Also check if there's an existing lock file pointing to this PID
                elif self.lock_file.exists():
                    try:
                        with open(self.lock_file, "r", encoding="utf-8") as f:
                            lock_data = json.load(f)
                            if lock_data.get("pid") == pid:
                                is_youtube_dae = True
                    except:
                        pass

            if is_youtube_dae:
                duplicates.append(pid)

                # Get detailed process info
                create_time = process.info.get("create_time")
                exe = process.info.get("exe", "Unknown")
                cmdline = process.info.get("cmdline", [])

                start_time = "Unknown"
                if create_time:
                    start_time = datetime.fromtimestamp(create_time).strftime("%Y-%m-%d %H:%M:%S")

                # Determine if it's venv or system Python
                python_type = "Unknown"
                if exe:
                    if "venv" in exe.lower() or ".venv" in exe:
                        python_type = "Virtual environment"
                    elif exe.lower().endswith("python.exe"):
                        python_type = "System Python"
                    else:
                        python_type = "Other Python"

                duplicate_details.append({
                    "pid": pid,
                    "start_time": start_time,
                    "python_type": python_type,
                    "exe": exe,
                    "cmdline": " ".join(cmdline) if cmdline else "Unknown"
                })

        if duplicates:
            logger.warning("Found duplicate YouTube monitors: %s", duplicates)
            # Only show detailed output if not in quiet mode (for menu usage)
            if not quiet:
                print("\n[U+1F534] Duplicate main.py Instances Detected!")
                print(f"\n  Found {len(duplicates)} instances of main.py running:")
                print()

                for i, detail in enumerate(duplicate_details, 1):
                    print(f"  {i}. PID {detail['pid']} - {detail['exe']}")
                    print(f"    - Started: {detail['start_time']}")
                    print(f"    - Using {detail['python_type']}")

                print(f"\n  Current PID: {current_pid} (this instance)")
                print("\n  Kill duplicates with:")
                for pid in duplicates:
                    print(f"    taskkill /F /PID {pid}")
                print()

        return duplicates

    def kill_pids(self, pids: list[int], wait_seconds: float = 1.0) -> Dict[str, Any]:
        """
        Terminate a list of PIDs best-effort and report results.

        This is used by 012 automation to deterministically clear stale/duplicate
        DAEs and continue launching without interactive prompts.
        """
        killed: list[int] = []
        failed: Dict[int, str] = {}

        for pid in pids:
            try:
                if pid == self.pid:
                    continue
                self._kill_process(pid)
                killed.append(pid)
            except Exception as error:
                failed[pid] = str(error)

        if wait_seconds:
            try:
                time.sleep(wait_seconds)
            except Exception:
                pass

        still_running = [pid for pid in pids if pid != self.pid and self._is_process_running(pid)]

        return {
            "requested": list(pids),
            "killed": killed,
            "failed": failed,
            "still_running": still_running,
        }

    def get_instance_summary(self) -> Dict[str, Any]:
        """Get a summary of all running instances for logging"""
        current_pid = os.getpid()
        instances = []

        for process in psutil.process_iter(["pid", "name", "cmdline", "create_time", "exe", "cpu_percent", "memory_info"]):
            pid = process.info.get("pid")
            if not self._is_python_process_info(process.info):
                continue

            if self._looks_like_monitor(process.info.get("cmdline")):
                # Get detailed process info
                create_time = process.info.get("create_time")
                exe = process.info.get("exe", "Unknown")
                cmdline = process.info.get("cmdline", [])

                start_time = "Unknown"
                age_minutes = 0
                if create_time:
                    start_time = datetime.fromtimestamp(create_time).strftime("%Y-%m-%d %H:%M:%S")
                    age_minutes = (datetime.now() - datetime.fromtimestamp(create_time)).total_seconds() / 60

                # Determine if it's venv or system Python
                python_type = "Unknown"
                if exe:
                    if "venv" in exe.lower() or ".venv" in exe:
                        python_type = "Virtual environment"
                    elif exe.lower().endswith("python.exe"):
                        python_type = "System Python"
                    else:
                        python_type = "Other Python"

                # Get resource usage
                cpu_percent = "Unknown"
                memory_mb = "Unknown"
                try:
                    cpu_percent = f"{process.info.get('cpu_percent', 'N/A')}%"
                    memory_info = process.info.get("memory_info")
                    if memory_info:
                        memory_mb = f"{memory_info.rss / 1024 / 1024:.1f}MB"
                except:
                    pass

                instance_info = {
                    "pid": pid,
                    "is_current": pid == current_pid,
                    "start_time": start_time,
                    "age_minutes": age_minutes,
                    "python_type": python_type,
                    "exe": exe,
                    "cpu_percent": cpu_percent,
                    "memory_mb": memory_mb,
                    "cmdline": " ".join(cmdline) if cmdline else "Unknown"
                }
                instances.append(instance_info)

        return {
            "total_instances": len(instances),
            "current_pid": current_pid,
            "instances": instances,
            "timestamp": datetime.now().isoformat()
        }

    def __enter__(self):
        if not self.acquire():
            raise SystemExit(1)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

_instance_lock: Optional[InstanceLock] = None

def get_instance_lock(lock_name: str = "youtube_monitor") -> InstanceLock:
    global _instance_lock
    if _instance_lock is None or _instance_lock.lock_name != lock_name:
        _instance_lock = InstanceLock(lock_name)
    return _instance_lock

def check_single_instance() -> bool:
    lock = get_instance_lock()
    return len(lock.check_duplicates()) == 0



