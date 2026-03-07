#!/usr/bin/env python3
"""Tests for centralized local model routing."""

from __future__ import annotations

from pathlib import Path

from modules.infrastructure.shared_utilities import local_model_selection as lms


def _clear_role_overrides(monkeypatch) -> None:
    monkeypatch.delenv("LOCAL_MODEL_TRIAGE_PATH", raising=False)
    monkeypatch.delenv("LOCAL_MODEL_TRIAGE_DIR", raising=False)
    monkeypatch.delenv("LOCAL_MODEL_GENERAL_PATH", raising=False)
    monkeypatch.delenv("LOCAL_MODEL_GENERAL_DIR", raising=False)
    monkeypatch.delenv("LOCAL_MODEL_CODE_PATH", raising=False)
    monkeypatch.delenv("LOCAL_MODEL_CODE_DIR", raising=False)
    monkeypatch.delenv("HOLO_QWEN_MODEL", raising=False)
    monkeypatch.delenv("LOCAL_MODEL_ENABLE_LEGACY_FALLBACK", raising=False)


def test_resolve_code_model_prefers_role_default_dir(tmp_path: Path, monkeypatch) -> None:
    _clear_role_overrides(monkeypatch)
    monkeypatch.setenv("LOCAL_MODEL_ROOT", str(tmp_path))

    code_dir = tmp_path / "qwen-coder-7b"
    code_dir.mkdir(parents=True)
    code_model = code_dir / "qwen2.5-coder-7b-instruct-q4_k_m.gguf"
    code_model.write_bytes(b"stub")

    selection = lms.resolve_model_selection("code")
    assert selection.path == code_model
    assert selection.exists is True
    assert selection.source == "LOCAL_MODEL_ROOT/default"


def test_legacy_fallback_disabled_by_default(tmp_path: Path, monkeypatch) -> None:
    _clear_role_overrides(monkeypatch)
    monkeypatch.setenv("LOCAL_MODEL_ROOT", str(tmp_path / "missing-root"))

    legacy_model = tmp_path / "legacy" / "qwen-coder-1.5b.gguf"
    legacy_model.parent.mkdir(parents=True)
    legacy_model.write_bytes(b"stub")

    patched_fallbacks = dict(lms.LEGACY_FILE_FALLBACKS)
    patched_fallbacks["code"] = [legacy_model]
    monkeypatch.setattr(lms, "LEGACY_FILE_FALLBACKS", patched_fallbacks)

    selection = lms.resolve_model_selection("code")
    assert selection.source != "legacy_fallback"
    assert selection.path != legacy_model
    assert selection.exists is False


def test_legacy_fallback_enabled_with_opt_in(tmp_path: Path, monkeypatch) -> None:
    _clear_role_overrides(monkeypatch)
    monkeypatch.setenv("LOCAL_MODEL_ROOT", str(tmp_path / "missing-root"))
    monkeypatch.setenv("LOCAL_MODEL_ENABLE_LEGACY_FALLBACK", "1")

    legacy_model = tmp_path / "legacy" / "qwen-coder-1.5b.gguf"
    legacy_model.parent.mkdir(parents=True)
    legacy_model.write_bytes(b"stub")

    patched_fallbacks = dict(lms.LEGACY_FILE_FALLBACKS)
    patched_fallbacks["code"] = [legacy_model]
    monkeypatch.setattr(lms, "LEGACY_FILE_FALLBACKS", patched_fallbacks)

    selection = lms.resolve_model_selection("code")
    assert selection.source == "legacy_fallback"
    assert selection.path == legacy_model
    assert selection.exists is True


def test_resolve_general_model_prefers_qwen3_5_default_dir(tmp_path: Path, monkeypatch) -> None:
    _clear_role_overrides(monkeypatch)
    monkeypatch.setenv("LOCAL_MODEL_ROOT", str(tmp_path))

    general_dir = tmp_path / "qwen3.5-4b"
    general_dir.mkdir(parents=True)
    general_model = general_dir / "Qwen3.5-4B-Instruct-Q4_K_M.gguf"
    general_model.write_bytes(b"stub")

    selection = lms.resolve_model_selection("general")
    assert selection.path == general_model
    assert selection.exists is True
    assert selection.source == "LOCAL_MODEL_ROOT/default"
