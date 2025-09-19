#!/usr/bin/env python3
"""
Quick SSD speed test for E: drive
No dependencies required!
"""

import time
import os
from pathlib import Path

def test_ssd_speed():
    """Test E: drive SSD performance"""
    print("[SSD TEST] Testing E: Drive SSD Performance\n")

    # Test path on E: drive
    test_dir = Path("E:/HoloIndex/cache")
    test_file = test_dir / "speed_test.tmp"

    # Create test data (10MB)
    test_size_mb = 10
    test_data = b"x" * (test_size_mb * 1024 * 1024)

    print(f"[INFO] Test Size: {test_size_mb}MB")
    print("-" * 40)

    # Test 1: Write Speed
    print("\n[WRITE] Write Speed Test:")
    start = time.time()
    with open(test_file, 'wb') as f:
        f.write(test_data)
    write_time = time.time() - start
    write_speed = test_size_mb / write_time
    print(f"  Time: {write_time:.3f} seconds")
    print(f"  Speed: {write_speed:.1f} MB/s")

    # Test 2: Read Speed
    print("\n[READ] Read Speed Test:")
    start = time.time()
    with open(test_file, 'rb') as f:
        _ = f.read()
    read_time = time.time() - start
    read_speed = test_size_mb / read_time
    print(f"  Time: {read_time:.3f} seconds")
    print(f"  Speed: {read_speed:.1f} MB/s")

    # Test 3: Small File Operations (simulating index operations)
    print("\n[OPS] Small File Operations Test:")
    num_files = 100
    start = time.time()

    # Write 100 small files
    for i in range(num_files):
        small_file = test_dir / f"small_{i}.tmp"
        with open(small_file, 'w') as f:
            f.write(f"Test data {i}")

    # Read them back
    for i in range(num_files):
        small_file = test_dir / f"small_{i}.tmp"
        with open(small_file, 'r') as f:
            _ = f.read()

    # Clean up small files
    for i in range(num_files):
        small_file = test_dir / f"small_{i}.tmp"
        small_file.unlink()

    ops_time = time.time() - start
    ops_per_second = (num_files * 2) / ops_time  # 2 ops per file (write + read)
    print(f"  {num_files} files written and read")
    print(f"  Time: {ops_time:.3f} seconds")
    print(f"  Speed: {ops_per_second:.1f} operations/second")

    # Clean up test file
    test_file.unlink()

    print("\n" + "=" * 40)
    print("[COMPLETE] SSD Performance Test Complete!")
    print("=" * 40)

    # Summary
    print("\n[SUMMARY] Performance Summary:")
    print(f"  Write Speed: {write_speed:.1f} MB/s")
    print(f"  Read Speed: {read_speed:.1f} MB/s")
    print(f"  File Ops: {ops_per_second:.1f} ops/sec")

    # Compare to typical speeds
    print("\n[COMPARE] Comparison:")
    print("  HDD: ~100-150 MB/s")
    print("  SATA SSD: ~500-550 MB/s")
    print("  USB 3.0 SSD: ~400-600 MB/s ← Your Drive")
    print("  NVMe SSD: ~2000-7000 MB/s")

    if write_speed > 400 and read_speed > 400:
        print("\n[EXCELLENT] Your SSD is performing at USB 3.0+ speeds!")
    elif write_speed > 200 and read_speed > 200:
        print("\n[GOOD] Your SSD is fast enough for HoloIndex!")
    else:
        print("\n[WARNING] Check USB port - might be USB 2.0 (limited to ~40MB/s)")

if __name__ == "__main__":
    test_ssd_speed()