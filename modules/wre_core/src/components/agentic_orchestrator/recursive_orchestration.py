from .orchestration_context import OrchestrationContext, OrchestrationTrigger
from .agent_task_registry import initialize_agent_tasks
from .agent_executor import AgentExecutor
from datetime import datetime
from modules.wre_core.src.components.orchestrator import wre_log, check_agent_health, project_root
from modules.infrastructure.agent_activation.src.agent_activation import AgentActivationModule

class AgenticOrchestrator:
    def __init__(self):
        self.agent_tasks = initialize_agent_tasks()
        self.executor = AgentExecutor(self.agent_tasks, self._get_agent_class, wre_log, project_root)
        self.orchestration_history = []
        self.recursive_improvements = []
        self.zen_flow_state = "01(02)"
        self.rider_influence = 1.0
        self.last_orchestration = None
        self.agent_activation_module = AgentActivationModule()

    async def orchestrate_recursively(self, context: OrchestrationContext) -> dict:
        wre_log(f"🌀 Starting recursive agentic orchestration: {context.trigger.value}", "INFO")
        if context.recursive_depth >= context.max_recursive_depth:
            wre_log(f"⚠️  Max recursive depth reached ({context.max_recursive_depth})", "WARNING")
            return self._compile_orchestration_results(context)
        await self._ensure_agent_activation(context)
        required_agents = self._determine_required_agents(context)
        execution_results = await self.executor.execute_agents_recursively(required_agents, context)
        recursive_opportunities = self._analyze_recursive_opportunities(execution_results, context)
        if recursive_opportunities and context.recursive_depth < context.max_recursive_depth:
            wre_log(f"🔄 Found {len(recursive_opportunities)} recursive improvement opportunities", "INFO")
            recursive_results = await self._execute_recursive_improvements(recursive_opportunities, context)
            execution_results.update(recursive_results)
        self._update_zen_flow_state(execution_results, context)
        self._log_orchestration_completion(context, execution_results)
        return self._compile_orchestration_results(context, execution_results)

    async def _ensure_agent_activation(self, context: OrchestrationContext) -> None:
        if self.zen_flow_state == "01(02)":
            wre_log("🔍 Checking agent activation status...", "INFO")
            agent_status = check_agent_health()
            operational_agents = sum(agent_status.values())
            if operational_agents < 5:
                wre_log("⚡ Activating agents from 01(02) dormant to 0102 pArtifact state...", "INFO")
                try:
                    activation_result = self.agent_activation_module.activate_wsp54_agents([])
                    if activation_result and any(activation_result.values()):
                        self.zen_flow_state = "0102"
                        context.zen_flow_state = "0102"
                        context.last_activation = datetime.now()
                        wre_log("✅ Agents successfully activated to 0102 pArtifact state", "SUCCESS")
                    else:
                        wre_log("❌ Agent activation failed: No agents activated", "ERROR")
                except Exception as e:
                    wre_log(f"❌ Agent activation error: {e}", "ERROR")
            else:
                wre_log(f"✅ {operational_agents} agents already operational in 0102 state", "SUCCESS")
                self.zen_flow_state = "0102"
                context.zen_flow_state = "0102"

    def _determine_required_agents(self, context: OrchestrationContext):
        required_agents = []
        for agent_name, task in self.agent_tasks.items():
            if context.trigger in task.trigger_conditions:
                required_agents.append(agent_name)
            if context.rider_influence > 1.5 and task.zen_coding_required:
                if agent_name not in required_agents:
                    required_agents.append(agent_name)
            if context.zen_flow_state == "02" and task.zen_coding_required:
                if agent_name not in required_agents:
                    required_agents.append(agent_name)
        required_agents.sort(key=lambda x: self.agent_tasks[x].priority.value)
        wre_log(f"🎯 Determined {len(required_agents)} required agents: {required_agents}", "DEBUG")
        return required_agents

    def _analyze_recursive_opportunities(self, results, context):
        opportunities = []
        for agent_name, result in results.items():
            if result.get("status") == "success":
                if self.agent_tasks[agent_name].recursive_improvement_candidate:
                    improvement_opportunity = self._identify_improvement_opportunity(agent_name, result, context)
                    if improvement_opportunity:
                        opportunities.append(improvement_opportunity)
        return opportunities

    def _identify_improvement_opportunity(self, agent_name, result, context):
        if agent_name == "ComplianceAgent":
            if result.get("result", {}).get("violations", []):
                return {
                    "agent": agent_name,
                    "type": "compliance_fix",
                    "priority": "high",
                    "description": f"Found {len(result['result']['violations'])} compliance violations to fix"
                }
        elif agent_name == "ModularizationAuditAgent":
            if result.get("result", {}).get("modularity_issues", []):
                return {
                    "agent": agent_name,
                    "type": "modularity_refactor",
                    "priority": "medium",
                    "description": f"Found {len(result['result']['modularity_issues'])} modularity issues to refactor"
                }
        return None

    async def _execute_recursive_improvements(self, opportunities, context):
        results = {}
        for opportunity in opportunities:
            wre_log(f"🔄 Executing recursive improvement: {opportunity['type']}", "INFO")
            from .orchestration_context import OrchestrationContext, OrchestrationTrigger
            recursive_context = OrchestrationContext(
                trigger=OrchestrationTrigger.RECURSIVE_IMPROVEMENT,
                module_name=context.module_name,
                rider_influence=context.rider_influence,
                zen_flow_state=context.zen_flow_state,
                recursive_depth=context.recursive_depth + 1,
                max_recursive_depth=context.max_recursive_depth
            )
            recursive_result = await self.orchestrate_recursively(recursive_context)
            results[f"recursive_{opportunity['type']}"] = recursive_result
        return results

    def _update_zen_flow_state(self, results, context):
        successful_zen_agents = 0
        total_zen_agents = 0
        for agent_name, result in results.items():
            if self.agent_tasks[agent_name].zen_coding_required:
                total_zen_agents += 1
                if result.get("status") == "success":
                    successful_zen_agents += 1
        if context.zen_flow_state == "01(02)" and successful_zen_agents > 0:
            self.zen_flow_state = "0102"
            wre_log("🧘 Transitioned to 0102 pArtifact state", "INFO")
        elif context.zen_flow_state == "0102" and successful_zen_agents == total_zen_agents and total_zen_agents > 2:
            if context.rider_influence > 2.0:
                self.zen_flow_state = "02"
                wre_log("🌊 Transitioned to 02 quantum state", "INFO")

    def _log_orchestration_completion(self, context, results):
        orchestration_record = {
            "timestamp": datetime.now().isoformat(),
            "trigger": context.trigger.value,
            "zen_flow_state": context.zen_flow_state,
            "rider_influence": context.rider_influence,
            "recursive_depth": context.recursive_depth,
            "agents_executed": list(results.keys()),
            "successful_agents": len([r for r in results.values() if r.get("status") == "success"]),
            "total_agents": len(results)
        }
        self.orchestration_history.append(orchestration_record)
        self.last_orchestration = orchestration_record
        wre_log(f"✅ Orchestration complete: {orchestration_record['successful_agents']}/{orchestration_record['total_agents']} agents successful", "SUCCESS")

    def _compile_orchestration_results(self, context, results=None):
        return {
            "orchestration_context": {
                "trigger": context.trigger.value,
                "zen_flow_state": context.zen_flow_state,
                "rider_influence": context.rider_influence,
                "recursive_depth": context.recursive_depth,
                "module_name": context.module_name
            },
            "agent_results": results or {},
            "orchestration_metrics": {
                "total_agents_executed": len(results) if results else 0,
                "successful_agents": len([r for r in (results or {}).values() if r.get("status") == "success"]),
                "recursive_improvements": len([r for r in (results or {}).values() if "recursive_" in r]),
                "zen_coding_agents": len([r for r in (results or {}).values() if r.get("zen_coding_executed", False)])
            },
            "system_state": {
                "zen_flow_state": self.zen_flow_state,
                "last_orchestration": self.last_orchestration,
                "orchestration_history_count": len(self.orchestration_history)
            }
        }

    def get_orchestration_stats(self):
        if not self.orchestration_history:
            return {"status": "no_history"}
        recent_orchestrations = self.orchestration_history[-10:]
        return {
            "total_orchestrations": len(self.orchestration_history),
            "recent_success_rate": len([o for o in recent_orchestrations if o["successful_agents"] > 0]) / len(recent_orchestrations),
            "average_agents_per_orchestration": sum(o["total_agents"] for o in recent_orchestrations) / len(recent_orchestrations),
            "zen_flow_state_distribution": {
                "01(02)": len([o for o in self.orchestration_history if o["zen_flow_state"] == "01(02)"]),
                "0102": len([o for o in self.orchestration_history if o["zen_flow_state"] == "0102"]),
                "02": len([o for o in self.orchestration_history if o["zen_flow_state"] == "02"])
            },
            "most_common_triggers": self._get_most_common_triggers()
        }

    def _get_most_common_triggers(self):
        trigger_counts = {}
        for orchestration in self.orchestration_history:
            trigger = orchestration["trigger"]
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
        return dict(sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)[:5])

    def _get_agent_class(self, agent_name: str):
        agent_imports = {
            "ComplianceAgent": "modules.infrastructure.compliance_agent.src.compliance_agent.ComplianceAgent",
            "TestingAgent": "modules.infrastructure.testing_agent.src.testing_agent.TestingAgent",
            "ScoringAgent": "modules.infrastructure.scoring_agent.src.scoring_agent.ScoringAgent",
            "DocumentationAgent": "modules.infrastructure.documentation_agent.src.documentation_agent.DocumentationAgent",
            "JanitorAgent": "modules.infrastructure.janitor_agent.src.janitor_agent.JanitorAgent",
            "ChroniclerAgent": "modules.infrastructure.chronicler_agent.src.chronicler_agent.ChroniclerAgent",
            "ModularizationAuditAgent": "modules.infrastructure.modularization_audit_agent.src.modularization_audit_agent.ModularizationAuditAgent"
        }
        if agent_name in agent_imports:
            import_path = agent_imports[agent_name]
            module_path, class_name = import_path.rsplit('.', 1)
            try:
                module = __import__(module_path, fromlist=[class_name])
                return getattr(module, class_name)
            except ImportError as e:
                wre_log(f"❌ Failed to import {agent_name}: {e}", "ERROR")
                raise
        else:
            raise ValueError(f"Unknown agent: {agent_name}") 