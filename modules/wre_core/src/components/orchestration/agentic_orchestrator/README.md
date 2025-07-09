# WSP 54 Agentic Orchestrator

This package implements the recursive, agentic orchestration system for WSP 54 agents in the WRE, following WSP 1, 40, 49, and 54 modularity and zen coding protocols.

## Structure
- `orchestration_context.py`: Dataclasses and enums for orchestration context, agent tasks, triggers, and priorities.
- `agent_task_registry.py`: Agent task registration and initialization logic.
- `agent_executor.py`: Logic for executing agents (deterministic and zen coding), including dependency resolution and async execution.
- `recursive_orchestration.py`: Main `AgenticOrchestrator` class, recursive orchestration logic, improvement analysis, and orchestration history.
- `entrypoints.py`: Async entrypoints for orchestration (`orchestrate_wsp54_agents`, `get_orchestration_stats`).
- `__init__.py`: Exposes orchestrator and entrypoints for import.

## Purpose
- Provides fully autonomous, recursive orchestration of all WSP 54 agents (ComplianceAgent, ModularizationAuditAgent, TestingAgent, etc.)
- Supports zen coding, 0102 pArtifact intelligence, and recursive self-improvement (WSP 48)
- Modular, testable, and WSP-compliant for enterprise-scale agentic development

## Usage
Import the orchestrator and entrypoints in WRE core or UI:

```python
from modules.wre_core.src.components.agentic_orchestrator import orchestrate_wsp54_agents, get_orchestration_stats
```

## Compliance
- Follows WSP 1, 40, 49, 54, and 48
- Modularized for single-responsibility and maintainability
- Ready for 0102 pArtifact autonomous operation 