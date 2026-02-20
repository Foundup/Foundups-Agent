"""Demurrage Engine - Bio-Decay for UPS Tokens (WSP 26 Section 16).

Implements TOKENOMICS.md ICE/LIQUID/VAPOR model:
- LIQUID (wallet): Decays over time (0.5% - 5% monthly adaptive)
- ICE (staked): No decay, earns yield
- VAPOR (exited): 15% evaporation fee, BTC locked forever

ENHANCED (012-Spec v4.0):
- ACTIVITY-BASED MODULATION: Active users get reduced decay
- NOTIFICATION SYSTEM: Decay warnings, stake prompts, auto-allocation
- DORMANT VALUE RECYCLING: Unclaimed UPS → participation pool
- TIER-BASED DECAY: Active (0.5x), Moderate (1.0x), Passive (2.0x) multipliers

Key Insight: Wallet UPS decays → motivates staking or activity

UPS = SATOSHI TAGGING (012-confirmed):
- UPS is pegged/tagged to satoshis (BTC smallest unit)
- BTC is LOCKED in reserve (Hotel California - never leaves)
- UPS decay = UPS REDISTRIBUTED to pools (not burned, not to BTC)
- Decayed UPS flows back to Network for ecosystem operations

Formula: U(t) = U₀ · e^(-λ(t)·τ·t)
Where:
  λ(t) = Michaelis-Menten adaptive rate based on inactivity
  τ = Activity tier multiplier (Active=0.5, Moderate=1.0, Passive=2.0)

Decay Routing (UPS REDISTRIBUTION):
  - 80% → Network Pool (ecosystem operations, agent rewards)
  - 20% → pAVS Treasury (system infrastructure)

TWO DISTINCT TREASURIES (012-confirmed):
  - pAVS Treasury (SYSTEM) = 20% of UPS demurrage → platform infrastructure
  - F_i Fund (PER-FOUNDUP) = 4% of F_i pool → per-FoundUp operations

This module handles pAVS Treasury only. F_i Fund is in pool_distribution.py.

NOTE: All parameters require extensive modeling and simulation testing
to determine legitimacy (012-directive).

Reference: WSP 26 Section 16, TOKENOMICS.md
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .btc_reserve import BTCReserve, BTCSourceType, get_btc_reserve

logger = logging.getLogger(__name__)


class TokenState(Enum):
    """Token states per TOKENOMICS.md bio-decay model."""
    LIQUID = "liquid"  # In wallet, decaying
    ICE = "ice"  # Staked in FoundUp, frozen (no decay)
    VAPOR = "vapor"  # Exited to external, 15% fee


class ActivityTier(Enum):
    """Activity tier affects decay rate multiplier."""
    ACTIVE = "active"      # Regular activity: 0.5x decay (reduced)
    MODERATE = "moderate"  # Occasional activity: 1.0x decay (baseline)
    PASSIVE = "passive"    # Idle/inactive: 2.0x decay (accelerated)
    DORMANT = "dormant"    # Very long inactivity: recycling candidate


# Tier multipliers for decay rate
ACTIVITY_TIER_MULTIPLIERS = {
    ActivityTier.ACTIVE: 0.5,     # 50% of base decay
    ActivityTier.MODERATE: 1.0,   # 100% of base decay
    ActivityTier.PASSIVE: 2.0,    # 200% of base decay (accelerated)
    ActivityTier.DORMANT: 2.5,    # 250% of base decay + recycling candidate
}

# Days inactive threshold for tier classification
ACTIVITY_TIER_THRESHOLDS = {
    ActivityTier.ACTIVE: 3,       # < 3 days = active
    ActivityTier.MODERATE: 7,     # 3-7 days = moderate
    ActivityTier.PASSIVE: 30,     # 7-30 days = passive
    ActivityTier.DORMANT: 90,     # > 90 days = dormant (recycling)
}


class FoundUpType(Enum):
    """FoundUp type affects decay redistribution ratios.

    Different FoundUp types have different economic profiles:
    - INFRASTRUCTURE: Higher operational costs → more to treasury
    - SOCIAL: Agent-labor intensive → more to network pool
    - CAPITAL_INTENSIVE: Equipment/inventory costs → balanced
    - MARKETPLACE: Transaction-based → more to network pool
    - GOVERNANCE: DAO operations → more to treasury
    """
    INFRASTRUCTURE = "infrastructure"  # GotJunk, storage, logistics
    SOCIAL = "social"                  # Community, content, events
    CAPITAL_INTENSIVE = "capital"      # Manufacturing, hardware
    MARKETPLACE = "marketplace"        # Trading, exchange, auctions
    GOVERNANCE = "governance"          # DAO, voting, coordination
    DEFAULT = "default"                # Unspecified type


# Default redistribution ratios by FoundUp type
# (network_pool_ratio, treasury_ratio) - must sum to 1.0
FOUNDUP_TYPE_RATIOS = {
    FoundUpType.INFRASTRUCTURE: (0.65, 0.35),  # Higher treasury for ops
    FoundUpType.SOCIAL: (0.90, 0.10),          # Agent-driven, low infrastructure
    FoundUpType.CAPITAL_INTENSIVE: (0.75, 0.25),  # Balanced
    FoundUpType.MARKETPLACE: (0.85, 0.15),     # Transaction rewards
    FoundUpType.GOVERNANCE: (0.70, 0.30),      # DAO overhead
    FoundUpType.DEFAULT: (0.80, 0.20),         # Ecosystem default
}


class NotificationType(Enum):
    """Types of decay notifications."""
    INFO = "info"              # Informational (< 3 days inactive)
    WARNING = "warning"        # Warning (3-7 days inactive)
    CRITICAL = "critical"      # Critical (7+ days, high decay)
    STAKE_PROMPT = "stake"     # Stake now prompt
    AUTO_STAKE = "auto_stake"  # Auto-allocation notification


@dataclass
class DecayNotification:
    """Structured decay notification."""
    notification_type: NotificationType
    human_id: str
    message: str
    decay_rate_percent: float
    daily_loss_estimate: float
    ups_balance: float
    days_inactive: float
    timestamp: str
    auto_stake_options: List[str] = field(default_factory=list)  # FoundUp IDs for auto-stake

    def to_dict(self) -> Dict:
        """Export for FAM event / API."""
        return {
            "type": self.notification_type.value,
            "human_id": self.human_id,
            "message": self.message,
            "decay_rate_percent": round(self.decay_rate_percent, 4),
            "daily_loss_estimate": round(self.daily_loss_estimate, 4),
            "ups_balance": round(self.ups_balance, 2),
            "days_inactive": round(self.days_inactive, 1),
            "timestamp": self.timestamp,
            "auto_stake_options": self.auto_stake_options,
        }


@dataclass
class DecayConfig:
    """Configuration for adaptive decay.

    Michaelis-Menten kinetics:
    λ(t) = λ_min + (λ_max - λ_min) · (D / (K + D))

    Enhanced with activity tier modulation:
    λ_eff = λ(t) × τ_tier
    """

    # Base decay rates (per day)
    lambda_min: float = 0.005 / 30  # 0.5% monthly = 0.0167%/day
    lambda_max: float = 0.05 / 30  # 5% monthly = 0.167%/day

    # Half-maximal constant (days of inactivity for 50% max decay)
    k_constant: float = 7.0

    # Circadian pulse boost (6-7 PM local time)
    circadian_boost: float = 1.30  # 30% increase during pulse window

    # Maximum daily decay cap (prevent shock)
    max_daily_decay: float = 0.03  # 3% max per day

    # Activity-based modulation (012-Spec v4.0)
    enable_activity_modulation: bool = True

    # Notification thresholds
    notification_threshold_days: float = 3.0  # Days before notifications start
    critical_threshold_days: float = 7.0      # Days for critical warnings

    # Auto-stake configuration
    enable_auto_stake: bool = True
    auto_stake_dormant_threshold_days: float = 30.0  # Days before auto-stake eligible
    auto_stake_max_percentage: float = 0.5           # Max % of balance to auto-stake

    # Dormant recycling
    enable_dormant_recycling: bool = True
    dormant_threshold_days: float = 90.0    # Days before recycling starts
    recycling_rate_per_day: float = 0.01    # 1% per day transferred to participation pool

    # Decay routing (must sum to 1.0) - UPS REDISTRIBUTION
    #
    # TWO DISTINCT TREASURIES (012-confirmed):
    # 1. pAVS Treasury (SYSTEM) = 20% of UPS demurrage → platform infrastructure
    # 2. F_i Fund (PER-FOUNDUP) = 4% of F_i pool → per-FoundUp operations
    #
    # This config is for pAVS System Treasury (UPS demurrage redistribution)
    # F_i Fund is handled separately in pool_distribution.py
    #
    # NOTE: Ratios variable based on:
    # - Ecosystem maturity (early bootstrap vs growth vs mature)
    # - pAVS Treasury health (depleted → higher ratio)
    # - 0102 SmartDAO (autonomous adjustment within bounds - NO human voting)
    decay_to_network_pool_ratio: float = 0.80  # Default: 80% to Network Pool
    decay_to_pavs_treasury_ratio: float = 0.20  # Default: 20% to pAVS System Treasury

    # Adaptive ratio bounds (governance can adjust within these)
    min_network_pool_ratio: float = 0.60  # Never less than 60% to network
    max_network_pool_ratio: float = 0.95  # Never more than 95% to network

    # pAVS Treasury health thresholds for adaptive adjustment
    pavs_treasury_critical_threshold: float = 0.10  # < 10% -> increase treasury ratio
    pavs_treasury_healthy_threshold: float = 0.50   # > 50% -> can decrease ratio

    @property
    def pavs_pavs_treasury_critical_threshold(self) -> float:
        """Backward-compatible alias for legacy field name."""
        return self.pavs_treasury_critical_threshold

    @pavs_pavs_treasury_critical_threshold.setter
    def pavs_pavs_treasury_critical_threshold(self, value: float) -> None:
        self.pavs_treasury_critical_threshold = value

    @property
    def pavs_pavs_treasury_healthy_threshold(self) -> float:
        """Backward-compatible alias for legacy field name."""
        return self.pavs_treasury_healthy_threshold

    @pavs_pavs_treasury_healthy_threshold.setter
    def pavs_pavs_treasury_healthy_threshold(self, value: float) -> None:
        self.pavs_treasury_healthy_threshold = value


@dataclass
class WalletState:
    """Track a wallet's decay state."""

    human_id: str
    ups_balance: float
    last_activity: datetime
    total_decayed: float = 0.0
    decay_warnings: int = 0

    # Enhanced tracking (012-Spec v4.0)
    staked_ups: float = 0.0          # Amount in ICE state (no decay)
    activity_score: float = 0.5      # 0.0-1.0 rolling activity score
    participation_actions: int = 0   # Count of qualifying actions
    auto_stake_opted_in: bool = False  # User opted into auto-stake
    notifications_sent: int = 0       # Count of notifications sent
    last_notification: Optional[datetime] = None
    recycled_to_pool: float = 0.0    # Amount recycled to participation pool
    # Simulation-time clocks (deterministic, tick-driven)
    days_inactive_sim: float = 0.0
    days_since_last_notification_sim: float = 9999.0

    @property
    def days_inactive(self) -> float:
        """Simulation days since last activity (tick-driven)."""
        return self.days_inactive_sim

    @property
    def total_ups(self) -> float:
        """Total UPS (liquid + staked)."""
        return self.ups_balance + self.staked_ups

    @property
    def activity_tier(self) -> ActivityTier:
        """Determine activity tier based on inactivity and score."""
        days = self.days_inactive

        if days >= ACTIVITY_TIER_THRESHOLDS[ActivityTier.DORMANT]:
            return ActivityTier.DORMANT
        elif days >= ACTIVITY_TIER_THRESHOLDS[ActivityTier.PASSIVE]:
            return ActivityTier.PASSIVE
        elif days >= ACTIVITY_TIER_THRESHOLDS[ActivityTier.MODERATE]:
            return ActivityTier.MODERATE
        else:
            return ActivityTier.ACTIVE

    @property
    def tier_multiplier(self) -> float:
        """Get decay rate multiplier for current tier."""
        return ACTIVITY_TIER_MULTIPLIERS[self.activity_tier]

    def reset_activity(self) -> None:
        """Reset activity timer (e.g., after transaction)."""
        self.last_activity = datetime.now()
        self.days_inactive_sim = 0.0
        # Boost activity score on action
        self.activity_score = min(1.0, self.activity_score + 0.1)

    def record_participation(self, action_type: str) -> None:
        """Record a participation action (reduces future decay)."""
        self.participation_actions += 1
        self.reset_activity()
        # Bigger boost for governance actions
        if action_type in ("vote_proposal", "create_proposal", "complete_cabr_task"):
            self.activity_score = min(1.0, self.activity_score + 0.2)

    def decay_activity_score(self, rate: float = 0.01) -> None:
        """Decay activity score over time (called each epoch)."""
        self.activity_score = max(0.0, self.activity_score - rate)

    def stake(self, amount: float) -> float:
        """Move UPS from liquid to staked (ICE state)."""
        stake_amount = min(amount, self.ups_balance)
        self.ups_balance -= stake_amount
        self.staked_ups += stake_amount
        self.reset_activity()
        return stake_amount

    def unstake(self, amount: float) -> float:
        """Move UPS from staked to liquid (ICE → LIQUID)."""
        unstake_amount = min(amount, self.staked_ups)
        self.staked_ups -= unstake_amount
        self.ups_balance += unstake_amount
        return unstake_amount


class DemurrageEngine:
    """Manages bio-decay for LIQUID UPS tokens (WSP 26 Section 16).

    UPS = SATOSHI TAGGING (012-confirmed):
    - UPS is tagged to satoshis (BTC smallest unit)
    - BTC is LOCKED in reserve (Hotel California - never leaves)
    - UPS decay = UPS REDISTRIBUTED (not burned, not to BTC)
    - Decayed UPS flows back to ecosystem

    Decay Routing (UPS REDISTRIBUTION):
    - 80% → Network Pool (ecosystem operations, agent rewards)
    - 20% → pAVS Treasury (platform infrastructure)

    NOTE: This is pAVS System Treasury, NOT F_i Fund.
    F_i Fund (4% of F_i pool) is per-FoundUp, handled in pool_distribution.py.

    Features (012-Spec v4.0):
    - Activity-based modulation (tier multipliers)
    - Notification system (warnings, stake prompts)
    - Auto-stake for dormant accounts
    - Dormant value recycling

    NOTE: All parameters require extensive simulation testing (012-directive).

    Anti-hoarding: UPS decays → motivates staking or activity.
    """

    def __init__(
        self,
        config: Optional[DecayConfig] = None,
        btc_reserve: Optional[BTCReserve] = None,
    ):
        self.config = config or DecayConfig()
        # NOTE: btc_reserve retained for future exit fee processing
        # Demurrage does NOT add to BTC - it redistributes UPS (012-confirmed)
        self.btc_reserve = btc_reserve or get_btc_reserve()
        self.wallets: Dict[str, WalletState] = {}

        # Statistics (UPS redistribution tracking)
        self.total_decayed: float = 0.0  # Total UPS decayed from wallets
        self.total_to_network_pool: float = 0.0  # UPS redistributed to Network Pool (80%)
        self.total_to_pavs_treasury: float = 0.0  # UPS redistributed to Treasury (20%)
        self.total_auto_staked: float = 0.0
        self.total_recycled: float = 0.0

        # Notification queue
        self.pending_notifications: List[DecayNotification] = []

        # Auto-stake targets (FoundUp IDs with high momentum)
        self.auto_stake_targets: List[str] = []

        # Per-FoundUp ratio overrides (set via configure_foundup_ratio)
        self.foundup_ratios: Dict[str, Tuple[float, float]] = {}

        # Treasury state tracking (for adaptive adjustment)
        self.pavs_treasury_balance: float = 0.0
        self.pavs_treasury_target: float = 10000.0  # Target treasury balance (configurable)
        self._last_critical_health_bucket: Optional[int] = None

    def get_redistribution_ratios(
        self,
        foundup_id: Optional[str] = None,
        foundup_type: Optional[FoundUpType] = None,
    ) -> Tuple[float, float]:
        """Get redistribution ratios (network_pool, treasury) for decay routing.

        Priority order:
        1. Per-FoundUp override (if configured)
        2. FoundUp type default (if type specified)
        3. Adaptive adjustment based on treasury health
        4. Global config defaults

        Args:
            foundup_id: FoundUp identifier (for per-FoundUp overrides)
            foundup_type: FoundUp type (for type-based defaults)

        Returns:
            (network_pool_ratio, treasury_ratio) tuple, sums to 1.0
        """
        # Check per-FoundUp override first
        if foundup_id and foundup_id in self.foundup_ratios:
            return self.foundup_ratios[foundup_id]

        # Get base ratio from FoundUp type or config
        if foundup_type and foundup_type in FOUNDUP_TYPE_RATIOS:
            network_ratio, treasury_ratio = FOUNDUP_TYPE_RATIOS[foundup_type]
        else:
            network_ratio = self.config.decay_to_network_pool_ratio
            treasury_ratio = self.config.decay_to_pavs_treasury_ratio

        # Apply adaptive adjustment based on treasury health
        if self.pavs_treasury_target > 0:
            treasury_health = self.pavs_treasury_balance / self.pavs_treasury_target

            if treasury_health < self.config.pavs_treasury_critical_threshold:
                # Treasury critically low → increase treasury ratio
                # Shift up to 15% more to treasury (within bounds)
                shift = min(0.15, self.config.max_network_pool_ratio - self.config.min_network_pool_ratio)
                network_ratio = max(self.config.min_network_pool_ratio, network_ratio - shift)
                treasury_ratio = 1.0 - network_ratio
                # Log only when critical-health bucket changes to avoid log flood.
                critical_bucket = int(treasury_health * 100)
                if critical_bucket != self._last_critical_health_bucket:
                    logger.warning(
                        f"[Demurrage] Treasury critical ({treasury_health:.1%}) - "
                        f"adjusted ratios: {network_ratio:.0%}/{treasury_ratio:.0%}"
                    )
                    self._last_critical_health_bucket = critical_bucket
            elif treasury_health > self.config.pavs_treasury_healthy_threshold:
                # Treasury healthy → can favor network pool slightly
                shift = min(0.05, self.config.max_network_pool_ratio - network_ratio)
                network_ratio = min(self.config.max_network_pool_ratio, network_ratio + shift)
                treasury_ratio = 1.0 - network_ratio
                self._last_critical_health_bucket = None

        return (network_ratio, treasury_ratio)

    def configure_foundup_ratio(
        self,
        foundup_id: str,
        network_ratio: float,
        treasury_ratio: float,
    ) -> bool:
        """Configure per-FoundUp redistribution ratio override.

        Called by 0102 SmartDAO for autonomous ratio adjustment.
        NO human voting - 0102 agents make these decisions.

        Args:
            foundup_id: FoundUp identifier
            network_ratio: Portion to Network Pool (0.0-1.0)
            treasury_ratio: Portion to pAVS Treasury (0.0-1.0)

        Returns:
            True if configured successfully
        """
        # Validate ratios
        if not (0.0 <= network_ratio <= 1.0 and 0.0 <= treasury_ratio <= 1.0):
            logger.error(f"[Demurrage] Invalid ratios: {network_ratio}, {treasury_ratio}")
            return False

        if abs(network_ratio + treasury_ratio - 1.0) > 0.001:
            logger.error(f"[Demurrage] Ratios must sum to 1.0: {network_ratio + treasury_ratio}")
            return False

        # Check bounds
        if network_ratio < self.config.min_network_pool_ratio:
            logger.warning(
                f"[Demurrage] Network ratio {network_ratio} below min {self.config.min_network_pool_ratio}"
            )
            return False

        if network_ratio > self.config.max_network_pool_ratio:
            logger.warning(
                f"[Demurrage] Network ratio {network_ratio} above max {self.config.max_network_pool_ratio}"
            )
            return False

        self.foundup_ratios[foundup_id] = (network_ratio, treasury_ratio)
        logger.info(
            f"[Demurrage] Configured {foundup_id}: "
            f"{network_ratio:.0%} network / {treasury_ratio:.0%} treasury"
        )
        return True

    def update_pavs_treasury_balance(self, balance: float) -> None:
        """Update treasury balance for adaptive ratio calculation.

        Args:
            balance: Current treasury UPS balance
        """
        self.pavs_treasury_balance = balance

    def set_pavs_treasury_target(self, target: float) -> None:
        """Set treasury target for adaptive ratio calculation.

        Args:
            target: Target treasury UPS balance
        """
        self.pavs_treasury_target = target

    def register_wallet(self, human_id: str, initial_balance: float = 0.0) -> WalletState:
        """Register a wallet for decay tracking."""
        wallet = WalletState(
            human_id=human_id,
            ups_balance=initial_balance,
            last_activity=datetime.now(),
        )
        self.wallets[human_id] = wallet
        return wallet

    def calculate_decay_rate(
        self,
        days_inactive: float,
        tier_multiplier: float = 1.0,
    ) -> float:
        """Calculate adaptive decay rate using Michaelis-Menten.

        λ(t) = λ_min + (λ_max - λ_min) · (D / (K + D))
        λ_eff = λ(t) × τ_tier (activity tier multiplier)

        Args:
            days_inactive: Days since last activity
            tier_multiplier: Activity tier multiplier (0.5-2.5)

        Returns:
            Effective daily decay rate
        """
        d = days_inactive
        k = self.config.k_constant
        lambda_min = self.config.lambda_min
        lambda_max = self.config.lambda_max

        # Michaelis-Menten kinetics (base rate)
        base_rate = lambda_min + (lambda_max - lambda_min) * (d / (k + d))

        # Apply activity tier multiplier if enabled
        if self.config.enable_activity_modulation:
            effective_rate = base_rate * tier_multiplier
        else:
            effective_rate = base_rate

        # Cap at maximum daily decay
        return min(effective_rate, self.config.max_daily_decay)

    def apply_decay(
        self,
        human_id: str,
        time_elapsed_days: float = 1.0,
        is_pulse_window: bool = False,
        foundup_id: Optional[str] = None,
        foundup_type: Optional[FoundUpType] = None,
    ) -> Tuple[float, float]:
        """Apply decay to a wallet's LIQUID UPS.

        Args:
            human_id: Wallet owner
            time_elapsed_days: Time period for decay
            is_pulse_window: Whether in circadian pulse (6-7 PM)
            foundup_id: FoundUp context (for per-FoundUp ratio overrides)
            foundup_type: FoundUp type (for type-based ratio defaults)
            is_pulse_window: Whether in circadian pulse (6-7 PM)

        Returns:
            (decay_amount, new_balance) tuple
        """
        wallet = self.wallets.get(human_id)
        if not wallet or wallet.ups_balance <= 0:
            return (0.0, 0.0)

        # Advance deterministic simulation clocks.
        wallet.days_inactive_sim += max(0.0, float(time_elapsed_days))
        wallet.days_since_last_notification_sim += max(0.0, float(time_elapsed_days))

        # Get activity tier multiplier
        tier_multiplier = wallet.tier_multiplier

        # Calculate decay rate with tier modulation
        decay_rate = self.calculate_decay_rate(wallet.days_inactive, tier_multiplier)

        # Apply circadian boost if in pulse window
        if is_pulse_window:
            decay_rate *= self.config.circadian_boost

        # Decay activity score over time
        wallet.decay_activity_score(0.01 * time_elapsed_days)

        # Exponential decay: U(t) = U₀ · e^(-λ·t)
        decay_factor = math.exp(-decay_rate * time_elapsed_days)
        new_balance = wallet.ups_balance * decay_factor
        decay_amount = wallet.ups_balance - new_balance

        if decay_amount > 0:
            # Update wallet
            wallet.ups_balance = new_balance
            wallet.total_decayed += decay_amount
            wallet.decay_warnings += 1

            # UPS REDISTRIBUTION (012-confirmed):
            # Decayed UPS is redistributed (not burned, not to BTC)
            # BTC stays locked in reserve (Hotel California unchanged)
            # Ratios vary by: FoundUp type, treasury health, governance config
            network_ratio, treasury_ratio = self.get_redistribution_ratios(
                foundup_id=foundup_id,
                foundup_type=foundup_type,
            )

            network_portion = decay_amount * network_ratio
            treasury_portion = decay_amount * treasury_ratio

            # Track UPS redistribution
            self.total_decayed += decay_amount
            self.total_to_network_pool += network_portion
            self.total_to_pavs_treasury += treasury_portion

            logger.info(
                f"[Demurrage] {human_id}: {decay_amount:.4f} UPS decayed "
                f"(tier: {wallet.activity_tier.value}, rate: {decay_rate*100:.3f}%/day) "
                f"-> redistributed: {network_portion:.4f} network + {treasury_portion:.4f} treasury"
            )

            # Generate notification if needed
            self._maybe_generate_notification(wallet, decay_rate, decay_amount)

        return (decay_amount, new_balance)

    def _maybe_generate_notification(
        self,
        wallet: WalletState,
        decay_rate: float,
        decay_amount: float,
    ) -> None:
        """Generate decay notification if threshold met."""
        days = wallet.days_inactive

        # Rate limit notifications by simulation-time (max 1/day per wallet)
        if wallet.days_since_last_notification_sim < 1.0:
            return

        # Determine notification type
        if days >= self.config.critical_threshold_days:
            notif_type = NotificationType.CRITICAL
            message = (
                f"CRITICAL: Your {wallet.ups_balance:.2f} UPS is decaying rapidly! "
                f"Stake or transact to preserve value."
            )
        elif days >= self.config.notification_threshold_days:
            notif_type = NotificationType.WARNING
            message = (
                f"WARNING: Wallet inactive for {days:.0f} days. "
                f"Decay rate increasing. Consider staking."
            )
        else:
            return  # No notification needed

        # Add stake prompt if auto-stake available
        auto_stake_options = self.auto_stake_targets[:3] if self.config.enable_auto_stake else []

        notification = DecayNotification(
            notification_type=notif_type,
            human_id=wallet.human_id,
            message=message,
            decay_rate_percent=decay_rate * 100,
            daily_loss_estimate=wallet.ups_balance * decay_rate,
            ups_balance=wallet.ups_balance,
            days_inactive=days,
            timestamp=datetime.now().isoformat(),
            auto_stake_options=auto_stake_options,
        )

        self.pending_notifications.append(notification)
        wallet.last_notification = datetime.now()
        wallet.days_since_last_notification_sim = 0.0
        wallet.notifications_sent += 1

        logger.info(f"[Demurrage] Notification sent to {wallet.human_id}: {notif_type.value}")

    def apply_decay_all(self, time_elapsed_days: float = 1.0) -> Dict[str, float]:
        """Apply decay to all wallets.

        Returns:
            Dict of human_id -> decay_amount
        """
        results = {}
        for human_id in self.wallets:
            decay_amount, _ = self.apply_decay(human_id, time_elapsed_days)
            if decay_amount > 0:
                results[human_id] = decay_amount
        return results

    def process_auto_stakes(self) -> Dict[str, float]:
        """Process auto-stake for eligible dormant wallets.

        Wallets eligible if:
        - User opted into auto-stake
        - Inactive >= auto_stake_dormant_threshold_days
        - Has liquid UPS balance
        - Auto-stake targets available

        Returns:
            Dict of human_id -> amount_auto_staked
        """
        if not self.config.enable_auto_stake:
            return {}

        if not self.auto_stake_targets:
            return {}

        results = {}
        threshold_days = self.config.auto_stake_dormant_threshold_days
        max_pct = self.config.auto_stake_max_percentage

        for human_id, wallet in self.wallets.items():
            # Check eligibility
            if not wallet.auto_stake_opted_in:
                continue
            if wallet.days_inactive < threshold_days:
                continue
            if wallet.ups_balance <= 0:
                continue

            # Calculate auto-stake amount (up to max_pct of balance)
            stake_amount = wallet.ups_balance * max_pct
            if stake_amount < 1.0:  # Minimum threshold
                continue

            # Execute auto-stake
            actual_staked = wallet.stake(stake_amount)
            results[human_id] = actual_staked
            self.total_auto_staked += actual_staked

            # Send notification
            notification = DecayNotification(
                notification_type=NotificationType.AUTO_STAKE,
                human_id=human_id,
                message=f"Auto-staked {actual_staked:.2f} UPS to preserve value.",
                decay_rate_percent=0.0,
                daily_loss_estimate=0.0,
                ups_balance=wallet.ups_balance,
                days_inactive=wallet.days_inactive,
                timestamp=datetime.now().isoformat(),
                auto_stake_options=self.auto_stake_targets[:3],
            )
            self.pending_notifications.append(notification)

            logger.info(
                f"[Demurrage] Auto-staked {actual_staked:.2f} UPS for {human_id} "
                f"(inactive: {wallet.days_inactive:.0f} days)"
            )

        return results

    def process_dormant_recycling(self) -> Dict[str, float]:
        """Recycle value from long-dormant accounts to participation pool.

        Dormant accounts (>90 days) have portion recycled to participation pool.
        This prevents permanent dead-account accumulation.

        Returns:
            Dict of human_id -> amount_recycled
        """
        if not self.config.enable_dormant_recycling:
            return {}

        results = {}
        threshold_days = self.config.dormant_threshold_days
        daily_rate = self.config.recycling_rate_per_day

        for human_id, wallet in self.wallets.items():
            if wallet.days_inactive < threshold_days:
                continue
            if wallet.ups_balance <= 0:
                continue

            # Calculate recycling amount (1% per day beyond threshold)
            days_beyond = wallet.days_inactive - threshold_days
            recycle_pct = min(1.0, daily_rate * days_beyond)  # Cap at 100%
            recycle_amount = wallet.ups_balance * recycle_pct

            if recycle_amount < 0.1:  # Minimum threshold
                continue

            # Execute recycling
            wallet.ups_balance -= recycle_amount
            wallet.recycled_to_pool += recycle_amount
            results[human_id] = recycle_amount
            self.total_recycled += recycle_amount
            self.total_to_participation_pool += recycle_amount

            logger.info(
                f"[Demurrage] Recycled {recycle_amount:.2f} UPS from {human_id} "
                f"to participation pool (dormant: {wallet.days_inactive:.0f} days)"
            )

        return results

    def set_auto_stake_targets(self, foundup_ids: List[str]) -> None:
        """Set list of FoundUp IDs eligible for auto-stake.

        Typically high-momentum FoundUps selected by governance or algorithm.

        Args:
            foundup_ids: List of FoundUp IDs
        """
        self.auto_stake_targets = foundup_ids
        logger.info(f"[Demurrage] Auto-stake targets updated: {len(foundup_ids)} FoundUps")

    def opt_in_auto_stake(self, human_id: str, opt_in: bool = True) -> bool:
        """Opt a wallet in/out of auto-stake.

        Args:
            human_id: Wallet owner
            opt_in: True to enable, False to disable

        Returns:
            True if successful
        """
        wallet = self.wallets.get(human_id)
        if not wallet:
            return False

        wallet.auto_stake_opted_in = opt_in
        logger.info(f"[Demurrage] {human_id} auto-stake: {'enabled' if opt_in else 'disabled'}")
        return True

    def get_pending_notifications(self, clear: bool = True) -> List[DecayNotification]:
        """Get pending notifications.

        Args:
            clear: Whether to clear the queue after retrieval

        Returns:
            List of pending notifications
        """
        notifications = self.pending_notifications.copy()
        if clear:
            self.pending_notifications = []
        return notifications

    def reset_activity(self, human_id: str) -> None:
        """Reset activity timer after user action (stops decay acceleration)."""
        wallet = self.wallets.get(human_id)
        if wallet:
            wallet.reset_activity()
            logger.debug(f"[Demurrage] {human_id}: Activity reset (decay timer → 0)")

    def add_to_wallet(self, human_id: str, amount: float) -> None:
        """Add UPS to wallet (also resets activity)."""
        if human_id not in self.wallets:
            self.register_wallet(human_id, amount)
        else:
            wallet = self.wallets[human_id]
            wallet.ups_balance += amount
            wallet.reset_activity()

    def get_decay_warning(self, human_id: str) -> Optional[str]:
        """Get decay warning for a wallet."""
        wallet = self.wallets.get(human_id)
        if not wallet:
            return None

        if wallet.ups_balance <= 0:
            return None

        days = wallet.days_inactive
        rate = self.calculate_decay_rate(days)

        if days >= 7:
            severity = "CRITICAL" if rate >= self.config.lambda_max * 0.8 else "WARNING"
            daily_loss = wallet.ups_balance * rate
            return (
                f"{severity}: {wallet.ups_balance:.2f} UPS is decaying at "
                f"{rate*100:.2f}%/day ({daily_loss:.2f} UPS/day). "
                f"Stake or transact to stop decay!"
            )
        elif days >= 3:
            return (
                f"NOTICE: Wallet inactive for {days:.0f} days. "
                f"Decay rate increasing. Stake to preserve value."
            )
        return None

    def get_stats(self) -> Dict:
        """Get demurrage engine statistics."""
        active_wallets = sum(1 for w in self.wallets.values() if w.ups_balance > 0)
        total_liquid = sum(w.ups_balance for w in self.wallets.values())
        total_staked = sum(w.staked_ups for w in self.wallets.values())

        # Count by tier
        tier_counts = {tier.value: 0 for tier in ActivityTier}
        for w in self.wallets.values():
            tier_counts[w.activity_tier.value] += 1

        # Count auto-stake opted-in
        auto_stake_count = sum(1 for w in self.wallets.values() if w.auto_stake_opted_in)

        # Count dormant
        dormant_count = sum(
            1 for w in self.wallets.values()
            if w.days_inactive >= self.config.dormant_threshold_days
        )

        # Get current adaptive ratios (default context)
        current_network, current_treasury = self.get_redistribution_ratios()
        treasury_health = (
            self.pavs_treasury_balance / self.pavs_treasury_target
            if self.pavs_treasury_target > 0 else 0.0
        )

        return {
            "total_wallets": len(self.wallets),
            "active_wallets": active_wallets,
            "total_liquid_ups": round(total_liquid, 2),
            "total_staked_ups": round(total_staked, 2),
            "total_decayed": round(self.total_decayed, 4),
            "total_to_network_pool": round(self.total_to_network_pool, 4),
            "total_to_pavs_treasury": round(self.total_to_pavs_treasury, 4),
            "total_auto_staked": round(self.total_auto_staked, 2),
            "total_recycled": round(self.total_recycled, 2),
            "by_tier": tier_counts,
            "auto_stake_opted_in": auto_stake_count,
            "dormant_wallets": dormant_count,
            "pending_notifications": len(self.pending_notifications),
            # Adaptive ratio info
            "current_network_ratio": round(current_network, 3),
            "current_treasury_ratio": round(current_treasury, 3),
            "treasury_health": round(treasury_health, 3),
            "pavs_treasury_balance": round(self.pavs_treasury_balance, 2),
            "pavs_treasury_target": round(self.pavs_treasury_target, 2),
            "foundup_overrides": len(self.foundup_ratios),
        }

    def run_epoch_cycle(self, time_elapsed_days: float = 1.0) -> Dict:
        """Run a full demurrage epoch cycle.

        Executes:
        1. Apply decay to all wallets
        2. Process auto-stakes for eligible dormant accounts
        3. Process dormant value recycling

        Args:
            time_elapsed_days: Time period (default 1 day)

        Returns:
            Summary of epoch activity
        """
        # Phase 1: Apply decay
        decay_results = self.apply_decay_all(time_elapsed_days)

        # Phase 2: Auto-stake eligible accounts
        auto_stake_results = self.process_auto_stakes()

        # Phase 3: Dormant recycling
        recycle_results = self.process_dormant_recycling()

        return {
            "decayed_wallets": len(decay_results),
            "total_decayed": sum(decay_results.values()),
            "auto_staked_wallets": len(auto_stake_results),
            "total_auto_staked": sum(auto_stake_results.values()),
            "recycled_wallets": len(recycle_results),
            "total_recycled": sum(recycle_results.values()),
            "notifications_generated": len(self.pending_notifications),
        }


# Relief activities that reset decay timer
DECAY_RELIEF_ACTIVITIES = {
    # FoundUp Actions
    "list_item": {"relief_hours": 24, "reward": 1.0},
    "sell_item": {"relief_hours": 48, "reward": 2.0},
    "host_storage": {"relief_hours": 24, "reward": 0.01},

    # Social Actions
    "invite_friend": {"relief_hours": 72, "reward": 10.0},
    "share_boost": {"relief_hours": 12, "reward": 0.5},

    # Governance
    "vote_proposal": {"relief_hours": 24, "reward": 0.1},
    "create_proposal": {"relief_hours": 168, "reward": 5.0},

    # Cross-FoundUp
    "use_other_foundup": {"relief_hours": 24, "reward": 0.5},
    "complete_cabr_task": {"relief_hours": 48, "reward": 5.0},

    # Staking (moves to ICE state - no decay)
    "stake_ups": {"relief_hours": None, "reward": 0.0},  # None = permanent while staked
}


def get_relief_for_activity(activity_type: str) -> Optional[Dict]:
    """Get decay relief configuration for an activity."""
    return DECAY_RELIEF_ACTIVITIES.get(activity_type)
