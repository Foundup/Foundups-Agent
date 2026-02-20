"""Centralized DAEmon Schemas — Layer 0.

Pure data definitions for the cardiovascular DAEmon system.
Zero external dependencies — only stdlib.

WSP Compliance:
    WSP 3: Infrastructure domain
    WSP 49: Standard module structure
    WSP 72: No cross-module imports (pure data)
"""

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class DAEState(Enum):
    """Lifecycle state of a Domain Autonomous Ecosystem."""
    REGISTERED = "registered"  # Known to registry, not started
    STARTING = "starting"      # Launch in progress
    RUNNING = "running"        # Active and healthy
    DEGRADED = "degraded"      # Running but missed heartbeats
    STOPPING = "stopping"      # Graceful shutdown in progress
    STOPPED = "stopped"        # Cleanly shut down
    DETACHED = "detached"      # Killswitch triggered — isolated
    CRASHED = "crashed"        # Unexpected termination


class DAEEventType(Enum):
    """Event types flowing through the cardiovascular system."""
    # Lifecycle
    DAE_REGISTERED = "dae_registered"
    DAE_STARTED = "dae_started"
    DAE_STOPPED = "dae_stopped"
    DAE_HEARTBEAT = "dae_heartbeat"
    DAE_STATE_CHANGED = "dae_state_changed"
    # Cardiovascular (message/action observation)
    MESSAGE_IN = "message_in"
    MESSAGE_OUT = "message_out"
    ACTION_PERFORMED = "action_performed"
    # Security
    SECURITY_VIOLATION = "security_violation"
    KILLSWITCH_TRIGGERED = "killswitch_triggered"
    DAE_DETACHED = "dae_detached"
    # System
    DAEMON_STARTED = "daemon_started"
    DAEMON_STOPPED = "daemon_stopped"
    DAEMON_HEARTBEAT = "daemon_heartbeat"


class SecuritySeverity(Enum):
    """Severity levels for security events."""
    INFO = "info"          # Logged only
    WARNING = "warning"    # Logged, counted
    HIGH = "high"          # Counted toward detach threshold
    CRITICAL = "critical"  # Immediate detach


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class DAERegistration:
    """Registration record for a DAE in the cardiovascular system."""
    dae_id: str                          # Unique slug (e.g. "fam_daemon")
    dae_name: str                        # Human name (e.g. "FAM DAEmon")
    domain: str                          # WSP 3 domain (e.g. "foundups")
    module_path: str = ""                # Python module path
    enabled: bool = True                 # Centralized on/off switch
    state: DAEState = DAEState.REGISTERED
    pid: Optional[int] = None            # OS process ID (if external)
    heartbeat_interval_sec: float = 60.0 # Expected heartbeat cadence
    last_heartbeat: float = 0.0          # time.time() of last heartbeat
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["state"] = self.state.value
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "DAERegistration":
        d = dict(d)  # shallow copy
        if isinstance(d.get("state"), str):
            d["state"] = DAEState(d["state"])
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class DAEEvent:
    """Single event flowing through the cardiovascular system.

    Mirrors the FAMEvent schema for consistency.
    Deterministic ID: sha256(type:dae_id:payload_hash:timestamp)[:16]
    """
    event_type: DAEEventType
    dae_id: str                          # Which DAE emitted this
    payload: Dict[str, Any] = field(default_factory=dict)
    actor_id: str = "central_daemon"     # Who triggered the event
    timestamp: float = 0.0              # Filled on creation
    event_id: str = ""                  # Deterministic hash
    sequence_id: int = 0                # Monotonic counter (set by store)
    dedupe_key: str = ""                # For idempotent writes

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
        if not self.event_id:
            self.event_id = self._generate_id()
        if not self.dedupe_key:
            self.dedupe_key = self.event_id

    def _generate_id(self) -> str:
        """Deterministic ID: sha256(type:dae_id:payload_hash:ts)[:16]."""
        payload_str = json.dumps(self.payload, sort_keys=True, default=str)
        payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()[:8]
        raw = f"{self.event_type.value}:{self.dae_id}:{payload_hash}:{self.timestamp}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "sequence_id": self.sequence_id,
            "dedupe_key": self.dedupe_key,
            "event_type": self.event_type.value,
            "dae_id": self.dae_id,
            "actor_id": self.actor_id,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "DAEEvent":
        d = dict(d)
        if isinstance(d.get("event_type"), str):
            d["event_type"] = DAEEventType(d["event_type"])
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class KillswitchReport:
    """Report generated when the killswitch detaches a DAE."""
    dae_id: str
    dae_name: str = ""
    reason: str = ""
    severity: SecuritySeverity = SecuritySeverity.CRITICAL
    triggering_event_ids: List[str] = field(default_factory=list)
    pid_terminated: Optional[int] = None
    pid_kill_success: bool = False
    timestamp: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["severity"] = self.severity.value
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "KillswitchReport":
        d = dict(d)
        if isinstance(d.get("severity"), str):
            d["severity"] = SecuritySeverity(d["severity"])
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
