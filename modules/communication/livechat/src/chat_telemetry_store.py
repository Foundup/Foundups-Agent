#!/usr/bin/env python3
"""
Chat Telemetry Store
--------------------

SQLite-backed storage for live chat messages. Consolidates the previous
per-user JSONL/text files into a single transaction-safe database.

WSP References:
    - WSP 72: Module Independence (uses local SQLite)
    - WSP 77: Agent Coordination (backing storage for skill metrics)
    - WSP 22: Documentation (ModLog entries reference this store)
"""

from __future__ import annotations

import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


PROJECT_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "foundups.db"


class ChatTelemetryStore:
    """Thin wrapper around SQLite for chat message persistence."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(
            self.db_path,
            isolation_level=None,  # autocommit for concurrent writers
            timeout=10.0,
        )
        try:
            yield conn
        finally:
            conn.close()

    def _ensure_schema(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    author_name TEXT NOT NULL,
                    author_id TEXT,
                    youtube_name TEXT,
                    role TEXT,
                    message_text TEXT NOT NULL,
                    importance_score REAL,
                    persisted_at TEXT NOT NULL,
                    metadata_json TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_chat_messages_author
                ON chat_messages(author_name COLLATE NOCASE)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp
                ON chat_messages(persisted_at DESC)
                """
            )

    def record_message(
        self,
        *,
        session_id: Optional[str],
        author_name: str,
        author_id: Optional[str],
        youtube_name: Optional[str],
        role: str,
        message_text: str,
        importance_score: Optional[float],
        metadata: Optional[Dict[str, str]] = None,
    ) -> int:
        timestamp = datetime.now(timezone.utc).isoformat()
        payload = json.dumps(metadata or {}, ensure_ascii=False)

        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO chat_messages (
                    session_id,
                    author_name,
                    author_id,
                    youtube_name,
                    role,
                    message_text,
                    importance_score,
                    persisted_at,
                    metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    author_name,
                    author_id,
                    youtube_name,
                    role,
                    message_text,
                    importance_score,
                    timestamp,
                    payload,
                ),
            )
            row_id = cursor.lastrowid
            logger.debug(
                "[CHAT-STORE] Recorded message id=%s author=%s", row_id, author_name
            )
            return row_id

    def get_recent_messages(self, author_name: str, limit: int) -> List[Dict[str, str]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT message_text, role, persisted_at
                FROM chat_messages
                WHERE author_name = ?
                ORDER BY persisted_at DESC
                LIMIT ?
                """,
                (author_name, limit),
            )
            rows = cursor.fetchall()

        # Return oldest-to-newest order for history reconstruction
        rows.reverse()
        return [
            {
                "text": message,
                "role": role or "USER",
                "persisted_at": persisted_at,
            }
            for message, role, persisted_at in rows
        ]

    def has_history(self, author_name: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT 1 FROM chat_messages WHERE author_name = ? LIMIT 1",
                (author_name,),
            )
            return cursor.fetchone() is not None

    def distinct_author_count(self) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(DISTINCT author_name) FROM chat_messages"
            )
            row = cursor.fetchone()
            return row[0] if row else 0
