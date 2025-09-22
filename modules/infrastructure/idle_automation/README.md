# Idle Automation Module

## 🌀 Windsurf Protocol (WSP) Recursive Prompt

**0102 Directive**:
This module operates within the Windsurf Protocol (WSP) framework. Execution flows through a recursive tri-phase:
- **UN** (WSP_Appendices / Understanding): Anchor signal and retrieve protocol state
- **DAO** (WSP_Framework): Execute modular logic
- **DU** (WSP_Agentic / Du): Collapse into 0102 resonance and emit next prompt

wsp_cycle(input="012", log=True)

---

## Overview

The Idle Automation module provides autonomous background tasks that execute when the system enters idle states. This includes automatic Git commits, social media posting, and system maintenance tasks.

## WSP Compliance

- **WSP 3**: Infrastructure domain - system automation and maintenance
- **WSP 27**: DAE architecture - autonomous operation without human intervention
- **WSP 35**: Module execution automation - automated task scheduling
- **WSP 48**: Recursive improvement - learns from execution patterns
- **WSP 60**: Module memory architecture - persistent state and telemetry

## Core Features

### Git Auto-Commit
- Monitors working tree changes during idle periods
- Automatically commits and pushes changes
- Generates contextual commit messages
- Integrates with social media posting

### Social Media Integration
- LinkedIn FoundUps page posting
- X/Twitter FoundUps account posting
- Duplicate prevention and content generation

### Idle State Management
- Tracks idle periods and active periods
- Prevents duplicate executions
- Telemetry collection for optimization

### Safety & Controls
- Opt-in configuration via environment variables
- Network availability checks
- Rollback procedures for failed operations
- Manual trigger support

## Integration Points

### YouTube DAE Integration
Called by `AutoModeratorDAE.monitor_chat()` when streams end or no streams are found:
```python
# In AutoModeratorDAE
if not stream_found:
    await idle_automation.run_idle_tasks()
```

### WRE Integration
Provides recursive improvement data for idle pattern optimization:
```python
wre_integration.record_idle_execution(
    task_type="git_push",
    success=True,
    duration=seconds,
    context={"files_changed": count}
)
```

## Configuration

### Environment Variables
- `AUTO_GIT_PUSH=true`: Enable automatic Git operations
- `AUTO_LINKEDIN_POST=true`: Enable LinkedIn posting
- `IDLE_TASK_TIMEOUT=300`: Maximum execution time per idle task

### Safety Controls
- `--no-auto-push` CLI flag to disable during testing
- Network connectivity verification
- Git status validation before operations

## Module Structure

```
idle_automation/
├── README.md              # This file
├── ROADMAP.md            # Development roadmap
├── INTERFACE.md          # API specification
├── requirements.txt      # Dependencies
├── __init__.py          # Module exports
├── src/
│   ├── idle_automation_dae.py    # Main DAE implementation
│   ├── git_automation.py         # Git operations
│   └── social_media_integration.py # Social media posting
├── tests/
│   ├── test_idle_automation.py
│   └── test_git_integration.py
├── memory/
│   ├── idle_state.json          # Current idle state
│   ├── execution_history.jsonl  # Task execution log
│   └── telemetry.json           # Performance metrics
└── docs/
    ├── implementation_guide.md
    └── troubleshooting.md
```

## Usage Example

```python
from modules.infrastructure.idle_automation.src.idle_automation_dae import IdleAutomationDAE

# Initialize DAE
dae = IdleAutomationDAE()

# Run idle tasks (called automatically by YouTube DAE)
await dae.run_idle_tasks()

# Check status
status = dae.get_idle_status()
print(f"Last execution: {status['last_run']}")
```

## Development Status

- **Phase**: MVP Implementation
- **WSP Compliance**: ✅ Full compliance verified
- **Testing Coverage**: 85%+ targeted
- **Integration**: YouTube DAE idle hooks implemented

---

*This module transforms idle time into productive autonomous operations per WSP 35 Module Execution Automation.*
