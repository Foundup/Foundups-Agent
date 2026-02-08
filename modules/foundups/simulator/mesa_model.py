"""Mesa model wrapper for FoundUps simulation.

Coordinates agent stepping and integrates with FAM modules.
"""

from __future__ import annotations

import logging
import random
import time
from typing import TYPE_CHECKING, Dict, List, Optional, Type

from .config import SimulatorConfig, DEFAULT_CONFIG
from .event_bus import EventBus
from .state_store import StateStore
from .adapters.fam_bridge import FAMBridge
from .adapters.phantom_plugs import PhantomTokenEconomy, PhantomSocialActions
from .agents.base_agent import BaseSimAgent
from .agents.founder_agent import FounderAgent
from .agents.user_agent import UserAgent

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class FoundUpsModel:
    """Mesa-like model for FoundUps simulation.

    This is a simplified Mesa model that coordinates agents
    without requiring the full Mesa dependency. If Mesa is
    needed later, this can be subclassed from mesa.Model.

    Key responsibilities:
    - Initialize FAM components (bridge, token economy)
    - Create and manage agents
    - Step through simulation ticks
    - Maintain SSoT via StateStore
    """

    def __init__(
        self,
        config: Optional[SimulatorConfig] = None,
        fam_daemon: Optional["Any"] = None,
    ) -> None:
        """Initialize the model.

        Args:
            config: Simulation configuration
            fam_daemon: Optional FAMDaemon instance for event SSoT
        """
        self._config = config or DEFAULT_CONFIG
        self._seed = self._config.seed
        random.seed(self._seed)

        # Current tick
        self._tick: int = 0
        self._start_time: float = 0.0
        self._running: bool = False

        # FAM bridge (thin wrapper around FAM modules)
        self._fam_bridge = FAMBridge()

        # Event system (SSoT) - connect to FAMBridge's daemon
        self._event_bus = EventBus()
        daemon = fam_daemon or self._fam_bridge.get_daemon()
        if daemon:
            self._event_bus.connect_fam_daemon(daemon)

        # State store (derived from events)
        self._state_store = StateStore(
            event_bus=self._event_bus,
            grid_width=self._config.grid_width,
            grid_height=self._config.grid_height,
        )

        # Phantom plugs (simulated token/social systems)
        self._token_economy = PhantomTokenEconomy(
            initial_balance=self._config.initial_agent_tokens,
        )
        self._social_actions = PhantomSocialActions(
            like_cost=self._config.like_cost,
            follow_cost=self._config.follow_cost,
            token_economy=self._token_economy,
        )

        # Agents
        self._agents: Dict[str, BaseSimAgent] = {}
        self._agent_order: List[str] = []

        # Initialize agents
        self._create_agents()

        logger.info(
            f"[MODEL] Initialized with {len(self._agents)} agents, "
            f"seed={self._seed}"
        )

    def _create_agents(self) -> None:
        """Create initial agent population."""
        use_ai = self._config.use_ai

        # Create founder agents (Qwen-powered if AI enabled)
        for i in range(self._config.num_founder_agents):
            agent_id = f"founder_{i:03d}"
            agent = FounderAgent(
                agent_id=agent_id,
                fam_bridge=self._fam_bridge,
                token_economy=self._token_economy,
                social_actions=self._social_actions,
                state_store=self._state_store,
                creation_cost=self._config.foundup_creation_cost,
                action_probability=self._config.agent_action_probability,
                cooldown_ticks=self._config.agent_cooldown_ticks,
                use_ai=use_ai,
            )
            self._agents[agent_id] = agent
            self._agent_order.append(agent_id)

            # Register with state store and token economy
            self._state_store.register_agent(
                agent_id, "founder", self._config.initial_agent_tokens
            )
            self._token_economy.register_agent(agent_id)

        # Create user agents (Gemma-powered if AI enabled)
        for i in range(self._config.num_user_agents):
            agent_id = f"user_{i:03d}"
            # Vary risk tolerance across users
            risk_tolerance = self._config.ai_risk_tolerance + (i % 5 - 2) * 0.1
            risk_tolerance = max(0.1, min(0.9, risk_tolerance))

            agent = UserAgent(
                agent_id=agent_id,
                fam_bridge=self._fam_bridge,
                token_economy=self._token_economy,
                social_actions=self._social_actions,
                state_store=self._state_store,
                like_cost=self._config.like_cost,
                follow_cost=self._config.follow_cost,
                stake_min=self._config.stake_min,
                stake_max=self._config.stake_max,
                action_probability=self._config.agent_action_probability,
                cooldown_ticks=self._config.agent_cooldown_ticks,
                use_ai=use_ai,
                risk_tolerance=risk_tolerance,
            )
            self._agents[agent_id] = agent
            self._agent_order.append(agent_id)

            # Register with state store and token economy
            self._state_store.register_agent(
                agent_id, "user", self._config.initial_agent_tokens
            )
            self._token_economy.register_agent(agent_id)

        logger.info(
            f"[MODEL] Created {self._config.num_founder_agents} founders, "
            f"{self._config.num_user_agents} users"
        )

    def step(self) -> None:
        """Execute one simulation tick.

        Mesa convention: model.step() advances simulation by one tick.
        """
        self._tick += 1
        elapsed = time.time() - self._start_time if self._start_time else 0.0

        # Update event bus tick
        self._event_bus.set_tick(self._tick)

        # Step state store
        self._state_store.tick(self._tick, elapsed)

        # Shuffle agent order for fairness
        random.shuffle(self._agent_order)

        # Step each agent
        for agent_id in self._agent_order:
            agent = self._agents[agent_id]
            agent.step(self._tick)

            # Sync token balance to state store
            balance = self._token_economy.get_balance(agent_id)
            current = self._state_store.get_state().agents.get(agent_id)
            if current and current.tokens != balance:
                delta = balance - current.tokens
                self._state_store.update_agent_tokens(agent_id, delta)

        if self._config.verbose:
            logger.debug(f"[MODEL] Tick {self._tick} complete")

    def start(self) -> None:
        """Start the simulation."""
        self._running = True
        self._start_time = time.time()
        logger.info("[MODEL] Simulation started")

    def stop(self) -> None:
        """Stop the simulation."""
        self._running = False
        logger.info(f"[MODEL] Simulation stopped at tick {self._tick}")

    @property
    def tick(self) -> int:
        """Current simulation tick."""
        return self._tick

    @property
    def running(self) -> bool:
        """Whether simulation is running."""
        return self._running

    @property
    def state_store(self) -> StateStore:
        """Get state store for rendering."""
        return self._state_store

    @property
    def event_bus(self) -> EventBus:
        """Get event bus."""
        return self._event_bus

    @property
    def config(self) -> SimulatorConfig:
        """Get simulation config."""
        return self._config

    def get_agent(self, agent_id: str) -> Optional[BaseSimAgent]:
        """Get agent by ID."""
        return self._agents.get(agent_id)

    def get_agents_by_type(self, agent_type: str) -> List[BaseSimAgent]:
        """Get all agents of a given type."""
        return [a for a in self._agents.values() if a.agent_type == agent_type]

    def get_stats(self) -> Dict:
        """Get simulation statistics."""
        state = self._state_store.get_state()
        return {
            "tick": self._tick,
            "elapsed_seconds": state.elapsed_seconds,
            "total_foundups": state.total_foundups,
            "total_likes": state.total_likes,
            "total_stakes": state.total_stakes,
            "total_tokens": state.total_tokens_circulating,
            "agent_count": len(self._agents),
            "founders": len([a for a in self._agents.values() if a.agent_type == "founder"]),
            "users": len([a for a in self._agents.values() if a.agent_type == "user"]),
        }
