"""Emergency Reserve Fund - Last Line of Defense.

Based on Ethena's $32.7M reserve fund model.

Purpose:
- Collect 10% of all fees into emergency fund
- Deploy when circuit breaker activates
- Restore backing ratio during stress
- Never touched during normal operation

This provides a buffer against tail risks and builds user confidence.

"Importance of adequate reserve sizing" - Ethena research
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class ReserveSourceType(Enum):
    """Sources of emergency reserve funds."""
    MINED_EXIT_FEE = "mined_exit_fee"  # 10% of 11% exit fee
    STAKED_EXIT_FEE = "staked_exit_fee"  # 10% of 5% exit fee
    TRADING_FEE = "trading_fee"  # 10% of 2% trading fee
    DEMURRAGE = "demurrage"  # 10% of demurrage decay
    MANUAL_DEPOSIT = "manual_deposit"  # Protocol deposits


class DeploymentReason(Enum):
    """Why emergency funds were deployed."""
    BACKING_RESTORATION = "backing_restoration"
    CIRCUIT_BREAKER_ACTIVE = "circuit_breaker_active"
    RAGE_QUIT_LIQUIDITY = "rage_quit_liquidity"
    GOVERNANCE_APPROVED = "governance_approved"


@dataclass
class ReserveDeposit:
    """A deposit into the emergency reserve."""
    amount_btc: float
    source: ReserveSourceType
    foundup_id: Optional[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ReserveDeployment:
    """A deployment from the emergency reserve."""
    amount_btc: float
    reason: DeploymentReason
    target_foundup_id: Optional[str]
    approved_by: str  # "circuit_breaker" or "governance"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class EmergencyReserveConfig:
    """Configuration for emergency reserve."""

    # Percentage of fees to route to emergency reserve
    reserve_percentage: float = 0.10  # 10%

    # Minimum deployment threshold
    min_deployment_btc: float = 0.001  # Don't deploy tiny amounts

    # Maximum single deployment (% of reserve)
    max_deployment_pct: float = 0.25  # Max 25% of reserve per deployment

    # Circuit breaker backing threshold that triggers deployment
    deployment_trigger_backing: float = 0.60  # Deploy when backing < 60%


@dataclass
class EmergencyReserve:
    """Emergency reserve fund for system stability.

    Collects portion of all fees, deploys during stress.
    Provides confidence that system can weather crises.
    """

    config: EmergencyReserveConfig = field(default_factory=EmergencyReserveConfig)

    # Reserve balance
    btc_balance: float = 0.0

    # Track that we've never cheated
    ever_deployed: bool = False

    # History
    deposits: List[ReserveDeposit] = field(default_factory=list)
    deployments: List[ReserveDeployment] = field(default_factory=list)

    # Source breakdown
    by_source: Dict[str, float] = field(default_factory=lambda: {
        source.value: 0.0 for source in ReserveSourceType
    })

    # Statistics
    total_deposited: float = 0.0
    total_deployed: float = 0.0

    def collect_from_fee(
        self,
        fee_btc: float,
        source: ReserveSourceType,
        foundup_id: Optional[str] = None,
    ) -> float:
        """Route percentage of fee to emergency reserve.

        Args:
            fee_btc: Total fee amount in BTC
            source: Source of the fee
            foundup_id: Optional FoundUp ID

        Returns:
            Amount that went to main reserve (after emergency portion)
        """
        emergency_portion = fee_btc * self.config.reserve_percentage
        main_portion = fee_btc - emergency_portion

        # Deposit to emergency reserve
        self.btc_balance += emergency_portion
        self.total_deposited += emergency_portion
        self.by_source[source.value] = self.by_source.get(source.value, 0.0) + emergency_portion

        # Record deposit
        deposit = ReserveDeposit(
            amount_btc=emergency_portion,
            source=source,
            foundup_id=foundup_id,
        )
        self.deposits.append(deposit)

        logger.debug(
            f"[EmergencyReserve] Collected {emergency_portion:.8f} BTC from {source.value} "
            f"(total reserve: {self.btc_balance:.8f} BTC)"
        )

        return main_portion

    def can_deploy(self) -> bool:
        """Check if deployment is currently allowed.

        Only deploy when circuit breaker is active.
        """
        from .circuit_breaker import get_circuit_breaker, BreakerState

        breaker = get_circuit_breaker()
        return breaker.state in (BreakerState.RESTRICTED, BreakerState.EMERGENCY)

    def calculate_deployment_amount(
        self,
        target_backing_restoration: float,
        current_backing: float,
        total_ups_supply: float,
        btc_price: float,
    ) -> float:
        """Calculate how much BTC to deploy to restore backing.

        Args:
            target_backing_restoration: Target backing ratio (e.g., 0.80)
            current_backing: Current backing ratio
            total_ups_supply: Total UP$ in circulation
            btc_price: Current BTC price in USD

        Returns:
            BTC amount to deploy (capped by config limits)
        """
        if current_backing >= target_backing_restoration:
            return 0.0

        # Calculate UP$ gap
        current_ups_backed = current_backing * total_ups_supply
        target_ups_backed = target_backing_restoration * total_ups_supply
        ups_gap = target_ups_backed - current_ups_backed

        # Convert to BTC needed
        btc_needed = ups_gap / btc_price if btc_price > 0 else 0

        # Apply limits
        max_deployment = self.btc_balance * self.config.max_deployment_pct
        btc_to_deploy = min(btc_needed, max_deployment, self.btc_balance)

        if btc_to_deploy < self.config.min_deployment_btc:
            return 0.0

        return btc_to_deploy

    def deploy(
        self,
        amount_btc: float,
        reason: DeploymentReason,
        target_foundup_id: Optional[str] = None,
    ) -> Tuple[bool, float]:
        """Deploy emergency funds to restore system health.

        Args:
            amount_btc: Amount to deploy
            reason: Why deploying
            target_foundup_id: Optional target FoundUp

        Returns:
            (success, amount_deployed) tuple
        """
        if not self.can_deploy():
            logger.warning(
                "[EmergencyReserve] Deployment blocked - circuit breaker not active"
            )
            return (False, 0.0)

        if amount_btc > self.btc_balance:
            logger.warning(
                f"[EmergencyReserve] Insufficient funds: requested {amount_btc:.8f}, "
                f"available {self.btc_balance:.8f}"
            )
            amount_btc = self.btc_balance

        if amount_btc < self.config.min_deployment_btc:
            return (False, 0.0)

        # Deploy
        self.btc_balance -= amount_btc
        self.total_deployed += amount_btc
        self.ever_deployed = True

        # Record deployment
        deployment = ReserveDeployment(
            amount_btc=amount_btc,
            reason=reason,
            target_foundup_id=target_foundup_id,
            approved_by="circuit_breaker",
        )
        self.deployments.append(deployment)

        logger.warning(
            f"[EmergencyReserve] DEPLOYED {amount_btc:.8f} BTC "
            f"(reason: {reason.value}, remaining: {self.btc_balance:.8f})"
        )

        return (True, amount_btc)

    def deploy_for_backing(
        self,
        current_backing: float,
        total_ups_supply: float,
        btc_price: float,
        target_backing: float = 0.80,
    ) -> Tuple[bool, float]:
        """Automatically deploy to restore backing ratio.

        Args:
            current_backing: Current backing ratio
            total_ups_supply: Total UP$ supply
            btc_price: Current BTC price
            target_backing: Target backing to restore to

        Returns:
            (success, amount_deployed) tuple
        """
        if current_backing >= self.config.deployment_trigger_backing:
            return (False, 0.0)  # Not needed

        amount = self.calculate_deployment_amount(
            target_backing,
            current_backing,
            total_ups_supply,
            btc_price,
        )

        if amount <= 0:
            return (False, 0.0)

        return self.deploy(
            amount,
            DeploymentReason.BACKING_RESTORATION,
        )

    def get_health_score(self) -> float:
        """Get reserve health score (0-1).

        Based on:
        - Balance relative to historical average
        - Never deployed = bonus
        - Diversity of sources
        """
        # Base score from balance
        avg_deposit = self.total_deposited / max(1, len(self.deposits))
        balance_score = min(1.0, self.btc_balance / (avg_deposit * 10)) if avg_deposit > 0 else 0.5

        # Bonus for never deploying (trust building)
        never_deployed_bonus = 0.2 if not self.ever_deployed else 0.0

        # Diversity bonus (funds from multiple sources)
        active_sources = sum(1 for v in self.by_source.values() if v > 0)
        diversity_bonus = min(0.1, active_sources * 0.02)

        return min(1.0, balance_score + never_deployed_bonus + diversity_bonus)

    def get_stats(self) -> Dict:
        """Get emergency reserve statistics."""
        return {
            "btc_balance": self.btc_balance,
            "total_deposited": self.total_deposited,
            "total_deployed": self.total_deployed,
            "ever_deployed": self.ever_deployed,
            "health_score": f"{self.get_health_score():.2%}",
            "by_source": self.by_source,
            "num_deposits": len(self.deposits),
            "num_deployments": len(self.deployments),
            "reserve_percentage": f"{self.config.reserve_percentage * 100:.0f}%",
            "can_deploy_now": self.can_deploy(),
        }


# Singleton instance
_emergency_reserve: Optional[EmergencyReserve] = None


def get_emergency_reserve() -> EmergencyReserve:
    """Get singleton emergency reserve instance."""
    global _emergency_reserve
    if _emergency_reserve is None:
        _emergency_reserve = EmergencyReserve()
    return _emergency_reserve


def reset_emergency_reserve() -> None:
    """Reset emergency reserve (for testing)."""
    global _emergency_reserve
    _emergency_reserve = None
