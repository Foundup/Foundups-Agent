"""Immutable frame schema for animation consumers.

Animation must consume snapshots only and never mutate simulator state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Mapping


@dataclass(frozen=True)
class FoundUpFrame:
    foundup_id: str
    lifecycle_stage: str
    tasks_completed: int
    customer_count: int
    dex_trades: int
    dex_volume_ups: float
    total_staked: int
    glow_intensity: float


@dataclass(frozen=True)
class ActorFrame:
    actor_id: str
    actor_type: str
    status: str
    tokens: int
    last_action: str


@dataclass(frozen=True)
class PoolFrame:
    pavs_treasury_ups: float
    network_pool_ups: float
    fund_pool_ups: float
    foundup_treasury_ups: Mapping[str, float]


@dataclass(frozen=True)
class MetricsFrame:
    total_foundups: int
    total_tokens: int
    total_stakes: int
    total_dex_trades: int
    total_dex_volume_ups: float
    allocation_batches: int
    allocation_ups_total: float
    allocation_fi_total: float


@dataclass(frozen=True)
class SystemStateFrame:
    tick: int
    elapsed_seconds: float
    foundups: List[FoundUpFrame]
    actors: List[ActorFrame]
    pools: PoolFrame
    metrics: MetricsFrame
    recent_events: List[str]


FRAME_SCHEMA_VERSION = "1.0.0"
