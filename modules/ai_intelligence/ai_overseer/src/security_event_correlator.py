#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Security Event Correlator for OpenClaw incident detection.

Ingests security events from multiple sources, correlates them within
configurable time windows, and emits openclaw_incident_alert when
thresholds are crossed.

WSP Compliance:
    - WSP 71: Secrets Management (forensics logging)
    - WSP 95: Skill Safety (fail-closed containment)
    - WSP 91: Observability (structured DAEmon signals)
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Security event types tracked by correlator."""
    SECURITY_ALERT = "openclaw_security_alert"
    PERMISSION_DENIED = "permission_denied"
    RATE_LIMITED = "rate_limited"
    COMMAND_FALLBACK = "command_fallback"


class IncidentSeverity(str, Enum):
    """Incident severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ContainmentAction(str, Enum):
    """Containment action types."""
    MUTE_SENDER = "mute_sender"
    MUTE_CHANNEL = "mute_channel"
    ADVISORY_ONLY = "advisory_only"
    NONE = "none"


@dataclass
class SecurityEvent:
    """Individual security event."""
    event_type: EventType
    timestamp: float
    sender: str
    channel: str
    details: Dict[str, Any] = field(default_factory=dict)
    dedupe_key: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "sender": self.sender,
            "channel": self.channel,
            "details": self.details,
            "dedupe_key": self.dedupe_key,
        }


@dataclass
class ContainmentState:
    """Current containment state for a sender/channel."""
    action: ContainmentAction
    applied_at: float
    expires_at: float
    reason: str
    incident_id: str

    def is_active(self) -> bool:
        return time.time() < self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action.value,
            "applied_at": self.applied_at,
            "expires_at": self.expires_at,
            "reason": self.reason,
            "incident_id": self.incident_id,
            "active": self.is_active(),
        }


@dataclass
class Incident:
    """Correlated security incident."""
    incident_id: str
    severity: IncidentSeverity
    first_seen: float
    last_seen: float
    event_counts: Dict[str, int]
    events: List[SecurityEvent]
    containment: Optional[ContainmentAction]
    policy_trigger: str
    status: str = "open"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "severity": self.severity.value,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "event_counts": self.event_counts,
            "events": [e.to_dict() for e in self.events],
            "containment": self.containment.value if self.containment else None,
            "policy_trigger": self.policy_trigger,
            "status": self.status,
        }


def _env_int(name: str, default: int) -> int:
    """Get int from env with default."""
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def _env_bool(name: str, default: bool) -> bool:
    """Get bool from env with default."""
    raw = os.getenv(name)
    if raw is None:
        return default
    return str(raw).strip().lower() not in {"0", "false", "no", "off"}


@dataclass
class ReleaseAuditRecord:
    """Audit record for containment release operations."""
    release_id: str
    target_type: str
    target_id: str
    requested_by: str
    reason: str
    source_ip: str
    session_id: str
    timestamp: float
    success: bool
    auth_method: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "release_id": self.release_id,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "requested_by": self.requested_by,
            "reason": self.reason,
            "source_ip": self.source_ip,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "success": self.success,
            "auth_method": self.auth_method,
        }


class SecurityEventCorrelator:
    """Correlates security events and triggers incidents."""

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()

        # Configuration from env
        self.correlation_window_sec = _env_int("OPENCLAW_CORRELATION_WINDOW_SEC", 300)
        self.incident_threshold = _env_int("OPENCLAW_INCIDENT_THRESHOLD", 5)
        self.containment_enabled = _env_bool("OPENCLAW_CONTAINMENT_ENABLED", True)
        self.containment_duration_sec = _env_int("OPENCLAW_CONTAINMENT_DURATION_SEC", 300)
        self.alert_dedupe_window_sec = _env_int("OPENCLAW_INCIDENT_DEDUPE_SEC", 60)

        # Operator auth config (WSP 71)
        self.operator_token = os.getenv("OPENCLAW_OPERATOR_TOKEN", "")
        self.operator_token_previous = os.getenv("OPENCLAW_OPERATOR_TOKEN_PREVIOUS", "")
        self.replay_window_sec = _env_int("OPENCLAW_REPLAY_WINDOW_SEC", 300)
        self.discord_webhook_url = os.getenv("OPENCLAW_DISCORD_WEBHOOK_URL", "")
        self.notification_dedupe_sec = _env_int("OPENCLAW_NOTIFICATION_DEDUPE_SEC", 300)
        self.notification_retry_max = _env_int("OPENCLAW_NOTIFICATION_RETRY_MAX", 3)
        self.notification_retry_backoff_sec = _env_int("OPENCLAW_NOTIFICATION_RETRY_BACKOFF_SEC", 1)
        self.release_rate_limit_count = _env_int("OPENCLAW_RELEASE_RATE_LIMIT_COUNT", 10)
        self.release_rate_limit_window_sec = _env_int("OPENCLAW_RELEASE_RATE_LIMIT_WINDOW_SEC", 60)
        self.auth_failure_threshold = _env_int("OPENCLAW_AUTH_FAILURE_THRESHOLD", 5)
        self.auth_lockout_sec = _env_int("OPENCLAW_AUTH_LOCKOUT_SEC", 300)
        self.audit_retention_days = _env_int("OPENCLAW_AUDIT_RETENTION_DAYS", 30)
        self.audit_jsonl_max_mb = _env_int("OPENCLAW_AUDIT_JSONL_MAX_MB", 10)
        self.audit_jsonl_keep_files = _env_int("OPENCLAW_AUDIT_JSONL_KEEP_FILES", 5)

        if not self.operator_token and self.operator_token_previous:
            logger.warning(
                "[DAEMON][OPENCLAW-AUTH] event=token_rotation_warning "
                "reason=primary_missing_using_previous_only"
            )

        # Notification dedupe state
        self._notification_history: Dict[str, float] = {}
        self._notification_attempts = 0
        self._notification_successes = 0
        self._notification_failures = 0
        self._notification_retries = 0

        # Replay prevention (nonce tracking)
        self._used_nonces: Dict[str, float] = {}

        # Event storage (bounded by correlation window)
        self._events: List[SecurityEvent] = []
        self._events_by_sender: Dict[str, List[SecurityEvent]] = {}
        self._events_by_channel: Dict[str, List[SecurityEvent]] = {}

        # Incident tracking
        self._incidents: Dict[str, Incident] = {}
        self._incident_dedupe: Dict[str, float] = {}

        # Containment state
        self._sender_containment: Dict[str, ContainmentState] = {}
        self._channel_containment: Dict[str, ContainmentState] = {}

        # Forensics paths
        self.incidents_log = (
            self.repo_root
            / "modules"
            / "ai_intelligence"
            / "ai_overseer"
            / "memory"
            / "openclaw_incidents.jsonl"
        )
        self.bundles_dir = (
            self.repo_root
            / "modules"
            / "ai_intelligence"
            / "ai_overseer"
            / "memory"
            / "incident_bundles"
        )
        self.bundles_dir.mkdir(parents=True, exist_ok=True)
        self.incidents_log.parent.mkdir(parents=True, exist_ok=True)
        self.containment_store = (
            self.repo_root
            / "modules"
            / "ai_intelligence"
            / "ai_overseer"
            / "memory"
            / "openclaw_containment.db"
        )
        self.audit_log = (
            self.repo_root
            / "modules"
            / "ai_intelligence"
            / "ai_overseer"
            / "memory"
            / "openclaw_release_audit.jsonl"
        )
        self._init_containment_store()

        # Suppression counters for DAEmon signals
        self._dedupe_suppressions = 0

        # Startup health check (run BEFORE load to detect stale entries)
        self._consistency_errors: List[str] = []
        self._run_consistency_check()

        # Load containment state (this cleans up stale entries found by consistency check)
        self._load_containment_state()
        self._run_housekeeping(time.time())

    def _connect_containment_db(self) -> sqlite3.Connection:
        """Create sqlite connection for containment state."""
        conn = sqlite3.connect(str(self.containment_store), timeout=5.0)
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def _containment_conn(self):
        """Context manager that always closes sqlite connection."""
        conn = self._connect_containment_db()
        try:
            yield conn
        finally:
            conn.close()

    def _init_containment_store(self) -> None:
        """Initialize persistent containment store."""
        try:
            with self._containment_conn() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS containment_state (
                        target_type TEXT NOT NULL,
                        target_id TEXT NOT NULL,
                        action TEXT NOT NULL,
                        applied_at REAL NOT NULL,
                        expires_at REAL NOT NULL,
                        reason TEXT NOT NULL,
                        incident_id TEXT NOT NULL,
                        PRIMARY KEY (target_type, target_id)
                    )
                    """
                )
                # Audit table for release operations (Tranche 5)
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS release_audit (
                        release_id TEXT PRIMARY KEY,
                        target_type TEXT NOT NULL,
                        target_id TEXT NOT NULL,
                        requested_by TEXT NOT NULL,
                        reason TEXT NOT NULL,
                        source_ip TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        timestamp REAL NOT NULL,
                        success INTEGER NOT NULL,
                        auth_method TEXT NOT NULL
                    )
                    """
                )
                # Nonce table for replay prevention
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS used_nonces (
                        nonce TEXT PRIMARY KEY,
                        used_at REAL NOT NULL
                    )
                    """
                )
                # Release attempts for rate limiting
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS release_attempts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        requested_by TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        attempted_at REAL NOT NULL
                    )
                    """
                )
                # Auth failure history for lockout control
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS auth_failures (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        requested_by TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        failed_at REAL NOT NULL
                    )
                    """
                )
                conn.commit()
        except Exception as exc:
            logger.warning("[CORRELATOR] Failed initializing containment store: %s", exc)

    def _run_housekeeping(self, now: Optional[float] = None) -> None:
        """Run periodic retention and cleanup tasks."""
        ts = now if now is not None else time.time()
        self._prune_used_nonces(ts)
        self._prune_audit_records(ts)
        self._rotate_audit_jsonl_if_needed()

    def _prune_used_nonces(self, now: float) -> None:
        """Prune expired nonce entries from memory and DB."""
        expired = [n for n, t in self._used_nonces.items() if now - t > self.replay_window_sec]
        for nonce in expired:
            self._used_nonces.pop(nonce, None)
        try:
            with self._containment_conn() as conn:
                conn.execute(
                    "DELETE FROM used_nonces WHERE used_at < ?",
                    (now - self.replay_window_sec,),
                )
                conn.commit()
        except Exception as exc:
            logger.warning("[CORRELATOR] Failed pruning used nonces: %s", exc)

    def _prune_audit_records(self, now: float) -> None:
        """Prune old audit/attempt/failure records by retention windows."""
        retention_cutoff = now - max(self.audit_retention_days, 1) * 86400
        rate_cutoff = now - max(self.release_rate_limit_window_sec, 1)
        lockout_cutoff = now - max(self.auth_lockout_sec, 1)
        try:
            with self._containment_conn() as conn:
                conn.execute(
                    "DELETE FROM release_audit WHERE timestamp < ?",
                    (retention_cutoff,),
                )
                conn.execute(
                    "DELETE FROM release_attempts WHERE attempted_at < ?",
                    (rate_cutoff,),
                )
                conn.execute(
                    "DELETE FROM auth_failures WHERE failed_at < ?",
                    (lockout_cutoff,),
                )
                conn.commit()
        except Exception as exc:
            logger.warning("[CORRELATOR] Failed pruning audit records: %s", exc)

    def _rotate_audit_jsonl_if_needed(self) -> None:
        """Rotate JSONL audit file when size threshold is exceeded."""
        try:
            if not self.audit_log.exists():
                return
            max_bytes = max(self.audit_jsonl_max_mb, 1) * 1024 * 1024
            if self.audit_log.stat().st_size < max_bytes:
                return

            timestamp = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
            rotated = self.audit_log.with_name(f"{self.audit_log.stem}_{timestamp}.jsonl")
            self.audit_log.replace(rotated)

            archives = sorted(
                self.audit_log.parent.glob(f"{self.audit_log.stem}_*.jsonl"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            for old in archives[self.audit_jsonl_keep_files :]:
                old.unlink(missing_ok=True)
        except Exception as exc:
            logger.warning("[CORRELATOR] Failed rotating audit JSONL: %s", exc)

    def _record_release_attempt(self, requested_by: str, session_id: str, now: float) -> None:
        """Persist release attempt used by rate limiter."""
        try:
            with self._containment_conn() as conn:
                conn.execute(
                    """
                    INSERT INTO release_attempts (requested_by, session_id, attempted_at)
                    VALUES (?, ?, ?)
                    """,
                    (requested_by, session_id, now),
                )
                conn.commit()
        except Exception as exc:
            logger.warning("[CORRELATOR] Failed recording release attempt: %s", exc)

    def _is_rate_limited(self, requested_by: str, session_id: str, now: float) -> bool:
        """Enforce per-operator/session release rate limits."""
        try:
            with self._containment_conn() as conn:
                cutoff = now - max(self.release_rate_limit_window_sec, 1)
                row = conn.execute(
                    """
                    SELECT COUNT(*) AS cnt FROM release_attempts
                    WHERE attempted_at >= ?
                      AND (requested_by = ? OR session_id = ?)
                    """,
                    (cutoff, requested_by, session_id),
                ).fetchone()
                count = int(row["cnt"]) if row else 0
            return count > max(self.release_rate_limit_count, 1)
        except Exception as exc:
            logger.warning("[CORRELATOR] Rate limit check failed: %s", exc)
            return True

    def _record_auth_failure(self, requested_by: str, session_id: str, now: float) -> None:
        """Persist failed auth attempt for lockout checks."""
        try:
            with self._containment_conn() as conn:
                conn.execute(
                    """
                    INSERT INTO auth_failures (requested_by, session_id, failed_at)
                    VALUES (?, ?, ?)
                    """,
                    (requested_by, session_id, now),
                )
                conn.commit()
        except Exception as exc:
            logger.warning("[CORRELATOR] Failed recording auth failure: %s", exc)

    def _is_locked_out(self, requested_by: str, session_id: str, now: float) -> bool:
        """Check lockout state based on repeated auth failures."""
        try:
            with self._containment_conn() as conn:
                cutoff = now - max(self.auth_lockout_sec, 1)
                row = conn.execute(
                    """
                    SELECT COUNT(*) AS cnt, MAX(failed_at) AS last_failed
                    FROM auth_failures
                    WHERE failed_at >= ?
                      AND (requested_by = ? OR session_id = ?)
                    """,
                    (cutoff, requested_by, session_id),
                ).fetchone()
                failures = int(row["cnt"]) if row else 0
                last_failed = float(row["last_failed"]) if row and row["last_failed"] else 0.0
            if failures >= max(self.auth_failure_threshold, 1):
                if (now - last_failed) < max(self.auth_lockout_sec, 1):
                    return True
            return False
        except Exception as exc:
            logger.warning("[CORRELATOR] Lockout check failed: %s", exc)
            return True

    def _load_containment_state(self) -> None:
        """Load active containment state from sqlite store on startup."""
        now = time.time()
        try:
            with self._containment_conn() as conn:
                rows = conn.execute(
                    """
                    SELECT target_type, target_id, action, applied_at, expires_at, reason, incident_id
                    FROM containment_state
                    """
                ).fetchall()

                for row in rows:
                    if float(row["expires_at"]) <= now:
                        conn.execute(
                            "DELETE FROM containment_state WHERE target_type = ? AND target_id = ?",
                            (row["target_type"], row["target_id"]),
                        )
                        continue
                    try:
                        action = ContainmentAction(str(row["action"]))
                    except ValueError:
                        action = ContainmentAction.NONE
                    state = ContainmentState(
                        action=action,
                        applied_at=float(row["applied_at"]),
                        expires_at=float(row["expires_at"]),
                        reason=str(row["reason"]),
                        incident_id=str(row["incident_id"]),
                    )
                    if row["target_type"] == "sender":
                        self._sender_containment[str(row["target_id"])] = state
                    else:
                        self._channel_containment[str(row["target_id"])] = state

                conn.commit()
        except Exception as exc:
            logger.warning("[CORRELATOR] Failed loading containment state: %s", exc)

    def _persist_containment_state(
        self, target_type: str, target_id: str, state: ContainmentState
    ) -> None:
        """Persist containment upsert to sqlite store."""
        try:
            with self._containment_conn() as conn:
                conn.execute(
                    """
                    INSERT INTO containment_state
                        (target_type, target_id, action, applied_at, expires_at, reason, incident_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(target_type, target_id) DO UPDATE SET
                        action = excluded.action,
                        applied_at = excluded.applied_at,
                        expires_at = excluded.expires_at,
                        reason = excluded.reason,
                        incident_id = excluded.incident_id
                    """,
                    (
                        target_type,
                        target_id,
                        state.action.value,
                        state.applied_at,
                        state.expires_at,
                        state.reason,
                        state.incident_id,
                    ),
                )
                conn.commit()
        except Exception as exc:
            logger.warning("[CORRELATOR] Failed persisting containment state: %s", exc)

    def _delete_containment_state(self, target_type: str, target_id: str) -> None:
        """Delete containment row from sqlite store."""
        try:
            with self._containment_conn() as conn:
                conn.execute(
                    "DELETE FROM containment_state WHERE target_type = ? AND target_id = ?",
                    (target_type, target_id),
                )
                conn.commit()
        except Exception as exc:
            logger.warning("[CORRELATOR] Failed deleting containment state: %s", exc)

    def ingest_event(self, event: SecurityEvent) -> Optional[Incident]:
        """
        Ingest a security event and check for incident threshold.

        Returns Incident if threshold crossed, None otherwise.
        """
        now = time.time()

        # Prune old events outside correlation window
        self._prune_old_events(now)

        # Add event to storage
        self._events.append(event)
        self._events_by_sender.setdefault(event.sender, []).append(event)
        self._events_by_channel.setdefault(event.channel, []).append(event)

        logger.debug(
            "[CORRELATOR] Ingested event: type=%s sender=%s channel=%s",
            event.event_type.value, event.sender, event.channel,
        )

        # Check thresholds
        return self._check_thresholds(event.sender, event.channel, now)

    def _prune_old_events(self, now: float) -> None:
        """Remove events outside correlation window."""
        cutoff = now - self.correlation_window_sec

        self._events = [e for e in self._events if e.timestamp > cutoff]

        for sender in list(self._events_by_sender.keys()):
            self._events_by_sender[sender] = [
                e for e in self._events_by_sender[sender] if e.timestamp > cutoff
            ]
            if not self._events_by_sender[sender]:
                del self._events_by_sender[sender]

        for channel in list(self._events_by_channel.keys()):
            self._events_by_channel[channel] = [
                e for e in self._events_by_channel[channel] if e.timestamp > cutoff
            ]
            if not self._events_by_channel[channel]:
                del self._events_by_channel[channel]

    def _check_thresholds(
        self, sender: str, channel: str, now: float
    ) -> Optional[Incident]:
        """Check if incident threshold is crossed."""
        sender_events = self._events_by_sender.get(sender, [])
        channel_events = self._events_by_channel.get(channel, [])

        # Check sender threshold
        if len(sender_events) >= self.incident_threshold:
            return self._create_incident(
                events=sender_events,
                policy_trigger=f"sender_threshold:{sender}",
                target_type="sender",
                target_id=sender,
                now=now,
            )

        # Check channel threshold
        if len(channel_events) >= self.incident_threshold:
            return self._create_incident(
                events=channel_events,
                policy_trigger=f"channel_threshold:{channel}",
                target_type="channel",
                target_id=channel,
                now=now,
            )

        return None

    def _create_incident(
        self,
        events: List[SecurityEvent],
        policy_trigger: str,
        target_type: str,
        target_id: str,
        now: float,
    ) -> Optional[Incident]:
        """Create incident from correlated events."""
        # Dedupe check
        dedupe_key = f"{policy_trigger}"
        last_incident = self._incident_dedupe.get(dedupe_key)
        if last_incident and (now - last_incident) < self.alert_dedupe_window_sec:
            self._dedupe_suppressions += 1
            logger.debug(
                "[CORRELATOR] Incident suppressed (dedupe): %s (total suppressed: %d)",
                dedupe_key, self._dedupe_suppressions,
            )
            return None

        self._incident_dedupe[dedupe_key] = now

        # Calculate severity based on event mix
        severity = self._calculate_severity(events)

        # Determine containment action
        containment = self._determine_containment(target_type, severity)

        incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
        event_counts = {}
        for e in events:
            event_counts[e.event_type.value] = event_counts.get(e.event_type.value, 0) + 1

        incident = Incident(
            incident_id=incident_id,
            severity=severity,
            first_seen=min(e.timestamp for e in events),
            last_seen=max(e.timestamp for e in events),
            event_counts=event_counts,
            events=list(events),
            containment=containment,
            policy_trigger=policy_trigger,
            status="open",
        )

        self._incidents[incident_id] = incident

        # Apply containment if enabled
        if self.containment_enabled and containment != ContainmentAction.NONE:
            self._apply_containment(target_type, target_id, containment, incident_id, now)

        # Log incident signal
        logger.warning(
            "[DAEMON][OPENCLAW-INCIDENT] event=openclaw_incident_alert "
            "incident_id=%s severity=%s policy=%s event_counts=%s containment=%s",
            incident_id,
            severity.value,
            policy_trigger,
            json.dumps(event_counts),
            containment.value if containment else "none",
        )

        # Persist to JSONL
        self._persist_incident(incident)

        return incident

    def _calculate_severity(self, events: List[SecurityEvent]) -> IncidentSeverity:
        """Calculate incident severity based on event composition."""
        has_security_alert = any(
            e.event_type == EventType.SECURITY_ALERT for e in events
        )
        has_permission_denied = any(
            e.event_type == EventType.PERMISSION_DENIED for e in events
        )
        event_count = len(events)

        if has_security_alert and event_count >= 10:
            return IncidentSeverity.CRITICAL
        if has_security_alert or (has_permission_denied and event_count >= 5):
            return IncidentSeverity.HIGH
        if event_count >= self.incident_threshold * 2:
            return IncidentSeverity.MEDIUM
        return IncidentSeverity.LOW

    def _determine_containment(
        self, target_type: str, severity: IncidentSeverity
    ) -> ContainmentAction:
        """Determine containment action based on severity."""
        if not self.containment_enabled:
            return ContainmentAction.NONE

        if severity == IncidentSeverity.CRITICAL:
            return ContainmentAction.ADVISORY_ONLY
        if severity in (IncidentSeverity.HIGH, IncidentSeverity.MEDIUM):
            if target_type == "sender":
                return ContainmentAction.MUTE_SENDER
            return ContainmentAction.MUTE_CHANNEL
        return ContainmentAction.NONE

    def _apply_containment(
        self,
        target_type: str,
        target_id: str,
        action: ContainmentAction,
        incident_id: str,
        now: float,
    ) -> None:
        """Apply containment action."""
        state = ContainmentState(
            action=action,
            applied_at=now,
            expires_at=now + self.containment_duration_sec,
            reason=f"Incident {incident_id}",
            incident_id=incident_id,
        )

        if target_type == "sender":
            self._sender_containment[target_id] = state
        else:
            self._channel_containment[target_id] = state
        self._persist_containment_state(target_type, target_id, state)

        logger.warning(
            "[DAEMON][OPENCLAW-CONTAINMENT] event=containment_applied "
            "target_type=%s target_id=%s action=%s incident_id=%s expires_at=%.0f",
            target_type, target_id, action.value, incident_id, state.expires_at,
        )

    def release_containment(self, target_type: str, target_id: str) -> bool:
        """Explicitly release containment for target."""
        containment_map = (
            self._sender_containment if target_type == "sender"
            else self._channel_containment
        )
        if target_id in containment_map:
            state = containment_map.pop(target_id)
            self._delete_containment_state(target_type, target_id)
            logger.warning(
                "[DAEMON][OPENCLAW-CONTAINMENT] event=containment_released "
                "target_type=%s target_id=%s action=%s incident_id=%s",
                target_type, target_id, state.action.value, state.incident_id,
            )
            return True
        self._delete_containment_state(target_type, target_id)
        return False

    def check_containment(self, sender: str, channel: str) -> Optional[ContainmentState]:
        """Check if sender or channel is under containment."""
        now = time.time()

        # Check sender containment
        if sender in self._sender_containment:
            state = self._sender_containment[sender]
            if state.is_active():
                return state
            else:
                # Auto-expire
                self._sender_containment.pop(sender)
                self._delete_containment_state("sender", sender)
                logger.info(
                    "[DAEMON][OPENCLAW-CONTAINMENT] event=containment_expired "
                    "target_type=sender target_id=%s", sender
                )

        # Check channel containment
        if channel in self._channel_containment:
            state = self._channel_containment[channel]
            if state.is_active():
                return state
            else:
                self._channel_containment.pop(channel)
                self._delete_containment_state("channel", channel)
                logger.info(
                    "[DAEMON][OPENCLAW-CONTAINMENT] event=containment_expired "
                    "target_type=channel target_id=%s", channel
                )

        return None

    def is_advisory_only_mode(self) -> bool:
        """Check if global advisory-only mode is active."""
        for state in self._sender_containment.values():
            if state.is_active() and state.action == ContainmentAction.ADVISORY_ONLY:
                return True
        for state in self._channel_containment.values():
            if state.is_active() and state.action == ContainmentAction.ADVISORY_ONLY:
                return True
        return False

    def _persist_incident(self, incident: Incident) -> None:
        """Persist incident to JSONL log."""
        try:
            with open(self.incidents_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(incident.to_dict()) + "\n")
        except Exception as exc:
            logger.warning("[CORRELATOR] Failed to persist incident: %s", exc)

    def close_incident(self, incident_id: str) -> bool:
        """Close an incident."""
        if incident_id in self._incidents:
            self._incidents[incident_id].status = "closed"
            logger.warning(
                "[DAEMON][OPENCLAW-INCIDENT] event=incident_closed incident_id=%s",
                incident_id,
            )
            return True
        return False

    def export_bundle(self, incident_id: str) -> Optional[Path]:
        """
        Export forensic bundle for incident.

        Returns path to bundle file, or None if incident not found.
        """
        incident = self._incidents.get(incident_id)
        if not incident:
            return None

        bundle = self._build_bundle(incident)
        bundle_path = self.bundles_dir / f"{incident_id}.json"

        try:
            with open(bundle_path, "w", encoding="utf-8") as f:
                json.dump(bundle, f, indent=2)
            logger.info(
                "[CORRELATOR] Exported bundle for %s to %s",
                incident_id, bundle_path,
            )
            return bundle_path
        except Exception as exc:
            logger.error("[CORRELATOR] Failed to export bundle: %s", exc)
            return None

    def _build_bundle(self, incident: Incident) -> Dict[str, Any]:
        """Build forensic bundle for incident."""
        # Environment snapshot (safe, no secrets)
        safe_env = {
            "OPENCLAW_CORRELATION_WINDOW_SEC": self.correlation_window_sec,
            "OPENCLAW_INCIDENT_THRESHOLD": self.incident_threshold,
            "OPENCLAW_CONTAINMENT_ENABLED": self.containment_enabled,
            "OPENCLAW_CONTAINMENT_DURATION_SEC": self.containment_duration_sec,
        }

        # Containment actions taken
        containment_actions = []
        for target_id, state in self._sender_containment.items():
            if state.incident_id == incident.incident_id:
                containment_actions.append({
                    "target_type": "sender",
                    "target_id": target_id,
                    **state.to_dict(),
                })
        for target_id, state in self._channel_containment.items():
            if state.incident_id == incident.incident_id:
                containment_actions.append({
                    "target_type": "channel",
                    "target_id": target_id,
                    **state.to_dict(),
                })

        return {
            "bundle_version": "1.0",
            "exported_at": time.time(),
            "incident": incident.to_dict(),
            "containment_actions": containment_actions,
            "environment": safe_env,
            "log_pointers": {
                "incidents_log": str(self.incidents_log),
                "security_alerts_log": str(
                    self.repo_root
                    / "modules/ai_intelligence/ai_overseer/memory/openclaw_security_alerts.jsonl"
                ),
            },
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get correlator statistics."""
        now = time.time()
        active_sender_containments = sum(
            1 for s in self._sender_containment.values() if s.is_active()
        )
        active_channel_containments = sum(
            1 for s in self._channel_containment.values() if s.is_active()
        )

        return {
            "events_in_window": len(self._events),
            "correlation_window_sec": self.correlation_window_sec,
            "incident_threshold": self.incident_threshold,
            "open_incidents": sum(
                1 for i in self._incidents.values() if i.status == "open"
            ),
            "total_incidents": len(self._incidents),
            "active_sender_containments": active_sender_containments,
            "active_channel_containments": active_channel_containments,
            "dedupe_suppressions": self._dedupe_suppressions,
            "containment_enabled": self.containment_enabled,
            "consistency_errors": len(self._consistency_errors),
            "notification_attempts": self._notification_attempts,
            "notification_successes": self._notification_successes,
            "notification_failures": self._notification_failures,
            "notification_retries": self._notification_retries,
            "release_rate_limit_count": self.release_rate_limit_count,
            "release_rate_limit_window_sec": self.release_rate_limit_window_sec,
            "auth_failure_threshold": self.auth_failure_threshold,
            "auth_lockout_sec": self.auth_lockout_sec,
        }

    # -------------------------------------------------------------------------
    # Tranche 5: Authenticated Release, Audit, Consistency, Notifications
    # -------------------------------------------------------------------------

    def _run_consistency_check(self) -> None:
        """
        Cross-process consistency check on startup.

        Detects stale DB vs in-memory containment mismatches.
        WSP 95: Fail-closed - log errors but don't crash.
        """
        self._consistency_errors = []
        try:
            with self._containment_conn() as conn:
                rows = conn.execute(
                    "SELECT target_type, target_id, expires_at FROM containment_state"
                ).fetchall()

                db_keys: Set[tuple] = set()
                now = time.time()

                for row in rows:
                    key = (str(row["target_type"]), str(row["target_id"]))
                    db_keys.add(key)
                    expires_at = float(row["expires_at"])

                    # Check if DB has expired entries that weren't cleaned
                    if expires_at <= now:
                        self._consistency_errors.append(
                            f"stale_db_entry:{key[0]}:{key[1]}"
                        )

                # Check memory vs DB
                memory_senders = set(("sender", k) for k in self._sender_containment.keys())
                memory_channels = set(("channel", k) for k in self._channel_containment.keys())
                memory_keys = memory_senders | memory_channels

                # DB has entries not in memory (could be from another process)
                orphan_db = db_keys - memory_keys
                for key in orphan_db:
                    if key not in [
                        (str(r["target_type"]), str(r["target_id"]))
                        for r in rows
                        if float(r["expires_at"]) <= now
                    ]:
                        # Active in DB but not in memory - potential cross-process state
                        logger.info(
                            "[CORRELATOR] Consistency: loaded %s:%s from DB (cross-process)",
                            key[0], key[1]
                        )

                if self._consistency_errors:
                    logger.warning(
                        "[DAEMON][OPENCLAW-CONSISTENCY] event=consistency_check "
                        "errors=%d details=%s",
                        len(self._consistency_errors),
                        json.dumps(self._consistency_errors[:5]),  # Limit log size
                    )
                else:
                    logger.info(
                        "[DAEMON][OPENCLAW-CONSISTENCY] event=consistency_check errors=0"
                    )

        except Exception as exc:
            self._consistency_errors.append(f"db_error:{exc}")
            logger.warning("[CORRELATOR] Consistency check failed: %s", exc)

    def _validate_operator_token(self, provided_token: str) -> tuple[bool, str]:
        """
        Validate operator token for authenticated release.

        WSP 71: Token validation without timing side-channel.
        """
        if not self.operator_token and not self.operator_token_previous:
            logger.warning(
                "[DAEMON][OPENCLAW-AUTH] event=auth_failed reason=no_token_configured"
            )
            return False, "token_not_configured"

        # Constant-time comparison to prevent timing attacks
        import hmac
        if self.operator_token and hmac.compare_digest(
            provided_token.encode("utf-8"),
            self.operator_token.encode("utf-8"),
        ):
            return True, "token"
        if self.operator_token_previous and hmac.compare_digest(
            provided_token.encode("utf-8"),
            self.operator_token_previous.encode("utf-8"),
        ):
            logger.warning(
                "[DAEMON][OPENCLAW-AUTH] event=token_rotation_legacy_token_used"
            )
            return True, "token_previous"

        logger.warning(
            "[DAEMON][OPENCLAW-AUTH] event=auth_failed reason=invalid_token"
        )
        return False, "token_failed"

    def _check_replay(self, nonce: str) -> bool:
        """
        Check if nonce was already used (replay prevention).

        Returns True if nonce is fresh (not replayed), False if replay detected.
        """
        if not nonce:
            return False  # Missing nonce = reject

        now = time.time()
        self._prune_used_nonces(now)

        # Check memory first
        if nonce in self._used_nonces:
            logger.warning(
                "[DAEMON][OPENCLAW-AUTH] event=replay_detected nonce=%s",
                nonce[:8] + "...",
            )
            return False

        # Check DB for cross-process replay detection
        try:
            with self._containment_conn() as conn:
                # Check if nonce exists
                row = conn.execute(
                    "SELECT nonce FROM used_nonces WHERE nonce = ?",
                    (nonce,)
                ).fetchone()

                if row:
                    logger.warning(
                        "[DAEMON][OPENCLAW-AUTH] event=replay_detected_db nonce=%s",
                        nonce[:8] + "...",
                    )
                    return False

                # Record nonce
                conn.execute(
                    "INSERT INTO used_nonces (nonce, used_at) VALUES (?, ?)",
                    (nonce, now)
                )
                conn.commit()

        except Exception as exc:
            logger.warning("[CORRELATOR] Nonce DB check failed: %s", exc)
            # Fail-closed: treat as replay on DB error
            return False

        # Record in memory
        self._used_nonces[nonce] = now
        return True

    def release_containment_authenticated(
        self,
        target_type: str,
        target_id: str,
        token: str,
        nonce: str,
        requested_by: str,
        reason: str,
        source_ip: str = "unknown",
        session_id: str = "",
    ) -> Dict[str, Any]:
        """
        Authenticated containment release with full audit trail.

        Args:
            target_type: "sender" or "channel"
            target_id: The sender/channel ID to release
            token: Operator authentication token
            nonce: Unique request nonce for replay prevention
            requested_by: Operator identifier
            reason: Reason for release
            source_ip: Source IP of request
            session_id: Session identifier

        Returns:
            Dict with success status and details.
        """
        release_id = f"REL-{uuid.uuid4().hex[:8].upper()}"
        now = time.time()
        self._run_housekeeping(now)

        # Always record attempt for abuse controls.
        self._record_release_attempt(requested_by, session_id, now)
        if self._is_rate_limited(requested_by, session_id, now):
            record = ReleaseAuditRecord(
                release_id=release_id,
                target_type=target_type,
                target_id=target_id,
                requested_by=requested_by,
                reason=reason,
                source_ip=source_ip,
                session_id=session_id,
                timestamp=now,
                success=False,
                auth_method="rate_limited",
            )
            self._persist_audit_record(record)
            logger.warning(
                "[DAEMON][OPENCLAW-AUTH] event=rate_limited requested_by=%s session_id=%s",
                requested_by,
                session_id,
            )
            return {
                "success": False,
                "error": "rate_limited",
                "release_id": release_id,
            }

        if self._is_locked_out(requested_by, session_id, now):
            record = ReleaseAuditRecord(
                release_id=release_id,
                target_type=target_type,
                target_id=target_id,
                requested_by=requested_by,
                reason=reason,
                source_ip=source_ip,
                session_id=session_id,
                timestamp=now,
                success=False,
                auth_method="locked_out",
            )
            self._persist_audit_record(record)
            logger.warning(
                "[DAEMON][OPENCLAW-AUTH] event=locked_out requested_by=%s session_id=%s",
                requested_by,
                session_id,
            )
            return {
                "success": False,
                "error": "locked_out",
                "release_id": release_id,
            }

        # Step 1: Validate token
        token_ok, token_method = self._validate_operator_token(token)
        if not token_ok:
            self._record_auth_failure(requested_by, session_id, now)
            record = ReleaseAuditRecord(
                release_id=release_id,
                target_type=target_type,
                target_id=target_id,
                requested_by=requested_by,
                reason=reason,
                source_ip=source_ip,
                session_id=session_id,
                timestamp=now,
                success=False,
                auth_method=token_method,
            )
            self._persist_audit_record(record)
            return {
                "success": False,
                "error": "authentication_failed",
                "release_id": release_id,
            }

        # Step 2: Check replay
        if not self._check_replay(nonce):
            record = ReleaseAuditRecord(
                release_id=release_id,
                target_type=target_type,
                target_id=target_id,
                requested_by=requested_by,
                reason=reason,
                source_ip=source_ip,
                session_id=session_id,
                timestamp=now,
                success=False,
                auth_method="replay_detected",
            )
            self._persist_audit_record(record)
            return {
                "success": False,
                "error": "replay_detected",
                "release_id": release_id,
            }

        # Step 3: Perform release
        released = self.release_containment(target_type, target_id)

        record = ReleaseAuditRecord(
            release_id=release_id,
            target_type=target_type,
            target_id=target_id,
            requested_by=requested_by,
            reason=reason,
            source_ip=source_ip,
            session_id=session_id,
            timestamp=now,
            success=released,
            auth_method=token_method,
        )
        self._persist_audit_record(record)

        # Step 4: Dispatch notification
        if released:
            self._dispatch_notification(
                event_type="containment_released",
                severity=IncidentSeverity.MEDIUM,
                details={
                    "release_id": release_id,
                    "target_type": target_type,
                    "target_id": target_id,
                    "requested_by": requested_by,
                    "reason": reason,
                },
            )

        logger.warning(
            "[DAEMON][OPENCLAW-RELEASE] event=authenticated_release "
            "release_id=%s target=%s:%s success=%s requested_by=%s",
            release_id, target_type, target_id, released, requested_by,
        )

        return {
            "success": released,
            "release_id": release_id,
            "target_type": target_type,
            "target_id": target_id,
            "released_at": now if released else None,
        }

    def _persist_audit_record(self, record: ReleaseAuditRecord) -> None:
        """Persist audit record to JSONL and SQLite."""
        # JSONL append
        try:
            self.audit_log.parent.mkdir(parents=True, exist_ok=True)
            self._rotate_audit_jsonl_if_needed()
            with open(self.audit_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(record.to_dict()) + "\n")
        except Exception as exc:
            logger.warning("[CORRELATOR] Failed to persist audit to JSONL: %s", exc)

        # SQLite insert
        try:
            with self._containment_conn() as conn:
                conn.execute(
                    """
                    INSERT INTO release_audit
                        (release_id, target_type, target_id, requested_by, reason,
                         source_ip, session_id, timestamp, success, auth_method)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.release_id,
                        record.target_type,
                        record.target_id,
                        record.requested_by,
                        record.reason,
                        record.source_ip,
                        record.session_id,
                        record.timestamp,
                        1 if record.success else 0,
                        record.auth_method,
                    ),
                )
                conn.commit()
        except Exception as exc:
            logger.warning("[CORRELATOR] Failed to persist audit to SQLite: %s", exc)

    def _dispatch_notification(
        self,
        event_type: str,
        severity: IncidentSeverity,
        details: Dict[str, Any],
    ) -> bool:
        """
        Dispatch notification to Discord/livechat with dedupe.

        Returns True if notification was sent, False if deduped or failed.
        """
        now = time.time()

        # Build dedupe key
        dedupe_key = f"{event_type}:{details.get('target_type', '')}:{details.get('target_id', '')}"

        # Check dedupe
        last_sent = self._notification_history.get(dedupe_key)
        if last_sent and (now - last_sent) < self.notification_dedupe_sec:
            logger.debug(
                "[CORRELATOR] Notification deduped: %s (sent %.0fs ago)",
                dedupe_key, now - last_sent,
            )
            return False

        # Record send time
        self._notification_history[dedupe_key] = now

        # Dispatch to Discord if configured
        discord_ok = True
        if self.discord_webhook_url:
            self._notification_attempts += 1
            discord_ok = self._send_discord_notification_with_retry(
                event_type, severity, details
            )
            if discord_ok:
                self._notification_successes += 1
            else:
                self._notification_failures += 1

        # Dispatch to livechat
        try:
            self._send_livechat_notification(event_type, severity, details)
        except Exception as exc:
            logger.warning("[CORRELATOR] Livechat notification failed: %s", exc)
            if not self.discord_webhook_url:
                return False

        return discord_ok

    def _send_discord_notification(
        self,
        event_type: str,
        severity: IncidentSeverity,
        details: Dict[str, Any],
    ) -> bool:
        """Send notification to Discord webhook. Returns True on success."""
        import urllib.request
        import urllib.error

        # Severity to color mapping
        colors = {
            IncidentSeverity.LOW: 0x3498DB,      # Blue
            IncidentSeverity.MEDIUM: 0xF39C12,   # Orange
            IncidentSeverity.HIGH: 0xE74C3C,     # Red
            IncidentSeverity.CRITICAL: 0x9B59B6, # Purple
        }

        # Build embed
        embed = {
            "title": f"🔒 OpenClaw: {event_type.replace('_', ' ').title()}",
            "color": colors.get(severity, 0x95A5A6),
            "fields": [
                {"name": k.replace("_", " ").title(), "value": str(v), "inline": True}
                for k, v in details.items()
            ],
            "footer": {"text": f"Severity: {severity.value.upper()}"},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

        payload = json.dumps({"embeds": [embed]}).encode("utf-8")

        req = urllib.request.Request(
            self.discord_webhook_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status not in (200, 204):
                    logger.warning(
                        "[CORRELATOR] Discord webhook returned %d", resp.status
                    )
                    return False
            return True
        except urllib.error.URLError as exc:
            logger.warning("[CORRELATOR] Discord webhook error: %s", exc)
            return False

    def _send_discord_notification_with_retry(
        self,
        event_type: str,
        severity: IncidentSeverity,
        details: Dict[str, Any],
    ) -> bool:
        """Send Discord notification with bounded retry/backoff."""
        max_attempts = max(self.notification_retry_max, 1)
        backoff = max(self.notification_retry_backoff_sec, 0)
        for attempt in range(1, max_attempts + 1):
            if self._send_discord_notification(event_type, severity, details):
                return True
            if attempt < max_attempts:
                self._notification_retries += 1
                sleep_sec = min(backoff * (2 ** (attempt - 1)), 5)
                if sleep_sec > 0:
                    time.sleep(sleep_sec)
        return False

    def _send_livechat_notification(
        self,
        event_type: str,
        severity: IncidentSeverity,
        details: Dict[str, Any],
    ) -> None:
        """
        Send notification to livechat via DAEmon signal.

        Livechat integration picks up structured log signals.
        """
        logger.warning(
            "[DAEMON][OPENCLAW-NOTIFY] event=%s severity=%s details=%s",
            event_type,
            severity.value,
            json.dumps(details),
        )

    def dispatch_incident_notification(self, incident: Incident) -> bool:
        """Dispatch notification for new incident."""
        return self._dispatch_notification(
            event_type="incident_created",
            severity=incident.severity,
            details={
                "incident_id": incident.incident_id,
                "policy_trigger": incident.policy_trigger,
                "event_counts": json.dumps(incident.event_counts),
                "containment": incident.containment.value if incident.containment else "none",
            },
        )

    def get_audit_records(
        self, limit: int = 100, target_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve audit records from SQLite."""
        try:
            with self._containment_conn() as conn:
                if target_id:
                    rows = conn.execute(
                        """
                        SELECT * FROM release_audit
                        WHERE target_id = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                        """,
                        (target_id, limit),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        """
                        SELECT * FROM release_audit
                        ORDER BY timestamp DESC
                        LIMIT ?
                        """,
                        (limit,),
                    ).fetchall()

                return [dict(row) for row in rows]
        except Exception as exc:
            logger.warning("[CORRELATOR] Failed to retrieve audit records: %s", exc)
            return []
