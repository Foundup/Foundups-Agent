#!/usr/bin/env python3
"""
DocDAE Autonomous Cleanup Chain Runner

Wraps the shared AutonomousCleanupEngine so we can exercise the Gemma/Qwen/0102
micro-sprint from the CLI while we bring the FastMCP server online.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Dict

REPO_ROOT = Path(__file__).resolve().parents[4]

import sys  # noqa: E402

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from holo_index.adaptive_learning import breadcrumb_tracer  # noqa: E402
from modules.infrastructure.doc_dae.src.autonomous_cleanup_engine import (  # noqa: E402
    AutonomousCleanupEngine,
)


def _trace(skill_id: str, phase: int, message: str, learned: str) -> None:
    breadcrumb_tracer.trace_action(
        action=f"skill:{skill_id}",
        target=f"autonomous_cleanup_phase_{phase}",
        result=message,
        learned=learned,
    )


async def run_chain(limit: int | None, dry_run: bool) -> Dict[str, object]:
    engine = AutonomousCleanupEngine()

    labels, summary = engine.run_phase_one(limit=limit, persist=not dry_run)
    _trace(
        "gemma_noise_detector_v1_prototype",
        1,
        f"{summary.noise_files} noise / {summary.signal_files} signal (total {summary.total_files})",
        "labels_jsonl_written" if not dry_run else "analysis_only",
    )

    cleanup_plan = engine.run_phase_two(labels, persist=not dry_run)
    _trace(
        "qwen_cleanup_strategist_v1_prototype",
        2,
        f"{len(cleanup_plan['batches'])} autonomous batches / {len(cleanup_plan['flagged_for_review'])} flagged",
        "cleanup_plan_built" if not dry_run else "analysis_only",
    )

    validation = await engine.run_phase_three(
        cleanup_plan,
        persist=not dry_run,
        preview_lines=6,
    )
    summary_dict = validation["summary"]
    previews = []
    for batch in validation["validated_plan"]["batches"][:3]:
        if batch.get("preview"):
            previews.extend(batch["preview"])
    previews = previews[:5]
    _trace(
        "0102_cleanup_validator",
        3,
        f"{summary_dict['approved']} approved / {summary_dict['deferred']} deferred / {summary_dict['manual_review']} review",
        "validation_complete" if not dry_run else "analysis_only",
    )

    return {
        "labels_persisted": not dry_run,
        "plan_persisted": not dry_run,
        "summary": summary_dict,
        "previews": previews,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the DocDAE autonomous cleanup chain.")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of files processed in phase 1.")
    parser.add_argument("--dry-run", action="store_true", help="Skip writing outputs to disk.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = asyncio.run(run_chain(limit=args.limit, dry_run=args.dry_run))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
