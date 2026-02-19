"""Ecosystem fee revenue model tests."""

from __future__ import annotations

import pytest

from modules.foundups.simulator.economics.ecosystem_revenue import (
    DEX_FEE_RATE,
    FoundUpActivity,
    calculate_foundup_revenue,
    get_exit_fee_rate,
    model_ecosystem_revenue,
)


def test_get_exit_fee_rate_uses_vesting_schedule_floor() -> None:
    assert get_exit_fee_rate(0.25) == pytest.approx(0.15, abs=1e-12)
    assert get_exit_fee_rate(2.0) == pytest.approx(0.07, abs=1e-12)
    assert get_exit_fee_rate(9.0) == pytest.approx(0.02, abs=1e-12)


def test_calculate_foundup_revenue_breaks_out_components() -> None:
    activity = FoundUpActivity(
        foundup_id="f_test",
        tier="F1_OPO",
        daily_trading_volume_usd=10_000,
        daily_exits_usd=2_000,
        avg_vesting_years=1.0,
        mined_fi_daily=100_000,
        staked_fi_daily=50_000,
    )
    revenue = calculate_foundup_revenue(activity)

    expected_dex = activity.daily_trading_volume_usd * DEX_FEE_RATE
    expected_exit = activity.daily_exits_usd * 0.10
    # 1 sat = $0.001 at BTC $100k
    expected_creation = (100_000 * 0.11 + 50_000 * 0.03) * 0.001

    assert revenue.dex_fee_usd == pytest.approx(expected_dex, abs=1e-9)
    assert revenue.exit_fee_usd == pytest.approx(expected_exit, abs=1e-9)
    assert revenue.creation_fee_usd == pytest.approx(expected_creation, abs=1e-9)
    assert revenue.total_usd == pytest.approx(
        expected_dex + expected_exit + expected_creation,
        abs=1e-9,
    )


def test_model_ecosystem_revenue_zero_counts_returns_zero_totals() -> None:
    revenue = model_ecosystem_revenue({"F0_DAE": 0, "F1_OPO": 0})
    assert revenue["daily"]["total"] == pytest.approx(0.0, abs=1e-12)
    assert revenue["monthly"]["total"] == pytest.approx(0.0, abs=1e-12)
    assert revenue["annual"]["total"] == pytest.approx(0.0, abs=1e-12)
