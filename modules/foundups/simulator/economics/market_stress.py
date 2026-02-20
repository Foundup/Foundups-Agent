"""Market stress primitives for fee-elasticity and slippage modeling.

Purpose:
- Convert raw fee flow into conservative effective flow under market stress.
- Keep assumptions explicit and testable for investor diligence.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketStressConfig:
    """Configurable market stress assumptions.

    All rates are decimal fractions (0.01 = 1%).
    """

    base_fee_rate: float = 0.02
    base_slippage_rate: float = 0.001
    slippage_impact_coeff: float = 0.06
    slippage_impact_exponent: float = 1.10
    max_slippage_rate: float = 0.25
    elasticity: float = 1.20
    min_volume_factor: float = 0.15
    max_volume_factor: float = 1.35


@dataclass(frozen=True)
class MarketStressResult:
    """Derived stress outputs for one market condition."""

    slippage_rate: float
    slippage_bps: float
    total_cost_rate: float
    elasticity_factor: float
    effective_volume_factor: float


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def estimate_slippage_rate(
    *,
    avg_trade_volume_sats: float,
    depth_sats: float,
    config: MarketStressConfig | None = None,
) -> float:
    """Estimate per-trade slippage from utilization and depth."""
    cfg = config or MarketStressConfig()
    if avg_trade_volume_sats <= 0 or depth_sats <= 0:
        return cfg.base_slippage_rate

    utilization = avg_trade_volume_sats / max(1.0, depth_sats)
    impact = cfg.slippage_impact_coeff * (utilization ** cfg.slippage_impact_exponent)
    slippage = cfg.base_slippage_rate + impact
    return _clamp(slippage, cfg.base_slippage_rate, cfg.max_slippage_rate)


def estimate_effective_volume_factor(
    *,
    fee_rate: float,
    slippage_rate: float,
    demand_factor: float,
    config: MarketStressConfig | None = None,
) -> float:
    """Estimate order-flow multiplier under fee+slippage cost."""
    cfg = config or MarketStressConfig()
    reference_cost = max(1e-9, cfg.base_fee_rate + cfg.base_slippage_rate)
    total_cost = max(1e-9, fee_rate + slippage_rate)

    # Elasticity > 1 amplifies volume loss when cost rises.
    elasticity_factor = (reference_cost / total_cost) ** cfg.elasticity
    raw = max(0.0, demand_factor) * elasticity_factor
    return _clamp(raw, cfg.min_volume_factor, cfg.max_volume_factor)


def estimate_market_stress(
    *,
    avg_trade_volume_sats: float,
    depth_sats: float,
    fee_rate: float,
    demand_factor: float = 1.0,
    config: MarketStressConfig | None = None,
) -> MarketStressResult:
    """Compute slippage + elasticity-adjusted volume factor."""
    cfg = config or MarketStressConfig()
    slippage_rate = estimate_slippage_rate(
        avg_trade_volume_sats=avg_trade_volume_sats,
        depth_sats=depth_sats,
        config=cfg,
    )
    effective_volume_factor = estimate_effective_volume_factor(
        fee_rate=fee_rate,
        slippage_rate=slippage_rate,
        demand_factor=demand_factor,
        config=cfg,
    )
    total_cost = fee_rate + slippage_rate
    elasticity_factor = (
        effective_volume_factor / max(demand_factor, 1e-9)
        if demand_factor > 0
        else 0.0
    )
    return MarketStressResult(
        slippage_rate=slippage_rate,
        slippage_bps=slippage_rate * 10_000,
        total_cost_rate=total_cost,
        elasticity_factor=elasticity_factor,
        effective_volume_factor=effective_volume_factor,
    )

