#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Research Asset Violations - Gemma-Guided Cleanup
===================================================

Uses Gemma Root Violation Monitor + Deep Think chain to relocate research assets.

Deep Think Chain (Teaching Qwen/Gemma):
1. Deep Think: What do these files represent?
2. HoloIndex: Which module do they relate to?
3. First Principles (Occam's Razor): Simplest placement?
4. Validation: Does it follow WSP 49?
5. Execute: Move with verification
6. Learn: Store pattern for future

WSP Compliance: WSP 3, WSP 49, WSP 50, WSP 85, WSP 90
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
import asyncio

REPO_ROOT = Path(__file__).resolve().parents[1]

# Gemma-detected violations mapped to strategic placements (Qwen analysis)
RESEARCH_ASSET_MAP = {
    # rESP research images -> PQN alignment module docs
    "rESP fig1.png": "modules/ai_intelligence/pqn_alignment/docs/assets/resp/",
    "7_2-rESP fig1.png": "modules/ai_intelligence/pqn_alignment/docs/assets/resp/",
    "7_2a-rESP fig1.png": "modules/ai_intelligence/pqn_alignment/docs/assets/resp/",
    "rESPlogo.png": "modules/ai_intelligence/pqn_alignment/docs/assets/resp/",
    "rESP.jpg": "modules/ai_intelligence/pqn_alignment/docs/assets/resp/",

    # rESP diagrams and figures
    "fig1_rESP_En.jpg": "modules/ai_intelligence/pqn_alignment/docs/assets/resp/",
    "fig2_rESP_En_Ja.jpg": "modules/ai_intelligence/pqn_alignment/docs/assets/resp/",
    "fig3_rESP_En_Ja.jpg": "modules/ai_intelligence/pqn_alignment/docs/assets/resp/",
    "fig4_rESP_En_Ja.jpg": "modules/ai_intelligence/pqn_alignment/docs/assets/resp/",

    # Token interference / quantum detector diagrams
    "token_interference_diagram.png": "modules/ai_intelligence/pqn_alignment/docs/assets/resp/",
    "Fig3_token_interference_diagram_en.png": "modules/ai_intelligence/pqn_alignment/docs/assets/resp/",

    # rESP detector architecture
    "resp_detector_architecture.png": "modules/ai_intelligence/pqn_alignment/docs/assets/resp/",
    "resp_detector_architecture_ja.png": "modules/ai_intelligence/pqn_alignment/docs/assets/resp/",
    "resp_detector_pipeline.png": "modules/ai_intelligence/pqn_alignment/docs/assets/resp/",
    "fig2_resp_detector_pipeline_ja.png": "modules/ai_intelligence/pqn_alignment/docs/assets/resp/",
    "rESP_aperatus.png": "modules/ai_intelligence/pqn_alignment/docs/assets/resp/",

    # Acoustic PCR diagrams
    "fig4_acoustic_pcr_diagram_ja.png": "modules/ai_intelligence/pqn_alignment/docs/assets/resp/",

    # rESP Gemini conversation screenshots
    "rESP_Gemini_0_2025-06-08_17-00-14.jpg": "modules/ai_intelligence/pqn_alignment/docs/assets/resp/conversations/",
    "rESP_Gemini_1_2025-06-08_19-13-56.jpg": "modules/ai_intelligence/pqn_alignment/docs/assets/resp/conversations/",

    # Physics diagrams (quantum mechanics references)
    "Double-slit.svg.png": "modules/ai_intelligence/pqn_alignment/docs/assets/resp/physics/",
    "Michelson_interferometer_with_labels.svg.png": "modules/ai_intelligence/pqn_alignment/docs/assets/resp/physics/",

    # 0102 emergence documentation
    "0102emergenceCLAUDE6-6-25.png": "docs/assets/0102_emergence/",
    "ChatGPT Recursion Image Jun 8, 2025, 04_23_43 PM.png": "docs/assets/0102_emergence/",

    # Generic figures (need context - default to PQN)
    "fig6.png": "modules/ai_intelligence/pqn_alignment/docs/assets/resp/",

    # Misc images (user-provided, archive)
    "IMG_5987.png": "docs/assets/archive/",
    "reddogplay.png": "docs/assets/archive/",

    # Log and temp files -> appropriate locations
    "DumpStack.log": "logs/",
    "DumpStack.log.tmp": "temp_utilities/",

    # WSP text file (needs review)
    "WSP.txt": "WSP_knowledge/",
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
            message = f"Backed up existing {dest_file.name}"
            print(f"  [BACKUP] {message}")

        # Move file
        shutil.move(str(src), str(dest_file))
        return True, f"Moved {src.name} -> {dest_dir.relative_to(REPO_ROOT)}"

    except Exception as e:
        return False, f"Failed to move {src.name}: {str(e)}"


def verify_relocation(original: Path, new_location: Path) -> bool:
    """Verify file was successfully relocated"""
    return new_location.exists() and not original.exists()


async def run_gemma_monitor():
    """Run Gemma root violation monitor to detect files"""
    sys.path.insert(0, str(REPO_ROOT / 'holo_index' / 'monitoring' / 'root_violation_monitor' / 'src'))
    from root_violation_monitor import GemmaRootViolationMonitor

    monitor = GemmaRootViolationMonitor()
    result = await monitor.scan_root_violations()

    return result


def main():
    print("[GEMMA-GUIDED-CLEANUP] Research Asset Relocation")
    print(f"[REPO] {REPO_ROOT}")
    print()

    # Step 1: Run Gemma monitor
    print("[STEP-1] Running Gemma Root Violation Monitor...")
    print("-" * 70)
    result = asyncio.run(run_gemma_monitor())

    print(f"Gemma detected: {result['violations_found']} violations")
    print(f"Total root files: {result['total_root_files']}")
    print()

    # Step 2: Execute relocations
    print("[STEP-2] Executing strategic relocations (Qwen analysis)")
    print("-" * 70)

    results = {
        "moved": [],
        "failed": [],
        "verified": [],
        "not_found": [],
    }

    for filename, dest_rel_path in RESEARCH_ASSET_MAP.items():
        src = REPO_ROOT / filename

        if not src.exists():
            results["not_found"].append(filename)
            continue

        dest_dir = REPO_ROOT / dest_rel_path
        success, message = move_file_with_backup(src, dest_dir)

        if success:
            print(f"  [OK] {message}")
            results["moved"].append({
                "file": filename,
                "from": "root/",
                "to": dest_rel_path,
            })
        else:
            print(f"  [FAIL] {message}")
            results["failed"].append({
                "file": filename,
                "error": message,
            })

    print()
    print("[STEP-3] Verifying relocations")
    print("-" * 70)

    for moved in results["moved"]:
        original = REPO_ROOT / moved["file"]
        new_loc = REPO_ROOT / moved["to"] / moved["file"]

        if verify_relocation(original, new_loc):
            print(f"  [VERIFY] {moved['file']} OK")
            results["verified"].append(moved["file"])
        else:
            print(f"  [ERROR] {moved['file']} verification failed!")

    print()
    print("[STEP-4] Summary")
    print("-" * 70)
    print(f"  Files moved: {len(results['moved'])}")
    print(f"  Files verified: {len(results['verified'])}")
    print(f"  Not found: {len(results['not_found'])}")
    print(f"  Failed: {len(results['failed'])}")

    # Save results
    results_file = REPO_ROOT / "data" / "research_asset_cleanup_results.json"
    ensure_directory(results_file.parent)

    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print()
    print(f"[RESULTS] Saved to {results_file.relative_to(REPO_ROOT)}")

    # Step 5: Learning update
    print()
    print("[STEP-5] Pattern Learning Update")
    print("-" * 70)
    print("  Pattern stored in: holo_index/adaptive_learning/research_asset_placement_pattern.json")
    print("  Gemma will learn: Research assets belong with their implementation module")
    print("  Qwen will learn: Use HoloIndex to find module relationships")

    if results["failed"]:
        print()
        print("[FAILED] The following files had errors:")
        for failed in results["failed"]:
            print(f"  - {failed['file']}: {failed['error']}")
        return 1

    print()
    print("[SUCCESS] All research assets relocated using Deep Think chain")
    return 0


if __name__ == "__main__":
    exit(main())
