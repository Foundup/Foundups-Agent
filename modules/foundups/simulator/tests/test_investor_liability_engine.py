"""Investor liability and coverage underwriting tests."""

from __future__ import annotations

import math

import pytest

from modules.foundups.simulator.economics import (
    BuyoutCoverageEngine,
    BuyoutPolicy,
    CoverageCovenants,
    EscrowSchedule,
    FundingSources,
    InvestorCohort,
    InvestorLiabilityEngine,
)


def test_annualized_return_reference_points() -> None:
    """Check canonical annualized return math points."""
    irr_3y_10x = InvestorLiabilityEngine.annualized_return(10.0, 3.0)
    irr_10y_10x = InvestorLiabilityEngine.annualized_return(10.0, 10.0)

    assert irr_3y_10x == pytest.approx(1.1544346900, abs=1e-9)
    assert irr_10y_10x == pytest.approx(0.2589254118, abs=1e-9)


def test_conservative_targets_defaults() -> None:
    targets = InvestorLiabilityEngine.conservative_targets()
    assert targets["target_3y_multiple"] == 2.5
    assert targets["target_10y_multiple"] == 10.0


def test_buyout_liability_with_partial_exercise() -> None:
    """755 BTC principal, 40% exercise, 10x buyout."""
    policy = BuyoutPolicy(buyout_multiple=10.0, exercise_rate=0.4)
    liability, exercised = InvestorLiabilityEngine.buyout_liability(755.0, policy)

    assert exercised == pytest.approx(302.0, abs=1e-9)
    assert liability == pytest.approx(3020.0, abs=1e-9)


def test_cohort_snapshot_escrow_release_schedule() -> None:
    cohort = InvestorCohort(cohort_id="seed", principal_btc=100.0, start_year=2026)
    policy = BuyoutPolicy(buyout_multiple=10.0, exercise_rate=0.5)
    schedule = EscrowSchedule()

    snap_y2 = InvestorLiabilityEngine.cohort_snapshot(
        cohort=cohort,
        year=2028,
        policy=policy,
        schedule=schedule,
    )

    assert snap_y2.escrow_released_btc == pytest.approx(40.0, abs=1e-9)
    assert snap_y2.escrow_unreleased_btc == pytest.approx(60.0, abs=1e-9)
    assert snap_y2.buyout_liability_btc == pytest.approx(500.0, abs=1e-9)


def test_aggregate_snapshots_multi_cohort() -> None:
    cohorts = [
        InvestorCohort(cohort_id="seed", principal_btc=100.0, start_year=2026),
        InvestorCohort(cohort_id="series_a", principal_btc=200.0, start_year=2027),
    ]
    policy = BuyoutPolicy(buyout_multiple=10.0, exercise_rate=0.4)
    schedule = EscrowSchedule()

    snapshots, total_liability, total_released = InvestorLiabilityEngine.aggregate_snapshots(
        cohorts=cohorts,
        year=2029,
        policy=policy,
        schedule=schedule,
    )

    assert len(snapshots) == 2
    assert total_liability == pytest.approx(1200.0, abs=1e-9)
    assert total_released == pytest.approx(180.0, abs=1e-9)


def test_coverage_passes_covenants() -> None:
    funding = FundingSources(
        escrow_releasable_btc=400.0,
        protocol_fees_btc=700.0,
        refinancing_btc=500.0,
        reserve_buffer_btc=100.0,
    )
    result = BuyoutCoverageEngine.evaluate_coverage(
        liability_btc=1200.0,
        funding=funding,
    )

    assert result.coverage_ratio == pytest.approx(1.4166666667, abs=1e-9)
    assert result.funding_gap_btc == pytest.approx(0.0, abs=1e-9)
    assert result.pass_p50 is True
    assert result.pass_p90 is True


def test_coverage_fails_covenants_when_underfunded() -> None:
    funding = FundingSources(
        escrow_releasable_btc=120.0,
        protocol_fees_btc=90.0,
        refinancing_btc=0.0,
        reserve_buffer_btc=0.0,
    )
    covenants = CoverageCovenants(p50_min=1.25, p90_min=1.0)

    result = BuyoutCoverageEngine.evaluate_coverage(
        liability_btc=400.0,
        funding=funding,
        covenants=covenants,
    )

    assert result.coverage_ratio == pytest.approx(0.525, abs=1e-9)
    assert result.funding_gap_btc == pytest.approx(190.0, abs=1e-9)
    assert result.pass_p50 is False
    assert result.pass_p90 is False


def test_required_total_funding() -> None:
    assert BuyoutCoverageEngine.required_total_funding(400.0, 1.25) == pytest.approx(
        500.0, abs=1e-9
    )


def test_zero_liability_is_trivially_covered() -> None:
    result = BuyoutCoverageEngine.evaluate_coverage(
        liability_btc=0.0,
        funding=FundingSources(),
    )
    assert math.isinf(result.coverage_ratio)
    assert result.funding_gap_btc == 0.0
    assert result.pass_p50 is True
    assert result.pass_p90 is True


def test_invalid_inputs_raise() -> None:
    with pytest.raises(ValueError):
        InvestorLiabilityEngine.annualized_return(0.0, 3.0)
    with pytest.raises(ValueError):
        InvestorLiabilityEngine.buyout_liability(
            principal_btc=10.0,
            policy=BuyoutPolicy(buyout_multiple=10.0, exercise_rate=1.2),
        )
    with pytest.raises(ValueError):
        BuyoutCoverageEngine.required_total_funding(100.0, -0.1)
