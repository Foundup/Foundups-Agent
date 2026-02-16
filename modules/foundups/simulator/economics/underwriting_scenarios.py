"""Underwriting scenario engine for FoundUps investor contract stress tests.

Purpose:
- Project 3-year and 10-year investor outcomes under S-curve adoption.
- Enforce dynamic contract rates: 12.16% pre-hurdle, 0.64% post-hurdle.
- Surface year-3 buyout floor (10x) and coverage covenant status.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from .investor_liability import (
    BuyoutCoverageEngine,
    CoverageCovenants,
    FundingSources,
)
from .token_economics import adoption_curve


@dataclass(frozen=True)
class ContractTerms:
    """Investor contract terms used in underwriting."""

    pre_hurdle_pool_rate: float = 0.1216
    post_hurdle_pool_rate: float = 0.0064
    repayment_multiple: float = 10.0
    buyout_floor_enabled: bool = True


@dataclass(frozen=True)
class ScenarioConfig:
    """Scenario assumptions for network distributions and adoption."""

    name: str
    horizon_years: int = 10
    base_network_distribution_btc: float = 250.0
    distribution_cagr: float = 0.30
    adoption_cap: float = 0.80
    adoption_steepness: float = 10.0
    investor_weight: float = 0.01
    buyout_exercise_rate: float = 0.40
    escrow_release_year3: float = 0.40
    protocol_fees_year3_btc: float = 0.0
    refinancing_year3_btc: float = 0.0
    reserve_buffer_year3_btc: float = 0.0
    # Optional pooled allocation mode.
    focal_investor_id: str = "seed_investor"
    pool_members: List["PoolMember"] = field(default_factory=list)
    foundup_lanes: List["FoundupLane"] = field(default_factory=list)


@dataclass(frozen=True)
class PoolMember:
    """Member of investor payout pool.

    membership:
    - "seed": participates in every FoundUp lane
    - "foundup": participates only in its target FoundUp lane
    """

    investor_id: str
    member_weight: float
    membership: str = "seed"
    target_foundup_id: str | None = None


@dataclass(frozen=True)
class FoundupLane:
    """Adoption-weighted lane for a specific FoundUp segment."""

    foundup_id: str
    network_distribution_share: float
    adoption_cap: float = 0.80
    adoption_steepness: float = 10.0


@dataclass(frozen=True)
class YearProjection:
    """Yearly projection row."""

    year: int
    adoption_factor: float
    network_distribution_btc: float
    pool_rate: float
    investor_distribution_btc: float
    cumulative_distribution_btc: float
    cumulative_multiple: float
    lane_allocations: Dict[str, float] | None = None


@dataclass(frozen=True)
class UnderwritingOutcome:
    """Scenario underwriting result."""

    scenario: str
    principal_btc: float
    investor_weight: float
    target_multiple: float
    projected_multiple_3y: float
    projected_multiple_10y: float
    effective_multiple_3y: float
    hurdle_year: int | None
    year3_buyout_liability_btc: float
    year3_funding_btc: float
    year3_coverage_ratio: float
    year3_pass_p50: bool
    year3_pass_p90: bool
    year3_funding_gap_btc: float
    yearly: List[YearProjection]


def stake_weight(principal_btc: float, total_invested_btc: float) -> float:
    """Calculate investor pool weight from principal over total invested."""
    if principal_btc <= 0:
        raise ValueError("principal_btc must be > 0")
    if total_invested_btc <= 0:
        raise ValueError("total_invested_btc must be > 0")
    return principal_btc / total_invested_btc


def _value_at_year(yearly: Sequence[YearProjection], year: int) -> YearProjection:
    for row in yearly:
        if row.year == year:
            return row
    return yearly[-1]


def _normalize_lane_shares(lanes: Sequence[FoundupLane]) -> List[FoundupLane]:
    total = sum(max(0.0, lane.network_distribution_share) for lane in lanes)
    if total <= 0:
        raise ValueError("foundup lane shares must sum to > 0")
    return [
        FoundupLane(
            foundup_id=lane.foundup_id,
            network_distribution_share=max(0.0, lane.network_distribution_share) / total,
            adoption_cap=lane.adoption_cap,
            adoption_steepness=lane.adoption_steepness,
        )
        for lane in lanes
    ]


def _pool_weighted_distribution(
    *,
    network_distribution: float,
    pool_rate: float,
    year: int,
    horizon_years: int,
    focal_investor_id: str,
    pool_members: Sequence[PoolMember],
    foundup_lanes: Sequence[FoundupLane],
) -> tuple[float, float, Dict[str, float]]:
    """Compute investor distribution from pooled lane mechanics.

    Returns:
      (effective_adoption_factor, investor_distribution_btc, lane_allocations)
    """
    if not pool_members:
        raise ValueError("pool_members is required for pooled allocation mode")
    if not foundup_lanes:
        raise ValueError("foundup_lanes is required for pooled allocation mode")

    normalized_lanes = _normalize_lane_shares(foundup_lanes)
    normalized_progress = min(1.0, max(0.0, year / horizon_years))

    lane_allocations: Dict[str, float] = {}
    weighted_adoption = 0.0
    investor_total = 0.0

    for lane in normalized_lanes:
        lane_adoption = lane.adoption_cap * adoption_curve(
            normalized_progress,
            steepness=lane.adoption_steepness,
        )
        weighted_adoption += lane.network_distribution_share * lane_adoption

        lane_distribution = (
            network_distribution * lane.network_distribution_share * lane_adoption * pool_rate
        )

        eligible_members = [
            member
            for member in pool_members
            if (
                member.membership == "seed"
                or (member.membership == "foundup" and member.target_foundup_id == lane.foundup_id)
            )
            and member.member_weight > 0
        ]
        weight_total = sum(member.member_weight for member in eligible_members)
        focal_weight = sum(
            member.member_weight
            for member in eligible_members
            if member.investor_id == focal_investor_id
        )
        if weight_total <= 0 or focal_weight <= 0:
            lane_allocations[lane.foundup_id] = 0.0
            continue

        lane_investor_dist = lane_distribution * (focal_weight / weight_total)
        lane_allocations[lane.foundup_id] = lane_investor_dist
        investor_total += lane_investor_dist

    return weighted_adoption, investor_total, lane_allocations


def simulate_underwriting(
    principal_btc: float,
    scenario: ScenarioConfig,
    terms: ContractTerms | None = None,
    covenants: CoverageCovenants | None = None,
) -> UnderwritingOutcome:
    """Run one scenario projection for a single investor principal."""
    if principal_btc <= 0:
        raise ValueError("principal_btc must be > 0")
    if scenario.horizon_years <= 0:
        raise ValueError("scenario.horizon_years must be > 0")
    if not (0.0 <= scenario.adoption_cap <= 1.0):
        raise ValueError("scenario.adoption_cap must be between 0 and 1")
    if not (0.0 <= scenario.investor_weight <= 1.0):
        raise ValueError("scenario.investor_weight must be between 0 and 1")

    contract = terms or ContractTerms()
    target_btc = principal_btc * contract.repayment_multiple
    cumulative = 0.0
    hurdle_year: int | None = None
    yearly: List[YearProjection] = []

    for year in range(1, scenario.horizon_years + 1):
        normalized_progress = min(1.0, max(0.0, year / scenario.horizon_years))
        network_distribution = scenario.base_network_distribution_btc * (
            (1.0 + scenario.distribution_cagr) ** (year - 1)
        )

        pool_rate = (
            contract.pre_hurdle_pool_rate
            if cumulative < target_btc
            else contract.post_hurdle_pool_rate
        )

        if scenario.pool_members and scenario.foundup_lanes:
            adoption_factor, investor_distribution, lane_allocations = _pool_weighted_distribution(
                network_distribution=network_distribution,
                pool_rate=pool_rate,
                year=year,
                horizon_years=scenario.horizon_years,
                focal_investor_id=scenario.focal_investor_id,
                pool_members=scenario.pool_members,
                foundup_lanes=scenario.foundup_lanes,
            )
        else:
            adoption_factor = scenario.adoption_cap * adoption_curve(
                normalized_progress,
                steepness=scenario.adoption_steepness,
            )
            investor_distribution = (
                network_distribution * adoption_factor * pool_rate * scenario.investor_weight
            )
            lane_allocations = None
        cumulative += investor_distribution

        if hurdle_year is None and cumulative >= target_btc:
            hurdle_year = year

        yearly.append(
            YearProjection(
                year=year,
                adoption_factor=adoption_factor,
                network_distribution_btc=network_distribution,
                pool_rate=pool_rate,
                investor_distribution_btc=investor_distribution,
                cumulative_distribution_btc=cumulative,
                cumulative_multiple=cumulative / principal_btc,
                lane_allocations=lane_allocations,
            )
        )

    y3 = _value_at_year(yearly, 3)
    y10 = _value_at_year(yearly, 10)
    projected_3y = y3.cumulative_multiple
    projected_10y = y10.cumulative_multiple
    effective_3y = (
        max(projected_3y, contract.repayment_multiple)
        if contract.buyout_floor_enabled
        else projected_3y
    )

    year3_liability = (
        principal_btc * contract.repayment_multiple * scenario.buyout_exercise_rate
    )
    year3_funding = FundingSources(
        escrow_releasable_btc=principal_btc * scenario.escrow_release_year3,
        protocol_fees_btc=scenario.protocol_fees_year3_btc,
        refinancing_btc=scenario.refinancing_year3_btc,
        reserve_buffer_btc=scenario.reserve_buffer_year3_btc,
    )
    coverage = BuyoutCoverageEngine.evaluate_coverage(
        liability_btc=year3_liability,
        funding=year3_funding,
        covenants=covenants,
    )

    return UnderwritingOutcome(
        scenario=scenario.name,
        principal_btc=principal_btc,
        investor_weight=scenario.investor_weight,
        target_multiple=contract.repayment_multiple,
        projected_multiple_3y=projected_3y,
        projected_multiple_10y=projected_10y,
        effective_multiple_3y=effective_3y,
        hurdle_year=hurdle_year,
        year3_buyout_liability_btc=year3_liability,
        year3_funding_btc=coverage.funding_btc,
        year3_coverage_ratio=coverage.coverage_ratio,
        year3_pass_p50=coverage.pass_p50,
        year3_pass_p90=coverage.pass_p90,
        year3_funding_gap_btc=coverage.funding_gap_btc,
        yearly=yearly,
    )


def default_scenarios(
    investor_weight: float,
) -> List[ScenarioConfig]:
    """Conservative/base/scale scenarios with investor-aligned assumptions."""
    return [
        ScenarioConfig(
            name="conservative",
            base_network_distribution_btc=120.0,
            distribution_cagr=0.18,
            adoption_cap=0.65,
            investor_weight=investor_weight,
            protocol_fees_year3_btc=80.0,
            refinancing_year3_btc=120.0,
            reserve_buffer_year3_btc=40.0,
        ),
        ScenarioConfig(
            name="base",
            base_network_distribution_btc=240.0,
            distribution_cagr=0.30,
            adoption_cap=0.80,
            investor_weight=investor_weight,
            protocol_fees_year3_btc=160.0,
            refinancing_year3_btc=220.0,
            reserve_buffer_year3_btc=60.0,
        ),
        ScenarioConfig(
            name="scale",
            base_network_distribution_btc=420.0,
            distribution_cagr=0.42,
            adoption_cap=0.90,
            investor_weight=investor_weight,
            protocol_fees_year3_btc=280.0,
            refinancing_year3_btc=320.0,
            reserve_buffer_year3_btc=90.0,
        ),
    ]


def run_underwriting_matrix(
    principal_btc: float,
    total_invested_btc: float,
    terms: ContractTerms | None = None,
) -> Dict[str, UnderwritingOutcome]:
    """Run default scenario matrix for one investor ticket."""
    weight = stake_weight(principal_btc, total_invested_btc)
    scenarios = default_scenarios(investor_weight=weight)
    return {
        scenario.name: simulate_underwriting(principal_btc, scenario, terms)
        for scenario in scenarios
    }
