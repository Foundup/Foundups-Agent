# WSP Orchestrator - 0102 Orchestrator + Worker Bee Architecture

**WSP Domain**: `infrastructure` (WSP 3)

## Purpose

Modular "follow WSP" system where 0102 orchestrates Qwen/Gemma/MCP workers.

**CRITICAL**: This is a **standalone module** - **NO CODE IN MAIN.PY**.

## Architecture (Based on autonomous_refactoring.py Proven Pattern)

```
0102 Meta-Orchestration
    +-- Worker Bee 1: HoloIndex MCP (semantic search, WSP lookup)
    +-- Worker Bee 2: Gemma 3 270M (fast pattern matching)
    +-- Worker Bee 3: Qwen 1.5B (strategic planning)
    +-- Worker Bee 4: Rules Engine (grep/regex)
    +-- 0102 Supervision (human oversight)
```

### Execution Flow

0. **Phase -1: WSP_00 Gate** - zen-state compliance gate (fail-closed in strict mode)
1. **Phase 0: Meta-Orchestration** - 0102 scores task via WSP 15
2. **Phase 1: Generate Plan** - create WSP execution plan
3. **Phase 2: Assign Workers** - route tasks to appropriate bees
4. **Phase 3: Execute with Supervision** - worker execution under 0102 control
5. **Phase 4: Learning** - store patterns for future use

## Usage

### Standalone CLI (NOT from main.py)

```bash
python modules/infrastructure/wsp_orchestrator/src/wsp_orchestrator.py "create new module for YouTube analysis"
```

### Programmatic API

```python
from modules.infrastructure.wsp_orchestrator.src.wsp_orchestrator import WSPOrchestrator

orchestrator = WSPOrchestrator()

import asyncio

async def _run():
    try:
        results = await orchestrator.follow_wsp("implement new feature X")
        print(results["wsp00_gate"])
    finally:
        await orchestrator.shutdown()

asyncio.run(_run())
```

## Key Features

- **WSP_00 Hard Gate**: "follow WSP" blocks up front when compliance gate fails in strict mode
- **0102 Orchestration**: 0102 controls execution strategy and worker assignment
- **Worker Bees**: Specialized agents (Gemma/MCP/Qwen/Rules)
- **MCP Integration**: HoloIndex search, WSP lookup via MCP servers
- **Fail-Closed Safety**: missing tracker/gate errors block when strict mode is enabled
- **Modular Design**: Zero code in main.py

## WSP Compliance

- **WSP 77**: Agent Coordination Protocol (Overseer -> Workers)
- **WSP 50**: Pre-Action Verification (HoloIndex first)
- **WSP 00**: Zen-state compliance gate before orchestration
- **WSP 84**: Code Memory Verification (MCP tools, no duplication)
- **WSP 3**: Infrastructure Domain (orchestration)
- **WSP 49**: Module Structure (complete)

## Gate Controls (Env Vars)

- `WSP00_AUTO_AWAKEN=1` (default): auto-attempt awakening when gate is non-compliant
- `WSP00_STRICT_GATE=1` (default): fail closed when gate fails / tracker unavailable / gate check errors

## Worker Assignment Logic

| Task Type | Worker Assigned | Rationale |
|-----------|----------------|-----------|
| HoloIndex search | MCP:HoloIndex | Semantic code search (100ms) |
| WSP lookup | MCP:HoloIndex | Protocol documentation (100ms) |
| Pattern matching | Gemma:PatternMatch | Fast binary decisions (50ms) |
| Strategic planning | Qwen:Planning | Deep analysis (250ms) |
| Implementation | 0102:Supervision | Human oversight required |
| ModLog updates | Qwen:Planning | Documentation generation |

## Dependencies

- `modules.infrastructure.mcp_manager` - MCP server management
- `holo_index.qwen_advisor.orchestration.autonomous_refactoring` - Qwen/Gemma workers
- `logging`, `json`, `time` - Standard library

## Future Enhancements

- Full MCP tool invocation (not just server start/stop)
- Pattern learning and storage
- Autonomous execution mode (no 0102 approval)
- Integration with main.py menu (option 15: "WSP Orchestrator")
