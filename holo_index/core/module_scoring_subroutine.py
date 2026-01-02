# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

try:
    from tools.shared.module_scoring_engine import WSP37ScoringEngine
except Exception:
    WSP37ScoringEngine = None  # type: ignore

logger = logging.getLogger(__name__)


class ModuleScoringSubroutine:
    """WSP 15/37 module scoring wrapper for HoloIndex subroutines."""

    def __init__(self, project_root: Optional[Path] = None, scoring_file: Optional[Path] = None) -> None:
        self.project_root = project_root or Path(__file__).resolve().parents[2]
        self.scoring_file = scoring_file or self._resolve_scoring_file()

    def _resolve_scoring_file(self) -> Optional[Path]:
        candidates = [
            self.project_root / "modules_to_score.yaml",
            self.project_root / "modules" / "development" / "modules_to_score.yaml",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    def _load_scoring_metadata(self) -> Dict[str, Dict[str, Any]]:
        if not self.scoring_file or not self.scoring_file.exists() or yaml is None:
            return {}

        try:
            data = yaml.safe_load(self.scoring_file.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.debug("Module scoring metadata load failed: %s", exc)
            return {}

        modules = data.get("modules", []) if isinstance(data, dict) else []
        metadata: Dict[str, Dict[str, Any]] = {}
        for module in modules:
            name = module.get("name")
            path = module.get("path")
            if name:
                metadata[str(name)] = module
            if path:
                metadata[str(path)] = module
        return metadata

    def _normalize(self, value: str) -> str:
        return value.replace("\\", "/").strip().lower()

    def _match_target(self, target_module: str, entries: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        target_norm = self._normalize(target_module)
        for entry in entries:
            name = self._normalize(str(entry.get("name", "")))
            path = self._normalize(str(entry.get("path", "")))
            if target_norm == name or target_norm == path:
                return entry
            if path.endswith(target_norm):
                return entry
        return None

    def score(self, target_module: Optional[str] = None, limit: int = 3) -> Dict[str, Any]:
        if WSP37ScoringEngine is None:
            return {"error": "module scoring engine unavailable"}

        if not self.scoring_file:
            return {"error": "modules_to_score.yaml not found"}

        engine = WSP37ScoringEngine(scoring_file=str(self.scoring_file))
        prioritized = engine.export_prioritized_list()

        metadata = self._load_scoring_metadata()
        for entry in prioritized:
            meta = metadata.get(entry.get("name")) or metadata.get(entry.get("path"))
            if not meta:
                continue
            entry["active"] = meta.get("active", False)
            entry["activation_phase"] = meta.get("activation_phase")
            entry["llme_current"] = meta.get("llme_current")
            entry["llme_target"] = meta.get("llme_target")

        active = [entry for entry in prioritized if entry.get("active")]
        inactive = [entry for entry in prioritized if not entry.get("active")]

        response: Dict[str, Any] = {
            "scoring_file": str(self.scoring_file),
            "top_active": active[:limit] if active else prioritized[:limit],
            "top_inactive": inactive[:limit],
        }

        if target_module:
            response["target_module"] = target_module
            response["target_score"] = self._match_target(target_module, prioritized)

        return response
