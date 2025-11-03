# FoundUps Vision DAE - Public Interface Specification

**Module**: `modules.infrastructure.dae_infrastructure.foundups_vision_dae`
**WSP Compliance**: WSP 49 (Module Structure), WSP 11 (Interface Definition)
**Version**: 0.1.1
**Status**: Active Development

---

## Overview

FoundUps Vision DAE is an asynchronous daemon that orchestrates multi-modal signal capture for Gemma/Qwen pattern learning. It aggregates browser telemetry, desktop activity, and (optionally) voice triggers into structured JSONL sessions and SQLite persistence.

## Public API

### Core Classes

#### `FoundUpsVisionDAE`

Primary daemon class extending `BaseDAE` for vision signal orchestration.

**Constructor**:
```python
FoundUpsVisionDAE(
    telemetry_store: Optional[TelemetryStore] = None,
    summary_dir: Optional[Path] = None,
    ui_tars_inbox: Optional[Path] = None
) -> None
```

**Parameters**:
- `telemetry_store` (optional): SQLite telemetry store instance (defaults to TelemetryStore with default DB)
- `summary_dir` (optional): Directory for run history summaries (defaults to `docs/session_backups/foundups_vision_dae/run_history`)
- `ui_tars_inbox` (optional): UI-TARS telemetry inbox path (defaults to `E:/HoloIndex/models/ui-tars-1.5/telemetry/inbox`)

**Methods**:

##### `async run(*, enable_voice: bool = False) -> None`
Start the Vision DAE with configurable voice listener.

**Parameters**:
- `enable_voice` (keyword-only): Enable voice listener worker (default: False)

**Behavior**:
- Spawns 3-4 async workers (browser telemetry, session batching, summary reporting, optional voice)
- Tails `logs/foundups_browser_events.log` for Selenium telemetry
- Aggregates events into 50-event JSONL bundles at `holo_index/telemetry/vision_dae/vision_session_*.jsonl`
- Monitors SQLite `selenium_sessions` table for new entries
- Generates run history summaries every 5 seconds using `SeleniumRunHistoryMission`
- Dispatches summaries to UI-TARS inbox and archive directory

**Raises**:
- Worker exceptions propagated if any worker fails prematurely

**Example**:
```python
from modules.infrastructure.dae_infrastructure.foundups_vision_dae.src.vision_dae import FoundUpsVisionDAE

dae = FoundUpsVisionDAE()
await dae.run(enable_voice=False)  # Run without voice listener
```

##### `stop() -> None`
Signal all workers to gracefully shut down.

**Behavior**:
- Sets internal stop event
- Cancels all active async workers
- Waits for worker cleanup completion

**Example**:
```python
dae = FoundUpsVisionDAE()
try:
    await dae.run()
except KeyboardInterrupt:
    dae.stop()  # Graceful shutdown
```

---

#### `VisionTelemetryReporter`

Utility class for persisting run history summaries and dispatching to UI-TARS.

**Constructor**:
```python
VisionTelemetryReporter(
    summary_dir: Path,
    ui_tars_inbox: Optional[Path] = None
) -> None
```

**Parameters**:
- `summary_dir`: Directory for summary snapshots (creates if missing)
- `ui_tars_inbox` (optional): UI-TARS inbox path (None disables dispatch)

**Methods**:

##### `persist_summary(summary: Dict[str, Any]) -> Path`
Write summary to `latest_run_history.json` and timestamped archive.

**Parameters**:
- `summary`: Dictionary containing run history data

**Returns**:
- `Path`: Archive file path (`run_history_YYYYMMDD_HHMMSS.json`)

**Example**:
```python
reporter = VisionTelemetryReporter(Path("./summaries"))
archive_path = reporter.persist_summary({
    "mission": "selenium_run_history",
    "raw_session_count": 42,
    "summary_ready": True
})
```

##### `dispatch_to_ui_tars(summary: Dict[str, Any]) -> Optional[Path]`
Forward summary to UI-TARS inbox if configured.

**Parameters**:
- `summary`: Dictionary containing run history data

**Returns**:
- `Path`: Dispatched file path or `None` if inbox unavailable/failed

**Behavior**:
- Creates inbox directory if missing
- Writes timestamped `vision_summary_YYYYMMDD_HHMMSS.json`
- Failures logged as warnings (best-effort)

---

### Standalone Function

#### `async launch_vision_dae(enable_voice: bool = False) -> None`
Convenience launcher for CLI entry points and scripts.

**Parameters**:
- `enable_voice`: Enable voice listener worker (default: False)

**Behavior**:
- Instantiates `FoundUpsVisionDAE()` with default configuration
- Handles KeyboardInterrupt for graceful shutdown
- Logs startup and shutdown events

**Example**:
```python
import asyncio
from modules.infrastructure.dae_infrastructure.foundups_vision_dae.src.vision_dae import launch_vision_dae

# CLI entry point
asyncio.run(launch_vision_dae(enable_voice=False))
```

---

## Data Flow

### Input Sources

1. **Browser Telemetry Log**: `logs/foundups_browser_events.log`
   - Format: JSONL (one event per line)
   - Source: FoundUpsDriver observer hooks
   - Events: `init_*`, `connect_or_create_*`, `vision_analyze_*`, `post_to_*`

2. **SQLite Telemetry Store**: `data/foundups.db` (table: `selenium_sessions`)
   - Source: `telemetry_store.record_session()` calls from FoundUpsDriver
   - Polling: Every 5 seconds for new session IDs
   - Query: Last 100 sessions ordered by timestamp DESC

### Output Artifacts

1. **Session Bundles**: `holo_index/telemetry/vision_dae/vision_session_NNNNN.jsonl`
   - Format: JSONL (50 events per file)
   - Purpose: Gemma/Qwen batch processing inputs

2. **Run History Summaries**: `docs/session_backups/foundups_vision_dae/run_history/`
   - `latest_run_history.json`: Always-current snapshot
   - `run_history_YYYYMMDD_HHMMSS.json`: Timestamped archives
   - Content: `SeleniumRunHistoryMission` output (7-day aggregates)

3. **UI-TARS Dispatch**: `E:/HoloIndex/models/ui-tars-1.5/telemetry/inbox/`
   - `vision_summary_YYYYMMDD_HHMMSS.json`: Forwarded summaries
   - Purpose: UI-TARS worker consumption (future integration)

---

## Dependencies

### Internal Modules
- `modules.infrastructure.dae_infrastructure.base_dae.BaseDAE` (base class)
- `modules.infrastructure.foundups_selenium.src.telemetry_store.TelemetryStore` (SQLite storage)
- `holo_index.missions.selenium_run_history.SeleniumRunHistoryMission` (summary generation)

### External Libraries
- `asyncio`: Async/await orchestration
- `json`: Event serialization
- `logging`: Diagnostic output
- `pathlib`: Path manipulation

See `requirements.txt` for version specifications.

---

## Error Handling

### Graceful Degradation
- **Missing browser log**: Worker sleeps 1s and retries (does not crash)
- **Malformed JSONL**: Skips invalid lines with debug log
- **SQLite errors**: Logs warning, sleeps 5s, retries query
- **UI-TARS dispatch failure**: Logs warning, continues (best-effort)
- **Summary generation failure**: Returns error summary, continues monitoring

### Exception Propagation
- **Worker crashes**: Supervisor detects via `asyncio.wait()`, propagates exception, triggers shutdown
- **KeyboardInterrupt**: Caught by launcher, calls `stop()` for graceful cleanup

---

## Configuration

### Environment-Specific Paths

Defaults are optimized for Windows development environment:

| Path Type | Default | Override Method |
|-----------|---------|-----------------|
| Browser log | `logs/foundups_browser_events.log` | Hardcoded in `__init__` |
| Session output | `holo_index/telemetry/vision_dae/` | Hardcoded in `__init__` |
| Summary dir | `docs/session_backups/.../run_history/` | Constructor `summary_dir` param |
| UI-TARS inbox | `E:/HoloIndex/models/ui-tars-1.5/telemetry/inbox/` | Constructor `ui_tars_inbox` param |
| SQLite DB | `data/foundups.db` | Pass custom `TelemetryStore(db_path=...)` |

**Example Custom Configuration**:
```python
from pathlib import Path
from modules.infrastructure.foundups_selenium.src.telemetry_store import TelemetryStore

custom_store = TelemetryStore(db_path=Path("/custom/telemetry.db"))
dae = FoundUpsVisionDAE(
    telemetry_store=custom_store,
    summary_dir=Path("/custom/summaries"),
    ui_tars_inbox=Path("/custom/ui_tars_inbox")
)
```

---

## Vision Control Center

**Sprint 4: Interactive Menu Interface** (`scripts/menu.py`)

The Vision Control Center provides a centralized interactive menu for managing the Vision DAE daemon and accessing MCP endpoints:

```python
from modules.infrastructure.dae_infrastructure.foundups_vision_dae.scripts.menu import show_vision_control_center

# Launch from main.py option 8 or standalone
show_vision_control_center()
```

**Menu Options**:
1. Start Vision DAE Daemon - Launches `run_vision_dae()` with progress output
2. Stop Daemon / Show Worker Checkpoint State - Displays checkpoint (browser offset, batch index, session ID)
3. View Latest Summary - Formatted display of most recent run history
4. Stream Recent Events - Interactive JSONL event viewer with limit selection
5. Show UI-TARS Dispatch Log Directory - Browse dispatch audit trail
6. List Recent Summaries - Browse summary archive with metadata
7. Show Worker State (Detailed) - Full checkpoint file paths and status
8. Cleanup Old Files - Retention enforcement menu (30-day summaries, 14-day dispatches)
0. Return to Main Menu

**Features**:
- Real-time MCP endpoint access via `VisionMCPServer`
- User-friendly formatted output with emojis and progress indicators
- Interactive parameter input (event limits, cleanup options)
- Error handling with fallback messages
- Standalone mode support (`python menu.py`)

**Access**:
- Main menu option 8: "Vision DAE Control Center (Pattern Sensorium)"
- CLI flag: `python main.py --vision` (direct daemon launch, bypasses menu)
- Standalone: `python modules/infrastructure/dae_infrastructure/foundups_vision_dae/scripts/menu.py`

---

## Integration Points

### MCP Server Compatibility

**Sprint 3: Vision MCP Server** (`mcp/vision_mcp_server.py`)

The Vision DAE provides a dedicated MCP server for accessing telemetry summaries and worker state:

```python
from modules.infrastructure.dae_infrastructure.foundups_vision_dae.mcp.vision_mcp_server import VisionMCPServer, create_vision_mcp_app

# Standalone usage
server = VisionMCPServer()
latest = server.get_latest_summary()
summaries = server.list_recent_summaries(limit=10)
state = server.get_worker_state()

# FastMCP integration
app = create_vision_mcp_app()  # Ready for uvicorn deployment
```

**MCP Endpoints** (7 total):
- `get_latest_summary()` - Returns most recent run history summary
- `list_recent_summaries(limit=10)` - Lists recent summaries with metadata
- `stream_events(session_index=None, limit=50)` - Stream browser telemetry events from JSONL bundles (Sprint 4)
- `get_worker_state()` - Returns worker checkpoint (browser offset, batch index, last session ID)
- `update_worker_checkpoint()` - Updates worker resume state
- `cleanup_old_summaries(days_to_keep=30)` - Retention cleanup for summaries
- `cleanup_old_dispatches(days_to_keep=14)` - Retention cleanup for dispatches

**Other MCP Integration**:
- **MCP Browser Gateway**: JSONL session bundles for real-time stream
- **MCP Telemetry Server**: SQLite database queries via `TelemetryStore`
- **UI-TARS Desktop**: Inbox JSON summaries for agent context

### Gemma/Qwen Pattern Learning
- **Gemma 3 270M**: Fast classification of vision session bundles (50 events/batch)
- **Qwen 1.5B**: Strategic analysis of run history summaries (7-day aggregates)
- **HoloIndex**: Pattern storage in `holo_index/adaptive_learning/refactoring_patterns.json`

---

## Testing

**Unit Tests**:
- `tests/test_vision_reporter.py` - VisionTelemetryReporter (summary persistence, UI-TARS dispatch)
- `tests/test_vision_mcp_server.py` - Vision MCP Server (21/21 passing)
  - get_latest_summary endpoint
  - list_recent_summaries endpoint with pagination
  - Worker checkpoint get/update operations
  - Retention cleanup (30-day summaries, 14-day dispatches)
  - End-to-end integration workflows

**Integration Tests**: Full daemon lifecycle pending Sprint 4.

---

## WSP References

- **WSP 49**: Module Directory Structure (INTERFACE.md requirement)
- **WSP 11**: Interface Definition Protocol
- **WSP 72**: Module Independence (standalone SQLite, minimal coupling)
- **WSP 77**: Agent Coordination (Gemma/Qwen integration hooks)
- **WSP 80**: DAE Architecture (BaseDAE inheritance)
- **WSP 22**: Documentation (ModLog maintenance)

---

**Last Updated**: 2025-10-19 (Sprint 3 - MCP Interface Stub complete)
**Maintainer**: 0102 Infrastructure Team
**Status**: MVP - Sprint 3 MCP endpoints operational
