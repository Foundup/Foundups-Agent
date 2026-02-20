"""Dynamic Fee Taper Engine - Fees decrease as reserve strengthens.

As BTC reserve builds relative to F_i released, exit fees taper down.
This creates a self-regulating system:
- Early: High fees to build reserve (Hotel California filling up)
- Mature: Low fees once reserve is robust (reward loyalty)
- Stress: Fees rise if reserve depletes (protect remaining holders)
- Overflow: At 100%+ reserve, excess drips to Network Pool (UBD)

The system is FLOAT - continuously adjusting based on reserve health.

012-CONFIRMED DECISIONS (2026-02-17):
1. Target ratio: 0.000001 BTC per F_i (1 sat per 1,000 F_i)
2. Taper curve: SIGMOID (matches S-curve token release)
3. Floor fee: 2% minimum
4. Overflow: 100%+ reserve drips 1% per epoch to Network Pool

012-CONFIRMED INSIGHTS (2026-02-17):
5. Staked F_i is pre-backed: UPS (backed by BTC) → F_i (inherits backing)
   - Only MINED F_i needs backing from exit fees
   - Reserve health targets mined_fi coverage, not total_fi

6. Fractal Treasury Model: F_0 DUPES into every F_i
   - F_0 = pAVS template (the blueprint, first instance)
   - F_i = F_0.clone() → every FoundUp gets FULL pAVS machinery
   - F_0 is NOT special - just instance #0
   - ALL F_i have SAME: treasury, fees, overflow, paywall capability
   - Network Pool collects overflow from ALL F_i (including F_0)

   Template (F_0) duped into every F_i:
     F_i ──┬── paywalls/subs ──→ F_i Treasury (BTC)
           ├── staking ────────→ F_i Reserve (pre-backed)
           ├── exit fees ──────→ F_i Reserve (mined backing)
           └── overflow ───────→ Network Pool (shared ecosystem)
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import math


# Reserve health thresholds
CRITICAL_THRESHOLD = 0.10    # <10% = critical, max fees
BUILDING_THRESHOLD = 0.25    # 10-25% = building
HEALTHY_THRESHOLD = 0.40     # 25-40% = healthy
STRONG_THRESHOLD = 0.60      # 40-60% = strong
ROBUST_THRESHOLD = 0.80      # >80% = robust, min fees

# Fee multiplier range
MIN_MULTIPLIER = 0.3   # Fees can drop to 30% of base (reward strong reserve)
MAX_MULTIPLIER = 2.0   # Fees can rise to 200% of base (protect weak reserve)

# 012-CONFIRMED (2026-02-17): Backing ratio SCALES WITH TIER
# The treasury threshold IS the backing - it covers operational costs
# Backing per F_i = tier_treasury / 21M tokens (implicit, not fixed)
#
# Example (at $100K/BTC):
#   F1_OPO:     $100K treasury → $0.0048/F_i → 4.8 sats/F_i
#   F5_SYSTEMIC: $1B treasury  → $47.62/F_i  → 47,600 sats/F_i
#
# pAVS = TOTALITY of all F_i treasuries (distributed autonomous ecosystem)
# Treasury funds: servers, compute, storage, network, 0102 agent costs
#
# 012-INSIGHT (2026-02-17): TIDE-LIKE ECONOMICS
# - System LENDS and RETURNS like a tide (ebb and flow)
# - No competition between F_i - BLUE OCEAN strategy
# - When costs go up, it all BALANCES across the ecosystem
# - Like treasuries and IMF, but for FoundUps (decentralized)
# - Network Pool = SDR (Special Drawing Rights) - ecosystem liquidity

# BTC/USD conversion (for display purposes only - math is in sats)
BTC_USD_RATE = 100_000  # $100K/BTC assumption

# Tier treasury thresholds (UPS = sats, at $100K/BTC)
TIER_TREASURY_THRESHOLDS = {
    "F0_DAE": 0,                      # Seed stage
    "F1_OPO": 100_000_000,            # 100M sats = 1 BTC = $100K
    "F2_GROWTH": 1_000_000_000,       # 1B sats = 10 BTC = $1M
    "F3_INFRA": 10_000_000_000,       # 10B sats = 100 BTC = $10M
    "F4_MEGA": 100_000_000_000,       # 100B sats = 1K BTC = $100M
    "F5_SYSTEMIC": 1_000_000_000_000, # 1T sats = 10K BTC = $1B
}

FI_SUPPLY_PER_FOUNDUP = 21_000_000  # 21M F_i per FoundUp
SATS_PER_BTC = 100_000_000

def sats_to_usd(sats: int) -> float:
    """Convert sats to USD (for display only - math is in sats)."""
    return (sats / SATS_PER_BTC) * BTC_USD_RATE


def btc_to_usd(btc: float) -> float:
    """Convert BTC to USD (for display only)."""
    return btc * BTC_USD_RATE


def get_target_sats_per_fi(tier: str) -> float:
    """Get backing ratio for a tier (sats per F_i token).

    Backing = tier_treasury / 21M tokens

    Examples (at $100K/BTC):
        F0_DAE:     0 sats/F_i (seed, no backing yet)
        F1_OPO:     ~4.76 sats/F_i ($100K treasury)
        F5_SYSTEMIC: ~47,619 sats/F_i ($1B treasury)
    """
    treasury_sats = TIER_TREASURY_THRESHOLDS.get(tier, TIER_TREASURY_THRESHOLDS["F1_OPO"])
    return treasury_sats / FI_SUPPLY_PER_FOUNDUP


def get_target_btc_per_fi(tier: str) -> float:
    """Get backing ratio in BTC for a tier.

    Same as get_target_sats_per_fi but in BTC units.
    """
    return get_target_sats_per_fi(tier) / SATS_PER_BTC


def get_tier_target_usd(tier: str) -> float:
    """Get treasury target in USD for a tier (at BTC_USD_RATE)."""
    return sats_to_usd(TIER_TREASURY_THRESHOLDS.get(tier, TIER_TREASURY_THRESHOLDS["F1_OPO"]))


# Legacy constant for backwards compatibility (use F1_OPO as default)
DEFAULT_TARGET_BTC_PER_FI = TIER_TREASURY_THRESHOLDS["F1_OPO"] / FI_SUPPLY_PER_FOUNDUP / SATS_PER_BTC

# 012-CONFIRMED: Overflow parameters
OVERFLOW_THRESHOLD = 1.0       # 100% reserve health triggers overflow
OVERFLOW_DRIP_RATE = 0.01      # 1% of excess per epoch drips to Network
MIN_EXIT_FEE = 0.02            # 2% floor (can't go below)


@dataclass
class ReserveHealth:
    """Current reserve health metrics.

    012-CONFIRMED INSIGHT (2026-02-17):
    - STAKED F_i is pre-backed (UPS backed by BTC → transferred backing)
    - MINED F_i needs backing from exit fees
    - Reserve health should focus on MINED F_i coverage
    """

    btc_reserve: float              # Total BTC in reserve
    total_fi_released: float        # Total F_i tokens released
    total_ups_circulation: float    # UPS in circulation
    target_btc_per_fi: float        # Target backing ratio
    staked_fi: float = 0.0          # F_i from staking (already backed)
    mined_fi: float = 0.0           # F_i from mining (needs backing)

    @property
    def fi_needing_backing(self) -> float:
        """F_i that needs reserve backing (mined only, not staked).

        STAKED F_i: Already backed by UPS (which is backed by BTC)
        MINED F_i: Needs backing from exit fees
        """
        if self.mined_fi > 0:
            return self.mined_fi
        # Fallback: if breakdown not provided, assume all needs backing
        return self.total_fi_released

    @property
    def reserve_ratio(self) -> float:
        """Calculate reserve health ratio (0.0 to 1.0+).

        Uses fi_needing_backing (mined only) not total F_i,
        because staked F_i is already backed by UPS.
        """
        fi_to_back = self.fi_needing_backing
        if fi_to_back <= 0:
            return 1.0  # No F_i needs backing = fully reserved

        target_reserve = fi_to_back * self.target_btc_per_fi
        if target_reserve <= 0:
            return 1.0

        return min(2.0, self.btc_reserve / target_reserve)

    @property
    def health_status(self) -> str:
        """Human-readable health status."""
        r = self.reserve_ratio
        if r < CRITICAL_THRESHOLD:
            return "CRITICAL"
        elif r < BUILDING_THRESHOLD:
            return "BUILDING"
        elif r < HEALTHY_THRESHOLD:
            return "HEALTHY"
        elif r < STRONG_THRESHOLD:
            return "STRONG"
        elif r < OVERFLOW_THRESHOLD:
            return "ROBUST"
        else:
            return "OVERFLOW"

    @property
    def target_reserve(self) -> float:
        """Target BTC reserve for 100% health.

        Only targets backing for MINED F_i (staked F_i already backed).
        """
        return self.fi_needing_backing * self.target_btc_per_fi

    @property
    def has_overflow(self) -> bool:
        """True if reserve exceeds 100% target."""
        return self.reserve_ratio >= OVERFLOW_THRESHOLD

    @property
    def overflow_btc(self) -> float:
        """BTC amount exceeding target (available for Network drip)."""
        if not self.has_overflow:
            return 0.0
        return max(0.0, self.btc_reserve - self.target_reserve)

    @property
    def epoch_drip_to_network(self) -> float:
        """BTC to drip to Network Pool this epoch (1% of overflow)."""
        return self.overflow_btc * OVERFLOW_DRIP_RATE


def calculate_fee_multiplier(reserve_ratio: float, curve: str = "sigmoid") -> float:
    """Calculate fee multiplier based on reserve health.

    Args:
        reserve_ratio: Current reserve health (0.0 to 1.0+)
        curve: "sigmoid", "linear", or "stepped"

    Returns:
        Fee multiplier (0.3 to 2.0)
    """

    if curve == "sigmoid":
        # Smooth S-curve transition
        # Centered at 40% reserve health
        # Steep transition between 20% and 60%
        x = reserve_ratio
        center = 0.40
        steepness = 8.0

        # Sigmoid: high at low reserve, low at high reserve
        raw = 1.0 / (1.0 + math.exp(steepness * (x - center)))

        # Scale to our multiplier range
        # raw=1.0 (low reserve) -> MAX_MULTIPLIER
        # raw=0.0 (high reserve) -> MIN_MULTIPLIER
        multiplier = MIN_MULTIPLIER + (MAX_MULTIPLIER - MIN_MULTIPLIER) * raw

    elif curve == "linear":
        # Simple linear interpolation
        if reserve_ratio <= CRITICAL_THRESHOLD:
            multiplier = MAX_MULTIPLIER
        elif reserve_ratio >= ROBUST_THRESHOLD:
            multiplier = MIN_MULTIPLIER
        else:
            # Linear between critical and robust
            t = (reserve_ratio - CRITICAL_THRESHOLD) / (ROBUST_THRESHOLD - CRITICAL_THRESHOLD)
            multiplier = MAX_MULTIPLIER - t * (MAX_MULTIPLIER - MIN_MULTIPLIER)

    elif curve == "stepped":
        # Discrete steps
        if reserve_ratio < CRITICAL_THRESHOLD:
            multiplier = 2.0
        elif reserve_ratio < BUILDING_THRESHOLD:
            multiplier = 1.5
        elif reserve_ratio < HEALTHY_THRESHOLD:
            multiplier = 1.0
        elif reserve_ratio < STRONG_THRESHOLD:
            multiplier = 0.7
        elif reserve_ratio < ROBUST_THRESHOLD:
            multiplier = 0.5
        else:
            multiplier = 0.3

    else:
        raise ValueError(f"Unknown curve type: {curve}")

    return max(MIN_MULTIPLIER, min(MAX_MULTIPLIER, multiplier))


@dataclass
class DynamicFeeResult:
    """Result of dynamic fee calculation."""

    base_fee: float
    reserve_ratio: float
    fee_multiplier: float
    effective_fee: float
    health_status: str
    has_overflow: bool = False
    overflow_btc: float = 0.0
    epoch_drip_to_network: float = 0.0

    @property
    def fee_change_pct(self) -> float:
        """Percentage change from base fee."""
        return (self.effective_fee / self.base_fee - 1.0) * 100 if self.base_fee > 0 else 0


class DynamicFeeTaper:
    """Engine for calculating dynamic fees based on reserve health."""

    def __init__(
        self,
        target_btc_per_fi: float = DEFAULT_TARGET_BTC_PER_FI,  # 012-confirmed: 1 sat per 1,000 F_i
        curve: str = "sigmoid",  # 012-confirmed: sigmoid matches S-curve release
    ):
        """Initialize dynamic fee taper.

        Args:
            target_btc_per_fi: Target BTC backing per F_i token
            curve: Fee curve type ("sigmoid", "linear", "stepped")
        """
        self.target_btc_per_fi = target_btc_per_fi
        self.curve = curve

    def calculate_effective_fee(
        self,
        base_fee: float,
        btc_reserve: float,
        total_fi_released: float,
        staked_fi: float = 0.0,
        mined_fi: float = 0.0,
    ) -> DynamicFeeResult:
        """Calculate effective fee with dynamic taper.

        Args:
            base_fee: Base fee rate (e.g., 0.11 for 11%)
            btc_reserve: Current BTC in reserve
            total_fi_released: Total F_i tokens released
            staked_fi: F_i from staking (already backed by UPS)
            mined_fi: F_i from mining (needs backing from fees)

        Returns:
            DynamicFeeResult with effective fee

        Note:
            If staked_fi/mined_fi not provided, assumes all F_i needs backing.
            When provided, reserve health only targets mined_fi coverage,
            because staked F_i is already backed by UPS (which is backed by BTC).
        """
        health = ReserveHealth(
            btc_reserve=btc_reserve,
            total_fi_released=total_fi_released,
            total_ups_circulation=0,  # Not used in basic calc
            target_btc_per_fi=self.target_btc_per_fi,
            staked_fi=staked_fi,
            mined_fi=mined_fi,
        )

        multiplier = calculate_fee_multiplier(health.reserve_ratio, self.curve)
        effective_fee = base_fee * multiplier

        # Cap effective fee at reasonable bounds
        effective_fee = max(0.01, min(0.50, effective_fee))  # 1% to 50%

        return DynamicFeeResult(
            base_fee=base_fee,
            reserve_ratio=health.reserve_ratio,
            fee_multiplier=multiplier,
            effective_fee=effective_fee,
            health_status=health.health_status,
            has_overflow=health.has_overflow,
            overflow_btc=health.overflow_btc,
            epoch_drip_to_network=health.epoch_drip_to_network,
        )


def simulate_taper_over_time(
    epochs: int = 100,
    fi_per_epoch: float = 10000,
    btc_capture_rate: float = 0.15,  # % of fees that become BTC
    base_exit_fee: float = 0.15,
    exit_rate: float = 0.05,  # % of holders exit per epoch
    target_btc_per_fi: float = 0.00001,
) -> list:
    """Simulate fee taper as reserve builds over time.

    Returns list of (epoch, reserve_ratio, fee_multiplier, effective_fee)
    """
    taper = DynamicFeeTaper(target_btc_per_fi=target_btc_per_fi)

    btc_reserve = 0.0
    total_fi = 0.0
    results = []

    for epoch in range(epochs):
        # New F_i released this epoch
        total_fi += fi_per_epoch

        # Calculate current dynamic fee
        result = taper.calculate_effective_fee(
            base_fee=base_exit_fee,
            btc_reserve=btc_reserve,
            total_fi_released=total_fi,
        )

        # Exits this epoch generate fees -> BTC
        exits_fi = total_fi * exit_rate
        fees_collected = exits_fi * result.effective_fee
        btc_captured = fees_collected * btc_capture_rate * target_btc_per_fi

        btc_reserve += btc_captured

        results.append({
            "epoch": epoch,
            "total_fi": total_fi,
            "btc_reserve": btc_reserve,
            "reserve_ratio": result.reserve_ratio,
            "fee_multiplier": result.fee_multiplier,
            "effective_fee": result.effective_fee,
            "health_status": result.health_status,
        })

    return results


def print_taper_simulation():
    """Print a simulation of fee taper over time."""

    print("\n" + "=" * 80)
    print("DYNAMIC FEE TAPER SIMULATION")
    print("=" * 80)

    results = simulate_taper_over_time(epochs=50)

    print(f"\n{'Epoch':>6} {'Total F_i':>12} {'BTC Reserve':>12} {'Ratio':>8} {'Mult':>6} {'Fee':>8} {'Status':>10}")
    print("-" * 70)

    for r in results[::5]:  # Every 5th epoch
        print(
            f"{r['epoch']:>6} "
            f"{r['total_fi']:>12,.0f} "
            f"{r['btc_reserve']:>12.6f} "
            f"{r['reserve_ratio']:>7.1%} "
            f"{r['fee_multiplier']:>5.2f}x "
            f"{r['effective_fee']:>7.1%} "
            f"{r['health_status']:>10}"
        )

    # Show the taper curve
    print("\n" + "-" * 80)
    print("FEE TAPER CURVE (Sigmoid)")
    print("-" * 80)
    print(f"\n{'Reserve %':>10} {'Multiplier':>12} {'Effective Fee (base 15%)':>25}")
    print("-" * 50)

    for pct in [0, 5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90, 100]:
        ratio = pct / 100
        mult = calculate_fee_multiplier(ratio, "sigmoid")
        eff = 0.15 * mult
        bar = "#" * int(mult * 20)
        print(f"{pct:>9}% {mult:>11.2f}x {eff:>10.1%}  {bar}")


# === INTEGRATION WITH HYBRID MODEL ===

@dataclass
class HybridDynamicFees:
    """Combined Hybrid model + Dynamic taper."""

    # Base fees (Hybrid model)
    mined_creation: float = 0.11
    staked_creation: float = 0.03
    vesting_base: float = 0.10
    dex_fee: float = 0.02
    cashout_fee: float = 0.07

    # Vesting discounts (fixed, not tapered)
    vesting_schedule: dict = None

    # Dynamic taper (applied to vesting_base and cashout)
    taper_engine: DynamicFeeTaper = None

    def __post_init__(self):
        if self.vesting_schedule is None:
            self.vesting_schedule = {
                "0-1yr": 1.0,
                "1-2yr": 0.67,
                "2-4yr": 0.47,
                "4-8yr": 0.27,
                "8+yr": 0.13,
            }
        if self.taper_engine is None:
            self.taper_engine = DynamicFeeTaper()

    def calculate_exit_fee(
        self,
        vesting_tier: str,
        btc_reserve: float,
        total_fi_released: float,
    ) -> Tuple[float, DynamicFeeResult]:
        """Calculate exit fee with vesting + dynamic taper.

        Returns (effective_fee, taper_result)
        """
        # 1. Base fee from vesting
        vesting_mult = self.vesting_schedule.get(vesting_tier, 1.0)
        base_fee = self.vesting_base * vesting_mult

        # 2. Apply dynamic taper
        taper_result = self.taper_engine.calculate_effective_fee(
            base_fee=base_fee,
            btc_reserve=btc_reserve,
            total_fi_released=total_fi_released,
        )

        return taper_result.effective_fee, taper_result


def demo_hybrid_dynamic():
    """Demonstrate hybrid model with dynamic taper."""

    print("\n" + "=" * 80)
    print("HYBRID MODEL + DYNAMIC TAPER")
    print("=" * 80)

    model = HybridDynamicFees()

    scenarios = [
        # (vesting_tier, btc_reserve, total_fi)
        ("0-1yr", 0.001, 1_000_000),   # Weak reserve, short hold
        ("0-1yr", 0.01, 1_000_000),    # Strong reserve, short hold
        ("8+yr", 0.001, 1_000_000),    # Weak reserve, long hold
        ("8+yr", 0.01, 1_000_000),     # Strong reserve, long hold
    ]

    print(f"\n{'Vesting':>8} {'Reserve':>10} {'Ratio':>8} {'Base Fee':>10} {'Tapered':>10} {'Status':>10}")
    print("-" * 66)

    for vesting, btc, fi in scenarios:
        eff_fee, result = model.calculate_exit_fee(vesting, btc, fi)
        print(
            f"{vesting:>8} "
            f"{btc:>10.4f} "
            f"{result.reserve_ratio:>7.1%} "
            f"{result.base_fee:>9.1%} "
            f"{eff_fee:>9.1%} "
            f"{result.health_status:>10}"
        )

    print("\n" + "-" * 80)
    print("INSIGHT: Fees automatically adjust based on reserve health!")
    print("- Weak reserve (CRITICAL) → Fees UP to protect remaining holders")
    print("- Strong reserve (ROBUST) → Fees DOWN to reward participants")
    print("-" * 80)


@dataclass
class FoundUpReserve:
    """Per-FoundUp reserve tracking for fractal treasury model.

    Each F_i operates like F_0 with its own treasury/reserve.
    Backing ratio scales with tier (not fixed).

    012-CONFIRMED (2026-02-17):
    - pAVS = TOTALITY of all F_i treasuries (distributed autonomous ecosystem)
    - Treasury funds: servers, compute, storage, network, 0102 agent costs
    - F_0 dupes into every F_i (same machinery, different instance)
    """

    foundup_id: str             # F_0 = platform, F_1..F_n = ventures
    tier: str = "F0_DAE"        # Tier determines backing ratio
    btc_reserve: float = 0.0    # F_i's BTC treasury
    staked_fi: float = 0.0      # F_i from UPS staking (pre-backed)
    mined_fi: float = 0.0       # F_i from agent work (needs backing)
    paywall_revenue: float = 0.0  # BTC from F_i's paywalls/subs

    @property
    def total_fi(self) -> float:
        return self.staked_fi + self.mined_fi

    @property
    def target_btc_per_fi(self) -> float:
        """Get tier-appropriate backing ratio (BTC per F_i)."""
        return get_target_btc_per_fi(self.tier)

    @property
    def target_sats_per_fi(self) -> float:
        """Get tier-appropriate backing ratio (sats per F_i)."""
        return get_target_sats_per_fi(self.tier)

    @property
    def treasury_target_sats(self) -> int:
        """Target treasury in sats for this tier."""
        return TIER_TREASURY_THRESHOLDS.get(self.tier, TIER_TREASURY_THRESHOLDS["F1_OPO"])

    @property
    def treasury_target_btc(self) -> float:
        """Target treasury in BTC for this tier."""
        return self.treasury_target_sats / SATS_PER_BTC

    @property
    def treasury_sats(self) -> int:
        """Current treasury in sats."""
        return int(self.btc_reserve * SATS_PER_BTC)

    def get_health(self, target_btc_per_fi: Optional[float] = None) -> ReserveHealth:
        """Get reserve health for this FoundUp.

        Uses tier-based backing ratio if target_btc_per_fi not provided.
        """
        backing = target_btc_per_fi if target_btc_per_fi is not None else self.target_btc_per_fi
        return ReserveHealth(
            btc_reserve=self.btc_reserve,
            total_fi_released=self.total_fi,
            total_ups_circulation=0,
            target_btc_per_fi=backing,
            staked_fi=self.staked_fi,
            mined_fi=self.mined_fi,
        )

    def process_epoch(self, taper: Optional[DynamicFeeTaper] = None) -> Tuple[float, DynamicFeeResult]:
        """Process epoch for this FoundUp.

        Returns (overflow_drip, fee_result).
        Overflow drip goes to Network Pool (ecosystem-wide balancing).

        012-INSIGHT (2026-02-17): System lends and returns like a tide.
        No competition - blue ocean. Like treasuries/IMF but for FoundUps.
        """
        # Add paywall revenue to reserve
        self.btc_reserve += self.paywall_revenue
        self.paywall_revenue = 0.0  # Reset for next epoch

        # Use tier-appropriate taper engine
        if taper is None:
            taper = DynamicFeeTaper(target_btc_per_fi=self.target_btc_per_fi)

        # Calculate fee and check overflow
        result = taper.calculate_effective_fee(
            base_fee=0.15,  # Hybrid base
            btc_reserve=self.btc_reserve,
            total_fi_released=self.total_fi,
            staked_fi=self.staked_fi,
            mined_fi=self.mined_fi,
        )

        overflow_drip = result.epoch_drip_to_network
        if overflow_drip > 0:
            self.btc_reserve -= overflow_drip  # Drip to Network Pool (ecosystem tide)

        return overflow_drip, result


class FractalTreasuryManager:
    """Manages all F_i reserves in the fractal model.

    Each FoundUp has its own reserve. Network Pool collects all overflow.

    012-CONFIRMED (2026-02-17): IMF-like ecosystem balancing
    - System lends and returns like a tide (ebb and flow)
    - No competition - blue ocean strategy
    - When costs go up, it all balances across ecosystem
    - pAVS = TOTALITY (distributed autonomous ecosystem)
    """

    # Ecosystem balancing parameters
    CRISIS_SUPPORT_RATE = 0.10    # 10% of Network Pool can support CRITICAL F_i
    SUPPORT_THRESHOLD = 0.05     # Support if reserve ratio < 5%

    def __init__(self):
        self.foundups: Dict[str, FoundUpReserve] = {}
        self.network_pool: float = 0.0  # Shared ecosystem reserve (like IMF SDR)
        self.epoch_count: int = 0

    def register_foundup(self, foundup_id: str, tier: str = "F0_DAE") -> FoundUpReserve:
        """Register a new FoundUp (creates its treasury).

        Args:
            foundup_id: Unique identifier (F_0, F_1, etc.)
            tier: FoundUp tier (F0_DAE through F5_SYSTEMIC)
        """
        if foundup_id not in self.foundups:
            self.foundups[foundup_id] = FoundUpReserve(foundup_id=foundup_id, tier=tier)
        return self.foundups[foundup_id]

    @property
    def total_ecosystem_btc(self) -> float:
        """Total BTC across ALL F_i + Network Pool (pAVS totality)."""
        return sum(r.btc_reserve for r in self.foundups.values()) + self.network_pool

    @property
    def total_ecosystem_sats(self) -> int:
        """Total sats across ecosystem."""
        return int(self.total_ecosystem_btc * SATS_PER_BTC)

    def _ecosystem_tide_balance(self, results: Dict[str, DynamicFeeResult]) -> Dict[str, float]:
        """Ecosystem tide: support CRITICAL F_i from Network Pool.

        Like IMF emergency lending - temporary support during crisis.
        Returns dict of foundup_id -> support_received.
        """
        support_given = {}

        # Find CRITICAL F_i needing support
        critical_foundups = [
            (fid, r) for fid, r in self.foundups.items()
            if results.get(fid) and results[fid].reserve_ratio < self.SUPPORT_THRESHOLD
        ]

        if not critical_foundups or self.network_pool <= 0:
            return support_given

        # Available support from Network Pool
        available_support = self.network_pool * self.CRISIS_SUPPORT_RATE

        # Distribute support proportionally to need
        total_need = sum(
            r.target_btc_per_fi * r.mined_fi * (self.SUPPORT_THRESHOLD - results[fid].reserve_ratio)
            for fid, r in critical_foundups
        )

        if total_need <= 0:
            return support_given

        for fid, reserve in critical_foundups:
            need = reserve.target_btc_per_fi * reserve.mined_fi * (self.SUPPORT_THRESHOLD - results[fid].reserve_ratio)
            share = min(available_support * (need / total_need), need)

            if share > 0:
                reserve.btc_reserve += share
                self.network_pool -= share
                support_given[fid] = share

        return support_given

    def process_all_epochs(self) -> Dict[str, DynamicFeeResult]:
        """Process epoch for all FoundUps.

        1. Collect overflow into Network Pool (tide out)
        2. Support CRITICAL F_i from Network Pool (tide in)

        Returns dict of foundup_id -> fee result.
        """
        results = {}
        total_overflow = 0.0

        # Phase 1: Process each F_i, collect overflow (tide out)
        for foundup_id, reserve in self.foundups.items():
            overflow_drip, result = reserve.process_epoch()  # Uses tier-based taper
            total_overflow += overflow_drip
            results[foundup_id] = result

        self.network_pool += total_overflow

        # Phase 2: Ecosystem tide balance - support CRITICAL F_i (tide in)
        support_given = self._ecosystem_tide_balance(results)

        # Log support if any given
        if support_given:
            for fid, amount in support_given.items():
                # Recalculate result after support
                reserve = self.foundups[fid]
                _, new_result = reserve.process_epoch()
                results[fid] = new_result

        self.epoch_count += 1
        return results

    def get_network_health(self) -> str:
        """Get overall network health summary."""
        if not self.foundups:
            return "NO_FOUNDUPS"

        statuses = [r.get_health().health_status for r in self.foundups.values()]
        critical_count = statuses.count("CRITICAL")
        overflow_count = statuses.count("OVERFLOW")

        if critical_count > len(statuses) / 2:
            return "NETWORK_STRESSED"
        elif overflow_count > len(statuses) / 2:
            return "NETWORK_THRIVING"
        else:
            return "NETWORK_BALANCED"

    def get_ecosystem_summary(self) -> dict:
        """Get comprehensive ecosystem summary.

        pAVS = TOTALITY of all treasuries functioning as math.
        Like treasuries/IMF but for FoundUps - tide-like balancing.
        """
        return {
            "total_foundups": len(self.foundups),
            "total_ecosystem_btc": self.total_ecosystem_btc,
            "total_ecosystem_sats": self.total_ecosystem_sats,
            "total_ecosystem_usd": btc_to_usd(self.total_ecosystem_btc),
            "network_pool_btc": self.network_pool,
            "network_pool_sats": int(self.network_pool * SATS_PER_BTC),
            "network_pool_usd": btc_to_usd(self.network_pool),
            "network_health": self.get_network_health(),
            "epoch_count": self.epoch_count,
            "tier_breakdown": {
                tier: len([r for r in self.foundups.values() if r.tier == tier])
                for tier in TIER_TREASURY_THRESHOLDS.keys()
            },
            "btc_usd_rate": BTC_USD_RATE,
        }


if __name__ == "__main__":
    print_taper_simulation()
    demo_hybrid_dynamic()

    # Demo fractal model with tier-based backing
    print("\n" + "=" * 80)
    print("FRACTAL TREASURY MODEL DEMO (TIER-BASED BACKING)")
    print("=" * 80)
    print("\n012-INSIGHT: System lends and returns like a tide.")
    print("             No competition - blue ocean. Like IMF but for FoundUps.")
    print("             pAVS = TOTALITY of all treasuries functioning as math.")

    manager = FractalTreasuryManager()

    # F_0 = Platform (F2_GROWTH tier - established platform)
    f0 = manager.register_foundup("F_0", tier="F2_GROWTH")
    f0.btc_reserve = 10.0  # 10 BTC = $1M @ $100K/BTC
    f0.mined_fi = 5_000_000
    f0.staked_fi = 5_000_000

    # F_1 = Strong FoundUp with paywalls (F1_OPO tier)
    f1 = manager.register_foundup("F_1", tier="F1_OPO")
    f1.btc_reserve = 1.5  # 1.5 BTC = $150K (above F1_OPO threshold)
    f1.mined_fi = 1_000_000
    f1.staked_fi = 1_000_000
    f1.paywall_revenue = 0.1  # Paywall income

    # F_2 = Weak FoundUp (early stage, F0_DAE tier)
    f2 = manager.register_foundup("F_2", tier="F0_DAE")
    f2.btc_reserve = 0.01  # 0.01 BTC = $1K (seed stage)
    f2.mined_fi = 100_000
    f2.staked_fi = 0

    # F_3 = CRITICAL FoundUp (will receive ecosystem support)
    f3 = manager.register_foundup("F_3", tier="F1_OPO")
    f3.btc_reserve = 0.001  # 0.001 BTC = $100 (CRITICAL - below threshold)
    f3.mined_fi = 500_000
    f3.staked_fi = 0

    # Seed the Network Pool (like IMF SDR reserves)
    manager.network_pool = 0.5  # 0.5 BTC from prior epoch overflows

    print(f"\n{'FoundUp':>8} {'Tier':>12} {'Reserve':>10} {'Target':>10} {'Sats/F_i':>10}")
    print("-" * 55)
    for fid, reserve in manager.foundups.items():
        print(
            f"{fid:>8} "
            f"{reserve.tier:>12} "
            f"{reserve.btc_reserve:>9.4f} "
            f"{reserve.treasury_target_btc:>9.2f} "
            f"{reserve.target_sats_per_fi:>9.2f}"
        )

    print(f"\nNetwork Pool (pre-epoch): {manager.network_pool:.4f} BTC")

    # Process epoch - this triggers tide (overflow out, support in)
    print("\n--- PROCESSING EPOCH (Tide Cycle) ---\n")
    results = manager.process_all_epochs()

    print(f"{'FoundUp':>8} {'Tier':>12} {'Reserve':>10} {'Health':>10} {'Fee':>8} {'Overflow':>10}")
    print("-" * 65)
    for fid, result in results.items():
        reserve = manager.foundups[fid]
        print(
            f"{fid:>8} "
            f"{reserve.tier:>12} "
            f"{reserve.btc_reserve:>9.4f} "
            f"{result.health_status:>10} "
            f"{result.effective_fee:>7.1%} "
            f"{result.overflow_btc:>9.4f}"
        )

    # Show ecosystem summary
    summary = manager.get_ecosystem_summary()
    print(f"\n{'=' * 65}")
    print("ECOSYSTEM SUMMARY (pAVS = TOTALITY)")
    print("Like treasuries/IMF - tide-like balancing across all F_i")
    print(f"{'=' * 65}")
    print(f"Total FoundUps:       {summary['total_foundups']}")
    print(f"Total Ecosystem BTC:  {summary['total_ecosystem_btc']:.6f} ({summary['total_ecosystem_sats']:,} sats)")
    print(f"Total Ecosystem USD:  ${summary['total_ecosystem_usd']:,.0f} (@ ${BTC_USD_RATE:,}/BTC)")
    print(f"Network Pool:         {summary['network_pool_btc']:.6f} BTC (${summary['network_pool_usd']:,.0f})")
    print(f"Network Health:       {summary['network_health']}")
    print(f"\nTier Breakdown: {summary['tier_breakdown']}")

    # Show tier reference
    print(f"\n{'=' * 65}")
    print("TIER BACKING REFERENCE (Target Treasury / 21M F_i)")
    print(f"{'=' * 65}")
    print(f"{'Tier':>12} {'Treasury':>15} {'USD':>15} {'Sats/F_i':>12}")
    print("-" * 58)
    for tier, sats in TIER_TREASURY_THRESHOLDS.items():
        usd = sats_to_usd(sats)
        sats_per_fi = get_target_sats_per_fi(tier)
        print(f"{tier:>12} {sats:>15,} ${usd:>13,.0f} {sats_per_fi:>11.2f}")
