#!/usr/bin/env python3
"""
Bulk WSP 90 Fix: Remove UTF-8 enforcement from ALL library modules
Only entry points (main.py, scripts with __main__) should wrap sys.stderr
"""

import os
import re
from pathlib import Path

def is_entry_point(file_path):
    """Check if file is an entry point (has __main__ block)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return 'if __name__ == "__main__"' in content or file_path.name == 'main.py'
    except:
        return False

def remove_utf8_enforcement(file_path):
    """Remove UTF-8 enforcement block from library module"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Find UTF-8 enforcement block
        start_idx = None
        end_idx = None

        for i, line in enumerate(lines):
            if '=== UTF-8 ENFORCEMENT' in line or 'UTF-8 ENFORCEMENT (WSP 90)' in line:
                start_idx = i
            if start_idx is not None and '=== END UTF-8 ENFORCEMENT' in line:
                end_idx = i + 1
                break

        if start_idx is not None and end_idx is not None:
            # Remove the block
            new_lines = lines[:start_idx] + lines[end_idx:]

            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

            removed_lines = end_idx - start_idx
            return True, removed_lines

        return False, 0
    except Exception as e:
        print(f"[ERROR] {file_path}: {e}")
        return False, 0

def main():
    print("[WSP 90 BULK FIX] Removing UTF-8 enforcement from library modules")
    print("=" * 70)

    # Find all Python files with UTF-8 enforcement
    root = Path('O:/Foundups-Agent/modules')
    files_with_enforcement = []

    for py_file in root.rglob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'sys.stderr = io.TextIOWrapper' in content:
                    files_with_enforcement.append(py_file)
        except:
            pass

    print(f"\n[FOUND] {len(files_with_enforcement)} files with UTF-8 enforcement")

    # Separate entry points from library modules
    entry_points = []
    library_modules = []

    for file_path in files_with_enforcement:
        if is_entry_point(file_path):
            entry_points.append(file_path)
        else:
            library_modules.append(file_path)

    print(f"[ENTRY POINTS] {len(entry_points)} files (will keep UTF-8 enforcement)")
    print(f"[LIBRARY MODULES] {len(library_modules)} files (will remove UTF-8 enforcement)")

    # Fix library modules
    print(f"\n[FIXING] Removing UTF-8 enforcement from {len(library_modules)} library modules...")
    print("-" * 70)

    fixed_count = 0
    total_lines_removed = 0

    for file_path in library_modules:
        success, lines_removed = remove_utf8_enforcement(file_path)
        if success:
            fixed_count += 1
            total_lines_removed += lines_removed
            rel_path = file_path.relative_to('O:/Foundups-Agent')
            print(f"  [OK] {rel_path} (-{lines_removed} lines)")

    print("\n" + "=" * 70)
    print(f"[COMPLETE] Fixed {fixed_count}/{len(library_modules)} library modules")
    print(f"[TOTAL] Removed {total_lines_removed} lines of UTF-8 enforcement code")
    print(f"[KEPT] {len(entry_points)} entry points still have UTF-8 enforcement")

    if entry_points:
        print("\n[ENTRY POINTS KEPT]:")
        for ep in entry_points[:10]:
            print(f"  - {ep.relative_to('O:/Foundups-Agent')}")
        if len(entry_points) > 10:
            print(f"  ... and {len(entry_points) - 10} more")

    print("\n[WSP 90] All library modules now comply with WSP 90")
    print("[NEXT] Test main.py to verify sys.stderr error is fixed")

if __name__ == '__main__':
    main()
