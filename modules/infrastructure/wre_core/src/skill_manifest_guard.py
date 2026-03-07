#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Skill manifest integrity verification (hash + optional signature)."""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class SkillManifestResult:
    available: bool
    passed: bool
    manifest_path: Optional[str]
    message: str
    checked_files: int = 0
    missing_files: List[str] = field(default_factory=list)
    mismatched_files: List[str] = field(default_factory=list)
    unexpected_files: List[str] = field(default_factory=list)
    signature_verified: bool = False


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _collect_skill_docs(skills_dir: Path) -> List[Path]:
    files: List[Path] = []
    for pattern in ("**/SKILL.md", "**/SKILLz.md"):
        files.extend(skills_dir.glob(pattern))
    return sorted({p.resolve() for p in files})


def _canonical_signature_payload(entries: List[Tuple[str, str]]) -> str:
    lines = [f"{path}:{sha}" for path, sha in sorted(entries)]
    return "\n".join(lines)


def generate_skill_manifest(
    skills_dir: Path,
    *,
    manifest_path: Optional[Path] = None,
    hmac_key: Optional[str] = None,
) -> Dict:
    """Generate manifest payload for workspace skills."""
    skills_dir = skills_dir.resolve()
    docs = _collect_skill_docs(skills_dir)
    files = []
    tuples: List[Tuple[str, str]] = []
    for p in docs:
        rel = p.relative_to(skills_dir).as_posix()
        sha = _sha256(p)
        files.append({"path": rel, "sha256": sha})
        tuples.append((rel, sha))

    payload: Dict[str, object] = {"version": 1, "files": files}
    if hmac_key:
        canonical = _canonical_signature_payload(tuples)
        sig = hmac.new(
            hmac_key.encode("utf-8"),
            canonical.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        payload["signature"] = {"algorithm": "hmac-sha256", "value": sig}

    if manifest_path:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def verify_skill_manifest(
    skills_dir: Path,
    *,
    manifest_path: Optional[Path] = None,
    required: bool = True,
    verify_signature: bool = False,
    hmac_key: Optional[str] = None,
    allow_extra: bool = False,
) -> SkillManifestResult:
    """Verify workspace skill files against signed hash manifest."""
    skills_dir = skills_dir.resolve()
    manifest_path = (manifest_path or (skills_dir / "SKILL_MANIFEST.json")).resolve()

    if not manifest_path.exists():
        return SkillManifestResult(
            available=False,
            passed=not required,
            manifest_path=str(manifest_path),
            message="manifest not found",
        )

    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return SkillManifestResult(
            available=True,
            passed=False,
            manifest_path=str(manifest_path),
            message=f"manifest parse failed: {exc}",
        )

    files = payload.get("files", [])
    if not isinstance(files, list):
        return SkillManifestResult(
            available=True,
            passed=False,
            manifest_path=str(manifest_path),
            message="manifest missing files list",
        )

    expected: Dict[str, str] = {}
    for entry in files:
        if not isinstance(entry, dict):
            continue
        rel = str(entry.get("path", "")).strip()
        sha = str(entry.get("sha256", "")).strip().lower()
        if rel and sha:
            expected[rel] = sha

    if not expected:
        return SkillManifestResult(
            available=True,
            passed=False,
            manifest_path=str(manifest_path),
            message="manifest contains no valid entries",
        )

    missing_files: List[str] = []
    mismatched_files: List[str] = []
    tuples: List[Tuple[str, str]] = []
    for rel, expected_sha in expected.items():
        path = (skills_dir / rel).resolve()
        if not path.exists():
            missing_files.append(rel)
            continue
        actual_sha = _sha256(path)
        tuples.append((rel, actual_sha))
        if actual_sha.lower() != expected_sha.lower():
            mismatched_files.append(rel)

    unexpected_files: List[str] = []
    if not allow_extra:
        listed = {k for k in expected.keys()}
        for p in _collect_skill_docs(skills_dir):
            rel = p.relative_to(skills_dir).as_posix()
            if rel not in listed:
                unexpected_files.append(rel)

    signature_verified = False
    if verify_signature:
        sig_obj = payload.get("signature", {})
        algorithm = str((sig_obj or {}).get("algorithm", "")).strip().lower()
        signature = str((sig_obj or {}).get("value", "")).strip().lower()
        if algorithm != "hmac-sha256" or not signature:
            return SkillManifestResult(
                available=True,
                passed=False,
                manifest_path=str(manifest_path),
                message="signature missing or unsupported algorithm",
                checked_files=len(expected),
                missing_files=missing_files,
                mismatched_files=mismatched_files,
                unexpected_files=unexpected_files,
                signature_verified=False,
            )
        if not hmac_key:
            return SkillManifestResult(
                available=True,
                passed=False,
                manifest_path=str(manifest_path),
                message="signature verification requested but HMAC key missing",
                checked_files=len(expected),
                missing_files=missing_files,
                mismatched_files=mismatched_files,
                unexpected_files=unexpected_files,
                signature_verified=False,
            )
        canonical = _canonical_signature_payload(tuples)
        computed = hmac.new(
            hmac_key.encode("utf-8"),
            canonical.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        signature_verified = hmac.compare_digest(computed, signature)
        if not signature_verified:
            return SkillManifestResult(
                available=True,
                passed=False,
                manifest_path=str(manifest_path),
                message="signature verification failed",
                checked_files=len(expected),
                missing_files=missing_files,
                mismatched_files=mismatched_files,
                unexpected_files=unexpected_files,
                signature_verified=False,
            )

    passed = not (missing_files or mismatched_files or unexpected_files)
    message = "manifest verified" if passed else "manifest verification failed"
    return SkillManifestResult(
        available=True,
        passed=passed,
        manifest_path=str(manifest_path),
        message=message,
        checked_files=len(expected),
        missing_files=missing_files,
        mismatched_files=mismatched_files,
        unexpected_files=unexpected_files,
        signature_verified=signature_verified or (not verify_signature),
    )

