#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for skill manifest hash/signature verification."""

from __future__ import annotations

from pathlib import Path

from modules.infrastructure.wre_core.src.skill_manifest_guard import (
    generate_skill_manifest,
    verify_skill_manifest,
)


def test_manifest_verification_passes_for_untampered_files(tmp_path: Path):
    skills_dir = tmp_path / "skills"
    (skills_dir / "a").mkdir(parents=True)
    (skills_dir / "a" / "SKILL.md").write_text("# ok", encoding="utf-8")
    manifest = skills_dir / "SKILL_MANIFEST.json"
    generate_skill_manifest(skills_dir, manifest_path=manifest)

    result = verify_skill_manifest(skills_dir, manifest_path=manifest, required=True)
    assert result.passed is True
    assert result.checked_files == 1


def test_manifest_verification_fails_on_hash_mismatch(tmp_path: Path):
    skills_dir = tmp_path / "skills"
    (skills_dir / "a").mkdir(parents=True)
    skill_file = skills_dir / "a" / "SKILL.md"
    skill_file.write_text("# v1", encoding="utf-8")
    manifest = skills_dir / "SKILL_MANIFEST.json"
    generate_skill_manifest(skills_dir, manifest_path=manifest)
    skill_file.write_text("# v2", encoding="utf-8")

    result = verify_skill_manifest(skills_dir, manifest_path=manifest, required=True)
    assert result.passed is False
    assert "a/SKILL.md" in result.mismatched_files


def test_manifest_signature_verification_passes_with_hmac_key(tmp_path: Path):
    skills_dir = tmp_path / "skills"
    (skills_dir / "a").mkdir(parents=True)
    (skills_dir / "a" / "SKILL.md").write_text("# signed", encoding="utf-8")
    manifest = skills_dir / "SKILL_MANIFEST.json"
    generate_skill_manifest(skills_dir, manifest_path=manifest, hmac_key="secret-key")

    result = verify_skill_manifest(
        skills_dir,
        manifest_path=manifest,
        required=True,
        verify_signature=True,
        hmac_key="secret-key",
    )
    assert result.passed is True
    assert result.signature_verified is True

