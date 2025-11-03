#!/usr/bin/env python3
"""
Autonomous Cleanup Engine
=========================

Shared runtime for DocDAE wardrobe skills:
    - Phase 1: Gemma noise detector
    - Phase 2: Qwen cleanup strategist (with WSP 15 MPS scoring)
    - Phase 3: 0102 validator (HoloIndex research + overrides)

The engine exposes helpers so both the CLI runner and the upcoming FastMCP
server can drive the same logic without duplicating heuristics.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional, Tuple

from holo_index.mcp_client.holo_mcp_client import HoloIndexMCPClient
from modules.infrastructure.doc_dae.src.doc_dae import DocDAE

REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = REPO_ROOT / "data"
LABELS_PATH = DATA_DIR / "gemma_noise_labels.jsonl"
PLAN_PATH = DATA_DIR / "cleanup_plan.json"
VALIDATED_PLAN_PATH = DATA_DIR / "cleanup_plan_validated.json"
METRICS_PATH = (
    REPO_ROOT
    / "modules"
    / "infrastructure"
    / "wre_core"
    / "recursive_improvement"
    / "metrics"
    / "doc_dae_cleanup_skill_metrics.jsonl"
)

NOISE_EXTENSIONS = {
    ".jsonl",
    ".tmp",
    ".temp",
    ".bak",
    ".backup",
    ".log",
    ".cache",
    ".pyc",
    ".swp",
    ".swo",
    ".ds_store",
}

NOISE_DIR_TOKENS = {
    "__pycache__",
    "temp",
    "tmp",
    "backup",
    "backups",
    ".pytest_cache",
    ".mypy_cache",
}

CRITICAL_PATH_TOKENS = {
    "modules",
    "WSP_framework/src",
    "data",
    "holo_index",
    "scripts",
}

BACKUP_NAME_TOKENS = ("backup", "bak", "temp", "tmp", "copy", "old")


def _posix(path: Path) -> str:
    return path.as_posix()


def _relative(path: Path) -> Path:
    return path.relative_to(REPO_ROOT)


@dataclass
class PhaseSummary:
    total_files: int
    noise_files: int
    signal_files: int
    generated_at: str


class GemmaClassifier:
    """Implements the rule-based logic from gemma_noise_detector SKILL.md."""

    def classify(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        rel_path = _posix(_relative(Path(file_info["full_path"])))
        path_obj = Path(rel_path)
        file_name = path_obj.name
        extension = path_obj.suffix.lower()
        parent_parts = {part.lower() for part in path_obj.parts[:-1]}
        last_modified_days = file_info.get("last_modified_days") or math.inf
        size_bytes = file_info.get("size_bytes", 0)

        rules_triggered: List[str] = []
        label = "signal"
        category = "critical_file"
        confidence = 0.50

        if self._is_critical_path(rel_path, file_name):
            rules_triggered.append("critical_path_override")
            return self._build_result(rel_path, "signal", "critical_file", 1.0, rules_triggered, size_bytes)

        if parent_parts & NOISE_DIR_TOKENS:
            rules_triggered.append("noise_directory")
            return self._build_result(rel_path, "noise", "noise_directory", 0.95, rules_triggered, size_bytes)

        if extension in NOISE_EXTENSIONS and not self._extension_is_exempt(rel_path, extension):
            rules_triggered.append("extension_noise")
            return self._build_result(rel_path, "noise", "file_type_noise", 0.95, rules_triggered, size_bytes)

        lowered = file_name.lower()
        if any(token in lowered for token in BACKUP_NAME_TOKENS):
            rules_triggered.append("backup_pattern")
            return self._build_result(rel_path, "noise", "backup_file", 0.90, rules_triggered, size_bytes)

        if (
            extension in {".jsonl", ".log", ".json"}
            and last_modified_days != math.inf
            and last_modified_days > 30
            and size_bytes > 1_000_000
        ):
            rules_triggered.append("rotting_data")
            return self._build_result(rel_path, "noise", "rotting_data", 0.85, rules_triggered, size_bytes)

        return self._build_result(rel_path, label, category, confidence, rules_triggered, size_bytes)

    @staticmethod
    def _build_result(
        rel_path: str,
        label: str,
        category: str,
        confidence: float,
        rules: Iterable[str],
        size_bytes: int,
    ) -> Dict[str, Any]:
        return {
            "file_path": rel_path,
            "label": label,
            "category": category,
            "confidence": round(confidence, 3),
            "rules_triggered": list(rules),
            "size_bytes": size_bytes,
        }

    @staticmethod
    def _extension_is_exempt(rel_path: str, extension: str) -> bool:
        if extension == ".jsonl":
            return any(
                rel_path.startswith(prefix)
                for prefix in (
                    "data/",
                    "modules/",
                    "memory/",
                    "logs/",
                    "tests/",
                )
            )
        if extension == ".log":
            return "/logs/" in rel_path or rel_path.startswith("logs/")
        return False

    @staticmethod
    def _is_critical_path(rel_path: str, file_name: str) -> bool:
        if file_name in {".env", "requirements.txt", "pyproject.toml"}:
            return True
        if rel_path == "data/foundup.db":
            return True
        return any(rel_path.startswith(token) for token in CRITICAL_PATH_TOKENS)


class AutonomousCleanupEngine:
    """Co-ordinates the three-phase autonomous cleanup pipeline."""

    def __init__(self, doc_root: Optional[Path] = None) -> None:
        self.repo_root = REPO_ROOT
        self.doc_dae = DocDAE(root_docs_path=doc_root or (self.repo_root / "docs"))
        self.classifier = GemmaClassifier()
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ Phase 1
    def run_phase_one(self, limit: Optional[int] = None, persist: bool = True) -> Tuple[List[Dict[str, Any]], PhaseSummary]:
        analysis = self.doc_dae.analyze_docs_folder()
        files = analysis.get("files", [])
        if limit:
            files = files[:limit]

        labels: List[Dict[str, Any]] = []
        if persist:
            LABELS_PATH.parent.mkdir(parents=True, exist_ok=True)
            handle = open(LABELS_PATH, "w", encoding="utf-8")
        else:
            handle = None

        try:
            for file_info in files:
                result = self.classifier.classify(file_info)
                labels.append(result)
                if handle:
                    handle.write(json.dumps(result) + "\n")
        finally:
            if handle:
                handle.close()

        noise = sum(1 for item in labels if item["label"] == "noise")
        signal = len(labels) - noise
        summary = PhaseSummary(
            total_files=len(labels),
            noise_files=noise,
            signal_files=signal,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )
        self._record_metric(
            skill_id="gemma_noise_detector_v1_prototype",
            phase=1,
            payload={
                "total_files": summary.total_files,
                "noise_files": summary.noise_files,
                "signal_files": summary.signal_files,
                "persisted": persist,
                "labels_path": str(LABELS_PATH),
            },
        )
        return labels, summary

    # ------------------------------------------------------------------ Phase 2
    def run_phase_two(
        self,
        labels: List[Dict[str, Any]],
        persist: bool = True,
    ) -> Dict[str, Any]:
        grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for entry in labels:
            if entry["label"] == "noise":
                grouped[entry["category"]].append(entry)

        batches = []
        flagged_for_review: List[Dict[str, Any]] = []

        for category, items in grouped.items():
            batch = self._build_batch(category, items)
            if batch["mps_scoring"]["priority"] in {"P0", "P1"}:
                batches.append(batch)
            else:
                flagged_for_review.append(batch)

        now = datetime.now(timezone.utc)
        cleanup_plan = {
            "plan_id": f"cleanup_plan_{now.strftime('%Y%m%d_%H%M%S')}",
            "generated_at": now.isoformat(),
            "batches": batches,
            "flagged_for_review": flagged_for_review,
            "skill_id": "qwen_cleanup_strategist_v1_prototype",
            "metrics": {
                "total_noise_candidates": sum(len(v) for v in grouped.values()),
                "autonomous_batches": len(batches),
                "manual_review": len(flagged_for_review),
            },
        }

        if persist:
            PLAN_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(PLAN_PATH, "w", encoding="utf-8") as handle:
                json.dump(cleanup_plan, handle, indent=2)

        self._record_metric(
            skill_id="qwen_cleanup_strategist_v1_prototype",
            phase=2,
            payload={
                "plan_id": cleanup_plan["plan_id"],
                "autonomous_batches": len(batches),
                "manual_review": len(flagged_for_review),
                "total_noise_candidates": cleanup_plan["metrics"]["total_noise_candidates"],
                "persisted": persist,
                "plan_path": str(PLAN_PATH),
            },
        )

        return cleanup_plan

    # ------------------------------------------------------------------ Phase 3
    async def run_phase_three(
        self,
        cleanup_plan: Dict[str, Any],
        persist: bool = True,
        sample_limit: int = 5,
        preview_lines: int = 6,
    ) -> Dict[str, Any]:
        batches = cleanup_plan.get("batches", [])
        flagged = cleanup_plan.get("flagged_for_review", [])
        summary = {"approved": 0, "deferred": 0, "manual_review": len(flagged)}
        validated_batches: List[Dict[str, Any]] = []

        validated_plan = {
            "plan_id": cleanup_plan["plan_id"],
            "validated_at": datetime.now(timezone.utc).isoformat(),
            "batches": [],
            "flagged_for_review": flagged,
        }

        if not batches:
            if persist:
                VALIDATED_PLAN_PATH.parent.mkdir(parents=True, exist_ok=True)
                with open(VALIDATED_PLAN_PATH, "w", encoding="utf-8") as handle:
                    json.dump(validated_plan, handle, indent=2)
            self._record_metric(
                skill_id="0102_cleanup_validator",
                phase=3,
                payload={
                    "plan_id": cleanup_plan["plan_id"],
                    "approved": 0,
                    "deferred": 0,
                    "manual_review": len(flagged),
                    "persisted": persist,
                    "validated_plan_path": str(VALIDATED_PLAN_PATH),
                    "notes": "no_batches_available",
                },
            )
            return {"validated_plan": validated_plan, "summary": summary}

        async with HoloIndexMCPClient() as client:
            for batch in batches:
                validation = await self._validate_batch(
                    client,
                    batch,
                    sample_limit=sample_limit,
                    preview_lines=preview_lines,
                )
                validated_batches.append(validation)
                decision = validation["0102_decision"]
                if decision == "APPROVED":
                    summary["approved"] += 1
                elif decision == "DEFER":
                    summary["deferred"] += 1
                else:
                    summary["manual_review"] += 1

        validated_plan["batches"] = validated_batches

        if persist:
            VALIDATED_PLAN_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(VALIDATED_PLAN_PATH, "w", encoding="utf-8") as handle:
                json.dump(validated_plan, handle, indent=2)

        self._record_metric(
            skill_id="0102_cleanup_validator",
            phase=3,
            payload={
                "plan_id": cleanup_plan["plan_id"],
                "approved": summary["approved"],
                "deferred": summary["deferred"],
                "manual_review": summary["manual_review"],
                "persisted": persist,
                "validated_plan_path": str(VALIDATED_PLAN_PATH),
            },
        )

        return {"validated_plan": validated_plan, "summary": summary}

    # ------------------------------------------------------------------ Helpers
    def _build_batch(self, category: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        file_paths = [item["file_path"] for item in items]
        total_size_mb = sum(item.get("size_bytes", 0) for item in items) / 1_048_576
        avg_confidence = mean(item["confidence"] for item in items) if items else 0.5

        risk_level = self._determine_risk(category, total_size_mb, len(items))
        mps = self._calculate_mps(category, len(items), total_size_mb, risk_level)

        return {
            "batch_id": f"{category}_{len(items)}_{int(total_size_mb)}",
            "category": category,
            "file_count": len(items),
            "files": file_paths,
            "total_size_mb": round(total_size_mb, 3),
            "avg_confidence": round(avg_confidence, 3),
            "rationale": self._build_rationale(category, len(items), total_size_mb),
            "risk_level": risk_level,
            "mps_scoring": mps,
        }

    @staticmethod
    def _determine_risk(category: str, total_size_mb: float, file_count: int) -> str:
        if category in {"critical_file", "unknown_keep_safe"}:
            return "HIGH"
        if file_count > 300 or total_size_mb > 200:
            return "HIGH"
        if file_count > 150 or total_size_mb > 100:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _build_rationale(category: str, file_count: int, total_size_mb: float) -> str:
        return (
            f"{file_count} files in category '{category}' totalling "
            f"{round(total_size_mb, 2)} MB. Generated by Qwen strategic scoring."
        )

    @staticmethod
    def _calculate_mps(category: str, file_count: int, total_size_mb: float, risk_level: str) -> Dict[str, Any]:
        def clamp(value: int) -> int:
            return max(1, min(value, 5))

        complexity = clamp(1 if file_count < 50 else 2 if file_count < 100 else 3 if file_count < 250 else 4)
        importance = clamp(5 if category in {"rotting_data", "file_type_noise"} else 3)
        deferability = clamp(2 if risk_level == "LOW" else 3 if risk_level == "MEDIUM" else 5)
        impact = clamp(2 if total_size_mb < 10 else 3 if total_size_mb < 50 else 4 if total_size_mb < 200 else 5)

        total = complexity + importance + deferability + impact
        if total >= 16:
            priority = "P0"
        elif total >= 13:
            priority = "P1"
        elif total >= 10:
            priority = "P2"
        elif total >= 7:
            priority = "P3"
        else:
            priority = "P4"

        if priority in {"P0", "P1"} and risk_level != "HIGH":
            decision = "AUTONOMOUS_EXECUTE"
        elif priority in {"P0", "P1"} and risk_level == "HIGH":
            decision = "REVIEW_REQUIRED"
        elif priority == "P2":
            decision = "REQUIRES_VALIDATION"
        else:
            decision = "DEFER"

        confidence = 0.9 if priority in {"P0", "P1"} else 0.75

        return {
            "complexity": complexity,
            "importance": importance,
            "deferability": deferability,
            "impact": impact,
            "mps_total": total,
            "priority": priority,
            "qwen_decision": decision,
            "qwen_confidence": round(confidence, 2),
        }

    async def _validate_batch(
        self,
        client: HoloIndexMCPClient,
        batch: Dict[str, Any],
        sample_limit: int,
        preview_lines: int,
    ) -> Dict[str, Any]:
        files = batch.get("files", [])[:sample_limit]
        active_references: Dict[str, List[str]] = {}

        previews: List[Dict[str, Any]] = []

        for file_path in files:
            references = await self._search_references(client, file_path)
            if references:
                active_references[file_path] = references
            preview = self._generate_preview(file_path, preview_lines)
            if preview:
                previews.append(preview)

        qwen_decision = batch["mps_scoring"]["qwen_decision"]
        if active_references:
            decision = "DEFER"
            notes = "Active references discovered via HoloIndex"
        elif batch["mps_scoring"]["priority"] in {"P0", "P1"}:
            decision = "APPROVED" if qwen_decision == "AUTONOMOUS_EXECUTE" else "REVIEW"
            notes = "No references detected; safe to proceed" if decision == "APPROVED" else "Manual review requested"
        else:
            decision = "REVIEW"
            notes = "Priority below autonomous threshold"

        return {
            **batch,
            "0102_decision": decision,
            "validation": {
                "active_references": active_references,
                "notes": notes,
            },
            "preview": previews[:3],
        }

    @staticmethod
    async def _search_references(client: HoloIndexMCPClient, file_path: str) -> List[str]:
        file_name = Path(file_path).name
        query = f"\"{file_name}\""
        try:
            search_result = await client.semantic_code_search(query=query, limit=5)
        except Exception as exc:
            return [f"[search_error] {exc}"]

        references: List[str] = []
        for bucket in ("code_results", "wsp_results"):
            for hit in search_result.get(bucket, []):
                snippet = hit.get("snippet") or hit.get("content", "")
                path = hit.get("path", "")
                if file_name in snippet or file_path in snippet:
                    references.append(f"{bucket}:{path}")
        return references

    def _generate_preview(self, file_path: str, lines: int) -> Optional[Dict[str, Any]]:
        target = self.repo_root / file_path
        if not target.exists() or not target.is_file():
            return None

        head: List[str] = []
        tail: List[str] = []
        try:
            with target.open("r", encoding="utf-8", errors="ignore") as handle:
                all_lines = handle.readlines()
        except OSError:
            return None

        if not all_lines:
            return None

        head = [line.rstrip("\n") for line in all_lines[:lines]]
        if len(all_lines) > lines:
            tail = [line.rstrip("\n") for line in all_lines[-lines:]]

        return {
            "file_path": file_path,
            "head": head,
            "tail": tail,
            "total_lines": len(all_lines),
        }

    def _record_metric(self, skill_id: str, phase: int, payload: Dict[str, Any]) -> None:
        metric = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "skill_id": skill_id,
            "phase": phase,
            **payload,
        }
        try:
            with METRICS_PATH.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(metric) + "\n")
        except Exception:
            # Metrics collection should never break the main flow
            pass
