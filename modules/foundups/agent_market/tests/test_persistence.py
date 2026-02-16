"""Tests for SQLite persistence adapter."""

import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from modules.foundups.agent_market.src.exceptions import NotFoundError, ValidationError
from modules.foundups.agent_market.src.models import (
    EventRecord,
    Foundup,
    Payout,
    PayoutStatus,
    Proof,
    Task,
    TaskStatus,
    Verification,
)
from modules.foundups.agent_market.src.persistence.sqlite_adapter import SQLiteAdapter


@pytest.fixture
def adapter():
    """Create a temporary SQLite adapter for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_fam.db"
        adapter = SQLiteAdapter(db_path)
        yield adapter
        adapter.close()


@pytest.fixture
def sample_foundup():
    """Create a sample Foundup for testing."""
    return Foundup(
        foundup_id="fdup_test123",
        name="Test FoundUp",
        owner_id="user_owner",
        token_symbol="TEST",
        immutable_metadata={"version": "1"},
        mutable_metadata={"status": "active"},
    )


@pytest.fixture
def sample_task(sample_foundup):
    """Create a sample Task for testing."""
    return Task(
        task_id="task_test123",
        foundup_id=sample_foundup.foundup_id,
        title="Test Task",
        description="A test task description",
        acceptance_criteria=["Criterion 1", "Criterion 2"],
        reward_amount=1000,
        creator_id="user_creator",
    )


class TestFoundupCRUD:
    """Tests for Foundup CRUD operations."""

    def test_create_and_get_foundup(self, adapter, sample_foundup):
        """Test creating and retrieving a Foundup."""
        adapter.create_foundup(sample_foundup)
        retrieved = adapter.get_foundup(sample_foundup.foundup_id)

        assert retrieved.foundup_id == sample_foundup.foundup_id
        assert retrieved.name == sample_foundup.name
        assert retrieved.owner_id == sample_foundup.owner_id
        assert retrieved.token_symbol == sample_foundup.token_symbol

    def test_get_nonexistent_foundup_raises(self, adapter):
        """Test that getting a nonexistent Foundup raises NotFoundError."""
        with pytest.raises(NotFoundError):
            adapter.get_foundup("fdup_nonexistent")

    def test_update_foundup_metadata(self, adapter, sample_foundup):
        """Test updating Foundup mutable metadata."""
        adapter.create_foundup(sample_foundup)
        adapter.update_foundup(sample_foundup.foundup_id, {"status": "paused"})

        retrieved = adapter.get_foundup(sample_foundup.foundup_id)
        assert retrieved.mutable_metadata["status"] == "paused"

    def test_list_foundups(self, adapter, sample_foundup):
        """Test listing Foundups."""
        adapter.create_foundup(sample_foundup)
        foundups = adapter.list_foundups()

        assert len(foundups) >= 1
        assert any(f.foundup_id == sample_foundup.foundup_id for f in foundups)

    def test_duplicate_token_symbol_raises(self, adapter, sample_foundup):
        """Token symbols must be unique (case-insensitive)."""
        adapter.create_foundup(sample_foundup)
        duplicate = Foundup(
            foundup_id="fdup_other",
            name="Other",
            owner_id="owner_2",
            token_symbol="test",
            immutable_metadata={},
            mutable_metadata={},
        )
        with pytest.raises(ValidationError):
            adapter.create_foundup(duplicate)


class TestTaskCRUD:
    """Tests for Task CRUD operations."""

    def test_create_and_get_task(self, adapter, sample_foundup, sample_task):
        """Test creating and retrieving a Task."""
        adapter.create_foundup(sample_foundup)
        adapter.create_task(sample_task)
        retrieved = adapter.get_task(sample_task.task_id)

        assert retrieved.task_id == sample_task.task_id
        assert retrieved.title == sample_task.title
        assert retrieved.status == TaskStatus.OPEN

    def test_update_task_status(self, adapter, sample_foundup, sample_task):
        """Test updating Task status."""
        adapter.create_foundup(sample_foundup)
        adapter.create_task(sample_task)

        sample_task.status = TaskStatus.CLAIMED
        sample_task.assignee_id = "agent_123"
        adapter.update_task(sample_task)

        retrieved = adapter.get_task(sample_task.task_id)
        assert retrieved.status == TaskStatus.CLAIMED
        assert retrieved.assignee_id == "agent_123"

    def test_list_tasks_by_foundup(self, adapter, sample_foundup, sample_task):
        """Test listing Tasks by Foundup."""
        adapter.create_foundup(sample_foundup)
        adapter.create_task(sample_task)

        tasks = adapter.list_tasks(sample_foundup.foundup_id)
        assert len(tasks) >= 1
        assert any(t.task_id == sample_task.task_id for t in tasks)


class TestProofVerificationPayoutCRUD:
    """Tests for Proof, Verification, and Payout CRUD."""

    def test_create_and_get_proof(self, adapter, sample_foundup, sample_task):
        """Test creating and retrieving a Proof."""
        adapter.create_foundup(sample_foundup)
        adapter.create_task(sample_task)

        proof = Proof(
            proof_id="proof_test123",
            task_id=sample_task.task_id,
            submitter_id="agent_123",
            artifact_uri="https://example.com/proof",
            artifact_hash="abc123hash",
            notes="Test proof notes",
        )
        adapter.create_proof(proof)
        retrieved = adapter.get_proof(proof.proof_id)

        assert retrieved.proof_id == proof.proof_id
        assert retrieved.artifact_uri == proof.artifact_uri

    def test_create_and_get_verification(self, adapter, sample_foundup, sample_task):
        """Test creating and retrieving a Verification."""
        adapter.create_foundup(sample_foundup)
        adapter.create_task(sample_task)

        verification = Verification(
            verification_id="ver_test123",
            task_id=sample_task.task_id,
            verifier_id="user_verifier",
            approved=True,
            reason="Looks good!",
        )
        adapter.create_verification(verification)
        retrieved = adapter.get_verification(verification.verification_id)

        assert retrieved.verification_id == verification.verification_id
        assert retrieved.approved is True

    def test_create_and_get_payout(self, adapter, sample_foundup, sample_task):
        """Test creating and retrieving a Payout."""
        adapter.create_foundup(sample_foundup)
        adapter.create_task(sample_task)

        payout = Payout(
            payout_id="pay_test123",
            task_id=sample_task.task_id,
            recipient_id="agent_123",
            amount=1000,
        )
        adapter.create_payout(payout)
        retrieved = adapter.get_payout(payout.payout_id)

        assert retrieved.payout_id == payout.payout_id
        assert retrieved.amount == 1000
        assert retrieved.status == PayoutStatus.INITIATED


class TestEventCRUD:
    """Tests for EventRecord CRUD."""

    def test_create_and_query_events(self, adapter, sample_foundup):
        """Test creating and querying events."""
        adapter.create_foundup(sample_foundup)

        event = EventRecord(
            event_id="evt_test123",
            event_type="task.created",
            actor_id="user_actor",
            payload={"key": "value"},
            foundup_id=sample_foundup.foundup_id,
        )
        adapter.create_event(event)

        events = adapter.query_events(foundup_id=sample_foundup.foundup_id)
        assert len(events) >= 1
        assert any(e.event_id == event.event_id for e in events)

    def test_query_events_by_type(self, adapter, sample_foundup):
        """Test querying events by type."""
        adapter.create_foundup(sample_foundup)

        event1 = EventRecord(
            event_id="evt_1",
            event_type="task.created",
            actor_id="user_actor",
            payload={},
            foundup_id=sample_foundup.foundup_id,
        )
        event2 = EventRecord(
            event_id="evt_2",
            event_type="task.claimed",
            actor_id="user_actor",
            payload={},
            foundup_id=sample_foundup.foundup_id,
        )
        adapter.create_event(event1)
        adapter.create_event(event2)

        events = adapter.query_events(event_type="task.created")
        assert all(e.event_type == "task.created" for e in events)


class TestComputeAccessPersistence:
    """Tests for compute access persistence operations."""

    def test_activate_plan_and_wallet(self, adapter):
        plan = adapter.activate_compute_plan(
            actor_id="actor_1",
            tier="builder",
            monthly_credit_allocation=30,
        )
        wallet = adapter.get_wallet("actor_1")
        assert plan["tier"] == "builder"
        assert wallet["credit_balance"] == 30
        assert wallet["tier"] == "builder"

    def test_purchase_and_debit_and_rebate(self, adapter):
        adapter.activate_compute_plan("actor_1", tier="builder", monthly_credit_allocation=0)
        purchase = adapter.purchase_credits("actor_1", amount=20, rail="subscription", payment_ref="pay_1")
        debit = adapter.debit_credits(
            actor_id="actor_1",
            amount=5,
            reason="task.create",
            foundup_id="f_1",
        )
        rebate = adapter.rebate_credits("actor_1", amount=2, reason="pob_bonus")
        wallet = adapter.get_wallet("actor_1")
        ledger = adapter.list_compute_ledger("actor_1")

        assert purchase["entry_type"] == "purchase"
        assert debit["entry_type"] == "debit"
        assert rebate["entry_type"] == "rebate"
        assert wallet["credit_balance"] == 17
        assert len(ledger) == 3

    def test_ensure_access_enforced(self, adapter):
        adapter.compute_access_enforced = True
        adapter.activate_compute_plan("actor_1", tier="builder", monthly_credit_allocation=1)
        denied = adapter.ensure_access("actor_1", capability="foundup.launch", foundup_id="f_1")
        allowed = adapter.ensure_access("actor_1", capability="task.claim", foundup_id="f_1")

        assert denied["allowed"] is False
        assert denied["reason"] == "insufficient compute credits"
        assert allowed["allowed"] is True

    def test_compute_session_round_trip(self, adapter):
        session_id = adapter.record_compute_session(
            actor_id="actor_1",
            foundup_id="f_1",
            workload={"tasks": 2, "model": "qwen"},
            credits_debited=3,
        )
        session = adapter.get_compute_session(session_id)
        assert session["session_id"] == session_id
        assert session["credits_debited"] == 3
        assert session["workload"]["tasks"] == 2

    def test_compute_session_missing_raises(self, adapter):
        with pytest.raises(NotFoundError):
            adapter.get_compute_session("missing")
