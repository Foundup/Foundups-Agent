#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

Quick test to verify instance lock prevents duplicate YouTube monitors.
"""

import sys
import os
import subprocess
import time

def test_instance_lock():
    """Test that instance lock prevents multiple instances."""
    print("[LOCK] Testing Instance Lock Prevention")
    print("=" * 50)

    # Start first instance in background
    print("1. Starting first YouTube monitor instance...")
    proc1 = subprocess.Popen([
        sys.executable, "main.py", "--youtube"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Give it time to start and acquire lock
    time.sleep(3)

    # Check if it's still running
    if proc1.poll() is not None:
        stdout, stderr = proc1.communicate()
        print(f"[FAIL] First instance exited early (code: {proc1.returncode})")
        print(f"STDOUT: {stdout.decode()}")
        print(f"STDERR: {stderr.decode()}")
        return False

    print("[OK] First instance is running (PID: {})".format(proc1.pid))

    # Try to start second instance
    print("\n2. Attempting to start second YouTube monitor instance...")
    proc2 = subprocess.Popen([
        sys.executable, "main.py", "--youtube"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Give it time to check for duplicates
    time.sleep(2)

    # Check if second instance exited (should exit due to lock)
    if proc2.poll() is None:
        print("[FAIL] Second instance is still running - lock failed!")
        proc2.terminate()
        proc1.terminate()
        return False
    else:
        stdout, stderr = proc2.communicate()
        output = stdout.decode() + stderr.decode()

        if "Duplicate main.py Instances Detected" in output:
            print("[OK] Second instance correctly detected duplicates and exited")
            print("   Lock prevention working!")
        else:
            print("[FAIL] Second instance exited but didn't show duplicate detection message")
            print(f"Output: {output}")
            proc1.terminate()
            return False

    # Test --no-lock flag
    print("\n3. Testing --no-lock flag (should allow multiple instances)...")
    proc3 = subprocess.Popen([
        sys.executable, "main.py", "--youtube", "--no-lock"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    time.sleep(2)

    if proc3.poll() is None:
        print("[OK] Third instance with --no-lock is running (multiple instances allowed)")
        proc3.terminate()
    else:
        print("[FAIL] Third instance with --no-lock exited unexpectedly")
        proc1.terminate()
        return False

    # Clean up
    print("\n4. Cleaning up...")
    proc1.terminate()

    try:
        proc1.wait(timeout=5)
        print("[OK] First instance terminated cleanly")
    except subprocess.TimeoutExpired:
        proc1.kill()
        print("[U+26A0]️ First instance had to be force-killed")

    print("\n[CELEBRATE] Instance lock test completed successfully!")
    print("   - Lock prevents duplicate instances")
    print("   - --no-lock flag allows multiple instances")
    print("   - Clean shutdown works properly")

    return True

if __name__ == "__main__":
    success = test_instance_lock()
    sys.exit(0 if success else 1)
