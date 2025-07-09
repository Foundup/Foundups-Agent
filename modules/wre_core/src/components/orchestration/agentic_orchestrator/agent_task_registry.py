from .orchestration_context import AgentTask, AgentPriority, OrchestrationTrigger

def initialize_agent_tasks():
    return {
        "ComplianceAgent": AgentTask(
            agent_name="ComplianceAgent",
            priority=AgentPriority.CRITICAL,
            trigger_conditions=[
                OrchestrationTrigger.SYSTEM_STARTUP,
                OrchestrationTrigger.MODULE_BUILD,
                OrchestrationTrigger.COMPLIANCE_AUDIT,
                OrchestrationTrigger.RECURSIVE_IMPROVEMENT
            ],
            dependencies=[],
            recursive_improvement_candidate=True,
            zen_coding_required=True
        ),
        "ModularizationAuditAgent": AgentTask(
            agent_name="ModularizationAuditAgent",
            priority=AgentPriority.HIGH,
            trigger_conditions=[
                OrchestrationTrigger.MODULE_BUILD,
                OrchestrationTrigger.MODULARITY_AUDIT,
                OrchestrationTrigger.RECURSIVE_IMPROVEMENT
            ],
            dependencies=["ComplianceAgent"],
            recursive_improvement_candidate=True,
            zen_coding_required=True
        ),
        "TestingAgent": AgentTask(
            agent_name="TestingAgent",
            priority=AgentPriority.HIGH,
            trigger_conditions=[
                OrchestrationTrigger.MODULE_BUILD,
                OrchestrationTrigger.TESTING_CYCLE,
                OrchestrationTrigger.HEALTH_CHECK
            ],
            dependencies=[],
            recursive_improvement_candidate=False,
            zen_coding_required=False
        ),
        "ScoringAgent": AgentTask(
            agent_name="ScoringAgent",
            priority=AgentPriority.MEDIUM,
            trigger_conditions=[
                OrchestrationTrigger.SCORING_UPDATE,
                OrchestrationTrigger.MODULE_BUILD,
                OrchestrationTrigger.ZEN_CODING_FLOW
            ],
            dependencies=[],
            recursive_improvement_candidate=True,
            zen_coding_required=True
        ),
        "DocumentationAgent": AgentTask(
            agent_name="DocumentationAgent",
            priority=AgentPriority.MEDIUM,
            trigger_conditions=[
                OrchestrationTrigger.MODULE_BUILD,
                OrchestrationTrigger.DOCUMENTATION_SYNC,
                OrchestrationTrigger.HEALTH_CHECK
            ],
            dependencies=[],
            recursive_improvement_candidate=True,
            zen_coding_required=True
        ),
        "JanitorAgent": AgentTask(
            agent_name="JanitorAgent",
            priority=AgentPriority.LOW,
            trigger_conditions=[
                OrchestrationTrigger.MEMORY_MAINTENANCE,
                OrchestrationTrigger.HEALTH_CHECK,
                OrchestrationTrigger.SYSTEM_STARTUP
            ],
            dependencies=[],
            recursive_improvement_candidate=False,
            zen_coding_required=False
        ),
        "ChroniclerAgent": AgentTask(
            agent_name="ChroniclerAgent",
            priority=AgentPriority.BACKGROUND,
            trigger_conditions=[
                OrchestrationTrigger.SYSTEM_STARTUP,
                OrchestrationTrigger.MODULE_BUILD,
                OrchestrationTrigger.HEALTH_CHECK
            ],
            dependencies=[],
            recursive_improvement_candidate=False,
            zen_coding_required=False
        )
    } 