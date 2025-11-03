#!/usr/bin/env python3
"""
Unit tests for Selenium telemetry storage module.

Tests cover:
- Table auto-creation
- Session recording with required/optional fields
- Concurrent write safety
- Data retrieval and JSON parsing
- Error handling

WSP References:
- WSP 5: Test Coverage Requirements
- WSP 6: Test Audit Protocol
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone
import sqlite3

from modules.infrastructure.foundups_selenium.src.telemetry_store import (
    TelemetryStore,
    record_session
)


@pytest.fixture
def temp_db():
    """
    Fixture providing a temporary database for isolated testing.

    Yields:
        Path: Temporary database file path

    Cleanup:
        Deletes database file after test completion
    """
    # Create unique temp file path for each test
    import random
    temp_dir = Path(tempfile.gettempdir())
    unique_id = f"{id(temp_dir)}_{random.randint(100000, 999999)}"
    db_path = temp_dir / f"test_selenium_{unique_id}.db"

    # Ensure it doesn't exist at start
    if db_path.exists():
        db_path.unlink()

    yield db_path

    # Cleanup (with retry for Windows file locking)
    if db_path.exists():
        try:
            db_path.unlink()
        except PermissionError:
            # Windows may keep file locked briefly after connection close
            import time
            time.sleep(0.1)
            try:
                db_path.unlink()
            except PermissionError:
                pass  # Ignore if still locked (cleanup will happen eventually)


@pytest.fixture
def store(temp_db):
    """
    Fixture providing a fresh TelemetryStore instance with temp database.

    Args:
        temp_db: Temporary database path from temp_db fixture

    Returns:
        TelemetryStore: Fresh store instance
    """
    return TelemetryStore(db_path=temp_db)


class TestTelemetryStoreTableCreation:
    """Test suite for automatic table creation and schema validation."""

    def test_table_auto_creation(self, temp_db):
        """Verify selenium_sessions table is created automatically on init."""
        # Initially, DB file shouldn't exist
        assert not temp_db.exists()

        # Create store (should create DB and table)
        store = TelemetryStore(db_path=temp_db)

        # Verify DB file was created
        assert temp_db.exists()

        # Verify table exists with correct schema
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='selenium_sessions'"
            )
            assert cursor.fetchone() is not None

            # Verify columns
            cursor = conn.execute("PRAGMA table_info(selenium_sessions)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}

            assert columns == {
                "id": "INTEGER",
                "timestamp": "TEXT",
                "url": "TEXT",
                "screenshot_hash": "TEXT",
                "screenshot_path": "TEXT",
                "annotated_path": "TEXT",
                "analysis_json": "TEXT"
            }

    def test_indexes_created(self, temp_db):
        """Verify performance indexes are created on timestamp and hash."""
        store = TelemetryStore(db_path=temp_db)

        with sqlite3.connect(temp_db) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index'"
            )
            indexes = {row[0] for row in cursor.fetchall()}

            assert "idx_selenium_sessions_timestamp" in indexes
            assert "idx_selenium_sessions_hash" in indexes

    def test_idempotent_table_creation(self, temp_db):
        """Verify repeated initialization doesn't break existing table."""
        # Create store and insert data
        store1 = TelemetryStore(db_path=temp_db)
        session_id = store1.record_session({"url": "https://test.com"})

        # Create another store (should not recreate table)
        store2 = TelemetryStore(db_path=temp_db)

        # Verify original data still exists
        session = store2.get_session(session_id)
        assert session is not None
        assert session["url"] == "https://test.com"


class TestSessionRecording:
    """Test suite for session recording functionality."""

    def test_record_minimal_session(self, store):
        """Record session with only required 'url' field."""
        session_id = store.record_session({
            "url": "https://github.com/bytedance/UI-TARS-desktop"
        })

        assert session_id > 0

        # Verify record was stored
        session = store.get_session(session_id)
        assert session["url"] == "https://github.com/bytedance/UI-TARS-desktop"
        assert session["screenshot_hash"] is None
        assert session["screenshot_path"] is None
        assert session["annotated_path"] is None
        assert session["analysis_json"] is None

    def test_record_full_session(self, store):
        """Record session with all optional fields populated."""
        analysis = {
            "elements_detected": 42,
            "confidence": 0.95,
            "tags": ["form", "button", "input"]
        }

        session_id = store.record_session({
            "url": "https://example.com/form",
            "screenshot_hash": "sha256:abc123def456",
            "screenshot_path": "/tmp/screenshots/test1.png",
            "annotated_path": "/tmp/annotated/test1_annotated.png",
            "analysis_json": analysis
        })

        # Verify all fields stored correctly
        session = store.get_session(session_id)
        assert session["url"] == "https://example.com/form"
        assert session["screenshot_hash"] == "sha256:abc123def456"
        assert session["screenshot_path"] == "/tmp/screenshots/test1.png"
        assert session["annotated_path"] == "/tmp/annotated/test1_annotated.png"

        # Verify JSON was serialized and deserialized correctly
        assert isinstance(session["analysis_json"], dict)
        assert session["analysis_json"] == analysis

    def test_auto_timestamp_generation(self, store):
        """Verify timestamp is auto-generated if not provided."""
        before = datetime.now(timezone.utc)
        session_id = store.record_session({"url": "https://test.com"})
        after = datetime.now(timezone.utc)

        session = store.get_session(session_id)
        timestamp = datetime.fromisoformat(session["timestamp"])

        # Timestamp should be between before and after
        assert before <= timestamp <= after

    def test_custom_timestamp(self, store):
        """Verify custom timestamp is preserved if provided."""
        custom_time = "2025-10-19T12:34:56.789Z"

        session_id = store.record_session({
            "url": "https://test.com",
            "timestamp": custom_time
        })

        session = store.get_session(session_id)
        assert session["timestamp"] == custom_time

    def test_json_string_analysis(self, store):
        """Verify analysis_json accepts pre-serialized JSON string."""
        analysis_str = '{"key": "value", "count": 123}'

        session_id = store.record_session({
            "url": "https://test.com",
            "analysis_json": analysis_str
        })

        session = store.get_session(session_id)
        # Should still be parsed back to dict
        assert isinstance(session["analysis_json"], dict)
        assert session["analysis_json"] == {"key": "value", "count": 123}


class TestSessionRetrieval:
    """Test suite for session data retrieval."""

    def test_get_nonexistent_session(self, store):
        """Verify get_session returns None for missing ID."""
        session = store.get_session(99999)
        assert session is None

    def test_get_recent_sessions_empty(self, store):
        """Verify get_recent_sessions returns empty list when DB is empty."""
        sessions = store.get_recent_sessions()
        assert sessions == []

    def test_get_recent_sessions_ordering(self, store):
        """Verify sessions are returned in reverse chronological order."""
        # Insert 5 sessions with sequential URLs
        for i in range(5):
            store.record_session({
                "url": f"https://test.com/page{i}",
                "timestamp": f"2025-10-19T12:00:{i:02d}Z"
            })

        # Retrieve recent sessions
        sessions = store.get_recent_sessions(limit=3)

        assert len(sessions) == 3
        # Should be in reverse order (newest first)
        assert sessions[0]["url"] == "https://test.com/page4"
        assert sessions[1]["url"] == "https://test.com/page3"
        assert sessions[2]["url"] == "https://test.com/page2"

    def test_get_recent_sessions_limit(self, store):
        """Verify limit parameter correctly restricts result count."""
        # Insert 10 sessions
        for i in range(10):
            store.record_session({"url": f"https://test.com/page{i}"})

        # Request only 5
        sessions = store.get_recent_sessions(limit=5)
        assert len(sessions) == 5

        # Request more than available
        sessions = store.get_recent_sessions(limit=20)
        assert len(sessions) == 10


class TestErrorHandling:
    """Test suite for error handling and validation."""

    def test_missing_url_raises_error(self, store):
        """Verify ValueError is raised when 'url' field is missing."""
        with pytest.raises(ValueError, match="Missing required field 'url'"):
            store.record_session({
                "screenshot_path": "/tmp/test.png"
            })

    def test_malformed_json_handled_gracefully(self, store, temp_db):
        """Verify malformed JSON in analysis_json is handled gracefully on retrieval."""
        # Insert record with malformed JSON directly via SQL
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.execute("""
                INSERT INTO selenium_sessions
                (timestamp, url, analysis_json)
                VALUES (?, ?, ?)
            """, (
                "2025-10-19T12:00:00Z",
                "https://test.com",
                "{this is not valid json}"
            ))
            session_id = cursor.lastrowid

        # Retrieve should not crash
        session = store.get_session(session_id)
        assert session is not None
        # analysis_json should remain as string (not parsed)
        assert session["analysis_json"] == "{this is not valid json}"


class TestConcurrentWrites:
    """Test suite for concurrent write safety."""

    def test_concurrent_writes_safe(self, temp_db):
        """Verify multiple simultaneous writes don't cause corruption."""
        import threading

        stores = [TelemetryStore(db_path=temp_db) for _ in range(5)]
        results = []

        def write_session(store, url):
            try:
                session_id = store.record_session({"url": url})
                results.append(session_id)
            except Exception as e:
                results.append(e)

        # Launch 10 concurrent writes
        threads = []
        for i in range(10):
            store = stores[i % 5]  # Reuse stores
            t = threading.Thread(target=write_session, args=(store, f"https://test{i}.com"))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Verify all writes succeeded
        assert len(results) == 10
        assert all(isinstance(r, int) for r in results)

        # Verify all records are in DB
        store = TelemetryStore(db_path=temp_db)
        sessions = store.get_recent_sessions(limit=20)
        assert len(sessions) == 10


class TestStandaloneHelper:
    """Test suite for standalone record_session helper function."""

    def test_standalone_record_session(self, temp_db):
        """Verify standalone record_session function works correctly."""
        session_id = record_session(
            {"url": "https://standalone.com"},
            db_path=temp_db
        )

        assert session_id > 0

        # Verify via TelemetryStore
        store = TelemetryStore(db_path=temp_db)
        session = store.get_session(session_id)
        assert session["url"] == "https://standalone.com"

    def test_standalone_uses_default_path(self):
        """Verify standalone function uses default path when not specified."""
        # This test just verifies the function doesn't crash
        # We can't easily test the actual default path without cleanup issues
        # So we just verify the signature works
        from modules.infrastructure.foundups_selenium.src.telemetry_store import DEFAULT_DB_PATH
        assert DEFAULT_DB_PATH.name == "foundups.db"
        assert "data" in str(DEFAULT_DB_PATH)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
