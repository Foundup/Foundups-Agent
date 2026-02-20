"""MVP offering tests for F_0 investor program semantics."""

from __future__ import annotations

import pytest

from modules.foundups.agent_market.src.exceptions import PermissionDeniedError
from modules.foundups.agent_market.src.in_memory import InMemoryAgentMarket
from modules.foundups.agent_market.src.models import Foundup


def _seed_foundup(market: InMemoryAgentMarket, foundup_id: str = "f_target") -> None:
    market.create_foundup(
        Foundup(
            foundup_id=foundup_id,
            name="Target FoundUp",
            owner_id="founder_0",
            token_symbol="TGT",
            immutable_metadata={},
            mutable_metadata={},
        )
    )


def test_accrue_investor_terms_caps_at_five_terms() -> None:
    market = InMemoryAgentMarket(deterministic=True)
    result = market.accrue_investor_terms("investor_a", terms=7, term_ups=200, max_terms=5)

    assert result["terms"] == 5
    assert result["added_terms"] == 5
    assert result["available_ups"] == 1_000

    second = market.accrue_investor_terms("investor_a", terms=1, term_ups=200, max_terms=5)
    assert second["terms"] == 5
    assert second["added_terms"] == 0
    assert second["available_ups"] == 1_000


def test_place_mvp_bid_requires_hoarded_ups() -> None:
    market = InMemoryAgentMarket(deterministic=True)
    _seed_foundup(market)
    market.accrue_investor_terms("investor_a", terms=1, term_ups=200, max_terms=5)

    with pytest.raises(PermissionDeniedError):
        market.place_mvp_bid("f_target", "investor_a", bid_ups=250)


def test_resolve_mvp_offering_highest_bidder_wins_and_injects_treasury() -> None:
    market = InMemoryAgentMarket(
        actor_roles={"treasury_0": "treasury"},
        deterministic=True,
    )
    _seed_foundup(market)

    market.accrue_investor_terms("investor_a", terms=5, term_ups=200, max_terms=5)
    market.accrue_investor_terms("investor_b", terms=5, term_ups=200, max_terms=5)

    market.place_mvp_bid("f_target", "investor_a", bid_ups=300)
    market.place_mvp_bid("f_target", "investor_b", bid_ups=450)

    allocations = market.resolve_mvp_offering(
        foundup_id="f_target",
        actor_id="treasury_0",
        token_amount=1_000,
        top_n=1,
    )

    assert len(allocations) == 1
    assert allocations[0]["investor_id"] == "investor_b"
    assert allocations[0]["bid_ups"] == 450
    assert allocations[0]["token_amount"] == 1_000
    assert market.get_mvp_treasury_injection("f_target") == 450

    # Losing bids are refunded to available balance.
    investor_a = market.get_investor_subscription_state("investor_a")
    investor_b = market.get_investor_subscription_state("investor_b")
    assert investor_a["available_ups"] == 1_000
    assert investor_b["available_ups"] == 550


def test_resolve_mvp_offering_requires_treasury_role() -> None:
    market = InMemoryAgentMarket(
        actor_roles={"advisory_0": "advisory"},
        deterministic=True,
    )
    _seed_foundup(market)
    market.accrue_investor_terms("investor_a", terms=2, term_ups=200, max_terms=5)
    market.place_mvp_bid("f_target", "investor_a", bid_ups=150)

    with pytest.raises(PermissionDeniedError):
        market.resolve_mvp_offering(
            foundup_id="f_target",
            actor_id="advisory_0",
            token_amount=1_000,
            top_n=1,
        )
