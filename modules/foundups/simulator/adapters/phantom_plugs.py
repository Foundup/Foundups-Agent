"""Phantom plugs - simulate logic that isn't wired yet.

These provide temporary simulation of:
- Token economics (spending, earning, release schedules)
- Social actions (like, follow, stake)

IMPORTANT: These are PLACEHOLDERS until real logic is wired.
Mark clearly which plugs are phantom vs real.
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class TokenBalance:
    """Token balance for an agent."""

    agent_id: str
    balance: int = 0
    total_earned: int = 0
    total_spent: int = 0


@dataclass
class StakeRecord:
    """Record of a stake on a FoundUp."""

    agent_id: str
    foundup_id: str
    amount: int
    tick: int


class PhantomTokenEconomy:
    """Phantom plug for token economics.

    Simulates:
    - Agent token balances
    - Spending tokens (create, like, stake)
    - Earning tokens (from owned FoundUps)
    - Token release schedules

    PHANTOM: This is NOT the real token logic.
    """

    def __init__(
        self,
        initial_balance: int = 1000,
        release_per_tick: int = 10,
    ) -> None:
        """Initialize phantom token economy.

        Args:
            initial_balance: Starting tokens for new agents
            release_per_tick: Tokens released per tick per FoundUp
        """
        self._initial_balance = initial_balance
        self._release_per_tick = release_per_tick

        self._balances: Dict[str, TokenBalance] = {}
        self._foundup_treasuries: Dict[str, int] = {}
        self._stakes: List[StakeRecord] = []

    def register_agent(self, agent_id: str) -> int:
        """Register agent with initial balance.

        Returns:
            Initial balance
        """
        if agent_id not in self._balances:
            self._balances[agent_id] = TokenBalance(
                agent_id=agent_id,
                balance=self._initial_balance,
            )
            logger.debug(f"[PHANTOM-TOKEN] Agent {agent_id} registered with {self._initial_balance} tokens")
        return self._balances[agent_id].balance

    def get_balance(self, agent_id: str) -> int:
        """Get agent's token balance."""
        if agent_id not in self._balances:
            self.register_agent(agent_id)
        return self._balances[agent_id].balance

    def spend(self, agent_id: str, amount: int, reason: str = "") -> Tuple[bool, str]:
        """Spend tokens.

        Args:
            agent_id: Agent spending
            amount: Amount to spend
            reason: Reason for spending

        Returns:
            (success, message)
        """
        if agent_id not in self._balances:
            self.register_agent(agent_id)

        balance = self._balances[agent_id]
        if balance.balance < amount:
            return (False, f"insufficient: need {amount}, have {balance.balance}")

        balance.balance -= amount
        balance.total_spent += amount
        logger.debug(f"[PHANTOM-TOKEN] {agent_id} spent {amount} ({reason}), balance={balance.balance}")
        return (True, "ok")

    def earn(self, agent_id: str, amount: int, reason: str = "") -> None:
        """Earn tokens."""
        if agent_id not in self._balances:
            self.register_agent(agent_id)

        balance = self._balances[agent_id]
        balance.balance += amount
        balance.total_earned += amount
        logger.debug(f"[PHANTOM-TOKEN] {agent_id} earned {amount} ({reason}), balance={balance.balance}")

    def register_foundup(self, foundup_id: str, max_supply: int = 21_000_000) -> None:
        """Register a FoundUp with treasury."""
        self._foundup_treasuries[foundup_id] = max_supply
        logger.debug(f"[PHANTOM-TOKEN] FoundUp {foundup_id} registered with {max_supply} supply")

    def release_tokens(self, foundup_id: str, owner_id: str) -> int:
        """Release tokens from FoundUp to owner.

        Returns:
            Amount released
        """
        if foundup_id not in self._foundup_treasuries:
            return 0

        treasury = self._foundup_treasuries[foundup_id]
        release = min(self._release_per_tick, treasury)

        if release > 0:
            self._foundup_treasuries[foundup_id] -= release
            self.earn(owner_id, release, f"release from {foundup_id}")

        return release

    def stake(
        self,
        agent_id: str,
        foundup_id: str,
        amount: int,
        tick: int,
    ) -> Tuple[bool, str]:
        """Stake tokens on a FoundUp.

        Returns:
            (success, message)
        """
        success, msg = self.spend(agent_id, amount, f"stake on {foundup_id}")
        if not success:
            return (success, msg)

        self._stakes.append(
            StakeRecord(
                agent_id=agent_id,
                foundup_id=foundup_id,
                amount=amount,
                tick=tick,
            )
        )
        return (True, "ok")

    def get_stakes_for_foundup(self, foundup_id: str) -> List[StakeRecord]:
        """Get all stakes for a FoundUp."""
        return [s for s in self._stakes if s.foundup_id == foundup_id]

    def tick(self) -> None:
        """Advance token economy by one tick.

        Releases tokens from all FoundUps to owners.
        """
        # Note: In real implementation, would need owner lookup
        # For phantom, we skip automatic release - agents must claim
        pass


class PhantomSocialActions:
    """Phantom plug for social actions.

    Simulates:
    - Likes (costs tokens, increases visibility)
    - Follows (costs tokens, enables notifications)
    - Stakes (locks tokens, increases influence)

    PHANTOM: This is NOT the real social logic.
    """

    def __init__(
        self,
        token_economy: PhantomTokenEconomy,
        like_cost: int = 1,
        follow_cost: int = 5,
    ) -> None:
        """Initialize phantom social actions.

        Args:
            token_economy: Token economy for spending
            like_cost: Cost to like
            follow_cost: Cost to follow
        """
        self._tokens = token_economy
        self._like_cost = like_cost
        self._follow_cost = follow_cost

        # Track social state
        self._likes: Dict[str, List[str]] = {}  # foundup_id -> [agent_ids]
        self._follows: Dict[str, List[str]] = {}  # foundup_id -> [agent_ids]

    def like(
        self,
        agent_id: str,
        foundup_id: str,
    ) -> Tuple[bool, str]:
        """Like a FoundUp.

        Args:
            agent_id: Agent liking
            foundup_id: FoundUp to like

        Returns:
            (success, message)
        """
        # Check if already liked
        if foundup_id in self._likes and agent_id in self._likes[foundup_id]:
            return (False, "already liked")

        # Spend tokens
        success, msg = self._tokens.spend(agent_id, self._like_cost, f"like {foundup_id}")
        if not success:
            return (success, msg)

        # Record like
        if foundup_id not in self._likes:
            self._likes[foundup_id] = []
        self._likes[foundup_id].append(agent_id)

        logger.debug(f"[PHANTOM-SOCIAL] {agent_id} liked {foundup_id}")
        return (True, "ok")

    def follow(
        self,
        agent_id: str,
        foundup_id: str,
    ) -> Tuple[bool, str]:
        """Follow a FoundUp.

        Returns:
            (success, message)
        """
        # Check if already following
        if foundup_id in self._follows and agent_id in self._follows[foundup_id]:
            return (False, "already following")

        # Spend tokens
        success, msg = self._tokens.spend(agent_id, self._follow_cost, f"follow {foundup_id}")
        if not success:
            return (success, msg)

        # Record follow
        if foundup_id not in self._follows:
            self._follows[foundup_id] = []
        self._follows[foundup_id].append(agent_id)

        logger.debug(f"[PHANTOM-SOCIAL] {agent_id} followed {foundup_id}")
        return (True, "ok")

    def get_like_count(self, foundup_id: str) -> int:
        """Get like count for a FoundUp."""
        return len(self._likes.get(foundup_id, []))

    def get_follow_count(self, foundup_id: str) -> int:
        """Get follow count for a FoundUp."""
        return len(self._follows.get(foundup_id, []))

    def get_liked_foundups(self, agent_id: str) -> List[str]:
        """Get FoundUps liked by an agent."""
        return [
            fid for fid, agents in self._likes.items() if agent_id in agents
        ]
