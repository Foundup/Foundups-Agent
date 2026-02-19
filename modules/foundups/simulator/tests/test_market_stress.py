"""Unit tests for market stress and scenario confidence modeling."""

from __future__ import annotations

from modules.foundups.simulator.economics.market_stress import (
    MarketStressConfig,
    estimate_effective_volume_factor,
    estimate_market_stress,
    estimate_slippage_rate,
)
from modules.foundups.simulator.economics.sustainability_scenarios import (
    evaluate_scenario_pack,
)


def test_slippage_increases_with_trade_utilization() -> None:
    cfg = MarketStressConfig()
    low = estimate_slippage_rate(avg_trade_volume_sats=10_000, depth_sats=5_000_000, config=cfg)
    high = estimate_slippage_rate(avg_trade_volume_sats=500_000, depth_sats=5_000_000, config=cfg)
    assert high > low


def test_effective_volume_factor_declines_with_higher_total_cost() -> None:
    cfg = MarketStressConfig()
    low_cost = estimate_effective_volume_factor(
        fee_rate=0.02,
        slippage_rate=0.001,
        demand_factor=1.0,
        config=cfg,
    )
    high_cost = estimate_effective_volume_factor(
        fee_rate=0.02,
        slippage_rate=0.05,
        demand_factor=1.0,
        config=cfg,
    )
    assert high_cost < low_cost


def test_scenario_pack_confidence_bands_and_ordering() -> None:
    pack = evaluate_scenario_pack(
        daily_dex_fee_btc=0.25,
        daily_exit_fee_btc=0.02,
        daily_creation_fee_btc=0.01,
        burn_btc=0.01,
        foundup_count=100,
        network_pool_btc=12.0,
        avg_trade_volume_sats=250_000,
    )
    assert {"downside", "base", "upside"} <= set(pack.keys())

    downside = pack["downside"]
    base = pack["base"]
    upside = pack["upside"]

    assert downside["daily_revenue_btc_p10"] <= downside["daily_revenue_btc_p50"] <= downside["daily_revenue_btc_p90"]
    assert base["daily_revenue_btc_p10"] <= base["daily_revenue_btc_p50"] <= base["daily_revenue_btc_p90"]
    assert upside["daily_revenue_btc_p10"] <= upside["daily_revenue_btc_p50"] <= upside["daily_revenue_btc_p90"]

    assert downside["daily_revenue_btc"] <= base["daily_revenue_btc"] <= upside["daily_revenue_btc"]


def test_market_stress_result_contains_bps() -> None:
    result = estimate_market_stress(
        avg_trade_volume_sats=100_000,
        depth_sats=10_000_000,
        fee_rate=0.02,
        demand_factor=0.8,
    )
    assert result.slippage_bps >= 0
    assert 0 <= result.effective_volume_factor <= 1.35

