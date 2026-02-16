"""Immutable simulator state contracts.

These contracts are used by pure-step modules so tick evolution can be tested
without mutating the runtime model.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Mapping, Optional, TypeVar

from .state_store import SimulatorState

K = TypeVar("K")
V = TypeVar("V")


class FrozenDict(Mapping[K, V], Generic[K, V]):
    """Minimal immutable mapping wrapper used by pure-step contracts."""

    __slots__ = ("_data", "_hash")

    def __init__(self, data: Optional[Mapping[K, V]] = None) -> None:
        self._data = dict(data or {})
        self._hash: Optional[int] = None

    def __getitem__(self, key: K) -> V:
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __hash__(self) -> int:
        if self._hash is None:
            items = tuple(sorted(self._data.items(), key=lambda item: str(item[0])))
            self._hash = hash(items)
        return self._hash

    def to_dict(self) -> dict[K, V]:
        return dict(self._data)


STAGE_TO_INT = {
    "Idea": 0,
    "PoC": 1,
    "Soft-Proto": 2,
    "Proto": 3,
    "MVP": 4,
    "Launch": 5,
}


@dataclass(frozen=True)
class ActorState:
    id: str
    actor_type: str  # "agent" | "human"
    tokens: float
    ups_balance: float
    coherence: float
    rank: int


@dataclass(frozen=True)
class FoundUpState:
    id: str
    stage: int
    total_tokens: float
    cabr_score: float
    btc_reserve: float


@dataclass(frozen=True)
class PoolState:
    un_pool: float      # 60%
    dao_pool: float     # 16%
    du_pool: float      # 4%
    network_pool: float # 16%
    fund_pool: float    # 4%


@dataclass(frozen=True)
class SimState:
    tick: int
    actors: FrozenDict[str, ActorState]
    foundups: FrozenDict[str, FoundUpState]
    pools: PoolState
    btc_reserve_total: float
    fi_released_total: float


def build_sim_state(
    runtime_state: SimulatorState,
    stats: Mapping[str, float],
    *,
    coherence_by_actor: Optional[Mapping[str, float]] = None,
    rank_by_actor: Optional[Mapping[str, int]] = None,
    ups_balance_by_actor: Optional[Mapping[str, float]] = None,
    cabr_by_foundup: Optional[Mapping[str, float]] = None,
) -> SimState:
    """Build immutable `SimState` snapshot from runtime model state.

    This is intentionally a lossless-enough bridge for step-core extraction.
    """
    coherence_by_actor = coherence_by_actor or {}
    rank_by_actor = rank_by_actor or {}
    ups_balance_by_actor = ups_balance_by_actor or {}
    cabr_by_foundup = cabr_by_foundup or {}

    actors = {}
    for agent_id, agent in runtime_state.agents.items():
        actors[agent_id] = ActorState(
            id=agent_id,
            actor_type="agent",
            tokens=float(agent.tokens),
            ups_balance=float(ups_balance_by_actor.get(agent_id, 0.0)),
            coherence=float(coherence_by_actor.get(agent_id, 0.618)),
            rank=int(rank_by_actor.get(agent_id, 1)),
        )

    foundups = {}
    btc_reserve_total = float(stats.get("btc_reserve_total", 0.0))
    for foundup_id, tile in runtime_state.foundups.items():
        foundups[foundup_id] = FoundUpState(
            id=foundup_id,
            stage=STAGE_TO_INT.get(tile.lifecycle_stage, 0),
            total_tokens=float(tile.tokens_released),
            cabr_score=float(cabr_by_foundup.get(foundup_id, 0.0)),
            btc_reserve=btc_reserve_total,
        )

    total_stakes = float(runtime_state.total_stakes)
    pools = PoolState(
        un_pool=total_stakes * 0.60,
        dao_pool=total_stakes * 0.16,
        du_pool=total_stakes * 0.04,
        network_pool=float(stats.get("network_pool_ups", 0.0)),
        fund_pool=float(stats.get("fund_pool_ups", 0.0)),
    )

    return SimState(
        tick=runtime_state.tick,
        actors=FrozenDict(actors),
        foundups=FrozenDict(foundups),
        pools=pools,
        btc_reserve_total=btc_reserve_total,
        fi_released_total=float(stats.get("fi_outstanding", 0.0)),
    )
