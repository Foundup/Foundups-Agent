"""Fee Revenue Tracker - Tracks all fee flows in pAVS ecosystem.

Full Tide Economics Integration (012-approved 2026-02-17).

This module tracks:
1. DEX trading fees (2% per trade)
2. Exit fees (2-15% vesting-based)
3. Creation fees (3-11% mined vs staked)
4. Fee distribution to pools (F_i 50%, Network 30%, pAVS 20%)

Benchmarked against pump.fun real-world data:
- pump.fun: $3.5M/day at 1.25% fee
- pAVS: 1.8x revenue per volume (2% + exit + creation)

WSP References:
- WSP 26: Token economics
- WSP 29: CABR integration
- WSP 100: Tier escalation
"""

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Dict, List, Optional, Tuple, Callable
import logging

from .sustainability_scenarios import evaluate_scenario_pack

logger = logging.getLogger(__name__)


class FeeType(Enum):
    """Types of fees collected in pAVS."""
    DEX_TRADE = "dex_trade"           # 2% per trade
    EXIT_MINED = "exit_mined"          # 2-15% vesting (mined F_i)
    EXIT_STAKED = "exit_staked"        # 2-15% vesting (staked F_i)
    CREATION_MINED = "creation_mined"  # 11% on mined creation
    CREATION_STAKED = "creation_staked"  # 3% on staked creation


class FoundUpTier(Enum):
    """FoundUp tiers from WSP 100."""
    F0_DAE = "F0_DAE"           # Seed stage ($0)
    F1_OPO = "F1_OPO"           # $100K treasury
    F2_GROWTH = "F2_GROWTH"     # $1M treasury
    F3_INFRA = "F3_INFRA"       # $10M treasury
    F4_MEGA = "F4_MEGA"         # $100M treasury
    F5_SYSTEMIC = "F5_SYSTEMIC" # $1B treasury


# Treasury thresholds in satoshis (at $100K/BTC)
TIER_TREASURY_SATS = {
    FoundUpTier.F0_DAE: 0,
    FoundUpTier.F1_OPO: 100_000_000,        # 1 BTC
    FoundUpTier.F2_GROWTH: 1_000_000_000,   # 10 BTC
    FoundUpTier.F3_INFRA: 10_000_000_000,   # 100 BTC
    FoundUpTier.F4_MEGA: 100_000_000_000,   # 1K BTC
    FoundUpTier.F5_SYSTEMIC: 1_000_000_000_000,  # 10K BTC
}


# Fee rates
FEE_RATES = {
    FeeType.DEX_TRADE: 0.02,        # 2%
    FeeType.CREATION_MINED: 0.11,   # 11%
    FeeType.CREATION_STAKED: 0.03,  # 3%
}

# Vesting-based exit fee schedule
EXIT_FEE_SCHEDULE = {
    0: 0.15,    # 0 years: 15%
    1: 0.10,    # 1 year: 10%
    2: 0.07,    # 2 years: 7%
    4: 0.05,    # 4 years: 5%
    6: 0.03,    # 6 years: 3%
    8: 0.02,    # 8+ years: 2% (floor)
}

# Fee distribution splits
FEE_DISTRIBUTION = {
    "dex": {
        "fi_treasury": 0.50,    # 50% to specific F_i
        "network_pool": 0.30,   # 30% to Network Pool (tide)
        "pavs_treasury": 0.20,  # 20% to pAVS platform
    },
    "exit": {
        "btc_reserve": 0.80,    # 80% to BTC Reserve
        "network_pool": 0.20,   # 20% to Network Pool
    },
    "creation": {
        "fi_treasury": 1.00,    # 100% to that F_i's reserve
    },
}

# Sustainability guardrails (investor-conservative defaults)
DEFAULT_BREAK_EVEN_FOUNDUPS = 3500
MIN_SUSTAINABILITY_TICKS = 1440  # Require >= 1 simulated day before milestone.
MIN_SUSTAINABILITY_FOUNDUPS = 25


@dataclass
class FeeEvent:
    """A single fee collection event."""
    tick: int
    fee_type: FeeType
    foundup_id: str
    amount_sats: int
    volume_sats: int  # Original transaction volume
    metadata: Dict = field(default_factory=dict)


@dataclass
class FeeDistribution:
    """How a fee was distributed."""
    fee_event: FeeEvent
    fi_treasury_sats: int = 0
    network_pool_sats: int = 0
    pavs_treasury_sats: int = 0
    btc_reserve_sats: int = 0


@dataclass
class FoundUpFeeState:
    """Fee state for a single FoundUp."""
    foundup_id: str
    tier: FoundUpTier = FoundUpTier.F0_DAE
    treasury_sats: int = 0
    total_dex_volume_sats: int = 0
    total_dex_fees_sats: int = 0
    total_exit_fees_sats: int = 0
    total_creation_fees_sats: int = 0

    @property
    def total_fees_sats(self) -> int:
        return self.total_dex_fees_sats + self.total_exit_fees_sats + self.total_creation_fees_sats

    @property
    def daily_volume_estimate(self) -> int:
        """Estimate based on typical activity patterns."""
        # Activity multipliers by tier (from ecosystem_revenue.py)
        multipliers = {
            FoundUpTier.F0_DAE: 1,
            FoundUpTier.F1_OPO: 10,
            FoundUpTier.F2_GROWTH: 50,
            FoundUpTier.F3_INFRA: 200,
            FoundUpTier.F4_MEGA: 1000,
            FoundUpTier.F5_SYSTEMIC: 5000,
        }
        base_volume_sats = 100_000  # $1 equivalent per tick
        return base_volume_sats * multipliers.get(self.tier, 1)


@dataclass
class EcosystemFeeState:
    """Aggregate fee state for entire ecosystem."""
    tick: int = 0
    total_dex_volume_sats: int = 0
    total_dex_fees_sats: int = 0
    total_exit_fees_sats: int = 0
    total_creation_fees_sats: int = 0
    network_pool_sats: int = 0
    pavs_treasury_sats: int = 0
    btc_reserve_from_fees_sats: int = 0

    # Monthly burn for F_0 platform
    f0_monthly_burn_sats: int = 26_658_000  # ~$26.6K @ $100K/BTC

    @property
    def total_fees_sats(self) -> int:
        return self.total_dex_fees_sats + self.total_exit_fees_sats + self.total_creation_fees_sats

    @property
    def total_fees_btc(self) -> float:
        return self.total_fees_sats / 100_000_000

    @property
    def is_self_sustaining(self) -> bool:
        """True if fee revenue exceeds operational costs."""
        # Estimate daily revenue from total fees / ticks
        if self.tick == 0:
            return False
        daily_fees = (self.total_fees_sats / self.tick) * 1440  # Assuming 1 tick = 1 min
        daily_burn = self.f0_monthly_burn_sats / 30
        return daily_fees > daily_burn


class FeeRevenueTracker:
    """Tracks all fee revenue in pAVS ecosystem.

    This is the core fee tracking component integrated into mesa_model.py.

    Usage:
        tracker = FeeRevenueTracker()

        # On each DEX trade
        dist = tracker.record_dex_trade(tick, "foundup_001", volume_sats)

        # On each exit
        dist = tracker.record_exit(tick, "foundup_001", amount_sats, years_held, is_mined)

        # On F_i creation
        dist = tracker.record_creation(tick, "foundup_001", amount_sats, is_mined)

        # Get ecosystem metrics
        state = tracker.get_ecosystem_state()
    """

    def __init__(
        self,
        on_fee_collected: Optional[Callable[[FeeEvent, FeeDistribution], None]] = None,
    ):
        """Initialize the tracker.

        Args:
            on_fee_collected: Callback when fee is collected (for FAM events)
        """
        self._foundup_states: Dict[str, FoundUpFeeState] = {}
        self._ecosystem_state = EcosystemFeeState()
        self._fee_history: List[FeeDistribution] = []
        self._tick_totals: Dict[int, Dict[str, int]] = {}
        self._on_fee_collected = on_fee_collected
        self._fractional_fee_carry: Dict[str, float] = {
            "dex": 0.0,
            "exit": 0.0,
            "creation": 0.0,
        }

    def _quantize_fee_with_carry(self, raw_fee_sats: float, lane: str) -> int:
        """Convert fractional sat fees into integer sats without silent loss.

        Trades are often small in early simulations; naive int() truncation drops
        all sub-sat fees and materially understates treasury inflows. We carry
        residual fractions forward and realize whole sats once accumulated.
        """
        carried = self._fractional_fee_carry.get(lane, 0.0)
        total = max(0.0, raw_fee_sats) + carried
        quantized = int(total)
        self._fractional_fee_carry[lane] = total - quantized
        return quantized

    def _record_tick_totals(
        self,
        tick: int,
        dex_fee_sats: int = 0,
        exit_fee_sats: int = 0,
        creation_fee_sats: int = 0,
        dex_volume_sats: int = 0,
        dex_trade_count: int = 0,
        pavs_treasury_sats: int = 0,
        network_pool_sats: int = 0,
        btc_reserve_sats: int = 0,
    ) -> None:
        """Accumulate per-tick fee totals for rolling-window metrics."""
        bucket = self._tick_totals.setdefault(
            tick,
            {
                "dex_fee_sats": 0,
                "exit_fee_sats": 0,
                "creation_fee_sats": 0,
                "dex_volume_sats": 0,
                "dex_trade_count": 0,
                "pavs_treasury_sats": 0,
                "network_pool_sats": 0,
                "btc_reserve_sats": 0,
            },
        )
        bucket["dex_fee_sats"] += dex_fee_sats
        bucket["exit_fee_sats"] += exit_fee_sats
        bucket["creation_fee_sats"] += creation_fee_sats
        bucket["dex_volume_sats"] += dex_volume_sats
        bucket["dex_trade_count"] += dex_trade_count
        bucket["pavs_treasury_sats"] += pavs_treasury_sats
        bucket["network_pool_sats"] += network_pool_sats
        bucket["btc_reserve_sats"] += btc_reserve_sats

    def _get_window_totals(self, window_ticks: int) -> Dict[str, int]:
        """Return summed fee totals across trailing window_ticks."""
        current_tick = self._ecosystem_state.tick
        if current_tick <= 0:
            return {
                "ticks": 0,
                "dex_fee_sats": 0,
                "exit_fee_sats": 0,
                "creation_fee_sats": 0,
                "dex_volume_sats": 0,
                "dex_trade_count": 0,
                "pavs_treasury_sats": 0,
                "network_pool_sats": 0,
                "btc_reserve_sats": 0,
            }

        start_tick = max(1, current_tick - window_ticks + 1)
        totals = {
            "ticks": current_tick - start_tick + 1,
            "dex_fee_sats": 0,
            "exit_fee_sats": 0,
            "creation_fee_sats": 0,
            "dex_volume_sats": 0,
            "dex_trade_count": 0,
            "pavs_treasury_sats": 0,
            "network_pool_sats": 0,
            "btc_reserve_sats": 0,
        }
        for tick in range(start_tick, current_tick + 1):
            bucket = self._tick_totals.get(tick)
            if not bucket:
                continue
            totals["dex_fee_sats"] += bucket["dex_fee_sats"]
            totals["exit_fee_sats"] += bucket["exit_fee_sats"]
            totals["creation_fee_sats"] += bucket["creation_fee_sats"]
            totals["dex_volume_sats"] += bucket["dex_volume_sats"]
            totals["dex_trade_count"] += bucket["dex_trade_count"]
            totals["pavs_treasury_sats"] += bucket["pavs_treasury_sats"]
            totals["network_pool_sats"] += bucket["network_pool_sats"]
            totals["btc_reserve_sats"] += bucket["btc_reserve_sats"]
        return totals

    def _get_or_create_foundup(self, foundup_id: str) -> FoundUpFeeState:
        """Get or create FoundUp fee state."""
        if foundup_id not in self._foundup_states:
            self._foundup_states[foundup_id] = FoundUpFeeState(foundup_id=foundup_id)
        return self._foundup_states[foundup_id]

    def _calculate_exit_fee_rate(self, years_held: float) -> float:
        """Calculate exit fee rate based on vesting schedule."""
        # Find applicable rate
        for years, rate in sorted(EXIT_FEE_SCHEDULE.items(), reverse=True):
            if years_held >= years:
                return rate
        return EXIT_FEE_SCHEDULE[0]  # Default to highest rate

    def _distribute_dex_fee(self, fee_sats: int) -> Tuple[int, int, int]:
        """Distribute DEX fee to pools."""
        splits = FEE_DISTRIBUTION["dex"]
        fi_treasury = int(fee_sats * splits["fi_treasury"])
        network_pool = int(fee_sats * splits["network_pool"])
        pavs_treasury = fee_sats - fi_treasury - network_pool  # Remainder to pAVS
        return fi_treasury, network_pool, pavs_treasury

    def _distribute_exit_fee(self, fee_sats: int) -> Tuple[int, int]:
        """Distribute exit fee to pools."""
        splits = FEE_DISTRIBUTION["exit"]
        btc_reserve = int(fee_sats * splits["btc_reserve"])
        network_pool = fee_sats - btc_reserve  # Remainder to network
        return btc_reserve, network_pool

    def record_dex_trade(
        self,
        tick: int,
        foundup_id: str,
        volume_sats: int | float,
        source_ref: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> FeeDistribution:
        """Record a DEX trade and calculate fees.

        Args:
            tick: Current simulation tick
            foundup_id: ID of the FoundUp being traded
            volume_sats: Trade volume in satoshis
            source_ref: Optional unique source ID (trade_id/order_id) for dedupe-safe tracing
            metadata: Optional metadata (buyer, seller, etc.)

        Returns:
            FeeDistribution showing how fee was split
        """
        volume_sats_float = max(0.0, float(volume_sats))
        volume_sats_int = int(round(volume_sats_float))
        fee_rate = FEE_RATES[FeeType.DEX_TRADE]
        fee_sats = self._quantize_fee_with_carry(volume_sats_float * fee_rate, lane="dex")

        # Create event
        event = FeeEvent(
            tick=tick,
            fee_type=FeeType.DEX_TRADE,
            foundup_id=foundup_id,
            amount_sats=fee_sats,
            volume_sats=volume_sats_int,
            metadata={
                **(metadata or {}),
                **({"source_ref": source_ref} if source_ref else {}),
            },
        )

        # Distribute fee
        fi_treasury, network_pool, pavs_treasury = self._distribute_dex_fee(fee_sats)

        distribution = FeeDistribution(
            fee_event=event,
            fi_treasury_sats=fi_treasury,
            network_pool_sats=network_pool,
            pavs_treasury_sats=pavs_treasury,
        )

        # Update states
        foundup = self._get_or_create_foundup(foundup_id)
        foundup.total_dex_volume_sats += volume_sats_int
        foundup.total_dex_fees_sats += fee_sats
        foundup.treasury_sats += fi_treasury

        self._ecosystem_state.tick = tick
        self._ecosystem_state.total_dex_volume_sats += volume_sats_int
        self._ecosystem_state.total_dex_fees_sats += fee_sats
        self._ecosystem_state.network_pool_sats += network_pool
        self._ecosystem_state.pavs_treasury_sats += pavs_treasury
        self._record_tick_totals(
            tick=tick,
            dex_fee_sats=fee_sats,
            dex_volume_sats=volume_sats_int,
            dex_trade_count=1,
            pavs_treasury_sats=pavs_treasury,
            network_pool_sats=network_pool,
        )

        # Keep history/event sink focused on economically material events.
        if fee_sats <= 0:
            return distribution

        # Record history
        self._fee_history.append(distribution)

        # Callback
        if self._on_fee_collected:
            self._on_fee_collected(event, distribution)

        logger.debug(
            f"DEX trade: {foundup_id} vol={volume_sats} fee={fee_sats} "
            f"(fi={fi_treasury}, network={network_pool}, pavs={pavs_treasury})"
        )

        return distribution

    def record_exit(
        self,
        tick: int,
        foundup_id: str,
        amount_sats: int | float,
        years_held: float = 0.0,
        is_mined: bool = True,
        metadata: Optional[Dict] = None,
    ) -> FeeDistribution:
        """Record an F_i exit (swap to UPS then BTC).

        Args:
            tick: Current simulation tick
            foundup_id: ID of the FoundUp being exited
            amount_sats: Exit amount in satoshis
            years_held: Years held (affects fee rate)
            is_mined: True if mined F_i (vs staked)
            metadata: Optional metadata

        Returns:
            FeeDistribution showing how fee was split
        """
        amount_sats_float = max(0.0, float(amount_sats))
        fee_rate = self._calculate_exit_fee_rate(years_held)
        fee_sats = self._quantize_fee_with_carry(amount_sats_float * fee_rate, lane="exit")

        fee_type = FeeType.EXIT_MINED if is_mined else FeeType.EXIT_STAKED

        # Create event
        event = FeeEvent(
            tick=tick,
            fee_type=fee_type,
            foundup_id=foundup_id,
            amount_sats=fee_sats,
            volume_sats=int(round(amount_sats_float)),
            metadata={**(metadata or {}), "years_held": years_held, "fee_rate": fee_rate},
        )

        # Distribute fee (exit goes to BTC reserve + network pool)
        btc_reserve, network_pool = self._distribute_exit_fee(fee_sats)

        distribution = FeeDistribution(
            fee_event=event,
            btc_reserve_sats=btc_reserve,
            network_pool_sats=network_pool,
        )

        # Update states
        foundup = self._get_or_create_foundup(foundup_id)
        foundup.total_exit_fees_sats += fee_sats

        self._ecosystem_state.tick = tick
        self._ecosystem_state.total_exit_fees_sats += fee_sats
        self._ecosystem_state.network_pool_sats += network_pool
        self._ecosystem_state.btc_reserve_from_fees_sats += btc_reserve
        self._record_tick_totals(
            tick=tick,
            exit_fee_sats=fee_sats,
            network_pool_sats=network_pool,
            btc_reserve_sats=btc_reserve,
        )

        if fee_sats <= 0:
            return distribution

        # Record history
        self._fee_history.append(distribution)

        # Callback
        if self._on_fee_collected:
            self._on_fee_collected(event, distribution)

        logger.debug(
            f"Exit: {foundup_id} amt={amount_sats} fee={fee_sats} "
            f"(btc={btc_reserve}, network={network_pool}) years={years_held}"
        )

        return distribution

    def record_creation(
        self,
        tick: int,
        foundup_id: str,
        amount_sats: int | float,
        is_mined: bool = True,
        metadata: Optional[Dict] = None,
    ) -> FeeDistribution:
        """Record F_i creation fee.

        Args:
            tick: Current simulation tick
            foundup_id: ID of the new FoundUp
            amount_sats: Amount being created
            is_mined: True if mined (11%) vs staked (3%)
            metadata: Optional metadata

        Returns:
            FeeDistribution showing how fee was split
        """
        amount_sats_float = max(0.0, float(amount_sats))
        fee_type = FeeType.CREATION_MINED if is_mined else FeeType.CREATION_STAKED
        fee_rate = FEE_RATES[fee_type]
        fee_sats = self._quantize_fee_with_carry(amount_sats_float * fee_rate, lane="creation")

        # Create event
        event = FeeEvent(
            tick=tick,
            fee_type=fee_type,
            foundup_id=foundup_id,
            amount_sats=fee_sats,
            volume_sats=int(round(amount_sats_float)),
            metadata=metadata or {},
        )

        # Creation fees go 100% to F_i treasury
        distribution = FeeDistribution(
            fee_event=event,
            fi_treasury_sats=fee_sats,
        )

        # Update states
        foundup = self._get_or_create_foundup(foundup_id)
        foundup.total_creation_fees_sats += fee_sats
        foundup.treasury_sats += fee_sats

        self._ecosystem_state.tick = tick
        self._ecosystem_state.total_creation_fees_sats += fee_sats
        self._record_tick_totals(
            tick=tick,
            creation_fee_sats=fee_sats,
        )

        if fee_sats <= 0:
            return distribution

        # Record history
        self._fee_history.append(distribution)

        # Callback
        if self._on_fee_collected:
            self._on_fee_collected(event, distribution)

        logger.debug(
            f"Creation: {foundup_id} amt={amount_sats} fee={fee_sats} "
            f"({'mined' if is_mined else 'staked'})"
        )

        return distribution

    def get_foundup_state(self, foundup_id: str) -> Optional[FoundUpFeeState]:
        """Get fee state for a specific FoundUp."""
        return self._foundup_states.get(foundup_id)

    def get_ecosystem_state(self) -> EcosystemFeeState:
        """Get aggregate ecosystem fee state."""
        return self._ecosystem_state

    def get_fee_history(
        self,
        fee_type: Optional[FeeType] = None,
        foundup_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[FeeDistribution]:
        """Get fee history with optional filters."""
        result = self._fee_history

        if fee_type:
            result = [d for d in result if d.fee_event.fee_type == fee_type]

        if foundup_id:
            result = [d for d in result if d.fee_event.foundup_id == foundup_id]

        return result[-limit:]

    def get_daily_revenue_estimate(self, window_ticks: int = MIN_SUSTAINABILITY_TICKS) -> Dict[str, float]:
        """Estimate daily revenue based on current state.

        Returns dict with BTC values.
        """
        state = self._ecosystem_state
        if state.tick == 0:
            return {"dex": 0, "exit": 0, "creation": 0, "total": 0}

        # Assume 1 tick = 1 minute, 1440 ticks = 1 day.
        # Use trailing window for conservative, adaptive estimates.
        ticks_per_day = 1440
        window = self._get_window_totals(window_ticks=window_ticks)
        observed_ticks = max(1, window["ticks"])

        daily_dex = (window["dex_fee_sats"] / observed_ticks) * ticks_per_day / 100_000_000
        daily_exit = (window["exit_fee_sats"] / observed_ticks) * ticks_per_day / 100_000_000
        daily_creation = (window["creation_fee_sats"] / observed_ticks) * ticks_per_day / 100_000_000

        return {
            "dex": daily_dex,
            "exit": daily_exit,
            "creation": daily_creation,
            "total": daily_dex + daily_exit + daily_creation,
        }

    def get_sustainability_metrics(self) -> Dict:
        """Get metrics related to ecosystem self-sustainability.

        Based on pump.fun validation: ecosystem is self-sustaining
        when captured fee revenue > operational costs.

        Conservative policy:
        - Milestone gating uses pAVS treasury capture only.
        - Gross fee flows are still reported for observability.
        - Sustainability requires a minimum observation window.
        """
        state = self._ecosystem_state
        ticks_per_day = 1440
        daily_revenue = self.get_daily_revenue_estimate(window_ticks=MIN_SUSTAINABILITY_TICKS)
        window = self._get_window_totals(window_ticks=MIN_SUSTAINABILITY_TICKS)
        observed_ticks = max(1, window["ticks"])

        # Monthly burn for F_0 platform (from tracker state).
        f0_monthly_burn_btc = state.f0_monthly_burn_sats / 100_000_000
        f0_daily_burn_btc = f0_monthly_burn_btc / 30

        pavs_daily_btc = (window["pavs_treasury_sats"] / observed_ticks) * ticks_per_day / 100_000_000
        network_daily_btc = (window["network_pool_sats"] / observed_ticks) * ticks_per_day / 100_000_000
        reserve_daily_btc = (window["btc_reserve_sats"] / observed_ticks) * ticks_per_day / 100_000_000
        protocol_capture_daily_btc = pavs_daily_btc + network_daily_btc + reserve_daily_btc

        # Conservative gate: platform ops are paid by pAVS treasury.
        revenue_cost_ratio = (
            pavs_daily_btc / f0_daily_burn_btc if f0_daily_burn_btc > 0 else 0.0
        )
        protocol_capture_ratio = (
            protocol_capture_daily_btc / f0_daily_burn_btc if f0_daily_burn_btc > 0 else 0.0
        )

        # Estimated FoundUps needed for sustainability.
        # Use dynamic estimate from observed pAVS capture per FoundUp when possible.
        # Fallback to DEFAULT_BREAK_EVEN_FOUNDUPS when sample is too small.
        fi_count = len(self._foundup_states)
        per_foundup_capture_daily_btc = pavs_daily_btc / fi_count if fi_count > 0 else 0.0
        estimated_break_even_fi = DEFAULT_BREAK_EVEN_FOUNDUPS
        if per_foundup_capture_daily_btc > 0 and f0_daily_burn_btc > 0:
            estimated_break_even_fi = max(
                1,
                math.ceil(f0_daily_burn_btc / per_foundup_capture_daily_btc),
            )

        # Require minimum sample maturity before asserting sustainability.
        has_min_samples = (
            state.tick >= MIN_SUSTAINABILITY_TICKS
            and fi_count >= MIN_SUSTAINABILITY_FOUNDUPS
        )
        is_self_sustaining_raw = revenue_cost_ratio >= 1.0
        is_self_sustaining_protocol_capture_raw = protocol_capture_ratio >= 1.0
        is_self_sustaining_base_gate = is_self_sustaining_raw and has_min_samples
        is_self_sustaining_protocol_capture_base = (
            is_self_sustaining_protocol_capture_raw and has_min_samples
        )

        avg_trade_volume_sats = (
            window["dex_volume_sats"] / max(1, window["dex_trade_count"])
            if window["dex_trade_count"] > 0
            else 0.0
        )
        scenario_pack = evaluate_scenario_pack(
            daily_dex_fee_btc=daily_revenue["dex"],
            daily_exit_fee_btc=daily_revenue["exit"],
            daily_creation_fee_btc=daily_revenue["creation"],
            burn_btc=f0_daily_burn_btc,
            foundup_count=fi_count,
            network_pool_btc=state.network_pool_sats / 100_000_000,
            avg_trade_volume_sats=avg_trade_volume_sats,
            fee_rate=FEE_RATES[FeeType.DEX_TRADE],
        )
        downside = scenario_pack.get("downside", {})
        downside_ratio_p10 = float(downside.get("revenue_cost_ratio_p10", 0.0))
        is_self_sustaining_downside = has_min_samples and downside_ratio_p10 >= 1.0

        # Final claim gate: must pass conservative base gate and downside p10.
        is_self_sustaining_claim = is_self_sustaining_base_gate and is_self_sustaining_downside

        return {
            "tick": state.tick,
            "foundup_count": fi_count,
            "daily_revenue_btc": pavs_daily_btc,  # conservative capture for ops gate
            "gross_daily_revenue_btc": daily_revenue["total"],
            "protocol_capture_daily_btc": protocol_capture_daily_btc,
            "daily_burn_btc": f0_daily_burn_btc,
            "revenue_cost_ratio": revenue_cost_ratio,
            "protocol_capture_ratio": protocol_capture_ratio,
            "is_self_sustaining_raw": is_self_sustaining_raw,
            "is_self_sustaining_protocol_capture_raw": is_self_sustaining_protocol_capture_raw,
            "is_self_sustaining_base_gate": is_self_sustaining_base_gate,
            "is_self_sustaining_protocol_capture_base": is_self_sustaining_protocol_capture_base,
            "is_self_sustaining_downside": is_self_sustaining_downside,
            "is_self_sustaining_claim": is_self_sustaining_claim,
            "is_self_sustaining": is_self_sustaining_claim,
            "is_self_sustaining_protocol_capture": is_self_sustaining_protocol_capture_base,
            "has_min_sample_window": has_min_samples,
            "min_sustainability_ticks": MIN_SUSTAINABILITY_TICKS,
            "min_sustainability_foundups": MIN_SUSTAINABILITY_FOUNDUPS,
            "observation_days": state.tick / ticks_per_day if ticks_per_day > 0 else 0.0,
            "estimated_break_even_fi": estimated_break_even_fi,
            "progress_to_sustainability": fi_count / estimated_break_even_fi,
            "avg_trade_volume_sats": avg_trade_volume_sats,
            "scenario_pack": scenario_pack,
            "downside_revenue_cost_ratio_p10": downside_ratio_p10,
            "network_pool_btc": state.network_pool_sats / 100_000_000,
            "pavs_treasury_btc": state.pavs_treasury_sats / 100_000_000,
            "btc_reserve_from_fees_btc": state.btc_reserve_from_fees_sats / 100_000_000,
        }

    def update_foundup_tier(self, foundup_id: str, tier: FoundUpTier) -> None:
        """Update a FoundUp's tier (affects activity estimates)."""
        foundup = self._get_or_create_foundup(foundup_id)
        foundup.tier = tier


# Module-level singleton for integration
_fee_tracker: Optional[FeeRevenueTracker] = None


def get_fee_tracker() -> FeeRevenueTracker:
    """Get the singleton FeeRevenueTracker."""
    global _fee_tracker
    if _fee_tracker is None:
        _fee_tracker = FeeRevenueTracker()
    return _fee_tracker


def reset_fee_tracker() -> None:
    """Reset the singleton (for testing)."""
    global _fee_tracker
    _fee_tracker = None


if __name__ == "__main__":
    # Quick demo
    tracker = FeeRevenueTracker()

    # Simulate some trades
    for tick in range(100):
        # DEX trades
        tracker.record_dex_trade(tick, "foundup_001", 100_000)
        tracker.record_dex_trade(tick, "foundup_002", 500_000)

        # Some exits
        if tick % 10 == 0:
            tracker.record_exit(tick, "foundup_001", 50_000, years_held=2.5)

        # Some creations
        if tick % 20 == 0:
            tracker.record_creation(tick, "foundup_003", 1_000_000, is_mined=True)

    # Print results
    state = tracker.get_ecosystem_state()
    print(f"\nEcosystem Fee State after {state.tick} ticks:")
    print(f"  Total DEX volume: {state.total_dex_volume_sats:,} sats")
    print(f"  Total DEX fees: {state.total_dex_fees_sats:,} sats")
    print(f"  Total exit fees: {state.total_exit_fees_sats:,} sats")
    print(f"  Total creation fees: {state.total_creation_fees_sats:,} sats")
    print(f"  Network Pool: {state.network_pool_sats:,} sats")
    print(f"  pAVS Treasury: {state.pavs_treasury_sats:,} sats")
    print(f"  BTC Reserve (from fees): {state.btc_reserve_from_fees_sats:,} sats")

    metrics = tracker.get_sustainability_metrics()
    print(f"\nSustainability Metrics:")
    print(f"  FoundUp count: {metrics['foundup_count']}")
    print(f"  Daily revenue: {metrics['daily_revenue_btc']:.4f} BTC")
    print(f"  Daily burn: {metrics['daily_burn_btc']:.4f} BTC")
    print(f"  Revenue/Cost ratio: {metrics['revenue_cost_ratio']:.2f}x")
    print(f"  Self-sustaining: {metrics['is_self_sustaining']}")
    print(f"  Progress to sustainability: {metrics['progress_to_sustainability']*100:.1f}%")
