#!/usr/bin/env python3
"""
Quick test to verify instance lock prevents duplicate YouTube monitors.
"""

import sys
import os
import subprocess
import time

def test_instance_lock():
    """Test that instance lock prevents multiple instances."""
    print("🔒 Testing Instance Lock Prevention")
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
        print(f"❌ First instance exited early (code: {proc1.returncode})")
        print(f"STDOUT: {stdout.decode()}")
        print(f"STDERR: {stderr.decode()}")
        return False

    print("✅ First instance is running (PID: {})".format(proc1.pid))

    # Try to start second instance
    print("\n2. Attempting to start second YouTube monitor instance...")
    proc2 = subprocess.Popen([
        sys.executable, "main.py", "--youtube"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Give it time to check for duplicates
    time.sleep(2)

    # Check if second instance exited (should exit due to lock)
    if proc2.poll() is None:
        print("❌ Second instance is still running - lock failed!")
        proc2.terminate()
        proc1.terminate()
        return False
    else:
        stdout, stderr = proc2.communicate()
        output = stdout.decode() + stderr.decode()

        if "Duplicate main.py Instances Detected" in output:
            print("✅ Second instance correctly detected duplicates and exited")
            print("   Lock prevention working!")
        else:
            print("❌ Second instance exited but didn't show duplicate detection message")
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
        print("✅ Third instance with --no-lock is running (multiple instances allowed)")
        proc3.terminate()
    else:
        print("❌ Third instance with --no-lock exited unexpectedly")
        proc1.terminate()
        return False

    # Clean up
    print("\n4. Cleaning up...")
    proc1.terminate()

    try:
        proc1.wait(timeout=5)
        print("✅ First instance terminated cleanly")
    except subprocess.TimeoutExpired:
        proc1.kill()
        print("⚠️ First instance had to be force-killed")

    print("\n🎉 Instance lock test completed successfully!")
    print("   - Lock prevents duplicate instances")
    print("   - --no-lock flag allows multiple instances")
    print("   - Clean shutdown works properly")

    return True

if __name__ == "__main__":
    success = test_instance_lock()
    sys.exit(0 if success else 1)
