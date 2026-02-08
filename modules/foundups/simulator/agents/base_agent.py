"""Base agent class for simulator.

All agents inherit from this and implement step() behavior.
"""

from __future__ import annotations

import logging
import random
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from ..adapters.fam_bridge import FAMBridge
    from ..adapters.phantom_plugs import PhantomTokenEconomy, PhantomSocialActions
    from ..state_store import StateStore

logger = logging.getLogger(__name__)


class BaseSimAgent(ABC):
    """Base class for simulator agents.

    Agents are autonomous entities that:
    - Have a token balance
    - Can perform actions (create, like, stake, etc.)
    - Enter cooldown or waiting states
    - Use FAM interfaces (no logic invention)
    """

    def __init__(
        self,
        agent_id: str,
        fam_bridge: "FAMBridge",
        token_economy: "PhantomTokenEconomy",
        social_actions: "PhantomSocialActions",
        state_store: "StateStore",
        action_probability: float = 0.3,
        cooldown_ticks: int = 5,
    ) -> None:
        """Initialize base agent.

        Args:
            agent_id: Unique agent identifier
            fam_bridge: Bridge to FAM modules
            token_economy: Phantom token economy
            social_actions: Phantom social actions
            state_store: State store for recording actions
            action_probability: Chance to act each tick
            cooldown_ticks: Ticks between actions
        """
        self.agent_id = agent_id
        self._fam = fam_bridge
        self._tokens = token_economy
        self._social = social_actions
        self._state_store = state_store
        self._action_probability = action_probability
        self._cooldown_ticks = cooldown_ticks

        # State
        self._cooldown_remaining = 0
        self._status = "active"  # active, cooldown, broke, waiting

        # Register with token economy
        self._tokens.register_agent(agent_id)

        # Register with state store
        self._state_store.register_agent(
            agent_id=agent_id,
            agent_type=self.agent_type,
            initial_tokens=self._tokens.get_balance(agent_id),
        )

    @property
    @abstractmethod
    def agent_type(self) -> str:
        """Return agent type string."""
        pass

    @abstractmethod
    def _choose_action(self, tick: int) -> Optional[str]:
        """Choose an action to perform.

        Args:
            tick: Current simulation tick

        Returns:
            Action name or None if no action
        """
        pass

    @abstractmethod
    def _perform_action(self, action: str, tick: int) -> bool:
        """Perform the chosen action.

        Args:
            action: Action name
            tick: Current simulation tick

        Returns:
            True if action succeeded
        """
        pass

    def step(self, tick: int) -> None:
        """Execute one simulation step.

        Args:
            tick: Current simulation tick
        """
        # Check if in cooldown
        if self._cooldown_remaining > 0:
            self._cooldown_remaining -= 1
            return

        # Check if broke
        if self._tokens.get_balance(self.agent_id) <= 0:
            self._status = "broke"
            return

        # Random chance to act
        if random.random() > self._action_probability:
            return

        # Choose and perform action
        action = self._choose_action(tick)
        if action:
            success = self._perform_action(action, tick)
            if success:
                self._cooldown_remaining = self._cooldown_ticks
                self._state_store.record_agent_action(
                    agent_id=self.agent_id,
                    action=action,
                    tick=tick,
                    cooldown=self._cooldown_ticks,
                )

        # Update state store with current balance
        current_balance = self._tokens.get_balance(self.agent_id)
        # Calculate delta from last known balance
        agent_state = self._state_store._state.agents.get(self.agent_id)
        if agent_state:
            delta = current_balance - agent_state.tokens
            if delta != 0:
                self._state_store.update_agent_tokens(self.agent_id, delta)

    def is_active(self) -> bool:
        """Check if agent can act."""
        return self._status == "active" and self._cooldown_remaining == 0

    def get_balance(self) -> int:
        """Get current token balance."""
        return self._tokens.get_balance(self.agent_id)
