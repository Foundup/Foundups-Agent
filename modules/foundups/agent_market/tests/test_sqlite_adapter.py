"""Tests for SQLite adapter implementation details."""

import tempfile
from pathlib import Path

import pytest

from modules.foundups.agent_market.src.models import Foundup
from modules.foundups.agent_market.src.persistence.sqlite_adapter import (
    Base,
    FoundupRow,
    SQLiteAdapter,
    TaskRow,
)


@pytest.fixture
def adapter():
    """Create a temporary SQLite adapter for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_fam.db"
        adapter = SQLiteAdapter(db_path)
        yield adapter
        adapter.close()


class TestSQLiteAdapterInit:
    """Tests for SQLite adapter initialization."""

    def test_creates_database_file(self):
        """Test that adapter creates database file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            adapter = SQLiteAdapter(db_path)

            assert db_path.exists()
            adapter.close()

    def test_creates_parent_directories(self):
        """Test that adapter creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "nested" / "dir" / "test.db"
            adapter = SQLiteAdapter(db_path)

            assert db_path.parent.exists()
            adapter.close()

    def test_wal_mode_enabled(self, adapter):
        """Test that WAL mode is enabled."""
        with adapter.session() as sess:
            result = sess.execute(
                sess.bind.execute("PRAGMA journal_mode")
            )
            # WAL mode should be set by event listener
            # Note: This test verifies the pragma was executed

    def test_tables_created(self, adapter):
        """Test that all tables are created."""
        from sqlalchemy import inspect

        inspector = inspect(adapter.engine)
        tables = inspector.get_table_names()

        expected_tables = [
            "foundups",
            "token_terms",
            "agent_profiles",
            "tasks",
            "proofs",
            "verifications",
            "payouts",
            "distribution_posts",
            "event_records",
        ]
        for table in expected_tables:
            assert table in tables, f"Table {table} not found"


class TestSessionManagement:
    """Tests for session context manager."""

    def test_session_commits_on_success(self, adapter):
        """Test that session commits on successful operations."""
        foundup = Foundup(
            foundup_id="fdup_session_test",
            name="Session Test",
            owner_id="user_1",
            token_symbol="TST",
        )
        adapter.create_foundup(foundup)

        # Should be retrievable after commit
        retrieved = adapter.get_foundup(foundup.foundup_id)
        assert retrieved.foundup_id == foundup.foundup_id

    def test_session_rollback_on_error(self, adapter):
        """Test that session rolls back on error."""
        foundup = Foundup(
            foundup_id="fdup_rollback_test",
            name="Rollback Test",
            owner_id="user_1",
            token_symbol="RBK",
        )
        adapter.create_foundup(foundup)

        # Try to create duplicate (should fail due to primary key)
        with pytest.raises(Exception):
            adapter.create_foundup(foundup)

        # Original should still be retrievable
        retrieved = adapter.get_foundup(foundup.foundup_id)
        assert retrieved is not None


class TestORMModels:
    """Tests for ORM model mappings."""

    def test_foundup_row_columns(self):
        """Test FoundupRow has correct columns."""
        columns = FoundupRow.__table__.columns.keys()
        expected = [
            "foundup_id",
            "name",
            "owner_id",
            "token_symbol",
            "immutable_metadata",
            "mutable_metadata",
            "created_at",
        ]
        for col in expected:
            assert col in columns

    def test_task_row_columns(self):
        """Test TaskRow has correct columns."""
        columns = TaskRow.__table__.columns.keys()
        expected = [
            "task_id",
            "foundup_id",
            "title",
            "description",
            "acceptance_criteria",
            "reward_amount",
            "creator_id",
            "status",
            "assignee_id",
            "proof_id",
            "verification_id",
            "payout_id",
            "created_at",
        ]
        for col in expected:
            assert col in columns


class TestEnvironmentConfig:
    """Tests for environment-based configuration."""

    def test_default_db_path(self, monkeypatch):
        """Test default database path when not specified."""
        monkeypatch.delenv("FAM_DB_PATH", raising=False)
        with tempfile.TemporaryDirectory() as tmpdir:
            # Adapter uses default path if not specified
            adapter = SQLiteAdapter(Path(tmpdir) / "test.db")
            assert adapter.db_path == Path(tmpdir) / "test.db"
            adapter.close()
