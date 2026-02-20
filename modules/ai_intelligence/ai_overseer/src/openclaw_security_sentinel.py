#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OpenClaw security sentinel driven by AI Overseer.

Runs the OpenClaw skill safety scan and persists a TTL-bounded cache so
startup/runtime checks remain deterministic and auditable.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class OpenClawSecurityStatus:
    available: bool
    passed: bool
    required: bool
    enforced: bool
    cached: bool
    checked_at: float
    ttl_sec: int
    max_severity: str
    message: str
    skills_dir: str
    report_path: Optional[str]
    exit_code: int

    def as_dict(self) -> Dict[str, Any]:
        return {
            "available": self.available,
            "passed": self.passed,
            "required": self.required,
            "enforced": self.enforced,
            "cached": self.cached,
            "checked_at": self.checked_at,
            "ttl_sec": self.ttl_sec,
            "max_severity": self.max_severity,
            "message": self.message,
            "skills_dir": self.skills_dir,
            "report_path": self.report_path,
            "exit_code": self.exit_code,
        }


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return str(raw).strip().lower() not in {"0", "false", "no", "off"}


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


class OpenClawSecuritySentinel:
    """AI Overseer-managed OpenClaw security sentinel."""

    def __init__(
        self,
        repo_root: Path,
        *,
        skills_dir: Optional[Path] = None,
        cache_path: Optional[Path] = None,
    ):
        self.repo_root = Path(repo_root)
        self.skills_dir = (
            Path(skills_dir)
            if skills_dir
            else self.repo_root / "modules/communication/moltbot_bridge/workspace/skills"
        )
        default_cache = (
            self.repo_root
            / "modules/ai_intelligence/ai_overseer/memory/openclaw_security_sentinel.json"
        )
        self.cache_path = Path(os.getenv("OPENCLAW_SENTINEL_CACHE_PATH", str(cache_path or default_cache)))
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

    def check(self, *, force: bool = False) -> Dict[str, Any]:
        """Run (or reuse) OpenClaw security check."""
        ttl_sec = _env_int("OPENCLAW_SKILL_SCAN_TTL_SEC", 900)
        required = _env_bool("OPENCLAW_SKILL_SCAN_REQUIRED", True)
        enforced = _env_bool("OPENCLAW_SKILL_SCAN_ENFORCED", True)
        max_severity = os.getenv("OPENCLAW_SKILL_SCAN_MAX_SEVERITY", "medium")
        now = time.time()

        cached = self._load_cache()
        if cached and not force:
            checked_at = float(cached.get("checked_at", 0))
            if checked_at > 0 and (now - checked_at) < max(ttl_sec, 0):
                cached["cached"] = True
                return cached

        try:
            from modules.communication.moltbot_bridge.src.skill_safety_guard import run_skill_scan
        except Exception as exc:
            status = OpenClawSecurityStatus(
                available=False,
                passed=not required,
                required=required,
                enforced=enforced,
                cached=False,
                checked_at=now,
                ttl_sec=ttl_sec,
                max_severity=max_severity,
                message=f"skill safety guard unavailable: {exc}",
                skills_dir=str(self.skills_dir),
                report_path=None,
                exit_code=127,
            ).as_dict()
            self._save_cache(status)
            return status

        try:
            result = run_skill_scan(
                skills_dir=self.skills_dir,
                max_severity=max_severity,
            )
        except Exception as exc:
            status = OpenClawSecurityStatus(
                available=False,
                passed=not required,
                required=required,
                enforced=enforced,
                cached=False,
                checked_at=now,
                ttl_sec=ttl_sec,
                max_severity=max_severity,
                message=f"skill scan execution failed: {exc}",
                skills_dir=str(self.skills_dir),
                report_path=None,
                exit_code=70,
            ).as_dict()
            self._save_cache(status)
            return status
        if not result.available:
            passed = not required
        else:
            passed = result.passed or (not enforced)

        status = OpenClawSecurityStatus(
            available=result.available,
            passed=passed,
            required=required,
            enforced=enforced,
            cached=False,
            checked_at=now,
            ttl_sec=ttl_sec,
            max_severity=max_severity,
            message=result.message,
            skills_dir=result.skills_dir,
            report_path=result.report_path,
            exit_code=result.exit_code,
        ).as_dict()
        self._save_cache(status)
        return status

    def _load_cache(self) -> Optional[Dict[str, Any]]:
        if not self.cache_path.exists():
            return None
        try:
            return json.loads(self.cache_path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _save_cache(self, payload: Dict[str, Any]) -> None:
        try:
            self.cache_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception:
            # Non-fatal: cache write should never block security decision.
            pass
