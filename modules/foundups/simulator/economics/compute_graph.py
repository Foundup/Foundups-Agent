"""Compute graph primitives for litepaper animation.

Purpose:
- Translate agent compute into human-work and BTC-sats equivalents.
- Keep CABR pipe-flow and UPS distribution math explicit and auditable.

CABR Model (2026-02-17):
- Treasury holds UPS (backed by BTC sats)
- CABR score = PIPE SIZE (controls flow rate to FoundUp)
- PoB validation = VALVE (opens when work verified)
- Workers receive UPS from what flows through their FoundUp's pipe

Formula:
  pipe_flow = treasury_epoch_release * cabr_pipe_size
  worker_ups = (contribution_weight / total_contribution) * pipe_flow
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .pool_distribution import COMPUTE_TIER_WEIGHTS


# Conservative baseline equivalents for 1.0 compute weight unit.
HUMAN_HOURS_PER_WEIGHT_UNIT = 0.4
SATS_PER_WEIGHT_UNIT = 50


@dataclass(frozen=True)
class ComputeEquivalent:
    """Computed equivalence for one workload slice."""

    model_tier: str
    tokens_used: int
    tier_weight: float
    compute_weight: float
    human_hours_equivalent: float
    sats_equivalent: float
    fi_earned: float

    @property
    def ups_routed(self) -> float:
        """Backward-compatible alias: fi_earned is UPS routed in pipe model."""
        return self.fi_earned


def calculate_compute_weight(tokens_used: int, model_tier: str) -> float:
    """Compute-weight formula aligned with pool_distribution.ComputeMetrics."""
    tier_weight = float(COMPUTE_TIER_WEIGHTS.get(model_tier, 1.0))
    token_factor = tokens_used / 1000.0 if tokens_used > 0 else 0.1
    return token_factor * tier_weight


def calculate_compute_equivalent(
    *,
    tokens_used: int,
    model_tier: str,
    cabr_pipe_size: float | None = None,  # CABR = pipe size (0.0-1.0), controls flow rate
    epoch_ups_available: float | None = None,  # UPS available in treasury this epoch
    total_contribution_weight: float | None = None,  # Sum of all worker weights for this task.
    # Legacy aliases (for existing callers/tests).
    cabr_v3_score: float | None = None,
    base_fi_rate: float | None = None,
) -> ComputeEquivalent:
    """Map workload into compute weight, human-hours, sats, and UPS flow.

    CABR Pipe Model:
    - cabr_pipe_size: How much of treasury flow reaches this FoundUp (0.0-1.0)
    - epoch_ups_available: Total UPS available for distribution this epoch
    - Worker receives: (their_weight / total_weight) * pipe_flow

    For single-worker calculation, total_contribution_weight=worker_weight
    so worker gets 100% of pipe_flow.
    """
    weight = calculate_compute_weight(tokens_used=tokens_used, model_tier=model_tier)
    tier_weight = float(COMPUTE_TIER_WEIGHTS.get(model_tier, 1.0))
    if cabr_pipe_size is None:
        cabr_pipe_size = 1.0 if cabr_v3_score is None else cabr_v3_score
    if epoch_ups_available is None:
        epoch_ups_available = 1.0 if base_fi_rate is None else base_fi_rate
    if total_contribution_weight is None:
        total_contribution_weight = weight
    total_contribution_weight = max(0.000001, total_contribution_weight)

    # Pipe flow: CABR controls how much UPS flows to this FoundUp
    pipe_flow = epoch_ups_available * max(0.0, min(1.0, cabr_pipe_size))
    # Worker receives proportional share of flow.
    share = max(0.0, min(1.0, weight / total_contribution_weight))
    ups_received = pipe_flow * share
    return ComputeEquivalent(
        model_tier=model_tier,
        tokens_used=tokens_used,
        tier_weight=tier_weight,
        compute_weight=weight,
        human_hours_equivalent=weight * HUMAN_HOURS_PER_WEIGHT_UNIT,
        sats_equivalent=weight * SATS_PER_WEIGHT_UNIT,
        fi_earned=ups_received,  # UPS received through CABR pipe
    )


def build_tier_equivalence_table(tokens_per_slice: int = 1000) -> List[Dict]:
    """Build a deterministic per-tier table for UI rendering."""
    rows: List[Dict] = []
    for tier, weight in COMPUTE_TIER_WEIGHTS.items():
        eq = calculate_compute_equivalent(
            tokens_used=tokens_per_slice,
            model_tier=tier,
            cabr_pipe_size=1.0,  # Full pipe (max flow)
            epoch_ups_available=1.0,  # 1 UPS available
        )
        rows.append(
            {
                "tier": tier,
                "tier_weight": weight,
                "tokens": tokens_per_slice,
                "compute_weight": round(eq.compute_weight, 4),
                "human_hours": round(eq.human_hours_equivalent, 4),
                "sats": round(eq.sats_equivalent, 2),
                "ups_at_full_pipe": round(eq.fi_earned, 6),  # UPS when CABR = 1.0
            }
        )
    rows.sort(key=lambda r: r["tier_weight"], reverse=True)
    return rows


def build_compute_graph_payload(
    *,
    model_tier: str = "opus",
    agents_assigned: int = 10,
    tokens_per_agent_epoch: int = 1000,
    cabr_pipe_size: float = 0.65,  # CABR = pipe size (flow rate)
    epoch_ups_available: float = 1000.0,  # UPS in treasury available this epoch
) -> Dict:
    """Build payload for litepaper compute graph section.

    CABR Pipe Model:
    - Treasury holds UPS (backed by BTC sats)
    - CABR score determines pipe size (0.0-1.0)
    - PoB validation opens the valve
    - Workers receive UPS proportional to contribution
    """
    per_agent = calculate_compute_equivalent(
        tokens_used=tokens_per_agent_epoch,
        model_tier=model_tier,
        cabr_pipe_size=cabr_pipe_size,
        epoch_ups_available=epoch_ups_available,
        total_contribution_weight=max(0.000001, agents_assigned * calculate_compute_weight(
            tokens_used=tokens_per_agent_epoch,
            model_tier=model_tier,
        )),
    )
    total_weight = per_agent.compute_weight * max(0, agents_assigned)
    total_hours = per_agent.human_hours_equivalent * max(0, agents_assigned)
    total_sats = per_agent.sats_equivalent * max(0, agents_assigned)
    total_ups = per_agent.fi_earned * max(0, agents_assigned)

    return {
        "formula": {
            "compute_weight": "(tokens_used / 1000) * tier_weight",
            "pipe_flow": "epoch_ups_available * cabr_pipe_size",
            "ups_received": "pipe_flow * (worker_weight / total_weight)",
        },
        "model": {
            "treasury": "UPS backed by BTC sats",
            "cabr": "Pipe size - controls flow rate to FoundUp",
            "pob": "Valve - opens when work validated (V3)",
        },
        "equivalence_baselines": {
            "human_hours_per_weight_unit": HUMAN_HOURS_PER_WEIGHT_UNIT,
            "sats_per_weight_unit": SATS_PER_WEIGHT_UNIT,
        },
        "tiers": build_tier_equivalence_table(tokens_per_slice=1000),
        "angel_seeding_example": {
            "agents_assigned": agents_assigned,
            "model_tier": model_tier,
            "tokens_per_agent_epoch": tokens_per_agent_epoch,
            "cabr_pipe_size": cabr_pipe_size,
            "epoch_ups_available": epoch_ups_available,
            "per_agent": {
                "compute_weight": round(per_agent.compute_weight, 4),
                "human_hours": round(per_agent.human_hours_equivalent, 4),
                "sats": round(per_agent.sats_equivalent, 2),
                "ups_received": round(per_agent.fi_earned, 6),
            },
            "total": {
                "compute_weight": round(total_weight, 4),
                "human_hours": round(total_hours, 4),
                "sats": round(total_sats, 2),
                "ups_received": round(total_ups, 6),
            },
        },
    }
