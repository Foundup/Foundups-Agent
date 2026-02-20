#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HoloAdapter - Minimal in-process facade for Holo core capabilities
=================================================================

Surface: search(), guard(), analyze_exec_log()

Design goals:
- Deterministic, local, and dependency-light by default
- Graceful degradation if HoloIndex or optional tools are unavailable
- Enforce WSP hygiene checks without noisy output
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import logging
import os
import time


# HoloIndex is loaded lazily on first use to avoid blocking main.py startup
# with 20-30s model load. See _get_holo() method.
_HOLOINDEX_AVAILABLE: Optional[bool] = None  # None = not yet checked
_HoloIndex_class = None  # type: ignore

try:
    from .holo_memory_sentinel import HoloMemorySentinel
    _SENTINEL_AVAILABLE = True
except Exception:
    HoloMemorySentinel = None  # type: ignore
    _SENTINEL_AVAILABLE = False


class HoloAdapter:
    """Thin adapter exposing the minimal surface used by AI Overseer.

    HoloIndex is loaded lazily on first ``search()`` call to avoid blocking
    ``main.py`` startup with a 20-30s SentenceTransformer model load.
    """

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = Path(repo_root)
        # WSP 60: Persist artifacts under module-local memory
        self.memory_dir = (
            self.repo_root
            / "modules"
            / "ai_intelligence"
            / "ai_overseer"
            / "memory"
        )
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Lazy initialization: HoloIndex is NOT constructed here.
        # It's constructed on first use via _get_holo() to keep main.py fast.
        self._holo = None
        self._holo_initialized = False
        self._sentinel = HoloMemorySentinel(self.repo_root) if _SENTINEL_AVAILABLE else None

    def _get_holo(self):
        """Lazy-load HoloIndex on first use. Returns None if unavailable."""
        if self._holo_initialized:
            return self._holo
        self._holo_initialized = True
        global _HOLOINDEX_AVAILABLE, _HoloIndex_class
        if _HOLOINDEX_AVAILABLE is None:
            try:
                from holo_index.core.holo_index import HoloIndex as _cls  # type: ignore
                _HoloIndex_class = _cls
                _HOLOINDEX_AVAILABLE = True
            except Exception:
                _HoloIndex_class = None
                _HOLOINDEX_AVAILABLE = False
        if _HOLOINDEX_AVAILABLE and _HoloIndex_class is not None:
            try:
                self._holo = _HoloIndex_class()
            except Exception as exc:
                logging.getLogger(__name__).warning(
                    "[HoloAdapter] Failed to initialize HoloIndex: %s", exc
                )
                self._holo = None
        return self._holo

    # ------------------- SURFACE: search ------------------- #
    def search(
        self,
        query: str,
        limit: int = 5,
        doc_type_filter: str = "all",
    ) -> Dict[str, Any]:
        """Semantic search via HoloIndex; returns empty result if unavailable."""
        holo = self._get_holo()
        if holo is None:
            empty_result = {
                "query": query,
                "code": [],
                "wsps": [],
                "warnings": [],
                "reminders": [],
                "elapsed_ms": "0.0",
            }
            if self._sentinel:
                self._sentinel.observe_search(query, empty_result)
            return empty_result
        try:
            results = holo.search(query, limit=limit, doc_type_filter=doc_type_filter)
            if self._sentinel:
                self._sentinel.observe_search(query, results)
            return results
        except Exception:
            # Never break overseer flow
            fallback = {
                "query": query,
                "code": [],
                "wsps": [],
                "warnings": ["[WARN] HoloIndex.search failed; using fallback"],
                "reminders": [],
                "elapsed_ms": "0.0",
            }
            if self._sentinel:
                self._sentinel.observe_search(query, fallback)
            return fallback

    # ------------------- SURFACE: guard ------------------- #
    def guard(
        self,
        payload: Any,
        intent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Lightweight WSP guard. Checks common hygiene rules and emits compact warnings.
        Rules covered:
        - WSP 60: Memory writes must target modules/<domain>/<module>/memory
        - WSP 85: No root directory artifacts
        - WSP 22: Prefer module ModLogs over root ModLog for module changes
        """
        warnings: List[str] = []
        intent_value = intent or "unknown"
        mode = (os.getenv("HOLO_GUARD_MODE", "summary") or "summary").lower()
        max_warnings = int(os.getenv("HOLO_GUARD_MAX_WARNINGS", "3"))
        intents_allow = os.getenv("HOLO_GUARD_INTENTS", "").strip()
        if intents_allow:
            allowed = {i.strip().lower() for i in intents_allow.split(",") if i.strip()}
            if intent_value.lower() not in allowed:
                return {
                    "ok": True,
                    "warnings": [],
                    "emit_warnings": [],
                    "intent": intent_value,
                    "mode": mode,
                }

        # Check for paths inside dict-like payloads
        def _scan(obj: Any) -> None:
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(v, (str, Path)):
                        self._check_path(str(v), warnings)
                    else:
                        _scan(v)
            elif isinstance(obj, list):
                for item in obj:
                    _scan(item)

        _scan(payload)

        warnings = list(dict.fromkeys(warnings))
        emit_warnings: List[str] = []
        if mode == "attach":
            emit_warnings = warnings[:max_warnings]
        elif mode == "summary" and warnings:
            emit_warnings = [warnings[0]]
            if len(warnings) > 1:
                emit_warnings.append(f"[GUARD] +{len(warnings) - 1} more warnings suppressed")

        self._persist_guard_report(intent_value, payload, warnings)

        return {
            "ok": len(warnings) == 0,
            "warnings": warnings,
            "emit_warnings": emit_warnings,
            "intent": intent_value,
            "mode": mode,
        }

    def _check_path(self, path_str: str, out: List[str]) -> None:
        p = Path(path_str)
        # WSP 85: discourage root artifacts
        if p.parent == self.repo_root:
            out.append("[WSP 85] Root artifact discouraged: " + str(p))
        # WSP 60: memory artifacts must live under module memory
        if p.suffix in {".json", ".log", ".ndjson"} and "memory" not in str(p).replace("\\", "/"):
            out.append("[WSP 60] Persist artifacts under module memory/: " + str(p))
        # WSP 22: ModLog selection hint
        if p.name.lower() == "modlog.md" and "modules" not in str(p).lower():
            out.append("[WSP 22] Prefer module ModLog over root ModLog for module-specific changes")

    def _persist_guard_report(self, intent: str, payload: Any, warnings: List[str]) -> None:
        """Persist guard warnings under module memory (no stdout noise)."""
        if not warnings:
            return
        try:
            report_dir = self.memory_dir / "guard_reports"
            report_dir.mkdir(parents=True, exist_ok=True)
            stamp = int(time.time())
            out_path = report_dir / f"guard_{stamp}.json"
            snapshot = {
                "intent": intent,
                "warnings": warnings,
                "payload_type": type(payload).__name__,
                "timestamp": stamp,
            }
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=2, ensure_ascii=False)
        except Exception:
            return

    # ------------------- SURFACE: analyze_exec_log ------------------- #
    def analyze_exec_log(self, mission_id: str, results: Dict[str, Any]) -> Optional[Path]:
        """
        Persist a compact execution report under module memory for later learning.
        Never raises; returns path if written.
        """
        try:
            report_dir = self.memory_dir / "exec_reports"
            report_dir.mkdir(parents=True, exist_ok=True)
            out_path = report_dir / f"exec_{mission_id}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            return out_path
        except Exception:
            return None
