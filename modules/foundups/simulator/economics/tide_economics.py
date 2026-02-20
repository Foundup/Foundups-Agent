"""Tide Economics Engine - IMF-like ecosystem balancing for pAVS.

Full Tide Integration (012-approved 2026-02-17).

012 INSIGHT: "The system lends and returns ebbing like a tide...
there is no competition in foundups is a blue ocean strategy...
if costs go up it all balances... think of treasuries and IMF but for FoundUps"

This module implements:
1. TIDE OUT: Overflow from healthy F_i drips to Network Pool
2. TIDE IN: Network Pool supports CRITICAL F_i
3. Blue Ocean: No F_i is an island - all connected via tide

WSP References:
- WSP 26: Token economics
- WSP 100: Tier escalation
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Callable, Tuple
import logging

logger = logging.getLogger(__name__)


class TreasuryHealth(Enum):
    """Health status of a FoundUp treasury."""
    CRITICAL = "CRITICAL"       # < 5% of target, needs support
    BUILDING = "BUILDING"       # 5-50% of target, growing
    HEALTHY = "HEALTHY"         # 50-80% of target, normal
    STRONG = "STRONG"           # 80-100% of target, good
    OVERFLOW = "OVERFLOW"       # > 100% of target, can contribute


class NetworkHealth(Enum):
    """Health status of Network Pool."""
    DEPLETED = "DEPLETED"       # < 10% of target, crisis
    LOW = "LOW"                 # 10-30%, cautious
    ADEQUATE = "ADEQUATE"       # 30-70%, normal operations
    THRIVING = "THRIVING"       # > 70%, can be generous


# Tier thresholds in sats (same as fee_revenue_tracker.py)
TIER_TREASURY_TARGETS = {
    "F0_DAE": 0,
    "F1_OPO": 100_000_000,        # 1 BTC
    "F2_GROWTH": 1_000_000_000,   # 10 BTC
    "F3_INFRA": 10_000_000_000,   # 100 BTC
    "F4_MEGA": 100_000_000_000,   # 1K BTC
    "F5_SYSTEMIC": 1_000_000_000_000,  # 10K BTC
}

# Tide parameters
TIDE_CONFIG = {
    "support_threshold": 0.05,    # Support if reserve ratio < 5%
    "overflow_threshold": 1.00,   # Drip to network if > 100%
    "support_rate": 0.10,         # 10% of Network Pool per CRITICAL F_i
    "overflow_drip_rate": 0.01,   # 1% of overflow drips per epoch
    "max_support_per_epoch": 0.25,  # Max 25% of Network Pool used per epoch
    "min_network_reserve": 0.10,  # Keep at least 10% in Network Pool
}


@dataclass
class FoundUpTreasuryState:
    """State of a single FoundUp's treasury."""
    foundup_id: str
    tier: str = "F1_OPO"
    treasury_sats: int = 0
    target_sats: int = 100_000_000  # Default: F1_OPO

    @property
    def reserve_ratio(self) -> float:
        """Treasury / Target ratio."""
        if self.target_sats == 0:
            return 1.0  # F0_DAE has no requirement
        return self.treasury_sats / self.target_sats

    @property
    def health(self) -> TreasuryHealth:
        """Current health status."""
        ratio = self.reserve_ratio
        if ratio < 0.05:
            return TreasuryHealth.CRITICAL
        elif ratio < 0.50:
            return TreasuryHealth.BUILDING
        elif ratio < 0.80:
            return TreasuryHealth.HEALTHY
        elif ratio <= 1.00:
            return TreasuryHealth.STRONG
        else:
            return TreasuryHealth.OVERFLOW

    @property
    def overflow_sats(self) -> int:
        """Amount above target (for tide-out)."""
        if self.treasury_sats > self.target_sats:
            return self.treasury_sats - self.target_sats
        return 0

    @property
    def deficit_sats(self) -> int:
        """Amount below 5% target (for tide-in)."""
        min_threshold = int(self.target_sats * TIDE_CONFIG["support_threshold"])
        if self.treasury_sats < min_threshold:
            return min_threshold - self.treasury_sats
        return 0


@dataclass
class TideEvent:
    """A single tide flow event."""
    tick: int
    event_type: str  # "tide_in" or "tide_out"
    foundup_id: str
    amount_sats: int
    from_source: str  # "network_pool" or foundup_id
    to_destination: str  # "network_pool" or foundup_id
    reason: str


@dataclass
class TideEpochResult:
    """Result of processing one tide epoch."""
    tick: int
    tide_in_total_sats: int = 0
    tide_out_total_sats: int = 0
    critical_foundups: int = 0
    overflow_foundups: int = 0
    supported_foundups: List[str] = field(default_factory=list)
    contributing_foundups: List[str] = field(default_factory=list)
    events: List[TideEvent] = field(default_factory=list)


class TideEconomicsEngine:
    """IMF-like ecosystem balancing engine.

    The tide ebbs and flows:
    - TIDE OUT: Overflow F_i contribute to Network Pool
    - TIDE IN: Network Pool supports CRITICAL F_i
    - No competition: Blue ocean strategy

    Usage:
        engine = TideEconomicsEngine(
            on_tide_event=lambda e: print(f"Tide: {e}")
        )

        # Register FoundUps
        engine.register_foundup("f_001", tier="F1_OPO", treasury_sats=50_000_000)

        # Process tide epoch
        result = engine.process_epoch(tick=100)

        # Check ecosystem state
        metrics = engine.get_ecosystem_metrics()
    """

    def __init__(
        self,
        initial_network_pool_sats: int = 0,
        on_tide_event: Optional[Callable[[TideEvent], None]] = None,
    ):
        """Initialize the engine.

        Args:
            initial_network_pool_sats: Starting Network Pool balance
            on_tide_event: Callback for each tide flow event
        """
        self._foundups: Dict[str, FoundUpTreasuryState] = {}
        self._network_pool_sats: int = initial_network_pool_sats
        self._on_tide_event = on_tide_event
        self._tide_history: List[TideEpochResult] = []

        # Cumulative metrics
        self._total_tide_in_sats: int = 0
        self._total_tide_out_sats: int = 0
        self._times_supported: Dict[str, int] = {}  # How many times each F_i was supported

    def register_foundup(
        self,
        foundup_id: str,
        tier: str = "F1_OPO",
        treasury_sats: int = 0,
    ) -> FoundUpTreasuryState:
        """Register a FoundUp with the tide system."""
        target = TIER_TREASURY_TARGETS.get(tier, TIER_TREASURY_TARGETS["F1_OPO"])
        state = FoundUpTreasuryState(
            foundup_id=foundup_id,
            tier=tier,
            treasury_sats=treasury_sats,
            target_sats=target,
        )
        self._foundups[foundup_id] = state
        return state

    def update_treasury(self, foundup_id: str, treasury_sats: int) -> None:
        """Update a FoundUp's treasury balance."""
        if foundup_id in self._foundups:
            self._foundups[foundup_id].treasury_sats = treasury_sats

    def update_tier(self, foundup_id: str, tier: str) -> None:
        """Update a FoundUp's tier (changes target)."""
        if foundup_id in self._foundups:
            target = TIER_TREASURY_TARGETS.get(tier, TIER_TREASURY_TARGETS["F1_OPO"])
            self._foundups[foundup_id].tier = tier
            self._foundups[foundup_id].target_sats = target

    def add_to_network_pool(self, amount_sats: int) -> None:
        """Add sats to Network Pool (from fees, etc.)."""
        self._network_pool_sats += amount_sats

    def get_network_pool(self) -> int:
        """Get current Network Pool balance."""
        return self._network_pool_sats

    def get_network_health(self) -> NetworkHealth:
        """Get Network Pool health status."""
        # Network Pool target = sum of all F_i targets * 10%
        total_fi_targets = sum(f.target_sats for f in self._foundups.values())
        network_target = max(total_fi_targets * 0.10, 10_000_000)  # Min 0.1 BTC

        ratio = self._network_pool_sats / network_target if network_target > 0 else 1.0

        if ratio < 0.10:
            return NetworkHealth.DEPLETED
        elif ratio < 0.30:
            return NetworkHealth.LOW
        elif ratio < 0.70:
            return NetworkHealth.ADEQUATE
        else:
            return NetworkHealth.THRIVING

    def _identify_critical_foundups(self) -> List[FoundUpTreasuryState]:
        """Find F_i that need support (CRITICAL status)."""
        return [
            f for f in self._foundups.values()
            if f.health == TreasuryHealth.CRITICAL
        ]

    def _identify_overflow_foundups(self) -> List[FoundUpTreasuryState]:
        """Find F_i that can contribute (OVERFLOW status)."""
        return [
            f for f in self._foundups.values()
            if f.health == TreasuryHealth.OVERFLOW
        ]

    def _calculate_support_amount(
        self,
        foundup: FoundUpTreasuryState,
        available_pool: int,
    ) -> int:
        """Calculate how much support a CRITICAL F_i should receive."""
        # Support up to bring them to 5% threshold
        deficit = foundup.deficit_sats

        # But limited by support rate and available pool
        max_support = int(available_pool * TIDE_CONFIG["support_rate"])

        return min(deficit, max_support)

    def _calculate_overflow_drip(self, foundup: FoundUpTreasuryState) -> int:
        """Calculate how much a OVERFLOW F_i should contribute."""
        overflow = foundup.overflow_sats
        drip = int(overflow * TIDE_CONFIG["overflow_drip_rate"])
        return drip

    def process_epoch(self, tick: int) -> TideEpochResult:
        """Process one tide epoch.

        This is called periodically (e.g., every 100 ticks) to balance
        the ecosystem.

        Returns:
            TideEpochResult with all tide flows for this epoch
        """
        result = TideEpochResult(tick=tick)

        # Phase 1: TIDE OUT - Overflow F_i contribute to Network Pool
        overflow_foundups = self._identify_overflow_foundups()
        result.overflow_foundups = len(overflow_foundups)

        for foundup in overflow_foundups:
            drip = self._calculate_overflow_drip(foundup)
            if drip > 0:
                # Transfer from F_i to Network Pool
                foundup.treasury_sats -= drip
                self._network_pool_sats += drip
                result.tide_out_total_sats += drip
                self._total_tide_out_sats += drip
                result.contributing_foundups.append(foundup.foundup_id)

                event = TideEvent(
                    tick=tick,
                    event_type="tide_out",
                    foundup_id=foundup.foundup_id,
                    amount_sats=drip,
                    from_source=foundup.foundup_id,
                    to_destination="network_pool",
                    reason=f"OVERFLOW drip ({foundup.reserve_ratio:.1%} > 100%)",
                )
                result.events.append(event)

                if self._on_tide_event:
                    self._on_tide_event(event)

        # Phase 2: TIDE IN - Network Pool supports CRITICAL F_i
        critical_foundups = self._identify_critical_foundups()
        result.critical_foundups = len(critical_foundups)

        # Limit total support per epoch
        max_epoch_support = int(self._network_pool_sats * TIDE_CONFIG["max_support_per_epoch"])
        min_reserve = int(self._network_pool_sats * TIDE_CONFIG["min_network_reserve"])
        available_support = max(0, self._network_pool_sats - min_reserve)
        available_support = min(available_support, max_epoch_support)

        # Sort by severity (lowest ratio first)
        critical_foundups.sort(key=lambda f: f.reserve_ratio)

        for foundup in critical_foundups:
            if available_support <= 0:
                break

            support = self._calculate_support_amount(foundup, available_support)
            if support > 0:
                # Transfer from Network Pool to F_i
                self._network_pool_sats -= support
                foundup.treasury_sats += support
                result.tide_in_total_sats += support
                self._total_tide_in_sats += support
                available_support -= support
                result.supported_foundups.append(foundup.foundup_id)

                # Track support count
                self._times_supported[foundup.foundup_id] = (
                    self._times_supported.get(foundup.foundup_id, 0) + 1
                )

                event = TideEvent(
                    tick=tick,
                    event_type="tide_in",
                    foundup_id=foundup.foundup_id,
                    amount_sats=support,
                    from_source="network_pool",
                    to_destination=foundup.foundup_id,
                    reason=f"CRITICAL support ({foundup.reserve_ratio:.1%} < 5%)",
                )
                result.events.append(event)

                if self._on_tide_event:
                    self._on_tide_event(event)

        # Record history
        self._tide_history.append(result)

        logger.info(
            f"Tide epoch {tick}: "
            f"OUT={result.tide_out_total_sats} sats from {result.overflow_foundups} F_i, "
            f"IN={result.tide_in_total_sats} sats to {result.critical_foundups} F_i"
        )

        return result

    def get_foundup_state(self, foundup_id: str) -> Optional[FoundUpTreasuryState]:
        """Get state of a specific FoundUp."""
        return self._foundups.get(foundup_id)

    def get_all_foundups(self) -> List[FoundUpTreasuryState]:
        """Get all registered FoundUps."""
        return list(self._foundups.values())

    def get_ecosystem_metrics(self) -> Dict:
        """Get comprehensive ecosystem metrics."""
        foundups = list(self._foundups.values())

        health_counts = {h: 0 for h in TreasuryHealth}
        for f in foundups:
            health_counts[f.health] += 1

        total_treasury = sum(f.treasury_sats for f in foundups)
        total_target = sum(f.target_sats for f in foundups)
        avg_ratio = total_treasury / total_target if total_target > 0 else 0

        return {
            "foundup_count": len(foundups),
            "network_pool_sats": self._network_pool_sats,
            "network_pool_btc": self._network_pool_sats / 100_000_000,
            "network_health": self.get_network_health().value,
            "total_treasury_sats": total_treasury,
            "total_treasury_btc": total_treasury / 100_000_000,
            "total_target_sats": total_target,
            "average_reserve_ratio": avg_ratio,
            "health_distribution": {h.value: c for h, c in health_counts.items()},
            "total_tide_in_sats": self._total_tide_in_sats,
            "total_tide_out_sats": self._total_tide_out_sats,
            "tide_epochs_processed": len(self._tide_history),
            "most_supported_foundups": sorted(
                self._times_supported.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5],
        }

    def get_tide_history(self, limit: int = 10) -> List[TideEpochResult]:
        """Get recent tide epoch results."""
        return self._tide_history[-limit:]


# Module-level singleton
_tide_engine: Optional[TideEconomicsEngine] = None


def get_tide_engine() -> TideEconomicsEngine:
    """Get the singleton TideEconomicsEngine."""
    global _tide_engine
    if _tide_engine is None:
        _tide_engine = TideEconomicsEngine()
    return _tide_engine


def reset_tide_engine() -> None:
    """Reset the singleton (for testing)."""
    global _tide_engine
    _tide_engine = None


if __name__ == "__main__":
    # Demo the tide system
    engine = TideEconomicsEngine(initial_network_pool_sats=500_000_000)  # 5 BTC

    # Register some FoundUps at different states
    engine.register_foundup("f_001", tier="F1_OPO", treasury_sats=150_000_000)  # 150% (OVERFLOW)
    engine.register_foundup("f_002", tier="F1_OPO", treasury_sats=80_000_000)   # 80% (STRONG)
    engine.register_foundup("f_003", tier="F1_OPO", treasury_sats=2_000_000)    # 2% (CRITICAL)
    engine.register_foundup("f_004", tier="F1_OPO", treasury_sats=30_000_000)   # 30% (BUILDING)
    engine.register_foundup("f_005", tier="F2_GROWTH", treasury_sats=20_000_000)  # 2% of 10 BTC (CRITICAL)

    print("=" * 80)
    print("TIDE ECONOMICS DEMO")
    print("=" * 80)

    print("\nInitial State:")
    for f in engine.get_all_foundups():
        print(f"  {f.foundup_id}: {f.treasury_sats/100_000_000:.2f} BTC "
              f"({f.reserve_ratio:.1%}) - {f.health.value}")
    print(f"  Network Pool: {engine.get_network_pool()/100_000_000:.2f} BTC")

    # Process a few epochs
    for epoch in range(5):
        print(f"\n--- Epoch {epoch+1} ---")
        result = engine.process_epoch(tick=epoch * 100)

        if result.events:
            for event in result.events:
                print(f"  {event.event_type.upper()}: {event.amount_sats/100_000_000:.4f} BTC "
                      f"({event.from_source} -> {event.to_destination})")

    print("\n" + "=" * 80)
    print("FINAL STATE")
    print("=" * 80)

    print("\nFoundUps:")
    for f in engine.get_all_foundups():
        times_supported = engine._times_supported.get(f.foundup_id, 0)
        print(f"  {f.foundup_id}: {f.treasury_sats/100_000_000:.4f} BTC "
              f"({f.reserve_ratio:.1%}) - {f.health.value}"
              + (f" [supported {times_supported}x]" if times_supported else ""))

    print(f"\nNetwork Pool: {engine.get_network_pool()/100_000_000:.4f} BTC "
          f"({engine.get_network_health().value})")

    metrics = engine.get_ecosystem_metrics()
    print(f"\nEcosystem Metrics:")
    print(f"  Total tide IN:  {metrics['total_tide_in_sats']/100_000_000:.4f} BTC")
    print(f"  Total tide OUT: {metrics['total_tide_out_sats']/100_000_000:.4f} BTC")
    print(f"  Health distribution: {metrics['health_distribution']}")
