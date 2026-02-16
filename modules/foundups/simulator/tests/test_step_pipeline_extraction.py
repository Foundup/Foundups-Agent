"""Tests for step pipeline extraction seam."""

from __future__ import annotations

from modules.foundups.simulator.config import SimulatorConfig
from modules.foundups.simulator.mesa_model import FoundUpsModel


def test_model_step_delegates_to_pipeline(monkeypatch) -> None:
    model = FoundUpsModel(
        config=SimulatorConfig(
            num_founder_agents=1,
            num_user_agents=1,
            use_ai=False,
        )
    )
    called = {"count": 0}

    def _fake_run_step(instance):
        called["count"] += 1
        assert instance is model

    monkeypatch.setattr("modules.foundups.simulator.mesa_model.run_step", _fake_run_step)
    model.step()

    assert called["count"] == 1
