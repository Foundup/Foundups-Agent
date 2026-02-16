"""Parameter registry tests."""

from __future__ import annotations

from modules.foundups.simulator.parameter_registry import load_bundle, to_simulator_config


def test_load_baseline_bundle() -> None:
    bundle = load_bundle("baseline")
    assert bundle.version == "1.0.0"
    assert bundle.scenario == "baseline"
    assert bundle.params["num_user_agents"] >= 0


def test_convert_to_simulator_config() -> None:
    bundle = load_bundle("high_adoption")
    config = to_simulator_config(bundle)
    assert config.num_founder_agents == bundle.params["num_founder_agents"]
    assert config.tick_rate_hz == bundle.params["tick_rate_hz"]
