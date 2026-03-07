"""
Tests for Move2Japan Stakeholder Database (WSP 34)
===================================================

Covers: create, get, update, get_or_create, stats
"""

import os
import tempfile
import pytest

from modules.foundups.move2japan.src.m2j_stakeholder_db import M2JStakeholderDB


@pytest.fixture
def db():
    """Create a temporary DB for each test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_stakeholders.db")
        yield M2JStakeholderDB(db_path=db_path)


class TestM2JStakeholderDB:

    def test_create_stakeholder(self, db):
        record = db.create_stakeholder("UC_test_123", "TestUser")
        assert record["stakeholder_id"] == "UC_test_123"
        assert record["chat_handle"] == "TestUser"
        assert record["bc0_state"] == "BC0.1"
        assert record["urgency_level"] == "unknown"
        assert record["passport_status"] == "unknown"

    def test_get_stakeholder(self, db):
        db.create_stakeholder("UC_test_456", "AnotherUser")
        record = db.get_stakeholder("UC_test_456")
        assert record is not None
        assert record["chat_handle"] == "AnotherUser"

    def test_get_stakeholder_not_found(self, db):
        result = db.get_stakeholder("UC_nonexistent")
        assert result is None

    def test_update_stakeholder(self, db):
        db.create_stakeholder("UC_test_789", "UpdateMe")
        db.update_stakeholder("UC_test_789", {
            "urgency_level": "serious",
            "passport_status": "yes",
            "bc0_state": "BC0.5",
        })
        record = db.get_stakeholder("UC_test_789")
        assert record["urgency_level"] == "serious"
        assert record["passport_status"] == "yes"
        assert record["bc0_state"] == "BC0.5"

    def test_get_or_create_new(self, db):
        record = db.get_or_create("UC_new_001", "NewUser")
        assert record["stakeholder_id"] == "UC_new_001"
        assert record["chat_handle"] == "NewUser"

    def test_get_or_create_existing(self, db):
        db.create_stakeholder("UC_existing_002", "ExistingUser")
        db.update_stakeholder("UC_existing_002", {"urgency_level": "planner"})
        record = db.get_or_create("UC_existing_002", "ExistingUser")
        assert record["urgency_level"] == "planner"

    def test_get_stats(self, db):
        db.create_stakeholder("UC_s1", "User1")
        db.create_stakeholder("UC_s2", "User2")
        db.update_stakeholder("UC_s2", {"urgency_level": "serious"})
        stats = db.get_stats()
        assert stats["total_stakeholders"] == 2
        assert "unknown" in stats["by_urgency"]

    def test_duplicate_create_ignored(self, db):
        db.create_stakeholder("UC_dup", "DupUser")
        db.create_stakeholder("UC_dup", "DupUser2")  # Should be INSERT OR IGNORE
        record = db.get_stakeholder("UC_dup")
        assert record["chat_handle"] == "DupUser"  # Original preserved
