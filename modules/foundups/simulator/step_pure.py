"""Pure immutable step function over `SimState` contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional

from .behavior.agents import advance_actor
from .state_contracts import ActorState, FrozenDict, PoolState, SimState


@dataclass(frozen=True)
class StepParams:
    """Pure-step parameters for contract-level simulation."""

    demurrage_rate_per_tick: float = 0.0
    token_release_per_tick: float = 0.0
    network_share_of_demurrage: float = 0.80
    fund_share_of_demurrage: float = 0.20


def step(
    current_state: SimState,
    params: StepParams,
    *,
    actor_activity: Optional[Mapping[str, float]] = None,
    actor_earnings: Optional[Mapping[str, float]] = None,
    actor_loyalty: Optional[Mapping[str, float]] = None,
) -> SimState:
    """Compute next immutable `SimState`.

    This function is deterministic and side-effect free.
    """
    actor_activity = actor_activity or {}
    actor_earnings = actor_earnings or {}
    actor_loyalty = actor_loyalty or {}

    next_actors: dict[str, ActorState] = {}
    total_demurrage = 0.0
    for actor_id, actor in current_state.actors.items():
        demurrage_loss = actor.ups_balance * params.demurrage_rate_per_tick
        total_demurrage += demurrage_loss
        earning_delta = float(actor_earnings.get(actor_id, 0.0))
        next_actors[actor_id] = advance_actor(
            actor,
            delta_tokens=earning_delta,
            delta_ups=-demurrage_loss,
            activity_signal=float(actor_activity.get(actor_id, 0.0)),
            earnings_signal=min(1.0, max(0.0, earning_delta / 500.0)),
            loyalty_signal=float(actor_loyalty.get(actor_id, 0.0)),
        )

    next_foundups = {
        foundup_id: foundup.__class__(
            id=foundup.id,
            stage=foundup.stage,
            total_tokens=foundup.total_tokens + params.token_release_per_tick,
            cabr_score=foundup.cabr_score,
            btc_reserve=foundup.btc_reserve,
        )
        for foundup_id, foundup in current_state.foundups.items()
    }

    next_pools = PoolState(
        un_pool=current_state.pools.un_pool,
        dao_pool=current_state.pools.dao_pool,
        du_pool=current_state.pools.du_pool,
        network_pool=current_state.pools.network_pool
        + total_demurrage * params.network_share_of_demurrage,
        fund_pool=current_state.pools.fund_pool
        + total_demurrage * params.fund_share_of_demurrage,
    )

    return SimState(
        tick=current_state.tick + 1,
        actors=FrozenDict(next_actors),
        foundups=FrozenDict(next_foundups),
        pools=next_pools,
        btc_reserve_total=current_state.btc_reserve_total,
        fi_released_total=current_state.fi_released_total + params.token_release_per_tick,
    )
