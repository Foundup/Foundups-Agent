"""Tests for git main-merge sentinel safety behavior."""

from pathlib import Path

from modules.infrastructure.wre_core.src import git_main_merge_sentinel as sentinel


def test_merge_sentinel_disarms_on_dirty_feature_branch(monkeypatch, tmp_path: Path):
    calls = []

    def fake_git(args, cwd, timeout_sec=30):
        calls.append(tuple(args))
        if args == ["rev-parse", "--abbrev-ref", "HEAD"]:
            return {"ok": True, "code": 0, "stdout": "feature/test\n", "stderr": ""}
        if args == ["status", "--porcelain"]:
            return {"ok": True, "code": 0, "stdout": " M main.py\n?? notes.txt\n", "stderr": ""}
        raise AssertionError(f"unexpected git call: {args}")

    monkeypatch.setattr(sentinel, "_git", fake_git)
    result = sentinel.run_main_merge_sentinel(tmp_path)

    assert result["passed"] is True
    assert result["merged"] is False
    assert result["branch"] == "feature/test"
    assert result["dirty_count"] == 2
    assert "dirty worktree detected" in result["message"]
    assert calls == [
        ("rev-parse", "--abbrev-ref", "HEAD"),
        ("status", "--porcelain"),
    ]


def test_merge_sentinel_disarms_on_dirty_main_before_push(monkeypatch, tmp_path: Path):
    calls = []

    def fake_git(args, cwd, timeout_sec=30):
        calls.append(tuple(args))
        if args == ["rev-parse", "--abbrev-ref", "HEAD"]:
            return {"ok": True, "code": 0, "stdout": "main\n", "stderr": ""}
        if args == ["status", "--porcelain"]:
            return {"ok": True, "code": 0, "stdout": " M modules/file.py\n", "stderr": ""}
        raise AssertionError(f"unexpected git call: {args}")

    monkeypatch.setattr(sentinel, "_git", fake_git)
    result = sentinel.run_main_merge_sentinel(tmp_path)

    assert result["passed"] is True
    assert result["merged"] is False
    assert result["branch"] == "main"
    assert result["dirty_count"] == 1
    assert "merge sentinel disarmed" in result["message"]
    assert calls == [
        ("rev-parse", "--abbrev-ref", "HEAD"),
        ("status", "--porcelain"),
    ]
