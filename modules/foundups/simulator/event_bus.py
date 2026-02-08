"""Event bus - subscribes to FAMDaemon and normalizes events.

This is the bridge between FAMDaemon (SSoT) and the simulator's state_store.
"""

from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Deque, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SimEvent:
    """Normalized event for simulator consumption.

    Wraps FAMEvent with simulator-specific metadata.
    """

    # From FAMEvent
    event_id: str
    sequence_id: int
    event_type: str
    actor_id: str
    foundup_id: Optional[str]
    task_id: Optional[str]
    payload: Dict[str, Any]
    timestamp: datetime

    # Simulator metadata
    tick: int = 0
    display_text: str = ""

    @classmethod
    def from_fam_event(cls, fam_event: Any, tick: int = 0) -> "SimEvent":
        """Create SimEvent from FAMEvent."""
        # Generate human-readable display text
        display = cls._generate_display_text(
            fam_event.event_type,
            fam_event.actor_id,
            fam_event.foundup_id,
            fam_event.payload,
        )

        return cls(
            event_id=fam_event.event_id,
            sequence_id=fam_event.sequence_id,
            event_type=fam_event.event_type,
            actor_id=fam_event.actor_id,
            foundup_id=fam_event.foundup_id,
            task_id=fam_event.task_id,
            payload=fam_event.payload,
            timestamp=fam_event.timestamp,
            tick=tick,
            display_text=display,
        )

    @staticmethod
    def _generate_display_text(
        event_type: str,
        actor_id: str,
        foundup_id: Optional[str],
        payload: Dict[str, Any],
    ) -> str:
        """Generate human-readable event description."""
        if event_type == "foundup_created":
            name = payload.get("name", "?")
            return f"{actor_id} created FoundUp '{name}'"
        elif event_type == "task_state_changed":
            new_status = payload.get("new_status", "?")
            task_id = payload.get("task_id", "?")
            return f"Task {task_id[:8]} -> {new_status}"
        elif event_type == "proof_submitted":
            return f"{actor_id} submitted proof"
        elif event_type == "verification_recorded":
            approved = payload.get("approved", False)
            return f"Verification: {'APPROVED' if approved else 'REJECTED'}"
        elif event_type == "payout_triggered":
            amount = payload.get("amount", 0)
            return f"Payout: {amount} tokens"
        elif event_type == "heartbeat":
            return f"[heartbeat #{payload.get('heartbeat_number', '?')}]"
        elif event_type == "daemon_started":
            return "[daemon started]"
        elif event_type == "daemon_stopped":
            return "[daemon stopped]"
        else:
            return f"{event_type}: {actor_id}"


class EventBus:
    """Central event bus that subscribes to FAMDaemon.

    Normalizes FAMEvents into SimEvents and distributes to listeners.
    """

    def __init__(self, max_history: int = 100) -> None:
        """Initialize event bus.

        Args:
            max_history: Max events to keep in history
        """
        self._listeners: List[Callable[[SimEvent], None]] = []
        self._history: Deque[SimEvent] = deque(maxlen=max_history)
        self._current_tick: int = 0
        self._fam_daemon: Optional[Any] = None
        self._connected: bool = False

    def connect_fam_daemon(self, daemon: Any) -> None:
        """Connect to FAMDaemon as event source.

        Args:
            daemon: FAMDaemon instance
        """
        if self._connected:
            return

        self._fam_daemon = daemon
        daemon.add_listener(self._on_fam_event)
        self._connected = True
        logger.info("[EVENT-BUS] Connected to FAMDaemon")

    def disconnect(self) -> None:
        """Disconnect from FAMDaemon."""
        if self._fam_daemon and self._connected:
            self._fam_daemon.remove_listener(self._on_fam_event)
            self._connected = False
            logger.info("[EVENT-BUS] Disconnected from FAMDaemon")

    def _on_fam_event(self, fam_event: Any) -> None:
        """Handle incoming FAMEvent."""
        sim_event = SimEvent.from_fam_event(fam_event, self._current_tick)
        self._history.append(sim_event)

        # Notify listeners
        for listener in self._listeners:
            try:
                listener(sim_event)
            except Exception as e:
                logger.warning(f"[EVENT-BUS] Listener error: {e}")

    def add_listener(self, listener: Callable[[SimEvent], None]) -> None:
        """Add event listener."""
        self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[SimEvent], None]) -> None:
        """Remove event listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)

    def set_tick(self, tick: int) -> None:
        """Set current simulation tick."""
        self._current_tick = tick

    def get_history(self, limit: int = 10) -> List[SimEvent]:
        """Get recent event history.

        Args:
            limit: Max events to return

        Returns:
            List of recent SimEvents (newest last)
        """
        history_list = list(self._history)
        return history_list[-limit:]

    def get_events_by_type(self, event_type: str, limit: int = 10) -> List[SimEvent]:
        """Get events filtered by type."""
        filtered = [e for e in self._history if e.event_type == event_type]
        return filtered[-limit:]

    def get_events_by_foundup(
        self, foundup_id: str, limit: int = 10
    ) -> List[SimEvent]:
        """Get events filtered by foundup."""
        filtered = [e for e in self._history if e.foundup_id == foundup_id]
        return filtered[-limit:]
