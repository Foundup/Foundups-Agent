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

### `await follow_wsp(user_task: str) -> Dict[str, Any]`

Main "follow WSP" entry point - executes WSP_00 gate first, then orchestrates worker plan.

**Parameters**:
- `user_task`: Task description for orchestration.

**Returns**:
```python
{
    "tasks_completed": int,
    "tasks_failed": int,
    "success": bool,
    "outputs": List[Dict[str, Any]],
    "wsp00_gate": Dict[str, Any],  # gate status payload
}
```

### `await shutdown() -> None`
- Closes async MCP session resources for one-shot CLI execution.

**Example**:
```python
from modules.infrastructure.wsp_orchestrator.src.wsp_orchestrator import WSPOrchestrator

orchestrator = WSPOrchestrator()

import asyncio

async def _run() -> None:
    orchestrator = WSPOrchestrator()
    try:
        results = await orchestrator.follow_wsp(
            user_task="update ModLog documentation"
        )
        print(results["wsp00_gate"]["gate_passed"])
    finally:
        await orchestrator.shutdown()

asyncio.run(_run())
```

## WSP_00 Gate Controls (Environment)

- `WSP00_AUTO_AWAKEN` (default: `1`)
  - Auto-attempt awakening if gate is non-compliant.
- `WSP00_STRICT_GATE` (default: `1`)
  - Fail closed when gate fails, tracker is unavailable, or gate check errors.

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
