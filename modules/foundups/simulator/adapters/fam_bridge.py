"""FAM Bridge - thin calls into existing FAM modules.

NO LOGIC INVENTION - only wraps existing FAM interfaces.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

logger = logging.getLogger(__name__)


class _IdGenerator:
    """ID generator for simulation entities."""

    def __init__(self, deterministic: bool = True) -> None:
        self._deterministic = deterministic
        self._counters: Dict[str, int] = {}

    def next_id(self, prefix: str) -> str:
        """Generate next ID with prefix."""
        if self._deterministic:
            self._counters.setdefault(prefix, 0)
            self._counters[prefix] += 1
            return f"{prefix}_{self._counters[prefix]:04d}"
        return f"{prefix}_{uuid4().hex[:10]}"

    def reset(self) -> None:
        """Reset counters."""
        self._counters.clear()


class FAMBridge:
    """Bridge to FAM modules for simulator.

    Provides thin wrappers around:
    - InMemoryAgentMarket (registry, task pipeline)
    - FAMDaemon (event emission)
    - TokenFactory (phantom plug if not wired)
    - TreasuryGovernance (phantom plug if not wired)
    """

    def __init__(
        self,
        data_dir: Optional[Path] = None,
        deterministic: bool = True,
    ) -> None:
        """Initialize FAM bridge.

        Args:
            data_dir: Directory for FAMDaemon persistence
            deterministic: Use deterministic ID generation
        """
        self._data_dir = data_dir or Path(__file__).parent.parent / "memory"
        self._deterministic = deterministic
        self._id_gen = _IdGenerator(deterministic=deterministic)

        # Lazy-loaded components
        self._market: Optional[Any] = None
        self._daemon: Optional[Any] = None

        self._initialize()

    def _initialize(self) -> None:
        """Initialize FAM components."""
        try:
            # Import FAM modules
            from modules.foundups.agent_market.src.in_memory import InMemoryAgentMarket
            from modules.foundups.agent_market.src.fam_daemon import FAMDaemon

            # Create in-memory market with verifier/treasury roles
            self._market = InMemoryAgentMarket(
                actor_roles={
                    "system": "admin",
                    "verifier_0": "verifier",
                    "treasury_0": "treasury",
                    "distribution_0": "distribution",
                },
                deterministic=self._deterministic,
            )

            # Create daemon (don't auto-start - simulator controls timing)
            self._daemon = FAMDaemon(
                data_dir=self._data_dir,
                heartbeat_interval_sec=60.0,  # Slow heartbeat
                auto_start=False,
            )

            logger.info("[FAM-BRIDGE] Initialized with InMemoryAgentMarket + FAMDaemon")

        except ImportError as e:
            logger.error(f"[FAM-BRIDGE] Failed to import FAM modules: {e}")
            raise

    def get_daemon(self) -> Any:
        """Get FAMDaemon instance."""
        return self._daemon

    def get_market(self) -> Any:
        """Get InMemoryAgentMarket instance."""
        return self._market

    # =========================================================================
    # Foundup Operations (wraps InMemoryAgentMarket)
    # =========================================================================

    def create_foundup(
        self,
        name: str,
        owner_id: str,
        token_symbol: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Tuple[bool, str, Optional[str]]:
        """Create a new FoundUp.

        Args:
            name: FoundUp name
            owner_id: Owner agent ID
            token_symbol: Token symbol (e.g., "PROJ")
            metadata: Optional metadata dict

        Returns:
            (success, message, foundup_id or None)
        """
        try:
            from modules.foundups.agent_market.src.models import Foundup

            # Generate ID (InMemoryAgentMarket expects pre-filled ID)
            foundup_id = self._id_gen.next_id("fup")

            foundup = Foundup(
                foundup_id=foundup_id,
                name=name,
                owner_id=owner_id,
                token_symbol=token_symbol.upper(),
                immutable_metadata=metadata or {},
                mutable_metadata={},
            )

            result = self._market.create_foundup(foundup)

            # Emit event via daemon
            self._daemon.emit(
                event_type="foundup_created",
                payload={
                    "name": result.name,
                    "token_symbol": result.token_symbol,
                },
                actor_id=owner_id,
                foundup_id=result.foundup_id,
            )

            return (True, "ok", result.foundup_id)

        except Exception as e:
            logger.error(f"[FAM-BRIDGE] create_foundup failed: {e}")
            return (False, str(e), None)

    def get_foundup(self, foundup_id: str) -> Optional[Any]:
        """Get FoundUp by ID."""
        try:
            return self._market.get_foundup(foundup_id)
        except Exception:
            return None

    def list_foundups(self) -> List[Any]:
        """List all FoundUps."""
        # InMemoryAgentMarket stores foundups in .foundups dict
        return list(self._market.foundups.values())

    # =========================================================================
    # Task Operations (wraps InMemoryAgentMarket)
    # =========================================================================

    def create_task(
        self,
        foundup_id: str,
        title: str,
        description: str,
        reward_amount: int,
        creator_id: str,
    ) -> Tuple[bool, str, Optional[str]]:
        """Create a task for a FoundUp."""
        try:
            from modules.foundups.agent_market.src.models import Task

            # Generate ID (InMemoryAgentMarket expects pre-filled ID)
            task_id = self._id_gen.next_id("task")

            task = Task(
                task_id=task_id,
                foundup_id=foundup_id,
                title=title,
                description=description,
                acceptance_criteria=["Complete the task"],
                reward_amount=reward_amount,
                creator_id=creator_id,
            )

            result = self._market.create_task(task)

            # Emit event
            self._daemon.emit(
                event_type="task_state_changed",
                payload={
                    "task_id": result.task_id,
                    "old_status": None,
                    "new_status": "open",
                },
                actor_id=creator_id,
                foundup_id=foundup_id,
                task_id=result.task_id,
            )

            return (True, "ok", result.task_id)

        except Exception as e:
            logger.error(f"[FAM-BRIDGE] create_task failed: {e}")
            return (False, str(e), None)

    def claim_task(self, task_id: str, agent_id: str) -> Tuple[bool, str]:
        """Claim a task."""
        try:
            task = self._market.claim_task(task_id, agent_id)

            self._daemon.emit(
                event_type="task_state_changed",
                payload={
                    "task_id": task_id,
                    "old_status": "open",
                    "new_status": "claimed",
                    "claimer_id": agent_id,
                },
                actor_id=agent_id,
                foundup_id=task.foundup_id,
                task_id=task_id,
            )

            return (True, "ok")

        except Exception as e:
            return (False, str(e))

    def get_open_tasks(self, foundup_id: Optional[str] = None) -> List[Any]:
        """Get open tasks, optionally filtered by foundup."""
        from modules.foundups.agent_market.src.models import TaskStatus

        tasks = []
        for task in self._market.tasks.values():
            if task.status == TaskStatus.OPEN:
                if foundup_id is None or task.foundup_id == foundup_id:
                    tasks.append(task)
        return tasks

    # =========================================================================
    # Reset (for test isolation)
    # =========================================================================

    def reset(self) -> None:
        """Reset all state for test isolation."""
        if hasattr(self._market, "reset"):
            self._market.reset()
        logger.info("[FAM-BRIDGE] State reset")
