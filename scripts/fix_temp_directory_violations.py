#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Temp Directory Violations - WSP 49 Module Structure Compliance
===================================================================

Relocates temp/ directory files to proper module temp/ directories.

Per WSP 49: Each module can have a temp/ subdirectory for debug/utility scripts
specific to that module. Root-level temp/ should not contain module-specific files.

WSP Compliance: WSP 49 (Module Structure), WSP 3 (Module Organization)
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        pass
# === END UTF-8 ENFORCEMENT ===

import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]

# Map temp files to their proper module temp/ directories
TEMP_FILE_MODULE_MAP = {
    # HoloIndex CLI utilities
    "cli_top.py": "holo_index/temp/",
    "show_cli_head.py": "holo_index/temp/",
    "show_cli_search.py": "holo_index/temp/",
    "show_cli_segment.py": "holo_index/temp/",
    "show_holo_readme_head.py": "holo_index/temp/",

    # HoloIndex output throttler debug
    "dump_throttler.py": "holo_index/temp/",
    "dump_throttler_ascii.py": "holo_index/temp/",
    "find_throttler.py": "holo_index/temp/",

    # HoloIndex pattern coach utilities
    "find_pattern_coach.py": "holo_index/temp/",

    # HoloIndex advisor debug
    "show_advisor.py": "holo_index/temp/",

    # HoloIndex history debug
    "show_history.py": "holo_index/temp/",

    # HoloIndex output debug (generic)
    "show_args.py": "holo_index/temp/",
    "show_debug.py": "holo_index/temp/",
    "show_debug_lines.py": "holo_index/temp/",
    "show_line.py": "holo_index/temp/",
    "show_lines.py": "holo_index/temp/",
    "show_mid.py": "holo_index/temp/",
    "show_tail.py": "holo_index/temp/",
    "show_search.py": "holo_index/temp/",
    "show_search2.py": "holo_index/temp/",
    "show_section.py": "holo_index/temp/",
    "show_section_ascii.py": "holo_index/temp/",
    "show_segment.py": "holo_index/temp/",
    "show_segment2.py": "holo_index/temp/",
    "show_segment3.py": "holo_index/temp/",
    "show_segment4.py": "holo_index/temp/",
    "find_lines.py": "holo_index/temp/",

    # Unicode/emoji debug (cross-module - keep in holo_index as primary)
    "find_unicode.py": "holo_index/temp/",
    "list_unicode.py": "holo_index/temp/",
    "list_unicode_again.py": "holo_index/temp/",
    "replace_unicode.py": "holo_index/temp/",
    "replace_unicode2.py": "holo_index/temp/",
    "fix_dash.py": "holo_index/temp/",
    "fix_dash2.py": "holo_index/temp/",

    # Doc DAE debug utilities
    "show_docdae.py": "modules/infrastructure/doc_dae/temp/",
    "fix_doc.py": "modules/infrastructure/doc_dae/temp/",
    "fix_doc2.py": "modules/infrastructure/doc_dae/temp/",

    # Auto moderator debug (livechat)
    "show_auto.py": "modules/communication/livechat/temp/",

    # ModLog utilities (system-wide - keep in root temp_utilities/)
    "show_modlog_top.ps1": "temp_utilities/",
    "update_modlog.py": "temp_utilities/",
    "update_modlog_ascii.py": "temp_utilities/",
    "update_modlog_problem.py": "temp_utilities/",

    # Temp test files (WRE/skills)
    "temp_check_db.py": "modules/infrastructure/wre_core/temp/",
    "temp_skills_test.py": "modules/infrastructure/wre_core/temp/",
    "temp_test_audit.py": "modules/infrastructure/wre_core/temp/",

    # HoloIndex analysis docs
    "HoloIndex_Document_Classification_MCP_Analysis.md": "holo_index/temp/",

    # Temp data files
    "temp_012_first2k.txt": "temp_utilities/",
}


def ensure_directory(path: Path) -> None:
    """Create directory if it doesn't exist"""
    path.mkdir(parents=True, exist_ok=True)


def move_file_with_backup(src: Path, dest_dir: Path) -> Tuple[bool, str]:
    """
    Move file to destination with backup if exists

    Returns: (success, message)
    """
    try:
        ensure_directory(dest_dir)
        dest_file = dest_dir / src.name

        # If destination exists, create backup
        if dest_file.exists():
            backup = dest_file.with_suffix(dest_file.suffix + ".backup")
            shutil.copy2(dest_file, backup)
            message = f"Backed up existing {dest_file.name} to {backup.name}"
            print(f"  [BACKUP] {message}")

        # Move file
        shutil.move(str(src), str(dest_file))
        return True, f"Moved {src.name} -> {dest_dir.relative_to(REPO_ROOT)}"

    except Exception as e:
        return False, f"Failed to move {src.name}: {str(e)}"


def verify_relocation(original: Path, new_location: Path) -> bool:
    """Verify file was successfully relocated"""
    return new_location.exists() and not original.exists()


def main():
    print("[TEMP-CLEANUP] Starting temp/ directory module organization")
    print(f"[REPO] {REPO_ROOT}")
    print()

    results = {
        "moved": [],
        "failed": [],
        "verified": [],
    }

    # Phase 1: Move files to module-specific temp/ directories
    print("[PHASE-1] Moving temp files to module temp/ directories per WSP 49")
    print("-" * 70)

    for filename, dest_rel_path in TEMP_FILE_MODULE_MAP.items():
        src = REPO_ROOT / "temp" / filename

        if not src.exists():
            print(f"  [SKIP] {filename} not found")
            continue

        dest_dir = REPO_ROOT / dest_rel_path
        success, message = move_file_with_backup(src, dest_dir)

        if success:
            print(f"  [OK] {message}")
            results["moved"].append({
                "file": filename,
                "from": "temp/",
                "to": dest_rel_path,
            })
        else:
            print(f"  [FAIL] {message}")
            results["failed"].append({
                "file": filename,
                "error": message,
            })

    print()
    print("[PHASE-2] Verifying relocations")
    print("-" * 70)

    # Phase 2: Verify
    for moved in results["moved"]:
        original = REPO_ROOT / "temp" / moved["file"]
        new_loc = REPO_ROOT / moved["to"] / moved["file"]

        if verify_relocation(original, new_loc):
            print(f"  [VERIFY] {moved['file']} -> {moved['to']} OK")
            results["verified"].append(moved["file"])
        else:
            print(f"  [ERROR] {moved['file']} verification failed!")

    print()
    print("[PHASE-3] Summary")
    print("-" * 70)
    print(f"  Files moved: {len(results['moved'])}")
    print(f"  Files verified: {len(results['verified'])}")
    print(f"  Failed: {len(results['failed'])}")

    # Save results
    results_file = REPO_ROOT / "data" / "temp_cleanup_results.json"
    ensure_directory(results_file.parent)

    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print()
    print(f"[RESULTS] Saved to {results_file.relative_to(REPO_ROOT)}")

    if results["failed"]:
        print()
        print("[FAILED] The following files had errors:")
        for failed in results["failed"]:
            print(f"  - {failed['file']}: {failed['error']}")
        return 1

    print()
    print("[SUCCESS] All temp files relocated to module directories")
    return 0


if __name__ == "__main__":
    exit(main())
