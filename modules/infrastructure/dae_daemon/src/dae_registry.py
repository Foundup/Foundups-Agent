"""DAE Registry — Layer 2.

The address book for all Domain Autonomous Ecosystems.
Tracks registrations, heartbeats, state transitions, and enable/disable toggles.

WSP Compliance:
    WSP 72: Imports only Layer 0 (schemas) + Layer 1 (event_store)
"""

import logging
import threading
import time
from typing import Any, Callable, Dict, List, Optional

from modules.infrastructure.dae_daemon.src.schemas import (
    DAEEvent,
    DAEEventType,
    DAERegistration,
    DAEState,
)
from modules.infrastructure.dae_daemon.src.event_store import DAEEventStore

logger = logging.getLogger(__name__)


class DAERegistry:
    """Registry of all DAEs in the cardiovascular system."""

    def __init__(self, event_store: DAEEventStore) -> None:
        self._store = event_store
        self._registry: Dict[str, DAERegistration] = {}
        self._lock = threading.Lock()
        self._listeners: List[Callable[[DAEEvent], None]] = []

    # ------------------------------------------------------------------
    # Listeners (for killswitch wiring)
    # ------------------------------------------------------------------

    def add_listener(self, fn: Callable[[DAEEvent], None]) -> None:
        """Register a callback invoked on every emitted event."""
        self._listeners.append(fn)

    def _emit(self, event: DAEEvent) -> None:
        """Write event to store and notify listeners."""
        self._store.write(event)
        for fn in self._listeners:
            try:
                fn(event)
            except Exception as exc:
                logger.error("[DAE-REGISTRY] Listener error: %s", exc)

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, registration: DAERegistration) -> bool:
        """Register a DAE. Returns True if newly registered, False if already known."""
        with self._lock:
            if registration.dae_id in self._registry:
                logger.debug("[DAE-REGISTRY] Already registered: %s", registration.dae_id)
                return False

            self._registry[registration.dae_id] = registration
            self._emit(DAEEvent(
                event_type=DAEEventType.DAE_REGISTERED,
                dae_id=registration.dae_id,
                payload=registration.to_dict(),
            ))
            logger.info("[DAE-REGISTRY] Registered: %s (%s)", registration.dae_id, registration.dae_name)
            return True

    def unregister(self, dae_id: str) -> bool:
        """Remove a DAE from the registry."""
        with self._lock:
            if dae_id not in self._registry:
                return False
            del self._registry[dae_id]
            logger.info("[DAE-REGISTRY] Unregistered: %s", dae_id)
            return True

    # ------------------------------------------------------------------
    # State transitions
    # ------------------------------------------------------------------

    def set_state(self, dae_id: str, new_state: DAEState, reason: str = "") -> bool:
        """Transition a DAE to a new state."""
        with self._lock:
            reg = self._registry.get(dae_id)
            if reg is None:
                return False

            old_state = reg.state
            reg.state = new_state
            self._emit(DAEEvent(
                event_type=DAEEventType.DAE_STATE_CHANGED,
                dae_id=dae_id,
                payload={
                    "old_state": old_state.value,
                    "new_state": new_state.value,
                    "reason": reason,
                },
            ))
            logger.info("[DAE-REGISTRY] %s: %s -> %s (%s)", dae_id, old_state.value, new_state.value, reason)
            return True

    # ------------------------------------------------------------------
    # Enable / Disable (centralized switch)
    # ------------------------------------------------------------------

    def enable(self, dae_id: str) -> bool:
        """Enable a DAE (allow it to start)."""
        with self._lock:
            reg = self._registry.get(dae_id)
            if reg is None:
                return False
            reg.enabled = True
            # If it was detached, move back to registered
            if reg.state == DAEState.DETACHED:
                reg.state = DAEState.REGISTERED
            logger.info("[DAE-REGISTRY] Enabled: %s", dae_id)
            return True

    def disable(self, dae_id: str) -> bool:
        """Disable a DAE (prevent starting, request stop)."""
        with self._lock:
            reg = self._registry.get(dae_id)
            if reg is None:
                return False
            reg.enabled = False
            logger.info("[DAE-REGISTRY] Disabled: %s", dae_id)
            return True

    def is_enabled(self, dae_id: str) -> bool:
        """Check if a DAE is enabled."""
        reg = self._registry.get(dae_id)
        return reg.enabled if reg else False

    # ------------------------------------------------------------------
    # Heartbeat
    # ------------------------------------------------------------------

    def report_heartbeat(self, dae_id: str, health: Optional[Dict[str, Any]] = None) -> bool:
        """Record a heartbeat from a DAE."""
        with self._lock:
            reg = self._registry.get(dae_id)
            if reg is None:
                return False

            reg.last_heartbeat = time.time()

            # If degraded, recover to running on heartbeat
            if reg.state == DAEState.DEGRADED:
                reg.state = DAEState.RUNNING

            self._emit(DAEEvent(
                event_type=DAEEventType.DAE_HEARTBEAT,
                dae_id=dae_id,
                payload=health or {},
            ))
            return True

    def check_stale_heartbeats(self) -> List[str]:
        """Detect DAEs that missed their heartbeat window.

        Returns list of dae_ids that transitioned to DEGRADED.
        """
        now = time.time()
        degraded = []

        with self._lock:
            for dae_id, reg in self._registry.items():
                if reg.state != DAEState.RUNNING:
                    continue
                if reg.last_heartbeat == 0.0:
                    continue  # Never sent a heartbeat yet

                elapsed = now - reg.last_heartbeat
                # Allow 2x the expected interval before marking degraded
                if elapsed > reg.heartbeat_interval_sec * 2:
                    reg.state = DAEState.DEGRADED
                    degraded.append(dae_id)
                    logger.warning(
                        "[DAE-REGISTRY] %s DEGRADED (no heartbeat for %.0fs, expected every %.0fs)",
                        dae_id, elapsed, reg.heartbeat_interval_sec,
                    )

        return degraded

    # ------------------------------------------------------------------
    # Event reporting (cardiovascular observation)
    # ------------------------------------------------------------------

    def report_event(
        self, dae_id: str, event_type: DAEEventType, payload: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Report an observed event from a DAE."""
        if dae_id not in self._registry:
            return False
        self._emit(DAEEvent(
            event_type=event_type,
            dae_id=dae_id,
            payload=payload or {},
        ))
        return True

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def get(self, dae_id: str) -> Optional[DAERegistration]:
        """Get a single DAE registration."""
        return self._registry.get(dae_id)

    def get_all(self) -> Dict[str, DAERegistration]:
        """Get all registrations (snapshot)."""
        return dict(self._registry)

    def get_all_states(self) -> Dict[str, str]:
        """Get all DAE states as {dae_id: state_value}."""
        return {k: v.state.value for k, v in self._registry.items()}
