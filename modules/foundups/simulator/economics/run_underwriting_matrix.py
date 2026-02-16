"""CLI runner for investor underwriting matrix."""

from __future__ import annotations

import argparse

from .underwriting_scenarios import (
    ContractTerms,
    FoundupLane,
    PoolMember,
    default_scenarios,
    run_underwriting_matrix,
    simulate_underwriting,
    stake_weight,
)


def _format_row(name: str, outcome) -> str:
    hurdle = str(outcome.hurdle_year) if outcome.hurdle_year is not None else "-"
    return (
        f"{name:<14} "
        f"{outcome.projected_multiple_3y:>8.2f}x "
        f"{outcome.projected_multiple_10y:>9.2f}x "
        f"{outcome.effective_multiple_3y:>9.2f}x "
        f"{hurdle:>7} "
        f"{outcome.year3_coverage_ratio:>8.2f} "
        f"{outcome.year3_funding_gap_btc:>8.2f}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run FoundUps investor underwriting matrix")
    parser.add_argument("--principal-btc", type=float, default=10.0, help="Investor principal BTC")
    parser.add_argument("--total-invested-btc", type=float, default=755.0, help="Total network invested BTC")
    parser.add_argument("--repayment-multiple", type=float, default=10.0, help="Repayment target multiple")
    parser.add_argument(
        "--pool-weighted",
        action="store_true",
        help="Use pooled lane allocation (seed + foundup-specific membership) instead of straight investor_weight",
    )
    args = parser.parse_args()

    terms = ContractTerms(repayment_multiple=args.repayment_multiple)
    if args.pool_weighted:
        weight = stake_weight(args.principal_btc, args.total_invested_btc)
        matrix = {}
        for scenario in default_scenarios(investor_weight=weight):
            pooled = scenario.__class__(
                **{
                    **scenario.__dict__,
                    "focal_investor_id": "ticket_investor",
                    "pool_members": [
                        PoolMember(investor_id="seed_pool", member_weight=1.0, membership="seed"),
                        PoolMember(
                            investor_id="ticket_investor",
                            member_weight=max(1e-9, weight),
                            membership="foundup",
                            target_foundup_id="target_foundup",
                        ),
                    ],
                    "foundup_lanes": [
                        FoundupLane(
                            foundup_id="target_foundup",
                            network_distribution_share=0.35,
                            adoption_cap=scenario.adoption_cap,
                            adoption_steepness=scenario.adoption_steepness,
                        ),
                        FoundupLane(
                            foundup_id="rest_of_network",
                            network_distribution_share=0.65,
                            adoption_cap=max(0.0, min(1.0, scenario.adoption_cap * 0.95)),
                            adoption_steepness=scenario.adoption_steepness,
                        ),
                    ],
                }
            )
            matrix[scenario.name] = simulate_underwriting(
                principal_btc=args.principal_btc,
                scenario=pooled,
                terms=terms,
            )
    else:
        matrix = run_underwriting_matrix(
            principal_btc=args.principal_btc,
            total_invested_btc=args.total_invested_btc,
            terms=terms,
        )

    print("FoundUps Underwriting Matrix")
    print(
        "Scenario          3Y-Proj     10Y-Proj   3Y-Effective  Hurdle  Coverage     GapBTC"
    )
    print("-" * 84)
    for name, outcome in matrix.items():
        print(_format_row(name, outcome))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
