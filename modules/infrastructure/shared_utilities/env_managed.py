"""
Managed .env loader for Foundups main entrypoints.

Purpose:
- Keep operator-owned `.env` untouched.
- Build deterministic `.env.managed` where duplicate keys are resolved (last wins).
- Preserve unknown/non-parseable lines as comments in managed output for auditability.
- Load managed env so runtime behavior is stable and predictable.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import re
import os


_TRUTHY = {"1", "true", "yes", "y", "on"}
_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _parse_env_lines(lines: List[str]) -> Tuple[Dict[str, str], List[str], List[Tuple[int, str]], Dict[str, int]]:
    """
    Parse env-style lines.

    Returns:
    - values: final key/value map (last duplicate wins)
    - order: first-seen key order (stable output grouping)
    - orphan_lines: non-parseable lines with source line number
    - duplicate_counts: key -> number of duplicate overwrites
    """
    values: Dict[str, str] = {}
    order: List[str] = []
    orphan_lines: List[Tuple[int, str]] = []
    duplicate_counts: Dict[str, int] = {}

    for line_no, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue

        candidate = stripped
        if candidate.lower().startswith("export "):
            candidate = candidate[7:].strip()

        if "=" not in candidate:
            orphan_lines.append((line_no, raw.rstrip("\n")))
            continue

        key, value = candidate.split("=", 1)
        key = key.strip()
        if not _KEY_RE.match(key):
            orphan_lines.append((line_no, raw.rstrip("\n")))
            continue

        if key in values:
            duplicate_counts[key] = duplicate_counts.get(key, 0) + 1
        else:
            order.append(key)
        values[key] = value

    return values, order, orphan_lines, duplicate_counts


def build_managed_env(source_path: Path, managed_path: Path) -> Dict[str, Any]:
    """
    Build `.env.managed` from `.env`.

    `.env` is never modified. `.env.managed` is deterministic and regenerated when needed.
    """
    text = source_path.read_text(encoding="utf-8", errors="replace")
    values, order, orphan_lines, duplicate_counts = _parse_env_lines(text.splitlines())

    generated_at = time.strftime("%Y-%m-%d %H:%M:%S")
    output_lines: List[str] = [
        "# AUTO-GENERATED FILE. DO NOT EDIT DIRECTLY.",
        f"# Source: {source_path.name}",
        f"# Generated: {generated_at}",
        "# Resolution policy: last duplicate key wins, non-parseable lines preserved as comments.",
        "",
    ]

    for key in order:
        output_lines.append(f"{key}={values[key]}")

    if orphan_lines:
        output_lines.append("")
        output_lines.append("# Orphan/non-parseable lines preserved from source:")
        for line_no, raw in orphan_lines:
            output_lines.append(f"# ORPHAN L{line_no}: {raw}")

    managed_path.write_text("\n".join(output_lines) + "\n", encoding="utf-8")

    return {
        "active_file": str(managed_path),
        "total_keys": len(values),
        "duplicate_keys": len(duplicate_counts),
        "duplicate_overwrites": sum(duplicate_counts.values()),
        "orphan_lines": len(orphan_lines),
        "duplicates": duplicate_counts,
    }


def _apply_env_values(values: Dict[str, str], order: List[str], override: bool) -> int:
    """Apply parsed key-values to process environment."""
    applied = 0
    for key in order:
        if not override and key in os.environ:
            continue
        os.environ[key] = values[key]
        applied += 1
    return applied


def load_managed_env(
    repo_root: Path,
    override: bool = False,
    regenerate: bool = True,
) -> Dict[str, Any]:
    """
    Load effective env file for runtime.

    Default policy (security-first):
    - Parse `.env` in-memory and apply resolved values directly.
    - Do NOT persist `.env.managed` copy on disk.
    - Purge stale `.env.managed` copy if present.
    """
    source_path = repo_root / ".env"
    managed_path = repo_root / ".env.managed"

    stats: Dict[str, Any] = {
        "active_file": "",
        "mode": "none",
        "total_keys": 0,
        "duplicate_keys": 0,
        "duplicate_overwrites": 0,
        "orphan_lines": 0,
        "applied_keys": 0,
        "managed_copy_written": False,
        "managed_copy_deleted": False,
    }

    if not source_path.exists():
        # Keep legacy fallback behavior if source is missing.
        if managed_path.exists():
            try:
                from dotenv import load_dotenv  # type: ignore

                load_dotenv(dotenv_path=managed_path, override=override)
                stats["active_file"] = str(managed_path)
                stats["mode"] = "managed_file_fallback"
            except Exception:
                pass
        return stats

    text = source_path.read_text(encoding="utf-8", errors="replace")
    values, order, orphan_lines, duplicate_counts = _parse_env_lines(text.splitlines())
    stats["active_file"] = str(source_path)
    stats["mode"] = "in_memory"
    stats["total_keys"] = len(values)
    stats["duplicate_keys"] = len(duplicate_counts)
    stats["duplicate_overwrites"] = sum(duplicate_counts.values())
    stats["orphan_lines"] = len(orphan_lines)
    stats["duplicates"] = duplicate_counts

    # Resolve behavior from parsed env (or shell override before parse).
    # Default: no disk copy, purge stale copy.
    write_copy_raw = os.getenv("FOUNDUPS_ENV_MANAGED_DISK_COPY", values.get("FOUNDUPS_ENV_MANAGED_DISK_COPY", "0"))
    purge_copy_raw = os.getenv("FOUNDUPS_ENV_MANAGED_PURGE_COPY", values.get("FOUNDUPS_ENV_MANAGED_PURGE_COPY", "1"))
    write_copy = str(write_copy_raw).strip().lower() in _TRUTHY
    purge_copy = str(purge_copy_raw).strip().lower() in _TRUTHY

    if write_copy and regenerate:
        build_managed_env(source_path, managed_path)
        stats["managed_copy_written"] = True
        stats["active_file"] = str(managed_path)
        stats["mode"] = "managed_file"
        try:
            from dotenv import load_dotenv  # type: ignore

            load_dotenv(dotenv_path=managed_path, override=override)
        except Exception:
            pass
    else:
        stats["applied_keys"] = _apply_env_values(values, order, override=override)
        if purge_copy and managed_path.exists():
            try:
                managed_path.unlink()
                stats["managed_copy_deleted"] = True
            except Exception:
                # Best-effort purge; keep running.
                pass

    return stats


def env_managed_enabled() -> bool:
    return str(__import__("os").environ.get("FOUNDUPS_ENV_MANAGED", "1")).strip().lower() in _TRUTHY
