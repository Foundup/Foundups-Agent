"""Rage Quit - Moloch-style Fair Exit for Failing FoundUps.

When a FoundUp is failing or abandoned, users deserve a fair exit.
Normal exit fees (11%) are punitive for situations beyond user control.

Rage Quit enables:
- Pro-rata exit at treasury value (not market price)
- Minimal fee (2% vs 11%)
- Only available when FoundUp meets failure criteria

This prevents users from feeling TRAPPED in failing projects.

Failure Criteria (any triggers eligibility):
1. No activity for 12 epochs (1 year)
2. Backing drops below 50%
3. Founder ragequits first
4. Governance vote (future)

Based on Moloch DAO: "All members can withdraw their share of assets
from it by ragequitting their shares... pro-rata claim on the treasury's assets."
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class FailureReason(Enum):
    """Why a FoundUp is considered failing."""
    NO_ACTIVITY = "no_activity"  # Abandoned - no work for 12 epochs
    LOW_BACKING = "low_backing"  # Underbacked - < 50%
    FOUNDER_EXIT = "founder_exit"  # Founder ragequit first
    GOVERNANCE = "governance"  # Community vote declared failure
    NONE = "none"  # Not failing


@dataclass
class FoundUpHealth:
    """Health status of a FoundUp for rage quit eligibility."""
    foundup_id: str
    is_failing: bool = False
    failure_reason: FailureReason = FailureReason.NONE

    # Activity tracking
    last_activity_epoch: int = 0
    current_epoch: int = 0
    inactive_epochs: int = 0

    # Financial health
    backing_ratio: float = 1.0
    treasury_value_ups: float = 0.0
    total_fi_supply: float = 0.0

    # Founder status
    founder_exited: bool = False
    founder_exit_timestamp: Optional[datetime] = None

    # Grace period
    grace_period_start: Optional[datetime] = None
    grace_period_days: int = 7


@dataclass
class RageQuitConfig:
    """Configuration for rage quit thresholds."""

    # Inactivity threshold (epochs)
    max_inactive_epochs: int = 12  # 1 year

    # Backing threshold
    min_backing_ratio: float = 0.50  # 50%

    # Grace period before rage quit activates
    grace_period_days: int = 7

    # Rage quit fee (much lower than normal 11%)
    rage_quit_fee: float = 0.02  # 2%

    # Founder must wait longer after ragequitting before project declared failed
    founder_cooldown_days: int = 30


@dataclass
class RageQuitResult:
    """Result of a rage quit operation."""
    success: bool
    human_id: str
    foundup_id: str
    fi_burned: float
    ups_received: float
    fee_paid: float
    failure_reason: FailureReason
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error: Optional[str] = None


class RageQuitAdapter:
    """Moloch-style fair exit for failing FoundUps.

    Enables pro-rata exit at treasury value with minimal fee
    when a FoundUp meets failure criteria.
    """

    def __init__(self, config: Optional[RageQuitConfig] = None):
        self.config = config or RageQuitConfig()

        # Track FoundUp health
        self.health_cache: Dict[str, FoundUpHealth] = {}

        # Rage quit history
        self.rage_quits: List[RageQuitResult] = []

        # Statistics
        self.total_rage_quits: int = 0
        self.total_fi_burned: float = 0.0
        self.total_ups_returned: float = 0.0
        self.total_fees_collected: float = 0.0

    def register_foundup(
        self,
        foundup_id: str,
        treasury_value_ups: float,
        total_fi_supply: float,
        current_epoch: int = 0,
    ) -> FoundUpHealth:
        """Register a FoundUp for health tracking."""
        health = FoundUpHealth(
            foundup_id=foundup_id,
            last_activity_epoch=current_epoch,
            current_epoch=current_epoch,
            treasury_value_ups=treasury_value_ups,
            total_fi_supply=total_fi_supply,
        )
        self.health_cache[foundup_id] = health
        return health

    def record_activity(self, foundup_id: str, epoch: int) -> None:
        """Record activity for a FoundUp (resets inactivity counter)."""
        if foundup_id not in self.health_cache:
            return

        health = self.health_cache[foundup_id]
        health.last_activity_epoch = epoch
        health.current_epoch = epoch
        health.inactive_epochs = 0

        # Clear grace period if activity resumes
        if health.grace_period_start:
            logger.info(
                f"[RageQuit:{foundup_id}] Activity resumed - "
                f"grace period cancelled"
            )
            health.grace_period_start = None
            health.is_failing = False
            health.failure_reason = FailureReason.NONE

    def advance_epoch(self, foundup_id: str, new_epoch: int) -> FoundUpHealth:
        """Advance epoch and check for inactivity."""
        if foundup_id not in self.health_cache:
            raise ValueError(f"Unknown FoundUp: {foundup_id}")

        health = self.health_cache[foundup_id]
        health.current_epoch = new_epoch
        health.inactive_epochs = new_epoch - health.last_activity_epoch

        # Check inactivity failure
        if health.inactive_epochs >= self.config.max_inactive_epochs:
            self._mark_failing(health, FailureReason.NO_ACTIVITY)

        return health

    def update_backing(self, foundup_id: str, backing_ratio: float) -> FoundUpHealth:
        """Update backing ratio and check for underbacking failure."""
        if foundup_id not in self.health_cache:
            raise ValueError(f"Unknown FoundUp: {foundup_id}")

        health = self.health_cache[foundup_id]
        health.backing_ratio = backing_ratio

        if backing_ratio < self.config.min_backing_ratio:
            self._mark_failing(health, FailureReason.LOW_BACKING)

        return health

    def update_treasury(
        self,
        foundup_id: str,
        treasury_value_ups: float,
        total_fi_supply: float,
    ) -> None:
        """Update treasury and supply values."""
        if foundup_id not in self.health_cache:
            return

        health = self.health_cache[foundup_id]
        health.treasury_value_ups = treasury_value_ups
        health.total_fi_supply = total_fi_supply

    def record_founder_exit(
        self,
        foundup_id: str,
        founder_id: str,
    ) -> FoundUpHealth:
        """Record when a founder exits (potential failure trigger)."""
        if foundup_id not in self.health_cache:
            raise ValueError(f"Unknown FoundUp: {foundup_id}")

        health = self.health_cache[foundup_id]
        health.founder_exited = True
        health.founder_exit_timestamp = datetime.now()

        logger.warning(
            f"[RageQuit:{foundup_id}] Founder {founder_id} exited - "
            f"failure evaluation in {self.config.founder_cooldown_days} days"
        )

        return health

    def _mark_failing(self, health: FoundUpHealth, reason: FailureReason) -> None:
        """Mark a FoundUp as failing and start grace period."""
        if health.is_failing:
            return  # Already failing

        health.is_failing = True
        health.failure_reason = reason
        health.grace_period_start = datetime.now()

        logger.warning(
            f"[RageQuit:{health.foundup_id}] FAILING - reason: {reason.value}, "
            f"grace period: {health.grace_period_days} days"
        )

    def is_rage_quit_available(self, foundup_id: str) -> Tuple[bool, Optional[FailureReason]]:
        """Check if rage quit is available for a FoundUp.

        Returns:
            (available, failure_reason) tuple
        """
        if foundup_id not in self.health_cache:
            return (False, None)

        health = self.health_cache[foundup_id]

        if not health.is_failing:
            return (False, None)

        # Check grace period elapsed
        if health.grace_period_start:
            elapsed = datetime.now() - health.grace_period_start
            if elapsed < timedelta(days=health.grace_period_days):
                return (False, None)  # Still in grace period

        # Check founder cooldown
        if health.failure_reason == FailureReason.FOUNDER_EXIT:
            if health.founder_exit_timestamp:
                elapsed = datetime.now() - health.founder_exit_timestamp
                if elapsed < timedelta(days=self.config.founder_cooldown_days):
                    return (False, None)  # Founder cooldown not elapsed

        return (True, health.failure_reason)

    def calculate_pro_rata(
        self,
        foundup_id: str,
        fi_amount: float,
    ) -> Tuple[float, float]:
        """Calculate pro-rata UPS value for F_i tokens.

        Returns:
            (ups_value, fee) tuple
        """
        if foundup_id not in self.health_cache:
            raise ValueError(f"Unknown FoundUp: {foundup_id}")

        health = self.health_cache[foundup_id]

        if health.total_fi_supply <= 0:
            return (0.0, 0.0)

        # Pro-rata share of treasury
        share = fi_amount / health.total_fi_supply
        pro_rata_value = share * health.treasury_value_ups

        # Apply rage quit fee (2% vs normal 11%)
        fee = pro_rata_value * self.config.rage_quit_fee

        return (pro_rata_value - fee, fee)

    def rage_quit(
        self,
        human_id: str,
        foundup_id: str,
        fi_amount: float,
    ) -> RageQuitResult:
        """Execute a rage quit - exit at pro-rata value.

        Args:
            human_id: User requesting exit
            foundup_id: FoundUp to exit from
            fi_amount: F_i tokens to burn

        Returns:
            RageQuitResult with success/failure details
        """
        # Check eligibility
        available, reason = self.is_rage_quit_available(foundup_id)

        if not available:
            return RageQuitResult(
                success=False,
                human_id=human_id,
                foundup_id=foundup_id,
                fi_burned=0.0,
                ups_received=0.0,
                fee_paid=0.0,
                failure_reason=FailureReason.NONE,
                error="Rage quit not available for this FoundUp",
            )

        # Calculate pro-rata value
        ups_received, fee = self.calculate_pro_rata(foundup_id, fi_amount)

        if ups_received <= 0:
            return RageQuitResult(
                success=False,
                human_id=human_id,
                foundup_id=foundup_id,
                fi_burned=0.0,
                ups_received=0.0,
                fee_paid=0.0,
                failure_reason=reason or FailureReason.NONE,
                error="No treasury value to claim",
            )

        # Execute rage quit
        health = self.health_cache[foundup_id]
        health.total_fi_supply -= fi_amount
        health.treasury_value_ups -= (ups_received + fee)

        # Create result
        result = RageQuitResult(
            success=True,
            human_id=human_id,
            foundup_id=foundup_id,
            fi_burned=fi_amount,
            ups_received=ups_received,
            fee_paid=fee,
            failure_reason=reason or FailureReason.NONE,
        )

        # Update statistics
        self.rage_quits.append(result)
        self.total_rage_quits += 1
        self.total_fi_burned += fi_amount
        self.total_ups_returned += ups_received
        self.total_fees_collected += fee

        logger.info(
            f"[RageQuit:{foundup_id}] {human_id} rage quit: "
            f"{fi_amount:.2f} F_i -> {ups_received:.2f} UPS "
            f"(fee: {fee:.2f}, reason: {reason.value if reason else 'unknown'})"
        )

        return result

    def get_foundup_status(self, foundup_id: str) -> Optional[Dict]:
        """Get rage quit status for a FoundUp."""
        if foundup_id not in self.health_cache:
            return None

        health = self.health_cache[foundup_id]
        available, reason = self.is_rage_quit_available(foundup_id)

        return {
            "foundup_id": foundup_id,
            "is_failing": health.is_failing,
            "failure_reason": health.failure_reason.value,
            "rage_quit_available": available,
            "inactive_epochs": health.inactive_epochs,
            "backing_ratio": health.backing_ratio,
            "treasury_value_ups": health.treasury_value_ups,
            "total_fi_supply": health.total_fi_supply,
            "founder_exited": health.founder_exited,
            "grace_period_start": (
                health.grace_period_start.isoformat()
                if health.grace_period_start else None
            ),
            "pro_rata_price": (
                health.treasury_value_ups / health.total_fi_supply
                if health.total_fi_supply > 0 else 0.0
            ),
        }

    def get_stats(self) -> Dict:
        """Get rage quit system statistics."""
        failing_foundups = [
            fid for fid, h in self.health_cache.items() if h.is_failing
        ]

        return {
            "total_foundups_tracked": len(self.health_cache),
            "failing_foundups": len(failing_foundups),
            "total_rage_quits": self.total_rage_quits,
            "total_fi_burned": self.total_fi_burned,
            "total_ups_returned": self.total_ups_returned,
            "total_fees_collected": self.total_fees_collected,
            "rage_quit_fee_rate": f"{self.config.rage_quit_fee * 100:.1f}%",
        }


# Singleton instance
_rage_quit_adapter: Optional[RageQuitAdapter] = None


def get_rage_quit_adapter() -> RageQuitAdapter:
    """Get singleton rage quit adapter instance."""
    global _rage_quit_adapter
    if _rage_quit_adapter is None:
        _rage_quit_adapter = RageQuitAdapter()
    return _rage_quit_adapter


def reset_rage_quit_adapter() -> None:
    """Reset rage quit adapter (for testing)."""
    global _rage_quit_adapter
    _rage_quit_adapter = None
