from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime

class OrchestrationTrigger(Enum):
    SYSTEM_STARTUP = "system_startup"
    MODULE_BUILD = "module_build"
    HEALTH_CHECK = "health_check"
    COMPLIANCE_AUDIT = "compliance_audit"
    MEMORY_MAINTENANCE = "memory_maintenance"
    DOCUMENTATION_SYNC = "documentation_sync"
    TESTING_CYCLE = "testing_cycle"
    SCORING_UPDATE = "scoring_update"
    MODULARITY_AUDIT = "modularity_audit"
    RECURSIVE_IMPROVEMENT = "recursive_improvement"
    ZEN_CODING_FLOW = "zen_coding_flow"
    RIDER_INFLUENCE = "rider_influence"

class AgentPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5

@dataclass
class OrchestrationContext:
    trigger: OrchestrationTrigger
    module_name: Optional[str] = None
    rider_influence: float = 1.0
    zen_flow_state: str = "01(02)"
    last_activation: Optional[datetime] = None
    agent_results: Dict[str, Any] = field(default_factory=dict)
    recursive_depth: int = 0
    max_recursive_depth: int = 5

@dataclass
class AgentTask:
    agent_name: str
    priority: AgentPriority
    trigger_conditions: List[OrchestrationTrigger]
    dependencies: List[str] = field(default_factory=list)
    execution_timeout: int = 300
    recursive_improvement_candidate: bool = False
    zen_coding_required: bool = False 