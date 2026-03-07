#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dependency/CVE preflight checks for startup gating."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
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


def _run(cmd: List[str], timeout_sec: int = 180, cwd: Path | None = None) -> Dict[str, Any]:
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            cwd=str(cwd) if cwd else None,
        )
        return {
            "ok": True,
            "code": int(completed.returncode),
            "stdout": completed.stdout or "",
            "stderr": completed.stderr or "",
            "cmd": cmd,
            "cwd": str(cwd) if cwd else "",
        }
    except Exception as exc:
        return {
            "ok": False,
            "code": 127,
            "stdout": "",
            "stderr": str(exc),
            "cmd": cmd,
            "cwd": str(cwd) if cwd else "",
        }


def _resolve_tool(name: str) -> str:
    """Resolve executable name in a Windows-safe way (supports .cmd wrappers)."""
    candidates = [name]
    if os.name == "nt" and "." not in name:
        candidates = [f"{name}.cmd", f"{name}.exe", f"{name}.bat", name]
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return name


def _count_pip_audit(stdout: str) -> Dict[str, int]:
    """Best-effort parse for pip-audit json payload."""
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "unknown": 0}
    try:
        payload = json.loads(stdout or "[]")
    except Exception:
        counts["unknown"] = 1
        return counts

    # pip-audit historically emitted a list; newer versions emit
    # {"dependencies":[...], "fixes":[...]}.
    deps: List[Dict[str, Any]] = []
    if isinstance(payload, list):
        deps = [item for item in payload if isinstance(item, dict)]
    elif isinstance(payload, dict):
        deps = [item for item in (payload.get("dependencies") or []) if isinstance(item, dict)]
    else:
        counts["unknown"] = 1
        return counts

    for pkg in deps:
        vulns = pkg.get("vulns", []) if isinstance(pkg, dict) else []
        for vuln in vulns:
            sev = str((vuln or {}).get("severity", "unknown")).strip().lower()
            if sev in counts:
                counts[sev] += 1
            elif sev == "moderate":
                counts["medium"] += 1
            else:
                counts["unknown"] += 1
    return counts


def _count_npm_audit(stdout: str) -> Dict[str, int]:
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "unknown": 0}
    try:
        payload = json.loads(stdout or "{}")
        vulns = ((payload or {}).get("metadata") or {}).get("vulnerabilities") or {}
        for key in ("critical", "high", "moderate", "low"):
            value = int(vulns.get(key, 0) or 0)
            if key == "moderate":
                counts["medium"] += value
            else:
                counts[key] += value
    except Exception:
        counts["unknown"] = 1
    return counts


def _count_cargo_audit(stdout: str) -> Dict[str, int]:
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "unknown": 0}
    try:
        payload = json.loads(stdout or "{}")
        vulns = ((payload or {}).get("vulnerabilities") or {}).get("list") or []
        for vuln in vulns:
            sev = str((vuln or {}).get("severity", "unknown")).strip().lower()
            if sev in counts:
                counts[sev] += 1
            elif sev == "moderate":
                counts["medium"] += 1
            else:
                counts["unknown"] += 1
    except Exception:
        counts["unknown"] = 1
    return counts


def _merge_counts(dest: Dict[str, int], source: Dict[str, int]) -> None:
    for key in ("critical", "high", "medium", "low", "unknown"):
        dest[key] = int(dest.get(key, 0)) + int(source.get(key, 0))


def _iter_node_lockfiles(repo_root: Path, scope: str) -> List[Path]:
    scope_norm = str(scope or "all").strip().lower()
    if scope_norm in {"root", "repo-root", "main"}:
        root_lock = repo_root / "package-lock.json"
        return [root_lock] if root_lock.exists() else []
    results: List[Path] = []
    for lock in repo_root.rglob("package-lock.json"):
        rel_parts = lock.relative_to(repo_root).parts
        if rel_parts and str(rel_parts[0]).startswith("."):
            # Skip hidden top-level folders (typically nested worktrees/cache dirs).
            continue
        if "node_modules" in rel_parts:
            continue
        if ".git" in rel_parts:
            continue
        if ".worktrees" in rel_parts:
            continue
        # Skip lockfiles inside nested git repositories/worktrees.
        nested_repo = False
        probe = lock.parent
        while probe != repo_root:
            if (probe / ".git").exists():
                nested_repo = True
                break
            probe = probe.parent
        if nested_repo:
            continue
        results.append(lock)
    return sorted(results)


def _cache_path(repo_root: Path) -> Path:
    return (
        repo_root
        / "modules/infrastructure/wre_core/reports/dependency_security_cache.json"
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


def run_dependency_security_preflight(repo_root: Path, force: bool = False) -> Dict[str, Any]:
    """Run Python/Node/Rust dependency security checks with TTL cache."""
    repo_root = Path(repo_root).resolve()
    runtime_24x7 = _env_bool("OPENCLAW_24X7", False)
    ttl_sec = _env_int("OPENCLAW_DEP_SECURITY_PREFLIGHT_TTL_SEC", 21600)
    require_tools = _env_bool("OPENCLAW_DEP_SECURITY_REQUIRE_TOOLS", runtime_24x7)
    max_critical = _env_int("OPENCLAW_DEP_SECURITY_MAX_CRITICAL", 0)
    max_high = _env_int("OPENCLAW_DEP_SECURITY_MAX_HIGH", 0)
    max_unknown = _env_int("OPENCLAW_DEP_SECURITY_MAX_UNKNOWN", 0)
    check_node = _env_bool("OPENCLAW_DEP_SECURITY_CHECK_NODE", True)
    check_rust = _env_bool("OPENCLAW_DEP_SECURITY_CHECK_RUST", True)
    node_lock_scope = str(os.getenv("OPENCLAW_DEP_SECURITY_NODE_LOCK_SCOPE", "all")).strip().lower()

    cache = _cache_path(repo_root)
    now = time.time()
    cached = _load_cache(cache)
    if cached and not force:
        checked_at = float(cached.get("checked_at", 0))
        if checked_at > 0 and (now - checked_at) < max(ttl_sec, 0):
            cached["cached"] = True
            return cached

    totals = {"critical": 0, "high": 0, "medium": 0, "low": 0, "unknown": 0}
    checks: List[Dict[str, Any]] = []
    tool_failures = 0

    # Python (always relevant)
    py_cmd = [sys.executable, "-m", "pip_audit", "-f", "json", "--progress-spinner", "off"]
    py_run = _run(py_cmd, timeout_sec=240)
    if not py_run["ok"]:
        tool_failures += 1
        checks.append(
            {
                "ecosystem": "python",
                "available": False,
                "passed": not require_tools,
                "message": py_run["stderr"][:240],
                "counts": {"critical": 0, "high": 0, "medium": 0, "low": 0, "unknown": 0},
            }
        )
    else:
        py_counts = _count_pip_audit(py_run.get("stdout", ""))
        _merge_counts(totals, py_counts)
        checks.append(
            {
                "ecosystem": "python",
                "available": True,
                "passed": True,
                "message": f"pip-audit exit={py_run['code']}",
                "counts": py_counts,
            }
        )

    # Node (scan selected lockfiles using package-lock-only)
    node_lockfiles = _iter_node_lockfiles(repo_root, node_lock_scope)
    if check_node and node_lockfiles:
        npm_bin = _resolve_tool("npm")
        for node_lock in node_lockfiles:
            node_run = _run(
                [npm_bin, "audit", "--json", "--package-lock-only", "--omit=dev"],
                timeout_sec=300,
                cwd=node_lock.parent,
            )
            rel_lock = str(node_lock.relative_to(repo_root)).replace("\\", "/")
            if not node_run["ok"]:
                tool_failures += 1
                checks.append(
                    {
                        "ecosystem": "node",
                        "target": rel_lock,
                        "available": False,
                        "passed": not require_tools,
                        "message": node_run["stderr"][:240],
                        "counts": {"critical": 0, "high": 0, "medium": 0, "low": 0, "unknown": 0},
                    }
                )
                continue
            node_counts = _count_npm_audit(node_run.get("stdout", ""))
            _merge_counts(totals, node_counts)
            checks.append(
                {
                    "ecosystem": "node",
                    "target": rel_lock,
                    "available": True,
                    "passed": True,
                    "message": f"npm audit exit={node_run['code']}",
                    "counts": node_counts,
                }
            )

    # Rust (only if Cargo.lock exists anywhere)
    if check_rust:
        cargo_locks = list(repo_root.glob("**/Cargo.lock"))
        if cargo_locks:
            cargo_bin = _resolve_tool("cargo")
            cargo_run = _run([cargo_bin, "audit", "--json"], timeout_sec=300)
            if not cargo_run["ok"]:
                tool_failures += 1
                checks.append(
                    {
                        "ecosystem": "rust",
                        "available": False,
                        "passed": not require_tools,
                        "message": cargo_run["stderr"][:240],
                        "counts": {"critical": 0, "high": 0, "medium": 0, "low": 0, "unknown": 0},
                    }
                )
            else:
                cargo_counts = _count_cargo_audit(cargo_run.get("stdout", ""))
                _merge_counts(totals, cargo_counts)
                checks.append(
                    {
                        "ecosystem": "rust",
                        "available": True,
                        "passed": True,
                        "message": f"cargo audit exit={cargo_run['code']}",
                        "counts": cargo_counts,
                    }
                )

    has_threshold_violation = (
        int(totals.get("critical", 0)) > max_critical
        or int(totals.get("high", 0)) > max_high
        or int(totals.get("unknown", 0)) > max_unknown
    )
    passed = (not has_threshold_violation) and (
        tool_failures == 0 or not require_tools
    )
    status = {
        "available": True,
        "passed": passed,
        "checked_at": now,
        "cached": False,
        "ttl_sec": ttl_sec,
        "require_tools": require_tools,
        "max_critical": max_critical,
        "max_high": max_high,
        "max_unknown": max_unknown,
        "node_lock_scope": node_lock_scope,
        "node_lock_count": len(node_lockfiles),
        "totals": totals,
        "tool_failures": tool_failures,
        "checks": checks,
        "message": (
            f"critical={totals['critical']} high={totals['high']} unknown={totals['unknown']} "
            f"tool_failures={tool_failures}"
        ),
    }
    _save_cache(cache, status)
    return status
