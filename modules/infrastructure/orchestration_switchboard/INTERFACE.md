# Orchestration Switchboard - Interface Specification

**Module**: `infrastructure/orchestration_switchboard`
**Version**: 1.0.0
**WSP Reference**: WSP 11 (Interface Protocol)

## Public API

### Classes

#### `OrchestrationSwitchboard`

Main coordination class that receives signals and decides HOLD or EXECUTE.

```python
class OrchestrationSwitchboard:
    def __init__(self, repo_root: Optional[Path] = None)
    def receive_signal(self, signal_type: str, source_dae: str, metadata: Optional[Dict] = None) -> SwitchboardDecision
    def execute_signal(self, signal: Signal) -> Dict[str, Any]
    def get_status(self) -> Dict[str, Any]
    def get_learning_stats(self) -> Dict[str, Any]
```

#### `Signal`

Dataclass representing an incoming signal.

```python
@dataclass
class Signal:
    signal_type: str           # Type of signal (e.g., "rotation_complete")
    source_dae: str            # Source DAE name
    priority: SignalPriority   # WSP 15 priority level
    metadata: Dict[str, Any]   # Optional context data
    timestamp: datetime        # When signal was received
    execution_id: str          # Unique execution identifier
```

#### `SwitchboardDecision`

Dataclass representing the switchboard's decision.

```python
@dataclass
class SwitchboardDecision:
    action: SignalAction           # EXECUTE, HOLD, ESCALATE, or DROP
    signal: Signal                 # The original signal
    reason: str                    # Human-readable reason
    recommended_browser: str       # "chrome" or "edge" (optional)
    queue_position: int           # Position in queue if HOLD (optional)
    metadata: Dict[str, Any]       # Additional context
```

### Enums

#### `SignalPriority`

WSP 15 MPS priority levels.

```python
class SignalPriority(Enum):
    P0_CRITICAL = 0   # OAuth, live stream - ALWAYS wins
    P1_HIGH = 1       # Comment processing, rotation
    P2_MEDIUM = 2     # Social notifications, scheduling
    P3_LOW = 3        # Indexing, maintenance
    P4_IDLE = 4       # Background tasks
```

#### `SignalAction`

Switchboard decision actions.

```python
class SignalAction(Enum):
    EXECUTE = "execute"       # Proceed with signal
    HOLD = "hold"             # Queue for later
    ESCALATE = "escalate"     # Requires 0102 attention
    DROP = "drop"             # Signal superseded or invalid
```

### Functions

#### `get_orchestration_switchboard()`

Get or create singleton switchboard instance.

```python
def get_orchestration_switchboard() -> OrchestrationSwitchboard
```

### Constants

#### `SIGNAL_PRIORITIES`

Mapping of signal types to priority levels.

```python
SIGNAL_PRIORITIES: Dict[str, SignalPriority] = {
    "oauth_reauth": SignalPriority.P0_CRITICAL,
    "live_stream_started": SignalPriority.P0_CRITICAL,
    "rotation_complete": SignalPriority.P1_HIGH,
    "linkedin_notification": SignalPriority.P2_MEDIUM,
    "video_indexing": SignalPriority.P3_LOW,
    # ... etc
}
```

## Usage Examples

### Basic Signal Handling

```python
from modules.infrastructure.orchestration_switchboard import (
    get_orchestration_switchboard,
    SignalAction
)

switchboard = get_orchestration_switchboard()

# Send a signal
decision = switchboard.receive_signal(
    signal_type="rotation_complete",
    source_dae="comment_engagement",
    metadata={"browser": "chrome"}
)

# Handle the decision
if decision.action == SignalAction.EXECUTE:
    result = switchboard.execute_signal(decision.signal)
    print(f"Executed: {result}")
elif decision.action == SignalAction.HOLD:
    print(f"Queued at position {decision.queue_position}")
```

### Adding Custom Signal Types

```python
from modules.infrastructure.orchestration_switchboard import (
    SIGNAL_PRIORITIES,
    SignalPriority
)

# Add new signal type
SIGNAL_PRIORITIES["my_custom_signal"] = SignalPriority.P2_MEDIUM
```

## Integration Contract

Modules integrating with the switchboard must:

1. Import `get_orchestration_switchboard()` to get singleton
2. Call `receive_signal()` with valid signal_type, source_dae
3. Check decision.action before proceeding
4. Handle both EXECUTE and HOLD cases

## Error Handling

The switchboard is designed to be fault-tolerant:

- Missing components (telemetry, router, etc.) are handled gracefully
- Unknown signal types default to P3_LOW priority
- Execution errors are caught and returned in result dict
- Queue processing continues even if individual signals fail
