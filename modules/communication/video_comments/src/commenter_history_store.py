"""
Commenter History Store - WSP 60 Module Memory for Studio Engagement
====================================================================

Stores per-commenter interaction history for YouTube Studio comment engagement.
This provides contextual memory for intelligent replies (Grok/LM Studio) and
supports later Gemma/Qwen routing (WSP 77 / WSP 96).

Data stored here is *local* and scoped to the `communication/video_comments` module.
It is not intended for cross-service use without explicit integration.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MEMORY_DIR = Path(__file__).resolve().parents[1] / "memory"
DB_PATH = MEMORY_DIR / "commenter_history.db"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_handle(handle: Optional[str]) -> str:
    if not handle:
        return ""
    handle = handle.strip()
    if handle.startswith("@"):
        handle = handle[1:]
    return " ".join(handle.split())


def make_commenter_key(*, channel_id: Optional[str], handle: Optional[str]) -> str:
    """
    Stable commenter key for lookups.

    Preference order:
    1) YouTube channel id (best stability)
    2) normalized handle (lowercased)
    3) "unknown"
    """
    if channel_id:
        return channel_id.strip()
    normalized = _normalize_handle(handle)
    if normalized:
        return normalized.lower()
    return "unknown"


@dataclass(frozen=True)
class CommenterInteraction:
    commenter_key: str
    commenter_handle: str
    commenter_channel_id: Optional[str]
    comment_text: str
    reply_text: Optional[str]
    liked: bool
    hearted: bool
    replied: bool
    commenter_type: str
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "commenter_key": self.commenter_key,
            "commenter_handle": self.commenter_handle,
            "commenter_channel_id": self.commenter_channel_id,
            "comment_text": self.comment_text,
            "reply_text": self.reply_text,
            "liked": self.liked,
            "hearted": self.hearted,
            "replied": self.replied,
            "commenter_type": self.commenter_type,
            "created_at": self.created_at,
        }


class CommenterHistoryStore:
    """
    SQLite store for per-commenter history (WSP 60).

    Design goals (PoC):
    - Small schema
    - Append-only interactions
    - Fast retrieval of last N interactions per commenter
    """

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, isolation_level=None, timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def _ensure_schema(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS commenter_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    commenter_key TEXT NOT NULL,
                    commenter_handle TEXT,
                    commenter_channel_id TEXT,
                    comment_text TEXT,
                    reply_text TEXT,
                    liked INTEGER NOT NULL,
                    hearted INTEGER NOT NULL,
                    replied INTEGER NOT NULL,
                    commenter_type TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_commenter_interactions_key_time
                ON commenter_interactions(commenter_key, created_at DESC)
                """
            )

    def record_interaction(
        self,
        *,
        commenter_handle: Optional[str],
        commenter_channel_id: Optional[str],
        comment_text: str,
        reply_text: Optional[str],
        liked: bool,
        hearted: bool,
        replied: bool,
        commenter_type: Optional[str],
        created_at: Optional[str] = None,
    ) -> None:
        commenter_key = make_commenter_key(channel_id=commenter_channel_id, handle=commenter_handle)
        created_at = created_at or _utc_now_iso()
        handle_normalized = _normalize_handle(commenter_handle)

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO commenter_interactions (
                    commenter_key,
                    commenter_handle,
                    commenter_channel_id,
                    comment_text,
                    reply_text,
                    liked,
                    hearted,
                    replied,
                    commenter_type,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    commenter_key,
                    handle_normalized,
                    commenter_channel_id,
                    (comment_text or "")[:1000],
                    (reply_text or "")[:1000] if reply_text else None,
                    1 if liked else 0,
                    1 if hearted else 0,
                    1 if replied else 0,
                    commenter_type or "unknown",
                    created_at,
                ),
            )

    def get_recent_interactions(self, *, commenter_key: str, limit: int = 5) -> List[CommenterInteraction]:
        if not commenter_key:
            return []

        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT
                    commenter_key,
                    commenter_handle,
                    commenter_channel_id,
                    comment_text,
                    reply_text,
                    liked,
                    hearted,
                    replied,
                    commenter_type,
                    created_at
                FROM commenter_interactions
                WHERE commenter_key = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (commenter_key, limit),
            )
            rows = cursor.fetchall()

        # Oldest-to-newest for prompt readability
        rows.reverse()
        return [
            CommenterInteraction(
                commenter_key=row[0],
                commenter_handle=row[1] or "",
                commenter_channel_id=row[2],
                comment_text=row[3] or "",
                reply_text=row[4],
                liked=bool(row[5]),
                hearted=bool(row[6]),
                replied=bool(row[7]),
                commenter_type=row[8] or "unknown",
                created_at=row[9],
            )
            for row in rows
        ]

    def get_profile_summary(self, *, commenter_key: str) -> Dict[str, Any]:
        if not commenter_key:
            return {"commenter_key": commenter_key, "total": 0}

        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    SUM(replied) AS replies,
                    SUM(liked) AS likes,
                    SUM(hearted) AS hearts,
                    MAX(created_at) AS last_seen
                FROM commenter_interactions
                WHERE commenter_key = ?
                """,
                (commenter_key,),
            )
            row = cursor.fetchone()

        return {
            "commenter_key": commenter_key,
            "total": int(row[0] or 0),
            "replies": int(row[1] or 0),
            "likes": int(row[2] or 0),
            "hearts": int(row[3] or 0),
            "last_seen": row[4],
        }


_store: Optional[CommenterHistoryStore] = None


def get_commenter_history_store() -> CommenterHistoryStore:
    global _store
    if _store is None:
        _store = CommenterHistoryStore()
    return _store

