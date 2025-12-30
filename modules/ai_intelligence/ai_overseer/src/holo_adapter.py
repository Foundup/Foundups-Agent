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


try:
    # Lazy import; may trigger heavy deps in some environments
    from holo_index.core.holo_index import HoloIndex  # type: ignore
    _HOLOINDEX_AVAILABLE = True
except Exception:
    HoloIndex = None  # type: ignore
    _HOLOINDEX_AVAILABLE = False


class HoloAdapter:
    """Thin adapter exposing the minimal surface used by AI Overseer."""

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

        # Initialize HoloIndex if available; degrade gracefully otherwise
        self._holo = HoloIndex() if _HOLOINDEX_AVAILABLE else None

    # ------------------- SURFACE: search ------------------- #
    def search(
        self,
        query: str,
        limit: int = 5,
        doc_type_filter: str = "all",
    ) -> Dict[str, Any]:
        """Semantic search via HoloIndex; returns empty result if unavailable."""
        if self._holo is None:
            return {
                "query": query,
                "code": [],
                "wsps": [],
                "warnings": [],
                "reminders": [],
                "elapsed_ms": "0.0",
            }
        try:
            return self._holo.search(query, limit=limit, doc_type_filter=doc_type_filter)
        except Exception:
            # Never break overseer flow
            return {
                "query": query,
                "code": [],
                "wsps": [],
                "warnings": ["[WARN] HoloIndex.search failed; using fallback"],
                "reminders": [],
                "elapsed_ms": "0.0",
            }

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

        return {
            "ok": len(warnings) == 0,
            "warnings": warnings,
            "intent": intent or "unknown",
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


