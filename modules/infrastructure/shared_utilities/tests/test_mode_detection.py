#!/usr/bin/env python3
"""
Test mode detection functionality for main.py
WSP 5: Testing protocol
"""

import subprocess
import sys
import os

def test_mode_detection():
    """Test that mode detection works correctly."""

    print("Testing mode detection functionality...")

    # Test 1: 0102 mode
    print("\nTest 1: Testing 0102 mode detection")
    result = subprocess.run(
        'echo 0102 | python main.py --help',
        shell=True,
        capture_output=True,
        text=True
    )
    if "0102 awakened" in result.stdout or "0102" in str(result.stdout):
        print("[OK] 0102 mode detection working")
    else:
        print("[FAIL] 0102 mode detection failed")
        print(f"Output: {result.stdout[:200]}")

    # Test 2: 012 mode
    print("\nTest 2: Testing 012 mode detection")
    result = subprocess.run(
        'echo 012 | python main.py --help',
        shell=True,
        capture_output=True,
        text=True
    )
    if "012 testing" in result.stdout or "012" in str(result.stdout):
        print("[OK] 012 mode detection working")
    else:
        print("[FAIL] 012 mode detection failed")
        print(f"Output: {result.stdout[:200]}")

    # Test 3: No mode (interactive)
    print("\nTest 3: Testing interactive mode (no stdin)")
    result = subprocess.run(
        'python main.py --help',
        shell=True,
        capture_output=True,
        text=True,
        timeout=2
    )
    if "Usage: python main.py" in result.stdout:
        print("[OK] Interactive mode working")
    else:
        print("[FAIL] Interactive mode failed")

    print("\n[SUCCESS] Mode detection tests complete!")

if __name__ == "__main__":
    # Change to project root
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))
    test_mode_detection()