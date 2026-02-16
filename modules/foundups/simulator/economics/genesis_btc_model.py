"""Genesis BTC Model - 1 BTC Seeds the System.

GOAL: Model what happens when 1 BTC enters the FoundUps ecosystem.

EXPLICIT ASSUMPTIONS (need 012 validation):
1. F_i minting is driven by AGENT WORK (0102 task completion)
2. BTC backing determines UP$ capacity
3. Stakers earn F_i from Du pool (passive)
4. F_i/BTC ratio is DERIVED from actual economics, not set arbitrarily

KEY QUESTION: With 1 BTC reserve, what returns can stakers expect?
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class GenesisConfig:
    """Configuration for genesis BTC model.

    EXPLICIT ASSUMPTIONS - each needs 012 validation.
    """

    # === BTC STAKING ===
    total_btc_staked: float = 1.0          # Genesis goal: 1 BTC
    num_stakers: int = 100                  # 100 stakers cap
    # Implied: avg_stake = 0.01 BTC ($1k at $100k BTC)

    # === F_i MINTING (THE BIG UNKNOWN) ===
    # Option A: TIME-BASED (like Bitcoin)
    #   - Fixed F_i per block/epoch regardless of activity
    #   - Pro: Predictable, scarcity enforced
    #   - Con: No connection to actual work

    # Option B: WORK-BASED (current assumption)
    #   - F_i minted per 3V task completion
    #   - Pro: Rewards actual contribution
    #   - Con: Unpredictable rate, could be gamed

    # Option C: BTC-BACKED CAPACITY
    #   - F_i release rate = f(BTC reserve)
    #   - More BTC staked → more F_i can be minted
    #   - Pro: Direct backing relationship
    #   - Con: Complex, needs careful design

    fi_minting_model: str = "btc_backed"  # "time_based", "work_based", "btc_backed"

    # === BTC-BACKED MODEL PARAMETERS ===
    # If fi_minting_model == "btc_backed":
    # fi_capacity = btc_reserve × btc_to_fi_multiplier
    # This sets how much F_i the BTC can "back"
    btc_to_fi_multiplier: float = 1_000_000  # 1 BTC backs 1M F_i

    # Release rate: how fast F_i is released from capacity
    # S-curve based on adoption score
    fi_release_rate_pct: float = 0.10  # 10% of capacity per year at current adoption

    # === TIME PARAMETERS ===
    epochs_per_year: int = 365           # 1 epoch/day
    simulation_years: int = 5            # 5-year projection

    # === DU POOL PARAMETERS (from WSP 26) ===
    du_pool_pct: float = 0.04            # 4% of F_i to Du pool
    du_tier_share: float = 0.80          # 80% to du tier (new stakers)

    @property
    def avg_stake_btc(self) -> float:
        return self.total_btc_staked / self.num_stakers

    @property
    def fi_capacity_total(self) -> float:
        """Total F_i that can be minted with current BTC backing."""
        return self.total_btc_staked * self.btc_to_fi_multiplier

    @property
    def fi_released_per_year(self) -> float:
        """F_i released per year based on release rate."""
        return self.fi_capacity_total * self.fi_release_rate_pct

    @property
    def fi_per_epoch(self) -> float:
        """F_i released per epoch."""
        return self.fi_released_per_year / self.epochs_per_year


@dataclass
class YearlyProjection:
    """Projection for a single year."""

    year: int
    fi_released_cumulative: float
    fi_to_du_pool: float
    fi_per_staker: float
    fi_per_staker_cumulative: float
    btc_value_of_fi: float
    roi_multiple: float


def calculate_fi_btc_rate(
    btc_reserve: float,
    fi_released: float,
) -> float:
    """Calculate F_i to BTC rate based on backing ratio.

    This is the DERIVED rate, not an arbitrary assumption.

    rate = btc_reserve / fi_released

    Early: More BTC, less F_i released → high rate (each F_i worth more)
    Late: Same BTC, more F_i released → lower rate (dilution)

    BUT: If BTC reserve grows (fees, new stakes), rate can stay stable or increase.
    """
    if fi_released <= 0:
        return 0.0
    return btc_reserve / fi_released


@dataclass
class BTCInflowConfig:
    """Configuration for ongoing BTC inflows.

    THE CRITICAL MISSING PIECE:
    If BTC reserve grows faster than F_i release, value appreciates.
    """

    # Subscription revenue (monthly, converted to BTC)
    subscribers_year_1: int = 100
    subscribers_year_5: int = 10000
    avg_subscription_usd: float = 10.0  # Mix of tiers
    btc_price_usd: float = 100000.0

    # Trading fees (% of trade volume → BTC)
    trading_volume_pct_of_fi: float = 0.20  # 20% of F_i trades annually
    trading_fee_pct: float = 0.02           # 2% fee

    # Exit fees (% of exits → BTC)
    exit_rate_pct: float = 0.05             # 5% of F_i exits per year
    exit_fee_pct: float = 0.10              # 10% fee on exit

    def subscribers_at_year(self, year: int) -> int:
        """S-curve subscriber growth."""
        # Linear interpolation for now
        return int(self.subscribers_year_1 + (self.subscribers_year_5 - self.subscribers_year_1) * (year - 1) / 4)

    def subscription_btc_per_year(self, year: int) -> float:
        """BTC from subscriptions."""
        subs = self.subscribers_at_year(year)
        usd_revenue = subs * self.avg_subscription_usd * 12
        return usd_revenue / self.btc_price_usd


def run_genesis_model(
    config: GenesisConfig,
    btc_inflows: BTCInflowConfig = None,
) -> Dict:
    """Run the genesis BTC model simulation.

    Shows year-by-year projection of staker returns.

    KEY INSIGHT: ROI depends on BTC reserve growth vs F_i release rate.
    - If BTC grows faster → F_i appreciates
    - If F_i releases faster → F_i dilutes
    """
    if btc_inflows is None:
        btc_inflows = BTCInflowConfig()

    results = {
        "config": {
            "total_btc": config.total_btc_staked,
            "num_stakers": config.num_stakers,
            "avg_stake": config.avg_stake_btc,
            "fi_capacity": config.fi_capacity_total,
            "fi_per_epoch": config.fi_per_epoch,
            "minting_model": config.fi_minting_model,
        },
        "projections": [],
    }

    fi_released_cumulative = 0.0
    fi_per_staker_cumulative = 0.0
    btc_reserve = config.total_btc_staked  # Start with staked BTC

    for year in range(1, config.simulation_years + 1):
        # F_i released this year
        fi_this_year = config.fi_released_per_year
        fi_released_cumulative += fi_this_year

        # === BTC INFLOWS (the value creation engine) ===
        btc_from_subs = btc_inflows.subscription_btc_per_year(year)
        btc_from_trading = fi_released_cumulative * btc_inflows.trading_volume_pct_of_fi * btc_inflows.trading_fee_pct * (btc_reserve / fi_released_cumulative if fi_released_cumulative > 0 else 0)
        btc_from_exits = fi_released_cumulative * btc_inflows.exit_rate_pct * btc_inflows.exit_fee_pct * (btc_reserve / fi_released_cumulative if fi_released_cumulative > 0 else 0)

        btc_inflow_this_year = btc_from_subs + btc_from_trading + btc_from_exits
        btc_reserve += btc_inflow_this_year

        # F_i to Du pool (4%)
        fi_to_du = fi_this_year * config.du_pool_pct

        # F_i to du tier (80% of Du pool)
        fi_to_du_tier = fi_to_du * config.du_tier_share

        # F_i per staker (divided by count)
        fi_per_staker = fi_to_du_tier / config.num_stakers
        fi_per_staker_cumulative += fi_per_staker

        # F_i to BTC rate (DERIVED from backing ratio)
        # This is where value appreciation happens!
        fi_btc_rate = calculate_fi_btc_rate(
            btc_reserve,  # NOW includes inflows!
            fi_released_cumulative,
        )

        # BTC value of staker's F_i
        btc_value = fi_per_staker_cumulative * fi_btc_rate

        # ROI multiple
        roi = btc_value / config.avg_stake_btc if config.avg_stake_btc > 0 else 0

        projection = YearlyProjection(
            year=year,
            fi_released_cumulative=fi_released_cumulative,
            fi_to_du_pool=fi_to_du,
            fi_per_staker=fi_per_staker,
            fi_per_staker_cumulative=fi_per_staker_cumulative,
            btc_value_of_fi=btc_value,
            roi_multiple=roi,
        )
        results["projections"].append(projection)

        # Store BTC reserve for reporting
        if "btc_reserve_history" not in results:
            results["btc_reserve_history"] = []
        results["btc_reserve_history"].append({
            "year": year,
            "btc_reserve": btc_reserve,
            "btc_inflow": btc_inflow_this_year,
            "fi_btc_rate": fi_btc_rate,
        })

    return results


def print_genesis_analysis():
    """Print comprehensive genesis BTC analysis."""
    print("\n" + "=" * 80)
    print("GENESIS BTC MODEL - 1 BTC SEEDS THE SYSTEM")
    print("(WITH BTC INFLOWS - THE VALUE CREATION ENGINE)")
    print("=" * 80)

    print("\n### EXPLICIT ASSUMPTIONS (need 012 validation)")
    print("-" * 60)

    # Default config
    config = GenesisConfig()
    btc_inflows = BTCInflowConfig()

    print(f"""
BTC STAKING (Genesis):
  Total BTC staked: {config.total_btc_staked} BTC (${config.total_btc_staked * 100000:,.0f} at $100k)
  Number of stakers: {config.num_stakers}
  Average stake: {config.avg_stake_btc} BTC (${config.avg_stake_btc * 100000:,.0f})

F_i MINTING MODEL: {config.fi_minting_model.upper()}
  BTC-to-F_i multiplier: {config.btc_to_fi_multiplier:,}
    → 1 BTC backs {config.btc_to_fi_multiplier:,} F_i capacity
  Release rate: {config.fi_release_rate_pct * 100:.0f}% per year
    → {config.fi_released_per_year:,.0f} F_i released annually

BTC INFLOWS (value creation):
  Subscriptions: {btc_inflows.subscribers_year_1} → {btc_inflows.subscribers_year_5} subs over 5 years
  Avg subscription: ${btc_inflows.avg_subscription_usd}/month
  Trading fees: {btc_inflows.trading_fee_pct * 100:.0f}% on {btc_inflows.trading_volume_pct_of_fi * 100:.0f}% volume
  Exit fees: {btc_inflows.exit_fee_pct * 100:.0f}% on {btc_inflows.exit_rate_pct * 100:.0f}% exits

DU POOL (from WSP 26):
  Du pool: {config.du_pool_pct * 100:.0f}% of F_i minted
  Du tier share: {config.du_tier_share * 100:.0f}% of Du pool
    → {config.du_pool_pct * config.du_tier_share * 100:.1f}% of total F_i to du-tier stakers
""")

    # Run simulation WITH inflows
    results = run_genesis_model(config, btc_inflows)

    print("\n### 5-YEAR PROJECTION (WITH BTC INFLOWS)")
    print("-" * 80)
    print(f"{'Year':>4} | {'BTC Reserve':>12} | {'F_i Rate':>12} | {'F_i/Staker':>12} | {'BTC Value':>12} | {'ROI':>8}")
    print("-" * 80)

    for i, proj in enumerate(results["projections"]):
        btc_hist = results["btc_reserve_history"][i]
        print(
            f"{proj.year:>4} | "
            f"{btc_hist['btc_reserve']:>12.4f} | "
            f"{btc_hist['fi_btc_rate']:>12.8f} | "
            f"{proj.fi_per_staker_cumulative:>12,.0f} | "
            f"{proj.btc_value_of_fi:>12.6f} | "
            f"{proj.roi_multiple:>7.2f}x"
        )

    # Final analysis
    final = results["projections"][-1]
    final_btc = results["btc_reserve_history"][-1]
    print(f"""
RESULT ANALYSIS (WITH INFLOWS):
  BTC Reserve Growth: {config.total_btc_staked:.4f} → {final_btc['btc_reserve']:.4f} BTC ({final_btc['btc_reserve']/config.total_btc_staked:.1f}x)
  F_i/BTC Rate: Increases as BTC grows faster than F_i release

  After {config.simulation_years} years, each staker has:
    - {final.fi_per_staker_cumulative:,.0f} F_i accumulated
    - Worth {final.btc_value_of_fi:.6f} BTC
    - ROI: {final.roi_multiple:.2f}x on {config.avg_stake_btc} BTC stake

KEY INSIGHT:
  - Initial model (no inflows): 0.03x ROI (zero-sum)
  - With subscription/fee inflows: {final.roi_multiple:.2f}x ROI (value creation)
  - BTC inflows are THE engine that makes returns possible!
""")

    # Sensitivity analysis
    print("\n### SENSITIVITY: VARYING BTC-to-F_i MULTIPLIER")
    print("-" * 60)
    print("What if we change how much F_i 1 BTC can back?")
    print()

    for mult in [100_000, 500_000, 1_000_000, 5_000_000, 10_000_000]:
        test_config = GenesisConfig(btc_to_fi_multiplier=mult)
        test_results = run_genesis_model(test_config)
        final_proj = test_results["projections"][-1]
        print(
            f"  1 BTC backs {mult:>12,} F_i → "
            f"5yr ROI = {final_proj.roi_multiple:>6.2f}x, "
            f"F_i/staker = {final_proj.fi_per_staker_cumulative:>10,.0f}"
        )

    print("\n### SENSITIVITY: VARYING STAKER COUNT")
    print("-" * 60)
    print("What if more/fewer stakers share the pool?")
    print()

    for num in [10, 25, 50, 100, 250, 500]:
        test_config = GenesisConfig(num_stakers=num)
        test_results = run_genesis_model(test_config)
        final_proj = test_results["projections"][-1]
        print(
            f"  {num:>4} stakers (${test_config.avg_stake_btc * 100000:>6,.0f} each) → "
            f"5yr ROI = {final_proj.roi_multiple:>6.2f}x"
        )

    print("\n### SENSITIVITY: VARYING RELEASE RATE")
    print("-" * 60)
    print("What if F_i releases faster/slower?")
    print()

    for rate in [0.05, 0.10, 0.20, 0.50]:
        test_config = GenesisConfig(fi_release_rate_pct=rate)
        test_results = run_genesis_model(test_config)
        final_proj = test_results["projections"][-1]
        print(
            f"  {rate * 100:>3.0f}% release/year → "
            f"5yr ROI = {final_proj.roi_multiple:>6.2f}x, "
            f"F_i/staker = {final_proj.fi_per_staker_cumulative:>10,.0f}"
        )


def identify_unknowns():
    """Print what we need to decide/research."""
    print("\n" + "=" * 80)
    print("WHAT WE NEED TO DECIDE (012 INPUT REQUIRED)")
    print("=" * 80)

    print("""
1. F_i MINTING MODEL - Which one?

   A) TIME-BASED (Bitcoin-style)
      - Fixed F_i per epoch regardless of activity
      - Pro: Predictable, enforces scarcity
      - Con: No connection to work

   B) WORK-BASED (current assumption)
      - F_i minted per 3V task completion
      - Pro: Rewards contribution
      - Con: Unpredictable, gameable

   C) BTC-BACKED CAPACITY (this model)
      - F_i capacity = BTC reserve × multiplier
      - Release rate follows S-curve
      - Pro: Direct backing, self-regulating
      - Con: Needs multiplier decision

2. BTC-to-F_i MULTIPLIER

   How much F_i should 1 BTC be able to back?

   - 100,000 F_i/BTC → Very scarce, high per-F_i value
   - 1,000,000 F_i/BTC → Moderate (current default)
   - 10,000,000 F_i/BTC → Abundant, lower per-F_i value

   Trade-off: Scarcity vs Liquidity

3. RELEASE RATE

   How fast should F_i be released from capacity?

   - 5%/year → Slow, Bitcoin-like halving feel
   - 10%/year → Moderate (current default)
   - 20%/year → Faster ecosystem bootstrapping

   Trade-off: Early rewards vs Long-term scarcity

4. STAKER CAP

   How many stakers in genesis cohort?

   - 10-25 → Exclusive, high individual returns
   - 100 → Balanced (current default)
   - 500+ → Broader access, lower individual returns

   Trade-off: Exclusivity vs Community

5. MINIMUM STAKE

   What's the floor to participate?

   - 0.001 BTC (~$100) → Accessible
   - 0.01 BTC (~$1k) → Committed
   - 0.1 BTC (~$10k) → Serious investor

   Trade-off: Accessibility vs Quality of stakers
""")


if __name__ == "__main__":
    print_genesis_analysis()
    identify_unknowns()
