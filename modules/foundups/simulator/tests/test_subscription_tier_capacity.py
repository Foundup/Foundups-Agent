"""Regression tests for subscription tier capacity math."""

from __future__ import annotations

from modules.foundups.simulator.economics.subscription_tiers import (
    TIERS,
    get_tier_capacity_metrics,
    project_subscription_revenue,
)


def test_effective_ups_30d_reflects_reset_cadence() -> None:
    assert TIERS["starter"].effective_ups_30d == 6000
    assert TIERS["basic"].effective_ups_30d == 21000
    assert TIERS["plus"].effective_ups_30d == int(15000 * (30 / 7))


def test_daily_budget_matches_cycle_allocation() -> None:
    assert TIERS["free"].daily_budget_ups == (1000 / 30)
    assert TIERS["pro"].daily_budget_ups == (40000 / 5)


def test_capacity_metrics_include_investor_fields() -> None:
    metrics = get_tier_capacity_metrics()
    plus = metrics["plus"]
    assert plus["ups_per_cycle"] == 15000
    assert plus["reset_days"] == 7
    assert plus["effective_ups_30d"] > plus["ups_per_cycle"]


def test_revenue_projection_exposes_reset_aware_ups_distribution() -> None:
    projection = project_subscription_revenue(users=10_000)
    assert projection["ups_monthly_distributed_effective"] >= projection["ups_monthly_distributed"]
