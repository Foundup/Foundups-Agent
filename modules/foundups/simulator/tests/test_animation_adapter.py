"""Animation adapter contract tests."""

from __future__ import annotations

from modules.foundups.simulator.animation_adapter import to_frame_dict
from modules.foundups.simulator.config import SimulatorConfig
from modules.foundups.simulator.mesa_model import FoundUpsModel


def test_frame_adapter_outputs_versioned_contract() -> None:
    model = FoundUpsModel(
        SimulatorConfig(
            num_founder_agents=0,
            num_user_agents=1,
            max_ticks=2,
            seed=123,
            agent_action_probability=0.0,
            agent_cooldown_ticks=0,
        )
    )
    model.step()
    frame = to_frame_dict(model.state_store.get_state(), model.get_stats())
    assert frame["frame_schema_version"] == "1.0.0"
    assert "foundups" in frame
    assert "actors" in frame
    assert "metrics" in frame
