"""Pure step-decision core for simulator orchestration.

This module contains deterministic tick math only; no I/O and no model
mutation. It is the bridge toward the long-term pure transition contract:

    next_state = step(current_state, params, rng, events)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StepState:
    """Input state required for one scheduling decision."""

    tick: int
    start_time: float | None


@dataclass(frozen=True)
class StepPolicy:
    """Periodic action policy for the scheduler."""

    subscription_month_reset_interval: int
    subscription_refresh_interval: int
    demurrage_interval: int
    rating_update_interval: int
    ratio_snapshot_interval: int = 50


@dataclass(frozen=True)
class StepDecision:
    """Deterministic result of one scheduling step."""

    next_tick: int
    elapsed_seconds: float
    should_reset_subscription_cycles: bool
    should_refresh_subscription_allocations: bool
    should_apply_demurrage: bool
    should_record_ratio_snapshot: bool
    should_emit_rating_updates: bool


def compute_step_decision(state: StepState, policy: StepPolicy, now: float) -> StepDecision:
    """Compute next tick and all periodic action flags.

    Args:
        state: current tick/start-time values.
        policy: interval policy.
        now: monotonic/current wall time passed in by caller.
    """
    next_tick = state.tick + 1
    elapsed = 0.0 if state.start_time is None else max(0.0, now - state.start_time)

    return StepDecision(
        next_tick=next_tick,
        elapsed_seconds=elapsed,
        should_reset_subscription_cycles=(next_tick % policy.subscription_month_reset_interval == 0),
        should_refresh_subscription_allocations=(
            next_tick % policy.subscription_refresh_interval == 0
        ),
        should_apply_demurrage=(next_tick % policy.demurrage_interval == 0),
        should_record_ratio_snapshot=(next_tick % policy.ratio_snapshot_interval == 0),
        should_emit_rating_updates=(next_tick % policy.rating_update_interval == 0),
    )
