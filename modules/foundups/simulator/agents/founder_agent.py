"""Founder agent - creates FoundUps using FAM interfaces.

Supports two modes:
- Random: Template-based FoundUp generation (default)
- AI: Qwen-driven idea generation with CABR scoring
"""

from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING, Dict, Optional

from .base_agent import BaseSimAgent

if TYPE_CHECKING:
    from ..adapters.fam_bridge import FAMBridge
    from ..adapters.phantom_plugs import PhantomTokenEconomy, PhantomSocialActions
    from ..state_store import StateStore
    from ..ai.qwen_founder import QwenFounderBrain
    from ..ai.cabr_estimator import CABRScore

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
        use_ai: bool = False,
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
            use_ai: Whether to use Qwen for idea generation
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
        self._use_ai = use_ai
        self._qwen_brain: Optional["QwenFounderBrain"] = None
        self._cabr_scores: Dict[str, "CABRScore"] = {}
        self._task_count: Dict[str, int] = {}

        # Lazy-load AI brain
        if use_ai:
            try:
                from ..ai.qwen_founder import QwenFounderBrain
                self._qwen_brain = QwenFounderBrain(use_ai=True)
                logger.info(f"[FOUNDER] {agent_id} using Qwen brain")
            except ImportError:
                logger.warning(f"[FOUNDER] {agent_id} AI not available, using random")

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

        # Use AI brain if available
        if self._qwen_brain:
            return self._create_foundup_ai(tick)

        # Fall back to template generation
        return self._create_foundup_template(tick)

    def _create_foundup_ai(self, tick: int) -> bool:
        """Create FoundUp using Qwen brain."""
        idea, cabr_score = self._qwen_brain.generate_foundup_idea()

        # Create via FAM bridge with rich metadata
        success, msg, foundup_id = self._fam.create_foundup(
            name=idea.name,
            owner_id=self.agent_id,
            token_symbol=idea.token_symbol,
            metadata={
                "created_tick": str(tick),
                "pain_point": idea.pain_point,
                "outcome": idea.outcome,
                "category": idea.category,
                "cabr_estimated": str(round(cabr_score.total, 2)),
                "team_size": str(idea.team_size),
                "total_supply": str(idea.total_supply),
            },
        )

        if success and foundup_id:
            self._created_foundups.append(foundup_id)
            self._cabr_scores[foundup_id] = cabr_score
            self._task_count[foundup_id] = 0
            self._tokens.register_foundup(foundup_id)

            logger.info(
                f"[FOUNDER-AI] {self.agent_id} created '{idea.name}' "
                f"({foundup_id}) CABR={cabr_score.total:.2f}"
            )
            logger.info(f"  Pain: {idea.pain_point[:60]}...")
            logger.info(f"  Outcome: {idea.outcome[:60]}...")
            return True

        logger.warning(f"[FOUNDER-AI] {self.agent_id} failed: {msg}")
        return False

    def _create_foundup_template(self, tick: int) -> bool:
        """Create FoundUp using template generation."""
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
            self._task_count[foundup_id] = 0
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
        task_num = self._task_count.get(foundup_id, 0)

        # Get category for AI generation
        category = "infrastructure"  # Default
        if self._qwen_brain and foundup_id in self._cabr_scores:
            # Extract category from CABR reasoning if available
            category = "infrastructure"

        # Generate task (AI or template)
        if self._qwen_brain:
            foundup_name = foundup_id  # Could look up actual name
            task_data = self._qwen_brain.generate_task(foundup_name, category, task_num)
        else:
            task_data = {
                "title": f"Task {task_num} at tick {tick}",
                "description": "Complete this task to earn tokens",
                "reward": random.randint(10, 50),
            }

        # Create task via FAM bridge
        success, msg, task_id = self._fam.create_task(
            foundup_id=foundup_id,
            title=task_data["title"],
            description=task_data["description"],
            reward_amount=task_data["reward"],
            creator_id=self.agent_id,
        )

        if success:
            self._task_count[foundup_id] = task_num + 1
            logger.debug(f"[FOUNDER] {self.agent_id} created task: {task_data['title']}")
            return True

        return False

    def get_owned_foundups(self) -> list:
        """Get list of owned FoundUp IDs."""
        return self._created_foundups.copy()

    def get_cabr_score(self, foundup_id: str) -> Optional["CABRScore"]:
        """Get CABR score for a FoundUp."""
        return self._cabr_scores.get(foundup_id)
