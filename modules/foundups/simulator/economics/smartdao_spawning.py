"""SmartDAO Spawning Economics - Reserve overflow funds next-tier FoundUps.

012-CONFIRMED MODEL (2026-02-17):

FOUNDUP LIFECYCLE (Startup → IPO equivalent):
  STARTUP:  Seed → Series A → ... → IPO (public offering)
  FOUNDUP:  IDEA → PoC → Proto → MVP → [Early Adopters] → OPO → DAO Satellite

  OPO = Open Public Offering (at 16% adoption = Early Majority threshold)
  - S-curve ONLY covers Early Adopters stage (0-16%)
  - At 16%: OPO triggers → FoundUp becomes ungated DAO satellite
  - Community decides via 0102 agents (thresholds are guidelines, not fixed)

ALL FOUNDUPS WORK LIKE MOLTBOOK:
  - 012 digital twin = 0102 (agent proxy)
  - 012 talks with 0102 → 0102 executes
  - No human executives - fully autonomous

FRACTAL STRUCTURE:
  - F_0 is pAVS template that DUPES into every F_i
  - F_i gains traction → OPO → becomes SmartDAO (F_1)
  - SmartDAO uses reserve overflow to spawn next-tier FoundUps
  - Recursive: F_i → SmartDAO → spawns F_j → F_j → SmartDAO → spawns F_k

Math Integration with dynamic_fee_taper.py:
- Overflow from any F_i goes to Network Pool OR to SmartDAO spawning fund
- SmartDAO reserves split: 80% own operations, 20% spawning fund
- Spawning fund accumulates until spawn_threshold reached
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math


class DAOTier(Enum):
    """SmartDAO tier levels (WSP 100 Section 1.3).

    FoundUp lifecycle mirrors Startup → IPO:
      F0_DAE:  Gated/invite-only (Early Adopters stage, S-curve 0-16%)
      F1_OPO:  Open Public Offering → becomes DAO Satellite (ungated)
      F2+:     Tiered growth as autonomous SmartDAO
    """
    F0_DAE = 0           # FoundUp (DAE) - Gated, invite-only, Early Adopters
    F1_OPO = 1           # OPO (Open Public Offering) - Ungated DAO Satellite
    F2_GROWTH = 2        # Growth SmartDAO - Domain specialization
    F3_INFRA = 3         # Infrastructure SmartDAO - Large-scale
    F4_MEGA = 4          # Mega SmartDAO - Unicorn
    F5_SYSTEMIC = 5      # Systemic SmartDAO - Global impact


# Tier escalation thresholds (012-confirmed 2026-02-17)
# NOTE: These are GUIDELINES - community decides via 0102 agents
# S-curve only covers Early Adopters (0-16%), then OPO triggers
# UPS = 1 satoshi, $100K/BTC assumed
TIER_THRESHOLDS = {
    DAOTier.F0_DAE: {
        "adoption_ratio": 0.0,      # Starting point - gated/invite-only
        "treasury_ups": 0,          # Seed stage
        "active_agents": 0,
        "stage": "early_adopters",  # S-curve: Innovators + Early Adopters
        "real_world": "Gated Alpha (YC-style incubation)",
    },
    DAOTier.F1_OPO: {
        "adoption_ratio": 0.16,     # 16% = END of Early Adopters = OPO trigger
        "treasury_ups": 100_000_000,  # 100M sats = 1 BTC = $100K
        "active_agents": 10,
        "stage": "opo",             # Open Public Offering - becomes DAO Satellite
        "real_world": "YC Graduate ready for public (Series Seed)",
    },
    DAOTier.F2_GROWTH: {
        "adoption_ratio": 0.34,     # Post-OPO growth
        "treasury_ups": 1_000_000_000,  # 1B sats = 10 BTC = $1M
        "active_agents": 50,
        "stage": "growth",
        "real_world": "Series A/B company",
    },
    DAOTier.F3_INFRA: {
        "adoption_ratio": 0.50,     # Infrastructure scale
        "treasury_ups": 10_000_000_000,  # 10B sats = 100 BTC = $10M
        "active_agents": 200,
        "stage": "infrastructure",
        "real_world": "Infrastructure company (medium scale)",
    },
    DAOTier.F4_MEGA: {
        "adoption_ratio": 0.84,     # Unicorn scale
        "treasury_ups": 100_000_000_000,  # 100B sats = 1K BTC = $100M
        "active_agents": 1000,
        "stage": "mega",
        "real_world": "Cisco-scale established tech giant",
    },
    DAOTier.F5_SYSTEMIC: {
        "adoption_ratio": 0.95,     # Global impact
        "treasury_ups": 1_000_000_000_000,  # 1T sats = 10K BTC = $1B
        "active_agents": 10000,
        "stage": "systemic",
        "real_world": "Apple treasury scale - global infrastructure",
    },
}

# Reserve allocation for SmartDAOs
SMARTDAO_RESERVE_SPLIT = {
    "operations": 0.80,     # 80% for own operations
    "spawning_fund": 0.20,  # 20% for spawning new F_0s
}

# Spawning thresholds (minimum fund to spawn new F_0)
# DAO Satellites (F1+) can spawn new gated FoundUps
# ~1% of tier treasury required to spawn, seeds child with 10%
SPAWN_THRESHOLDS = {
    DAOTier.F1_OPO: 1_000_000,           # 1M sats = 0.01 BTC = $1K to spawn
    DAOTier.F2_GROWTH: 10_000_000,       # 10M sats = 0.1 BTC = $10K to spawn
    DAOTier.F3_INFRA: 100_000_000,       # 100M sats = 1 BTC = $100K to spawn
    DAOTier.F4_MEGA: 1_000_000_000,      # 1B sats = 10 BTC = $1M to spawn
    DAOTier.F5_SYSTEMIC: 10_000_000_000, # 10B sats = 100 BTC = $10M to spawn
}

# Initial seed for spawned F_0
SPAWN_SEED_RATIO = 0.10  # 10% of spawn_threshold goes to new F_0 as seed


@dataclass
class SmartDAOState:
    """State of a SmartDAO (F_1+) or FoundUp (F_0)."""

    foundup_id: str
    tier: DAOTier = DAOTier.F0_DAE
    parent_dao_id: Optional[str] = None  # Which SmartDAO spawned this
    spawn_tier: int = 0  # Generation (0 = original, 1 = spawned by F_1, etc.)

    # Economics
    btc_reserve: float = 0.0
    treasury_ups: float = 0.0
    staked_fi: float = 0.0
    mined_fi: float = 0.0

    # Spawning fund (SmartDAOs only)
    spawning_fund_ups: float = 0.0
    spawned_foundups: List[str] = field(default_factory=list)

    # Adoption metrics
    adoption_ratio: float = 0.0
    active_agents: int = 0

    @property
    def total_fi(self) -> float:
        return self.staked_fi + self.mined_fi

    def check_tier_escalation(self) -> Optional[DAOTier]:
        """Check if ready to escalate to next tier."""
        current_tier_value = self.tier.value
        next_tier_value = current_tier_value + 1

        if next_tier_value > DAOTier.F5_SYSTEMIC.value:
            return None  # Already at max

        next_tier = DAOTier(next_tier_value)
        thresholds = TIER_THRESHOLDS[next_tier]

        if (self.adoption_ratio >= thresholds["adoption_ratio"] and
            self.treasury_ups >= thresholds["treasury_ups"] and
            self.active_agents >= thresholds["active_agents"]):
            return next_tier

        return None

    def can_spawn(self) -> bool:
        """Check if SmartDAO can spawn a new F_0."""
        if self.tier == DAOTier.F0_DAE:
            return False  # F_0 cannot spawn

        threshold = SPAWN_THRESHOLDS.get(self.tier, float('inf'))
        return self.spawning_fund_ups >= threshold


@dataclass
class SpawnEvent:
    """Event when SmartDAO spawns a new FoundUp."""
    parent_dao_id: str
    child_foundup_id: str
    parent_tier: DAOTier
    seed_ups: float
    spawn_tier: int  # Generation number


class SmartDAOSpawningEngine:
    """Engine for SmartDAO tier escalation and spawning."""

    def __init__(self):
        self.daos: Dict[str, SmartDAOState] = {}
        self.spawn_history: List[SpawnEvent] = []
        self.network_pool: float = 0.0
        self.next_foundup_id: int = 0

    def register_foundup(self, foundup_id: str, parent_id: Optional[str] = None) -> SmartDAOState:
        """Register a new FoundUp (F_0)."""
        spawn_tier = 0
        if parent_id and parent_id in self.daos:
            spawn_tier = self.daos[parent_id].spawn_tier + 1

        dao = SmartDAOState(
            foundup_id=foundup_id,
            parent_dao_id=parent_id,
            spawn_tier=spawn_tier,
        )
        self.daos[foundup_id] = dao

        # Track ID to avoid collision
        if foundup_id.startswith("F_"):
            try:
                num = int(foundup_id.split("_")[1])
                self.next_foundup_id = max(self.next_foundup_id, num + 1)
            except (IndexError, ValueError):
                pass

        return dao

    def process_overflow(
        self,
        foundup_id: str,
        overflow_btc: float,
        btc_to_ups_rate: float = 100_000,  # 1 BTC = 100K UPS
    ) -> Tuple[float, float]:
        """Process overflow from a FoundUp.

        Returns (to_network_pool, to_spawning_fund).
        """
        if foundup_id not in self.daos:
            return overflow_btc, 0.0

        dao = self.daos[foundup_id]
        overflow_ups = overflow_btc * btc_to_ups_rate

        if dao.tier == DAOTier.F0_DAE:
            # F_0: All overflow goes to Network Pool
            self.network_pool += overflow_ups
            return overflow_ups, 0.0
        else:
            # SmartDAO: Split between operations and spawning
            to_operations = overflow_ups * SMARTDAO_RESERVE_SPLIT["operations"]
            to_spawning = overflow_ups * SMARTDAO_RESERVE_SPLIT["spawning_fund"]

            dao.treasury_ups += to_operations
            dao.spawning_fund_ups += to_spawning

            return to_operations, to_spawning

    def attempt_tier_escalation(self, foundup_id: str) -> Optional[DAOTier]:
        """Attempt to escalate a FoundUp to next tier."""
        if foundup_id not in self.daos:
            return None

        dao = self.daos[foundup_id]
        next_tier = dao.check_tier_escalation()

        if next_tier:
            dao.tier = next_tier
            return next_tier

        return None

    def attempt_spawn(self, parent_id: str) -> Optional[SpawnEvent]:
        """Attempt to spawn a new F_0 from a SmartDAO."""
        if parent_id not in self.daos:
            return None

        parent = self.daos[parent_id]

        if not parent.can_spawn():
            return None

        # Calculate seed for new F_0
        threshold = SPAWN_THRESHOLDS[parent.tier]
        seed_ups = threshold * SPAWN_SEED_RATIO

        # Deduct from spawning fund
        parent.spawning_fund_ups -= threshold

        # Create new F_0
        child_id = f"F_{self.next_foundup_id}"
        self.next_foundup_id += 1

        child = self.register_foundup(child_id, parent_id)
        child.treasury_ups = seed_ups

        # Record spawn
        parent.spawned_foundups.append(child_id)

        event = SpawnEvent(
            parent_dao_id=parent_id,
            child_foundup_id=child_id,
            parent_tier=parent.tier,
            seed_ups=seed_ups,
            spawn_tier=child.spawn_tier,
        )
        self.spawn_history.append(event)

        return event

    def process_epoch(self) -> Dict[str, any]:
        """Process one epoch for all DAOs.

        Returns summary of escalations, spawns, and overflow.
        """
        escalations = []
        spawns = []
        total_overflow_to_network = 0.0
        total_to_spawning = 0.0

        # Iterate over a snapshot because spawning can register new DAOs.
        for dao_id in list(self.daos.keys()):
            dao = self.daos[dao_id]
            # Check tier escalation
            new_tier = self.attempt_tier_escalation(dao_id)
            if new_tier:
                escalations.append((dao_id, new_tier))

            # Attempt spawn (SmartDAOs only)
            if dao.tier != DAOTier.F0_DAE:
                spawn_event = self.attempt_spawn(dao_id)
                if spawn_event:
                    spawns.append(spawn_event)

        return {
            "escalations": escalations,
            "spawns": spawns,
            "network_pool": self.network_pool,
        }

    def get_tier_distribution(self) -> Dict[DAOTier, int]:
        """Get count of DAOs at each tier."""
        distribution = {tier: 0 for tier in DAOTier}
        for dao in self.daos.values():
            distribution[dao.tier] += 1
        return distribution

    def get_spawn_tree(self, root_id: str, depth: int = 0) -> str:
        """Get ASCII tree of spawned FoundUps."""
        if root_id not in self.daos:
            return ""

        dao = self.daos[root_id]
        indent = "  " * depth
        tier_name = dao.tier.name
        line = f"{indent}{root_id} ({tier_name})"

        if dao.spawning_fund_ups > 0:
            line += f" [spawn_fund: {dao.spawning_fund_ups:,.0f} UPS]"

        lines = [line]

        for child_id in dao.spawned_foundups:
            lines.append(self.get_spawn_tree(child_id, depth + 1))

        return "\n".join(lines)


def simulate_ecosystem_growth(
    initial_foundups: int = 10,
    epochs: int = 100,
    growth_rate: float = 0.05,
    overflow_rate: float = 0.01,
) -> SmartDAOSpawningEngine:
    """Simulate ecosystem growth with tier escalation and spawning."""

    engine = SmartDAOSpawningEngine()

    # Create initial F_0s
    for i in range(initial_foundups):
        dao = engine.register_foundup(f"F_{i}")
        dao.treasury_ups = 10_000 + i * 5_000
        dao.active_agents = 5 + i
        dao.adoption_ratio = 0.05 + i * 0.02

    print(f"Initial: {initial_foundups} FoundUps (F_0)")
    print("-" * 60)

    for epoch in range(epochs):
        # Simulate growth
        for dao_id, dao in engine.daos.items():
            # Grow metrics
            dao.treasury_ups *= (1 + growth_rate)
            dao.adoption_ratio = min(1.0, dao.adoption_ratio * (1 + growth_rate * 0.5))
            dao.active_agents = int(dao.active_agents * (1 + growth_rate * 0.3))

            # Generate overflow based on treasury
            overflow_btc = dao.treasury_ups * overflow_rate / 100_000  # Convert to BTC scale
            engine.process_overflow(dao_id, overflow_btc)

        # Process epoch (escalations, spawns)
        result = engine.process_epoch()

        # Report significant events
        if result["escalations"]:
            for dao_id, new_tier in result["escalations"]:
                print(f"Epoch {epoch}: {dao_id} → {new_tier.name}")

        if result["spawns"]:
            for event in result["spawns"]:
                print(f"Epoch {epoch}: {event.parent_dao_id} spawned {event.child_foundup_id} (Tier {event.spawn_tier})")

    return engine


def demo_spawning_model():
    """Demo the SmartDAO spawning model."""

    print("=" * 70)
    print("SMARTDAO SPAWNING MODEL DEMO")
    print("=" * 70)

    engine = simulate_ecosystem_growth(
        initial_foundups=5,
        epochs=50,
        growth_rate=0.08,
        overflow_rate=0.02,
    )

    print("\n" + "=" * 70)
    print("FINAL STATE")
    print("=" * 70)

    print("\nTier Distribution:")
    for tier, count in engine.get_tier_distribution().items():
        if count > 0:
            print(f"  {tier.name}: {count}")

    print(f"\nNetwork Pool: {engine.network_pool:,.0f} UPS")
    print(f"Total DAOs: {len(engine.daos)}")
    print(f"Total Spawns: {len(engine.spawn_history)}")

    # Show spawn tree from first FoundUp
    print("\nSpawn Tree (from F_0):")
    print(engine.get_spawn_tree("F_0"))

    # Show escalation math
    print("\n" + "=" * 70)
    print("TIER ESCALATION THRESHOLDS")
    print("=" * 70)
    print(f"{'Tier':<15} {'Adoption':>10} {'Treasury':>15} {'Agents':>10}")
    print("-" * 50)
    for tier, thresholds in TIER_THRESHOLDS.items():
        print(
            f"{tier.name:<15} "
            f"{thresholds['adoption_ratio']:>9.0%} "
            f"{thresholds['treasury_ups']:>14,} "
            f"{thresholds['active_agents']:>10}"
        )

    print("\n" + "=" * 70)
    print("SPAWNING THRESHOLDS")
    print("=" * 70)
    print(f"{'Tier':<15} {'Fund Required':>15} {'Seed to Child':>15}")
    print("-" * 50)
    for tier, threshold in SPAWN_THRESHOLDS.items():
        seed = threshold * SPAWN_SEED_RATIO
        print(f"{tier.name:<15} {threshold:>14,} {seed:>14,}")


if __name__ == "__main__":
    demo_spawning_model()
