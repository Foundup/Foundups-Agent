"""CABR Hook Service for FoundUps Agent Market.

Provides evidence chain for Conscious AI-Based Rating (CABR) scoring.
Collects task metrics, agent performance, and FoundUp health indicators.

WSP References:
- WSP 29: CABR Engine integration
- WSP 26: FoundUPS tokenization metrics
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .interfaces import CABRHookService
from .models import TaskStatus

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class CABRInput:
    """Structured input for CABR scoring."""

    foundup_id: str
    window: str
    tasks_total: int
    tasks_claimed: int
    tasks_submitted: int
    tasks_verified: int
    tasks_paid: int
    completion_rate: float
    verification_rate: float
    avg_cycle_time_hours: float
    active_agents: int
    events_total: int
    collected_at: datetime = field(default_factory=_utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "foundup_id": self.foundup_id,
            "window": self.window,
            "tasks_total": self.tasks_total,
            "tasks_claimed": self.tasks_claimed,
            "tasks_submitted": self.tasks_submitted,
            "tasks_verified": self.tasks_verified,
            "tasks_paid": self.tasks_paid,
            "completion_rate": self.completion_rate,
            "verification_rate": self.verification_rate,
            "avg_cycle_time_hours": self.avg_cycle_time_hours,
            "active_agents": self.active_agents,
            "events_total": self.events_total,
            "collected_at": self.collected_at.isoformat(),
        }


@dataclass
class CABROutput:
    """Structured CABR scoring output."""

    foundup_id: str
    score: float
    confidence: float
    factors: Dict[str, float]
    window: str
    computed_at: datetime = field(default_factory=_utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "foundup_id": self.foundup_id,
            "score": self.score,
            "confidence": self.confidence,
            "factors": self.factors,
            "window": self.window,
            "computed_at": self.computed_at.isoformat(),
        }


class CABRHookStub(CABRHookService):
    """Stub implementation - use InMemoryAgentMarket or PersistentCABRHooks."""

    pass


class PersistentCABRHooks(CABRHookService):
    """CABR hooks with evidence chain persistence.

    Collects metrics from task pipeline and stores CABR inputs/outputs
    for audit trail and scoring verification.
    """

    def __init__(
        self,
        task_source: Any = None,
        event_source: Any = None,
        agent_source: Any = None,
    ) -> None:
        """Initialize with optional data sources.

        Args:
            task_source: Object with get_tasks_by_foundup(foundup_id) -> List[Task]
            event_source: Object with query_events(foundup_id) -> List[Event]
            agent_source: Object with list_agents(foundup_id) -> List[AgentProfile]
        """
        self._task_source = task_source
        self._event_source = event_source
        self._agent_source = agent_source
        self._cabr_inputs: Dict[str, List[CABRInput]] = {}
        self._cabr_outputs: Dict[str, List[CABROutput]] = {}

    def build_cabr_input(self, foundup_id: str, window: str) -> Dict[str, object]:
        """Build CABR input metrics for a FoundUp.

        Collects:
        - Task counts by status
        - Completion and verification rates
        - Average cycle time
        - Active agent count
        - Event volume

        Args:
            foundup_id: FoundUp to collect metrics for
            window: Time window identifier (e.g., "24h", "7d", "30d")

        Returns:
            Dict with CABR input metrics
        """
        # Default metrics if no sources available
        tasks_total = 0
        tasks_claimed = 0
        tasks_submitted = 0
        tasks_verified = 0
        tasks_paid = 0
        events_total = 0
        active_agents = 0

        # Collect from sources if available
        if self._task_source and hasattr(self._task_source, "get_tasks_by_foundup"):
            try:
                tasks = self._task_source.get_tasks_by_foundup(foundup_id)
                tasks_total = len(tasks)
                for task in tasks:
                    if task.status == TaskStatus.CLAIMED:
                        tasks_claimed += 1
                    elif task.status == TaskStatus.SUBMITTED:
                        tasks_submitted += 1
                    elif task.status == TaskStatus.VERIFIED:
                        tasks_verified += 1
                    elif task.status == TaskStatus.PAID:
                        tasks_paid += 1
            except Exception as exc:
                logger.warning("[CABR] Failed to collect task metrics: %s", exc)

        if self._event_source and hasattr(self._event_source, "query_events"):
            try:
                events = self._event_source.query_events(foundup_id=foundup_id)
                events_total = len(events)
            except Exception as exc:
                logger.warning("[CABR] Failed to collect event metrics: %s", exc)

        if self._agent_source and hasattr(self._agent_source, "list_agents"):
            try:
                agents = self._agent_source.list_agents(foundup_id)
                active_agents = len(agents)
            except Exception as exc:
                logger.warning("[CABR] Failed to collect agent metrics: %s", exc)

        # Calculate rates
        completion_rate = tasks_paid / tasks_total if tasks_total > 0 else 0.0
        verification_rate = (
            tasks_verified / tasks_submitted if tasks_submitted > 0 else 0.0
        )

        # Build input
        cabr_input = CABRInput(
            foundup_id=foundup_id,
            window=window,
            tasks_total=tasks_total,
            tasks_claimed=tasks_claimed,
            tasks_submitted=tasks_submitted,
            tasks_verified=tasks_verified,
            tasks_paid=tasks_paid,
            completion_rate=completion_rate,
            verification_rate=verification_rate,
            avg_cycle_time_hours=0.0,  # TODO: Calculate from timestamps
            active_agents=active_agents,
            events_total=events_total,
        )

        # Store for evidence chain
        self._cabr_inputs.setdefault(foundup_id, []).append(cabr_input)

        logger.debug(
            "[CABR] Built input for %s: tasks=%d, completion=%.2f",
            foundup_id,
            tasks_total,
            completion_rate,
        )

        return cabr_input.to_dict()

    def record_cabr_output(self, foundup_id: str, payload: Dict[str, object]) -> None:
        """Record CABR scoring output for evidence chain.

        Args:
            foundup_id: FoundUp the score applies to
            payload: CABR output with score, confidence, factors
        """
        score = float(payload.get("score", 0.0))
        confidence = float(payload.get("confidence", 0.0))
        factors = dict(payload.get("factors", {})) if payload.get("factors") else {}
        window = str(payload.get("window", "unknown"))

        cabr_output = CABROutput(
            foundup_id=foundup_id,
            score=score,
            confidence=confidence,
            factors=factors,
            window=window,
        )

        self._cabr_outputs.setdefault(foundup_id, []).append(cabr_output)

        logger.info(
            "[CABR] Recorded output for %s: score=%.3f, confidence=%.3f",
            foundup_id,
            score,
            confidence,
        )

    def get_latest_score(self, foundup_id: str) -> Optional[float]:
        """Get latest CABR score for a FoundUp."""
        outputs = self._cabr_outputs.get(foundup_id, [])
        if not outputs:
            return None
        return outputs[-1].score

    def get_score_history(
        self, foundup_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get CABR score history for a FoundUp."""
        outputs = self._cabr_outputs.get(foundup_id, [])
        return [o.to_dict() for o in outputs[-limit:]]

    def get_input_history(
        self, foundup_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get CABR input history for audit trail."""
        inputs = self._cabr_inputs.get(foundup_id, [])
        return [i.to_dict() for i in inputs[-limit:]]
