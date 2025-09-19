#!/usr/bin/env python3
"""
Single Instance Enforcement Utility
WSP 48: Recursive improvement - prevent duplicate processes
WSP 85: Infrastructure utility (not root pollution)
"""

import os
import sys
import time
import psutil
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class SingleInstanceEnforcer:
    """
    Ensures only one instance of a process is running.
    Uses PID file locking with process verification.
    """
    
    def __init__(self, name: str, lock_dir: str = "memory/locks"):
        """
        Initialize single instance enforcer.
        
        Args:
            name: Unique name for this process (e.g., 'youtube_dae')
            lock_dir: Directory to store lock files
        """
        self.name = name
        self.lock_dir = Path(lock_dir)
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        self.lock_file = self.lock_dir / f"{name}.lock"
        self.pid = os.getpid()
        
    def acquire_lock(self, force: bool = False) -> bool:
        """
        Try to acquire exclusive lock for this process.
        
        Args:
            force: If True, kill existing process and take over
            
        Returns:
            True if lock acquired, False otherwise
        """
        # Check if lock file exists
        if self.lock_file.exists():
            try:
                # Read existing PID
                with open(self.lock_file, 'r') as f:
                    old_pid = int(f.read().strip())
                
                # Check if process is still running
                if self._is_process_running(old_pid):
                    # Get process info for better debugging
                    try:
                        process = psutil.Process(old_pid)
                        process_info = f" ({process.name()}, started {process.create_time()})"
                    except:
                        process_info = ""

                    if force:
                        logger.warning(f"🔪 Killing existing {self.name} process (PID: {old_pid}{process_info})")
                        self._kill_process(old_pid)
                        time.sleep(2)  # Wait for process to die
                    else:
                        logger.error(f"❌ {self.name} already running (PID: {old_pid}{process_info})")
                        logger.info(f"💡 Current process trying to start: PID {self.pid}")
                        logger.info(f"💡 Use --force to kill existing process")
                        return False
                else:
                    logger.info(f"🧹 Cleaning stale lock file (PID {old_pid} not running)")
                    
            except (ValueError, IOError) as e:
                logger.warning(f"⚠️ Invalid lock file, removing: {e}")
        
        # Write our PID to lock file
        try:
            with open(self.lock_file, 'w') as f:
                f.write(str(self.pid))
            logger.info(f"🔒 Acquired lock for {self.name} (PID: {self.pid})")
            return True
        except IOError as e:
            logger.error(f"❌ Failed to create lock file: {e}")
            return False
    
    def release_lock(self):
        """
        Release the lock (remove lock file).
        """
        if self.lock_file.exists():
            try:
                # Verify it's our lock
                with open(self.lock_file, 'r') as f:
                    lock_pid = int(f.read().strip())
                
                if lock_pid == self.pid:
                    self.lock_file.unlink()
                    logger.info(f"🔓 Released lock for {self.name}")
                else:
                    logger.warning(f"⚠️ Lock belongs to PID {lock_pid}, not releasing")
            except (ValueError, IOError) as e:
                logger.error(f"❌ Error releasing lock: {e}")
    
    def _is_process_running(self, pid: int) -> bool:
        """
        Check if a process with given PID is running.
        
        Args:
            pid: Process ID to check
            
        Returns:
            True if process exists and is running
        """
        try:
            process = psutil.Process(pid)
            # Check if it's a Python process (not some other reused PID)
            return 'python' in process.name().lower()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def _kill_process(self, pid: int) -> bool:
        """
        Kill a process by PID.
        
        Args:
            pid: Process ID to kill
            
        Returns:
            True if killed successfully
        """
        try:
            process = psutil.Process(pid)
            process.terminate()  # Try graceful termination first
            time.sleep(2)
            
            if process.is_running():
                process.kill()  # Force kill if still running
                
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.warning(f"⚠️ Could not kill process {pid}: {e}")
            return False
    
    def check_status(self) -> Optional[int]:
        """
        Check if an instance is running.

        Returns:
            PID of running instance, or None if not running
        """
        if self.lock_file.exists():
            try:
                with open(self.lock_file, 'r') as f:
                    pid = int(f.read().strip())

                if self._is_process_running(pid):
                    return pid
            except (ValueError, IOError):
                pass

        return None

    def is_locked(self) -> bool:
        """
        Check if lock is currently held by another process.

        Returns:
            True if locked by another process, False otherwise
        """
        return self.check_status() is not None

    def force_acquire(self) -> bool:
        """
        Force acquire the lock by killing existing process if needed.

        Returns:
            True if lock acquired successfully
        """
        return self.acquire_lock(force=True)
    
    def __enter__(self):
        """Context manager entry."""
        if not self.acquire_lock():
            sys.exit(1)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - always release lock."""
        self.release_lock()


def enforce_single_instance(name: str, force: bool = False) -> SingleInstanceEnforcer:
    """
    Convenience function to enforce single instance.
    
    Args:
        name: Process name
        force: Kill existing if running
        
    Returns:
        SingleInstanceEnforcer object (use as context manager)
    """
    enforcer = SingleInstanceEnforcer(name)
    
    # Check current status
    existing_pid = enforcer.check_status()
    if existing_pid:
        logger.warning(f"⚠️ {name} is already running (PID: {existing_pid})")
        if not force:
            logger.error("❌ Exiting to prevent duplicate instance")
            logger.info("💡 Use --force flag to kill existing instance")
            sys.exit(1)
    
    return enforcer


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test single instance
    with SingleInstanceEnforcer("test_process") as lock:
        logger.info("Process running with exclusive lock")
        logger.info("Try running another instance - it will be blocked")
        time.sleep(10)
    
    logger.info("Lock released, process ended")
