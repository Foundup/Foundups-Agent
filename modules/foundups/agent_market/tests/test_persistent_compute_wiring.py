"""Tests for compute access wiring in persistent service layer."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from modules.foundups.agent_market.src.exceptions import PermissionDeniedError
from modules.foundups.agent_market.src.models import Foundup, Proof, Task, Verification
from modules.foundups.agent_market.src.persistence.sqlite_adapter import SQLiteAdapter
from modules.foundups.agent_market.src.registry import PersistentFoundupRegistry
from modules.foundups.agent_market.src.task_pipeline import PersistentTaskPipeline


@pytest.fixture
def adapter():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "persistent_compute.db"
        adapter = SQLiteAdapter(db_path)
        yield adapter
        adapter.close()


def _foundup(foundup_id: str = "f_1", owner_id: str = "owner_1") -> Foundup:
    return Foundup(
        foundup_id=foundup_id,
        name="persistent compute foundup",
        owner_id=owner_id,
        token_symbol="FUP",
        immutable_metadata={"launch_model": "tokenized"},
        mutable_metadata={},
    )


def test_registry_enforces_compute_access(adapter):
    adapter.compute_access_enforced = True
    registry = PersistentFoundupRegistry(adapter)
    with pytest.raises(PermissionDeniedError):
        registry.create_foundup(_foundup())


def test_registry_debits_launch_when_plan_active(adapter):
    adapter.compute_access_enforced = True
    adapter.activate_compute_plan("owner_1", tier="builder", monthly_credit_allocation=20)
    registry = PersistentFoundupRegistry(adapter)

    registry.create_foundup(_foundup())
    wallet = adapter.get_wallet("owner_1")
    assert wallet["credit_balance"] == 10

    ledger = adapter.list_compute_ledger("owner_1")
    assert any(entry["entry_type"] == "debit" and entry["reason"] == "create_foundup" for entry in ledger)


def test_task_pipeline_enforces_and_debits_each_step(adapter):
    adapter.compute_access_enforced = True
    for actor in ("owner_1", "agent_1", "verifier_1", "treasury_1"):
        adapter.activate_compute_plan(actor, tier="builder", monthly_credit_allocation=20)

    registry = PersistentFoundupRegistry(adapter)
    pipeline = PersistentTaskPipeline(adapter)
    registry.create_foundup(_foundup())

    task = Task(
        task_id="task_1",
        foundup_id="f_1",
        title="build compute gate",
        description="wire compute gating",
        acceptance_criteria=["gate", "tests"],
        reward_amount=100,
        creator_id="owner_1",
    )
    pipeline.create_task(task)
    pipeline.claim_task(task.task_id, "agent_1")
    pipeline.submit_proof(
        Proof(
            proof_id="proof_1",
            task_id=task.task_id,
            submitter_id="agent_1",
            artifact_uri="ipfs://proof",
            artifact_hash="sha256:abc",
        )
    )
    pipeline.verify_proof(
        task.task_id,
        Verification(
            verification_id="ver_1",
            task_id=task.task_id,
            verifier_id="verifier_1",
            approved=True,
            reason="looks good",
        ),
    )
    pipeline.trigger_payout(task.task_id, actor_id="treasury_1")

    owner_wallet = adapter.get_wallet("owner_1")
    agent_wallet = adapter.get_wallet("agent_1")
    verifier_wallet = adapter.get_wallet("verifier_1")
    treasury_wallet = adapter.get_wallet("treasury_1")

    assert owner_wallet["credit_balance"] == 8  # 20 - launch(10) - task.create(2)
    assert agent_wallet["credit_balance"] == 17  # 20 - claim(1) - submit(2)
    assert verifier_wallet["credit_balance"] == 18  # 20 - verify(2)
    assert treasury_wallet["credit_balance"] == 19  # 20 - payout(1)
