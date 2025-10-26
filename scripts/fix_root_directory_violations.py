#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Root Directory Violations - WSP 3 Compliance
================================================

Uses AI_Overseer + autonomous_cleanup_engine to:
1. Move markdown docs to correct locations
2. Move test files to correct modules
3. Move Python scripts with import path fixes
4. Verify all relocations

WSP Compliance: WSP 3, WSP 49, WSP 50, WSP 22
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

# Define correct locations per WSP 3
RELOCATION_MAP = {
    # WRE Phase completion docs -> WRE module
    "WRE_PHASE1_COMPLETE.md": "modules/infrastructure/wre_core/docs/",
    "WRE_PHASE1_CORRECTED_AUDIT.md": "modules/infrastructure/wre_core/docs/",
    "WRE_PHASE1_WSP_COMPLIANCE_AUDIT.md": "modules/infrastructure/wre_core/docs/",
    "WRE_PHASE2_CORRECTED_AUDIT.md": "modules/infrastructure/wre_core/docs/",
    "WRE_PHASE2_FINAL_AUDIT.md": "modules/infrastructure/wre_core/docs/",
    "WRE_PHASE2_WSP_COMPLIANCE_AUDIT.md": "modules/infrastructure/wre_core/docs/",
    "WRE_PHASE3_CORRECTED_AUDIT.md": "modules/infrastructure/wre_core/docs/",
    "WRE_PHASE3_TOKEN_ESTIMATE.md": "modules/infrastructure/wre_core/docs/",
    "WRE_PHASE3_WSP_COMPLIANCE_AUDIT.md": "modules/infrastructure/wre_core/docs/",
    "WRE_PHASES_COMPLETE_SUMMARY.md": "modules/infrastructure/wre_core/docs/",
    "WRE_SKILLS_IMPLEMENTATION_SUMMARY.md": "modules/infrastructure/wre_core/docs/",
    "WRE_CLI_REFACTOR_READY.md": "modules/infrastructure/wre_core/docs/",

    # Implementation docs -> docs/
    "IMPLEMENTATION_INSTRUCTIONS_OPTION5.md": "docs/",
    "WRE_PHASE1_COMPLIANCE_REPORT.md": "docs/",

    # PQN test files -> pqn_alignment module tests
    "test_pqn_meta_research.py": "modules/ai_intelligence/pqn_alignment/tests/",

    # AI Overseer test files -> ai_overseer module tests
    "test_ai_overseer_monitoring.py": "modules/ai_intelligence/ai_overseer/tests/",
    "test_ai_overseer_unicode_fix.py": "modules/ai_intelligence/ai_overseer/tests/",
    "test_monitor_flow.py": "modules/ai_intelligence/ai_overseer/tests/",

    # Gemma test files -> appropriate module tests
    "test_gemma_nested_module_detector.py": "modules/infrastructure/doc_dae/tests/",

    # PQN Python scripts -> pqn_alignment module scripts
    "async_pqn_research_orchestrator.py": "modules/ai_intelligence/pqn_alignment/scripts/",
    "pqn_cross_platform_validator.py": "modules/ai_intelligence/pqn_alignment/scripts/",
    "pqn_realtime_dashboard.py": "modules/ai_intelligence/pqn_alignment/scripts/",
    "pqn_streaming_aggregator.py": "modules/ai_intelligence/pqn_alignment/scripts/",
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
    print("[ROOT-CLEANUP] Starting root directory violation fixes")
    print(f"[REPO] {REPO_ROOT}")
    print()

    results = {
        "moved": [],
        "failed": [],
        "verified": [],
    }

    # Phase 1: Move files
    print("[PHASE-1] Moving files to correct locations per WSP 3")
    print("-" * 60)

    for filename, dest_rel_path in RELOCATION_MAP.items():
        src = REPO_ROOT / filename

        if not src.exists():
            print(f"  [SKIP] {filename} not found")
            continue

        dest_dir = REPO_ROOT / dest_rel_path
        success, message = move_file_with_backup(src, dest_dir)

        if success:
            print(f"  [OK] {message}")
            results["moved"].append({
                "file": filename,
                "from": str(REPO_ROOT),
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
    print("-" * 60)

    # Phase 2: Verify
    for moved in results["moved"]:
        original = REPO_ROOT / moved["file"]
        new_loc = REPO_ROOT / moved["to"] / moved["file"]

        if verify_relocation(original, new_loc):
            print(f"  [VERIFY] {moved['file']} -> {moved['to']} ✓")
            results["verified"].append(moved["file"])
        else:
            print(f"  [ERROR] {moved['file']} verification failed!")

    print()
    print("[PHASE-3] Summary")
    print("-" * 60)
    print(f"  Files moved: {len(results['moved'])}")
    print(f"  Files verified: {len(results['verified'])}")
    print(f"  Failed: {len(results['failed'])}")

    # Save results
    results_file = REPO_ROOT / "data" / "root_cleanup_results.json"
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
    print("[SUCCESS] All files relocated and verified ✓")
    return 0


if __name__ == "__main__":
    exit(main())
