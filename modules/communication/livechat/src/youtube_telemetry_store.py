#!/usr/bin/env python3
"""
YouTube DAE Telemetry Storage Module

Lightweight SQLite-based telemetry ingestion for YouTube live stream monitoring.
Stores stream sessions, heartbeats, and moderation actions.

WSP References:
- WSP 72: Module Independence (standalone SQLite storage)
- WSP 78: Database Integration (agent coordination)
- WSP 91: DAEMON Observability (cardiovascular telemetry)
- WSP 22: Documentation (ModLog integration)
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime, timezone
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Default database path (shared with Vision DAE)
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent.parent.parent / "data" / "foundups.db"


class YouTubeTelemetryStore:
    """
    SQLite-based storage for YouTube DAE cardiovascular telemetry.

    Thread-safe implementation with automatic table creation and
    concurrent write support via isolation_level=None (autocommit).

    Tables:
        - youtube_streams: Stream session metadata
        - youtube_heartbeats: Periodic health pulses
        - youtube_moderation_actions: Spam/toxic blocks
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize YouTube telemetry store.

        Args:
            db_path: Path to SQLite database file (creates if missing)
        """
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_tables()

    @contextmanager
    def _get_connection(self):
        """
        Context manager for thread-safe SQLite connections.

        Uses isolation_level=None for autocommit mode to handle
        concurrent writes safely.

        Yields:
            sqlite3.Connection: Database connection
        """
        conn = sqlite3.connect(
            self.db_path,
            isolation_level=None,  # Autocommit for concurrent writes
            timeout=10.0  # Wait up to 10s for lock
        )
        try:
            yield conn
        finally:
            conn.close()

    def _ensure_tables(self):
        """
        Create YouTube DAE telemetry tables if they don't exist.

        Schema:
            youtube_streams: Stream session metadata
            youtube_heartbeats: Periodic health pulses
            youtube_moderation_actions: Spam/toxic blocks
        """
        with self._get_connection() as conn:
            # Table 1: Stream Sessions
            conn.execute("""
                CREATE TABLE IF NOT EXISTS youtube_streams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT NOT NULL,
                    channel_name TEXT NOT NULL,
                    channel_id TEXT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration_minutes INTEGER,
                    chat_messages INTEGER DEFAULT 0,
                    moderation_actions INTEGER DEFAULT 0,
                    banter_responses INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active'
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_youtube_streams_start_time
                ON youtube_streams(start_time DESC)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_youtube_streams_video_id
                ON youtube_streams(video_id)
            """)

            # Table 2: Heartbeats
            conn.execute("""
                CREATE TABLE IF NOT EXISTS youtube_heartbeats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL,
                    stream_active BOOLEAN DEFAULT 0,
                    chat_messages_per_min REAL DEFAULT 0.0,
                    moderation_actions INTEGER DEFAULT 0,
                    banter_responses INTEGER DEFAULT 0,
                    uptime_seconds REAL DEFAULT 0.0,
                    memory_mb REAL,
                    cpu_percent REAL
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_youtube_heartbeats_timestamp
                ON youtube_heartbeats(timestamp DESC)
            """)

            # Table 3: Moderation Actions
            conn.execute("""
                CREATE TABLE IF NOT EXISTS youtube_moderation_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    stream_id INTEGER,
                    author_id TEXT,
                    message_text TEXT,
                    violation_type TEXT,
                    action_taken TEXT,
                    confidence REAL DEFAULT 0.0,
                    FOREIGN KEY (stream_id) REFERENCES youtube_streams(id)
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_youtube_moderation_timestamp
                ON youtube_moderation_actions(timestamp DESC)
            """)

            logger.info("YouTube DAE telemetry tables ensured")

    def record_stream_start(
        self,
        video_id: str,
        channel_name: str,
        channel_id: Optional[str] = None
    ) -> int:
        """
        Record new stream session start.

        Args:
            video_id: YouTube video ID
            channel_name: Channel display name
            channel_id: YouTube channel ID (optional)

        Returns:
            Stream session ID
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO youtube_streams (video_id, channel_name, channel_id, start_time, status)
                VALUES (?, ?, ?, ?, 'active')
            """, (video_id, channel_name, channel_id, timestamp))

            stream_id = cursor.lastrowid
            logger.info(f"Recorded stream start: {video_id} (session {stream_id})")
            return stream_id

    def record_stream_end(self, stream_id: int):
        """
        Record stream session end.

        Args:
            stream_id: Stream session ID from record_stream_start()
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        with self._get_connection() as conn:
            # Calculate duration
            cursor = conn.execute("""
                SELECT start_time FROM youtube_streams WHERE id = ?
            """, (stream_id,))
            row = cursor.fetchone()

            if row:
                start_time = datetime.fromisoformat(row[0])
                end_time = datetime.fromisoformat(timestamp)
                duration_minutes = int((end_time - start_time).total_seconds() / 60)

                conn.execute("""
                    UPDATE youtube_streams
                    SET end_time = ?, duration_minutes = ?, status = 'ended'
                    WHERE id = ?
                """, (timestamp, duration_minutes, stream_id))

                logger.info(f"Recorded stream end: session {stream_id} ({duration_minutes} min)")

    def record_heartbeat(
        self,
        status: str,
        stream_active: bool = False,
        chat_messages_per_min: float = 0.0,
        moderation_actions: int = 0,
        banter_responses: int = 0,
        uptime_seconds: float = 0.0,
        memory_mb: Optional[float] = None,
        cpu_percent: Optional[float] = None
    ):
        """
        Record periodic heartbeat pulse.

        Args:
            status: Health status (healthy, warning, critical, offline)
            stream_active: Whether actively monitoring a stream
            chat_messages_per_min: Recent chat message rate
            moderation_actions: Moderation actions taken
            banter_responses: Banter responses sent
            uptime_seconds: DAE uptime
            memory_mb: Memory usage in MB
            cpu_percent: CPU usage percentage
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO youtube_heartbeats (
                    timestamp, status, stream_active, chat_messages_per_min,
                    moderation_actions, banter_responses, uptime_seconds,
                    memory_mb, cpu_percent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp, status, stream_active, chat_messages_per_min,
                moderation_actions, banter_responses, uptime_seconds,
                memory_mb, cpu_percent
            ))

    def record_moderation_action(
        self,
        stream_id: Optional[int],
        author_id: str,
        message_text: str,
        violation_type: str,
        action_taken: str,
        confidence: float = 0.0
    ):
        """
        Record moderation action (spam block, toxic flag, etc.).

        Args:
            stream_id: Active stream session ID (None if no stream)
            author_id: Message author ID
            message_text: Original message text
            violation_type: Type of violation (spam, toxic, caps, repetitive)
            action_taken: Action taken (block, warn, delete)
            confidence: Confidence score (0.0-1.0)
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO youtube_moderation_actions (
                    timestamp, stream_id, author_id, message_text,
                    violation_type, action_taken, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp, stream_id, author_id, message_text,
                violation_type, action_taken, confidence
            ))

    def get_recent_streams(self, limit: int = 10) -> List[Dict]:
        """
        Get recent stream sessions.

        Args:
            limit: Maximum number of streams to return

        Returns:
            List of stream session dicts
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, video_id, channel_name, channel_id, start_time, end_time,
                       duration_minutes, chat_messages, moderation_actions,
                       banter_responses, status
                FROM youtube_streams
                ORDER BY start_time DESC
                LIMIT ?
            """, (limit,))

            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_recent_heartbeats(self, limit: int = 50) -> List[Dict]:
        """
        Get recent heartbeat pulses.

        Args:
            limit: Maximum number of heartbeats to return

        Returns:
            List of heartbeat dicts
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT timestamp, status, stream_active, chat_messages_per_min,
                       moderation_actions, banter_responses, uptime_seconds,
                       memory_mb, cpu_percent
                FROM youtube_heartbeats
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))

            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]


if __name__ == "__main__":
    # Test schema creation
    print("Testing YouTube Telemetry Store...")
    store = YouTubeTelemetryStore()

    # Test stream recording
    stream_id = store.record_stream_start("test_video_123", "Test Channel")
    print(f"Created stream session: {stream_id}")

    # Test heartbeat recording
    store.record_heartbeat(
        status="healthy",
        stream_active=True,
        chat_messages_per_min=15.5,
        uptime_seconds=120.0
    )
    print("Recorded heartbeat")

    # Test moderation recording
    store.record_moderation_action(
        stream_id=stream_id,
        author_id="user123",
        message_text="SPAM MESSAGE!!!",
        violation_type="spam",
        action_taken="block",
        confidence=0.95
    )
    print("Recorded moderation action")

    # Test stream end
    store.record_stream_end(stream_id)
    print("Ended stream session")

    # Query recent data
    streams = store.get_recent_streams(limit=5)
    print(f"\nRecent streams: {len(streams)}")

    heartbeats = store.get_recent_heartbeats(limit=5)
    print(f"Recent heartbeats: {len(heartbeats)}")

    print("\nSchema test complete!")
