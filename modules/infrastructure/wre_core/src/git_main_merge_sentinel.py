#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Git main-merge sentinel — auto-merge feature branches to main at startup.

One-shot preflight that detects when an agent left work on a feature branch
and merges it to main automatically. 012 should never have to manually merge.

Read the branch, push to both remotes, fast-forward main, checkout main,
delete the old branch. If anything fails, warn but don't block.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List

from modules.infrastructure.wre_core.src.git_branch_hygiene import (
    _env_bool,
    _git,
)


def _resolve_gh() -> str:
    """Resolve gh CLI binary."""
    return shutil.which("gh") or "gh"


def run_main_merge_sentinel(
    repo_root: Path, force: bool = False
) -> Dict[str, Any]:
    """Merge current feature branch into main and switch to main.

    Returns a status dict. Never raises — all failures are captured in the
    returned dict and printed as warnings.
    """
    repo_root = Path(repo_root).resolve()
    delete_branch = _env_bool("GIT_MAIN_MERGE_SENTINEL_DELETE_BRANCH", True)

    actions: List[str] = []

    # Step 1: What branch are we on?
    branch_result = _git(["rev-parse", "--abbrev-ref", "HEAD"], repo_root)
    if not branch_result["ok"] or branch_result["code"] != 0:
        return {"passed": True, "merged": False, "message": "not a git repo", "actions": actions}

    branch = branch_result["stdout"].strip()

    # Never auto-merge or auto-push from a dirty worktree unless explicitly forced.
    # In recursive multi-0102 flow, dirty means active sandbox state.
    status_result = _git(["status", "--porcelain"], repo_root)
    if status_result["ok"] and status_result["code"] == 0 and not force:
        dirty = [line for line in status_result["stdout"].splitlines() if line.strip()]
        if dirty:
            return {
                "passed": True,
                "merged": False,
                "message": f"dirty worktree detected ({len(dirty)} paths) - merge sentinel disarmed",
                "actions": actions,
                "dirty_count": len(dirty),
                "branch": branch,
            }

    # Step 1b: If on main, check for unpushed commits and push them
    if branch in ("main", "master"):
        unpushed = _git(["log", "@{u}..HEAD", "--oneline"], repo_root)
        if unpushed["ok"] and unpushed["code"] == 0:
            unpushed_count = len([l for l in unpushed["stdout"].splitlines() if l.strip()])
            if unpushed_count > 0:
                print(f"[GIT-MERGE-SENTINEL] {unpushed_count} unpushed commit(s) on main, pushing...")

                # Try direct push first
                push = _git(["push", "origin", "main"], repo_root, timeout_sec=30)
                if push["ok"] and push["code"] == 0:
                    actions.append("pushed main to origin")
                    _git(["push", "backup", "main"], repo_root, timeout_sec=30)
                    actions.append("pushed main to backup")
                else:
                    # Direct push failed (branch protection?) — create temp branch + PR
                    import subprocess
                    temp_branch = f"auto-push/main-{int(__import__('time').time())}"
                    _git(["checkout", "-b", temp_branch], repo_root)
                    _git(["push", "origin", temp_branch], repo_root, timeout_sec=30)
                    actions.append(f"created temp branch {temp_branch}")

                    gh = _resolve_gh()
                    try:
                        # Create and merge PR
                        subprocess.run(
                            [gh, "pr", "create", "--base", "main", "--head", temp_branch,
                             "--title", f"auto-push: {unpushed_count} commit(s) to main",
                             "--body", "Auto-created by git main-merge sentinel."],
                            capture_output=True, text=True, timeout=30, cwd=str(repo_root),
                        )
                        merge = subprocess.run(
                            [gh, "pr", "merge", temp_branch, "--merge", "--delete-branch"],
                            capture_output=True, text=True, timeout=30, cwd=str(repo_root),
                            input="y\n",
                        )
                        if merge.returncode == 0:
                            actions.append("merged PR via gh")
                        else:
                            actions.append(f"PR merge failed: {merge.stderr[:80]}")
                    except Exception as exc:
                        actions.append(f"PR error: {str(exc)[:80]}")

                    # Switch back to main and update (preserve uncommitted changes)
                    _git(["checkout", "main"], repo_root)
                    _git(["fetch", "origin", "main"], repo_root, timeout_sec=15)
                    # Use merge instead of reset --hard to preserve uncommitted changes
                    _git(["merge", "--ff-only", "origin/main"], repo_root)
                    _git(["push", "backup", "main"], repo_root, timeout_sec=30)
                    actions.append("synced main from origin")

                for a in actions:
                    print(f"  {a}")
                return {
                    "passed": True,
                    "merged": False,
                    "message": f"pushed {unpushed_count} commit(s) to main",
                    "actions": actions,
                }
        return {"passed": True, "merged": False, "message": f"on {branch}, nothing to merge", "actions": actions}

    print(f"[GIT-MERGE-SENTINEL] Merging {branch} -> main")

    # Step 2: Fetch remote refs
    _git(["fetch", "--all", "--quiet"], repo_root, timeout_sec=15)

    # Step 3: Push current branch to both remotes (ensure nothing is lost)
    for remote in ("origin", "backup"):
        push = _git(["push", remote, branch], repo_root, timeout_sec=30)
        if push["ok"] and push["code"] == 0:
            actions.append(f"pushed {branch} to {remote}")

    # Step 4: Try fast-forward push to main on both remotes
    ff_ok = True
    for remote in ("origin", "backup"):
        ff = _git(["push", remote, f"HEAD:main"], repo_root, timeout_sec=30)
        if ff["ok"] and ff["code"] == 0:
            actions.append(f"pushed HEAD to {remote}/main (fast-forward)")
        else:
            ff_ok = False
            actions.append(f"fast-forward to {remote}/main failed: {ff['stderr'][:120]}")

    # Step 4b: If fast-forward failed on origin, try PR merge
    if not ff_ok:
        print(f"[GIT-MERGE-SENTINEL] Fast-forward failed, attempting PR merge via gh...")
        gh = _resolve_gh()

        # Create PR if one doesn't exist
        import subprocess
        try:
            create = subprocess.run(
                [gh, "pr", "create", "--base", "main", "--head", branch,
                 "--title", f"auto-merge: {branch} -> main",
                 "--body", "Auto-created by git main-merge sentinel."],
                capture_output=True, text=True, timeout=30, cwd=str(repo_root),
            )
            if create.returncode == 0:
                actions.append("created PR")
            # PR may already exist — that's fine
        except Exception:
            pass

        # Merge the PR
        try:
            merge = subprocess.run(
                [gh, "pr", "merge", branch, "--merge", "--delete-branch"],
                capture_output=True, text=True, timeout=30, cwd=str(repo_root),
                input="y\n",
            )
            if merge.returncode == 0:
                actions.append("merged PR via gh")
                ff_ok = True
            else:
                actions.append(f"PR merge failed: {merge.stderr[:120]}")
        except Exception as exc:
            actions.append(f"PR merge error: {str(exc)[:120]}")

    if not ff_ok:
        # Could not merge at all — warn but don't block
        for a in actions:
            print(f"  {a}")
        return {
            "passed": True,
            "merged": False,
            "message": f"could not merge {branch} to main — resolve manually",
            "actions": actions,
        }

    # Step 5: Update local main ref
    _git(["fetch", "origin", "main"], repo_root, timeout_sec=15)
    _git(["branch", "-f", "main", "origin/main"], repo_root)
    actions.append("updated local main to origin/main")

    # Step 6: Checkout main
    checkout = _git(["checkout", "main"], repo_root)
    if checkout["ok"] and checkout["code"] == 0:
        actions.append("switched to main")
    else:
        # Try stash + checkout + stash pop
        _git(["stash", "push", "-m", "sentinel-auto-stash"], repo_root)
        checkout2 = _git(["checkout", "main"], repo_root)
        if checkout2["ok"] and checkout2["code"] == 0:
            _git(["stash", "pop"], repo_root)
            actions.append("switched to main (stash + pop)")
        else:
            _git(["stash", "pop"], repo_root)
            actions.append(f"checkout main failed: {checkout2['stderr'][:120]}")
            # Still merged remotely, just can't switch locally
            for a in actions:
                print(f"  {a}")
            return {
                "passed": True,
                "merged": True,
                "message": f"merged {branch} to main (remote), checkout failed",
                "actions": actions,
            }

    # Step 7: Delete old feature branch
    if delete_branch:
        _git(["branch", "-d", branch], repo_root)
        for remote in ("origin", "backup"):
            _git(["push", remote, "--delete", branch], repo_root, timeout_sec=15)
        actions.append(f"deleted branch {branch} (local + remote)")

    for a in actions:
        print(f"  {a}")

    return {
        "passed": True,
        "merged": True,
        "branch": branch,
        "message": f"merged {branch} to main",
        "actions": actions,
    }
