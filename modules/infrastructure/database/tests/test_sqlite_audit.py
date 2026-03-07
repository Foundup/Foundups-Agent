"""Tests for SQLite audit utility."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from modules.infrastructure.database.src.sqlite_audit import (
    AuditOptions,
    audit_sqlite_file,
    run_sqlite_audit,
)


def _create_test_db(path: Path) -> None:
    conn = sqlite3.connect(str(path))
    conn.execute("CREATE TABLE demo (id INTEGER PRIMARY KEY, value TEXT)")
    conn.execute("INSERT INTO demo (value) VALUES ('a'), ('b')")
    conn.commit()
    conn.close()


def test_audit_sqlite_file_ok(tmp_path: Path) -> None:
    db_path = tmp_path / "demo.db"
    _create_test_db(db_path)

    report = audit_sqlite_file(db_path, options=AuditOptions(max_tables=5))
    assert report["exists"] is True
    assert report["status"] == "ok"
    assert str(report["integrity"]).lower() == "ok"
    assert report["table_count"] >= 1
    assert any(t["table"] == "demo" for t in report.get("tables", []))


def test_run_sqlite_audit_counts_missing(tmp_path: Path) -> None:
    db_path = tmp_path / "demo.db"
    missing_path = tmp_path / "missing.db"
    _create_test_db(db_path)

    summary = run_sqlite_audit(
        targets=[db_path, missing_path],
        options=AuditOptions(max_tables=3, include_table_counts=False),
    )
    assert summary["target_count"] == 2
    assert summary["existing_count"] == 1
    assert summary["missing_count"] == 1
    assert summary["error_count"] == 0
