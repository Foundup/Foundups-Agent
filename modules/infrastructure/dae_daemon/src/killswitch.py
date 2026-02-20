"""Security Killswitch — Layer 3.

Emergency detach mechanism for the cardiovascular system.
When a security violation crosses the threshold, the killswitch:
1. Sets DAE state to DETACHED
2. Terminates the OS process (PID) if tracked
3. Sets thread stop signal if in-process
4. Disables the DAE (prevents restart until 012 re-enables)
5. Generates a KillswitchReport for investigation

Policy rules:
    1 CRITICAL event = immediate detach
    3+ HIGH events from same DAE in 5 min = detach
    WARNING = log only

WSP Compliance:
    WSP 72: Imports only Layer 0-2
"""

import logging
import sys
import time
import threading
from collections import defaultdict
from typing import Any, Dict, List, Optional

from modules.infrastructure.dae_daemon.src.schemas import (
    DAEEvent,
    DAEEventType,
    DAEState,
    KillswitchReport,
    SecuritySeverity,
)

logger = logging.getLogger(__name__)

# Threshold: 3 HIGH events in 5 minutes triggers detach
HIGH_EVENT_THRESHOLD = 3
HIGH_EVENT_WINDOW_SEC = 300.0


class Killswitch:
    """Emergency detach for Domain Autonomous Ecosystems."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        # Track HIGH-severity timestamps per DAE: {dae_id: [timestamp, ...]}
        self._high_events: Dict[str, List[float]] = defaultdict(list)
        # Generated reports
        self._reports: List[KillswitchReport] = []
        # Thread stop signals for in-process DAEs: {dae_id: threading.Event}
        self._stop_signals: Dict[str, threading.Event] = {}

    # ------------------------------------------------------------------
    # Stop signal management (for in-process DAEs)
    # ------------------------------------------------------------------

    def register_stop_signal(self, dae_id: str, stop_event: threading.Event) -> None:
        """Register a threading.Event that will be set on killswitch trigger."""
        self._stop_signals[dae_id] = stop_event

    # ------------------------------------------------------------------
    # Security event evaluation
    # ------------------------------------------------------------------

    def evaluate_security_event(self, event: DAEEvent) -> Optional[KillswitchReport]:
        """Evaluate a security event and decide if killswitch should trigger.

        Returns KillswitchReport if detach was triggered, None otherwise.
        """
        if event.event_type != DAEEventType.SECURITY_VIOLATION:
            return None

        severity_str = event.payload.get("severity", "info")
        try:
            severity = SecuritySeverity(severity_str)
        except ValueError:
            severity = SecuritySeverity.INFO

        reason = event.payload.get("reason", "unspecified")
        dae_id = event.dae_id

        if severity == SecuritySeverity.CRITICAL:
            logger.critical(
                "[KILLSWITCH] CRITICAL violation from %s: %s — IMMEDIATE DETACH",
                dae_id, reason,
            )
            self._alert_012(dae_id, f"CRITICAL: {reason} — DAE DETACHED", 0, 0)
            return self._generate_report(
                dae_id=dae_id,
                reason=f"CRITICAL: {reason}",
                severity=severity,
                event_ids=[event.event_id],
            )

        if severity == SecuritySeverity.HIGH:
            should_detach = False
            high_count = 0
            with self._lock:
                now = time.time()
                # Prune old entries
                self._high_events[dae_id] = [
                    ts for ts in self._high_events[dae_id]
                    if now - ts < HIGH_EVENT_WINDOW_SEC
                ]
                self._high_events[dae_id].append(now)

                if len(self._high_events[dae_id]) >= HIGH_EVENT_THRESHOLD:
                    logger.critical(
                        "[KILLSWITCH] %d HIGH violations from %s in %.0fs — DETACH",
                        len(self._high_events[dae_id]), dae_id, HIGH_EVENT_WINDOW_SEC,
                    )
                    self._high_events[dae_id].clear()
                    should_detach = True
                else:
                    high_count = len(self._high_events[dae_id])
                    logger.warning(
                        "[KILLSWITCH] HIGH violation from %s (%d/%d): %s",
                        dae_id, high_count, HIGH_EVENT_THRESHOLD, reason,
                    )

            # Alert 012 via popup (non-blocking, outside lock)
            if not should_detach:
                self._alert_012(dae_id, reason, high_count, HIGH_EVENT_THRESHOLD)

            # Generate report OUTSIDE lock to avoid deadlock
            if should_detach:
                return self._generate_report(
                    dae_id=dae_id,
                    reason=f"Threshold: {HIGH_EVENT_THRESHOLD}+ HIGH events in {HIGH_EVENT_WINDOW_SEC}s. Last: {reason}",
                    severity=severity,
                    event_ids=[event.event_id],
                )

        if severity == SecuritySeverity.WARNING:
            logger.warning("[KILLSWITCH] WARNING from %s: %s (logged only)", dae_id, reason)

        return None

    # ------------------------------------------------------------------
    # Trigger (the actual detach)
    # ------------------------------------------------------------------

    def trigger(
        self,
        dae_id: str,
        reason: str,
        severity: SecuritySeverity = SecuritySeverity.CRITICAL,
        event_ids: Optional[List[str]] = None,
        pid: Optional[int] = None,
    ) -> KillswitchReport:
        """Manually trigger the killswitch for a DAE.

        This is the low-level trigger — called by evaluate_security_event
        or directly by the central daemon.
        """
        return self._generate_report(
            dae_id=dae_id,
            reason=reason,
            severity=severity,
            event_ids=event_ids or [],
            pid_override=pid,
        )

    def _generate_report(
        self,
        dae_id: str,
        reason: str,
        severity: SecuritySeverity,
        event_ids: List[str],
        pid_override: Optional[int] = None,
    ) -> KillswitchReport:
        """Generate a killswitch report and attempt process termination."""
        pid = pid_override
        kill_success = False

        # Attempt PID termination
        if pid is not None:
            kill_success = self._terminate_pid(pid)

        # Set thread stop signal (for in-process DAEs)
        stop_event = self._stop_signals.get(dae_id)
        if stop_event is not None:
            stop_event.set()
            logger.info("[KILLSWITCH] Stop signal set for %s", dae_id)

        report = KillswitchReport(
            dae_id=dae_id,
            reason=reason,
            severity=severity,
            triggering_event_ids=event_ids,
            pid_terminated=pid,
            pid_kill_success=kill_success,
        )

        with self._lock:
            self._reports.append(report)

        logger.critical(
            "[KILLSWITCH] Report generated for %s: %s (pid=%s, killed=%s)",
            dae_id, reason, pid, kill_success,
        )
        return report

    def _terminate_pid(self, pid: int) -> bool:
        """Attempt to terminate a process by PID (Windows-compatible)."""
        try:
            import psutil
            proc = psutil.Process(pid)
            proc.terminate()
            try:
                proc.wait(timeout=5)
                logger.info("[KILLSWITCH] PID %d terminated gracefully", pid)
                return True
            except psutil.TimeoutExpired:
                proc.kill()
                logger.warning("[KILLSWITCH] PID %d force-killed after 5s timeout", pid)
                return True
        except ImportError:
            # psutil not available — try os.kill
            import os
            import signal
            try:
                os.kill(pid, signal.SIGTERM)
                logger.info("[KILLSWITCH] PID %d sent SIGTERM (no psutil)", pid)
                return True
            except (OSError, ProcessLookupError) as exc:
                logger.error("[KILLSWITCH] os.kill(%d) failed: %s", pid, exc)
                return False
        except Exception as exc:
            logger.error("[KILLSWITCH] PID %d termination failed: %s", pid, exc)
            return False

    # ------------------------------------------------------------------
    # 012 Alert (popup notification for HIGH events)
    # ------------------------------------------------------------------

    def _alert_012(self, dae_id: str, reason: str, count: int, threshold: int) -> None:
        """Show a popup alert to 012 for HIGH security events.

        Non-blocking: runs in a daemon thread so it doesn't stall the
        killswitch evaluation pipeline.  On Windows 11 uses a native
        MessageBox; everywhere else falls back to a console banner +
        system bell.
        """
        title = f"0102 SECURITY ALERT — {dae_id}"
        body = (
            f"HIGH severity violation from: {dae_id}\n\n"
            f"Reason: {reason}\n\n"
            f"Event {count}/{threshold} toward automatic DETACH.\n"
            f"Investigate immediately or disable the DAE from the dashboard."
        )

        def _show():
            if sys.platform.startswith("win"):
                try:
                    import ctypes
                    # MB_ICONWARNING (0x30) | MB_TOPMOST (0x40000) | MB_SETFOREGROUND (0x10000)
                    flags = 0x30 | 0x40000 | 0x10000
                    ctypes.windll.user32.MessageBoxW(0, body, title, flags)
                    return
                except Exception:
                    pass  # Fall through to console
            # Fallback: console banner + bell
            print(f"\a\n{'!'*60}")
            print(f"  {title}")
            print(f"  {reason}")
            print(f"  ({count}/{threshold} toward auto-detach)")
            print(f"{'!'*60}\n")

        t = threading.Thread(target=_show, name=f"alert-012-{dae_id}", daemon=True)
        t.start()

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def get_reports(self, dae_id: Optional[str] = None) -> List[KillswitchReport]:
        """Get killswitch reports, optionally filtered by dae_id."""
        with self._lock:
            if dae_id:
                return [r for r in self._reports if r.dae_id == dae_id]
            return list(self._reports)

    def get_high_event_counts(self) -> Dict[str, int]:
        """Get current HIGH event counts per DAE (within window)."""
        now = time.time()
        with self._lock:
            return {
                dae_id: len([
                    ts for ts in timestamps
                    if now - ts < HIGH_EVENT_WINDOW_SEC
                ])
                for dae_id, timestamps in self._high_events.items()
            }
