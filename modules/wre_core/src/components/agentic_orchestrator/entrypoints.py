from .orchestration_context import OrchestrationContext
from .recursive_orchestration import AgenticOrchestrator
from .orchestration_context import OrchestrationTrigger

agentic_orchestrator = AgenticOrchestrator()

async def orchestrate_wsp54_agents(trigger: OrchestrationTrigger, **kwargs):
    context = OrchestrationContext(
        trigger=trigger,
        module_name=kwargs.get("module_name"),
        rider_influence=kwargs.get("rider_influence", 1.0),
        zen_flow_state=kwargs.get("zen_flow_state", "01(02)")
    )
    return await agentic_orchestrator.orchestrate_recursively(context)

def get_orchestration_stats():
    return agentic_orchestrator.get_orchestration_stats() 