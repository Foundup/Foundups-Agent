"""
Video Index Metadata DB - SQLite catalog for indexed video artifacts.

Stores per-video metadata for auditability and fast listing without
parsing all JSON artifacts. This complements JSON storage (not replacing it).
"""

from __future__ import annotations

import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path("memory/video_index/metadata.sqlite3")


@contextmanager
def _connect(db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        yield conn
    finally:
        conn.close()


def _init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS video_index_metadata (
            video_id TEXT PRIMARY KEY,
            channel TEXT,
            title TEXT,
            duration REAL,
            indexed_at TEXT,
            indexer TEXT,
            model TEXT,
            topics_json TEXT,
            speakers_json TEXT,
            key_points_json TEXT,
            source_path TEXT,
            updated_at TEXT
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_video_index_channel ON video_index_metadata(channel)")
    conn.commit()


def _json_dump(value: Any) -> Optional[str]:
    if value is None:
        return None
    try:
        return json.dumps(value, ensure_ascii=False)
    except Exception:
        return None


def upsert_metadata(record: Dict[str, Any], db_path: Path = DEFAULT_DB_PATH) -> None:
    """Insert or update a metadata record."""
    with _connect(db_path) as conn:
        _init_db(conn)
        conn.execute(
            """
            INSERT INTO video_index_metadata (
                video_id, channel, title, duration, indexed_at, indexer, model,
                topics_json, speakers_json, key_points_json, source_path, updated_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(video_id) DO UPDATE SET
                channel=excluded.channel,
                title=excluded.title,
                duration=excluded.duration,
                indexed_at=excluded.indexed_at,
                indexer=excluded.indexer,
                model=excluded.model,
                topics_json=excluded.topics_json,
                speakers_json=excluded.speakers_json,
                key_points_json=excluded.key_points_json,
                source_path=excluded.source_path,
                updated_at=excluded.updated_at
            """,
            (
                record.get("video_id"),
                record.get("channel"),
                record.get("title"),
                record.get("duration"),
                record.get("indexed_at"),
                record.get("indexer"),
                record.get("model"),
                record.get("topics_json"),
                record.get("speakers_json"),
                record.get("key_points_json"),
                record.get("source_path"),
                record.get("updated_at"),
            ),
        )
        conn.commit()


def safe_upsert_from_index_data(
    index_data: Dict[str, Any],
    source_path: Optional[str] = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    """Safely upsert metadata from an index_data dict."""
    try:
        meta = index_data.get("metadata", {}) if isinstance(index_data, dict) else {}
        record = {
            "video_id": index_data.get("video_id"),
            "channel": index_data.get("channel"),
            "title": index_data.get("title"),
            "duration": index_data.get("duration"),
            "indexed_at": index_data.get("indexed_at"),
            "indexer": index_data.get("indexer") or "unknown",
            "model": index_data.get("model") or meta.get("model"),
            "topics_json": _json_dump(meta.get("topics")),
            "speakers_json": _json_dump(meta.get("speakers")),
            "key_points_json": _json_dump(meta.get("key_points")),
            "source_path": source_path,
            "updated_at": datetime.now().isoformat(),
        }
        if record["video_id"]:
            upsert_metadata(record, db_path=db_path)
    except Exception as exc:
        logger.warning(f"[VIDEO-INDEX-META] Upsert failed: {exc}")


def safe_upsert_from_gemini_result(
    result: Any,
    channel: str,
    source_path: Optional[str] = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> None:
    """Safely upsert metadata from GeminiAnalysisResult."""
    try:
        record = {
            "video_id": getattr(result, "video_id", None),
            "channel": channel,
            "title": getattr(result, "title", ""),
            "duration": getattr(result, "duration", None),
            "indexed_at": getattr(result, "analyzed_at", None).isoformat()
            if getattr(result, "analyzed_at", None) else None,
            "indexer": "gemini",
            "model": getattr(result, "model_used", None),
            "topics_json": _json_dump(getattr(result, "topics", None)),
            "speakers_json": _json_dump(getattr(result, "speakers", None)),
            "key_points_json": _json_dump(getattr(result, "key_points", None)),
            "source_path": source_path,
            "updated_at": datetime.now().isoformat(),
        }
        if record["video_id"]:
            upsert_metadata(record, db_path=db_path)
    except Exception as exc:
        logger.warning(f"[VIDEO-INDEX-META] Gemini upsert failed: {exc}")
