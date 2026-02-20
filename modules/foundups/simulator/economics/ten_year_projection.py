"""10-Year Financial Projection for pAVS Litepaper Animation.

012 REQUEST (2026-02-17):
"we should create a financial animation that pulls from the SIM that allows
the 012 to see where we are going... over the next 10 years?"

This module generates:
1. FoundUp ecosystem growth curve (S-curve adoption)
2. Fee revenue projections (DEX + exit + creation)
3. SUBSCRIPTION revenue projections (stake-to-spend model)
4. BTC reserve accumulation (Hotel California)
5. Genesis staker distribution ratios
6. Self-sustainability milestones

Output: JSON data suitable for D3.js/Chart.js animation in Litepaper.

COMBINED REVENUE MODEL (2026-02-17):
- Fee Revenue: DEX 2% + Exit fees + Creation fees (from ecosystem_revenue.py)
- Subscription Revenue: Tiered subscriptions ($2.95-$29.95) where UPs are staked
  in FoundUps and spent on agent tasks (from subscription_tiers.py + agent_compute_costs.py)

The stake-to-spend model:
1. User subscribes monthly -> Gets UPs allocation
2. User STAKES UPs in a FoundUp (e.g., OpenClaw)
3. Each agent action SPENDS UPs from stake
4. UPs flow to F_i holders (workers who built/maintain the agent)
5. Monthly reset refills wallet (not stakes) -> engagement loop

PRE-OPO vs POST-OPO LIFECYCLE (2026-02-17):
======================================================
CRITICAL: ALL FoundUps are INVITE-ONLY until they OPO!

FoundUp Lifecycle Stages:
  F0_DAE (60%) = PRE-OPO (invite-only, Angels access only)
  F1_OPO+      = POST-OPO (public, full fee revenue)

Revenue Sources by Lifecycle Stage:

  PRE-OPO (F0_DAE - 60% of ecosystem):
    - Angel subscriptions ($195/month per Angel)
    - OPO staking treasury fees (20% of UPS staked)
    - Pass fees (100K UPS when Angel passes)
    - NO DEX/exit fees (not public yet)

  POST-OPO (F1+ - 40% of ecosystem):
    - Full DEX fees (2% of volume)
    - Exit fees (7% avg on exits)
    - Creation fees (7% avg on token creation)
    - All subscriber tier access

Angels are the ONLY gateway to pre-OPO FoundUps. They get RED HOT
chili pepper alerts when F_i is ready to OPO. This creates:
  1. Scarcity: Pre-OPO F_i only available to Angels
  2. Quality signal: Angel stakes = validation
  3. Treasury flow: 20% of ALL Angel OPO activity
  4. FOMO: Pass still costs UPS
"""

import json
import math
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from enum import Enum

from .market_stress import estimate_market_stress
from .sustainability_scenarios import evaluate_scenario_pack
from .compute_graph import build_compute_graph_payload


# ============================================================================
# Growth Model Constants (from ecosystem_revenue.py + genesis_bootstrap.py)
# ============================================================================

# FoundUp growth scenarios (S-curve adoption)
GROWTH_SCENARIOS = {
    "conservative": {
        "y1": 3_500,
        "y3": 25_000,
        "y5": 100_000,
        "y10": 500_000,
        "description": "Organic growth, word-of-mouth",
    },
    "baseline": {
        "y1": 20_000,
        "y3": 100_000,
        "y5": 500_000,
        "y10": 2_000_000,
        "description": "Moderate marketing, partnerships",
    },
    "openclaw": {
        "y1": 105_000,
        "y3": 500_000,
        "y5": 2_000_000,
        "y10": 10_000_000,
        "description": "Viral adoption (like pump.fun)",
    },
}

# Fee rates (from fee_revenue_tracker.py)
DEX_FEE_RATE = 0.02  # 2%
EXIT_FEE_AVG = 0.07  # Average exit fee (2-15% range)
CREATION_FEE_AVG = 0.07  # Average creation fee (3-11% range)
BTC_PRICE_USD = 100_000
SATS_PER_USD = 100_000_000 / BTC_PRICE_USD  # 1000 sats/USD @ $100K BTC
USD_PER_UPS = 1.0 / SATS_PER_USD  # 1 UPS = 1 sat accounting unit

# Market calibration by growth lane (conservative investor defaults).
SCENARIO_MARKET_CONDITIONS = {
    "conservative": {
        "demand_factor": 0.70,
        "trades_per_foundup_per_day": 8,
        "active_trading_pct": 0.0025,
    },
    "baseline": {
        "demand_factor": 1.00,
        "trades_per_foundup_per_day": 20,
        "active_trading_pct": 0.0075,
    },
    "openclaw": {
        "demand_factor": 1.20,
        "trades_per_foundup_per_day": 35,
        "active_trading_pct": 0.015,
    },
}

# Fee lane capture assumptions (explicit + auditable):
# - Platform capture: pAVS treasury only
# - Protocol capture: pAVS + network + reserve + FoundUp treasury
CAPTURE_RATES = {
    "dex_platform": 0.20,      # pAVS treasury share
    "dex_protocol": 1.00,      # 50% treasury/network + 50% F_i treasury
    "exit_protocol": 1.00,     # reserve + network
    "creation_protocol": 1.00, # F_i treasury
}

# Activity assumptions per FoundUp tier (daily USD volume)
DAILY_VOLUME_PER_FI = {
    "F0_DAE": 100,
    "F1_OPO": 1_000,
    "F2_GROWTH": 10_000,
    "F3_INFRA": 100_000,
    "F4_MEGA": 1_000_000,
    "F5_SYSTEMIC": 10_000_000,
}

# Investor-conservative ceiling for high-tier projects contributing to
# daily market volume estimates. This avoids overstating volume by
# extrapolating long-tail tiers linearly at very large FoundUp counts.
MAX_FOUNDUPS_PER_TIER_FOR_VOLUME = {
    "F3_INFRA": 2_500,
    "F4_MEGA": 250,
    "F5_SYSTEMIC": 25,
}

# Tier distribution (what % of FoundUps at each tier)
TIER_DISTRIBUTION = {
    "F0_DAE": 0.60,      # 60% seed stage
    "F1_OPO": 0.25,      # 25% early
    "F2_GROWTH": 0.10,   # 10% growing
    "F3_INFRA": 0.04,    # 4% infrastructure
    "F4_MEGA": 0.009,    # 0.9% mega
    "F5_SYSTEMIC": 0.001,  # 0.1% systemic
}

# Genesis bootstrap scenarios
BOOTSTRAP_SCENARIOS = {
    "minimum": {"btc": 20, "description": "Tight runway"},
    "conservative": {"btc": 50, "description": "YC standard"},
    "comfortable": {"btc": 120, "description": "Solid buffer"},
    "aggressive": {"btc": 500, "description": "Bitclout-style"},
}

# Operational costs (monthly BTC @ $100K)
F0_MONTHLY_BURN_BTC = 0.27  # $27K/month for F2_GROWTH tier platform

# ============================================================================
# Subscription Revenue Model (from subscription_tiers.py + agent_compute_costs.py)
# ============================================================================

# Subscriber growth scenarios (S-curve adoption like Perplexity)
SUBSCRIBER_GROWTH_SCENARIOS = {
    "conservative": {
        "y1": 5_000,
        "y3": 50_000,
        "y5": 200_000,
        "y10": 500_000,
        "description": "Organic SaaS growth",
    },
    "baseline": {
        "y1": 25_000,
        "y3": 200_000,
        "y5": 1_000_000,
        "y10": 3_000_000,
        "description": "Perplexity-like trajectory",
    },
    "openclaw": {
        "y1": 100_000,
        "y3": 1_000_000,
        "y5": 5_000_000,
        "y10": 20_000_000,
        "description": "Viral agent adoption",
    },
}

# Subscription tier pricing and distribution
SUBSCRIPTION_TIERS = {
    "free":       {"price_usd": 0.00,  "ups_monthly": 1_000,   "pct": 0.40},
    "starter":    {"price_usd": 2.95,  "ups_monthly": 3_000,   "pct": 0.20},
    "basic":      {"price_usd": 5.95,  "ups_monthly": 7_000,   "pct": 0.18},
    "plus":       {"price_usd": 9.95,  "ups_monthly": 15_000,  "pct": 0.12},
    "pro":        {"price_usd": 19.95, "ups_monthly": 40_000,  "pct": 0.07},
    "enterprise": {"price_usd": 29.95, "ups_monthly": 100_000, "pct": 0.03},
}

# Average revenue per subscriber (ARPU) calculation
# = sum(tier_price * tier_pct) for all paid tiers
SUBSCRIPTION_ARPU = sum(
    t["price_usd"] * t["pct"] for t in SUBSCRIPTION_TIERS.values()
)  # ~$4.50/month

# Agent compute margins (from agent_compute_costs.py analysis)
SUBSCRIPTION_GROSS_MARGIN = 0.85  # 85% margin after infrastructure costs

# Genesis staker assumptions
GENESIS_STAKER_CONFIG = {
    "count": 100,
    "avg_stake_btc": 0.5,
    "du_pool_pct": 0.04,  # 4% Du pool
}

# ============================================================================
# ANGEL ECONOMICS (Pre-OPO Access - $195/month)
# ============================================================================

# Angel growth scenarios (separate from subscribers - accredited only)
ANGEL_GROWTH_SCENARIOS = {
    "conservative": {
        "y1": 50,
        "y3": 200,
        "y5": 500,
        "y10": 1_000,
        "description": "Organic angel network growth",
    },
    "baseline": {
        "y1": 200,
        "y3": 800,
        "y5": 2_000,
        "y10": 5_000,
        "description": "Moderate deal flow reputation",
    },
    "openclaw": {
        "y1": 500,
        "y3": 2_000,
        "y5": 10_000,
        "y10": 25_000,
        "description": "Viral angel adoption (YC-style)",
    },
}

# Angel tier economics (from subscription_tiers.py)
ANGEL_TIER_CONFIG = {
    "price_usd": 195.00,
    "ups_monthly": 2_000_000,
    "opo_treasury_fee": 0.20,  # 20% of UPS stake -> pAVS treasury
    "pass_fee_ups": 100_000,   # 100K UPS if Angel passes on OPO
    "max_angels_per_opo": 10,
}

# OPO conversion rates (what % of pre-OPO FoundUps OPO each month)
# This determines how fast FoundUps transition from F0_DAE to F1_OPO
OPO_MONTHLY_CONVERSION_RATE = {
    "y1": 0.05,   # 5%/month - slow start, building reputation
    "y3": 0.08,   # 8%/month - established deal flow
    "y5": 0.10,   # 10%/month - mature ecosystem
    "y10": 0.12,  # 12%/month - efficient pipeline
}

# Pre-OPO vs Post-OPO tier split
PRE_OPO_TIER_PCT = 0.60   # F0_DAE tier = 60% of FoundUps
POST_OPO_TIER_PCT = 0.40  # F1_OPO+ tiers = 40% of FoundUps

# Post-OPO tier weights normalized to 1.0 (exclude F0_DAE pre-OPO lane).
POST_OPO_TIER_WEIGHTS = {
    tier: pct / POST_OPO_TIER_PCT
    for tier, pct in TIER_DISTRIBUTION.items()
    if tier != "F0_DAE"
}

# Angel engagement assumptions
AVG_ANGELS_PER_OPO = 3.5          # Average Angels that stake per OPO
AVG_UPS_STAKED_PER_ANGEL = 500_000  # Average UPS stake per Angel per OPO
PASS_RATE = 0.40                    # 40% of Angels pass on any given OPO
ANGEL_MAX_OPOS_PER_YEAR = 120       # Conservative review bandwidth per Angel/year


@dataclass
class YearSnapshot:
    """Financial snapshot for a single year."""
    year: int
    foundups: int
    daily_volume_usd: float
    daily_volume_raw_usd: float
    volume_effective_factor: float
    slippage_bps: float
    daily_revenue_usd: float
    monthly_revenue_btc: float
    annual_revenue_btc: float
    annual_revenue_protocol_capture_btc: float
    annual_revenue_platform_capture_btc: float
    cumulative_btc_reserve: float
    operational_cost_btc: float
    net_revenue_btc: float
    is_self_sustaining: bool
    downside_revenue_cost_ratio_p10: float
    base_revenue_cost_ratio_p50: float
    upside_revenue_cost_ratio_p90: float
    genesis_staker_ratio: float  # Distribution ratio for genesis stakers
    f_i_price_multiple: float  # F_i price vs genesis
    # Subscription revenue (stake-to-spend model)
    subscribers: int = 0
    subscription_revenue_usd: float = 0.0
    subscription_revenue_btc: float = 0.0
    combined_revenue_btc: float = 0.0  # fees + subscriptions
    combined_revenue_protocol_capture_btc: float = 0.0
    combined_revenue_platform_capture_btc: float = 0.0
    combined_net_revenue_btc: float = 0.0
    milestones: List[str] = field(default_factory=list)
    # Pre-OPO vs Post-OPO lifecycle breakdown (2026-02-17)
    foundups_pre_opo: int = 0         # F0_DAE tier (invite-only)
    foundups_post_opo: int = 0        # F1_OPO+ tiers (public)
    opos_this_year: int = 0           # Number of OPOs in this year
    # Angel economics
    angels: int = 0                   # Active Angel subscribers
    angel_subscription_btc: float = 0.0  # Angel subscription revenue
    angel_opo_staking_btc: float = 0.0   # 20% treasury fee from OPO stakes
    angel_pass_fees_btc: float = 0.0     # Pass fee revenue
    angel_total_revenue_btc: float = 0.0 # Total Angel-derived revenue


@dataclass
class TenYearProjection:
    """Complete 10-year projection."""
    scenario: str
    description: str
    bootstrap_btc: float
    genesis_stakers: int
    genesis_stake_total_btc: float
    years: List[YearSnapshot] = field(default_factory=list)


def sigmoid(x: float, k: float = 12.0, x0: float = 0.5) -> float:
    """S-curve function for growth modeling."""
    return 1 / (1 + math.exp(-k * (x - x0)))


def _normalized_curve(t: float, k: float = 4.0, x0: float = 0.5) -> float:
    """Endpoint-preserving S-curve transform for t in [0, 1]."""
    raw = sigmoid(t, k=k, x0=x0)
    low = sigmoid(0.0, k=k, x0=x0)
    high = sigmoid(1.0, k=k, x0=x0)
    if high <= low:
        return t
    curved = (raw - low) / (high - low)
    return max(0.0, min(1.0, curved))


def interpolate_growth(year: int, scenario: str) -> int:
    """Interpolate FoundUp count for a given year using S-curve."""
    s = GROWTH_SCENARIOS[scenario]

    # Key points
    points = [
        (0, 100),  # Genesis
        (1, s["y1"]),
        (3, s["y3"]),
        (5, s["y5"]),
        (10, s["y10"]),
    ]

    # Find surrounding points
    for i in range(len(points) - 1):
        if points[i][0] <= year <= points[i + 1][0]:
            y0, f0 = points[i]
            y1, f1 = points[i + 1]

            # Linear interpolation with endpoint-preserving S-curve adjustment
            t = (year - y0) / (y1 - y0)
            t_curved = _normalized_curve(t, k=4.0, x0=0.5)

            return int(f0 + (f1 - f0) * t_curved)

    return s["y10"]  # Beyond year 10


def interpolate_subscribers(year: int, scenario: str) -> int:
    """Interpolate subscriber count for a given year using S-curve."""
    s = SUBSCRIBER_GROWTH_SCENARIOS[scenario]

    # Key points
    points = [
        (0, 100),  # Genesis founding members
        (1, s["y1"]),
        (3, s["y3"]),
        (5, s["y5"]),
        (10, s["y10"]),
    ]

    # Find surrounding points
    for i in range(len(points) - 1):
        if points[i][0] <= year <= points[i + 1][0]:
            y0, s0 = points[i]
            y1, s1 = points[i + 1]

            # Linear interpolation with endpoint-preserving S-curve.
            t = (year - y0) / (y1 - y0)
            t_curved = _normalized_curve(t, k=4.0, x0=0.5)

            return int(s0 + (s1 - s0) * t_curved)

    return s["y10"]


def interpolate_angels(year: int, scenario: str) -> int:
    """Interpolate Angel (accredited investor) count for a given year."""
    s = ANGEL_GROWTH_SCENARIOS[scenario]

    # Key points (slower growth - accreditation barrier)
    points = [
        (0, 10),   # Genesis Angels (founders/early believers)
        (1, s["y1"]),
        (3, s["y3"]),
        (5, s["y5"]),
        (10, s["y10"]),
    ]

    # Find surrounding points
    for i in range(len(points) - 1):
        if points[i][0] <= year <= points[i + 1][0]:
            y0, a0 = points[i]
            y1, a1 = points[i + 1]

            # Linear interpolation with endpoint-preserving S-curve.
            t = (year - y0) / (y1 - y0)
            t_curved = _normalized_curve(t, k=4.0, x0=0.5)

            return int(a0 + (a1 - a0) * t_curved)

    return s["y10"]


def calculate_opo_capacity(angels: int) -> int:
    """Calculate annual OPO throughput capacity based on Angel bandwidth."""
    if angels <= 0:
        return 0
    participants = min(AVG_ANGELS_PER_OPO, ANGEL_TIER_CONFIG["max_angels_per_opo"])
    if participants <= 0:
        return 0
    annual_decisions = angels * ANGEL_MAX_OPOS_PER_YEAR
    return int(annual_decisions / participants)


def calculate_angel_revenue(
    angels: int,
    opos_this_year: int,
) -> Dict[str, float]:
    """Calculate all Angel-derived revenue streams.

    Revenue sources:
    1. Angel subscriptions ($195/month × angels × 12)
    2. OPO staking treasury fees (20% of UPS staked per OPO)
    3. Pass fees (Angels who pass still pay 100K UPS)

    Returns:
        Dict with annual_usd and annual_btc breakdown
    """
    btc_price = 100_000  # $100K/BTC assumption

    # 1. Angel subscription revenue
    angel_sub_annual_usd = angels * ANGEL_TIER_CONFIG["price_usd"] * 12
    angel_sub_annual_btc = angel_sub_annual_usd / btc_price

    participants_per_opo = min(
        AVG_ANGELS_PER_OPO,
        ANGEL_TIER_CONFIG["max_angels_per_opo"],
        float(angels) if angels > 0 else 0.0,
    )

    # 2. OPO staking treasury fees
    # Each OPO: participant Angels stake AVG_UPS_STAKED_PER_ANGEL UPS.
    # 20% goes to treasury.
    ups_staked_per_opo = participants_per_opo * AVG_UPS_STAKED_PER_ANGEL
    treasury_ups_per_opo = ups_staked_per_opo * ANGEL_TIER_CONFIG["opo_treasury_fee"]
    # Convert UPS to USD from canonical 1 UPS = 1 sat accounting relation.
    opo_treasury_annual_usd = opos_this_year * treasury_ups_per_opo * USD_PER_UPS
    opo_treasury_annual_btc = opo_treasury_annual_usd / btc_price

    # 3. Pass fee revenue
    # PASS_RATE of participating Angels pass on each OPO, paying 100K UPS.
    passes_per_opo = participants_per_opo * PASS_RATE
    pass_ups_annual = opos_this_year * passes_per_opo * ANGEL_TIER_CONFIG["pass_fee_ups"]
    pass_fees_annual_usd = pass_ups_annual * USD_PER_UPS
    pass_fees_annual_btc = pass_fees_annual_usd / btc_price

    total_btc = angel_sub_annual_btc + opo_treasury_annual_btc + pass_fees_annual_btc

    return {
        "subscription_btc": angel_sub_annual_btc,
        "opo_staking_btc": opo_treasury_annual_btc,
        "pass_fees_btc": pass_fees_annual_btc,
        "total_btc": total_btc,
    }


def calculate_subscription_revenue(subscribers: int) -> Dict[str, float]:
    """Calculate subscription revenue from tier distribution.

    Returns:
        Dict with annual_usd, annual_btc, gross_margin_btc
    """
    # Calculate monthly revenue based on tier distribution
    monthly_revenue_usd = 0.0
    for tier_name, tier in SUBSCRIPTION_TIERS.items():
        tier_subscribers = int(subscribers * tier["pct"])
        monthly_revenue_usd += tier_subscribers * tier["price_usd"]

    annual_revenue_usd = monthly_revenue_usd * 12
    annual_revenue_btc = annual_revenue_usd / 100_000  # @ $100K/BTC

    # Apply gross margin (infrastructure costs)
    gross_margin_btc = annual_revenue_btc * SUBSCRIPTION_GROSS_MARGIN

    return {
        "annual_usd": annual_revenue_usd,
        "annual_btc": annual_revenue_btc,
        "gross_margin_btc": gross_margin_btc,
    }


def calculate_daily_volume(
    foundups: int,
    post_opo_only: bool = True,
    foundups_post_opo: int | None = None,
    *,
    cumulative_btc_reserve: float = 0.0,
    market_demand_factor: float = 1.0,
    trades_per_foundup_per_day: int = 20,
    active_trading_pct: float = 0.01,
    return_details: bool = False,
) -> float | Dict[str, float]:
    """Calculate total daily volume across FoundUps.

    Args:
        foundups: Total number of FoundUps
        post_opo_only: If True, only count POST-OPO FoundUps (F1_OPO+)
                       since pre-OPO (F0_DAE) don't generate DEX fees

    CRITICAL: Pre-OPO FoundUps (F0_DAE tier, 60%) are invite-only
    and don't generate DEX fees. Only post-OPO FoundUps (F1+, 40%)
    generate public trading volume and fees.
    """
    total = 0.0
    tier_counts_for_volume: Dict[str, int] = {}
    tier_caps_applied = 0
    for tier, pct in TIER_DISTRIBUTION.items():
        # Skip F0_DAE if post_opo_only (pre-OPO doesn't generate fees)
        if post_opo_only:
            if tier == "F0_DAE":
                continue
            if foundups_post_opo is not None:
                tier_count = int(foundups_post_opo * POST_OPO_TIER_WEIGHTS[tier])
            else:
                tier_count = int(foundups * pct)
        else:
            tier_count = int(foundups * pct)

        cap = MAX_FOUNDUPS_PER_TIER_FOR_VOLUME.get(tier)
        if cap is not None and tier_count > cap:
            tier_count = cap
            tier_caps_applied += 1
        tier_counts_for_volume[tier] = tier_count

        tier_volume = DAILY_VOLUME_PER_FI[tier]
        active_count = tier_count * max(0.0, min(1.0, active_trading_pct))
        total += active_count * tier_volume
    raw_daily_volume_usd = total

    # Liquidity-aware stress calibration (depth + demand):
    # - Higher reserve depth reduces slippage.
    # - Higher demand factor increases effective flow.
    post_opo_total = foundups_post_opo or int(foundups * POST_OPO_TIER_PCT)
    post_opo_count = max(
        1,
        int(post_opo_total * max(0.0, min(1.0, active_trading_pct))),
    )
    trades_per_day = max(1, post_opo_count * max(1, trades_per_foundup_per_day))
    avg_trade_usd = raw_daily_volume_usd / trades_per_day
    avg_trade_sats = avg_trade_usd * SATS_PER_USD

    depth_sats = max(
        5_000_000.0,  # 0.05 BTC minimum depth floor
        (cumulative_btc_reserve * 100_000_000 * 0.08)
        + (post_opo_count * 2_000_000.0),
    )
    stress = estimate_market_stress(
        avg_trade_volume_sats=avg_trade_sats,
        depth_sats=depth_sats,
        fee_rate=DEX_FEE_RATE,
        demand_factor=market_demand_factor,
    )
    adjusted_daily_volume_usd = raw_daily_volume_usd * stress.effective_volume_factor

    if return_details:
        return {
            "raw_daily_volume_usd": raw_daily_volume_usd,
            "adjusted_daily_volume_usd": adjusted_daily_volume_usd,
            "effective_volume_factor": stress.effective_volume_factor,
            "slippage_bps": stress.slippage_bps,
            "avg_trade_sats": avg_trade_sats,
            "depth_sats": depth_sats,
            "tier_counts_for_volume": tier_counts_for_volume,
            "tier_caps_applied": tier_caps_applied,
        }
    return adjusted_daily_volume_usd


def calculate_daily_fee_components(daily_volume: float, foundups_post_opo: int) -> Dict[str, float]:
    """Calculate daily fee components (USD) from post-OPO flow."""
    # DEX fees (2% of volume)
    dex_fees = daily_volume * DEX_FEE_RATE

    # Exit fees (assume 5% of volume exits, avg 7% fee)
    exit_volume = daily_volume * 0.05
    exit_fees = exit_volume * EXIT_FEE_AVG

    # Creation fees (1% of post-OPO foundups create new tokens per day, $1K avg)
    # Note: Only post-OPO FoundUps can create tokens publicly
    creation_volume = foundups_post_opo * 0.01 * 1000
    creation_fees = creation_volume * CREATION_FEE_AVG

    total = dex_fees + exit_fees + creation_fees
    return {
        "dex_usd": dex_fees,
        "exit_usd": exit_fees,
        "creation_usd": creation_fees,
        "total_usd": total,
    }


def calculate_daily_revenue(daily_volume: float, foundups_post_opo: int) -> float:
    """Calculate daily revenue from fees.

    IMPORTANT: Only POST-OPO FoundUps generate fee revenue.
    Pre-OPO FoundUps are handled via Angel revenue.

    Args:
        daily_volume: Daily trading volume (from post-OPO FoundUps only)
        foundups_post_opo: Number of post-OPO FoundUps (F1+)
    """
    return calculate_daily_fee_components(daily_volume, foundups_post_opo)["total_usd"]


def calculate_opos_per_year(
    foundups: int,
    year: int,
    pre_opo_foundups: int | None = None,
) -> int:
    """Calculate number of OPOs (Open Public Offerings) in a year.

    OPO rate depends on:
    - Number of pre-OPO FoundUps (F0_DAE = 60%)
    - OPO monthly conversion rate (increases over time)
    """
    # Get conversion rate for this year
    if year <= 1:
        monthly_rate = OPO_MONTHLY_CONVERSION_RATE["y1"]
    elif year <= 3:
        monthly_rate = OPO_MONTHLY_CONVERSION_RATE["y3"]
    elif year <= 5:
        monthly_rate = OPO_MONTHLY_CONVERSION_RATE["y5"]
    else:
        monthly_rate = OPO_MONTHLY_CONVERSION_RATE["y10"]

    # Pre-OPO FoundUps defaults to 60% of total when no explicit stock is provided.
    pre_opo_count = (
        int(foundups * PRE_OPO_TIER_PCT)
        if pre_opo_foundups is None
        else max(0, int(pre_opo_foundups))
    )

    # OPOs this year = pre-OPO × monthly_rate × 12
    # (capped at 90% of pre-OPO to prevent full depletion)
    annual_rate = min(monthly_rate * 12, 0.90)
    opos = int(pre_opo_count * annual_rate)

    if pre_opo_count <= 0:
        return 0
    return max(1, min(pre_opo_count, opos))  # At least 1 OPO when stock exists


def calculate_genesis_staker_ratio(
    cumulative_btc: float,
    years: int,
    stakers: int = 100,
    stake_each_btc: float = 0.5,
) -> float:
    """Calculate distribution ratio for genesis stakers.

    Based on:
    - Du pool distributions (4% of F_i minted)
    - F_i price appreciation
    - Cumulative BTC reserve growth
    """
    total_stake = stakers * stake_each_btc

    # Distribution ratio = (BTC value of F_i held) / (BTC staked)
    # F_i appreciation is key driver

    # Model: F_i price grows with ecosystem (bonding curve effect)
    # At genesis: 1M F_i per BTC
    # At maturity: 10K F_i per BTC (100x appreciation)

    # Use log growth for F_i price
    fi_price_multiple = 1 + math.log(1 + cumulative_btc / 10) * 2

    # Du pool accumulation (4% of all F_i, distributed to stakers)
    # Simplified: stakers get proportional share

    return min(1000, fi_price_multiple * (1 + years * 0.5))  # Cap at 1000x


def generate_projection(
    scenario: str = "baseline",
    bootstrap_btc: float = 50,
) -> TenYearProjection:
    """Generate 10-year financial projection with pre-OPO/post-OPO lifecycle.

    CRITICAL ECONOMICS (2026-02-17):
    - Pre-OPO (F0_DAE, 60%): Angels only -> Angel revenue
    - Post-OPO (F1+, 40%): Public -> Fee revenue

    Revenue Model:
    1. Fee Revenue: ONLY from post-OPO FoundUps (40%)
    2. Subscription Revenue: From all tier subscribers
    3. Angel Revenue: Subscriptions + OPO staking (20% treasury) + pass fees
    """

    config = GENESIS_STAKER_CONFIG
    projection = TenYearProjection(
        scenario=scenario,
        description=GROWTH_SCENARIOS[scenario]["description"],
        bootstrap_btc=bootstrap_btc,
        genesis_stakers=config["count"],
        genesis_stake_total_btc=config["count"] * config["avg_stake_btc"],
    )

    cumulative_btc = bootstrap_btc  # Start with bootstrap
    self_sustaining_reached = False
    previous_foundups = 0
    pre_opo_stock = 0
    post_opo_stock = 0

    for year in range(11):  # 0-10
        foundups = interpolate_growth(year, scenario)

        # Dynamic lifecycle stocks:
        # - New FoundUps enter pre-OPO by default.
        # - A bounded subset transitions pre->post via OPO annually.
        new_foundups = max(0, foundups - previous_foundups)
        pre_opo_stock += new_foundups

        angels = interpolate_angels(year, scenario)
        raw_opos = calculate_opos_per_year(foundups, year, pre_opo_foundups=pre_opo_stock)
        opo_capacity = calculate_opo_capacity(angels)
        opos_this_year = min(raw_opos, opo_capacity, pre_opo_stock)

        pre_opo_stock -= opos_this_year
        post_opo_stock += opos_this_year

        foundups_pre_opo = pre_opo_stock
        foundups_post_opo = post_opo_stock
        previous_foundups = foundups

        market_cfg = SCENARIO_MARKET_CONDITIONS[scenario]
        # Fee revenue: ONLY from post-OPO FoundUps
        # (Pre-OPO are invite-only, no public trading)
        volume_info = calculate_daily_volume(
            foundups,
            post_opo_only=True,
            foundups_post_opo=foundups_post_opo,
            cumulative_btc_reserve=cumulative_btc,
            market_demand_factor=market_cfg["demand_factor"],
            trades_per_foundup_per_day=market_cfg["trades_per_foundup_per_day"],
            active_trading_pct=market_cfg["active_trading_pct"],
            return_details=True,
        )
        daily_volume = float(volume_info["adjusted_daily_volume_usd"])
        daily_components = calculate_daily_fee_components(daily_volume, foundups_post_opo)
        daily_revenue = daily_components["total_usd"]

        # Fee revenue (DEX + exit + creation) - POST-OPO only
        daily_dex_btc = daily_components["dex_usd"] / BTC_PRICE_USD
        daily_exit_btc = daily_components["exit_usd"] / BTC_PRICE_USD
        daily_creation_btc = daily_components["creation_usd"] / BTC_PRICE_USD

        monthly_revenue_btc = (daily_revenue * 30) / BTC_PRICE_USD
        annual_fee_revenue_btc = (daily_revenue / BTC_PRICE_USD) * 365

        annual_fee_protocol_capture_btc = (
            daily_dex_btc * CAPTURE_RATES["dex_protocol"]
            + daily_exit_btc * CAPTURE_RATES["exit_protocol"]
            + daily_creation_btc * CAPTURE_RATES["creation_protocol"]
        ) * 365
        annual_fee_platform_capture_btc = (
            daily_dex_btc * CAPTURE_RATES["dex_platform"]
        ) * 365
        platform_capture_share = (
            annual_fee_platform_capture_btc / annual_fee_revenue_btc
            if annual_fee_revenue_btc > 0
            else 0.0
        )

        # Subscription revenue (stake-to-spend model)
        subscribers = interpolate_subscribers(year, scenario)
        sub_revenue = calculate_subscription_revenue(subscribers)
        annual_sub_revenue_btc = sub_revenue["gross_margin_btc"]

        # Angel revenue (separate from regular subscribers)
        angel_revenue = calculate_angel_revenue(angels, opos_this_year)

        # COMBINED revenue lanes
        annual_revenue_btc = (  # backward-compatible gross combined lane
            annual_fee_revenue_btc +
            annual_sub_revenue_btc +
            angel_revenue["total_btc"]
        )
        combined_revenue_btc = annual_revenue_btc
        combined_revenue_protocol_capture_btc = (
            annual_fee_protocol_capture_btc +
            annual_sub_revenue_btc +
            angel_revenue["total_btc"]
        )
        combined_revenue_platform_capture_btc = (
            annual_fee_platform_capture_btc +
            annual_sub_revenue_btc +
            angel_revenue["total_btc"]
        )

        # Operational costs
        operational_cost_btc = F0_MONTHLY_BURN_BTC * 12  # Annual

        # Net revenue (conservative: platform-capture lane)
        net_revenue_btc = combined_revenue_platform_capture_btc - operational_cost_btc
        combined_net_revenue_btc = combined_revenue_protocol_capture_btc - operational_cost_btc

        scenario_pack = evaluate_scenario_pack(
            daily_dex_fee_btc=daily_dex_btc,
            daily_exit_fee_btc=daily_exit_btc,
            daily_creation_fee_btc=daily_creation_btc,
            burn_btc=operational_cost_btc / 365,
            foundup_count=foundups_post_opo,
            network_pool_btc=max(1.0, cumulative_btc * 0.16),
            avg_trade_volume_sats=float(volume_info["avg_trade_sats"]),
            fee_rate=DEX_FEE_RATE,
        )
        downside = scenario_pack["downside"]
        base = scenario_pack["base"]
        upside = scenario_pack["upside"]

        downside_ratio_p10 = float(downside["revenue_cost_ratio_p10"]) * platform_capture_share
        base_ratio_p50 = float(base["revenue_cost_ratio_p50"]) * platform_capture_share
        upside_ratio_p90 = float(upside["revenue_cost_ratio_p90"]) * platform_capture_share

        # Cumulative BTC reserve (Hotel California - only grows)
        cumulative_btc += max(0, net_revenue_btc)

        # Self-sustainability check
        is_self_sustaining = net_revenue_btc > 0 and downside_ratio_p10 >= 1.0

        # Genesis staker ratio
        staker_ratio = calculate_genesis_staker_ratio(
            cumulative_btc, year,
            config["count"], config["avg_stake_btc"],
        )

        # F_i price multiple
        fi_price_multiple = 1 + math.log(1 + cumulative_btc / 10) * 2

        # Milestones
        milestones = []
        if year == 0:
            milestones.append("GENESIS")
        if is_self_sustaining and not self_sustaining_reached:
            milestones.append("SELF_SUSTAINING")
            self_sustaining_reached = True
        if staker_ratio >= 10 and year > 0:
            milestones.append("10X_RATIO")
        if staker_ratio >= 100 and year > 0:
            milestones.append("100X_RATIO")
        if foundups >= 1_000_000:
            milestones.append("1M_FOUNDUPS")
        if subscribers >= 1_000_000:
            milestones.append("1M_SUBSCRIBERS")
        if opos_this_year >= 1000:
            milestones.append("1K_OPOS_YEAR")
        if angels >= 1000:
            milestones.append("1K_ANGELS")

        snapshot = YearSnapshot(
            year=year,
            foundups=foundups,
            daily_volume_usd=daily_volume,
            daily_volume_raw_usd=float(volume_info["raw_daily_volume_usd"]),
            volume_effective_factor=float(volume_info["effective_volume_factor"]),
            slippage_bps=float(volume_info["slippage_bps"]),
            daily_revenue_usd=daily_revenue,
            monthly_revenue_btc=monthly_revenue_btc,
            annual_revenue_btc=annual_fee_revenue_btc,  # Fee revenue only (for backward compat)
            annual_revenue_protocol_capture_btc=annual_fee_protocol_capture_btc,
            annual_revenue_platform_capture_btc=annual_fee_platform_capture_btc,
            cumulative_btc_reserve=cumulative_btc,
            operational_cost_btc=operational_cost_btc,
            net_revenue_btc=net_revenue_btc,
            is_self_sustaining=is_self_sustaining,
            downside_revenue_cost_ratio_p10=downside_ratio_p10,
            base_revenue_cost_ratio_p50=base_ratio_p50,
            upside_revenue_cost_ratio_p90=upside_ratio_p90,
            genesis_staker_ratio=staker_ratio,
            f_i_price_multiple=fi_price_multiple,
            # Subscription metrics
            subscribers=subscribers,
            subscription_revenue_usd=sub_revenue["annual_usd"],
            subscription_revenue_btc=annual_sub_revenue_btc,
            combined_revenue_btc=combined_revenue_btc,
            combined_revenue_protocol_capture_btc=combined_revenue_protocol_capture_btc,
            combined_revenue_platform_capture_btc=combined_revenue_platform_capture_btc,
            combined_net_revenue_btc=combined_net_revenue_btc,
            milestones=milestones,
            # Pre-OPO vs Post-OPO lifecycle
            foundups_pre_opo=foundups_pre_opo,
            foundups_post_opo=foundups_post_opo,
            opos_this_year=opos_this_year,
            # Angel economics
            angels=angels,
            angel_subscription_btc=angel_revenue["subscription_btc"],
            angel_opo_staking_btc=angel_revenue["opo_staking_btc"],
            angel_pass_fees_btc=angel_revenue["pass_fees_btc"],
            angel_total_revenue_btc=angel_revenue["total_btc"],
        )
        projection.years.append(snapshot)

    return projection


def generate_all_projections() -> Dict[str, TenYearProjection]:
    """Generate projections for all scenarios."""
    projections = {}

    for scenario in GROWTH_SCENARIOS:
        for bootstrap_name, bootstrap_config in BOOTSTRAP_SCENARIOS.items():
            key = f"{scenario}_{bootstrap_name}"
            projections[key] = generate_projection(
                scenario=scenario,
                bootstrap_btc=bootstrap_config["btc"],
            )

    return projections


def export_for_animation(projections: Dict[str, TenYearProjection]) -> Dict:
    """Export projections as JSON-serializable dict for animation."""

    output = {
        "generated_at": "2026-02-17",
        "btc_price_assumption": BTC_PRICE_USD,
        "capture_rates": CAPTURE_RATES,
        "market_conditions": SCENARIO_MARKET_CONDITIONS,
        "genesis_staker_config": GENESIS_STAKER_CONFIG,
        "subscription_config": {
            "tiers": SUBSCRIPTION_TIERS,
            "arpu": round(SUBSCRIPTION_ARPU, 2),
            "gross_margin": SUBSCRIPTION_GROSS_MARGIN,
        },
        "angel_config": ANGEL_TIER_CONFIG,
        "lifecycle_config": {
            "pre_opo_tier_pct": PRE_OPO_TIER_PCT,
            "post_opo_tier_pct": POST_OPO_TIER_PCT,
            "opo_conversion_rates": OPO_MONTHLY_CONVERSION_RATE,
        },
        "compute_graph": build_compute_graph_payload(
            model_tier="opus",
            agents_assigned=10,
            tokens_per_agent_epoch=1000,
            cabr_v3_score=0.65,
            base_fi_rate=1.0,
        ),
        "scenarios": {},
    }

    for key, proj in projections.items():
        output["scenarios"][key] = {
            "scenario": proj.scenario,
            "description": proj.description,
            "bootstrap_btc": proj.bootstrap_btc,
            "genesis_stakers": proj.genesis_stakers,
            "genesis_stake_total_btc": proj.genesis_stake_total_btc,
            "years": [
                {
                    "year": y.year,
                    "foundups": y.foundups,
                    "daily_volume_usd": round(y.daily_volume_usd, 2),
                    "daily_volume_raw_usd": round(y.daily_volume_raw_usd, 2),
                    "volume_effective_factor": round(y.volume_effective_factor, 4),
                    "slippage_bps": round(y.slippage_bps, 2),
                    "daily_revenue_usd": round(y.daily_revenue_usd, 2),
                    "monthly_revenue_btc": round(y.monthly_revenue_btc, 4),
                    "annual_revenue_btc": round(y.annual_revenue_btc, 4),
                    "annual_revenue_protocol_capture_btc": round(y.annual_revenue_protocol_capture_btc, 4),
                    "annual_revenue_platform_capture_btc": round(y.annual_revenue_platform_capture_btc, 4),
                    "cumulative_btc_reserve": round(y.cumulative_btc_reserve, 4),
                    "operational_cost_btc": round(y.operational_cost_btc, 4),
                    "net_revenue_btc": round(y.net_revenue_btc, 4),
                    "is_self_sustaining": y.is_self_sustaining,
                    "downside_revenue_cost_ratio_p10": round(y.downside_revenue_cost_ratio_p10, 4),
                    "base_revenue_cost_ratio_p50": round(y.base_revenue_cost_ratio_p50, 4),
                    "upside_revenue_cost_ratio_p90": round(y.upside_revenue_cost_ratio_p90, 4),
                    "genesis_staker_ratio": round(y.genesis_staker_ratio, 2),
                    "f_i_price_multiple": round(y.f_i_price_multiple, 2),
                    # Subscription metrics
                    "subscribers": y.subscribers,
                    "subscription_revenue_usd": round(y.subscription_revenue_usd, 2),
                    "subscription_revenue_btc": round(y.subscription_revenue_btc, 4),
                    "combined_revenue_btc": round(y.combined_revenue_btc, 4),
                    "combined_revenue_protocol_capture_btc": round(y.combined_revenue_protocol_capture_btc, 4),
                    "combined_revenue_platform_capture_btc": round(y.combined_revenue_platform_capture_btc, 4),
                    "combined_net_revenue_btc": round(y.combined_net_revenue_btc, 4),
                    "milestones": y.milestones,
                    # Pre-OPO vs Post-OPO lifecycle
                    "foundups_pre_opo": y.foundups_pre_opo,
                    "foundups_post_opo": y.foundups_post_opo,
                    "opos_this_year": y.opos_this_year,
                    # Angel economics
                    "angels": y.angels,
                    "angel_subscription_btc": round(y.angel_subscription_btc, 4),
                    "angel_opo_staking_btc": round(y.angel_opo_staking_btc, 4),
                    "angel_pass_fees_btc": round(y.angel_pass_fees_btc, 4),
                    "angel_total_revenue_btc": round(y.angel_total_revenue_btc, 4),
                }
                for y in proj.years
            ],
        }

    return output


def print_projection(proj: TenYearProjection) -> None:
    """Print a formatted projection table with pre-OPO/post-OPO lifecycle."""
    print(f"\n{'='*140}")
    print(f"10-YEAR PROJECTION: {proj.scenario.upper()} + {proj.bootstrap_btc} BTC Bootstrap")
    print(f"{'='*140}")
    print(f"Description: {proj.description}")
    print(f"Genesis Stakers: {proj.genesis_stakers} @ {proj.genesis_stake_total_btc/proj.genesis_stakers:.1f} BTC each")
    print()

    # Lifecycle explanation
    print("LIFECYCLE: Pre-OPO (60% F0_DAE) = Angels only | Post-OPO (40% F1+) = Public fees")
    print("-" * 140)

    print(f"{'Yr':>3} {'Total':>8} {'PreOPO':>7} {'PostOPO':>7} {'Angels':>6} "
          f"{'FeeGross':>8} {'FeeProt':>8} {'SubRev':>8} {'AngelRev':>8} {'NetPlat':>8} {'Reserve':>9} {'Ratio':>6} {'Status':>15}")
    print("-" * 140)

    for y in proj.years:
        status = "SURPLUS" if y.is_self_sustaining else "DEFICIT"
        if y.milestones:
            status = y.milestones[0][:15]  # First milestone, truncated

        print(f"{y.year:>3} {y.foundups:>8,} {y.foundups_pre_opo:>7,} {y.foundups_post_opo:>7,} {y.angels:>6,} "
              f"{y.annual_revenue_btc:>8,.1f} {y.annual_revenue_protocol_capture_btc:>8,.1f} "
              f"{y.subscription_revenue_btc:>7,.1f} {y.angel_total_revenue_btc:>7,.2f} {y.net_revenue_btc:>8,.1f} "
              f"{y.cumulative_btc_reserve:>8,.1f} {y.genesis_staker_ratio:>5.1f}x {status:>15}")

    print()
    final = proj.years[-1]
    print(f"YEAR 10 SUMMARY:")
    print(f"  ECOSYSTEM:")
    print(f"    Total FoundUps:     {final.foundups:,}")
    print(f"    Pre-OPO (F0_DAE):   {final.foundups_pre_opo:,} (invite-only)")
    print(f"    Post-OPO (F1+):     {final.foundups_post_opo:,} (public)")
    print(f"    OPOs this year:     {final.opos_this_year:,}")
    print()
    print(f"  USERS:")
    print(f"    Subscribers:        {final.subscribers:,}")
    print(f"    Angels:             {final.angels:,} ($195/month)")
    print()
    print(f"  REVENUE (BTC/year):")
    print(f"    Fee Revenue:        {final.annual_revenue_btc:,.1f} BTC (from post-OPO only)")
    print(f"    Fee Protocol Cap:   {final.annual_revenue_protocol_capture_btc:,.1f} BTC")
    print(f"    Fee Platform Cap:   {final.annual_revenue_platform_capture_btc:,.1f} BTC")
    print(f"    Subscription Rev:   {final.subscription_revenue_btc:,.1f} BTC")
    print(f"    Angel Revenue:      {final.angel_total_revenue_btc:,.2f} BTC")
    print(f"      - Subscriptions:  {final.angel_subscription_btc:,.2f} BTC")
    print(f"      - OPO Staking:    {final.angel_opo_staking_btc:,.2f} BTC (20% treasury)")
    print(f"      - Pass Fees:      {final.angel_pass_fees_btc:,.3f} BTC")
    print(f"    COMBINED:           {final.combined_revenue_btc:,.1f} BTC/year")
    print(f"    COMBINED (Protocol):{final.combined_revenue_protocol_capture_btc:,.1f} BTC/year")
    print(f"    COMBINED (Platform):{final.combined_revenue_platform_capture_btc:,.1f} BTC/year")
    print(f"    NET (Platform):     {final.net_revenue_btc:,.1f} BTC/year")
    print(f"    Downside p10 Ratio: {final.downside_revenue_cost_ratio_p10:.2f}x")
    print()
    print(f"  METRICS:")
    print(f"    BTC Reserve:        {final.cumulative_btc_reserve:,.1f} BTC (${final.cumulative_btc_reserve * 100_000:,.0f})")
    print(f"    Genesis Ratio:      {final.genesis_staker_ratio:.1f}x")
    print(f"    F_i Price Multiple: {final.f_i_price_multiple:.1f}x")


def main():
    """Generate and display 10-year projections."""

    # Generate key scenarios
    scenarios = [
        ("baseline", 50),      # Most likely
        ("conservative", 50),   # Bear case
        ("openclaw", 120),      # Bull case
    ]

    for scenario, bootstrap in scenarios:
        proj = generate_projection(scenario, bootstrap)
        print_projection(proj)

    # Export all projections to JSON
    all_projections = generate_all_projections()
    output = export_for_animation(all_projections)

    # Write to file for animation
    output_path = "public/data/ten_year_projection.json"
    try:
        with open(output_path, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nExported projection data to: {output_path}")
    except Exception as e:
        print(f"\nCould not write to {output_path}: {e}")
        print("JSON data structure ready for animation integration.")

    print("\n" + "=" * 140)
    print("LITEPAPER ANIMATION DATA READY - PRE-OPO / POST-OPO LIFECYCLE MODEL")
    print("=" * 140)

    # Get Y10 data for each scenario
    cons_y10 = output['scenarios']['conservative_conservative']['years'][-1]
    base_y10 = output['scenarios']['baseline_conservative']['years'][-1]
    oclaw_y10 = output['scenarios']['openclaw_comfortable']['years'][-1]

    print(f"""
KEY INSIGHTS FOR ANIMATION:

1. FOUNDUPS LIFECYCLE (Pre-OPO vs Post-OPO)
   ┌─────────────┬──────────┬──────────┬───────────┬──────────┐
   │ Scenario    │ Total    │ Pre-OPO  │ Post-OPO  │ OPOs/yr  │
   ├─────────────┼──────────┼──────────┼───────────┼──────────┤
   │ Conservative│ {cons_y10['foundups']:>8,} │ {cons_y10['foundups_pre_opo']:>8,} │ {cons_y10['foundups_post_opo']:>9,} │ {cons_y10['opos_this_year']:>8,} │
   │ Baseline    │ {base_y10['foundups']:>8,} │ {base_y10['foundups_pre_opo']:>8,} │ {base_y10['foundups_post_opo']:>9,} │ {base_y10['opos_this_year']:>8,} │
   │ OpenClaw    │ {oclaw_y10['foundups']:>8,} │ {oclaw_y10['foundups_pre_opo']:>8,} │ {oclaw_y10['foundups_post_opo']:>9,} │ {oclaw_y10['opos_this_year']:>8,} │
   └─────────────┴──────────┴──────────┴───────────┴──────────┘

2. USERS: SUBSCRIBERS + ANGELS
   ┌─────────────┬──────────────┬──────────┐
   │ Scenario    │ Subscribers  │ Angels   │
   ├─────────────┼──────────────┼──────────┤
   │ Conservative│ {cons_y10['subscribers']:>12,} │ {cons_y10['angels']:>8,} │
   │ Baseline    │ {base_y10['subscribers']:>12,} │ {base_y10['angels']:>8,} │
   │ OpenClaw    │ {oclaw_y10['subscribers']:>12,} │ {oclaw_y10['angels']:>8,} │
   └─────────────┴──────────────┴──────────┘

3. REVENUE BREAKDOWN (BTC/year at Y10)
   ┌─────────────┬─────────┬─────────┬──────────┬──────────┐
   │ Scenario    │ Fees    │ Subs    │ Angels   │ COMBINED │
   ├─────────────┼─────────┼─────────┼──────────┼──────────┤
   │ Conservative│ {cons_y10['annual_revenue_btc']:>7,.1f} │ {cons_y10['subscription_revenue_btc']:>7,.1f} │ {cons_y10['angel_total_revenue_btc']:>8,.2f} │ {cons_y10['combined_revenue_btc']:>8,.1f} │
   │ Baseline    │ {base_y10['annual_revenue_btc']:>7,.1f} │ {base_y10['subscription_revenue_btc']:>7,.1f} │ {base_y10['angel_total_revenue_btc']:>8,.2f} │ {base_y10['combined_revenue_btc']:>8,.1f} │
   │ OpenClaw    │ {oclaw_y10['annual_revenue_btc']:>7,.1f} │ {oclaw_y10['subscription_revenue_btc']:>7,.1f} │ {oclaw_y10['angel_total_revenue_btc']:>8,.2f} │ {oclaw_y10['combined_revenue_btc']:>8,.1f} │
   └─────────────┴─────────┴─────────┴──────────┴──────────┘

   NOTE: Fee revenue ONLY from post-OPO FoundUps (40%)
         Pre-OPO FoundUps (60%) generate Angel revenue only

4. ANGEL REVENUE BREAKDOWN (Y10)
   Angels are the ONLY gateway to pre-OPO FoundUps
   - Subscription: $195/month × angels × 12
   - OPO Staking:  20% treasury fee on all Angel stakes
   - Pass Fees:    100K UPS when Angel passes on OPO

   Conservative: {cons_y10['angel_subscription_btc']:.2f} sub + {cons_y10['angel_opo_staking_btc']:.2f} OPO + {cons_y10['angel_pass_fees_btc']:.3f} pass = {cons_y10['angel_total_revenue_btc']:.2f} BTC
   Baseline:     {base_y10['angel_subscription_btc']:.2f} sub + {base_y10['angel_opo_staking_btc']:.2f} OPO + {base_y10['angel_pass_fees_btc']:.3f} pass = {base_y10['angel_total_revenue_btc']:.2f} BTC
   OpenClaw:     {oclaw_y10['angel_subscription_btc']:.2f} sub + {oclaw_y10['angel_opo_staking_btc']:.2f} OPO + {oclaw_y10['angel_pass_fees_btc']:.3f} pass = {oclaw_y10['angel_total_revenue_btc']:.2f} BTC

5. BTC RESERVE (Hotel California)
   - Conservative Y10: {cons_y10['cumulative_btc_reserve']:,.0f} BTC (${cons_y10['cumulative_btc_reserve']*100000:,.0f})
   - Baseline Y10:     {base_y10['cumulative_btc_reserve']:,.0f} BTC (${base_y10['cumulative_btc_reserve']*100000:,.0f})
   - OpenClaw Y10:     {oclaw_y10['cumulative_btc_reserve']:,.0f} BTC (${oclaw_y10['cumulative_btc_reserve']*100000:,.0f})

6. GENESIS STAKER DISTRIBUTION RATIOS
   - Conservative Y10: {cons_y10['genesis_staker_ratio']:.1f}x
   - Baseline Y10:     {base_y10['genesis_staker_ratio']:.1f}x
   - OpenClaw Y10:     {oclaw_y10['genesis_staker_ratio']:.1f}x

ANIMATION RECOMMENDATION:
- Interactive timeline slider (Y0-Y10)
- Switchable scenarios (Conservative/Baseline/OpenClaw)
- THREE revenue streams: Fees (purple) + Subscriptions (orange) + Angels (gold)
- FoundUp split: Pre-OPO (dim) vs Post-OPO (bright)
- OPO burst effects when FoundUps transition
- Angel count as separate metric (accredited badge)
- Milestone markers (1K_OPOS, 1K_ANGELS, 1M_SUBSCRIBERS)
""")


if __name__ == "__main__":
    main()
