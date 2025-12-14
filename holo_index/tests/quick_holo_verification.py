#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick HoloIndex Verification Script

No dependencies required (no pytest) - just runs basic verification tests.
Use this for quick smoke testing of HoloIndex operational status.

Run with:
    python holo_index/tests/quick_holo_verification.py
"""

import subprocess
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_EXE = "python"


def run_holo(args):
    """Run HoloIndex and measure time."""
    cmd = [PYTHON_EXE, "holo_index.py"] + args
    start = time.time()
    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60
    )
    elapsed = time.time() - start
    return result.stdout, result.stderr, elapsed, result.returncode


def test_semantic_search():
    """Test 1: Semantic search finds results."""
    print("\n[TEST 1] Semantic Search")
    print("-" * 60)

    stdout, stderr, elapsed, code = run_holo(["--search", "module health checking", "--limit", "3"])

    passed = "[SOLUTION FOUND]" in stdout or "[RESULTS]" in stdout
    print(f"  Query: 'module health checking'")
    print(f"  Time: {elapsed:.2f}s")
    print(f"  Result: {'[PASS]' if passed else '[FAIL]'}")

    if not passed:
        print(f"  Output: {stdout[:200]}")

    return passed


def test_module_checking():
    """Test 2: Module checking detects existing modules."""
    print("\n[TEST 2] Module Checking")
    print("-" * 60)

    stdout, stderr, elapsed, code = run_holo(["--check-module", "youtube_dae"])

    passed = "[SUCCESS] MODULE EXISTS" in stdout
    print(f"  Module: youtube_dae")
    print(f"  Time: {elapsed:.2f}s")
    print(f"  Result: {'[PASS]' if passed else '[FAIL]'}")

    if not passed:
        print(f"  Output: {stdout[:200]}")

    return passed


def test_health_check():
    """Test 3: Health check completes successfully."""
    print("\n[TEST 3] Health Check")
    print("-" * 60)

    stdout, stderr, elapsed, code = run_holo(["--health"])

    passed = "[HEALTH-CHECK] Complete" in stdout
    print(f"  Time: {elapsed:.2f}s")
    print(f"  Result: {'[PASS]' if passed else '[FAIL]'}")

    if not passed:
        print(f"  Output: {stdout[:200]}")

    return passed


def test_pattern_coach():
    """Test 4: Pattern Coach runs without errors."""
    print("\n[TEST 4] Pattern Coach")
    print("-" * 60)

    stdout, stderr, elapsed, code = run_holo(["--pattern-coach"])

    passed = code == 0 and ("PATTERN-COACH" in stdout or "analysis" in stdout.lower())
    print(f"  Time: {elapsed:.2f}s")
    print(f"  Result: {'[PASS]' if passed else '[FAIL]'}")

    if not passed:
        print(f"  Stderr: {stderr[:200]}")

    return passed


def test_function_indexing():
    """Test 5: Function-level indexing works."""
    print("\n[TEST 5] Function-Level Indexing")
    print("-" * 60)

    stdout, stderr, elapsed, code = run_holo(["--search", "coordinator", "--function-index", "--limit", "2"])

    passed = code == 0
    print(f"  Query: 'coordinator' with --function-index")
    print(f"  Time: {elapsed:.2f}s")
    print(f"  Result: {'[PASS]' if passed else '[FAIL]'}")

    return passed


def test_cli_flags():
    """Test 6: CLI has comprehensive flags."""
    print("\n[TEST 6] CLI Flags (40+ expected)")
    print("-" * 60)

    stdout, stderr, elapsed, code = run_holo(["--help"])

    # Count flags
    import re
    flag_count = len(re.findall(r'^\s*--\w+', stdout, re.MULTILINE))

    passed = flag_count >= 35
    print(f"  Flags found: {flag_count}")
    print(f"  Target: >=35")
    print(f"  Result: {'[PASS]' if passed else '[FAIL]'}")

    return passed


def main():
    """Run all verification tests."""
    print("="*60)
    print("HOLOINDEX QUICK VERIFICATION")
    print("="*60)
    print(f"Repository: {REPO_ROOT}")

    tests = [
        ("Semantic Search", test_semantic_search),
        ("Module Checking", test_module_checking),
        ("Health Check", test_health_check),
        ("Pattern Coach", test_pattern_coach),
        ("Function Indexing", test_function_indexing),
        ("CLI Flags", test_cli_flags),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n  [EXCEPTION]: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} - {name}")

    print(f"\n  Total: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n  [SUCCESS] ALL TESTS PASSED - HoloIndex is fully operational")
        return 0
    else:
        print(f"\n  [WARNING] {total_count - passed_count} test(s) failed")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
