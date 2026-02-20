"""Tests for immutable state contracts bridge."""

from __future__ import annotations

import pytest

from modules.foundups.simulator.state_contracts import (
    FrozenDict,
    STAGE_TO_INT,
    build_sim_state,
)
from modules.foundups.simulator.state_store import AgentState, FoundUpTile, SimulatorState


def _runtime_state() -> SimulatorState:
    state = SimulatorState()
    state.tick = 12
    state.total_stakes = 1000
    state.agents["agent_001"] = AgentState(
        agent_id="agent_001",
        agent_type="founder",
        tokens=250,
    )
    state.foundups["fup_001"] = FoundUpTile(
        foundup_id="fup_001",
        name="Alpha",
        token_symbol="ALPH",
        owner_id="agent_001",
        lifecycle_stage="Proto",
        tokens_released=111,
    )
    return state


def test_build_sim_state_maps_runtime_values() -> None:
    sim_state = build_sim_state(
        _runtime_state(),
        stats={"btc_reserve_total": 2.5, "fi_outstanding": 999, "network_pool_ups": 4, "fund_pool_ups": 1},
        coherence_by_actor={"agent_001": 0.71},
        rank_by_actor={"agent_001": 3},
    )

    assert sim_state.tick == 12
    assert sim_state.actors["agent_001"].coherence == 0.71
    assert sim_state.actors["agent_001"].rank == 3
    assert sim_state.foundups["fup_001"].stage == STAGE_TO_INT["Proto"]
    assert sim_state.pools.un_pool == pytest.approx(600.0)
    assert sim_state.btc_reserve_total == 2.5
    assert sim_state.fi_released_total == 999


def test_frozen_dict_is_immutable_mapping() -> None:
    frozen = FrozenDict({"a": 1})
    assert frozen["a"] == 1
    with pytest.raises(TypeError):
        frozen["b"] = 2  # type: ignore[index]
