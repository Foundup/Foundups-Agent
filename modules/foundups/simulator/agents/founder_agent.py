"""Founder agent - creates FoundUps using FAM interfaces."""

from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING, Optional

from .base_agent import BaseSimAgent

if TYPE_CHECKING:
    from ..adapters.fam_bridge import FAMBridge
    from ..adapters.phantom_plugs import PhantomTokenEconomy, PhantomSocialActions
    from ..state_store import StateStore

logger = logging.getLogger(__name__)

# Sample project names for generating FoundUps
FOUNDUP_NAMES = [
    "MetaForge",
    "NexusDAO",
    "QuantumLeap",
    "SynergyHub",
    "AetherNet",
    "CryptoSphere",
    "BlockPulse",
    "ChainLink",
    "TokenVault",
    "DeFiMatrix",
    "SmartStack",
    "NodeNexus",
    "DataStream",
    "CloudMesh",
    "AIForge",
]

# Sample token symbols
TOKEN_SYMBOLS = [
    "META",
    "NEXS",
    "QNTM",
    "SYNE",
    "AETH",
    "CRSP",
    "BLKP",
    "CHLK",
    "TKVT",
    "DFMX",
    "SMST",
    "NDNX",
    "DATA",
    "CLMS",
    "AIFO",
]


class FounderAgent(BaseSimAgent):
    """Agent that creates FoundUps.

    Behavior:
    - Periodically creates new FoundUps
    - Uses TokenFactory via FAM bridge
    - Creates initial tasks for FoundUps
    """

    def __init__(
        self,
        agent_id: str,
        fam_bridge: "FAMBridge",
        token_economy: "PhantomTokenEconomy",
        social_actions: "PhantomSocialActions",
        state_store: "StateStore",
        creation_cost: int = 100,
        max_foundups: int = 3,
        **kwargs,
    ) -> None:
        """Initialize founder agent.

        Args:
            agent_id: Unique agent identifier
            fam_bridge: Bridge to FAM modules
            token_economy: Phantom token economy
            social_actions: Phantom social actions
            state_store: State store for recording actions
            creation_cost: Cost to create a FoundUp
            max_foundups: Max FoundUps this agent can create
        """
        super().__init__(
            agent_id=agent_id,
            fam_bridge=fam_bridge,
            token_economy=token_economy,
            social_actions=social_actions,
            state_store=state_store,
            **kwargs,
        )
        self._creation_cost = creation_cost
        self._max_foundups = max_foundups
        self._created_foundups: list = []
        self._name_index = 0

    @property
    def agent_type(self) -> str:
        return "founder"

    def _choose_action(self, tick: int) -> Optional[str]:
        """Choose action - founders primarily create FoundUps."""
        # Check if can afford to create
        if self.get_balance() < self._creation_cost:
            return None

        # Check if at max foundups
        if len(self._created_foundups) >= self._max_foundups:
            # Maybe create a task instead
            if self._created_foundups and random.random() < 0.5:
                return "create_task"
            return None

        return "create_foundup"

    def _perform_action(self, action: str, tick: int) -> bool:
        """Perform the chosen action."""
        if action == "create_foundup":
            return self._create_foundup(tick)
        elif action == "create_task":
            return self._create_task(tick)
        return False

    def _create_foundup(self, tick: int) -> bool:
        """Create a new FoundUp."""
        # Spend tokens first
        success, msg = self._tokens.spend(
            self.agent_id,
            self._creation_cost,
            "create foundup",
        )
        if not success:
            logger.debug(f"[FOUNDER] {self.agent_id} can't afford FoundUp: {msg}")
            return False

        # Generate name and symbol
        name_idx = (self._name_index + hash(self.agent_id)) % len(FOUNDUP_NAMES)
        name = f"{FOUNDUP_NAMES[name_idx]}_{len(self._created_foundups)}"
        symbol = TOKEN_SYMBOLS[name_idx % len(TOKEN_SYMBOLS)]
        self._name_index += 1

        # Create via FAM bridge
        success, msg, foundup_id = self._fam.create_foundup(
            name=name,
            owner_id=self.agent_id,
            token_symbol=symbol,
            metadata={"created_tick": str(tick)},
        )

        if success and foundup_id:
            self._created_foundups.append(foundup_id)

            # Register with token economy
            self._tokens.register_foundup(foundup_id)

            logger.info(f"[FOUNDER] {self.agent_id} created FoundUp '{name}' ({foundup_id})")
            return True

        logger.warning(f"[FOUNDER] {self.agent_id} failed to create FoundUp: {msg}")
        return False

    def _create_task(self, tick: int) -> bool:
        """Create a task for one of our FoundUps."""
        if not self._created_foundups:
            return False

        # Pick a random owned foundup
        foundup_id = random.choice(self._created_foundups)

        # Create task via FAM bridge
        success, msg, task_id = self._fam.create_task(
            foundup_id=foundup_id,
            title=f"Task at tick {tick}",
            description="Complete this task to earn tokens",
            reward_amount=random.randint(10, 50),
            creator_id=self.agent_id,
        )

        if success:
            logger.debug(f"[FOUNDER] {self.agent_id} created task for {foundup_id}")
            return True

        return False

    def get_owned_foundups(self) -> list:
        """Get list of owned FoundUp IDs."""
        return self._created_foundups.copy()
