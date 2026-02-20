#!/usr/bin/env python
"""Run downside/base/upside sustainability matrix with confidence bands."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from .scenario_runner import _run_once


SCENARIO_MAP = {
    "downside": "stress_market",
    "base": "baseline",
    "upside": "high_adoption",
}

SCENARIO_RATIO_KEY = {
    "downside": "fee_scenario_downside_ratio_p10",
    "base": "fee_scenario_base_ratio_p50",
    "upside": "fee_scenario_upside_ratio_p90",
}


@dataclass(frozen=True)
class ScenarioBand:
    """Confidence band output for a scenario lane."""

    lane: str
    scenario: str
    runs: int
    ratio_key: str
    ratio_p10: float
    ratio_p50: float
    ratio_p90: float
    claim_pass_rate: float


def _quantile(values: List[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    idx = (len(ordered) - 1) * max(0.0, min(1.0, q))
    lo = int(idx)
    hi = min(lo + 1, len(ordered) - 1)
    frac = idx - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def run_matrix(
    *,
    ticks: int,
    frame_every: int,
    runs: int,
    base_seed: int,
    out_dir: Path,
) -> Dict[str, Dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    results: Dict[str, Dict] = {}

    for lane, scenario in SCENARIO_MAP.items():
        ratio_key = SCENARIO_RATIO_KEY[lane]
        ratios: List[float] = []
        claim_pass = 0

        for run_idx in range(runs):
            seed = base_seed + run_idx
            run_label = f"{lane}_mc_{run_idx:03d}"
            metrics = _run_once(
                scenario=scenario,
                ticks=ticks,
                frame_every=frame_every,
                out_dir=out_dir,
                run_label=run_label,
                seed_override=seed,
            )
            ratios.append(float(metrics.get(ratio_key, 0.0)))
            if metrics.get("fee_self_sustaining_claim", False):
                claim_pass += 1

        band = ScenarioBand(
            lane=lane,
            scenario=scenario,
            runs=runs,
            ratio_key=ratio_key,
            ratio_p10=_quantile(ratios, 0.10),
            ratio_p50=_quantile(ratios, 0.50),
            ratio_p90=_quantile(ratios, 0.90),
            claim_pass_rate=(claim_pass / runs) if runs > 0 else 0.0,
        )
        results[lane] = band.__dict__

    results["gate"] = {
        "rule": "self_sustaining claim requires downside p10 ratio >= 1.0",
        "downside_pass": results["downside"]["ratio_p10"] >= 1.0,
    }
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run downside/base/upside sustainability matrix with confidence bands."
    )
    parser.add_argument("--ticks", type=int, default=1500, help="Ticks per simulation run")
    parser.add_argument("--frame-every", type=int, default=30, help="Frame capture interval")
    parser.add_argument("--runs", type=int, default=9, help="Monte Carlo runs per scenario lane")
    parser.add_argument("--seed", type=int, default=42, help="Base seed for Monte Carlo")
    parser.add_argument(
        "--out",
        default="modules/foundups/simulator/memory/sustainability_matrix",
        help="Output folder",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out)
    matrix = run_matrix(
        ticks=args.ticks,
        frame_every=max(1, args.frame_every),
        runs=max(1, args.runs),
        base_seed=args.seed,
        out_dir=out_dir,
    )
    out_file = out_dir / "sustainability_matrix.json"
    out_file.write_text(json.dumps(matrix, indent=2), encoding="utf-8")
    print(json.dumps(matrix, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

