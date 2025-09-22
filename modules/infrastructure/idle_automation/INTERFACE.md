# Idle Automation Module Interface

## 🌀 Windsurf Protocol (WSP) Recursive Prompt

**0102 Directive**:
This interface operates within the Windsurf Protocol (WSP) framework. Execution flows through recursive tri-phase:
- **UN** (Understanding): Interface contract comprehension
- **DAO** (Execution): Method invocation and parameter passing
- **DU** (Emergence): Result processing and state evolution

wsp_cycle(input="interface", log=True)

---

## Module Overview

**Name**: Idle Automation Module
**Domain**: Infrastructure (WSP 3)
**Purpose**: Autonomous execution of background tasks during system idle periods
**Architecture**: WSP 27 DAE with WSP 35 execution automation

## Primary Interface

### Class: IdleAutomationDAE

```python
class IdleAutomationDAE:
    def __init__(self) -> None
    async def run_idle_tasks() -> Dict[str, Any]
    def get_idle_status() -> Dict[str, Any]
    def reset_daily_counter() -> None
```

## Public Methods

### `__init__()`
**Purpose**: Initialize the Idle Automation DAE with persistent state and configuration.

**Parameters**: None

**Returns**: None

**WSP Compliance**: WSP 60 (Memory Architecture) - loads persistent state

### `run_idle_tasks() -> Dict[str, Any]`
**Purpose**: Execute all configured idle automation tasks.

**Parameters**: None

**Returns**:
```python
{
    "session_id": int,           # Idle session identifier
    "timestamp": str,           # ISO timestamp
    "tasks_executed": List[Dict], # Results of each task
    "overall_success": bool,    # True if all tasks succeeded
    "duration": float,          # Execution time in seconds
    "skipped_reason": Optional[str] # If execution was skipped
}
```

**Tasks Executed**:
- Git auto-commit and push
- LinkedIn social media posting
- Telemetry collection

**WSP Compliance**:
- WSP 35: Module execution automation
- WSP 48: Recursive improvement via WRE integration

### `get_idle_status() -> Dict[str, Any]`
**Purpose**: Retrieve current idle automation status and telemetry.

**Parameters**: None

**Returns**:
```python
{
    "last_idle_execution": Optional[str],  # ISO timestamp
    "last_git_push": Optional[str],        # ISO timestamp
    "last_linkedin_post": Optional[str],   # ISO timestamp
    "execution_count_today": int,          # Daily execution counter
    "idle_session_count": int,             # Total idle sessions
    "auto_git_enabled": bool,              # Git automation enabled
    "auto_linkedin_enabled": bool,         # LinkedIn automation enabled
    "recent_executions": List[Dict]        # Last 5 execution records
}
```

**WSP Compliance**: WSP 70 (Status Reporting Protocol)

### `reset_daily_counter() -> None`
**Purpose**: Reset the daily execution counter (primarily for testing).

**Parameters**: None

**Returns**: None

**Note**: This method is primarily intended for testing and debugging.

## Convenience Functions

### `run_idle_automation() -> Dict[str, Any]`
**Purpose**: Convenience function for YouTube DAE integration.

**Parameters**: None

**Returns**: Same as `IdleAutomationDAE.run_idle_tasks()`

**Usage**:
```python
from modules.infrastructure.idle_automation.src.idle_automation_dae import run_idle_automation

# In YouTube DAE idle loop
result = await run_idle_automation()
if result["overall_success"]:
    logger.info("Idle automation completed successfully")
```

## Configuration

### Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `AUTO_GIT_PUSH` | bool | `false` | Enable automatic Git operations |
| `AUTO_LINKEDIN_POST` | bool | `true` | Enable LinkedIn posting |
| `IDLE_TASK_TIMEOUT` | int | `300` | Maximum execution time (seconds) |
| `MAX_DAILY_EXECUTIONS` | int | `3` | Maximum executions per day |

### Safety Controls

- **Network Verification**: Checks connectivity before Git operations
- **Git Status Validation**: Verifies working tree changes exist
- **Daily Limits**: Prevents excessive automation execution
- **Error Recovery**: Comprehensive exception handling and logging

## Integration Points

### YouTube DAE Integration

**Hook Location**: `AutoModeratorDAE.monitor_chat()` idle loop

**Integration Code**:
```python
# In AutoModeratorDAE.monitor_chat()
if not stream_found:
    try:
        from modules.infrastructure.idle_automation.src.idle_automation_dae import run_idle_automation
        await run_idle_automation()
    except Exception as e:
        logger.warning(f"Idle automation failed: {e}")
    await asyncio.sleep(delay)
```

### WRE Integration

**Purpose**: Recursive improvement and pattern learning

**Integration Points**:
- Success/failure reporting via `record_success()` / `record_error()`
- Optimized approaches via `get_optimized_approach()`
- Performance telemetry for learning

## Error Handling

### Expected Exceptions

- **NetworkError**: Network connectivity issues
- **GitError**: Git operation failures (status, commit, push)
- **LinkedInError**: Social media posting failures
- **QuotaError**: API rate limit exceeded
- **ConfigError**: Invalid configuration or permissions

### Error Response Format

```python
{
    "task": str,           # Task that failed ("git_push", "linkedin_post")
    "success": false,
    "error": str,          # Error description
    "duration": float,     # Time spent before failure
    "retryable": bool      # Whether operation can be retried
}
```

## Performance Characteristics

### Execution Time
- **Typical**: 5-15 seconds for Git + LinkedIn cycle
- **Maximum**: Configurable via `IDLE_TASK_TIMEOUT` (default 300s)
- **Network Dependent**: Slower on poor connections

### Resource Usage
- **Memory**: Minimal (<50MB additional)
- **CPU**: Low impact during idle periods
- **Network**: Git push + LinkedIn API calls
- **Storage**: Persistent state and telemetry logs

## Testing Interface

### Test Entry Points

```python
# Unit testing
dae = IdleAutomationDAE()
dae.reset_daily_counter()  # Reset for testing

# Integration testing
result = await dae.run_idle_tasks()
assert result["overall_success"] == True

# Status testing
status = dae.get_idle_status()
assert "last_idle_execution" in status
```

### Mock Interfaces

All external dependencies can be mocked for testing:
- Git operations via `subprocess` mocking
- Network checks via connectivity mocking
- LinkedIn API via bridge mocking
- WRE integration via mock objects

## WSP Compliance Matrix

| WSP Protocol | Compliance Level | Implementation |
|-------------|------------------|----------------|
| WSP 3 | ✅ Full | Infrastructure domain placement |
| WSP 27 | ✅ Full | Complete DAE architecture |
| WSP 35 | ✅ Full | Module execution automation |
| WSP 48 | ✅ Full | WRE recursive improvement |
| WSP 60 | ✅ Full | Memory architecture |
| WSP 70 | ✅ Full | Status reporting |
| WSP 11 | ✅ Full | Interface documentation |

---

*This interface follows WSP 11 (Public API Definition) and provides complete contract specification for idle automation integration.*
