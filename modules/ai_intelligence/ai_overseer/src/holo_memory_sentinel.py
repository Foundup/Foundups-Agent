#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HoloMemorySentinel - Silent per-session watcher for Holo searches.

Records compact memory bundles and quality metrics without printing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import json
import re
import uuid

try:
    from holo_index.feedback_learner import FeedbackRating, get_learner
    from holo_index.intent_classifier import IntentType
    _FEEDBACK_AVAILABLE = True
except Exception:
    FeedbackRating = None  # type: ignore
    get_learner = None  # type: ignore
    IntentType = None  # type: ignore
    _FEEDBACK_AVAILABLE = False


class HoloMemorySentinel:
    """Silent watcher that records Holo search quality and memory bundles."""

    def __init__(self, repo_root: Path, memory_dir: Optional[Path] = None) -> None:
        self.repo_root = Path(repo_root)
        self.memory_dir = memory_dir or (
            self.repo_root
            / "modules"
            / "ai_intelligence"
            / "ai_overseer"
            / "memory"
            / "holo_sentinel"
        )
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = uuid.uuid4().hex[:8]
        self._first_seen = True
        self._last_query: Optional[str] = None
        self._last_signature: Optional[str] = None
        self._system_checked = False

    def observe_search(self, query: str, results: Dict[str, Any]) -> None:
        """Observe a Holo search result and persist a compact record."""
        try:
            self._maybe_run_system_check()
            code_hits = results.get("code") or results.get("code_hits") or []
            wsp_hits = results.get("wsps") or results.get("wsp_hits") or []
            warnings = results.get("warnings") or []

            relevance = self._estimate_relevance(query, code_hits, wsp_hits)
            signature = self._signature(code_hits, wsp_hits)
            drift = (self._last_query == query and self._last_signature == signature)

            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_id": self.session_id,
                "first_seen": self._first_seen,
                "query": query,
                "metrics": {
                    "code_hits": len(code_hits),
                    "wsp_hits": len(wsp_hits),
                    "relevance": relevance,
                    "coverage_ok": bool(code_hits) and bool(wsp_hits),
                    "action_ready": bool(code_hits),
                    "noise_detected": self._detect_noise(warnings),
                    "drift": drift,
                },
                "memory_bundle": self._build_memory_bundle(code_hits, wsp_hits),
            }

            self._write_record(record)
            self._first_seen = False
            self._last_query = query
            self._last_signature = signature
        except Exception:
            # Silent by design
            pass

    def _maybe_run_system_check(self) -> None:
        if self._system_checked:
            return
        self._system_checked = True
        try:
            from holo_index.reports.holo_system_check import run_system_check, write_system_check_report
            report = run_system_check(self.repo_root)
            report_dir = self.memory_dir / "system_checks"
            report_path = write_system_check_report(report, report_dir)
            self._write_record({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_id": self.session_id,
                "event": "system_check",
                "report_path": str(report_path.relative_to(self.repo_root)),
                "summary": report.get("summary", {}),
            })
        except Exception:
            pass

    def record_memory_feedback(
        self,
        query: str,
        card_id: str,
        rating: str,
        notes: Optional[str] = None,
    ) -> Optional[str]:
        """Record explicit per-card feedback (good/noisy/missing)."""
        try:
            normalized = (rating or "").strip().lower()
            rating_enum = None
            if normalized == "good":
                rating_enum = FeedbackRating.GOOD if FeedbackRating else None
            elif normalized == "noisy":
                rating_enum = FeedbackRating.NOISY if FeedbackRating else None
            elif normalized == "missing":
                rating_enum = FeedbackRating.MISSING if FeedbackRating else None

            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_id": self.session_id,
                "event": "memory_feedback",
                "query": query,
                "card_id": card_id,
                "rating": normalized,
                "notes": notes,
            }
            self._write_record(record)

            if _FEEDBACK_AVAILABLE and rating_enum is not None:
                learner = get_learner()
                return learner.record_feedback(
                    query=query or "unknown",
                    intent=IntentType.GENERAL,
                    components_executed=[card_id],
                    rating=rating_enum,
                    notes=notes or f"memory_card:{card_id}",
                )
        except Exception:
            pass
        return None

    def _estimate_relevance(self, query: str, code_hits: List[Dict[str, Any]], wsp_hits: List[Dict[str, Any]]) -> float:
        tokens = [t for t in re.split(r"[^a-z0-9]+", query.lower()) if len(t) > 2]
        if not tokens:
            return 0.0

        hay = ""
        if code_hits:
            top = code_hits[0]
            hay = " ".join([
                str(top.get("need", "")),
                str(top.get("location", "")),
                str(top.get("path", "")),
                str(top.get("preview", "")),
            ])
        if wsp_hits:
            top = wsp_hits[0]
            hay += " " + " ".join([
                str(top.get("title", "")),
                str(top.get("summary", "")),
            ])
        hay = hay.lower()
        hits = sum(1 for t in tokens if t in hay)
        return round(hits / max(1, len(tokens)), 2)

    def _signature(self, code_hits: List[Dict[str, Any]], wsp_hits: List[Dict[str, Any]]) -> str:
        top_code = ""
        top_wsp = ""
        if code_hits:
            top_code = code_hits[0].get("location") or code_hits[0].get("path") or ""
        if wsp_hits:
            top_wsp = wsp_hits[0].get("path") or ""
        return f"c{len(code_hits)}|w{len(wsp_hits)}|{top_code}|{top_wsp}"

    def _detect_noise(self, warnings: List[str]) -> bool:
        for warning in warnings:
            lower = warning.lower()
            if any(term in lower for term in ["posthog", "telemetry", "httpx", "urllib3", "chromadb"]):
                return True
        return False

    def _build_memory_bundle(self, code_hits: List[Dict[str, Any]], wsp_hits: List[Dict[str, Any]]) -> Dict[str, Any]:
        code_ptrs = []
        for hit in code_hits[:3]:
            pointer = hit.get("location") or hit.get("path")
            if pointer:
                code_ptrs.append(pointer)

        wsp_ptrs = []
        for hit in wsp_hits[:3]:
            pointer = hit.get("path") or hit.get("location")
            if pointer:
                wsp_ptrs.append(pointer)

        return {
            "code": code_ptrs,
            "wsp": wsp_ptrs,
        }

    def _write_record(self, record: Dict[str, Any]) -> None:
        out_path = self.memory_dir / f"holo_sentinel_{self.session_id}.jsonl"
        with out_path.open("a", encoding="utf-8") as handle:
            json.dump(record, handle, ensure_ascii=False)
            handle.write("\n")
