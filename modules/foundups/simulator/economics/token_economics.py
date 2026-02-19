"""Token Economics - Human vs Agent Economic Boundary.

Implements WSP 26 Section 6.8: Anti-Sybil dual-token design.

Token Roles:
- UPS: Universal fuel (humans EARN, agents SPEND allocated budgets)
- F_i: FoundUp-specific tokens (agents EARN through PoUW, humans OWN)

Fee Boundary:
- Internal UPS spend: Low/none (encourage activity)
- F_i -> UPS conversion: 2-5% (realization event)
- UPS -> external: 5-10% (discourages extraction)
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def sigmoid(x: float, k: float = 1.0, x0: float = 0.5) -> float:
    """Logistic sigmoid function for adoption curve.

    S-curve that models diffusion of innovation.

    Args:
        x: Input value (0-1 for adoption percentage)
        k: Steepness (higher = sharper transition)
        x0: Midpoint (where curve is at 50%)

    Returns:
        Output value (0-1)
    """
    return 1.0 / (1.0 + math.exp(-k * (x - x0)))


def adoption_curve(adoption_score: float, steepness: float = 12.0) -> float:
    """Calculate token release based on adoption score.

    Uses logistic S-curve (diffusion of innovation).
    No artificial tiers - pure mathematics.

    The curve naturally produces:
    - Slow start (innovators/early adopters)
    - Rapid growth (early/late majority)
    - Saturation (laggards)

    Args:
        adoption_score: 0.0 to 1.0 representing adoption level
        steepness: How sharp the S-curve is (default 12 = nice curve)

    Returns:
        Percentage of tokens to release (0.0 to 1.0)
    """
    # Clamp input
    adoption_score = max(0.0, min(1.0, adoption_score))

    # Sigmoid with midpoint at 0.5 adoption
    # At 0% adoption -> ~0% release
    # At 50% adoption -> 50% release
    # At 100% adoption -> ~100% release
    raw = sigmoid(adoption_score, k=steepness, x0=0.5)

    # Normalize so sigmoid(0) maps to 0 and sigmoid(1) maps to 1
    min_val = sigmoid(0.0, k=steepness, x0=0.5)
    max_val = sigmoid(1.0, k=steepness, x0=0.5)

    return (raw - min_val) / (max_val - min_val)


class TokenType(Enum):
    """Token types in the FoundUps ecosystem."""

    UPS = "UPS"  # Universal participation/settlement token
    FOUNDUP = "F_i"  # FoundUp-specific work reward token


@dataclass
class FeeConfig:
    """Fee configuration for token operations.

    TWO F_i TYPES with different exit fees:
    - MINED F_i (earned by agents): 11% exit fee - discourages extraction
    - STAKED F_i (from UPS investment): 5% exit fee - preserves value
    """

    # Internal UPS spend (agent execution)
    internal_spend_fee: float = 0.001  # 0.1% - very low to encourage activity

    # === MINED F_i FEES (earned by agents doing work) ===
    # High fee (11%) discourages extraction - keeps value in ecosystem
    mined_fi_exit_fee: float = 0.11  # 11% total on MINED F_i conversion
    # Breakdown of 11%:
    mined_fee_ops: float = 0.03  # 3% to protocol ops
    mined_fee_vault: float = 0.05  # 5% to BTC vault (Hotel California)
    mined_fee_insurance: float = 0.02  # 2% to insurance pool
    mined_fee_network: float = 0.01  # 1% to network drip

    # === STAKED F_i FEES (from UPS investment) ===
    # Lower fee (5%) for value preservation - user is getting THEIR UPS back
    staked_fi_entry_fee: float = 0.03  # 3% on staking entry
    staked_fi_exit_fee: float = 0.05  # 5% on unstaking exit
    # Total round-trip: 3% + 5% = 8% (much lower than 11% extraction)

    # UPS -> external (cash out)
    cashout_fee: float = 0.07  # 7% discourages extraction

    @property
    def total_mined_conversion_fee(self) -> float:
        """Total fee on MINED F_i -> UPS conversion (11%)."""
        return self.mined_fee_ops + self.mined_fee_vault + self.mined_fee_insurance + self.mined_fee_network

    @property
    def total_staked_roundtrip_fee(self) -> float:
        """Total round-trip fee for staking (entry + exit = 8%)."""
        return self.staked_fi_entry_fee + self.staked_fi_exit_fee


class SubscriptionTier(Enum):
    """Subscription tiers per WSP 26 Section 4.9.

    Freemium → Premium revenue model:
    - Free participants get base allocation, runs out
    - Subscribe for higher allocation + faster regeneration
    - Subscription revenue → BTC reserve (self-reinforcing)
    """

    FREE = "free"
    SPARK = "spark"           # $2.95/mo
    EXPLORER = "explorer"     # $9.95/mo
    BUILDER = "builder"       # $19.95/mo
    FOUNDER = "founder"       # $49.95/mo


@dataclass
class SubscriptionConfig:
    """Configuration for a subscription tier per WSP 26 Section 4.9.

    Key property: Effective UPS = allocation × cycles (multiplicative, not additive)
    """

    tier: SubscriptionTier
    price_monthly: float           # USD per month
    allocation_multiplier: float   # Multiple of base allocation
    cycles_per_month: int          # How many times allocation refreshes
    staking_fee_discount: float    # Discount on staking fees (0.0-1.0)
    can_launch_foundups: bool      # Whether user can create FoundUps

    @property
    def effective_monthly_multiplier(self) -> float:
        """Effective monthly UPS = allocation × cycles."""
        return self.allocation_multiplier * self.cycles_per_month


# WSP 26 Section 4.9 tier configurations
SUBSCRIPTION_TIERS: Dict[SubscriptionTier, SubscriptionConfig] = {
    SubscriptionTier.FREE: SubscriptionConfig(
        tier=SubscriptionTier.FREE,
        price_monthly=0.0,
        allocation_multiplier=1.0,
        cycles_per_month=1,
        staking_fee_discount=0.0,
        can_launch_foundups=False,
    ),
    SubscriptionTier.SPARK: SubscriptionConfig(
        tier=SubscriptionTier.SPARK,
        price_monthly=2.95,
        allocation_multiplier=2.0,
        cycles_per_month=2,
        staking_fee_discount=0.10,
        can_launch_foundups=False,
    ),
    SubscriptionTier.EXPLORER: SubscriptionConfig(
        tier=SubscriptionTier.EXPLORER,
        price_monthly=9.95,
        allocation_multiplier=3.0,
        cycles_per_month=3,
        staking_fee_discount=0.25,
        can_launch_foundups=False,
    ),
    SubscriptionTier.BUILDER: SubscriptionConfig(
        tier=SubscriptionTier.BUILDER,
        price_monthly=19.95,
        allocation_multiplier=5.0,
        cycles_per_month=5,
        staking_fee_discount=0.40,
        can_launch_foundups=True,
    ),
    SubscriptionTier.FOUNDER: SubscriptionConfig(
        tier=SubscriptionTier.FOUNDER,
        price_monthly=49.95,
        allocation_multiplier=10.0,
        cycles_per_month=30,  # Daily drip (~300x effective)
        staking_fee_discount=0.60,
        can_launch_foundups=True,
    ),
}


@dataclass
class AgentExecutionWallet:
    """Agent wallet for holding allocated UPS budgets.

    This is NOT earning - it's delegated spending authority from humans.
    Agents hold UPS only as a prepaid execution budget.
    """

    agent_id: str
    allocator_id: str  # Human who funded this wallet
    ups_balance: float = 0.0
    total_allocated: float = 0.0
    total_spent: float = 0.0
    policy_gates: Dict = field(default_factory=dict)

    def receive_allocation(self, amount: float, policy: Optional[Dict] = None) -> None:
        """Human allocates UPS to agent for task execution."""
        self.ups_balance += amount
        self.total_allocated += amount
        if policy:
            self.policy_gates = policy
        logger.info(f"[Wallet:{self.agent_id}] Received {amount:.2f} UPS from {self.allocator_id}")

    def spend(self, amount: float, operation: str) -> Tuple[bool, float]:
        """Agent spends UPS under policy constraints.

        Returns:
            (success, fee_paid) tuple
        """
        if not self._policy_allows(operation, amount):
            logger.warning(f"[Wallet:{self.agent_id}] Policy denied: {operation} for {amount:.2f}")
            return (False, 0.0)

        if amount > self.ups_balance:
            logger.warning(f"[Wallet:{self.agent_id}] Insufficient balance: {amount:.2f} > {self.ups_balance:.2f}")
            return (False, 0.0)

        # Very low internal fee to encourage activity
        fee = amount * FeeConfig().internal_spend_fee
        total_debit = amount + fee

        if total_debit > self.ups_balance:
            return (False, 0.0)

        self.ups_balance -= total_debit
        self.total_spent += amount
        logger.info(f"[Wallet:{self.agent_id}] Spent {amount:.2f} UPS on {operation} (fee: {fee:.4f})")
        return (True, fee)

    def return_unused(self) -> float:
        """Unused budget returns to allocator (human) minus demurrage."""
        remaining = self.ups_balance
        self.ups_balance = 0.0
        logger.info(f"[Wallet:{self.agent_id}] Returning {remaining:.2f} UPS to {self.allocator_id}")
        return remaining

    def _policy_allows(self, operation: str, amount: float) -> bool:
        """Check if operation is within policy gates."""
        if not self.policy_gates:
            return True  # No policy = allow all

        allowed_ops = self.policy_gates.get("allowed_ops", [])
        max_per_task = self.policy_gates.get("max_per_task", float("inf"))

        if allowed_ops and operation not in allowed_ops:
            return False

        return amount <= max_per_task


@dataclass
class HumanUPSAccount:
    """Human UPS account - earned through real-world verified actions.

    WSP 26 Section 4.9: Subscription tiers determine allocation.
    - Earned UPS: From 0102 completing tasks (labor)
    - Allocated UPS: From subscription tier (monthly allocation)
    Both streams decay equally. Both can be staked.
    """

    human_id: str
    ups_balance: float = 0.0
    total_earned: float = 0.0
    lottery_wins: int = 0

    # F_i holdings (owned, earned by agents working for this human)
    foundup_tokens: Dict[str, float] = field(default_factory=dict)  # foundup_id -> balance

    # === WSP 26 Section 4.9: Subscription Tier System ===
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    base_allocation: float = 100.0  # Base UPS per cycle
    remaining_allocation: float = 100.0  # UPS left in current cycle
    current_cycle: int = 0  # Which cycle we're in (0 to cycles_per_month-1)
    total_allocated: float = 0.0  # Lifetime allocated from subscription

    # === VALUE-BACKED STAKING ===
    # Track staked positions per FoundUp (F_i that represents backed UPS)
    staked_positions: Dict[str, float] = field(default_factory=dict)  # foundup_id -> staked F_i
    total_ups_staked: float = 0.0  # Lifetime UPS staked across all FoundUps

    def earn_ups(self, amount: float, source: str) -> None:
        """Human earns UPS through verified real-world action."""
        self.ups_balance += amount
        self.total_earned += amount
        logger.info(f"[Human:{self.human_id}] Earned {amount:.2f} UPS from {source}")

    def earn_lottery(self, amount: float) -> None:
        """Human wins the 'found it!' lottery chime."""
        self.ups_balance += amount
        self.total_earned += amount
        self.lottery_wins += 1
        logger.info(f"[Human:{self.human_id}] WON LOTTERY! +{amount:.2f} UPS (total wins: {self.lottery_wins})")

    def receive_fi(self, foundup_id: str, amount: float) -> None:
        """Human receives F_i tokens earned by their agent."""
        current = self.foundup_tokens.get(foundup_id, 0.0)
        self.foundup_tokens[foundup_id] = current + amount
        logger.info(f"[Human:{self.human_id}] Received {amount:.2f} F_{foundup_id}")

    def allocate_to_agent(self, amount: float, agent_wallet: AgentExecutionWallet) -> bool:
        """Human allocates UPS budget to agent."""
        if amount > self.ups_balance:
            logger.warning(f"[Human:{self.human_id}] Insufficient UPS for allocation")
            return False

        self.ups_balance -= amount
        agent_wallet.receive_allocation(amount)
        return True

    def convert_mined_fi_to_ups(
        self,
        foundup_id: str,
        amount: float,
        fee_config: FeeConfig,
    ) -> Tuple[float, Dict[str, float]]:
        """Convert MINED F_i to UPS - HIGH FEE (11%) realization event.

        MINED F_i = earned by agents doing work (like Bitcoin mining 2009)
        This is the "extraction" path - high fee discourages taking value out.

        For STAKED F_i (from UPS investment), use unstake_fi() instead (5% fee).

        Returns:
            (ups_received, fee_breakdown) tuple
        """
        current = self.foundup_tokens.get(foundup_id, 0.0)
        if amount > current:
            logger.warning(f"[Human:{self.human_id}] Insufficient MINED F_{foundup_id}")
            return (0.0, {})

        # Calculate 11% fee breakdown (discourages extraction)
        fee_ops = amount * fee_config.mined_fee_ops  # 3%
        fee_vault = amount * fee_config.mined_fee_vault  # 5%
        fee_insurance = amount * fee_config.mined_fee_insurance  # 2%
        fee_network = amount * fee_config.mined_fee_network  # 1%
        total_fee = fee_ops + fee_vault + fee_insurance + fee_network

        ups_received = amount - total_fee

        # Debit MINED F_i, credit UPS
        self.foundup_tokens[foundup_id] = current - amount
        self.ups_balance += ups_received

        fee_breakdown = {
            "ops": fee_ops,
            "vault": fee_vault,
            "insurance": fee_insurance,
            "network": fee_network,
            "total": total_fee,
            "fee_type": "mined_extraction",  # Track source
        }

        logger.info(
            f"[Human:{self.human_id}] Converted MINED {amount:.2f} F_{foundup_id} -> "
            f"{ups_received:.2f} UPS (11% extraction fee: {total_fee:.4f})"
        )

        return (ups_received, fee_breakdown)

    def convert_fi_to_ups(
        self,
        foundup_id: str,
        amount: float,
        fee_config: FeeConfig,
    ) -> Tuple[float, Dict[str, float]]:
        """DEPRECATED: Use convert_mined_fi_to_ups() for clarity.

        Kept for backwards compatibility - routes to mined F_i conversion.
        """
        return self.convert_mined_fi_to_ups(foundup_id, amount, fee_config)

    # === WSP 26 Section 4.9: Subscription Methods ===

    def get_subscription_config(self) -> SubscriptionConfig:
        """Get current subscription tier configuration."""
        return SUBSCRIPTION_TIERS[self.subscription_tier]

    def upgrade_subscription(self, new_tier: SubscriptionTier) -> bool:
        """Upgrade to a new subscription tier.

        The gamification loop:
        1. User plays, uses UPS to stake in FoundUps
        2. UPS runs out (remaining_allocation = 0)
        3. User subscribes → gets more UPS, faster refresh
        4. Subscription revenue → BTC reserve (self-reinforcing)

        Returns:
            True if upgrade successful
        """
        if new_tier.value == self.subscription_tier.value:
            logger.info(f"[Human:{self.human_id}] Already at {new_tier.value} tier")
            return False

        old_tier = self.subscription_tier
        self.subscription_tier = new_tier
        config = self.get_subscription_config()

        # Immediately grant one allocation cycle at new rate
        allocation = self.base_allocation * config.allocation_multiplier
        self.remaining_allocation = allocation
        self.current_cycle = 0

        logger.info(
            f"[Human:{self.human_id}] UPGRADED: {old_tier.value} -> {new_tier.value} "
            f"(allocation: {allocation:.2f} UPS, {config.cycles_per_month} cycles/month, "
            f"effective: {config.effective_monthly_multiplier:.0f}x)"
        )
        return True

    def refresh_allocation(self) -> float:
        """Refresh allocation for next cycle.

        Called at cycle boundaries (determined by subscription tier).
        - Free: 1 cycle/month
        - Spark: 2 cycles/month (bi-weekly)
        - Explorer: 3 cycles/month (~10 days)
        - Builder: 5 cycles/month (weekly)
        - Founder: 30 cycles/month (daily drip)

        Returns:
            Amount of UPS allocated this cycle
        """
        config = self.get_subscription_config()

        # Check if we have cycles remaining this month
        if self.current_cycle >= config.cycles_per_month:
            logger.warning(f"[Human:{self.human_id}] No cycles remaining this month (tier: {config.tier.value})")
            return 0.0

        # Calculate allocation for this cycle
        allocation = self.base_allocation * config.allocation_multiplier
        self.remaining_allocation += allocation
        self.total_allocated += allocation
        self.current_cycle += 1

        logger.info(
            f"[Human:{self.human_id}] ALLOCATION REFRESH: +{allocation:.2f} UPS "
            f"(cycle {self.current_cycle}/{config.cycles_per_month}, tier: {config.tier.value})"
        )
        return allocation

    def reset_monthly_cycles(self) -> None:
        """Reset cycle counter at start of new month."""
        self.current_cycle = 0
        logger.info(f"[Human:{self.human_id}] Monthly cycles reset")

    def use_allocated_ups(self, amount: float) -> bool:
        """Use UPS from allocation (for staking into FoundUps).

        This is separate from earned UPS - allocated UPS is the gamification currency.
        When this runs out, user is motivated to upgrade subscription.

        Returns:
            True if allocation available and used
        """
        if amount > self.remaining_allocation:
            logger.warning(
                f"[Human:{self.human_id}] Insufficient allocation: {amount:.2f} > {self.remaining_allocation:.2f} "
                f"(Consider upgrading from {self.subscription_tier.value}!)"
            )
            return False

        self.remaining_allocation -= amount
        logger.info(
            f"[Human:{self.human_id}] Used {amount:.2f} allocated UPS "
            f"(remaining: {self.remaining_allocation:.2f})"
        )
        return True

    def get_staking_fee_with_discount(self, base_fee: float) -> float:
        """Apply subscription tier discount to staking fee."""
        config = self.get_subscription_config()
        return base_fee * (1.0 - config.staking_fee_discount)

    def record_stake(self, foundup_id: str, ups_amount: float, fi_received: float) -> None:
        """Record a staking action (called after FoundUpTokenPool.stake_ups).

        Args:
            foundup_id: FoundUp staked into
            ups_amount: UPS spent (before fee)
            fi_received: F_i tokens received
        """
        current = self.staked_positions.get(foundup_id, 0.0)
        self.staked_positions[foundup_id] = current + fi_received
        self.total_ups_staked += ups_amount
        logger.info(
            f"[Human:{self.human_id}] STAKED: {ups_amount:.2f} UPS -> {fi_received:.2f} F_i "
            f"in {foundup_id} (total staked positions: {len(self.staked_positions)})"
        )

    def record_unstake(self, foundup_id: str, fi_amount: float, ups_received: float) -> None:
        """Record an unstaking action (called after FoundUpTokenPool.unstake_fi).

        Args:
            foundup_id: FoundUp unstaked from
            fi_amount: F_i tokens unstaked
            ups_received: UPS received (after fee)
        """
        current = self.staked_positions.get(foundup_id, 0.0)
        self.staked_positions[foundup_id] = max(0.0, current - fi_amount)
        self.ups_balance += ups_received

        if self.staked_positions[foundup_id] == 0:
            del self.staked_positions[foundup_id]

        logger.info(
            f"[Human:{self.human_id}] UNSTAKED: {fi_amount:.2f} F_i -> {ups_received:.2f} UPS "
            f"from {foundup_id} (balance now: {self.ups_balance:.2f})"
        )

    def get_demurrage_warning(self) -> Optional[str]:
        """Check if UPS is decaying and should be staked.

        Returns warning message if action recommended, None otherwise.
        """
        if self.ups_balance > 0 and len(self.staked_positions) == 0:
            return (
                f"WARNING: {self.ups_balance:.2f} UPS is DECAYING! "
                f"Stake into a FoundUp to preserve value."
            )
        if self.remaining_allocation < self.base_allocation * 0.2:
            config = self.get_subscription_config()
            if config.tier != SubscriptionTier.FOUNDER:
                return (
                    f"LOW ALLOCATION: Only {self.remaining_allocation:.2f} UPS left. "
                    f"Consider upgrading from {config.tier.value} tier."
                )
        return None

    def get_staking_summary(self) -> Dict:
        """Get summary of staked positions."""
        return {
            "human_id": self.human_id,
            "ups_balance": self.ups_balance,
            "total_ups_staked": self.total_ups_staked,
            "staked_positions": dict(self.staked_positions),
            "num_foundups_staked": len(self.staked_positions),
            "subscription_tier": self.subscription_tier.value,
            "demurrage_warning": self.get_demurrage_warning(),
        }


@dataclass
class StakedPosition:
    """A human's staked position in a FoundUp.

    VALUE-BACKED STAKING:
    - F_i tokens represent a CLAIM on staked UPS (1:1 backed)
    - The UPS is held in FoundUp treasury
    - Unstaking returns the backed UPS (minus fee)
    - This PRESERVES value (minus fees) - no exchange rate risk
    """

    human_id: str
    foundup_id: str
    ups_staked: float  # Original UPS amount staked (before fee)
    fi_received: float  # F_i tokens received (1:1 with post-fee UPS)
    staked_at_epoch: int
    is_locked: bool = True  # Auto-locked by default

    @property
    def backing_ratio(self) -> float:
        """Backing ratio (should always be 1.0 for value preservation)."""
        if self.fi_received == 0:
            return 0.0
        return self.ups_staked / self.fi_received


@dataclass
@dataclass
class FoundUpTokenPool:
    """F_i token pool for a specific FoundUp.

    Each FoundUp has 21M tokens (Bitcoin-like scarcity).
    Tokens unlock based on ADOPTION CURVE (diffusion of innovation).

    ADOPTION-BASED RELEASE (continuous S-curve, NOT discrete tiers):
    - 0% adoption → 0% tokens released
    - 50% adoption → 50% tokens released
    - 100% adoption → 100% tokens released
    - Uses logistic sigmoid - the natural curve of innovation diffusion

    VALUE-BACKED STAKING:
    - ups_treasury holds the UPS that backs staked F_i tokens
    - When humans stake UPS, they get F_i 1:1 (after fee)
    - When they unstake, they get their UPS back (minus unstake fee)
    - This PRESERVES value - no exchange rate gambling
    """

    foundup_id: str
    total_supply: int = 21_000_000  # Every FoundUp is its own Bitcoin

    # Adoption score (0.0 to 1.0) - determines token release
    # Updated based on: users, revenue, activity, milestones
    adoption_score: float = 0.0

    # Curve steepness (higher = sharper S-curve)
    curve_steepness: float = 12.0

    # Token tracking
    minted: float = 0.0
    burned: float = 0.0

    # BTC vault backing (from conversion fees)
    btc_vault_balance: float = 0.0

    # UPS treasury (backs staked F_i tokens - VALUE PRESERVATION)
    ups_treasury: float = 0.0
    staked_fi_outstanding: float = 0.0  # Total F_i from staking (not mining)

    # Adoption metrics (inputs to adoption_score calculation)
    total_users: int = 0
    total_revenue_ups: float = 0.0
    total_work_completed: float = 0.0
    milestones_achieved: int = 0

    @property
    def release_percentage(self) -> float:
        """Percentage of tokens released at current adoption.

        Uses continuous S-curve (diffusion of innovation).
        No artificial tier boundaries.
        """
        return adoption_curve(self.adoption_score, self.curve_steepness)

    @property
    def available_supply(self) -> float:
        """Tokens available at current adoption level."""
        return self.total_supply * self.release_percentage

    @property
    def remaining_mintable(self) -> float:
        """Tokens that can still be minted at current adoption."""
        return max(0.0, self.available_supply - self.minted)

    def update_adoption(
        self,
        users: Optional[int] = None,
        revenue_ups: Optional[float] = None,
        work_completed: Optional[float] = None,
        milestone: bool = False,
    ) -> float:
        """Update adoption metrics and recalculate adoption score.

        Adoption score is derived from multiple factors:
        - User count (network effects)
        - Revenue (market validation)
        - Work completed (actual output)
        - Milestones (growth markers)

        Returns:
            New adoption score (0.0 to 1.0)
        """
        if users is not None:
            self.total_users = users
        if revenue_ups is not None:
            self.total_revenue_ups += revenue_ups
        if work_completed is not None:
            self.total_work_completed += work_completed
        if milestone:
            self.milestones_achieved += 1

        # Calculate adoption score from metrics
        # This is a simplified model - can be tuned
        old_score = self.adoption_score

        # User factor: log scale, 1000 users = 0.5, 10000 = ~0.67
        user_factor = math.log10(max(1, self.total_users) + 1) / 5.0

        # Revenue factor: $10K = 0.25, $100K = 0.5, $1M = 0.75
        revenue_factor = math.log10(max(1, self.total_revenue_ups) + 1) / 8.0

        # Work factor: 10K tasks = 0.25, 100K = 0.5
        work_factor = math.log10(max(1, self.total_work_completed) + 1) / 6.0

        # Milestone factor: each milestone = 0.05 bonus
        milestone_factor = min(0.2, self.milestones_achieved * 0.05)

        # Combined (weighted average)
        self.adoption_score = min(1.0, max(0.0,
            user_factor * 0.35 +
            revenue_factor * 0.30 +
            work_factor * 0.25 +
            milestone_factor
        ))

        if self.adoption_score > old_score:
            new_tokens = (self.release_percentage - adoption_curve(old_score, self.curve_steepness)) * self.total_supply
            if new_tokens > 100:  # Only log significant unlocks
                logger.info(
                    f"[Pool:{self.foundup_id}] Adoption {old_score:.2%} -> {self.adoption_score:.2%}, "
                    f"unlocked {new_tokens:,.0f} more tokens (total available: {self.available_supply:,.0f})"
                )

        return self.adoption_score

    def mint_for_work(self, amount: float, agent_id: str) -> float:
        """Mint F_i tokens for verified agent work (PoUW).

        0102 workers are the MINERS - they earn tokens by doing work.

        Returns:
            Actual amount minted (may be less if supply exhausted at current adoption)
        """
        mintable = min(amount, self.remaining_mintable)
        if mintable <= 0:
            logger.warning(
                f"[Pool:{self.foundup_id}] No tokens available "
                f"(adoption: {self.adoption_score:.2%}, released: {self.release_percentage:.2%})"
            )
            return 0.0

        self.minted += mintable
        # Work contributes to adoption
        self.total_work_completed += mintable
        logger.info(f"[Pool:{self.foundup_id}] Minted {mintable:.2f} F_i for {agent_id}")
        return mintable

    def progress_tier(self) -> bool:
        """DEPRECATED: Use update_adoption() instead.

        Kept for backwards compatibility.
        Adds 0.15 to adoption score (simulates tier jump).
        """
        old_score = self.adoption_score
        self.adoption_score = min(1.0, self.adoption_score + 0.15)
        logger.info(
            f"[Pool:{self.foundup_id}] (legacy) Adoption {old_score:.2%} -> {self.adoption_score:.2%}"
        )
        return self.adoption_score < 1.0

    def receive_vault_fee(self, btc_amount: float) -> None:
        """Receive BTC from conversion fees into vault."""
        self.btc_vault_balance += btc_amount
        logger.info(f"[Pool:{self.foundup_id}] Vault +{btc_amount:.6f} BTC (total: {self.btc_vault_balance:.6f})")

    # === VALUE-BACKED STAKING METHODS ===

    def stake_ups(
        self,
        ups_amount: float,
        staker_id: str,
        staking_fee_rate: float = 0.03,  # 3% default
    ) -> Tuple[float, float]:
        """Stake UPS into this FoundUp, receive F_i tokens 1:1 (after fee).

        VALUE PRESERVATION:
        - The UPS goes into ups_treasury (backing)
        - You get F_i = UPS * (1 - fee)
        - Your F_i is a CLAIM on that UPS
        - Unstaking returns the UPS (minus unstake fee)

        Args:
            ups_amount: Amount of UPS to stake
            staker_id: Human staking
            staking_fee_rate: Staking fee (e.g., 0.03 = 3%)

        Returns:
            (fi_received, fee_paid) tuple
        """
        # Calculate fee
        fee = ups_amount * staking_fee_rate
        ups_after_fee = ups_amount - fee

        # F_i received = UPS after fee (1:1 backing)
        fi_tokens = ups_after_fee

        # Add to treasury (this backs the F_i)
        self.ups_treasury += ups_after_fee
        self.staked_fi_outstanding += fi_tokens

        logger.info(
            f"[Pool:{self.foundup_id}] STAKE: {staker_id} staked {ups_amount:.2f} UPS "
            f"-> {fi_tokens:.2f} F_i (fee: {fee:.2f}, treasury: {self.ups_treasury:.2f})"
        )

        return (fi_tokens, fee)

    def unstake_fi(
        self,
        fi_amount: float,
        staker_id: str,
        unstaking_fee_rate: float = 0.05,  # 5% default (discourages churn)
    ) -> Tuple[float, float]:
        """Unstake F_i tokens, receive backed UPS (minus fee).

        VALUE PRESERVATION:
        - F_i is backed 1:1 by UPS in treasury
        - You get back your UPS (minus unstake fee)
        - No exchange rate risk - the backing IS the value

        Args:
            fi_amount: Amount of F_i to unstake
            staker_id: Human unstaking
            unstaking_fee_rate: Unstaking penalty (e.g., 0.05 = 5%)

        Returns:
            (ups_received, fee_paid) tuple
        """
        if fi_amount > self.staked_fi_outstanding:
            logger.warning(
                f"[Pool:{self.foundup_id}] Cannot unstake {fi_amount:.2f} F_i "
                f"(only {self.staked_fi_outstanding:.2f} outstanding)"
            )
            return (0.0, 0.0)

        # F_i is backed 1:1 by UPS in treasury
        ups_backing = fi_amount  # 1:1 ratio

        if ups_backing > self.ups_treasury:
            logger.warning(
                f"[Pool:{self.foundup_id}] Treasury insufficient: "
                f"{ups_backing:.2f} > {self.ups_treasury:.2f}"
            )
            return (0.0, 0.0)

        # Calculate fee
        fee = ups_backing * unstaking_fee_rate
        ups_after_fee = ups_backing - fee

        # Remove from treasury and outstanding
        self.ups_treasury -= ups_backing
        self.staked_fi_outstanding -= fi_amount

        logger.info(
            f"[Pool:{self.foundup_id}] UNSTAKE: {staker_id} unstaked {fi_amount:.2f} F_i "
            f"-> {ups_after_fee:.2f} UPS (fee: {fee:.2f}, treasury: {self.ups_treasury:.2f})"
        )

        return (ups_after_fee, fee)

    def get_staking_stats(self) -> Dict:
        """Get staking statistics for this FoundUp."""
        return {
            "foundup_id": self.foundup_id,
            "ups_treasury": self.ups_treasury,
            "staked_fi_outstanding": self.staked_fi_outstanding,
            "backing_ratio": 1.0 if self.staked_fi_outstanding > 0 else 0.0,  # Always 1:1
            "minted_fi": self.minted,
            "btc_vault": self.btc_vault_balance,
        }


class TokenEconomicsEngine:
    """Main engine for FoundUps token economics.

    Implements WSP 26 Section 6.8: Human vs Agent economic boundary.
    """

    def __init__(self, fee_config: Optional[FeeConfig] = None):
        self.fee_config = fee_config or FeeConfig()

        # Registries
        self.human_accounts: Dict[str, HumanUPSAccount] = {}
        self.agent_wallets: Dict[str, AgentExecutionWallet] = {}
        self.foundup_pools: Dict[str, FoundUpTokenPool] = {}

        # System accumulators
        self.total_fees_ops: float = 0.0
        self.total_fees_vault: float = 0.0
        self.total_fees_insurance: float = 0.0

    def register_human(self, human_id: str, initial_ups: float = 0.0) -> HumanUPSAccount:
        """Register a human account."""
        account = HumanUPSAccount(human_id=human_id, ups_balance=initial_ups)
        self.human_accounts[human_id] = account
        return account

    def register_agent(self, agent_id: str, allocator_id: str) -> AgentExecutionWallet:
        """Register an agent execution wallet."""
        wallet = AgentExecutionWallet(agent_id=agent_id, allocator_id=allocator_id)
        self.agent_wallets[agent_id] = wallet
        return wallet

    def register_foundup(self, foundup_id: str) -> FoundUpTokenPool:
        """Register a FoundUp token pool."""
        pool = FoundUpTokenPool(foundup_id=foundup_id)
        self.foundup_pools[foundup_id] = pool
        return pool

    def human_earns_ups(
        self,
        human_id: str,
        amount: float,
        source: str,
        is_lottery: bool = False,
    ) -> None:
        """Human earns UPS through verified real-world action."""
        account = self.human_accounts.get(human_id)
        if not account:
            account = self.register_human(human_id)

        if is_lottery:
            account.earn_lottery(amount)
        else:
            account.earn_ups(amount, source)

    def human_allocates_to_agent(
        self,
        human_id: str,
        agent_id: str,
        amount: float,
        policy: Optional[Dict] = None,
    ) -> bool:
        """Human allocates UPS budget to agent for task execution."""
        account = self.human_accounts.get(human_id)
        wallet = self.agent_wallets.get(agent_id)

        if not account or not wallet:
            return False

        if wallet.allocator_id != human_id:
            logger.warning(f"Human {human_id} is not the allocator for agent {agent_id}")
            return False

        success = account.allocate_to_agent(amount, wallet)
        if success and policy:
            wallet.policy_gates = policy

        return success

    def agent_completes_task(
        self,
        agent_id: str,
        foundup_id: str,
        task_cost_ups: float,
        work_reward_fi: float,
    ) -> Tuple[bool, float]:
        """Agent completes task: spends UPS budget, earns F_i for owner.

        Returns:
            (success, fi_earned) tuple
        """
        wallet = self.agent_wallets.get(agent_id)
        pool = self.foundup_pools.get(foundup_id)

        if not wallet or not pool:
            return (False, 0.0)

        # Agent spends UPS budget
        success, fee = wallet.spend(task_cost_ups, f"task:{foundup_id}")
        if not success:
            return (False, 0.0)

        # Agent earns F_i (goes to human owner)
        fi_minted = pool.mint_for_work(work_reward_fi, agent_id)
        if fi_minted <= 0:
            return (True, 0.0)  # Task completed but no tokens available

        # Transfer F_i to human owner
        owner_id = wallet.allocator_id
        owner = self.human_accounts.get(owner_id)
        if owner:
            owner.receive_fi(foundup_id, fi_minted)

        return (True, fi_minted)

    def human_converts_mined_fi_to_ups(
        self,
        human_id: str,
        foundup_id: str,
        amount: float,
    ) -> Tuple[float, Dict[str, float]]:
        """Human converts MINED F_i to UPS - HIGH FEE (11%) extraction event.

        MINED F_i = earned by agents doing work (Bitcoin mining 2009 model)

        This is where the system takes 11% to discourage extraction:
        - 3% ops fee -> protocol revenue
        - 5% vault fee -> BTC vault (Hotel California - never exits)
        - 2% insurance fee -> slashing pool
        - 1% network fee -> drip to active participants

        For STAKED F_i, use human_unstakes_fi() instead (5% fee).

        Returns:
            (ups_received, fee_breakdown) tuple
        """
        account = self.human_accounts.get(human_id)
        pool = self.foundup_pools.get(foundup_id)

        if not account or not pool:
            return (0.0, {})

        ups_received, fee_breakdown = account.convert_mined_fi_to_ups(
            foundup_id, amount, self.fee_config
        )

        if ups_received > 0:
            # Route 11% fees
            self.total_fees_ops += fee_breakdown.get("ops", 0.0)
            self.total_fees_insurance += fee_breakdown.get("insurance", 0.0)

            # Vault fee goes to FoundUp's BTC backing (Hotel California)
            vault_fee = fee_breakdown.get("vault", 0.0)
            self.total_fees_vault += vault_fee
            pool.receive_vault_fee(vault_fee)

            # Network fee goes to drip pool
            network_fee = fee_breakdown.get("network", 0.0)
            # TODO: Route to network drip distributor

            logger.info(
                f"[Engine] MINED F_i extraction: {amount:.2f} -> {ups_received:.2f} UPS "
                f"(11% fee breakdown: ops={fee_breakdown.get('ops', 0):.2f}, "
                f"vault={vault_fee:.2f}, insurance={fee_breakdown.get('insurance', 0):.2f}, "
                f"network={network_fee:.2f})"
            )

        return (ups_received, fee_breakdown)

    def human_converts_fi_to_ups(
        self,
        human_id: str,
        foundup_id: str,
        amount: float,
    ) -> Tuple[float, Dict[str, float]]:
        """DEPRECATED: Use human_converts_mined_fi_to_ups() for clarity.

        Kept for backwards compatibility.
        """
        return self.human_converts_mined_fi_to_ups(human_id, foundup_id, amount)

    def human_stakes_ups(
        self,
        human_id: str,
        foundup_id: str,
        ups_amount: float,
    ) -> Tuple[float, float]:
        """Human stakes UPS into a FoundUp, receives STAKED F_i (3% entry fee).

        STAKED F_i is value-backed:
        - The UPS goes into FoundUp treasury (1:1 backing)
        - User gets F_i representing their claim
        - Unstaking returns UPS (minus 5% exit fee)
        - Total round-trip: 8% (vs 11% for mined extraction)

        Returns:
            (fi_received, fee_paid) tuple
        """
        account = self.human_accounts.get(human_id)
        pool = self.foundup_pools.get(foundup_id)

        if not account or not pool:
            return (0.0, 0.0)

        if ups_amount > account.ups_balance:
            logger.warning(f"[Engine] Insufficient UPS for staking: {ups_amount:.2f}")
            return (0.0, 0.0)

        # Apply subscription tier discount to staking fee
        base_fee = self.fee_config.staked_fi_entry_fee
        effective_fee = account.get_staking_fee_with_discount(base_fee)

        # Stake into pool
        fi_received, fee_paid = pool.stake_ups(ups_amount, human_id, effective_fee)

        if fi_received > 0:
            # Debit UPS from human, record stake
            account.ups_balance -= ups_amount
            account.record_stake(foundup_id, ups_amount, fi_received)

            logger.info(
                f"[Engine] STAKED: {human_id} staked {ups_amount:.2f} UPS -> "
                f"{fi_received:.2f} STAKED F_i (entry fee: {fee_paid:.2f})"
            )

        return (fi_received, fee_paid)

    def human_unstakes_fi(
        self,
        human_id: str,
        foundup_id: str,
        fi_amount: float,
    ) -> Tuple[float, float]:
        """Human unstakes STAKED F_i, receives backed UPS (5% exit fee).

        VALUE PRESERVATION:
        - STAKED F_i is backed 1:1 by UPS in treasury
        - Unstaking returns the UPS (minus 5% exit fee)
        - This is much better than 11% extraction fee for MINED F_i

        Returns:
            (ups_received, fee_paid) tuple
        """
        account = self.human_accounts.get(human_id)
        pool = self.foundup_pools.get(foundup_id)

        if not account or not pool:
            return (0.0, 0.0)

        # Check staked position
        staked = account.staked_positions.get(foundup_id, 0.0)
        if fi_amount > staked:
            logger.warning(
                f"[Engine] Cannot unstake {fi_amount:.2f} STAKED F_i "
                f"(only {staked:.2f} staked in {foundup_id})"
            )
            return (0.0, 0.0)

        # Unstake from pool
        exit_fee = self.fee_config.staked_fi_exit_fee
        ups_received, fee_paid = pool.unstake_fi(fi_amount, human_id, exit_fee)

        if ups_received > 0:
            account.record_unstake(foundup_id, fi_amount, ups_received)

            logger.info(
                f"[Engine] UNSTAKED: {human_id} unstaked {fi_amount:.2f} STAKED F_i -> "
                f"{ups_received:.2f} UPS (exit fee: {fee_paid:.2f})"
            )

        return (ups_received, fee_paid)

    def get_system_stats(self) -> Dict:
        """Get overall system statistics."""
        total_ups = sum(a.ups_balance for a in self.human_accounts.values())
        total_fi = sum(
            sum(a.foundup_tokens.values())
            for a in self.human_accounts.values()
        )
        total_vault = sum(p.btc_vault_balance for p in self.foundup_pools.values())

        return {
            "total_ups_circulation": total_ups,
            "total_fi_outstanding": total_fi,
            "total_btc_vault": total_vault,
            "total_fees_ops": self.total_fees_ops,
            "total_fees_vault": self.total_fees_vault,
            "total_fees_insurance": self.total_fees_insurance,
            "num_humans": len(self.human_accounts),
            "num_agents": len(self.agent_wallets),
            "num_foundups": len(self.foundup_pools),
        }
