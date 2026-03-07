"""SQLite audit utility for FoundUps runtime stores.

Purpose:
- Produce repeatable health snapshots for core SQLite stores.
- Surface integrity/journal/pragma drift across SIM + FAM + DAE paths.
- Keep output JSON-friendly for CI and architecture reviews.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence


DEFAULT_AUDIT_TARGETS: tuple[Path, ...] = (
    Path("data/foundups.db"),
    Path("modules/infrastructure/database/data/foundups.db"),
    Path("modules/infrastructure/database/data/agent_db.sqlite"),
    Path("modules/foundups/agent_market/memory/fam_audit.db"),
    Path("modules/infrastructure/dae_daemon/memory/dae_audit.db"),
    Path("modules/foundups/simulator/memory/fam_audit.db"),
)


@dataclass(frozen=True)
class AuditOptions:
    max_tables: int = 20
    include_table_counts: bool = True


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _table_counts(conn: sqlite3.Connection, *, max_tables: int) -> List[Dict[str, Any]]:
    cursor = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name
        """
    )
    tables = [row[0] for row in cursor.fetchall()]

    rows: List[Dict[str, Any]] = []
    for table_name in tables[:max_tables]:
        try:
            count_row = conn.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()
            table_count = int(count_row[0]) if count_row else 0
        except Exception as exc:  # pragma: no cover - defensive fallback
            table_count = -1
            rows.append({"table": table_name, "row_count": table_count, "error": str(exc)})
            continue
        rows.append({"table": table_name, "row_count": table_count})
    if len(tables) > max_tables:
        rows.append(
            {
                "table": "__truncated__",
                "row_count": len(tables) - max_tables,
                "note": "additional tables omitted",
            }
        )
    return rows


def audit_sqlite_file(path: Path, options: AuditOptions | None = None) -> Dict[str, Any]:
    """Audit one SQLite file and return a JSON-serializable report."""
    options = options or AuditOptions()
    report: Dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
    }
    if not path.exists():
        report["status"] = "missing"
        return report

    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(str(path), timeout=5.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=5000")

        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        foreign_keys_initial = int(conn.execute("PRAGMA foreign_keys").fetchone()[0])
        conn.execute("PRAGMA foreign_keys=ON")
        foreign_keys_after_enable = int(conn.execute("PRAGMA foreign_keys").fetchone()[0])
        user_version = int(conn.execute("PRAGMA user_version").fetchone()[0])
        page_count = int(conn.execute("PRAGMA page_count").fetchone()[0])
        page_size = int(conn.execute("PRAGMA page_size").fetchone()[0])

        table_total = int(
            conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
        )

        report.update(
            {
                "status": "ok",
                "integrity": integrity,
                "journal_mode": journal_mode,
                "foreign_keys_initial": foreign_keys_initial,
                "foreign_keys_after_enable": foreign_keys_after_enable,
                "user_version": user_version,
                "page_count": page_count,
                "page_size": page_size,
                "table_count": table_total,
            }
        )
        if options.include_table_counts:
            report["tables"] = _table_counts(conn, max_tables=options.max_tables)
        return report
    except Exception as exc:
        report["status"] = "error"
        report["error"] = str(exc)
        return report
    finally:
        if conn is not None:
            conn.close()


def run_sqlite_audit(
    targets: Sequence[Path | str] | None = None,
    options: AuditOptions | None = None,
) -> Dict[str, Any]:
    """Run SQLite audit across selected targets."""
    options = options or AuditOptions()
    normalized_targets: Iterable[Path] = (
        Path(t) if not isinstance(t, Path) else t
        for t in (targets if targets is not None else DEFAULT_AUDIT_TARGETS)
    )

    reports = [audit_sqlite_file(path, options=options) for path in normalized_targets]
    existing = [r for r in reports if r.get("exists")]
    missing = [r for r in reports if not r.get("exists")]
    errors = [r for r in reports if r.get("status") == "error"]
    not_ok_integrity = [
        r for r in reports if r.get("status") == "ok" and str(r.get("integrity", "")).lower() != "ok"
    ]

    return {
        "generated_at_utc": _utc_now_iso(),
        "target_count": len(reports),
        "existing_count": len(existing),
        "missing_count": len(missing),
        "error_count": len(errors),
        "integrity_failures": len(not_ok_integrity),
        "targets": reports,
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit FoundUps SQLite stores.")
    parser.add_argument(
        "--target",
        action="append",
        default=[],
        help="SQLite path to audit (repeatable). Defaults to core runtime targets.",
    )
    parser.add_argument(
        "--max-tables",
        type=int,
        default=20,
        help="Max per-db table row-count entries to include.",
    )
    parser.add_argument(
        "--no-table-counts",
        action="store_true",
        help="Skip table row-count queries for faster audit.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="Optional file path to write JSON report.",
    )
    return parser


def main() -> int:
    parser = _build_arg_parser()
    args = parser.parse_args()

    options = AuditOptions(
        max_tables=max(1, int(args.max_tables)),
        include_table_counts=not bool(args.no_table_counts),
    )
    targets = [Path(p) for p in args.target] if args.target else None
    report = run_sqlite_audit(targets=targets, options=options)

    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["error_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
