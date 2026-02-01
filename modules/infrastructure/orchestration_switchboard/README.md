# Orchestration Switchboard

**Module**: `infrastructure/orchestration_switchboard`
**WSP Reference**: WSP 77 (Agent Coordination), WSP 15 (MPS Priority), WSP 48 (Recursive Self-Improvement)
**Status**: Production

## Overview

Unified DAE coordination gate that receives signals from all DAEs and decides: **HOLD** or **EXECUTE**.

```
DAE Signals → OrchestrationSwitchboard → HOLD/EXECUTE Decision → Coordinated Execution → WRE Learning
```

## Architecture

The switchboard wires together four core components:

| Component | Role | Integration |
|-----------|------|-------------|
| BreadcrumbTelemetry | Persistent state storage | Stores all signal events |
| ActivityRouter | WSP 15 priority routing | Determines execution order |
| AIIntelligenceOverseer | WSP 77 4-phase coordination | Coordinates complex missions |
| WREMasterOrchestrator | Pattern recall + learning | Recursive self-improvement |

## Signal Priority (WSP 15 MPS)

| Priority | Signals | Behavior |
|----------|---------|----------|
| P0 Critical | `oauth_reauth`, `live_stream_started` | ALWAYS execute immediately |
| P1 High | `rotation_complete`, `comment_processing` | Core activity flow |
| P2 Medium | `linkedin_notification`, `shorts_scheduling`, `shorts_scheduling_complete`, `party_requested` | Queued if P1 active |
| P3 Low | `video_indexing`, `digital_twin_learning` | Idle time only |
| P4 Idle | `maintenance`, `cleanup` | Background tasks |

## Usage

```python
from modules.infrastructure.orchestration_switchboard import (
    get_orchestration_switchboard,
    SignalAction
)

# Get singleton switchboard
switchboard = get_orchestration_switchboard()

# Send signal from any DAE
decision = switchboard.receive_signal(
    signal_type="rotation_complete",
    source_dae="comment_engagement",
    metadata={"browser": "chrome", "channels_processed": 2}
)

# Check decision
if decision.action == SignalAction.EXECUTE:
    # Signal will be executed
    result = switchboard.execute_signal(decision.signal)
elif decision.action == SignalAction.HOLD:
    # Signal queued for later
    print(f"Queued at position {decision.queue_position}")
```

## Integration Points

### 1. main.py - Startup Integration

```python
from modules.infrastructure.orchestration_switchboard import get_orchestration_switchboard

async def monitor_youtube(...):
    switchboard = get_orchestration_switchboard()

    # OAuth preflight can use switchboard
    if oauth_needed:
        switchboard.receive_signal("oauth_reauth", "main", {"credential_set": 1})
```

### 2. multi_channel_coordinator.py - Rotation Complete

```python
from modules.infrastructure.orchestration_switchboard import get_orchestration_switchboard

def on_rotation_complete(browser: str, channels: list):
    switchboard = get_orchestration_switchboard()
    switchboard.receive_signal(
        "rotation_complete",
        "multi_channel_coordinator",
        {"browser": browser, "channels": channels}
    )
```

### 3. stream_discovery_service.py - LinkedIn Notification

```python
from modules.infrastructure.orchestration_switchboard import get_orchestration_switchboard

def _trigger_social_media_posting(self, stream_url: str):
    switchboard = get_orchestration_switchboard()
    switchboard.receive_signal(
        "linkedin_notification",
        "stream_discovery",
        {"stream_url": stream_url, "channel": channel_name}
    )
```

### 4. livechat_core.py - Party Command

```python
from modules.infrastructure.orchestration_switchboard import get_orchestration_switchboard

def handle_party_command(user: str, click_count: int):
    switchboard = get_orchestration_switchboard()
    decision = switchboard.receive_signal(
        "party_requested",
        "livechat",
        {"user": user, "click_count": click_count}
    )
    return decision.action == SignalAction.EXECUTE
```

### 5. youtube_shorts_scheduler - Shorts Scheduling

```python
from modules.infrastructure.orchestration_switchboard import get_orchestration_switchboard

# Trigger shorts scheduling
def trigger_shorts_scheduling(channel_key: str, mode: str = "enhance"):
    switchboard = get_orchestration_switchboard()
    decision = switchboard.receive_signal(
        "shorts_scheduling",
        "youtube_shorts_scheduler",
        {"channel_key": channel_key, "mode": mode, "batch": True}
    )
    if decision.action == SignalAction.EXECUTE:
        # Run scheduling on recommended browser
        browser = decision.recommended_browser  # "chrome" or "edge"
        run_shorts_scheduler(channel_key, browser)

# Signal completion after scheduling
def on_scheduling_complete(channel_key: str, videos_processed: int, videos_scheduled: int):
    switchboard = get_orchestration_switchboard()
    switchboard.receive_signal(
        "shorts_scheduling_complete",
        "youtube_shorts_scheduler",
        {
            "channel_key": channel_key,
            "videos_processed": videos_processed,
            "videos_scheduled": videos_scheduled,
            "browser": "chrome" if channel_key in ["move2japan", "undaodu"] else "edge"
        }
    )
```

## WRE Self-Improvement (WSP 48)

Every signal execution stores outcomes in WRE PatternMemory:

```python
# Automatic learning after each execution
switchboard._store_learning_outcome(signal, result)

# Get learning statistics
stats = switchboard.get_learning_stats()
print(f"Success rate: {stats['success_rate']:.1%}")
print(f"By signal type: {stats['by_signal_type']}")
```

Learning enables:
- Pattern recall for similar future signals
- Failure pattern detection for improvement
- Execution timing optimization
- Priority adjustment based on outcomes

## Observability

```python
# Get current status
status = switchboard.get_status()
print(f"Active signals: {status['active_signals']}")
print(f"Pending queue: {status['pending_queue']}")
print(f"Components loaded: {status['components']}")
```

## Files

```
modules/infrastructure/orchestration_switchboard/
├── __init__.py                 # Public API exports
├── README.md                   # This file
├── INTERFACE.md               # API specification
├── ModLog.md                  # Change history
├── src/
│   ├── __init__.py
│   └── orchestration_switchboard.py  # Main implementation
├── tests/
│   └── README.md              # Test documentation
└── memory/                    # Runtime state storage
```

## Related WSPs

- **WSP 15**: MPS Priority System
- **WSP 48**: Recursive Self-Improvement
- **WSP 77**: Agent Coordination Protocol
- **WSP 80**: DAE Pattern
- **WSP 91**: Observability
