"""Hardening tests for ten-year projection lifecycle economics."""

from __future__ import annotations

from modules.foundups.simulator.economics.ten_year_projection import (
    ANGEL_TIER_CONFIG,
    AVG_ANGELS_PER_OPO,
    ANGEL_GROWTH_SCENARIOS,
    GROWTH_SCENARIOS,
    PASS_RATE,
    calculate_angel_revenue,
    calculate_daily_volume,
    calculate_opo_capacity,
    generate_projection,
    interpolate_angels,
    interpolate_growth,
    interpolate_subscribers,
    SUBSCRIBER_GROWTH_SCENARIOS,
)


def test_lifecycle_stocks_conserve_total_foundups() -> None:
    """Pre-OPO + post-OPO stock should always match total FoundUps."""
    projection = generate_projection("baseline", 50)
    for year in projection.years:
        assert year.foundups_pre_opo + year.foundups_post_opo == year.foundups


def test_opo_count_is_bounded_by_angel_capacity() -> None:
    """OPO throughput must stay within modeled Angel review capacity."""
    projection = generate_projection("baseline", 50)
    for year in projection.years:
        assert year.opos_this_year <= calculate_opo_capacity(year.angels)
        assert year.opos_this_year <= year.foundups


def test_pass_fee_scales_with_participating_angels_not_total_network() -> None:
    """Pass-fee revenue should not explode with total Angel count."""
    r_small = calculate_angel_revenue(angels=100, opos_this_year=1000)
    r_large = calculate_angel_revenue(angels=5000, opos_this_year=1000)
    # Participant cap means additional idle Angels do not amplify per-OPO pass fees.
    assert r_small["pass_fees_btc"] == r_large["pass_fees_btc"]


def test_pass_fee_upper_bound_matches_participation_cap() -> None:
    """Pass fees are bounded by participating Angels and pass rate assumptions."""
    opos = 500
    revenue = calculate_angel_revenue(angels=50, opos_this_year=opos)
    participants = min(AVG_ANGELS_PER_OPO, ANGEL_TIER_CONFIG["max_angels_per_opo"], 50)
    max_pass_ups = opos * participants * PASS_RATE * ANGEL_TIER_CONFIG["pass_fee_ups"]
    max_pass_btc = (max_pass_ups * 0.001) / 100_000
    assert revenue["pass_fees_btc"] <= max_pass_btc + 1e-12


def test_growth_curves_preserve_anchor_points() -> None:
    """Interpolation should honor explicit point values at year boundaries."""
    assert interpolate_growth(0, "baseline") == 100
    assert interpolate_subscribers(0, "baseline") == 100
    assert interpolate_angels(0, "baseline") == 10
    assert interpolate_growth(10, "baseline") == GROWTH_SCENARIOS["baseline"]["y10"]
    assert interpolate_subscribers(10, "baseline") == SUBSCRIBER_GROWTH_SCENARIOS["baseline"]["y10"]
    assert interpolate_angels(10, "baseline") == ANGEL_GROWTH_SCENARIOS["baseline"]["y10"]


def test_volume_calibration_improves_with_more_depth() -> None:
    """Higher reserve depth should reduce stress discount on daily volume."""
    low_depth = calculate_daily_volume(
        foundups=50_000,
        post_opo_only=True,
        foundups_post_opo=20_000,
        cumulative_btc_reserve=10,
        market_demand_factor=1.0,
        trades_per_foundup_per_day=20,
        return_details=True,
    )
    high_depth = calculate_daily_volume(
        foundups=50_000,
        post_opo_only=True,
        foundups_post_opo=20_000,
        cumulative_btc_reserve=1000,
        market_demand_factor=1.0,
        trades_per_foundup_per_day=20,
        return_details=True,
    )
    assert high_depth["effective_volume_factor"] >= low_depth["effective_volume_factor"]
    assert high_depth["adjusted_daily_volume_usd"] >= low_depth["adjusted_daily_volume_usd"]


def test_revenue_lanes_and_confidence_ratios_are_ordered() -> None:
    """Gross >= protocol >= platform and downside/base/upside ratio order holds."""
    projection = generate_projection("baseline", 50)
    y10 = projection.years[-1]
    assert y10.annual_revenue_btc + 1e-9 >= y10.annual_revenue_protocol_capture_btc
    assert y10.annual_revenue_protocol_capture_btc >= y10.annual_revenue_platform_capture_btc
    assert y10.downside_revenue_cost_ratio_p10 <= y10.base_revenue_cost_ratio_p50
    assert y10.base_revenue_cost_ratio_p50 <= y10.upside_revenue_cost_ratio_p90


def test_high_tier_volume_counts_are_capped_conservatively() -> None:
    """High-tier counts should be capped to avoid runaway volume projections."""
    details = calculate_daily_volume(
        foundups=10_000_000,
        post_opo_only=True,
        foundups_post_opo=4_000_000,
        cumulative_btc_reserve=1_000,
        market_demand_factor=1.0,
        trades_per_foundup_per_day=20,
        active_trading_pct=0.01,
        return_details=True,
    )
    tier_counts = details["tier_counts_for_volume"]
    assert tier_counts["F3_INFRA"] <= 2500
    assert tier_counts["F4_MEGA"] <= 250
    assert tier_counts["F5_SYSTEMIC"] <= 25
    assert details["tier_caps_applied"] >= 1
