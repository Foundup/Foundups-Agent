"""Pure actor behavior transitions for `SimState`."""

from __future__ import annotations

from dataclasses import replace

from ..state_contracts import ActorState


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def compute_coherence(
    current: float,
    *,
    activity_signal: float,
    earnings_signal: float,
    loyalty_signal: float,
) -> float:
    """Compute next coherence score.

    Weighted toward activity first; matches current roadmap intent.
    """
    next_value = (
        current * 0.65
        + activity_signal * 0.20
        + earnings_signal * 0.10
        + loyalty_signal * 0.05
    )
    return _clamp(next_value, 0.0, 1.0)


def compute_rank(tokens: float, current_rank: int) -> int:
    """Map token accumulation to rank band (1-7)."""
    thresholds = (
        (20000, 7),
        (10000, 6),
        (5000, 5),
        (2000, 4),
        (500, 3),
        (100, 2),
    )
    for threshold, rank in thresholds:
        if tokens >= threshold:
            return max(current_rank, rank)
    return current_rank


def advance_actor(
    actor: ActorState,
    *,
    delta_tokens: float = 0.0,
    delta_ups: float = 0.0,
    activity_signal: float = 0.0,
    earnings_signal: float = 0.0,
    loyalty_signal: float = 0.0,
) -> ActorState:
    """Return new `ActorState` after deterministic updates."""
    next_tokens = max(0.0, actor.tokens + delta_tokens)
    next_ups = max(0.0, actor.ups_balance + delta_ups)
    next_coherence = compute_coherence(
        actor.coherence,
        activity_signal=activity_signal,
        earnings_signal=earnings_signal,
        loyalty_signal=loyalty_signal,
    )
    next_rank = compute_rank(next_tokens, actor.rank)
    return replace(
        actor,
        tokens=next_tokens,
        ups_balance=next_ups,
        coherence=next_coherence,
        rank=next_rank,
    )
