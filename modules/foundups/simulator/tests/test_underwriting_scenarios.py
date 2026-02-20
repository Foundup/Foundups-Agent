"""Underwriting scenario engine tests."""

from __future__ import annotations

import pytest

from modules.foundups.simulator.economics import (
    ContractTerms,
    FoundupLane,
    PoolMember,
    ScenarioConfig,
    run_underwriting_matrix,
    simulate_underwriting,
    stake_weight,
)


def test_stake_weight_from_principal() -> None:
    assert stake_weight(10.0, 1000.0) == pytest.approx(0.01, abs=1e-12)
    with pytest.raises(ValueError):
        stake_weight(0.0, 1000.0)
    with pytest.raises(ValueError):
        stake_weight(10.0, 0.0)


def test_simulate_underwriting_respects_buyout_floor() -> None:
    scenario = ScenarioConfig(
        name="low-growth",
        horizon_years=10,
        base_network_distribution_btc=20.0,
        distribution_cagr=0.05,
        adoption_cap=0.50,
        investor_weight=0.01,
    )
    outcome = simulate_underwriting(
        principal_btc=10.0,
        scenario=scenario,
        terms=ContractTerms(
            pre_hurdle_pool_rate=0.1216,
            post_hurdle_pool_rate=0.0064,
            repayment_multiple=10.0,
            buyout_floor_enabled=True,
        ),
    )
    assert outcome.projected_multiple_3y < 10.0
    assert outcome.effective_multiple_3y == pytest.approx(10.0, abs=1e-9)


def test_pool_rate_transitions_post_hurdle_when_target_hit() -> None:
    scenario = ScenarioConfig(
        name="fast-growth",
        horizon_years=10,
        base_network_distribution_btc=6000.0,
        distribution_cagr=0.45,
        adoption_cap=0.95,
        investor_weight=0.05,
    )
    outcome = simulate_underwriting(
        principal_btc=5.0,
        scenario=scenario,
        terms=ContractTerms(repayment_multiple=10.0),
    )
    assert outcome.hurdle_year is not None
    assert any(row.pool_rate == pytest.approx(0.0064, abs=1e-12) for row in outcome.yearly)


def test_underwriting_matrix_has_conservative_base_scale() -> None:
    matrix = run_underwriting_matrix(principal_btc=10.0, total_invested_btc=1000.0)
    assert set(matrix.keys()) == {"conservative", "base", "scale"}
    for outcome in matrix.values():
        assert len(outcome.yearly) == 10
        assert outcome.projected_multiple_10y >= outcome.projected_multiple_3y


def test_pool_weighted_mode_uses_lane_membership_not_straight_share() -> None:
    scenario = ScenarioConfig(
        name="pool-weighted",
        horizon_years=1,
        base_network_distribution_btc=100.0,
        distribution_cagr=0.0,
        investor_weight=0.5,  # Ignored in pooled mode
        focal_investor_id="fx_investor",
        pool_members=[
            PoolMember(investor_id="seed", member_weight=1.0, membership="seed"),
            PoolMember(
                investor_id="fx_investor",
                member_weight=1.0,
                membership="foundup",
                target_foundup_id="FX",
            ),
        ],
        foundup_lanes=[
            FoundupLane(foundup_id="FX", network_distribution_share=0.5, adoption_cap=0.9),
            FoundupLane(foundup_id="FY", network_distribution_share=0.5, adoption_cap=0.9),
        ],
    )

    outcome = simulate_underwriting(
        principal_btc=10.0,
        scenario=scenario,
        terms=ContractTerms(repayment_multiple=100.0),  # keep pre-hurdle
    )
    row = outcome.yearly[0]
    assert row.lane_allocations is not None
    assert row.lane_allocations["FX"] > 0
    assert row.lane_allocations["FY"] == pytest.approx(0.0, abs=1e-12)
    assert row.investor_distribution_btc == pytest.approx(
        row.lane_allocations["FX"] + row.lane_allocations["FY"],
        abs=1e-12,
    )

    # Pooled result should not equal naive straight 50% share.
    naive = row.network_distribution_btc * row.adoption_factor * row.pool_rate * 0.5
    assert row.investor_distribution_btc < naive
