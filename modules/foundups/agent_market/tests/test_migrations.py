"""Tests for persistence schema migrations."""

import tempfile
from pathlib import Path

import pytest
from sqlalchemy import inspect

from modules.foundups.agent_market.src.exceptions import ValidationError
from modules.foundups.agent_market.src.persistence import LATEST_SCHEMA_VERSION, MigrationManager, SQLiteAdapter


def _make_adapter():
    tmpdir = tempfile.TemporaryDirectory()
    db_path = Path(tmpdir.name) / "migrations.db"
    adapter = SQLiteAdapter(db_path)
    return tmpdir, adapter


class TestMigrationManager:
    def test_default_schema_version_applied(self):
        tmpdir, adapter = _make_adapter()
        try:
            manager = MigrationManager(adapter.engine)
            assert manager.get_current_version() == LATEST_SCHEMA_VERSION
            applied = manager.list_applied_versions()
            assert applied[-1] == LATEST_SCHEMA_VERSION
            assert applied == sorted(applied)
        finally:
            adapter.close()
            tmpdir.cleanup()

    def test_migrations_are_idempotent(self):
        tmpdir, adapter = _make_adapter()
        try:
            manager = MigrationManager(adapter.engine)
            manager.migrate()
            manager.migrate()
            applied = manager.list_applied_versions()
            assert applied[-1] == LATEST_SCHEMA_VERSION
            assert applied == sorted(set(applied))
        finally:
            adapter.close()
            tmpdir.cleanup()

    def test_rejects_target_behind_current(self):
        tmpdir, adapter = _make_adapter()
        try:
            manager = MigrationManager(adapter.engine)
            with pytest.raises(ValidationError):
                manager.migrate(target_version=0)
        finally:
            adapter.close()
            tmpdir.cleanup()

    def test_expected_indexes_exist(self):
        tmpdir, adapter = _make_adapter()
        try:
            inspector = inspect(adapter.engine)
            tasks_indexes = {idx["name"] for idx in inspector.get_indexes("tasks")}
            events_indexes = {idx["name"] for idx in inspector.get_indexes("event_records")}
            ledger_indexes = {idx["name"] for idx in inspector.get_indexes("compute_ledger_entries")}
            assert "idx_tasks_foundup_status" in tasks_indexes
            assert "idx_events_foundup_timestamp" in events_indexes
            assert "idx_compute_ledger_actor_created" in ledger_indexes
        finally:
            adapter.close()
            tmpdir.cleanup()
