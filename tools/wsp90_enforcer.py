#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WSP 90 UTF-8 Enforcement Checker
=================================

Scans Python files and reports missing WSP 90 compliance.
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

import os
from pathlib import Path

WSP90_HEADER = "# === UTF-8 ENFORCEMENT (WSP 90) ==="

def check_file(file_path: Path) -> bool:
    """Check if file has WSP 90 compliance"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return WSP90_HEADER in content
    except Exception as e:
        print(f"[ERROR] Could not read {file_path}: {e}")
        return False

def scan_directory(directory: Path):
    """Scan directory for WSP 90 compliance"""
    if not directory.exists():
        print(f"[SKIP] Directory not found: {directory}")
        return True

    python_files = list(directory.rglob("*.py"))
    if not python_files:
        print(f"[SKIP] No Python files in {directory}")
        return True

    non_compliant = []

    for py_file in python_files:
        if not check_file(py_file):
            non_compliant.append(py_file)

    if non_compliant:
        print(f"[WARNING] {len(non_compliant)}/{len(python_files)} files missing WSP 90 compliance in {directory}:")
        for file in non_compliant[:10]:  # Show first 10
            print(f"  - {file}")
        if len(non_compliant) > 10:
            print(f"  ... and {len(non_compliant) - 10} more")
        return False
    else:
        print(f"[PASS] All {len(python_files)} Python files are WSP 90 compliant in {directory}")
        return True

if __name__ == "__main__":
    repo_root = Path(__file__).parent.parent

    print("WSP 90 UTF-8 Enforcement Compliance Check")
    print("=" * 50)

    # Check key directories
    directories = [
        repo_root / "modules",
        repo_root / "holo_index",
        repo_root / "WSP_agentic",
        repo_root / "tools",
        repo_root / "foundups-mcp-p1",
    ]

    total_passed = 0
    total_checked = len(directories)

    for directory in directories:
        if scan_directory(directory):
            total_passed += 1
        print()

    print("=" * 50)
    if total_passed == total_checked:
        print(f"[SUCCESS] All {total_checked} directories are WSP 90 compliant!")
        exit(0)
    else:
        print(f"[FAILURE] {total_checked - total_passed}/{total_checked} directories have WSP 90 violations")
        exit(1)
