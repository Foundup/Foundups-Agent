"""
Move2Japan Stakeholder Database (WSP 60 / WSP 78 Tier 2)
=========================================================

SQLite persistence for M2J stakeholder state across sessions.
Lives inside the FoundUp module memory directory.

DB: modules/foundups/move2japan/memory/m2j_stakeholders.db
"""

from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Default DB path inside the FoundUp module
_DEFAULT_DB_DIR = os.path.join(
    os.path.dirname(__file__), "..", "memory"
)
_DEFAULT_DB_PATH = os.path.join(_DEFAULT_DB_DIR, "m2j_stakeholders.db")


_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS m2j_stakeholders (
    stakeholder_id  TEXT PRIMARY KEY,
    chat_handle     TEXT,
    urgency_level   TEXT DEFAULT 'unknown',
    passport_status TEXT DEFAULT 'unknown',
    current_stage   TEXT DEFAULT 'BC0',
    timeline_estimate TEXT DEFAULT 'unknown',
    intent_source   TEXT DEFAULT 'youtube_chat',
    bc0_state       TEXT DEFAULT 'BC0.1',
    move_reason     TEXT DEFAULT '',
    language_level  TEXT DEFAULT '',
    target_region   TEXT DEFAULT '',
    first_seen      TEXT,
    last_seen       TEXT,
    notes           TEXT DEFAULT ''
);
"""


class M2JStakeholderDB:
    """SQLite-backed stakeholder memory for Move2Japan FoundUp."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or _DEFAULT_DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _init_db(self) -> None:
        """Create table if not exists."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(_CREATE_TABLE_SQL)
                conn.commit()
            logger.info(f"[M2J-DB] Stakeholder DB ready: {self.db_path}")
        except Exception as exc:
            logger.error(f"[M2J-DB] Failed to init DB: {exc}")

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_stakeholder(self, stakeholder_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve stakeholder by ID (YouTube channel ID). Returns None if not found."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                row = conn.execute(
                    "SELECT * FROM m2j_stakeholders WHERE stakeholder_id = ?",
                    (stakeholder_id,),
                ).fetchone()
                if row:
                    return dict(row)
        except Exception as exc:
            logger.error(f"[M2J-DB] get_stakeholder error: {exc}")
        return None

    def create_stakeholder(
        self,
        stakeholder_id: str,
        chat_handle: str = "",
        intent_source: str = "youtube_chat",
    ) -> Dict[str, Any]:
        """Create a new stakeholder record. Returns the created record."""
        now = self._now_iso()
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT OR IGNORE INTO m2j_stakeholders
                       (stakeholder_id, chat_handle, intent_source, first_seen, last_seen)
                       VALUES (?, ?, ?, ?, ?)""",
                    (stakeholder_id, chat_handle, intent_source, now, now),
                )
                conn.commit()
            logger.info(f"[M2J-DB] Created stakeholder: {chat_handle} ({stakeholder_id})")
        except Exception as exc:
            logger.error(f"[M2J-DB] create_stakeholder error: {exc}")
        return self.get_stakeholder(stakeholder_id) or {
            "stakeholder_id": stakeholder_id,
            "chat_handle": chat_handle,
        }

    def update_stakeholder(
        self, stakeholder_id: str, updates: Dict[str, Any]
    ) -> None:
        """Update specific fields for a stakeholder."""
        if not updates:
            return
        # Always bump last_seen
        updates["last_seen"] = self._now_iso()
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [stakeholder_id]
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    f"UPDATE m2j_stakeholders SET {set_clause} WHERE stakeholder_id = ?",
                    values,
                )
                conn.commit()
            logger.debug(f"[M2J-DB] Updated stakeholder {stakeholder_id}: {list(updates.keys())}")
        except Exception as exc:
            logger.error(f"[M2J-DB] update_stakeholder error: {exc}")

    def get_or_create(
        self,
        stakeholder_id: str,
        chat_handle: str = "",
        intent_source: str = "youtube_chat",
    ) -> Dict[str, Any]:
        """Get existing stakeholder or create new one. Updates last_seen either way."""
        existing = self.get_stakeholder(stakeholder_id)
        if existing:
            self.update_stakeholder(stakeholder_id, {"last_seen": self._now_iso()})
            # Refresh after update
            return self.get_stakeholder(stakeholder_id) or existing
        return self.create_stakeholder(stakeholder_id, chat_handle, intent_source)

    def get_stats(self) -> Dict[str, Any]:
        """Get aggregate stats for analytics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                total = conn.execute("SELECT COUNT(*) FROM m2j_stakeholders").fetchone()[0]
                by_stage = {}
                for row in conn.execute(
                    "SELECT current_stage, COUNT(*) FROM m2j_stakeholders GROUP BY current_stage"
                ):
                    by_stage[row[0]] = row[1]
                by_urgency = {}
                for row in conn.execute(
                    "SELECT urgency_level, COUNT(*) FROM m2j_stakeholders GROUP BY urgency_level"
                ):
                    by_urgency[row[0]] = row[1]
                return {
                    "total_stakeholders": total,
                    "by_stage": by_stage,
                    "by_urgency": by_urgency,
                }
        except Exception as exc:
            logger.error(f"[M2J-DB] get_stats error: {exc}")
            return {"total_stakeholders": 0}
