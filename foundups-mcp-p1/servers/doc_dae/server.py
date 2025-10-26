from fastmcp import FastMCP
import json
from pathlib import Path
from typing import Dict, List, Tuple

from modules.infrastructure.doc_dae.src.autonomous_cleanup_engine import (
    AutonomousCleanupEngine,
    LABELS_PATH,
    PLAN_PATH,
    VALIDATED_PLAN_PATH,
)

app = FastMCP("DocDAE Autonomous Cleanup MCP Server")


def _load_labels_from_disk() -> List[Dict]:
    if not LABELS_PATH.exists():
        return []
    with open(LABELS_PATH, "r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


def _load_plan_from_disk() -> Dict:
    if not PLAN_PATH.exists():
        raise FileNotFoundError("cleanup_plan.json not found. Run run_qwen_cleanup_strategist first.")
    with open(PLAN_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _engine() -> AutonomousCleanupEngine:
    return AutonomousCleanupEngine()


def _summarise_labels(labels: List[Dict]) -> Dict[str, int]:
    noise = sum(1 for item in labels if item.get("label") == "noise")
    signal = len(labels) - noise
    return {
        "total": len(labels),
        "noise": noise,
        "signal": signal,
    }


@app.tool()
async def run_gemma_noise_detector(limit: int = 200, persist: bool = True) -> Dict:
    """
    Execute Phase 1 (Gemma noise detector) and optionally persist labels.jsonl.
    """
    engine = _engine()
    labels, summary = engine.run_phase_one(limit=limit, persist=persist)

    return {
        "skill_id": "gemma_noise_detector_v1_prototype",
        "persisted": persist,
        "labels_path": str(LABELS_PATH),
        "summary": {
            "total_files": summary.total_files,
            "noise_files": summary.noise_files,
            "signal_files": summary.signal_files,
            "generated_at": summary.generated_at,
        },
        "preview": labels[:5],
    }


@app.tool()
async def run_qwen_cleanup_strategist(
    limit: int = 200,
    persist: bool = True,
    refresh_labels: bool = False,
) -> Dict:
    """
    Execute Phase 2 (Qwen cleanup strategist) producing cleanup_plan.json.

    Args:
        limit: Optional limit for phase 1 if refresh_labels=True or if labels missing.
        persist: When True, writes cleanup_plan.json to disk.
        refresh_labels: Force a fresh phase 1 run before generating the plan.
    """
    engine = _engine()

    labels: List[Dict]
    if refresh_labels or not LABELS_PATH.exists():
        labels, _ = engine.run_phase_one(limit=limit, persist=persist)
    else:
        labels = _load_labels_from_disk()
        if limit and len(labels) > limit:
            labels = labels[:limit]
        if not labels:
            labels, _ = engine.run_phase_one(limit=limit, persist=persist)

    cleanup_plan = engine.run_phase_two(labels, persist=persist)

    return {
        "skill_id": "qwen_cleanup_strategist_v1_prototype",
        "persisted": persist,
        "plan_path": str(PLAN_PATH),
        "metrics": cleanup_plan["metrics"],
        "batches": cleanup_plan["batches"][:3],  # preview first 3 batches
        "flagged_for_review": cleanup_plan["flagged_for_review"][:3],
    }


@app.tool()
async def run_cleanup_validator(
    sample_limit: int = 5,
    persist: bool = True,
) -> Dict:
    """
    Execute Phase 3 (0102 validation) on the current cleanup plan.

    Args:
        sample_limit: Number of files per batch to sample for active reference checks.
        persist: Persist cleanup_plan_validated.json when True.
    """
    engine = _engine()
    cleanup_plan = _load_plan_from_disk()
    validation = await engine.run_phase_three(cleanup_plan, persist=persist, sample_limit=sample_limit)
    summary = validation["summary"]

    return {
        "validator_id": "0102_cleanup_validator",
        "persisted": persist,
        "validated_plan_path": str(VALIDATED_PLAN_PATH),
        "summary": summary,
        "approved_batches_preview": [
            batch for batch in validation["validated_plan"]["batches"] if batch["0102_decision"] == "APPROVED"
        ][:3],
    }


if __name__ == "__main__":
    app.run()
