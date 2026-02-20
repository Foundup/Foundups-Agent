"""CentralDAEmon — Layer 4.

The beating heart of the cardiovascular system.
Singleton daemon that composes EventStore + Registry + Killswitch.
Monitors all registered DAEs via periodic heartbeat checks.

Pattern: Adapted from FAMDaemon (fam_daemon.py:536-787).

WSP Compliance:
    WSP 72: Imports only Layer 0-3
    WSP 84: Reuses FAMDaemon singleton + heartbeat pattern
"""

import logging
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from modules.infrastructure.dae_daemon.src.schemas import (
    DAEEvent,
    DAEEventType,
    DAERegistration,
    DAEState,
    KillswitchReport,
    SecuritySeverity,
)
from modules.infrastructure.dae_daemon.src.event_store import DAEEventStore
from modules.infrastructure.dae_daemon.src.dae_registry import DAERegistry
from modules.infrastructure.dae_daemon.src.killswitch import Killswitch

logger = logging.getLogger(__name__)

# Default data directory
_DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "memory"

# Singleton instance
_central_daemon: Optional["CentralDAEmon"] = None
_daemon_lock = threading.Lock()


class CentralDAEmon:
    """Centralized DAEmon — cardiovascular system for all DAEs.

    Singleton. Use get_central_daemon() to obtain the instance.
    """

    def __init__(self, data_dir: Optional[Path] = None, heartbeat_interval: float = 30.0) -> None:
        self._data_dir = Path(data_dir) if data_dir else _DEFAULT_DATA_DIR
        self._heartbeat_interval = heartbeat_interval

        # Compose layers
        self.event_store = DAEEventStore(data_dir=self._data_dir)
        self.registry = DAERegistry(event_store=self.event_store)
        self.killswitch = Killswitch()

        # Wire killswitch evaluation as registry listener
        self.registry.add_listener(self._on_event)

        # Heartbeat thread
        self._stop_event = threading.Event()
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._state = "stopped"

        logger.info("[CENTRAL-DAEMON] Initialized | data_dir=%s", self._data_dir)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the daemon heartbeat loop."""
        if self._state == "running":
            logger.warning("[CENTRAL-DAEMON] Already running")
            return

        self._stop_event.clear()
        self._state = "running"

        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            name="CentralDAEmon-heartbeat",
            daemon=True,
        )
        self._heartbeat_thread.start()

        self.event_store.write(DAEEvent(
            event_type=DAEEventType.DAEMON_STARTED,
            dae_id="central_daemon",
            payload={"heartbeat_interval": self._heartbeat_interval},
        ))
        logger.info("[CENTRAL-DAEMON] Started (heartbeat every %.0fs)", self._heartbeat_interval)

    def stop(self) -> None:
        """Stop the daemon heartbeat loop."""
        if self._state != "running":
            return

        self._stop_event.set()
        self._state = "stopping"

        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            self._heartbeat_thread.join(timeout=5.0)

        self._state = "stopped"

        self.event_store.write(DAEEvent(
            event_type=DAEEventType.DAEMON_STOPPED,
            dae_id="central_daemon",
        ))
        logger.info("[CENTRAL-DAEMON] Stopped")

    @property
    def state(self) -> str:
        return self._state

    # ------------------------------------------------------------------
    # Heartbeat loop
    # ------------------------------------------------------------------

    def _heartbeat_loop(self) -> None:
        """Periodic check of all registered DAEs."""
        while not self._stop_event.is_set():
            try:
                # Check for stale heartbeats
                degraded = self.registry.check_stale_heartbeats()
                if degraded:
                    logger.warning("[CENTRAL-DAEMON] Degraded DAEs: %s", degraded)

                # Emit daemon heartbeat
                self.event_store.write(DAEEvent(
                    event_type=DAEEventType.DAEMON_HEARTBEAT,
                    dae_id="central_daemon",
                    payload={
                        "registered_count": len(self.registry.get_all()),
                        "states": self.registry.get_all_states(),
                    },
                ))

            except Exception as exc:
                logger.error("[CENTRAL-DAEMON] Heartbeat error: %s", exc)

            self._stop_event.wait(timeout=self._heartbeat_interval)

    # ------------------------------------------------------------------
    # Event listener (wired to registry)
    # ------------------------------------------------------------------

    def _on_event(self, event: DAEEvent) -> None:
        """Process events — forward security events to killswitch."""
        if event.event_type == DAEEventType.SECURITY_VIOLATION:
            report = self.killswitch.evaluate_security_event(event)
            if report:
                self._execute_detach(report)

    def _execute_detach(self, report: KillswitchReport) -> None:
        """Execute a killswitch detach: update registry + emit events."""
        dae_id = report.dae_id

        # Set state to DETACHED
        self.registry.set_state(dae_id, DAEState.DETACHED, report.reason)

        # Disable to prevent restart
        self.registry.disable(dae_id)

        # Emit killswitch event
        self.event_store.write(DAEEvent(
            event_type=DAEEventType.KILLSWITCH_TRIGGERED,
            dae_id=dae_id,
            payload=report.to_dict(),
        ))

        # Emit detach event
        self.event_store.write(DAEEvent(
            event_type=DAEEventType.DAE_DETACHED,
            dae_id=dae_id,
            payload={"reason": report.reason},
        ))

        logger.critical("[CENTRAL-DAEMON] DAE DETACHED: %s — %s", dae_id, report.reason)

    # ------------------------------------------------------------------
    # Convenience delegations
    # ------------------------------------------------------------------

    def register_dae(self, registration: DAERegistration) -> bool:
        """Register a DAE with the cardiovascular system."""
        return self.registry.register(registration)

    def enable_dae(self, dae_id: str) -> bool:
        """Re-enable a DAE (e.g. after killswitch detach)."""
        return self.registry.enable(dae_id)

    def disable_dae(self, dae_id: str) -> bool:
        """Disable a DAE."""
        return self.registry.disable(dae_id)

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def get_dashboard(self) -> Dict[str, Any]:
        """Cardiovascular dashboard view."""
        all_regs = self.registry.get_all()
        store_stats = self.event_store.get_stats()
        reports = self.killswitch.get_reports()

        dae_summary = {}
        for dae_id, reg in all_regs.items():
            dae_summary[dae_id] = {
                "name": reg.dae_name,
                "domain": reg.domain,
                "state": reg.state.value,
                "enabled": reg.enabled,
                "pid": reg.pid,
                "last_heartbeat": reg.last_heartbeat,
            }

        return {
            "daemon_state": self._state,
            "dae_count": len(all_regs),
            "daes": dae_summary,
            "event_store": store_stats,
            "killswitch_reports": [r.to_dict() for r in reports],
            "high_event_counts": self.killswitch.get_high_event_counts(),
        }


# ---------------------------------------------------------------------------
# Singleton factory
# ---------------------------------------------------------------------------

def get_central_daemon(
    data_dir: Optional[Path] = None,
    heartbeat_interval: float = 30.0,
) -> CentralDAEmon:
    """Get or create the singleton CentralDAEmon instance."""
    global _central_daemon
    with _daemon_lock:
        if _central_daemon is None:
            _central_daemon = CentralDAEmon(
                data_dir=data_dir,
                heartbeat_interval=heartbeat_interval,
            )
        return _central_daemon


def reset_central_daemon() -> None:
    """Reset the singleton (for testing only)."""
    global _central_daemon
    with _daemon_lock:
        if _central_daemon is not None:
            _central_daemon.stop()
            _central_daemon = None
