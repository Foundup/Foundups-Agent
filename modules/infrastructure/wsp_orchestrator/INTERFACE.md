# WSP Orchestrator - Public API

## Main Class

### `WSPOrchestrator`

AI Overseer + Worker Bee architecture for modular "follow WSP"

#### Constructor

```python
WSPOrchestrator(repo_root: Path = Path("O:/Foundups-Agent"))
```

**Parameters**:
- `repo_root`: Repository root directory

#### Methods

### `follow_wsp(user_task: str, auto_execute: bool = False) -> Dict`

Main "follow WSP" entry point - AI Overseer orchestrates workers

**Parameters**:
- `user_task`: What the user wants to do (e.g., "create new module for X")
- `auto_execute`: If True, execute without approval prompts (default: False)

**Returns**:
```python
{
    "tasks_completed": int,
    "tasks_skipped": int,
    "errors": List[str],
    "success": bool,
    "outputs": List[Dict]
}
```

**Example**:
```python
from modules.infrastructure.wsp_orchestrator.src.wsp_orchestrator import WSPOrchestrator

orchestrator = WSPOrchestrator()

# Interactive mode (requires 0102 approval)
results = orchestrator.follow_wsp(
    user_task="implement YouTube trending analysis module",
    auto_execute=False
)

# Autonomous mode (no approval - use with caution!)
results = orchestrator.follow_wsp(
    user_task="update ModLog documentation",
    auto_execute=True
)
```

## Data Classes

### `WSPTask`

Single WSP compliance task

**Fields**:
- `task_type: str` - Type of task
- `description: str` - Human-readable description
- `wsp_references: List[str]` - Applicable WSP protocols
- `priority: str` - P0-P4 priority
- `requires_human_approval: bool` - 0102 supervision flag

### `WSPOrchestrationPlan`

Complete "follow WSP" execution plan

**Fields**:
- `tasks: List[WSPTask]` - All tasks to execute
- `estimated_time_ms: float` - Expected duration
- `worker_assignments: Dict[str, str]` - Task -> Worker mapping
- `mcp_tools_needed: List[str]` - Required MCP tools

## Standalone CLI

```bash
# Run as standalone script
python modules/infrastructure/wsp_orchestrator/src/wsp_orchestrator.py "your task here"

# Interactive mode
python modules/infrastructure/wsp_orchestrator/src/wsp_orchestrator.py
```

## Integration with Main.py (Future)

```python
# In main.py menu handler (option 15):
elif choice == "15":
    from modules.infrastructure.wsp_orchestrator.src.wsp_orchestrator import WSPOrchestrator
    orchestrator = WSPOrchestrator()

    task = input("Enter task: ")
    results = orchestrator.follow_wsp(task, auto_execute=False)

    print(f"\nCompleted: {results['tasks_completed']}")
    print(f"Success: {results['success']}")
```

## Worker Types

| Worker ID | Description | Speed | Use Case |
|-----------|-------------|-------|----------|
| MCP:HoloIndex | Semantic search via MCP | 100ms | Code discovery |
| MCP:WSP | WSP protocol lookup | 100ms | Compliance check |
| Gemma:PatternMatch | Fast classification | 50ms | Binary decisions |
| Qwen:Planning | Strategic analysis | 250ms | Deep planning |
| Rules:Grep | Regex/grep checks | 5ms | Simple validation |
| 0102:Supervision | Human oversight | Manual | Critical tasks |
