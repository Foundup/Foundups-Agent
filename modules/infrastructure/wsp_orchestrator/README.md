# WSP Orchestrator - AI Overseer + Worker Bee Architecture

**WSP Domain**: `infrastructure` (WSP 3)

## Purpose

Modular "follow WSP" system using AI Overseer (Qwen) + Worker Bees (Qwen/Gemma/MCP) architecture.

**CRITICAL**: This is a **standalone module** - **NO CODE IN MAIN.PY**.

## Architecture (Based on autonomous_refactoring.py Proven Pattern)

```
AI Overseer (Qwen Meta-Orchestration)
    +-- Worker Bee 1: HoloIndex MCP (semantic search, WSP lookup)
    +-- Worker Bee 2: Gemma 3 270M (fast pattern matching)
    +-- Worker Bee 3: Qwen 1.5B (strategic planning)
    +-- Worker Bee 4: Rules Engine (grep/regex)
    +-- 0102 Supervision (human oversight)
```

### Execution Flow

1. **Phase 0: Meta-Orchestration** - Qwen decides which workers to use
2. **Phase 1: Generate Plan** - Create WSP execution plan
3. **Phase 2: Assign Workers** - Route tasks to appropriate bees
4. **Phase 3: Execute with Supervision** - 0102 oversight + worker execution
5. **Phase 4: Learning** - Store patterns for future use

## Usage

### Standalone CLI (NOT from main.py)

```bash
python modules/infrastructure/wsp_orchestrator/src/wsp_orchestrator.py "create new module for YouTube analysis"
```

### Programmatic API

```python
from modules.infrastructure.wsp_orchestrator.src.wsp_orchestrator import WSPOrchestrator

orchestrator = WSPOrchestrator()
results = orchestrator.follow_wsp(
    user_task="implement new feature X",
    auto_execute=False  # Requires 0102 approval
)
```

## Key Features

- **AI Overseer**: Qwen meta-orchestration decides execution strategy
- **Worker Bees**: Specialized agents (Gemma/MCP/Qwen/Rules)
- **MCP Integration**: HoloIndex search, WSP lookup via MCP servers
- **0102 Supervision**: Human oversight for critical tasks
- **Modular Design**: Zero code in main.py

## WSP Compliance

- **WSP 77**: Agent Coordination Protocol (Overseer -> Workers)
- **WSP 50**: Pre-Action Verification (HoloIndex first)
- **WSP 84**: Code Memory Verification (MCP tools, no duplication)
- **WSP 3**: Infrastructure Domain (orchestration)
- **WSP 49**: Module Structure (complete)

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
