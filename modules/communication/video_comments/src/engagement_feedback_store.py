"""
Engagement Feedback Store - WSP 60 Human Supervision Memory
===========================================================

Stores 012 (human) ratings for Studio comment engagements.

This is intentionally separate from the engagement telemetry JSON:
- Telemetry is append-only session output
- Feedback is a long-lived memory used for learning (WSP 77 Phase 3)

Data is scoped to `communication/video_comments` only (WSP 72/60).
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


MEMORY_DIR = Path(__file__).resolve().parents[1] / "memory"
DB_PATH = MEMORY_DIR / "engagement_feedback.db"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class EngagementFeedback:
    session_id: str
    comment_idx: int
    commenter_key: str
    commenter_handle: str
    commenter_channel_id: Optional[str]
    commenter_type_ai: str
    semantic_state_ai: Optional[str]
    semantic_state_human: str
    commenter_type_human: Optional[str]
    notes: Optional[str]
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "comment_idx": self.comment_idx,
            "commenter_key": self.commenter_key,
            "commenter_handle": self.commenter_handle,
            "commenter_channel_id": self.commenter_channel_id,
            "commenter_type_ai": self.commenter_type_ai,
            "semantic_state_ai": self.semantic_state_ai,
            "semantic_state_human": self.semantic_state_human,
            "commenter_type_human": self.commenter_type_human,
            "notes": self.notes,
            "created_at": self.created_at,
        }


class EngagementFeedbackStore:
    """
    SQLite store for 012/human ratings (WSP 60).

    Design goals:
    - Simple schema
    - Append-only feedback rows
    - Fast queries by session and commenter_key
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
                CREATE TABLE IF NOT EXISTS engagement_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    comment_idx INTEGER NOT NULL,
                    commenter_key TEXT NOT NULL,
                    commenter_handle TEXT,
                    commenter_channel_id TEXT,
                    commenter_type_ai TEXT,
                    semantic_state_ai TEXT,
                    semantic_state_human TEXT NOT NULL,
                    commenter_type_human TEXT,
                    notes TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_engagement_feedback_session_time
                ON engagement_feedback(session_id, created_at DESC)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_engagement_feedback_commenter_time
                ON engagement_feedback(commenter_key, created_at DESC)
                """
            )

    def record_feedback(
        self,
        *,
        session_id: str,
        comment_idx: int,
        commenter_key: str,
        commenter_handle: str,
        commenter_channel_id: Optional[str],
        commenter_type_ai: str,
        semantic_state_ai: Optional[str],
        semantic_state_human: str,
        commenter_type_human: Optional[str] = None,
        notes: Optional[str] = None,
        created_at: Optional[str] = None,
    ) -> None:
        created_at = created_at or _utc_now_iso()
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO engagement_feedback (
                    session_id,
                    comment_idx,
                    commenter_key,
                    commenter_handle,
                    commenter_channel_id,
                    commenter_type_ai,
                    semantic_state_ai,
                    semantic_state_human,
                    commenter_type_human,
                    notes,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    int(comment_idx),
                    commenter_key,
                    (commenter_handle or "")[:200],
                    commenter_channel_id,
                    (commenter_type_ai or "unknown")[:50],
                    semantic_state_ai,
                    semantic_state_human,
                    commenter_type_human,
                    (notes or "")[:2000] if notes else None,
                    created_at,
                ),
            )

    def list_feedback_for_session(self, *, session_id: str, limit: int = 200) -> List[EngagementFeedback]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT
                    session_id,
                    comment_idx,
                    commenter_key,
                    commenter_handle,
                    commenter_channel_id,
                    commenter_type_ai,
                    semantic_state_ai,
                    semantic_state_human,
                    commenter_type_human,
                    notes,
                    created_at
                FROM engagement_feedback
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (session_id, limit),
            )
            rows = cursor.fetchall()

        rows.reverse()
        return [
            EngagementFeedback(
                session_id=row[0],
                comment_idx=int(row[1] or 0),
                commenter_key=row[2] or "",
                commenter_handle=row[3] or "",
                commenter_channel_id=row[4],
                commenter_type_ai=row[5] or "unknown",
                semantic_state_ai=row[6],
                semantic_state_human=row[7] or "",
                commenter_type_human=row[8],
                notes=row[9],
                created_at=row[10] or "",
            )
            for row in rows
        ]


_store: Optional[EngagementFeedbackStore] = None


def get_engagement_feedback_store() -> EngagementFeedbackStore:
    global _store
    if _store is None:
        _store = EngagementFeedbackStore()
    return _store

