"""Tests for pure immutable step() transitions."""

from __future__ import annotations

import pytest

from modules.foundups.simulator.state_contracts import (
    ActorState,
    FoundUpState,
    FrozenDict,
    PoolState,
    SimState,
)
from modules.foundups.simulator.step_pure import StepParams, step


def _base_state() -> SimState:
    return SimState(
        tick=5,
        actors=FrozenDict(
            {
                "agent_001": ActorState(
                    id="agent_001",
                    actor_type="agent",
                    tokens=100.0,
                    ups_balance=200.0,
                    coherence=0.60,
                    rank=1,
                )
            }
        ),
        foundups=FrozenDict(
            {
                "fup_001": FoundUpState(
                    id="fup_001",
                    stage=3,
                    total_tokens=1000.0,
                    cabr_score=0.7,
                    btc_reserve=1.2,
                )
            }
        ),
        pools=PoolState(un_pool=60, dao_pool=16, du_pool=4, network_pool=10, fund_pool=2),
        btc_reserve_total=1.2,
        fi_released_total=1000.0,
    )


def test_step_returns_new_state_with_tick_and_release_updates() -> None:
    current = _base_state()
    nxt = step(
        current,
        StepParams(demurrage_rate_per_tick=0.01, token_release_per_tick=25.0),
        actor_activity={"agent_001": 0.9},
        actor_earnings={"agent_001": 50.0},
        actor_loyalty={"agent_001": 0.8},
    )

    assert nxt.tick == 6
    assert nxt.foundups["fup_001"].total_tokens == pytest.approx(1025.0)
    assert nxt.fi_released_total == pytest.approx(1025.0)
    assert nxt.actors["agent_001"].tokens == pytest.approx(150.0)
    assert nxt.actors["agent_001"].ups_balance == pytest.approx(198.0)
    assert nxt.pools.network_pool > current.pools.network_pool
    assert nxt.pools.fund_pool > current.pools.fund_pool
    assert current.tick == 5  # immutable original preserved
