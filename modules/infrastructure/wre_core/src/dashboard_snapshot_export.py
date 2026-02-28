#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WRE Dashboard Snapshot Exporter (DB -> JSON).

DB remains source of truth. This module exports read-only JSON snapshots for:
- audits
- daily watch reports
- external sharing

Usage:
    python -m modules.infrastructure.wre_core.src.dashboard_snapshot_export
    python -m modules.infrastructure.wre_core.src.dashboard_snapshot_export --pretty
    python -m modules.infrastructure.wre_core.src.dashboard_snapshot_export --output-dir reports/wre
"""

from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from modules.infrastructure.wre_core.src.dashboard_alerts import check_dashboard_health

logger = logging.getLogger(__name__)


def _module_default_export_dir() -> Path:
    """Default export directory under the WRE module."""
    module_root = Path(__file__).resolve().parents[1]
    return module_root / "reports" / "dashboard_snapshots"


def resolve_export_dir(output_dir: Optional[str | Path] = None) -> Path:
    """Resolve export directory from arg/env/default."""
    if output_dir is None:
        import os

        env_dir = os.getenv("WRE_DASHBOARD_EXPORT_DIR", "").strip()
        if env_dir:
            output_dir = env_dir
        else:
            output_dir = _module_default_export_dir()

    out = Path(output_dir).expanduser()
    if not out.is_absolute():
        out = (Path.cwd() / out).resolve()
    return out


def prune_old_snapshots(output_dir: Path, retention_days: int) -> int:
    """Delete aged snapshot files; keep `latest.json`."""
    if retention_days < 0:
        return 0

    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    removed = 0

    for file in output_dir.glob("dashboard_snapshot_*.json"):
        try:
            mtime = datetime.fromtimestamp(file.stat().st_mtime, tz=timezone.utc)
            if mtime < cutoff:
                file.unlink(missing_ok=True)
                removed += 1
        except Exception as exc:
            logger.warning("[DASH-EXPORT] Failed to prune %s: %s", file, exc)

    return removed


def export_dashboard_snapshot(
    output_dir: Optional[str | Path] = None,
    retention_days: Optional[int] = None,
    pretty: bool = False,
    health_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Export dashboard health snapshot to timestamped JSON + latest.json.

    Args:
        output_dir: Target directory (arg/env/default resolution)
        retention_days: Snapshot retention window in days (arg/env/default)
        pretty: Pretty-print JSON output
        health_data: Optional injected payload for tests
    """
    import os

    out_dir = resolve_export_dir(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if retention_days is None:
        try:
            retention_days = int(os.getenv("WRE_DASHBOARD_EXPORT_RETENTION_DAYS", "30"))
        except (TypeError, ValueError):
            retention_days = 30
    retention_days = max(0, retention_days)

    payload = health_data if health_data is not None else check_dashboard_health()
    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    payload = {
        **payload,
        "exported_at": now.isoformat(),
        "source_of_truth": "sqlite",
    }

    snapshot_path = out_dir / f"dashboard_snapshot_{stamp}.json"
    latest_path = out_dir / "latest.json"
    dump_kwargs = {"ensure_ascii": False}
    if pretty:
        dump_kwargs["indent"] = 2

    snapshot_path.write_text(json.dumps(payload, **dump_kwargs), encoding="utf-8")
    latest_path.write_text(json.dumps(payload, **dump_kwargs), encoding="utf-8")
    removed = prune_old_snapshots(out_dir, retention_days=retention_days)

    return {
        "healthy": bool(payload.get("healthy", False)),
        "snapshot_path": str(snapshot_path),
        "latest_path": str(latest_path),
        "retention_days": retention_days,
        "pruned_files": removed,
        "exported_at": payload["exported_at"],
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export WRE dashboard health snapshot from DB to JSON.")
    parser.add_argument("--output-dir", type=str, default=None, help="Snapshot output directory.")
    parser.add_argument(
        "--retention-days",
        type=int,
        default=None,
        help="Delete timestamped snapshots older than this many days (default from env or 30).",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON files.")
    parser.add_argument("--quiet", action="store_true", help="Suppress stdout summary.")
    return parser


def main() -> int:
    parser = _build_arg_parser()
    args = parser.parse_args()

    result = export_dashboard_snapshot(
        output_dir=args.output_dir,
        retention_days=args.retention_days,
        pretty=args.pretty,
    )

    if not args.quiet:
        print(
            f"[DASH-EXPORT] healthy={result['healthy']} "
            f"snapshot={result['snapshot_path']} "
            f"pruned={result['pruned_files']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
