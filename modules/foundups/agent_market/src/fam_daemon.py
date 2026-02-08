"""FAM DAEmon - Observability backbone for FoundUps Agent Market.

Provides:
- fam_event_v1 schema for all domain events
- Append-only JSONL sink + SQLite audit index
- Deterministic event IDs, sequence IDs, dedupe keys
- Replay-safe writes with idempotency
- Health/status API for Overseer polling
- Heartbeat runtime loop

WSP References:
- WSP 91: Observability standards
- WSP 5: Testing standards
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sqlite3
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================================
# fam_event_v1 Schema
# ============================================================================


class FAMEventType(str, Enum):
    """Canonical event types for FAM domain."""

    # Foundup lifecycle
    FOUNDUP_CREATED = "foundup_created"
    FOUNDUP_UPDATED = "foundup_updated"

    # Task lifecycle
    TASK_STATE_CHANGED = "task_state_changed"

    # Proof/verification
    PROOF_SUBMITTED = "proof_submitted"
    VERIFICATION_RECORDED = "verification_recorded"

    # Payout
    PAYOUT_TRIGGERED = "payout_triggered"

    # Distribution
    MILESTONE_PUBLISHED = "milestone_published"

    # Security (forwarded from Overseer)
    SECURITY_ALERT_FORWARDED = "security_alert_forwarded"
    INCIDENT_ALERT_FORWARDED = "incident_alert_forwarded"

    # System
    HEARTBEAT = "heartbeat"
    DAEMON_STARTED = "daemon_started"
    DAEMON_STOPPED = "daemon_stopped"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _generate_event_id(event_type: str, payload_hash: str, timestamp: str) -> str:
    """Generate deterministic event ID from content hash."""
    content = f"{event_type}:{payload_hash}:{timestamp}"
    return f"fam_ev_{hashlib.sha256(content.encode()).hexdigest()[:16]}"


def _generate_dedupe_key(event_type: str, payload: Dict[str, Any]) -> str:
    """Generate dedupe key for idempotent writes.

    Key components depend on event type:
    - task_state_changed: task_id + new_status
    - proof_submitted: proof_id
    - verification_recorded: verification_id
    - payout_triggered: payout_id
    - milestone_published: distribution_id
    - heartbeat: timestamp (allows one per second)
    - default: event_type + sorted payload hash
    """
    if event_type == FAMEventType.TASK_STATE_CHANGED.value:
        return f"task:{payload.get('task_id')}:{payload.get('new_status')}"
    elif event_type == FAMEventType.PROOF_SUBMITTED.value:
        return f"proof:{payload.get('proof_id')}"
    elif event_type == FAMEventType.VERIFICATION_RECORDED.value:
        return f"verification:{payload.get('verification_id')}"
    elif event_type == FAMEventType.PAYOUT_TRIGGERED.value:
        return f"payout:{payload.get('payout_id')}"
    elif event_type == FAMEventType.MILESTONE_PUBLISHED.value:
        return f"distribution:{payload.get('distribution_id')}"
    elif event_type == FAMEventType.HEARTBEAT.value:
        # Allow one heartbeat per second
        ts = payload.get("timestamp", "")[:19]  # Truncate to second
        return f"heartbeat:{ts}"
    else:
        # Default: hash the payload
        payload_str = json.dumps(payload, sort_keys=True)
        payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()[:12]
        return f"{event_type}:{payload_hash}"


@dataclass
class FAMEvent:
    """fam_event_v1 schema.

    All FAM domain events conform to this schema.
    """

    # Identity
    event_id: str
    sequence_id: int
    dedupe_key: str

    # Classification
    event_type: str
    schema_version: str = "fam_event_v1"

    # Context
    actor_id: str = "system"
    foundup_id: Optional[str] = None
    task_id: Optional[str] = None

    # Payload
    payload: Dict[str, Any] = field(default_factory=dict)

    # Timestamps
    timestamp: datetime = field(default_factory=_utc_now)
    recorded_at: datetime = field(default_factory=_utc_now)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for JSON storage."""
        return {
            "event_id": self.event_id,
            "sequence_id": self.sequence_id,
            "dedupe_key": self.dedupe_key,
            "event_type": self.event_type,
            "schema_version": self.schema_version,
            "actor_id": self.actor_id,
            "foundup_id": self.foundup_id,
            "task_id": self.task_id,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "recorded_at": self.recorded_at.isoformat(),
        }

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FAMEvent":
        """Deserialize from dict."""
        return cls(
            event_id=data["event_id"],
            sequence_id=data["sequence_id"],
            dedupe_key=data["dedupe_key"],
            event_type=data["event_type"],
            schema_version=data.get("schema_version", "fam_event_v1"),
            actor_id=data.get("actor_id", "system"),
            foundup_id=data.get("foundup_id"),
            task_id=data.get("task_id"),
            payload=data.get("payload", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            recorded_at=datetime.fromisoformat(data["recorded_at"]),
        )


# ============================================================================
# Persistence Layer (JSONL + SQLite)
# ============================================================================


class FAMEventStore:
    """Dual-write event store with JSONL sink and SQLite index.

    Features:
    - Append-only JSONL for disaster recovery
    - SQLite for fast querying and deduplication
    - Replay-safe with dedupe key enforcement
    - Atomic sequence ID generation
    """

    SQLITE_SCHEMA = """
    CREATE TABLE IF NOT EXISTS fam_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT UNIQUE NOT NULL,
        sequence_id INTEGER UNIQUE NOT NULL,
        dedupe_key TEXT UNIQUE NOT NULL,
        event_type TEXT NOT NULL,
        actor_id TEXT,
        foundup_id TEXT,
        task_id TEXT,
        payload_json TEXT,
        timestamp TEXT NOT NULL,
        recorded_at TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_fam_events_type ON fam_events(event_type);
    CREATE INDEX IF NOT EXISTS idx_fam_events_foundup ON fam_events(foundup_id);
    CREATE INDEX IF NOT EXISTS idx_fam_events_task ON fam_events(task_id);
    CREATE INDEX IF NOT EXISTS idx_fam_events_timestamp ON fam_events(timestamp);
    """

    def __init__(
        self,
        data_dir: Path,
        jsonl_filename: str = "fam_events.jsonl",
        sqlite_filename: str = "fam_audit.db",
    ) -> None:
        """Initialize event store.

        Args:
            data_dir: Directory for persistence files
            jsonl_filename: JSONL sink filename
            sqlite_filename: SQLite index filename
        """
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)

        self._jsonl_path = self._data_dir / jsonl_filename
        self._sqlite_path = self._data_dir / sqlite_filename

        self._lock = threading.Lock()
        self._sequence_counter = 0

        # Initialize SQLite
        self._init_sqlite()

        # Load sequence counter from SQLite
        self._load_sequence_counter()

        logger.info(
            "[FAM-STORE] Initialized | jsonl=%s sqlite=%s sequence=%d",
            self._jsonl_path,
            self._sqlite_path,
            self._sequence_counter,
        )

    def _init_sqlite(self) -> None:
        """Initialize SQLite schema."""
        with sqlite3.connect(str(self._sqlite_path)) as conn:
            conn.executescript(self.SQLITE_SCHEMA)
            conn.commit()

    def _load_sequence_counter(self) -> None:
        """Load max sequence ID from SQLite."""
        with sqlite3.connect(str(self._sqlite_path)) as conn:
            cursor = conn.execute("SELECT MAX(sequence_id) FROM fam_events")
            row = cursor.fetchone()
            if row and row[0] is not None:
                self._sequence_counter = row[0]

    def _next_sequence_id(self) -> int:
        """Get next sequence ID (thread-safe)."""
        self._sequence_counter += 1
        return self._sequence_counter

    def write(self, event: FAMEvent) -> Tuple[bool, str]:
        """Write event to both JSONL and SQLite.

        Returns:
            (success, message) tuple
        """
        with self._lock:
            try:
                # Check dedupe in SQLite
                if self._is_duplicate(event.dedupe_key):
                    return (False, f"duplicate: {event.dedupe_key}")

                # Assign sequence ID if not set
                if event.sequence_id == 0:
                    event.sequence_id = self._next_sequence_id()

                # Write to JSONL (append-only)
                self._write_jsonl(event)

                # Write to SQLite
                self._write_sqlite(event)

                logger.debug(
                    "[FAM-STORE] Written | seq=%d type=%s",
                    event.sequence_id,
                    event.event_type,
                )
                return (True, "ok")

            except Exception as e:
                logger.error("[FAM-STORE] Write failed: %s", e)
                return (False, f"error: {e}")

    def _is_duplicate(self, dedupe_key: str) -> bool:
        """Check if dedupe key exists in SQLite."""
        with sqlite3.connect(str(self._sqlite_path)) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM fam_events WHERE dedupe_key = ? LIMIT 1",
                (dedupe_key,),
            )
            return cursor.fetchone() is not None

    def _write_jsonl(self, event: FAMEvent) -> None:
        """Append event to JSONL file."""
        with open(self._jsonl_path, "a", encoding="utf-8") as f:
            f.write(event.to_json() + "\n")

    def _write_sqlite(self, event: FAMEvent) -> None:
        """Insert event into SQLite."""
        with sqlite3.connect(str(self._sqlite_path)) as conn:
            conn.execute(
                """
                INSERT INTO fam_events (
                    event_id, sequence_id, dedupe_key, event_type,
                    actor_id, foundup_id, task_id, payload_json,
                    timestamp, recorded_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.sequence_id,
                    event.dedupe_key,
                    event.event_type,
                    event.actor_id,
                    event.foundup_id,
                    event.task_id,
                    json.dumps(event.payload),
                    event.timestamp.isoformat(),
                    event.recorded_at.isoformat(),
                ),
            )
            conn.commit()

    def query(
        self,
        event_type: Optional[str] = None,
        foundup_id: Optional[str] = None,
        task_id: Optional[str] = None,
        since_sequence: int = 0,
        limit: int = 100,
    ) -> List[FAMEvent]:
        """Query events from SQLite.

        Args:
            event_type: Filter by event type
            foundup_id: Filter by foundup
            task_id: Filter by task
            since_sequence: Return events after this sequence ID
            limit: Max events to return

        Returns:
            List of FAMEvent objects
        """
        conditions = ["sequence_id > ?"]
        params: List[Any] = [since_sequence]

        if event_type:
            conditions.append("event_type = ?")
            params.append(event_type)
        if foundup_id:
            conditions.append("foundup_id = ?")
            params.append(foundup_id)
        if task_id:
            conditions.append("task_id = ?")
            params.append(task_id)

        where_clause = " AND ".join(conditions)
        params.append(limit)

        with sqlite3.connect(str(self._sqlite_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                f"""
                SELECT * FROM fam_events
                WHERE {where_clause}
                ORDER BY sequence_id ASC
                LIMIT ?
                """,
                tuple(params),
            )
            rows = cursor.fetchall()

        events = []
        for row in rows:
            events.append(
                FAMEvent(
                    event_id=row["event_id"],
                    sequence_id=row["sequence_id"],
                    dedupe_key=row["dedupe_key"],
                    event_type=row["event_type"],
                    actor_id=row["actor_id"] or "system",
                    foundup_id=row["foundup_id"],
                    task_id=row["task_id"],
                    payload=json.loads(row["payload_json"] or "{}"),
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    recorded_at=datetime.fromisoformat(row["recorded_at"]),
                )
            )
        return events

    def get_stats(self) -> Dict[str, Any]:
        """Get event store statistics."""
        with sqlite3.connect(str(self._sqlite_path)) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM fam_events")
            total = cursor.fetchone()[0]

            cursor = conn.execute(
                """
                SELECT event_type, COUNT(*) as cnt
                FROM fam_events
                GROUP BY event_type
                """
            )
            by_type = {row[0]: row[1] for row in cursor.fetchall()}

            cursor = conn.execute("SELECT MAX(sequence_id) FROM fam_events")
            max_seq = cursor.fetchone()[0] or 0

        return {
            "total_events": total,
            "max_sequence_id": max_seq,
            "events_by_type": by_type,
            "jsonl_path": str(self._jsonl_path),
            "sqlite_path": str(self._sqlite_path),
        }

    def verify_parity(self) -> Tuple[bool, str]:
        """Verify JSONL and SQLite are in sync.

        Returns:
            (ok, message) tuple
        """
        try:
            # Count JSONL lines
            jsonl_count = 0
            if self._jsonl_path.exists():
                with open(self._jsonl_path, "r", encoding="utf-8") as f:
                    jsonl_count = sum(1 for _ in f)

            # Count SQLite rows
            with sqlite3.connect(str(self._sqlite_path)) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM fam_events")
                sqlite_count = cursor.fetchone()[0]

            if jsonl_count == sqlite_count:
                return (True, f"parity ok: {jsonl_count} events")
            else:
                return (
                    False,
                    f"parity mismatch: jsonl={jsonl_count} sqlite={sqlite_count}",
                )

        except Exception as e:
            return (False, f"parity check failed: {e}")


# ============================================================================
# FAM DAEmon
# ============================================================================


@dataclass
class FAMDaemonHealth:
    """Health status for FAM DAEmon."""

    running: bool
    uptime_seconds: float
    heartbeat_count: int
    last_heartbeat: Optional[str]
    event_store_stats: Dict[str, Any]
    parity_ok: bool
    parity_message: str
    errors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FAMDaemon:
    """FAM DAEmon - observability backbone.

    Provides:
    - Event emission with fam_event_v1 schema
    - Heartbeat loop for liveness monitoring
    - Health/status API for Overseer polling
    - Automatic event persistence
    """

    def __init__(
        self,
        data_dir: Optional[Path] = None,
        heartbeat_interval_sec: float = 60.0,
        auto_start: bool = False,
    ) -> None:
        """Initialize FAM DAEmon.

        Args:
            data_dir: Directory for event persistence (default: module memory/)
            heartbeat_interval_sec: Heartbeat interval in seconds
            auto_start: Start heartbeat loop automatically
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "memory"

        self._data_dir = Path(data_dir)
        self._heartbeat_interval = heartbeat_interval_sec
        self._event_store = FAMEventStore(self._data_dir)

        # Runtime state
        self._running = False
        self._start_time: Optional[float] = None
        self._heartbeat_count = 0
        self._last_heartbeat: Optional[datetime] = None
        self._errors: List[str] = []
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Event listeners
        self._listeners: List[Callable[[FAMEvent], None]] = []

        if auto_start:
            self.start()

    def start(self) -> None:
        """Start the DAEmon heartbeat loop."""
        if self._running:
            return

        self._running = True
        self._start_time = time.time()
        self._stop_event.clear()

        # Emit daemon started event
        self.emit(
            event_type=FAMEventType.DAEMON_STARTED,
            payload={"heartbeat_interval_sec": self._heartbeat_interval},
        )

        # Start heartbeat thread
        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop, daemon=True
        )
        self._heartbeat_thread.start()

        logger.info("[FAM-DAEMON] Started | interval=%.1fs", self._heartbeat_interval)

    def stop(self) -> None:
        """Stop the DAEmon heartbeat loop."""
        if not self._running:
            return

        self._running = False
        self._stop_event.set()

        # Emit daemon stopped event
        self.emit(
            event_type=FAMEventType.DAEMON_STOPPED,
            payload={"uptime_seconds": self._get_uptime()},
        )

        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=2.0)

        logger.info("[FAM-DAEMON] Stopped")

    def _heartbeat_loop(self) -> None:
        """Background heartbeat loop."""
        while not self._stop_event.is_set():
            try:
                self._emit_heartbeat()
            except Exception as e:
                self._errors.append(f"heartbeat error: {e}")
                logger.error("[FAM-DAEMON] Heartbeat error: %s", e)

            self._stop_event.wait(self._heartbeat_interval)

    def _emit_heartbeat(self) -> None:
        """Emit a heartbeat event."""
        now = _utc_now()
        self._heartbeat_count += 1
        self._last_heartbeat = now

        self.emit(
            event_type=FAMEventType.HEARTBEAT,
            payload={
                "heartbeat_number": self._heartbeat_count,
                "uptime_seconds": self._get_uptime(),
                "timestamp": now.isoformat(),
            },
        )

    def _get_uptime(self) -> float:
        """Get daemon uptime in seconds."""
        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time

    def emit(
        self,
        event_type: FAMEventType | str,
        payload: Dict[str, Any],
        actor_id: str = "system",
        foundup_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """Emit a FAM event.

        Args:
            event_type: Event type (FAMEventType or string)
            payload: Event payload
            actor_id: Actor performing the action
            foundup_id: Optional foundup context
            task_id: Optional task context

        Returns:
            (success, message) tuple
        """
        # Normalize event type
        if isinstance(event_type, FAMEventType):
            event_type_str = event_type.value
        else:
            event_type_str = event_type

        now = _utc_now()

        # Generate deterministic IDs
        payload_str = json.dumps(payload, sort_keys=True)
        payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()[:12]
        event_id = _generate_event_id(event_type_str, payload_hash, now.isoformat())
        dedupe_key = _generate_dedupe_key(event_type_str, payload)

        event = FAMEvent(
            event_id=event_id,
            sequence_id=0,  # Will be assigned by store
            dedupe_key=dedupe_key,
            event_type=event_type_str,
            actor_id=actor_id,
            foundup_id=foundup_id,
            task_id=task_id,
            payload=payload,
            timestamp=now,
            recorded_at=now,
        )

        # Write to store
        success, message = self._event_store.write(event)

        if success:
            # Notify listeners
            for listener in self._listeners:
                try:
                    listener(event)
                except Exception as e:
                    logger.warning("[FAM-DAEMON] Listener error: %s", e)

        return (success, message)

    def add_listener(self, listener: Callable[[FAMEvent], None]) -> None:
        """Add event listener."""
        self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[FAMEvent], None]) -> None:
        """Remove event listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)

    def query_events(
        self,
        event_type: Optional[str] = None,
        foundup_id: Optional[str] = None,
        task_id: Optional[str] = None,
        since_sequence: int = 0,
        limit: int = 100,
    ) -> List[FAMEvent]:
        """Query events from the store."""
        return self._event_store.query(
            event_type=event_type,
            foundup_id=foundup_id,
            task_id=task_id,
            since_sequence=since_sequence,
            limit=limit,
        )

    def get_health(self) -> FAMDaemonHealth:
        """Get DAEmon health status for Overseer polling."""
        parity_ok, parity_message = self._event_store.verify_parity()

        return FAMDaemonHealth(
            running=self._running,
            uptime_seconds=self._get_uptime(),
            heartbeat_count=self._heartbeat_count,
            last_heartbeat=(
                self._last_heartbeat.isoformat() if self._last_heartbeat else None
            ),
            event_store_stats=self._event_store.get_stats(),
            parity_ok=parity_ok,
            parity_message=parity_message,
            errors=self._errors[-10:],  # Last 10 errors
        )

    def get_status(self) -> Dict[str, Any]:
        """Get status dict for API responses."""
        return self.get_health().to_dict()


# ============================================================================
# Module-level singleton
# ============================================================================

_daemon: Optional[FAMDaemon] = None


def get_fam_daemon(
    data_dir: Optional[Path] = None,
    auto_start: bool = True,
) -> FAMDaemon:
    """Get or create FAM DAEmon singleton.

    Args:
        data_dir: Optional data directory override
        auto_start: Auto-start heartbeat loop

    Returns:
        FAMDaemon instance
    """
    global _daemon
    if _daemon is None:
        _daemon = FAMDaemon(data_dir=data_dir, auto_start=auto_start)
    return _daemon
