# -*- coding: utf-8 -*-
"""
WSP 78 database manager with backend abstraction.

Supported backends:
- SQLite (default)
- PostgreSQL (when DATABASE_URL starts with postgres:// or postgresql://)

Design goal:
- Keep current call pattern stable (`with db.get_connection() as conn: conn.execute(...)`)
- Allow gradual migration to PostgreSQL/pgvector without module rewrites.
"""

from __future__ import annotations

import logging
import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)


def _normalize_params(params: Sequence[Any] | Tuple[Any, ...] | None) -> Tuple[Any, ...]:
    if params is None:
        return ()
    if isinstance(params, tuple):
        return params
    if isinstance(params, list):
        return tuple(params)
    return (params,)


def _translate_qmark_sql(query: str, params: Tuple[Any, ...], backend: str) -> Tuple[str, Tuple[Any, ...]]:
    """Translate qmark placeholders to psycopg style for PostgreSQL."""
    if backend != "postgres" or not params:
        return query, params
    if "?" not in query:
        return query, params
    parts = query.split("?")
    if len(parts) - 1 != len(params):
        # Keep original query if placeholder counts don't match.
        return query, params
    return "%s".join(parts), params


class _UnifiedCursor:
    def __init__(self, raw_cursor: Any, backend: str):
        self._raw = raw_cursor
        self._backend = backend

    @property
    def rowcount(self) -> int:
        return int(getattr(self._raw, "rowcount", 0) or 0)

    def execute(self, query: str, params: Sequence[Any] | Tuple[Any, ...] | None = None) -> "_UnifiedCursor":
        q, p = _translate_qmark_sql(query, _normalize_params(params), self._backend)
        self._raw.execute(q, p)
        return self

    def fetchone(self) -> Dict[str, Any] | None:
        row = self._raw.fetchone()
        if row is None:
            return None
        return _row_to_dict(self._raw, row)

    def fetchall(self) -> List[Dict[str, Any]]:
        rows = self._raw.fetchall()
        return [_row_to_dict(self._raw, row) for row in rows]

    def close(self) -> None:
        close_fn = getattr(self._raw, "close", None)
        if callable(close_fn):
            close_fn()


def _row_to_dict(cursor: Any, row: Any) -> Dict[str, Any]:
    if isinstance(row, dict):
        return row
    if isinstance(row, sqlite3.Row):
        return dict(row)
    if hasattr(row, "keys"):
        try:
            return dict(row)
        except Exception:  # pragma: no cover - defensive
            pass
    # Tuple/list fallback from DB-API cursor.
    description = getattr(cursor, "description", None) or []
    columns = [d[0] for d in description]
    if isinstance(row, (tuple, list)) and columns:
        return dict(zip(columns, row))
    # Final fallback for unknown row object.
    return {"value": row}


class _UnifiedConnection:
    def __init__(self, raw_connection: Any, backend: str):
        self._raw = raw_connection
        self._backend = backend

    def execute(self, query: str, params: Sequence[Any] | Tuple[Any, ...] | None = None) -> _UnifiedCursor:
        p = _normalize_params(params)
        q, p = _translate_qmark_sql(query, p, self._backend)
        if self._backend == "sqlite":
            cursor = self._raw.execute(q, p)
        else:
            cursor = self._raw.cursor()
            cursor.execute(q, p)
        return _UnifiedCursor(cursor, self._backend)

    def cursor(self) -> _UnifiedCursor:
        return _UnifiedCursor(self._raw.cursor(), self._backend)

    def commit(self) -> None:
        self._raw.commit()

    def rollback(self) -> None:
        self._raw.rollback()

    def close(self) -> None:
        self._raw.close()

    def backup(self, target: Any) -> None:
        if self._backend != "sqlite":
            raise NotImplementedError("Backup API is only supported on SQLite via sqlite3 backup().")
        target_raw = getattr(target, "_raw", target)
        self._raw.backup(target_raw)


class DatabaseManager:
    """
    Unified database manager for WSP 78.

    Environment variables:
    - FOUNDUPS_DB_ENGINE: `sqlite` | `postgres` (optional)
    - FOUNDUPS_DB_PATH: SQLite file path (default: data/foundups.db)
    - DATABASE_URL: PostgreSQL DSN (required for postgres backend)
    - FOUNDUPS_ENABLE_PGVECTOR: `1` to attempt `CREATE EXTENSION vector`
    """

    _instance: Optional["DatabaseManager"] = None
    _db_path = "data/foundups.db"  # Backward-compatible default used by existing tests.
    _sqlite_busy_timeout_ms = 5000

    def __new__(cls) -> "DatabaseManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._backend = cls._instance._resolve_backend()
            cls._instance._init_db()
        return cls._instance

    @classmethod
    def reset_for_tests(cls) -> None:
        """Reset singleton to allow isolated tests with custom paths/env."""
        cls._instance = None

    def _resolve_backend(self) -> Dict[str, Any]:
        db_engine_env = os.getenv("FOUNDUPS_DB_ENGINE", "").strip().lower()
        database_url = os.getenv("DATABASE_URL", "").strip()

        if db_engine_env in {"postgres", "postgresql"}:
            engine = "postgres"
        elif db_engine_env in {"sqlite", ""}:
            engine = "postgres" if database_url.startswith(("postgres://", "postgresql://")) else "sqlite"
        else:
            raise ValueError(f"Unsupported FOUNDUPS_DB_ENGINE: {db_engine_env}")

        db_path = os.getenv("FOUNDUPS_DB_PATH", self._db_path)
        return {
            "engine": engine,
            "db_path": db_path,
            "database_url": database_url,
        }

    def _connect_raw(self) -> Any:
        if self._backend["engine"] == "sqlite":
            conn = sqlite3.connect(self._backend["db_path"])
            conn.row_factory = sqlite3.Row
            # Connection-scoped safety pragmas.
            # NOTE: foreign_keys is NOT persisted at file level in SQLite.
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute(f"PRAGMA busy_timeout={self._sqlite_busy_timeout_ms}")
            return conn

        database_url = self._backend["database_url"]
        if not database_url:
            raise RuntimeError("DATABASE_URL is required for PostgreSQL backend.")
        try:
            import psycopg
            from psycopg.rows import dict_row
        except Exception as exc:  # pragma: no cover - depends on optional dependency
            raise RuntimeError(
                "PostgreSQL backend requested but psycopg is not installed. "
                "Install with: pip install psycopg[binary]"
            ) from exc
        return psycopg.connect(database_url, autocommit=False, row_factory=dict_row)

    def _connect(self) -> _UnifiedConnection:
        return _UnifiedConnection(self._connect_raw(), self._backend["engine"])

    def _init_db(self) -> None:
        if self._backend["engine"] == "sqlite":
            os.makedirs(os.path.dirname(self._backend["db_path"]) or ".", exist_ok=True)
            with self.get_connection() as conn:
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                conn.execute("PRAGMA foreign_keys=ON")
                conn.execute("PRAGMA cache_size=-64000")
            logger.info("Database initialized (sqlite WAL) at %s", self._backend["db_path"])
            return

        with self.get_connection() as conn:
            conn.execute("SELECT 1")
            if os.getenv("FOUNDUPS_ENABLE_PGVECTOR", "0").strip().lower() in {"1", "true", "yes"}:
                try:
                    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
                    logger.info("pgvector extension ensured.")
                except Exception as exc:
                    logger.warning("Unable to enable pgvector extension automatically: %s", exc)
        logger.info("Database initialized (postgres).")

    @contextmanager
    def get_connection(self):
        conn = self._connect()
        try:
            yield conn
            conn.commit()
        except Exception as exc:
            conn.rollback()
            logger.error("Database transaction failed: %s", exc)
            raise
        finally:
            conn.close()

    def execute_query(self, query: str, params: Sequence[Any] | Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            return conn.execute(query, params).fetchall()

    def execute_write(self, query: str, params: Sequence[Any] | Tuple[Any, ...] = ()) -> int:
        with self.get_connection() as conn:
            return conn.execute(query, params).rowcount

    def table_exists(self, table_name: str) -> bool:
        if self._backend["engine"] == "sqlite":
            result = self.execute_query(
                "SELECT name FROM sqlite_master WHERE type='table' AND name = ?",
                (table_name,),
            )
            return bool(result)

        result = self.execute_query(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name = ?",
            (table_name,),
        )
        return bool(result)

    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        if self._backend["engine"] == "sqlite":
            return self.execute_query(f"PRAGMA table_info({table_name})")

        return self.execute_query(
            """
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema='public' AND table_name = ?
            ORDER BY ordinal_position
            """,
            (table_name,),
        )

    def backup_database(self, backup_path: str) -> bool:
        if self._backend["engine"] != "sqlite":
            logger.warning(
                "backup_database() is SQLite-only. Use pg_dump/managed snapshots for PostgreSQL."
            )
            return False

        try:
            source = self._connect_raw()
            os.makedirs(os.path.dirname(backup_path) or ".", exist_ok=True)
            target = sqlite3.connect(backup_path)
            source.backup(target)
            target.close()
            source.close()
            logger.info("Database backup created: %s", backup_path)
            return True
        except Exception as exc:
            logger.error("Database backup failed: %s", exc)
            return False

    def backend_info(self) -> Dict[str, Any]:
        info: Dict[str, Any] = {"engine": self._backend["engine"]}
        if self._backend["engine"] == "sqlite":
            info["db_path"] = self._backend["db_path"]
        else:
            # Do not expose credentials.
            url = self._backend.get("database_url", "")
            info["database_url_configured"] = bool(url)
            info["pgvector_enabled"] = os.getenv("FOUNDUPS_ENABLE_PGVECTOR", "0").strip().lower() in {
                "1",
                "true",
                "yes",
            }
        return info

    def get_stats(self) -> Dict[str, Any]:
        stats: Dict[str, Any] = {"backend": self.backend_info()}

        if self._backend["engine"] == "sqlite":
            tables = self.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
            for table in tables:
                table_name = table["name"]
                count = self.execute_query(f"SELECT COUNT(*) AS count FROM {table_name}")
                stats[table_name] = count[0]["count"] if count else 0
            db_path = self._backend["db_path"]
            stats["file_size_bytes"] = os.path.getsize(db_path) if os.path.exists(db_path) else 0
            return stats

        tables = self.execute_query(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
        )
        for table in tables:
            table_name = table["table_name"]
            count = self.execute_query(f"SELECT COUNT(*) AS count FROM {table_name}")
            stats[table_name] = count[0]["count"] if count else 0
        stats["file_size_bytes"] = None
        return stats
