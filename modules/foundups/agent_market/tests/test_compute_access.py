import pytest

from modules.foundups.agent_market.src.exceptions import PermissionDeniedError
from modules.foundups.agent_market.src.in_memory import InMemoryAgentMarket
from modules.foundups.agent_market.src.models import Foundup


def _foundup(foundup_id: str = "f_1", owner_id: str = "owner_1") -> Foundup:
    return Foundup(
        foundup_id=foundup_id,
        name="compute foundup",
        owner_id=owner_id,
        token_symbol="FUP",
        immutable_metadata={"launch_model": "tokenized"},
        mutable_metadata={},
    )


def test_compute_access_not_enforced_by_default():
    market = InMemoryAgentMarket()
    market.create_foundup(_foundup())
    assert market.get_foundup("f_1").owner_id == "owner_1"


def test_compute_access_enforced_requires_active_plan():
    market = InMemoryAgentMarket(compute_access_enforced=True)
    with pytest.raises(PermissionDeniedError):
        market.create_foundup(_foundup())

    denied = [e for e in market.query_events(foundup_id="f_1") if e["event_type"] == "paywall_access_denied"]
    assert denied
    assert denied[-1]["payload"]["reason"] == "active compute plan required"


def test_compute_access_enforced_scout_tier_denied():
    market = InMemoryAgentMarket(compute_access_enforced=True)
    market.activate_compute_plan("owner_1", tier="scout", monthly_credit_allocation=0)
    market.purchase_credits("owner_1", amount=50, rail="subscription", payment_ref="pay_ref_1")

    with pytest.raises(PermissionDeniedError):
        market.create_foundup(_foundup())

    denied = [e for e in market.query_events(foundup_id="f_1") if e["event_type"] == "paywall_access_denied"]
    assert denied
    assert "scout" in denied[-1]["payload"]["reason"]


def test_compute_access_builder_plan_debits_on_launch():
    market = InMemoryAgentMarket(compute_access_enforced=True, deterministic=True)
    market.activate_compute_plan("owner_1", tier="builder")
    market.purchase_credits("owner_1", amount=20, rail="subscription", payment_ref="pay_ref_2")
    market.create_foundup(_foundup())

    wallet = market.get_wallet("owner_1")
    assert wallet["credit_balance"] == 10  # foundup.launch cost = 10

    debits = [e for e in market.query_events(foundup_id="f_1") if e["event_type"] == "compute_credits_debited"]
    assert len(debits) == 1
    assert debits[0]["payload"]["amount"] == 10


def test_debit_credits_insufficient_emits_denied():
    market = InMemoryAgentMarket(deterministic=True)
    with pytest.raises(PermissionDeniedError):
        market.debit_credits("actor_1", amount=3, reason="task.create", foundup_id="f_1")

    denied = [e for e in market.query_events(foundup_id="f_1") if e["event_type"] == "paywall_access_denied"]
    assert denied


def test_record_compute_session_emits_event():
    market = InMemoryAgentMarket(deterministic=True)
    market.create_foundup(_foundup())
    session_id = market.record_compute_session("agent_1", "f_1", workload={"task_count": 2})
    assert session_id.startswith("ccsess_")
    assert session_id in market.compute_sessions

    events = [e for e in market.query_events(foundup_id="f_1") if e["event_type"] == "compute_session_recorded"]
    assert len(events) == 1
    assert events[0]["payload"]["session_id"] == session_id


def test_rebate_credits_updates_wallet_and_ledger():
    market = InMemoryAgentMarket(deterministic=True)
    entry = market.rebate_credits("actor_1", amount=7, reason="pob_quality_bonus")
    wallet = market.get_wallet("actor_1")

    assert entry["entry_type"] == "rebate"
    assert wallet["credit_balance"] == 7


def test_ensure_access_with_builder_and_balance():
    market = InMemoryAgentMarket(compute_access_enforced=True)
    market.activate_compute_plan("owner_1", tier="builder")
    market.purchase_credits("owner_1", amount=5, rail="subscription", payment_ref="pay_ref_3")

    decision = market.ensure_access("owner_1", capability="task.create", foundup_id="f_1")
    assert decision["allowed"] is True
    assert decision["required_credits"] == 2
