"""Investor liability and buyout coverage modeling for simulator underwriting.

This module adds cash-flow discipline on top of token return projections:
- Buyout liability at year-3 choice points
- Escrow release schedules
- Coverage ratio and covenant checks
- Return multiple annualization helpers
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple


@dataclass(frozen=True)
class InvestorCohort:
    """Investor principal grouped by cohort/vintage."""

    cohort_id: str
    principal_btc: float
    start_year: int


@dataclass(frozen=True)
class BuyoutPolicy:
    """Policy assumptions for year-3 optional buyout."""

    buyout_multiple: float = 10.0
    exercise_rate: float = 0.4
    buyout_horizon_years: int = 3


@dataclass(frozen=True)
class EscrowSchedule:
    """Escrow release percentages by years since cohort start.

    Example default:
    - year 1: 20%
    - year 2: 20%
    - year 3+: 100%
    """

    cumulative_release_by_elapsed_year: Dict[int, float] = field(
        default_factory=lambda: {0: 0.0, 1: 0.2, 2: 0.4, 3: 1.0}
    )

    def cumulative_release(self, elapsed_years: int) -> float:
        if elapsed_years < 0:
            return 0.0
        keys = sorted(self.cumulative_release_by_elapsed_year.keys())
        release = 0.0
        for year in keys:
            if elapsed_years >= year:
                release = self.cumulative_release_by_elapsed_year[year]
            else:
                break
        return max(0.0, min(1.0, release))


@dataclass(frozen=True)
class LiabilitySnapshot:
    """Computed buyout and escrow state for a cohort at a specific year."""

    cohort_id: str
    year: int
    principal_btc: float
    exercised_principal_btc: float
    buyout_liability_btc: float
    escrow_released_btc: float
    escrow_unreleased_btc: float


@dataclass(frozen=True)
class FundingSources:
    """Cash sources available to meet buyout liabilities."""

    escrow_releasable_btc: float = 0.0
    protocol_fees_btc: float = 0.0
    refinancing_btc: float = 0.0
    reserve_buffer_btc: float = 0.0

    @property
    def total_btc(self) -> float:
        return (
            self.escrow_releasable_btc
            + self.protocol_fees_btc
            + self.refinancing_btc
            + self.reserve_buffer_btc
        )


@dataclass(frozen=True)
class CoverageCovenants:
    """Coverage thresholds used in underwriting."""

    p50_min: float = 1.25
    p90_min: float = 1.0


@dataclass(frozen=True)
class CoverageResult:
    """Coverage metrics and covenant outcomes."""

    liability_btc: float
    funding_btc: float
    coverage_ratio: float
    funding_gap_btc: float
    pass_p50: bool
    pass_p90: bool


class InvestorLiabilityEngine:
    """Compute cohort and aggregate buyout liabilities."""

    @staticmethod
    def annualized_return(multiple: float, years: float) -> float:
        """Return annualized rate from return multiple and holding period."""
        if multiple <= 0.0:
            raise ValueError("multiple must be > 0")
        if years <= 0.0:
            raise ValueError("years must be > 0")
        return multiple ** (1.0 / years) - 1.0

    @staticmethod
    def conservative_targets() -> Dict[str, float]:
        """Conservative underwriting targets for investor planning."""
        return {
            "target_3y_multiple": 2.5,
            "target_10y_multiple": 10.0,
        }

    @staticmethod
    def buyout_liability(
        principal_btc: float,
        policy: BuyoutPolicy,
    ) -> Tuple[float, float]:
        """Return (buyout liability btc, exercised principal btc)."""
        if principal_btc < 0:
            raise ValueError("principal_btc cannot be negative")
        if policy.buyout_multiple <= 0:
            raise ValueError("buyout_multiple must be > 0")
        if not (0.0 <= policy.exercise_rate <= 1.0):
            raise ValueError("exercise_rate must be between 0 and 1")
        exercised_principal = principal_btc * policy.exercise_rate
        return exercised_principal * policy.buyout_multiple, exercised_principal

    @staticmethod
    def cohort_snapshot(
        cohort: InvestorCohort,
        year: int,
        policy: BuyoutPolicy,
        schedule: EscrowSchedule,
    ) -> LiabilitySnapshot:
        """Build liability snapshot for one cohort in a given calendar year."""
        elapsed = year - cohort.start_year
        release_pct = schedule.cumulative_release(elapsed)
        escrow_released = cohort.principal_btc * release_pct
        liability, exercised_principal = InvestorLiabilityEngine.buyout_liability(
            cohort.principal_btc, policy
        )
        return LiabilitySnapshot(
            cohort_id=cohort.cohort_id,
            year=year,
            principal_btc=cohort.principal_btc,
            exercised_principal_btc=exercised_principal,
            buyout_liability_btc=liability,
            escrow_released_btc=escrow_released,
            escrow_unreleased_btc=max(0.0, cohort.principal_btc - escrow_released),
        )

    @staticmethod
    def aggregate_snapshots(
        cohorts: Iterable[InvestorCohort],
        year: int,
        policy: BuyoutPolicy,
        schedule: EscrowSchedule,
    ) -> Tuple[List[LiabilitySnapshot], float, float]:
        """Return snapshots plus aggregate liability and released escrow."""
        snapshots: List[LiabilitySnapshot] = [
            InvestorLiabilityEngine.cohort_snapshot(c, year, policy, schedule)
            for c in cohorts
        ]
        total_liability = sum(s.buyout_liability_btc for s in snapshots)
        total_escrow_released = sum(s.escrow_released_btc for s in snapshots)
        return snapshots, total_liability, total_escrow_released


class BuyoutCoverageEngine:
    """Evaluate if funding sources can sustain buyout liabilities."""

    @staticmethod
    def evaluate_coverage(
        liability_btc: float,
        funding: FundingSources,
        covenants: CoverageCovenants | None = None,
    ) -> CoverageResult:
        if liability_btc < 0:
            raise ValueError("liability_btc cannot be negative")
        cov = covenants or CoverageCovenants()
        funding_total = max(0.0, funding.total_btc)
        if liability_btc == 0:
            ratio = float("inf")
            gap = 0.0
        else:
            ratio = funding_total / liability_btc
            gap = max(0.0, liability_btc - funding_total)

        return CoverageResult(
            liability_btc=liability_btc,
            funding_btc=funding_total,
            coverage_ratio=ratio,
            funding_gap_btc=gap,
            pass_p50=ratio >= cov.p50_min,
            pass_p90=ratio >= cov.p90_min,
        )

    @staticmethod
    def required_total_funding(
        liability_btc: float,
        target_ratio: float,
    ) -> float:
        if liability_btc < 0:
            raise ValueError("liability_btc cannot be negative")
        if target_ratio < 0:
            raise ValueError("target_ratio cannot be negative")
        return liability_btc * target_ratio
