#!/usr/bin/env python3
"""
Selenium Telemetry Storage Module

Lightweight SQLite-based telemetry ingestion for Selenium browser sessions.
Stores screenshots, URLs, annotations, and analysis JSON for VisionDAE processing.

WSP References:
- WSP 72: Module Independence (standalone SQLite storage)
- WSP 22: Documentation (ModLog integration)
- WSP 50: Pre-Action Verification (safe table creation)
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timezone
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Default database path (relative to project root)
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent.parent.parent / "data" / "foundups.db"


class TelemetryStore:
    """
    SQLite-based storage for Selenium browser telemetry sessions.

    Thread-safe implementation with automatic table creation and
    concurrent write support via isolation_level=None (autocommit).
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize telemetry store with database path.

        Args:
            db_path: Path to SQLite database file (creates if missing)
        """
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_table()

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

    def _ensure_table(self):
        """
        Create selenium_sessions table if it doesn't exist.

        Schema:
            id: INTEGER PRIMARY KEY AUTOINCREMENT
            timestamp: TEXT - ISO8601 UTC timestamp
            url: TEXT - Page URL being browsed
            screenshot_hash: TEXT - SHA256 of screenshot (deduplication)
            screenshot_path: TEXT - Absolute path to raw screenshot
            annotated_path: TEXT - Path to Gemini-annotated screenshot
            analysis_json: TEXT - Raw JSON dump of Gemini Vision analysis
        """
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS selenium_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    url TEXT NOT NULL,
                    screenshot_hash TEXT,
                    screenshot_path TEXT,
                    annotated_path TEXT,
                    analysis_json TEXT
                )
            """)

            # Create index on timestamp for efficient time-based queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_selenium_sessions_timestamp
                ON selenium_sessions(timestamp DESC)
            """)

            # Create index on screenshot_hash for deduplication
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_selenium_sessions_hash
                ON selenium_sessions(screenshot_hash)
            """)

            logger.debug(f"Ensured selenium_sessions table exists in {self.db_path}")

    def record_session(self, entry: Dict) -> int:
        """
        Record a Selenium telemetry session entry.

        Args:
            entry: Dictionary containing session data with keys:
                - url (required): str - Page URL
                - screenshot_hash (optional): str - Screenshot SHA256
                - screenshot_path (optional): str - Path to screenshot
                - annotated_path (optional): str - Path to annotated image
                - analysis_json (optional): dict - Gemini analysis results
                - timestamp (optional): str - ISO8601 UTC (auto-generated if missing)

        Returns:
            int: Row ID of inserted session

        Raises:
            ValueError: If required 'url' field is missing
            sqlite3.Error: On database errors

        Example:
            >>> store = TelemetryStore()
            >>> row_id = store.record_session({
            ...     "url": "https://example.com",
            ...     "screenshot_hash": "abc123...",
            ...     "screenshot_path": "/path/to/screenshot.png",
            ...     "analysis_json": {"elements": [...]}
            ... })
        """
        # Validate required fields
        if "url" not in entry:
            raise ValueError("Missing required field 'url' in session entry")

        # Auto-generate timestamp if not provided
        timestamp = entry.get("timestamp")
        if not timestamp:
            timestamp = datetime.now(timezone.utc).isoformat()

        # Serialize analysis_json to JSON string if dict provided
        analysis_json = entry.get("analysis_json")
        if isinstance(analysis_json, dict):
            analysis_json = json.dumps(analysis_json)

        # Insert session record
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO selenium_sessions
                (timestamp, url, screenshot_hash, screenshot_path, annotated_path, analysis_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                entry["url"],
                entry.get("screenshot_hash"),
                entry.get("screenshot_path"),
                entry.get("annotated_path"),
                analysis_json
            ))

            row_id = cursor.lastrowid
            logger.info(f"Recorded session {row_id}: {entry['url']}")
            return row_id

    def get_session(self, session_id: int) -> Optional[Dict]:
        """
        Retrieve a session by ID.

        Args:
            session_id: Row ID of session

        Returns:
            Dict with session data or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM selenium_sessions WHERE id = ?",
                (session_id,)
            )
            row = cursor.fetchone()

            if not row:
                return None

            columns = [desc[0] for desc in cursor.description]
            session = dict(zip(columns, row))

            # Parse analysis_json back to dict
            if session.get("analysis_json"):
                try:
                    session["analysis_json"] = json.loads(session["analysis_json"])
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse analysis_json for session {session_id}")

            return session

    def get_recent_sessions(self, limit: int = 10) -> list[Dict]:
        """
        Retrieve recent sessions ordered by timestamp.

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of session dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM selenium_sessions ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )

            columns = [desc[0] for desc in cursor.description]
            sessions = []

            for row in cursor.fetchall():
                session = dict(zip(columns, row))

                # Parse analysis_json back to dict
                if session.get("analysis_json"):
                    try:
                        session["analysis_json"] = json.loads(session["analysis_json"])
                    except json.JSONDecodeError:
                        pass

                sessions.append(session)

            return sessions


# Standalone helper function for simple usage
def record_session(entry: Dict, db_path: Optional[Path] = None) -> int:
    """
    Convenience function to record a session without instantiating TelemetryStore.

    Args:
        entry: Session data dictionary (see TelemetryStore.record_session)
        db_path: Optional custom database path

    Returns:
        int: Row ID of inserted session

    Example:
        >>> from modules.infrastructure.foundups_selenium.src.telemetry_store import record_session
        >>> record_session({
        ...     "url": "https://example.com",
        ...     "screenshot_path": "/tmp/screenshot.png"
        ... })
    """
    store = TelemetryStore(db_path)
    return store.record_session(entry)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.DEBUG)

    store = TelemetryStore()

    # Record a test session
    session_id = store.record_session({
        "url": "https://github.com/bytedance/UI-TARS-desktop",
        "screenshot_hash": "abc123def456",
        "screenshot_path": "/tmp/test_screenshot.png",
        "analysis_json": {
            "elements_detected": 42,
            "confidence": 0.95
        }
    })

    print(f"Recorded session ID: {session_id}")

    # Retrieve it back
    session = store.get_session(session_id)
    print(f"Retrieved session: {session}")

    # Get recent sessions
    recent = store.get_recent_sessions(limit=5)
    print(f"Recent sessions count: {len(recent)}")
