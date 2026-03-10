#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Git branch hygiene preflight checks for startup gating.

Read-only diagnostics. No auto-fix. Warns about stale branches, orphaned
worktrees, stash accumulation, and behind-main drift so 012 can see the
mess before it grows.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List


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


def _git(args: List[str], cwd: Path, timeout_sec: int = 30) -> Dict[str, Any]:
    """Run a git command and return structured result."""
    import shutil
    import subprocess

    git_bin = shutil.which("git")
    if not git_bin:
        return {"ok": False, "code": 127, "stdout": "", "stderr": "git not found"}
    cmd = [git_bin] + args
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            cwd=str(cwd),
        )
        return {
            "ok": True,
            "code": int(completed.returncode),
            "stdout": completed.stdout or "",
            "stderr": completed.stderr or "",
        }
    except Exception as exc:
        return {"ok": False, "code": 127, "stdout": "", "stderr": str(exc)}


# ---------------------------------------------------------------------------
# Individual checks — each returns a dict with {name, ok, message, detail}
# ---------------------------------------------------------------------------


def _check_main_behind_remote(cwd: Path) -> Dict[str, Any]:
    """Check if local main is behind origin/main."""
    result = _git(["rev-list", "--count", "main...origin/main", "--left-right"], cwd)
    if not result["ok"] or result["code"] != 0:
        return {"name": "main_behind_remote", "ok": True, "message": "skipped (no main or origin/main)", "detail": {}}
    # --left-right output: "<behind>\t<ahead>" (left=local-only, right=remote-only)
    parts = result["stdout"].strip().split()
    if len(parts) < 2:
        # Fallback: just count behind
        behind = _git(["rev-list", "--count", "main..origin/main"], cwd)
        if not behind["ok"] or behind["code"] != 0:
            return {"name": "main_behind_remote", "ok": True, "message": "skipped", "detail": {}}
        count = int(behind["stdout"].strip() or "0")
        if count > 0:
            return {
                "name": "main_behind_remote",
                "ok": False,
                "message": f"local main is {count} commits behind origin/main",
                "detail": {"behind": count},
            }
        return {"name": "main_behind_remote", "ok": True, "message": "main up to date", "detail": {"behind": 0}}
    # left-right: first number is local-only (ahead), second is remote-only (behind)
    behind = int(parts[1]) if len(parts) > 1 else 0
    if behind > 0:
        return {
            "name": "main_behind_remote",
            "ok": False,
            "message": f"local main is {behind} commits behind origin/main",
            "detail": {"behind": behind},
        }
    return {"name": "main_behind_remote", "ok": True, "message": "main up to date", "detail": {"behind": 0}}


def _check_stale_branches(cwd: Path) -> Dict[str, Any]:
    """Check for branches already merged into origin/main but not deleted."""
    result = _git(["branch", "--merged", "origin/main", "--format=%(refname:short)"], cwd)
    if not result["ok"] or result["code"] != 0:
        return {"name": "stale_branches", "ok": True, "message": "skipped", "detail": {}}
    merged = [
        b.strip() for b in result["stdout"].strip().splitlines()
        if b.strip() and b.strip() not in ("main", "master")
    ]
    if merged:
        names = ", ".join(merged[:5])
        suffix = f" (+{len(merged) - 5} more)" if len(merged) > 5 else ""
        return {
            "name": "stale_branches",
            "ok": False,
            "message": f"{len(merged)} branch(es) merged into origin/main but not deleted: {names}{suffix}",
            "detail": {"branches": merged},
        }
    return {"name": "stale_branches", "ok": True, "message": "no stale branches", "detail": {"branches": []}}


def _check_worktree_health(cwd: Path) -> Dict[str, Any]:
    """Check for detached HEAD worktrees."""
    result = _git(["worktree", "list", "--porcelain"], cwd)
    if not result["ok"] or result["code"] != 0:
        return {"name": "worktree_health", "ok": True, "message": "skipped", "detail": {}}
    detached: List[str] = []
    current_path = ""
    for line in result["stdout"].splitlines():
        if line.startswith("worktree "):
            current_path = line[len("worktree "):].strip()
        elif line.strip() == "detached":
            detached.append(current_path)
    if detached:
        return {
            "name": "worktree_health",
            "ok": False,
            "message": f"{len(detached)} worktree(s) in detached HEAD state (run: git worktree prune)",
            "detail": {"detached": detached},
        }
    return {"name": "worktree_health", "ok": True, "message": "worktrees healthy", "detail": {"detached": []}}


def _check_stash_count(cwd: Path, max_stashes: int) -> Dict[str, Any]:
    """Check if stash count exceeds threshold."""
    result = _git(["stash", "list"], cwd)
    if not result["ok"] or result["code"] != 0:
        return {"name": "stash_count", "ok": True, "message": "skipped", "detail": {}}
    lines = [l for l in result["stdout"].strip().splitlines() if l.strip()]
    count = len(lines)
    if count > max_stashes:
        return {
            "name": "stash_count",
            "ok": False,
            "message": f"{count} stashes (threshold: {max_stashes})",
            "detail": {"count": count, "threshold": max_stashes},
        }
    return {"name": "stash_count", "ok": True, "message": f"{count} stashes", "detail": {"count": count}}


def _check_unpushed_commits(cwd: Path) -> Dict[str, Any]:
    """Check if current branch has unpushed commits."""
    # Get current branch name
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    if not branch["ok"] or branch["code"] != 0:
        return {"name": "unpushed_commits", "ok": True, "message": "skipped", "detail": {}}
    branch_name = branch["stdout"].strip()
    if branch_name == "HEAD":
        return {"name": "unpushed_commits", "ok": True, "message": "detached HEAD", "detail": {}}
    # Check upstream
    result = _git(["log", "@{u}..HEAD", "--oneline"], cwd)
    if not result["ok"] or result["code"] != 0:
        # No upstream configured
        return {"name": "unpushed_commits", "ok": True, "message": f"no upstream for {branch_name}", "detail": {}}
    lines = [l for l in result["stdout"].strip().splitlines() if l.strip()]
    count = len(lines)
    if count > 0:
        return {
            "name": "unpushed_commits",
            "ok": False,
            "message": f"{count} unpushed commit(s) on {branch_name}",
            "detail": {"branch": branch_name, "count": count},
        }
    return {"name": "unpushed_commits", "ok": True, "message": f"{branch_name} pushed", "detail": {"count": 0}}


def _check_branch_behind_main(cwd: Path, max_behind: int) -> Dict[str, Any]:
    """Check if current branch is far behind origin/main."""
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    if not branch["ok"] or branch["code"] != 0:
        return {"name": "branch_behind_main", "ok": True, "message": "skipped", "detail": {}}
    branch_name = branch["stdout"].strip()
    if branch_name in ("main", "master", "HEAD"):
        return {"name": "branch_behind_main", "ok": True, "message": "on main", "detail": {}}
    result = _git(["rev-list", "--count", "HEAD..origin/main"], cwd)
    if not result["ok"] or result["code"] != 0:
        return {"name": "branch_behind_main", "ok": True, "message": "skipped", "detail": {}}
    behind = int(result["stdout"].strip() or "0")
    if behind > max_behind:
        return {
            "name": "branch_behind_main",
            "ok": False,
            "message": f"{branch_name} is {behind} commits behind origin/main (threshold: {max_behind})",
            "detail": {"branch": branch_name, "behind": behind, "threshold": max_behind},
        }
    return {
        "name": "branch_behind_main",
        "ok": True,
        "message": f"{branch_name} is {behind} behind main",
        "detail": {"behind": behind},
    }


# ---------------------------------------------------------------------------
# Cache helpers (same pattern as dependency_security_preflight.py)
# ---------------------------------------------------------------------------


def _cache_path(repo_root: Path) -> Path:
    return (
        repo_root
        / "modules/infrastructure/wre_core/reports/git_branch_hygiene_cache.json"
    )


def _load_cache(path: Path) -> Dict[str, Any] | None:
    try:
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except Exception:
        return None
    return None


def _save_cache(path: Path, payload: Dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except Exception:
        return


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def run_git_branch_hygiene_preflight(
    repo_root: Path, force: bool = False
) -> Dict[str, Any]:
    """Run 6 read-only git hygiene checks with TTL cache.

    Returns a dict with ``passed``, ``warnings``, ``checks``, and cache metadata.
    Always returns ``passed=True`` — this preflight warns but never blocks unless
    the caller checks the ``enforced`` env var separately.
    """
    repo_root = Path(repo_root).resolve()
    ttl_sec = _env_int("GIT_BRANCH_HYGIENE_PREFLIGHT_TTL_SEC", 3600)
    max_stashes = _env_int("GIT_BRANCH_HYGIENE_MAX_STASHES", 5)
    max_behind = _env_int("GIT_BRANCH_HYGIENE_MAX_BEHIND_MAIN", 20)

    cache = _cache_path(repo_root)
    now = time.time()
    cached = _load_cache(cache)
    if cached and not force:
        checked_at = float(cached.get("checked_at", 0))
        if checked_at > 0 and (now - checked_at) < max(ttl_sec, 0):
            cached["cached"] = True
            return cached

    # Refresh remote refs (fail-open, 15s timeout)
    _git(["fetch", "--all", "--quiet"], repo_root, timeout_sec=15)

    # Run all 6 checks
    checks: List[Dict[str, Any]] = [
        _check_main_behind_remote(repo_root),
        _check_stale_branches(repo_root),
        _check_worktree_health(repo_root),
        _check_stash_count(repo_root, max_stashes),
        _check_unpushed_commits(repo_root),
        _check_branch_behind_main(repo_root, max_behind),
    ]

    warnings = [c for c in checks if not c["ok"]]
    status = {
        "available": True,
        "passed": len(warnings) == 0,
        "checked_at": now,
        "cached": False,
        "ttl_sec": ttl_sec,
        "warning_count": len(warnings),
        "checks": checks,
        "message": f"warnings={len(warnings)}",
    }
    _save_cache(cache, status)
    return status
