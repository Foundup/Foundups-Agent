# WSP 54 Agentic Orchestrator package
# Exposes main orchestrator and entrypoints for recursive agentic orchestration

from .recursive_orchestration import AgenticOrchestrator
from .entrypoints import orchestrate_wsp54_agents, get_orchestration_stats 