"""Regression tests for SQLite runtime pragma behavior in DatabaseManager."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from modules.infrastructure.database.src.db_manager import DatabaseManager


def _reset_manager(path: Path) -> DatabaseManager:
    DatabaseManager.reset_for_tests()
    os.environ["FOUNDUPS_DB_ENGINE"] = "sqlite"
    os.environ["FOUNDUPS_DB_PATH"] = str(path)
    os.environ.pop("DATABASE_URL", None)
    return DatabaseManager()


def test_sqlite_foreign_keys_enforced_per_connection(tmp_path: Path) -> None:
    db = _reset_manager(tmp_path / "fk_enforced.db")

    with db.get_connection() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS parent (id INTEGER PRIMARY KEY)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS child (
                id INTEGER PRIMARY KEY,
                parent_id INTEGER NOT NULL,
                FOREIGN KEY(parent_id) REFERENCES parent(id)
            )
            """
        )

    with pytest.raises(Exception):
        with db.get_connection() as conn:
            conn.execute("INSERT INTO child (id, parent_id) VALUES (?, ?)", (1, 999))


def test_sqlite_pragmas_set_on_runtime_connection(tmp_path: Path) -> None:
    db = _reset_manager(tmp_path / "pragmas.db")

    with db.get_connection() as conn:
        fk_row = conn.execute("PRAGMA foreign_keys").fetchone()
        timeout_row = conn.execute("PRAGMA busy_timeout").fetchone()

    assert fk_row is not None
    assert int(next(iter(fk_row.values()))) == 1
    assert timeout_row is not None
    assert int(next(iter(timeout_row.values()))) >= 5000


def test_backend_info_reports_sqlite_path(tmp_path: Path) -> None:
    db_path = tmp_path / "backend_info.db"
    db = _reset_manager(db_path)
    info = db.backend_info()
    assert info["engine"] == "sqlite"
    assert Path(info["db_path"]) == db_path
