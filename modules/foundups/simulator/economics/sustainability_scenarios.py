"""Downside/base/upside sustainability scenario pack with confidence bands."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable

from .market_stress import (
    MarketStressConfig,
    estimate_market_stress,
)


CONFIDENCE_Z_10_90 = 1.2815515655446004
DEFAULT_FEE_RATE = 0.02


@dataclass(frozen=True)
class ScenarioDefinition:
    """Single scenario assumptions."""

    name: str
    demand_factor: float
    depth_factor: float
    volatility_sigma: float


def default_scenario_pack() -> tuple[ScenarioDefinition, ...]:
    """Investor-conservative default scenarios."""
    return (
        ScenarioDefinition(
            name="downside",
            demand_factor=0.65,
            depth_factor=0.55,
            volatility_sigma=0.35,
        ),
        ScenarioDefinition(
            name="base",
            demand_factor=1.00,
            depth_factor=1.00,
            volatility_sigma=0.20,
        ),
        ScenarioDefinition(
            name="upside",
            demand_factor=1.25,
            depth_factor=1.20,
            volatility_sigma=0.15,
        ),
    )


def _confidence_band(value: float, sigma: float) -> Dict[str, float]:
    """Log-normal style confidence band around central estimate."""
    if value <= 0:
        return {"p10": 0.0, "p50": 0.0, "p90": 0.0}
    spread = CONFIDENCE_Z_10_90 * max(0.0, sigma)
    return {
        "p10": value * math.exp(-spread),
        "p50": value,
        "p90": value * math.exp(spread),
    }


def evaluate_scenario_pack(
    *,
    daily_dex_fee_btc: float,
    daily_exit_fee_btc: float,
    daily_creation_fee_btc: float,
    burn_btc: float,
    foundup_count: int,
    network_pool_btc: float,
    avg_trade_volume_sats: float,
    fee_rate: float = DEFAULT_FEE_RATE,
    scenarios: Iterable[ScenarioDefinition] | None = None,
    stress_config: MarketStressConfig | None = None,
) -> Dict[str, Dict]:
    """Evaluate downside/base/upside scenarios with confidence intervals."""
    scenario_defs = tuple(scenarios or default_scenario_pack())
    cfg = stress_config or MarketStressConfig(base_fee_rate=fee_rate)

    # Conservative depth proxy: subset of network pool + per-foundup liquidity floor.
    base_depth_sats = max(
        5_000_000.0,  # 0.05 BTC floor
        (network_pool_btc * 100_000_000 * 0.25) + (max(foundup_count, 1) * 2_000_000),
    )

    outputs: Dict[str, Dict] = {}
    for scenario in scenario_defs:
        depth_sats = max(1.0, base_depth_sats * scenario.depth_factor)
        stress = estimate_market_stress(
            avg_trade_volume_sats=avg_trade_volume_sats,
            depth_sats=depth_sats,
            fee_rate=fee_rate,
            demand_factor=scenario.demand_factor,
            config=cfg,
        )

        adj_dex_fee_btc = daily_dex_fee_btc * stress.effective_volume_factor
        # Exit and creation are demand-sensitive but not directly slippage-priced.
        adj_exit_fee_btc = daily_exit_fee_btc * scenario.demand_factor
        adj_creation_fee_btc = daily_creation_fee_btc * scenario.demand_factor
        daily_total_btc = max(0.0, adj_dex_fee_btc + adj_exit_fee_btc + adj_creation_fee_btc)
        band = _confidence_band(daily_total_btc, scenario.volatility_sigma)

        outputs[scenario.name] = {
            "name": scenario.name,
            "demand_factor": scenario.demand_factor,
            "depth_factor": scenario.depth_factor,
            "volatility_sigma": scenario.volatility_sigma,
            "slippage_bps": stress.slippage_bps,
            "effective_volume_factor": stress.effective_volume_factor,
            "daily_revenue_btc": daily_total_btc,
            "daily_revenue_btc_p10": band["p10"],
            "daily_revenue_btc_p50": band["p50"],
            "daily_revenue_btc_p90": band["p90"],
            "revenue_cost_ratio_p10": (band["p10"] / burn_btc) if burn_btc > 0 else 0.0,
            "revenue_cost_ratio_p50": (band["p50"] / burn_btc) if burn_btc > 0 else 0.0,
            "revenue_cost_ratio_p90": (band["p90"] / burn_btc) if burn_btc > 0 else 0.0,
        }

    return outputs

