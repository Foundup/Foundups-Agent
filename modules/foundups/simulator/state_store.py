"""State store - derives renderable state from event stream.

This is the ONLY source of truth for the render layer.
All state is computed from FAMDaemon events via the event_bus.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .event_bus import EventBus, SimEvent

logger = logging.getLogger(__name__)


@dataclass
class FoundUpTile:
    """Renderable state for a single FoundUp tile."""

    foundup_id: str
    name: str
    token_symbol: str
    owner_id: str

    # Metrics (derived from events)
    likes: int = 0
    follows: int = 0
    stakes: int = 0
    total_staked: int = 0

    # Token state
    token_supply: int = 0
    tokens_released: int = 0

    # Activity
    task_count: int = 0
    tasks_completed: int = 0
    last_activity_tick: int = 0
    cabr_score: float = 0.0
    cabr_threshold_met: bool = False
    cabr_pipe_size: float = 0.0
    cabr_total_flow_ups: float = 0.0
    cabr_last_flow_ups: float = 0.0

    # Lifecycle state
    lifecycle_stage: str = "PoC"  # PoC -> Proto -> MVP
    beta_launched: bool = False
    customer_count: int = 0
    unique_customers: set[str] = field(default_factory=set, repr=False)

    # DEX activity
    dex_trades: int = 0
    dex_volume_ups: float = 0.0

    # MVP pre-launch market
    mvp_bid_count: int = 0
    mvp_treasury_injection_ups: float = 0.0

    # Visual state
    glow_intensity: float = 0.0  # 0.0 - 1.0, fades over time
    grid_x: int = 0
    grid_y: int = 0

    def decay_glow(self, decay_rate: float = 0.1) -> None:
        """Decay glow intensity over time."""
        self.glow_intensity = max(0.0, self.glow_intensity - decay_rate)

    def pulse_glow(self, intensity: float = 1.0) -> None:
        """Pulse glow on activity."""
        self.glow_intensity = min(1.0, self.glow_intensity + intensity)


@dataclass
class AgentState:
    """Renderable state for a single agent."""

    agent_id: str
    agent_type: str  # "founder" or "user"

    # Token balance
    tokens: int = 0

    # State
    status: str = "active"  # "active", "waiting", "broke", "cooldown"
    cooldown_remaining: int = 0

    # Stats
    foundups_created: int = 0
    likes_given: int = 0
    follows_given: int = 0
    stakes_made: int = 0
    total_staked: int = 0

    # Activity
    last_action_tick: int = 0
    last_action: str = ""


@dataclass
class SimulatorState:
    """Complete renderable state for the simulator.

    This is what the render layer reads.
    """

    # Time
    tick: int = 0
    elapsed_seconds: float = 0.0

    # FoundUps grid
    foundups: Dict[str, FoundUpTile] = field(default_factory=dict)
    foundup_grid: List[List[Optional[str]]] = field(default_factory=list)

    # Agents
    agents: Dict[str, AgentState] = field(default_factory=dict)

    # Global metrics
    total_foundups: int = 0
    total_tokens_circulating: int = 0
    total_likes: int = 0
    total_stakes: int = 0
    total_dex_trades: int = 0
    total_dex_volume_ups: float = 0.0
    pavs_treasury_ups: float = 0.0
    network_pool_ups: float = 0.0
    fund_pool_ups: float = 0.0

    # Event log (for debug panel)
    recent_events: List[SimEvent] = field(default_factory=list)

    # System health
    daemon_running: bool = False
    daemon_heartbeat_count: int = 0
    last_heartbeat_tick: int = 0


class StateStore:
    """Derives renderable state from event stream.

    Subscribes to EventBus and maintains SimulatorState.
    """

    def __init__(
        self,
        event_bus: EventBus,
        grid_width: int = 10,
        grid_height: int = 6,
    ) -> None:
        """Initialize state store.

        Args:
            event_bus: Event bus to subscribe to
            grid_width: Width of FoundUp grid
            grid_height: Height of FoundUp grid
        """
        self._event_bus = event_bus
        self._grid_width = grid_width
        self._grid_height = grid_height

        # Initialize state
        self._state = SimulatorState()
        self._state.foundup_grid = [
            [None for _ in range(grid_width)] for _ in range(grid_height)
        ]

        # Subscribe to events
        event_bus.add_listener(self._on_event)

    def _on_event(self, event: SimEvent) -> None:
        """Handle incoming event and update state."""
        # Add to recent events
        self._state.recent_events.append(event)
        if len(self._state.recent_events) > 20:
            self._state.recent_events.pop(0)

        # Dispatch by event type
        handler = getattr(self, f"_handle_{event.event_type}", None)
        if handler:
            handler(event)
        else:
            logger.debug(f"[STATE-STORE] Unhandled event type: {event.event_type}")

    def _handle_foundup_created(self, event: SimEvent) -> None:
        """Handle foundup_created event."""
        foundup_id = event.foundup_id
        if not foundup_id:
            return

        # Create tile
        tile = FoundUpTile(
            foundup_id=foundup_id,
            name=event.payload.get("name", "Unknown"),
            token_symbol=event.payload.get("token_symbol", "???"),
            owner_id=event.actor_id,
            last_activity_tick=event.tick,
        )
        tile.pulse_glow(1.0)

        # Place on grid
        pos = self._find_grid_position()
        if pos:
            tile.grid_x, tile.grid_y = pos
            self._state.foundup_grid[pos[1]][pos[0]] = foundup_id

        self._state.foundups[foundup_id] = tile
        self._state.total_foundups += 1

        # Update agent stats
        if event.actor_id in self._state.agents:
            self._state.agents[event.actor_id].foundups_created += 1

        logger.debug(f"[STATE-STORE] FoundUp created: {tile.name}")

    def _handle_task_state_changed(self, event: SimEvent) -> None:
        """Handle task_state_changed event."""
        foundup_id = event.foundup_id
        if foundup_id and foundup_id in self._state.foundups:
            tile = self._state.foundups[foundup_id]
            tile.last_activity_tick = event.tick
            tile.pulse_glow(0.5)

            new_status = event.payload.get("new_status", "")
            if new_status == "open":
                tile.task_count += 1
            elif new_status == "paid":
                tile.tasks_completed += 1

            self._recompute_lifecycle_stage(foundup_id)

    def _handle_proof_submitted(self, event: SimEvent) -> None:
        """Handle proof_submitted event."""
        foundup_id = event.foundup_id
        if foundup_id and foundup_id in self._state.foundups:
            self._state.foundups[foundup_id].pulse_glow(0.3)

    def _handle_verification_recorded(self, event: SimEvent) -> None:
        """Handle verification_recorded event."""
        foundup_id = event.foundup_id
        if foundup_id and foundup_id in self._state.foundups:
            self._state.foundups[foundup_id].pulse_glow(0.4)

    def _handle_payout_triggered(self, event: SimEvent) -> None:
        """Handle payout_triggered event."""
        foundup_id = event.foundup_id
        amount = event.payload.get("amount", 0)

        if foundup_id and foundup_id in self._state.foundups:
            tile = self._state.foundups[foundup_id]
            tile.tokens_released += amount
            tile.pulse_glow(0.6)

        self._state.total_tokens_circulating += amount

    def _handle_milestone_published(self, event: SimEvent) -> None:
        """Handle milestone_published event."""
        foundup_id = event.foundup_id
        if foundup_id and foundup_id in self._state.foundups:
            tile = self._state.foundups[foundup_id]
            tile.last_activity_tick = event.tick
            tile.pulse_glow(0.8)
            self._recompute_lifecycle_stage(foundup_id)

    def _handle_fi_trade_executed(self, event: SimEvent) -> None:
        """Handle fi_trade_executed event from decentralized exchange simulation."""
        foundup_id = event.foundup_id
        volume_ups = float(event.payload.get("ups_total", 0.0))

        if foundup_id and foundup_id in self._state.foundups:
            tile = self._state.foundups[foundup_id]
            tile.dex_trades += 1
            tile.dex_volume_ups += volume_ups
            tile.last_activity_tick = event.tick
            tile.pulse_glow(0.5)

        self._state.total_dex_trades += 1
        self._state.total_dex_volume_ups += volume_ups

    def _handle_mvp_bid_submitted(self, event: SimEvent) -> None:
        """Handle mvp_bid_submitted event."""
        foundup_id = event.foundup_id
        if foundup_id and foundup_id in self._state.foundups:
            tile = self._state.foundups[foundup_id]
            tile.mvp_bid_count += 1
            tile.last_activity_tick = event.tick
            tile.pulse_glow(0.4)

    def _handle_mvp_offering_resolved(self, event: SimEvent) -> None:
        """Handle mvp_offering_resolved event."""
        foundup_id = event.foundup_id
        injection_ups = float(event.payload.get("total_injection_ups", 0.0))
        if foundup_id and foundup_id in self._state.foundups:
            tile = self._state.foundups[foundup_id]
            tile.mvp_treasury_injection_ups += injection_ups
            tile.last_activity_tick = event.tick
            tile.pulse_glow(0.8)

        if injection_ups > 0:
            # Injected UPS is treasury capital entering the FoundUp.
            self._state.total_stakes += int(injection_ups)

    def _handle_ups_allocation_result(self, event: SimEvent) -> None:
        """Handle 012 UPS allocation routed by allocation engine."""
        foundup_id = event.foundup_id
        ups_allocated = float(event.payload.get("ups_allocated", 0.0))
        if foundup_id and foundup_id in self._state.foundups and ups_allocated > 0:
            tile = self._state.foundups[foundup_id]
            tile.stakes += 1
            tile.total_staked += int(round(ups_allocated))
            if event.actor_id not in tile.unique_customers:
                tile.unique_customers.add(event.actor_id)
                tile.customer_count = len(tile.unique_customers)
            tile.last_activity_tick = event.tick
            tile.pulse_glow(0.45)
            self._state.total_stakes += int(round(ups_allocated))
            self._recompute_lifecycle_stage(foundup_id)

    def _handle_pavs_treasury_updated(self, event: SimEvent) -> None:
        """Track pAVS/network treasury balances for renderers."""
        self._state.pavs_treasury_ups = float(event.payload.get("pavs_treasury_balance_ups", 0.0))
        self._state.network_pool_ups = float(event.payload.get("network_pool_balance_ups", 0.0))

    def _handle_treasury_separation_snapshot(self, event: SimEvent) -> None:
        """Track periodic treasury separation snapshots."""
        self._state.pavs_treasury_ups = float(event.payload.get("pavs_treasury_ups", 0.0))
        self._state.network_pool_ups = float(event.payload.get("network_pool_ups", 0.0))
        self._state.fund_pool_ups = float(event.payload.get("fund_pool_ups", 0.0))

    def _handle_cabr_score_updated(self, event: SimEvent) -> None:
        """Track CABR score for render and downstream flow diagnostics."""
        foundup_id = event.foundup_id
        if foundup_id and foundup_id in self._state.foundups:
            tile = self._state.foundups[foundup_id]
            tile.cabr_score = float(event.payload.get("total", tile.cabr_score))
            tile.cabr_threshold_met = bool(event.payload.get("threshold_met", False))
            tile.cabr_pipe_size = tile.cabr_score

    def _handle_cabr_pipe_flow_routed(self, event: SimEvent) -> None:
        """Track UPS routed through CABR-sized pipe for each FoundUp."""
        foundup_id = event.foundup_id
        routed_ups = float(event.payload.get("routed_ups", 0.0))
        if foundup_id and foundup_id in self._state.foundups and routed_ups > 0:
            tile = self._state.foundups[foundup_id]
            tile.cabr_pipe_size = float(event.payload.get("cabr_pipe_size", tile.cabr_pipe_size))
            tile.cabr_last_flow_ups = routed_ups
            tile.cabr_total_flow_ups += routed_ups
            tile.last_activity_tick = event.tick
            tile.pulse_glow(0.25)

    def _handle_investor_funding_received(self, event: SimEvent) -> None:
        """Handle investor_funding_received seed/inflow events."""
        foundup_id = event.foundup_id
        if foundup_id and foundup_id in self._state.foundups:
            self._state.foundups[foundup_id].pulse_glow(0.3)

    def _handle_heartbeat(self, event: SimEvent) -> None:
        """Handle heartbeat event."""
        self._state.daemon_heartbeat_count = event.payload.get("heartbeat_number", 0)
        self._state.last_heartbeat_tick = event.tick

    def _handle_daemon_started(self, event: SimEvent) -> None:
        """Handle daemon_started event."""
        self._state.daemon_running = True

    def _handle_daemon_stopped(self, event: SimEvent) -> None:
        """Handle daemon_stopped event."""
        self._state.daemon_running = False

    def _find_grid_position(self) -> Optional[tuple]:
        """Find next available grid position."""
        for y in range(self._grid_height):
            for x in range(self._grid_width):
                if self._state.foundup_grid[y][x] is None:
                    return (x, y)
        return None

    def tick(self, tick_num: int, elapsed: float) -> None:
        """Advance state by one tick.

        Args:
            tick_num: Current tick number
            elapsed: Elapsed time in seconds
        """
        self._state.tick = tick_num
        self._state.elapsed_seconds = elapsed

        # Decay glow on all tiles
        for tile in self._state.foundups.values():
            tile.decay_glow(0.05)

        # Update agent cooldowns
        for agent in self._state.agents.values():
            if agent.cooldown_remaining > 0:
                agent.cooldown_remaining -= 1
                if agent.cooldown_remaining == 0 and agent.status == "cooldown":
                    agent.status = "active"

    def register_agent(
        self,
        agent_id: str,
        agent_type: str,
        initial_tokens: int,
    ) -> None:
        """Register an agent in the state store."""
        self._state.agents[agent_id] = AgentState(
            agent_id=agent_id,
            agent_type=agent_type,
            tokens=initial_tokens,
            status="active",
        )

    def update_agent_tokens(self, agent_id: str, delta: int) -> None:
        """Update agent token balance."""
        if agent_id in self._state.agents:
            agent = self._state.agents[agent_id]
            agent.tokens += delta
            if agent.tokens <= 0:
                agent.tokens = 0
                agent.status = "broke"

    def record_agent_action(
        self,
        agent_id: str,
        action: str,
        tick: int,
        cooldown: int = 0,
    ) -> None:
        """Record an agent action."""
        if agent_id in self._state.agents:
            agent = self._state.agents[agent_id]
            agent.last_action = action
            agent.last_action_tick = tick
            if cooldown > 0:
                agent.cooldown_remaining = cooldown
                agent.status = "cooldown"

    def record_like(self, agent_id: str, foundup_id: str) -> None:
        """Record a like action."""
        if foundup_id in self._state.foundups:
            self._state.foundups[foundup_id].likes += 1
            self._state.foundups[foundup_id].pulse_glow(0.2)
            self._state.total_likes += 1

        if agent_id in self._state.agents:
            self._state.agents[agent_id].likes_given += 1

    def record_stake(self, agent_id: str, foundup_id: str, amount: int) -> None:
        """Record a stake action."""
        if foundup_id in self._state.foundups:
            tile = self._state.foundups[foundup_id]
            tile.stakes += 1
            tile.total_staked += amount
            tile.pulse_glow(0.4)
            if agent_id not in tile.unique_customers:
                tile.unique_customers.add(agent_id)
                tile.customer_count = len(tile.unique_customers)
            self._recompute_lifecycle_stage(foundup_id)
            self._state.total_stakes += amount

        if agent_id in self._state.agents:
            self._state.agents[agent_id].stakes_made += 1
            self._state.agents[agent_id].total_staked += amount

    def _recompute_lifecycle_stage(self, foundup_id: str) -> None:
        """Apply FoundUps lifecycle model: PoC -> Proto -> MVP."""
        tile = self._state.foundups.get(foundup_id)
        if not tile:
            return

        previous = tile.lifecycle_stage
        if tile.tasks_completed >= 1 and tile.customer_count >= 1:
            tile.lifecycle_stage = "MVP"
            tile.beta_launched = True
        elif tile.tasks_completed >= 1:
            tile.lifecycle_stage = "Proto"
        else:
            tile.lifecycle_stage = "PoC"

        if tile.lifecycle_stage != previous:
            tile.pulse_glow(0.7)
            logger.info(
                "[STATE-STORE] Lifecycle stage changed: %s %s -> %s (customers=%d, completed=%d)",
                foundup_id,
                previous,
                tile.lifecycle_stage,
                tile.customer_count,
                tile.tasks_completed,
            )

    def get_state(self) -> SimulatorState:
        """Get current renderable state."""
        return self._state

    def get_foundup_ids(self) -> List[str]:
        """Get list of all foundup IDs."""
        return list(self._state.foundups.keys())

    def get_active_agents(self) -> List[AgentState]:
        """Get list of active agents."""
        return [a for a in self._state.agents.values() if a.status == "active"]
