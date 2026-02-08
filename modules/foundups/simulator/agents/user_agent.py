"""User agent - interacts with FoundUps (like, follow, stake)."""

from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING, List, Optional

from .base_agent import BaseSimAgent

if TYPE_CHECKING:
    from ..adapters.fam_bridge import FAMBridge
    from ..adapters.phantom_plugs import PhantomTokenEconomy, PhantomSocialActions
    from ..state_store import StateStore

logger = logging.getLogger(__name__)


class UserAgent(BaseSimAgent):
    """Agent that interacts with FoundUps.

    Behavior:
    - Likes FoundUps (cheap, increases visibility)
    - Follows FoundUps (medium cost, enables notifications)
    - Stakes on FoundUps (expensive, increases influence)
    - Claims and works on tasks
    """

    def __init__(
        self,
        agent_id: str,
        fam_bridge: "FAMBridge",
        token_economy: "PhantomTokenEconomy",
        social_actions: "PhantomSocialActions",
        state_store: "StateStore",
        like_cost: int = 1,
        follow_cost: int = 5,
        stake_min: int = 10,
        stake_max: int = 100,
        **kwargs,
    ) -> None:
        """Initialize user agent.

        Args:
            agent_id: Unique agent identifier
            fam_bridge: Bridge to FAM modules
            token_economy: Phantom token economy
            social_actions: Phantom social actions
            state_store: State store for recording actions
            like_cost: Cost to like a FoundUp
            follow_cost: Cost to follow a FoundUp
            stake_min: Minimum stake amount
            stake_max: Maximum stake amount
        """
        super().__init__(
            agent_id=agent_id,
            fam_bridge=fam_bridge,
            token_economy=token_economy,
            social_actions=social_actions,
            state_store=state_store,
            **kwargs,
        )
        self._like_cost = like_cost
        self._follow_cost = follow_cost
        self._stake_min = stake_min
        self._stake_max = stake_max

        # Track interactions
        self._liked_foundups: List[str] = []
        self._followed_foundups: List[str] = []
        self._staked_foundups: List[str] = []

    @property
    def agent_type(self) -> str:
        return "user"

    def _get_available_foundups(self) -> List[str]:
        """Get list of available FoundUp IDs."""
        return self._state_store.get_foundup_ids()

    def _choose_action(self, tick: int) -> Optional[str]:
        """Choose an action based on balance and available FoundUps."""
        balance = self.get_balance()
        foundups = self._get_available_foundups()

        if not foundups:
            return None

        # Weight actions by cost and balance
        actions = []

        # Like is cheap - always an option if we have tokens
        if balance >= self._like_cost:
            unliked = [f for f in foundups if f not in self._liked_foundups]
            if unliked:
                actions.extend(["like"] * 5)  # High weight

        # Follow is medium cost
        if balance >= self._follow_cost:
            unfollowed = [f for f in foundups if f not in self._followed_foundups]
            if unfollowed:
                actions.extend(["follow"] * 3)

        # Stake is expensive
        if balance >= self._stake_min:
            actions.extend(["stake"] * 2)

        # Claim task if any available
        open_tasks = self._fam.get_open_tasks()
        if open_tasks:
            actions.extend(["claim_task"] * 2)

        if not actions:
            return None

        return random.choice(actions)

    def _perform_action(self, action: str, tick: int) -> bool:
        """Perform the chosen action."""
        if action == "like":
            return self._do_like(tick)
        elif action == "follow":
            return self._do_follow(tick)
        elif action == "stake":
            return self._do_stake(tick)
        elif action == "claim_task":
            return self._do_claim_task(tick)
        return False

    def _do_like(self, tick: int) -> bool:
        """Like a random FoundUp."""
        foundups = self._get_available_foundups()
        unliked = [f for f in foundups if f not in self._liked_foundups]

        if not unliked:
            return False

        foundup_id = random.choice(unliked)
        success, msg = self._social.like(self.agent_id, foundup_id)

        if success:
            self._liked_foundups.append(foundup_id)
            self._state_store.record_like(self.agent_id, foundup_id)
            logger.debug(f"[USER] {self.agent_id} liked {foundup_id}")
            return True

        logger.debug(f"[USER] {self.agent_id} failed to like {foundup_id}: {msg}")
        return False

    def _do_follow(self, tick: int) -> bool:
        """Follow a random FoundUp."""
        foundups = self._get_available_foundups()
        unfollowed = [f for f in foundups if f not in self._followed_foundups]

        if not unfollowed:
            return False

        foundup_id = random.choice(unfollowed)
        success, msg = self._social.follow(self.agent_id, foundup_id)

        if success:
            self._followed_foundups.append(foundup_id)
            logger.debug(f"[USER] {self.agent_id} followed {foundup_id}")
            return True

        return False

    def _do_stake(self, tick: int) -> bool:
        """Stake on a random FoundUp."""
        foundups = self._get_available_foundups()
        if not foundups:
            return False

        # Prefer FoundUps we've liked or followed
        preferred = [f for f in foundups if f in self._liked_foundups or f in self._followed_foundups]
        target_list = preferred if preferred else foundups

        foundup_id = random.choice(target_list)

        # Calculate stake amount based on balance
        balance = self.get_balance()
        max_stake = min(self._stake_max, balance // 2)  # Don't stake more than half
        stake_amount = random.randint(self._stake_min, max(self._stake_min, max_stake))

        success, msg = self._tokens.stake(
            agent_id=self.agent_id,
            foundup_id=foundup_id,
            amount=stake_amount,
            tick=tick,
        )

        if success:
            self._staked_foundups.append(foundup_id)
            self._state_store.record_stake(self.agent_id, foundup_id, stake_amount)
            logger.debug(f"[USER] {self.agent_id} staked {stake_amount} on {foundup_id}")
            return True

        return False

    def _do_claim_task(self, tick: int) -> bool:
        """Claim an open task."""
        open_tasks = self._fam.get_open_tasks()
        if not open_tasks:
            return False

        task = random.choice(open_tasks)
        success, msg = self._fam.claim_task(task.task_id, self.agent_id)

        if success:
            logger.debug(f"[USER] {self.agent_id} claimed task {task.task_id}")
            return True

        return False

    def get_stats(self) -> dict:
        """Get agent statistics."""
        return {
            "liked": len(self._liked_foundups),
            "followed": len(self._followed_foundups),
            "staked": len(self._staked_foundups),
            "balance": self.get_balance(),
        }
