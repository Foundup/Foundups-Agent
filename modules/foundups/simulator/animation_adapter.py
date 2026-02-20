"""Animation adapter for simulator snapshot frames."""

from __future__ import annotations

from dataclasses import asdict
from typing import Dict

from .frame_schema import (
    FRAME_SCHEMA_VERSION,
    ActorFrame,
    FoundUpFrame,
    MetricsFrame,
    PoolFrame,
    SystemStateFrame,
)
from .state_store import SimulatorState


def to_frame(state: SimulatorState, stats: Dict) -> SystemStateFrame:
    """Convert mutable simulator state + stats into immutable frame."""
    foundups = [
        FoundUpFrame(
            foundup_id=tile.foundup_id,
            lifecycle_stage=tile.lifecycle_stage,
            tasks_completed=tile.tasks_completed,
            customer_count=tile.customer_count,
            dex_trades=tile.dex_trades,
            dex_volume_ups=tile.dex_volume_ups,
            total_staked=tile.total_staked,
            glow_intensity=tile.glow_intensity,
        )
        for tile in state.foundups.values()
    ]

    actors = [
        ActorFrame(
            actor_id=agent.agent_id,
            actor_type=agent.agent_type,
            status=agent.status,
            tokens=agent.tokens,
            last_action=agent.last_action,
        )
        for agent in state.agents.values()
    ]

    pools = PoolFrame(
        pavs_treasury_ups=float(stats.get("pavs_treasury_ups", 0.0)),
        network_pool_ups=float(stats.get("network_pool_ups", 0.0)),
        fund_pool_ups=float(stats.get("fund_pool_ups", 0.0)),
        foundup_treasury_ups={},
    )

    metrics = MetricsFrame(
        total_foundups=state.total_foundups,
        total_tokens=state.total_tokens_circulating,
        total_stakes=state.total_stakes,
        total_dex_trades=state.total_dex_trades,
        total_dex_volume_ups=state.total_dex_volume_ups,
        allocation_batches=int(stats.get("allocation_batches", 0)),
        allocation_ups_total=float(stats.get("allocation_ups_total", 0.0)),
        allocation_fi_total=float(stats.get("allocation_fi_total", 0.0)),
    )

    recent_events = [evt.display_text for evt in state.recent_events[-10:]]
    return SystemStateFrame(
        tick=state.tick,
        elapsed_seconds=state.elapsed_seconds,
        foundups=foundups,
        actors=actors,
        pools=pools,
        metrics=metrics,
        recent_events=recent_events,
    )


def to_frame_dict(state: SimulatorState, stats: Dict) -> Dict:
    """Serialize frame for json output."""
    frame = to_frame(state, stats)
    data = asdict(frame)
    data["frame_schema_version"] = FRAME_SCHEMA_VERSION
    return data
