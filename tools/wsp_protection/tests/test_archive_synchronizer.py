"""Tests for WSP framework -> knowledge backup synchronization."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


def _load_module():
    script_path = Path(__file__).resolve().parents[1] / "archive_synchronizer.py"
    spec = importlib.util.spec_from_file_location("archive_synchronizer", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def test_compare_detects_missing_and_drift(tmp_path) -> None:
    mod = _load_module()
    framework = tmp_path / "framework"
    knowledge = tmp_path / "knowledge"
    framework.mkdir()
    knowledge.mkdir()

    (framework / "WSP_1_Test.md").write_text("canonical", encoding="utf-8")
    (framework / "WSP_2_Test.md").write_text("canonical2", encoding="utf-8")
    (knowledge / "WSP_2_Test.md").write_text("drift", encoding="utf-8")

    report = mod.compare_framework_to_knowledge(framework, knowledge)
    assert "WSP_1_Test.md" in report.missing_in_knowledge
    assert "WSP_2_Test.md" in report.drifted_in_knowledge
    assert report.has_drift is True


def test_sync_copies_and_updates(tmp_path) -> None:
    mod = _load_module()
    framework = tmp_path / "framework"
    knowledge = tmp_path / "knowledge"
    framework.mkdir()
    knowledge.mkdir()

    (framework / "WSP_1_Test.md").write_text("canonical", encoding="utf-8")
    (framework / "WSP_2_Test.md").write_text("canonical2", encoding="utf-8")
    (knowledge / "WSP_2_Test.md").write_text("drift", encoding="utf-8")

    report = mod.sync_framework_to_knowledge(framework, knowledge)
    assert "WSP_1_Test.md" in report.copied_to_knowledge
    assert "WSP_2_Test.md" in report.updated_in_knowledge
    post = mod.compare_framework_to_knowledge(framework, knowledge)
    assert post.has_drift is False


def test_sync_preserves_backup_only_files_without_prune(tmp_path) -> None:
    mod = _load_module()
    framework = tmp_path / "framework"
    knowledge = tmp_path / "knowledge"
    framework.mkdir()
    knowledge.mkdir()

    (framework / "WSP_1_Test.md").write_text("canonical", encoding="utf-8")
    (knowledge / "WSP_1_Test.md").write_text("canonical", encoding="utf-8")
    backup_only = knowledge / "WSP_999_BackupOnly.md"
    backup_only.write_text("backup-only", encoding="utf-8")

    report = mod.sync_framework_to_knowledge(framework, knowledge, prune=False)
    assert "WSP_999_BackupOnly.md" in report.extra_in_knowledge
    assert backup_only.exists()


def test_sync_prunes_backup_only_files_when_requested(tmp_path) -> None:
    mod = _load_module()
    framework = tmp_path / "framework"
    knowledge = tmp_path / "knowledge"
    framework.mkdir()
    knowledge.mkdir()

    (framework / "WSP_1_Test.md").write_text("canonical", encoding="utf-8")
    (knowledge / "WSP_1_Test.md").write_text("canonical", encoding="utf-8")
    backup_only = knowledge / "WSP_999_BackupOnly.md"
    backup_only.write_text("backup-only", encoding="utf-8")

    report = mod.sync_framework_to_knowledge(framework, knowledge, prune=True)
    assert "WSP_999_BackupOnly.md" in report.deleted_from_knowledge
    assert not backup_only.exists()


def test_repo_framework_and_backup_mirror_have_no_drift() -> None:
    mod = _load_module()
    repo_root = Path(__file__).resolve().parents[3]
    framework = repo_root / "WSP_framework" / "src"
    knowledge = repo_root / "WSP_knowledge" / "src"

    report = mod.compare_framework_to_knowledge(framework, knowledge)
    assert report.missing_in_knowledge == []
    assert report.drifted_in_knowledge == []
