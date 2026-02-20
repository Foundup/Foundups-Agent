"""Unit tests for pure step decision core."""

from __future__ import annotations

from modules.foundups.simulator.step_core import StepPolicy, StepState, compute_step_decision


def _policy() -> StepPolicy:
    return StepPolicy(
        subscription_month_reset_interval=300,
        subscription_refresh_interval=30,
        demurrage_interval=10,
        rating_update_interval=10,
        ratio_snapshot_interval=50,
    )


def test_compute_step_decision_boot_tick_no_start_time() -> None:
    decision = compute_step_decision(
        StepState(tick=0, start_time=None),
        _policy(),
        now=1234.56,
    )
    assert decision.next_tick == 1
    assert decision.elapsed_seconds == 0.0
    assert not decision.should_apply_demurrage
    assert not decision.should_emit_rating_updates


def test_compute_step_decision_periodic_flags_tick_50() -> None:
    decision = compute_step_decision(
        StepState(tick=49, start_time=100.0),
        _policy(),
        now=160.0,
    )
    assert decision.next_tick == 50
    assert decision.elapsed_seconds == 60.0
    assert decision.should_apply_demurrage
    assert decision.should_emit_rating_updates
    assert decision.should_record_ratio_snapshot
    assert not decision.should_refresh_subscription_allocations
    assert not decision.should_reset_subscription_cycles


def test_compute_step_decision_tick_300_all_relevant_flags() -> None:
    decision = compute_step_decision(
        StepState(tick=299, start_time=0.0),
        _policy(),
        now=301.0,
    )
    assert decision.next_tick == 300
    assert decision.should_reset_subscription_cycles
    assert decision.should_refresh_subscription_allocations
    assert decision.should_apply_demurrage
    assert decision.should_emit_rating_updates
    assert decision.should_record_ratio_snapshot
