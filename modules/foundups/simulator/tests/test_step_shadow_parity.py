"""Tests for pure-step shadow parity telemetry."""

from __future__ import annotations

from modules.foundups.simulator.config import SimulatorConfig
from modules.foundups.simulator.mesa_model import FoundUpsModel


def test_shadow_parity_records_check_metrics() -> None:
    model = FoundUpsModel(
        config=SimulatorConfig(
            num_founder_agents=1,
            num_user_agents=1,
            use_ai=False,
            pure_step_shadow_enabled=True,
            pure_step_shadow_log_interval=1,
            pure_step_shadow_max_actor_drift=1_000_000.0,
            pure_step_shadow_max_pool_drift=1_000_000.0,
            pure_step_shadow_max_fi_drift=1_000_000.0,
        )
    )
    model.start()
    model.step()

    stats = model.get_stats()
    assert stats["pure_step_shadow_checks"] >= 1
    assert stats["pure_step_shadow_last_tick"] == model.tick
    assert stats["pure_step_shadow_last_ok"] is True


def test_shadow_parity_failure_counter_increments_on_drift(monkeypatch) -> None:
    model = FoundUpsModel(
        config=SimulatorConfig(
            num_founder_agents=1,
            num_user_agents=1,
            use_ai=False,
            pure_step_shadow_enabled=True,
        )
    )

    def _broken_step(current_state, *_args, **_kwargs):
        return current_state

    monkeypatch.setattr("modules.foundups.simulator.step_pipeline.step", _broken_step)

    model.start()
    model.step()

    stats = model.get_stats()
    assert stats["pure_step_shadow_checks"] >= 1
    assert stats["pure_step_shadow_failures"] >= 1
    assert stats["pure_step_shadow_last_ok"] is False
