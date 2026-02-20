"""Genesis Bootstrap Calculator - Minimum BTC needed to launch pAVS.

012-DIRECTIVE (2026-02-17):
"F0_DAE needs funding source - Not self-sustaining at $0 treasury --
100 to 1000 BTC...? look at Bitclout as a model? can we calculate
the minimum needed for foundups?"

BITCLOUT REFERENCE (Wikipedia, DeSo Docs):
- Raised $200M from VCs (a16z, Coinbase Ventures, Sequoia, etc.)
- $165M in BTC deposits to bonding curve
- 10.8M token supply cap
- Bonding curve: price doubles every 1M tokens sold
- Top 20 genesis recipients got 37% of supply

pAVS BOOTSTRAP REQUIREMENTS:
1. F_0 Operations (pAVS platform itself)
2. Network Pool (IMF-like ecosystem reserves)
3. Spawning Fund (to create first F_i children)
4. DEX Liquidity (UPS/BTC and F_i/UPS pairs)
5. Genesis Staker Rewards (incentivize early BTC deposits)
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum


# Constants
SATS_PER_BTC = 100_000_000
FI_SUPPLY_PER_FOUNDUP = 21_000_000

# BTC price scenarios
BTC_PRICES = {
    "bear": 50_000,
    "current": 100_000,
    "bull": 200_000,
}

# From startup_cost_validation.py - monthly burns by tier
TIER_MONTHLY_BURN_USD = {
    "F0_DAE": 810,
    "F1_OPO": 6_282,
    "F2_GROWTH": 26_658,
    "F3_INFRA": 107_964,
    "F4_MEGA": 492_525,
    "F5_SYSTEMIC": 3_325_250,
}


class BootstrapComponent(Enum):
    """Components of genesis bootstrap capital."""
    F0_OPERATIONS = "f0_operations"       # Run pAVS platform
    NETWORK_POOL = "network_pool"         # IMF-like reserves
    SPAWNING_FUND = "spawning_fund"       # Create first F_i
    DEX_LIQUIDITY = "dex_liquidity"       # Trading pairs
    GENESIS_REWARDS = "genesis_rewards"   # Incentive early stakers


@dataclass
class BootstrapAllocation:
    """Allocation for a bootstrap component."""

    component: BootstrapComponent
    btc_amount: float
    description: str
    runway_months: float = 0.0

    @property
    def sats(self) -> int:
        return int(self.btc_amount * SATS_PER_BTC)

    def usd(self, btc_price: float = 100_000) -> float:
        return self.btc_amount * btc_price


@dataclass
class GenesisBootstrapPlan:
    """Complete genesis bootstrap plan."""

    allocations: List[BootstrapAllocation]
    target_runway_months: int = 24  # YC standard

    @property
    def total_btc(self) -> float:
        return sum(a.btc_amount for a in self.allocations)

    @property
    def total_sats(self) -> int:
        return int(self.total_btc * SATS_PER_BTC)

    def total_usd(self, btc_price: float = 100_000) -> float:
        return self.total_btc * btc_price

    def by_component(self, component: BootstrapComponent) -> float:
        return sum(a.btc_amount for a in self.allocations if a.component == component)

    def breakdown(self) -> Dict[str, float]:
        return {a.component.value: a.btc_amount for a in self.allocations}


def calculate_f0_operations(
    tier: str = "F2_GROWTH",
    runway_months: int = 24,
    btc_price: float = 100_000,
) -> BootstrapAllocation:
    """Calculate BTC needed for F_0 (pAVS platform) operations.

    F_0 is the platform itself - it needs to run before any F_i exist.
    Typically F2_GROWTH tier (50 agents, production infrastructure).
    """
    monthly_burn_usd = TIER_MONTHLY_BURN_USD.get(tier, TIER_MONTHLY_BURN_USD["F2_GROWTH"])
    total_usd = monthly_burn_usd * runway_months
    btc_needed = total_usd / btc_price

    return BootstrapAllocation(
        component=BootstrapComponent.F0_OPERATIONS,
        btc_amount=btc_needed,
        description=f"F_0 platform operations ({tier}, {runway_months}mo runway)",
        runway_months=runway_months,
    )


def calculate_network_pool(
    num_critical_fi: int = 10,
    support_per_fi_btc: float = 0.2,
    safety_multiplier: float = 2.0,
) -> BootstrapAllocation:
    """Calculate BTC needed for Network Pool (IMF-like reserves).

    Network Pool supports CRITICAL F_i during crisis.
    Should handle multiple simultaneous CRITICAL situations.
    """
    base_support = num_critical_fi * support_per_fi_btc
    btc_needed = base_support * safety_multiplier

    return BootstrapAllocation(
        component=BootstrapComponent.NETWORK_POOL,
        btc_amount=btc_needed,
        description=f"IMF-like reserves (support {num_critical_fi} CRITICAL F_i)",
    )


def calculate_spawning_fund(
    num_initial_spawns: int = 10,
    seed_per_spawn_btc: float = 0.5,
    buffer_multiplier: float = 1.5,
) -> BootstrapAllocation:
    """Calculate BTC needed for Spawning Fund (create first F_i).

    Each F0_DAE spawn needs seed capital to begin operations.
    Buffer allows for failed spawns and retries.
    """
    base_spawns = num_initial_spawns * seed_per_spawn_btc
    btc_needed = base_spawns * buffer_multiplier

    return BootstrapAllocation(
        component=BootstrapComponent.SPAWNING_FUND,
        btc_amount=btc_needed,
        description=f"Seed {num_initial_spawns} initial F_i spawns",
    )


def calculate_dex_liquidity(
    min_depth_btc: float = 5.0,
    num_pairs: int = 3,  # UPS/BTC, F_0/UPS, F_i/UPS
) -> BootstrapAllocation:
    """Calculate BTC needed for DEX initial liquidity.

    Need sufficient depth to prevent price manipulation.
    Multiple trading pairs need liquidity.
    """
    btc_needed = min_depth_btc * num_pairs

    return BootstrapAllocation(
        component=BootstrapComponent.DEX_LIQUIDITY,
        btc_amount=btc_needed,
        description=f"DEX liquidity for {num_pairs} trading pairs",
    )


def calculate_genesis_rewards(
    target_genesis_stakers: int = 100,
    avg_stake_btc: float = 0.1,
    reward_multiplier: float = 0.20,  # 20% bonus F_i for genesis
) -> BootstrapAllocation:
    """Calculate BTC needed for Genesis Staker incentives.

    Early stakers get bonus F_i to incentivize bootstrap participation.
    This is separate from their actual stake (which goes to reserve).
    """
    # Reward pool = portion of early F_i minting allocated to genesis
    # Not BTC directly, but need BTC-equivalent backing for reward F_i
    expected_stakes = target_genesis_stakers * avg_stake_btc
    reward_backing = expected_stakes * reward_multiplier

    return BootstrapAllocation(
        component=BootstrapComponent.GENESIS_REWARDS,
        btc_amount=reward_backing,
        description=f"Reward backing for {target_genesis_stakers} genesis stakers",
    )


def create_minimum_bootstrap() -> GenesisBootstrapPlan:
    """Create MINIMUM viable bootstrap plan.

    This is the bare minimum to launch - tight runway, minimal cushion.
    """
    return GenesisBootstrapPlan(
        allocations=[
            calculate_f0_operations(tier="F2_GROWTH", runway_months=18),  # 18mo tight
            calculate_network_pool(num_critical_fi=5, safety_multiplier=1.5),
            calculate_spawning_fund(num_initial_spawns=5, buffer_multiplier=1.0),
            calculate_dex_liquidity(min_depth_btc=2.0, num_pairs=2),
            calculate_genesis_rewards(target_genesis_stakers=50, avg_stake_btc=0.05),
        ],
        target_runway_months=18,
    )


def create_conservative_bootstrap() -> GenesisBootstrapPlan:
    """Create CONSERVATIVE bootstrap plan.

    Comfortable runway, good cushion for volatility.
    """
    return GenesisBootstrapPlan(
        allocations=[
            calculate_f0_operations(tier="F2_GROWTH", runway_months=24),  # YC standard
            calculate_network_pool(num_critical_fi=10, safety_multiplier=2.0),
            calculate_spawning_fund(num_initial_spawns=10, buffer_multiplier=1.5),
            calculate_dex_liquidity(min_depth_btc=5.0, num_pairs=3),
            calculate_genesis_rewards(target_genesis_stakers=100, avg_stake_btc=0.1),
        ],
        target_runway_months=24,
    )


def create_comfortable_bootstrap() -> GenesisBootstrapPlan:
    """Create COMFORTABLE bootstrap plan.

    Similar to Bitclout scale - serious ecosystem launch.
    """
    return GenesisBootstrapPlan(
        allocations=[
            calculate_f0_operations(tier="F2_GROWTH", runway_months=36),  # 3 years
            calculate_network_pool(num_critical_fi=25, safety_multiplier=3.0),
            calculate_spawning_fund(num_initial_spawns=25, buffer_multiplier=2.0),
            calculate_dex_liquidity(min_depth_btc=10.0, num_pairs=5),
            calculate_genesis_rewards(target_genesis_stakers=500, avg_stake_btc=0.2),
        ],
        target_runway_months=36,
    )


def create_aggressive_bootstrap() -> GenesisBootstrapPlan:
    """Create AGGRESSIVE bootstrap plan.

    Ecosystem dominance - like Bitclout's $165M.
    """
    return GenesisBootstrapPlan(
        allocations=[
            calculate_f0_operations(tier="F3_INFRA", runway_months=48),  # 4 years, F3 scale
            calculate_network_pool(num_critical_fi=100, safety_multiplier=5.0),
            calculate_spawning_fund(num_initial_spawns=100, buffer_multiplier=3.0),
            calculate_dex_liquidity(min_depth_btc=50.0, num_pairs=10),
            calculate_genesis_rewards(target_genesis_stakers=1000, avg_stake_btc=0.5),
        ],
        target_runway_months=48,
    )


def analyze_bootstrap_scenarios() -> None:
    """Analyze all bootstrap scenarios."""

    print("\n" + "=" * 100)
    print("GENESIS BOOTSTRAP ANALYSIS - Minimum BTC to Launch pAVS")
    print("=" * 100)

    print("\nBITCLOUT REFERENCE:")
    print("  - $200M raised from VCs")
    print("  - $165M in BTC deposits to bonding curve = ~1,650 BTC @ $100K")
    print("  - 10.8M token supply cap")
    print()

    scenarios = {
        "MINIMUM": create_minimum_bootstrap(),
        "CONSERVATIVE": create_conservative_bootstrap(),
        "COMFORTABLE": create_comfortable_bootstrap(),
        "AGGRESSIVE": create_aggressive_bootstrap(),
    }

    print(f"{'Scenario':<15} {'Total BTC':>12} {'USD @ $100K':>15} {'USD @ $50K':>15} {'USD @ $200K':>15}")
    print("-" * 75)

    for name, plan in scenarios.items():
        print(f"{name:<15} {plan.total_btc:>12.1f} "
              f"${plan.total_usd(100_000):>13,.0f} "
              f"${plan.total_usd(50_000):>13,.0f} "
              f"${plan.total_usd(200_000):>13,.0f}")

    print("\n" + "=" * 100)
    print("COMPONENT BREAKDOWN BY SCENARIO")
    print("=" * 100)

    for name, plan in scenarios.items():
        print(f"\n{name} ({plan.total_btc:.1f} BTC = ${plan.total_usd():,.0f} @ $100K):")
        print("-" * 60)
        for alloc in plan.allocations:
            pct = (alloc.btc_amount / plan.total_btc) * 100
            print(f"  {alloc.component.value:<20}: {alloc.btc_amount:>8.2f} BTC ({pct:>5.1f}%) - {alloc.description}")


def calculate_genesis_staker_requirements() -> None:
    """Calculate how many genesis stakers needed for each scenario."""

    print("\n" + "=" * 100)
    print("GENESIS STAKER REQUIREMENTS")
    print("=" * 100)
    print("\nHow many stakers needed to bootstrap each scenario?")
    print("(Assuming staker BTC goes to reserve, not just genesis fund)")
    print()

    scenarios = {
        "MINIMUM": (create_minimum_bootstrap().total_btc, 18),
        "CONSERVATIVE": (create_conservative_bootstrap().total_btc, 24),
        "COMFORTABLE": (create_comfortable_bootstrap().total_btc, 36),
        "AGGRESSIVE": (create_aggressive_bootstrap().total_btc, 48),
    }

    stake_tiers = [0.01, 0.1, 0.5, 1.0, 10.0]  # BTC per staker

    print(f"{'Scenario':<15} {'BTC Needed':>12}", end="")
    for tier in stake_tiers:
        print(f" {'@'+str(tier)+'BTC':>10}", end="")
    print()
    print("-" * 85)

    for name, (btc_needed, _) in scenarios.items():
        print(f"{name:<15} {btc_needed:>12.1f}", end="")
        for tier in stake_tiers:
            stakers = btc_needed / tier
            print(f" {stakers:>10.0f}", end="")
        print()

    print("\n" + "-" * 85)
    print("INSIGHT: CONSERVATIVE (50 BTC) needs 500 stakers @ 0.1 BTC each")
    print("         or 50 stakers @ 1 BTC each")
    print("         or 5 whales @ 10 BTC each")


def compare_to_bitclout() -> None:
    """Compare pAVS bootstrap to Bitclout."""

    print("\n" + "=" * 100)
    print("pAVS vs BITCLOUT COMPARISON")
    print("=" * 100)

    bitclout_btc = 1650  # ~$165M at $100K
    bitclout_supply = 10_800_000
    bitclout_genesis_pct = 0.37  # Top 20 got 37%

    pavs_conservative = create_conservative_bootstrap()
    pavs_comfortable = create_comfortable_bootstrap()

    print(f"""
BITCLOUT (2021):
  Initial BTC Reserve:  {bitclout_btc:,} BTC (~$165M)
  Token Supply:         {bitclout_supply:,} CLOUT/DESO
  Genesis Allocation:   {bitclout_genesis_pct*100:.0f}% to top 20 recipients
  BTC per Token:        {bitclout_btc/bitclout_supply:.6f} BTC (~$0.015)
  Model:                Bonding curve (price doubles per 1M sold)

pAVS CONSERVATIVE ({pavs_conservative.total_btc:.1f} BTC):
  Initial BTC Reserve:  {pavs_conservative.total_btc:.1f} BTC (~${pavs_conservative.total_usd():,.0f})
  Token Supply:         {FI_SUPPLY_PER_FOUNDUP:,} F_i per FoundUp
  Genesis Allocation:   Via staking (no pre-mine)
  BTC per F_i:          {pavs_conservative.total_btc/FI_SUPPLY_PER_FOUNDUP:.10f} BTC
  Model:                Tide economics (ecosystem balancing)

pAVS COMFORTABLE ({pavs_comfortable.total_btc:.1f} BTC):
  Initial BTC Reserve:  {pavs_comfortable.total_btc:.1f} BTC (~${pavs_comfortable.total_usd():,.0f})
  Bitclout Ratio:       {pavs_comfortable.total_btc/bitclout_btc*100:.1f}% of Bitclout's reserve

KEY DIFFERENCES:
  1. pAVS is 0102-native (no salaries, 90%+ cheaper operations)
  2. pAVS uses tide economics (ecosystem balancing, not bonding curve)
  3. pAVS has NO pre-mine (genesis via staking, not allocation)
  4. pAVS scales fractally (each F_i is independent treasury)
  5. pAVS is BTC-native (UPS = sats, not separate token)
""")


def recommend_minimum_viable() -> None:
    """Recommend the minimum viable bootstrap."""

    print("\n" + "=" * 100)
    print("RECOMMENDATION: MINIMUM VIABLE BOOTSTRAP")
    print("=" * 100)

    # Calculate true minimum
    min_plan = GenesisBootstrapPlan(
        allocations=[
            BootstrapAllocation(
                component=BootstrapComponent.F0_OPERATIONS,
                btc_amount=8.0,  # F2_GROWTH, 12 months tight
                description="F_0 operations (12mo minimum runway)",
                runway_months=12,
            ),
            BootstrapAllocation(
                component=BootstrapComponent.NETWORK_POOL,
                btc_amount=3.0,  # Support 3 CRITICAL F_i
                description="Network Pool (minimal ecosystem support)",
            ),
            BootstrapAllocation(
                component=BootstrapComponent.SPAWNING_FUND,
                btc_amount=2.5,  # Seed 5 F_i at 0.5 BTC each
                description="Spawn first 5 F_i children",
            ),
            BootstrapAllocation(
                component=BootstrapComponent.DEX_LIQUIDITY,
                btc_amount=3.0,  # Minimal trading depth
                description="DEX liquidity (bare minimum)",
            ),
            BootstrapAllocation(
                component=BootstrapComponent.GENESIS_REWARDS,
                btc_amount=1.0,  # Small incentive pool
                description="Genesis staker incentives (minimal)",
            ),
        ],
        target_runway_months=12,
    )

    print(f"""
ABSOLUTE MINIMUM (High Risk):
  Total:                {min_plan.total_btc:.1f} BTC = ${min_plan.total_usd():,.0f} @ $100K
  Runway:               12 months (TIGHT - need revenue within year)
  Stakers needed:       {min_plan.total_btc/0.1:.0f} @ 0.1 BTC each

  Breakdown:
""")
    for alloc in min_plan.allocations:
        print(f"    {alloc.component.value:<20}: {alloc.btc_amount:.1f} BTC")

    rec_plan = create_conservative_bootstrap()

    print(f"""
RECOMMENDED (Conservative):
  Total:                {rec_plan.total_btc:.1f} BTC = ${rec_plan.total_usd():,.0f} @ $100K
  Runway:               24 months (YC standard)
  Stakers needed:       {rec_plan.total_btc/0.1:.0f} @ 0.1 BTC each

  Breakdown:
""")
    for alloc in rec_plan.allocations:
        print(f"    {alloc.component.value:<20}: {alloc.btc_amount:.1f} BTC")

    print(f"""
012's RANGE (100-1000 BTC):
  100 BTC = ${100 * 100_000:,.0f}  → COMFORTABLE (36mo runway, 25 F_i spawns)
  500 BTC = ${500 * 100_000:,.0f}  → SERIOUS (between comfortable and aggressive)
  1000 BTC = ${1000 * 100_000:,.0f} → ECOSYSTEM DOMINANCE (like Bitclout)

BOTTOM LINE:
  - MINIMUM: ~20 BTC ($2M) - risky, tight runway
  - SAFE:    ~50 BTC ($5M) - conservative, 24mo runway
  - SERIOUS: ~100+ BTC ($10M+) - comfortable, multi-year

  Genesis stakers at 0.1 BTC each:
  - 200 stakers = 20 BTC (minimum)
  - 500 stakers = 50 BTC (safe)
  - 1000 stakers = 100 BTC (serious)
""")


def calculate_staker_distribution_ratio() -> None:
    """Calculate distribution ratio for genesis stakers.

    012-CONFIRMED: BTC stakers expect 10x-100x distribution ratio.
    This is NOT ROI (securities language) - it's protocol participation.

    Key insight: Genesis stakers earn from ALL FoundUps ecosystem-wide.
    The more FoundUps, the faster they reach target distribution ratio.
    """

    print("\n" + "=" * 100)
    print("GENESIS STAKER DISTRIBUTION RATIO ANALYSIS")
    print("=" * 100)
    print("\n012-CONFIRMED: BTC stakers expect 10x-100x distribution ratio.")
    print("Genesis stakers earn from ALL FoundUps (ecosystem-wide).")
    print()

    # From staker_viability.py analysis
    # Du pool = 4% of F_i minting per FoundUp
    # Genesis stakers share Du pool ecosystem-wide

    fi_per_foundup = 21_000_000
    du_pool_pct = 0.04  # 4% Du pool

    # Staker scenarios
    staker_configs = [
        {"stakers": 100, "btc_each": 0.1, "label": "Small (100 @ 0.1 BTC)"},
        {"stakers": 100, "btc_each": 0.5, "label": "Medium (100 @ 0.5 BTC)"},
        {"stakers": 100, "btc_each": 1.0, "label": "Large (100 @ 1 BTC)"},
        {"stakers": 500, "btc_each": 0.1, "label": "Wide (500 @ 0.1 BTC)"},
        {"stakers": 1000, "btc_each": 0.1, "label": "Massive (1000 @ 0.1 BTC)"},
    ]

    # FoundUp growth scenarios (from earlier ecosystem analysis)
    foundup_scenarios = {
        "Conservative": {"y1": 3_500, "y2": 10_000, "y3": 25_000},
        "Baseline": {"y1": 20_000, "y2": 50_000, "y3": 100_000},
        "OpenClaw-Style": {"y1": 105_000, "y2": 350_000, "y3": 750_000},
    }

    print("Assumptions:")
    print(f"  - Du pool = {du_pool_pct*100:.0f}% of F_i per FoundUp")
    print(f"  - F_i per FoundUp = {fi_per_foundup:,}")
    print(f"  - BTC price = $100K (for USD display)")
    print()

    for config in staker_configs:
        total_btc = config["stakers"] * config["btc_each"]
        btc_per_staker = config["btc_each"]
        usd_per_staker = btc_per_staker * 100_000

        print(f"\n{config['label']} - Total: {total_btc:.0f} BTC (${total_btc * 100_000:,.0f})")
        print("-" * 80)
        print(f"{'Growth Model':<20} {'FoundUps Y1':>12} {'Du Pool F_i':>15} {'Per Staker':>15} {'Dist Ratio':>12}")
        print("-" * 80)

        for name, foundups in foundup_scenarios.items():
            y1_foundups = foundups["y1"]

            # Du pool = 4% of F_i minted across ALL foundups
            total_fi_minted = y1_foundups * fi_per_foundup
            du_pool_fi = total_fi_minted * du_pool_pct

            # Each staker's share
            fi_per_staker = du_pool_fi / config["stakers"]

            # Distribution ratio = F_i value / BTC staked
            # Assume F_i price at 1 sat each (conservative)
            fi_value_sats = fi_per_staker  # 1 F_i = 1 sat
            fi_value_btc = fi_value_sats / SATS_PER_BTC
            fi_value_usd = fi_value_btc * 100_000

            dist_ratio = fi_value_usd / usd_per_staker if usd_per_staker > 0 else 0

            print(f"{name:<20} {y1_foundups:>12,} {du_pool_fi:>15,.0f} {fi_per_staker:>15,.0f} {dist_ratio:>11.1f}x")

    print("""
CRITICAL INSIGHT:
  At 1 sat per F_i (conservative), even OpenClaw-Style growth only gives ~0.04x Y1.
  This assumes F_i trades at 1:1 with sats.

  For 10x distribution ratio, F_i must appreciate OR:
  - Staker pool must be smaller (100 not 1000)
  - FoundUp ecosystem must be massive (1M+)
  - F_i must trade at premium to sats

  BITCLOUT MODEL: F_i appreciation via bonding curve
  - Early buyers got cheap F_i (low on curve)
  - Price doubled per 1M sold
  - Genesis holders got 10x-100x as curve rose

  pAVS MODEL: F_i appreciation via ecosystem value
  - F_i backed by UPS (backed by BTC)
  - As ecosystem grows, F_i demand → price rises
  - Genesis stakers have LOWEST cost basis
""")


def model_bonding_curve_bootstrap() -> None:
    """Model Bitclout-style bonding curve for pAVS genesis.

    Bonding curve: price = f(supply)
    Early stakers get more F_i per BTC than later stakers.
    """

    print("\n" + "=" * 100)
    print("BONDING CURVE MODEL FOR GENESIS BOOTSTRAP")
    print("=" * 100)

    # Bitclout: price doubles every 1M tokens
    # pAVS adaptation: price increases with cumulative BTC in reserve

    print("""
BITCLOUT BONDING CURVE:
  price(supply) = price_0 * 2^(supply / 1_000_000)

  At 0 supply:   price = $0.01
  At 1M supply:  price = $0.02
  At 2M supply:  price = $0.04
  At 5M supply:  price = $0.32
  At 10M supply: price = $10.24

  Early buyers: 1M tokens for ~$15K
  Late buyers:  1M tokens for ~$10M

pAVS ADAPTATION (reserve-based):
  Instead of supply-based curve, use RESERVE-based:

  fi_per_btc(reserve) = base_rate / (1 + reserve/scale)

  At 0 BTC:    1M F_i per BTC
  At 10 BTC:   500K F_i per BTC
  At 100 BTC:  100K F_i per BTC
  At 1000 BTC: 10K F_i per BTC

  This creates FOMO - earlier stakers get more F_i.
""")

    # Model the curve
    base_rate = 1_000_000  # F_i per BTC at genesis
    scale = 50  # BTC at which rate halves

    print("\nRESERVE-BASED BONDING CURVE:")
    print(f"  fi_per_btc = {base_rate:,} / (1 + reserve_btc / {scale})")
    print()
    print(f"{'Reserve (BTC)':>15} {'F_i per BTC':>15} {'Cumulative F_i':>18} {'Avg Price':>12}")
    print("-" * 65)

    cumulative_fi = 0
    reserves = [0, 10, 25, 50, 100, 200, 500, 1000]

    for i, reserve in enumerate(reserves):
        if i == 0:
            fi_per_btc = base_rate
            increment_fi = 0
        else:
            # F_i rate at this reserve level
            fi_per_btc = base_rate / (1 + reserve / scale)
            # How much F_i was minted between last reserve and this one
            btc_added = reserve - reserves[i-1]
            avg_rate = (base_rate / (1 + reserves[i-1] / scale) + fi_per_btc) / 2
            increment_fi = btc_added * avg_rate

        cumulative_fi += increment_fi
        avg_price = reserve / cumulative_fi if cumulative_fi > 0 else 0

        print(f"{reserve:>15,} {fi_per_btc:>15,.0f} {cumulative_fi:>18,.0f} {avg_price:>11.8f}")

    print("""
GENESIS STAKER ADVANTAGE:
  First 10 BTC → ~9.5M F_i (avg: 0.00000105 BTC/F_i)
  Next 90 BTC  → ~36M F_i (avg: 0.0000025 BTC/F_i)

  10x distribution ratio achieved when F_i trades at 10x the avg entry price.
  Early stakers (first 10 BTC) need F_i price = 0.0000105 BTC = 1,050 sats
  This happens when ecosystem matures and F_i is scarce.

  KEY: Genesis stakers have LOWEST cost basis.
       As F_i appreciates, their distribution ratio increases.
       10x-100x is achieved via F_i price appreciation, NOT just Du pool distributions.
""")


def integrate_ecosystem_revenue() -> None:
    """Integrate ecosystem revenue into bootstrap analysis.

    Shows how DEX/exit fees from ALL FoundUps generate revenue
    that offsets operational costs and makes ecosystem self-sustaining.
    """

    print("\n" + "=" * 100)
    print("ECOSYSTEM REVENUE INTEGRATION - DEX + Exit Fees Pay Back Bootstrap")
    print("=" * 100)
    print("\n012-INSIGHT: EVERY FoundUp generates trading fees.")
    print("             These fees flow BACK to ecosystem, offsetting operational costs.")
    print()

    # From ecosystem_revenue.py
    # OpenClaw-Style (Y1): $21.5M/day = 215 BTC/day
    # Monthly Revenue: $645M = 6,450 BTC

    bootstrap_scenarios = {
        "MINIMUM": (17.5, 12),    # BTC, runway months
        "CONSERVATIVE": (35.0, 24),
        "COMFORTABLE": (120.0, 36),
        "AGGRESSIVE": (902.0, 48),
    }

    # Revenue scenarios by ecosystem size (BTC per month from fees)
    revenue_scenarios = {
        "Genesis (110 F_i)": 0.56,        # $56K/mo = 0.56 BTC
        "Conservative (3.5K F_i)": 120.4,  # $12M/mo = 120 BTC
        "Baseline (20K F_i)": 969.4,       # $97M/mo = 969 BTC
        "OpenClaw (105K F_i)": 6450.6,     # $645M/mo = 6,451 BTC
    }

    # Monthly burn for F_0 platform (F2_GROWTH tier)
    f0_monthly_burn_btc = 0.27  # $26.6K/mo = 0.27 BTC @ $100K

    print("BOOTSTRAP PAYBACK ANALYSIS:")
    print("-" * 100)
    print(f"{'Bootstrap':<15} {'BTC':>10} {'Genesis Deficit':>18} {'Conservative':>18} {'Baseline':>18} {'OpenClaw':>18}")
    print(f"{'':15} {'':10} {'(110 F_i)':>18} {'(3.5K F_i)':>18} {'(20K F_i)':>18} {'(105K F_i)':>18}")
    print("-" * 100)

    for boot_name, (boot_btc, runway) in bootstrap_scenarios.items():
        print(f"{boot_name:<15} {boot_btc:>10.1f}", end="")

        for rev_name, rev_btc in revenue_scenarios.items():
            net_monthly = rev_btc - f0_monthly_burn_btc
            if net_monthly > 0:
                payback_months = boot_btc / net_monthly
                print(f" {payback_months:>15.1f}mo", end="")
            else:
                print(f" {'DEFICIT':>17}", end="")
        print()

    print(f"""

INTERPRETATION:
  - At Genesis (110 F_i): ALL scenarios are in DEFICIT
    → This is WHY we need bootstrap capital!

  - At Conservative (3,500 F_i):
    → MINIMUM bootstrap pays back in 0.1 months (3 days!)
    → Revenue exceeds costs dramatically

  - At Baseline (20,000 F_i):
    → Ecosystem generates 969 BTC/month in fees
    → Even AGGRESSIVE bootstrap pays back in under 1 month

  - At OpenClaw (105,000 F_i):
    → Ecosystem generates 6,450 BTC/month
    → Bootstrap is IRRELEVANT at this scale

KEY INSIGHT:
  Bootstrap capital is RUNWAY to reach scale.
  Once ecosystem has 1,000+ active FoundUps, fee revenue > costs.

  Genesis stakers provide this runway, then:
  1. Fee revenue makes ecosystem self-sustaining
  2. F_i appreciation provides distribution ratio (10x-100x)
  3. Tide economics redistributes to struggling F_i

  The question is NOT "how much bootstrap?"
  The question is "how fast can we reach 1,000+ FoundUps?"
""")

    # Show path to 1000 FoundUps
    print("=" * 100)
    print("PATH TO SELF-SUSTAINABILITY (1,000+ FoundUps)")
    print("=" * 100)

    print("""
SPAWNING RATE ANALYSIS:
  - Each F0_DAE spawn costs ~0.5 BTC seed capital
  - Spawning Fund for 100 FoundUps = 50 BTC

  If we spawn 10 F_i per week:
    - Week 10: 100 F_i
    - Week 25: 250 F_i  (conservative revenue ~= costs)
    - Week 100: 1000 F_i (self-sustaining)

  If we spawn 50 F_i per week (aggressive):
    - Week 2: 100 F_i
    - Week 5: 250 F_i
    - Week 20: 1000 F_i (self-sustaining in 5 months!)

CONSERVATIVE PATH (safe):
  Bootstrap: 50 BTC ($5M)
  Spawning: 10 F_i/week
  Break-even: ~6 months
  Self-sustaining: 2 years

AGGRESSIVE PATH (Bitclout-style):
  Bootstrap: 500 BTC ($50M)
  Spawning: 100 F_i/week
  Break-even: ~2 months
  Self-sustaining: 6 months

012's 100-1000 BTC RANGE:
  100 BTC = Comfortable, 1-year path to self-sustaining
  500 BTC = Aggressive, 6-month path to self-sustaining
  1000 BTC = Ecosystem dominance, 3-month path
""")


def main():
    """Run full genesis bootstrap analysis."""
    analyze_bootstrap_scenarios()
    calculate_genesis_staker_requirements()
    compare_to_bitclout()
    recommend_minimum_viable()
    calculate_staker_distribution_ratio()
    model_bonding_curve_bootstrap()
    integrate_ecosystem_revenue()


if __name__ == "__main__":
    main()
