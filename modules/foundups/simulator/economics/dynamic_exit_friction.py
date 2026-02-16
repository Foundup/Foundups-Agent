"""Dynamic Exit Friction Engine (WSP 26 Section 14).

Implements 012's Dynamic Exit Friction & Liquidity Model:

MATURITY-BASED EXIT:
- Early F₀: 25-30% exit fee (protect early capital)
- Mid F₁-F₂: 15-20% (moderate friction)
- Mature F₃+: 5-10% (reduced friction)

STAKE-PROPORTIONAL DISCOUNT:
- High stake ratio (>80%): 50% fee reduction
- Medium stake (>50%): 25% reduction
- Low stake: No discount

VESTING BONUS (time-based):
- 1-2 years: 10% reduction
- 2-4 years: 25% reduction
- 4-8 years: 40% reduction
- 8+ years: 50% reduction

ACTIVITY MODIFIER:
- Active contributors get up to 30% fee reduction
- Based on CABR contributions, validations, referrals

EXIT FEE ALLOCATION:
- 80% → BTC Reserve reinforcement
- 20% → Treasury

Reference: WSP 26 Section 14, WSP 100, WSP 101
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

# Minimum exit fee floor (prevent gaming)
MIN_EXIT_FEE = 0.02  # 2% minimum


class FoundUpTier(IntEnum):
    """FoundUp maturity tiers per WSP 100."""
    F0_DAE = 0           # Early stage DAE
    F1_EARLY_DAO = 1     # Early SmartDAO
    F2_GROWTH = 2        # Growth SmartDAO
    F3_INFRA = 3         # Infrastructure SmartDAO
    F4_GOVERNANCE = 4    # Governance SmartDAO
    F5_SOVEREIGN = 5     # Sovereign SmartDAO


# Base exit fees by maturity tier
MATURITY_EXIT_FEES = {
    FoundUpTier.F0_DAE: 0.30,        # 30% - early stage
    FoundUpTier.F1_EARLY_DAO: 0.25,  # 25%
    FoundUpTier.F2_GROWTH: 0.20,     # 20%
    FoundUpTier.F3_INFRA: 0.15,      # 15%
    FoundUpTier.F4_GOVERNANCE: 0.10, # 10%
    FoundUpTier.F5_SOVEREIGN: 0.05,  # 5% - mature
}


@dataclass
class ActivityMetrics:
    """Activity metrics for fee calculation."""
    cabr_contributions_last_12_epochs: int = 0
    v3_validations_performed: int = 0
    referrals_activated: int = 0


@dataclass
class ExitFeeResult:
    """Result of exit fee calculation."""
    base_fee_rate: float
    stake_discount: float
    vesting_bonus: float
    activity_modifier: float
    final_fee_rate: float
    exit_amount: float
    fee_amount: float
    btc_reserve_portion: float  # 80% of fee
    treasury_portion: float     # 20% of fee


def calculate_stake_discount(stake_ratio: float) -> float:
    """
    Calculate stake-proportional fee discount.

    High stake ratio = aligned with ecosystem = lower fee.

    Args:
        stake_ratio: User's staked UPS / total UPS held (0.0 to 1.0)

    Returns:
        Discount percentage (0.0 to 0.5)
    """
    if stake_ratio >= 0.8:
        return 0.50  # 50% discount for highly staked users
    elif stake_ratio >= 0.5:
        return 0.25  # 25% discount for moderately staked
    else:
        return 0.0   # No discount for low stake ratio


def calculate_vesting_bonus(hold_duration_epochs: int) -> float:
    """
    Calculate vesting bonus based on hold duration.

    Long-term holders get exit fee reduction.

    Args:
        hold_duration_epochs: Number of epochs held

    Returns:
        Vesting bonus (0.0 to 0.5)
    """
    if hold_duration_epochs < 13:
        return 0.0   # Under 1 year - no bonus
    elif hold_duration_epochs < 25:
        return 0.10  # 1-2 years - 10% reduction
    elif hold_duration_epochs < 49:
        return 0.25  # 2-4 years - 25% reduction
    elif hold_duration_epochs < 97:
        return 0.40  # 4-8 years - 40% reduction
    else:
        return 0.50  # 8+ years - max 50% reduction


def calculate_activity_modifier(
    cabr_contributions_last_12_epochs: int = 0,
    v3_validations_performed: int = 0,
    referrals_activated: int = 0,
) -> float:
    """
    Calculate activity modifier based on ecosystem contribution.

    Active participants who have contributed work (not just staked)
    receive better exit terms as recognition of value created.

    Args:
        cabr_contributions_last_12_epochs: CABR-validated work in last year
        v3_validations_performed: V3 validations performed
        referrals_activated: Activated referrals

    Returns:
        Multiplier 0.7-1.0 (lower = better exit rate)
    """
    # Score components (each max 100 points)
    cabr_score = min(cabr_contributions_last_12_epochs, 50) * 2  # Max 100
    validation_score = min(v3_validations_performed, 100) * 1   # Max 100
    referral_score = min(referrals_activated, 25) * 4           # Max 100

    # Normalize to 0-1
    activity_score = (cabr_score + validation_score + referral_score) / 300

    # High activity = up to 30% fee reduction
    return 1.0 - (activity_score * 0.30)


def calculate_dynamic_exit_fee(
    foundup_tier: FoundUpTier,
    stake_ratio: float,
    hold_duration_epochs: int,
    activity_metrics: Optional[ActivityMetrics],
    token_amount: float,
) -> ExitFeeResult:
    """
    Calculate composite exit fee combining all factors.

    Final = Base × (1 - Stake Discount) × (1 - Vesting Bonus) × Activity Modifier

    Example:
    - F₂ FoundUp (base 20%)
    - 60% staked (25% discount → 15%)
    - Held 30 epochs (25% vesting → 11.25%)
    - High activity (0.8 modifier → 9%)

    Result: 9% exit fee (down from 20% base)

    Args:
        foundup_tier: FoundUp maturity tier (0-5)
        stake_ratio: User's staked UPS / total UPS held
        hold_duration_epochs: Epochs since first stake
        activity_metrics: Activity data for modifier
        token_amount: Amount being exited

    Returns:
        ExitFeeResult with all calculation details
    """
    # 1. Base maturity fee
    base_fee = MATURITY_EXIT_FEES.get(foundup_tier, 0.30)

    # 2. Apply stake discount
    stake_discount = calculate_stake_discount(stake_ratio)
    fee_after_stake = base_fee * (1 - stake_discount)

    # 3. Apply vesting bonus
    vesting_bonus = calculate_vesting_bonus(hold_duration_epochs)
    fee_after_vesting = fee_after_stake * (1 - vesting_bonus)

    # 4. Apply activity modifier
    if activity_metrics:
        activity_mod = calculate_activity_modifier(
            activity_metrics.cabr_contributions_last_12_epochs,
            activity_metrics.v3_validations_performed,
            activity_metrics.referrals_activated,
        )
    else:
        activity_mod = 1.0  # No modifier if no activity data

    final_fee_rate = fee_after_vesting * activity_mod

    # 5. Floor: minimum 2% exit fee (prevents gaming)
    final_fee_rate = max(final_fee_rate, MIN_EXIT_FEE)

    # 6. Calculate amounts
    fee_amount = token_amount * final_fee_rate
    btc_reserve_portion = fee_amount * 0.80  # 80% to reserve
    treasury_portion = fee_amount * 0.20     # 20% to treasury

    return ExitFeeResult(
        base_fee_rate=base_fee,
        stake_discount=stake_discount,
        vesting_bonus=vesting_bonus,
        activity_modifier=activity_mod,
        final_fee_rate=final_fee_rate,
        exit_amount=token_amount,
        fee_amount=fee_amount,
        btc_reserve_portion=btc_reserve_portion,
        treasury_portion=treasury_portion,
    )


# Singleton instance
_dynamic_exit_engine: Optional["DynamicExitEngine"] = None


class DynamicExitEngine:
    """
    Engine for calculating and processing dynamic exit fees.

    Tracks:
    - Exit history per participant
    - Aggregate exit statistics
    - BTC reserve contributions from exits
    """

    def __init__(self):
        self.total_exits_processed = 0
        self.total_fee_collected = 0.0
        self.total_btc_reserve_contribution = 0.0
        self.total_treasury_contribution = 0.0

    def process_exit(
        self,
        participant_id: str,
        foundup_id: str,
        foundup_tier: FoundUpTier,
        stake_ratio: float,
        hold_duration_epochs: int,
        activity_metrics: Optional[ActivityMetrics],
        token_amount: float,
    ) -> ExitFeeResult:
        """
        Process an exit and calculate the dynamic fee.

        Updates aggregate statistics and returns the fee calculation.
        """
        result = calculate_dynamic_exit_fee(
            foundup_tier=foundup_tier,
            stake_ratio=stake_ratio,
            hold_duration_epochs=hold_duration_epochs,
            activity_metrics=activity_metrics,
            token_amount=token_amount,
        )

        # Update statistics
        self.total_exits_processed += 1
        self.total_fee_collected += result.fee_amount
        self.total_btc_reserve_contribution += result.btc_reserve_portion
        self.total_treasury_contribution += result.treasury_portion

        return result


def get_dynamic_exit_engine() -> DynamicExitEngine:
    """Get or create singleton exit engine."""
    global _dynamic_exit_engine
    if _dynamic_exit_engine is None:
        _dynamic_exit_engine = DynamicExitEngine()
    return _dynamic_exit_engine


def reset_dynamic_exit_engine() -> None:
    """Reset singleton for testing."""
    global _dynamic_exit_engine
    _dynamic_exit_engine = None
