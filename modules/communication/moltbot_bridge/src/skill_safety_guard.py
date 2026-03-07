#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Skill safety guard for OpenClaw workspace skills.

Runs Cisco Skill Scanner (`skill-scanner`) as a preflight safety check before
executing potentially mutating intents.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from modules.infrastructure.wre_core.src.skill_manifest_guard import verify_skill_manifest


@dataclass
class SkillScanResult:
    available: bool
    passed: bool
    exit_code: int
    skills_dir: str
    report_path: Optional[str]
    message: str
    stdout: str = ""
    stderr: str = ""
    manifest_available: bool = False
    manifest_passed: bool = False
    manifest_path: Optional[str] = None
    manifest_message: str = ""


_SEVERITY_ORDER = {
    "info": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


def _threshold_exceeded(report_path: Path, max_severity: str) -> Optional[bool]:
    """Return True if findings exceed threshold, False if safe, None on parse failure."""
    if not report_path.exists():
        return None

    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    summary = payload.get("summary", {})
    findings = summary.get("findings_by_severity", {})
    allowed = _SEVERITY_ORDER.get(max_severity.lower(), _SEVERITY_ORDER["medium"])
    for severity, count in findings.items():
        rank = _SEVERITY_ORDER.get(str(severity).lower(), -1)
        if rank >= allowed and int(count) > 0:
            return True
    return False


def run_skill_scan(
    skills_dir: Path,
    *,
    max_severity: str = "medium",
    timeout_sec: int = 90,
    report_dir: Optional[Path] = None,
    manifest_required: Optional[bool] = None,
    manifest_enforced: Optional[bool] = None,
    manifest_verify_signature: Optional[bool] = None,
    manifest_allow_extra: Optional[bool] = None,
    manifest_path: Optional[Path] = None,
    manifest_hmac_key: Optional[str] = None,
) -> SkillScanResult:
    """Run Cisco skill scanner against a local skills directory.

    Returns a normalized result that callers can use for fail-open/fail-closed
    policy decisions.
    """
    env_cmd = os.getenv("OPENCLAW_SKILL_SCANNER_BIN")
    scanner_cmd = env_cmd or shutil.which("skill-scanner")
    skills_dir = skills_dir.resolve()
    report_dir = (report_dir or skills_dir.parent / "reports").resolve()
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "openclaw_skill_scan_report.json"

    if manifest_required is None:
        manifest_required = os.getenv("OPENCLAW_SKILL_MANIFEST_REQUIRED", "1").strip() == "1"
    if manifest_enforced is None:
        manifest_enforced = os.getenv("OPENCLAW_SKILL_MANIFEST_ENFORCED", "1").strip() == "1"
    if manifest_verify_signature is None:
        manifest_verify_signature = (
            os.getenv("OPENCLAW_SKILL_MANIFEST_VERIFY_SIGNATURE", "0").strip() == "1"
        )
    if manifest_allow_extra is None:
        manifest_allow_extra = os.getenv("OPENCLAW_SKILL_MANIFEST_ALLOW_EXTRA", "0").strip() == "1"
    if manifest_hmac_key is None:
        manifest_hmac_key = os.getenv("OPENCLAW_SKILL_MANIFEST_HMAC_KEY")
    if manifest_path is None:
        manifest_override = os.getenv("OPENCLAW_SKILL_MANIFEST_FILE")
        manifest_path = (
            Path(manifest_override).resolve()
            if manifest_override
            else (skills_dir / "SKILL_MANIFEST.json")
        )

    manifest_result = verify_skill_manifest(
        skills_dir=skills_dir,
        manifest_path=manifest_path,
        required=manifest_required,
        verify_signature=manifest_verify_signature,
        hmac_key=manifest_hmac_key,
        allow_extra=manifest_allow_extra,
    )

    if not manifest_result.passed and manifest_enforced:
        return SkillScanResult(
            available=True,
            passed=False,
            exit_code=3,
            skills_dir=str(skills_dir),
            report_path=str(report_path),
            message=f"manifest verification failed: {manifest_result.message}",
            manifest_available=manifest_result.available,
            manifest_passed=manifest_result.passed,
            manifest_path=manifest_result.manifest_path,
            manifest_message=manifest_result.message,
        )

    if scanner_cmd is None:
        # Fallback: local repo venv command path.
        repo_root = skills_dir.parents[4] if len(skills_dir.parents) >= 5 else None
        if repo_root:
            win_bin = repo_root / ".venv" / "Scripts" / "skill-scanner.exe"
            unix_bin = repo_root / ".venv" / "bin" / "skill-scanner"
            if win_bin.exists():
                scanner_cmd = str(win_bin)
            elif unix_bin.exists():
                scanner_cmd = str(unix_bin)

    if scanner_cmd is None:
        return SkillScanResult(
            available=False,
            passed=False,
            exit_code=127,
            skills_dir=str(skills_dir),
            report_path=str(report_path),
            message="skill-scanner not installed (pip install cisco-ai-skill-scanner)",
            manifest_available=manifest_result.available,
            manifest_passed=manifest_result.passed,
            manifest_path=manifest_result.manifest_path,
            manifest_message=manifest_result.message,
        )

    if not skills_dir.exists():
        return SkillScanResult(
            available=True,
            passed=False,
            exit_code=2,
            skills_dir=str(skills_dir),
            report_path=str(report_path),
            message=f"skills directory not found: {skills_dir}",
            manifest_available=manifest_result.available,
            manifest_passed=manifest_result.passed,
            manifest_path=manifest_result.manifest_path,
            manifest_message=manifest_result.message,
        )

    cmd = [
        scanner_cmd,
        "scan-all",
        str(skills_dir),
        "--recursive",
        "--format",
        "json",
        "--output",
        str(report_path),
    ]

    env = os.environ.copy()
    completed = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout_sec,
        env=env,
    )

    passed = completed.returncode == 0
    exceeds_threshold = _threshold_exceeded(report_path, max_severity)
    if exceeds_threshold is True:
        passed = False
    msg = "skills passed safety scan"
    if not passed:
        msg = (
            f"skill scan failed (exit={completed.returncode}) "
            f"max_severity={max_severity}"
        )

    return SkillScanResult(
        available=True,
        passed=passed,
        exit_code=completed.returncode,
        skills_dir=str(skills_dir),
        report_path=str(report_path),
        message=msg,
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
        manifest_available=manifest_result.available,
        manifest_passed=manifest_result.passed,
        manifest_path=manifest_result.manifest_path,
        manifest_message=manifest_result.message,
    )
