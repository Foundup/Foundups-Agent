import asyncio
from .orchestration_context import OrchestrationContext
from typing import Dict, Any, List

class AgentExecutor:
    def __init__(self, agent_tasks, get_agent_class, wre_log, project_root):
        self.agent_tasks = agent_tasks
        self.get_agent_class = get_agent_class
        self.wre_log = wre_log
        self.project_root = project_root

    async def execute_agents_recursively(self, agent_names: List[str], context: OrchestrationContext) -> Dict[str, Any]:
        results = {}
        executed_agents = set()
        pending_agents = set(agent_names)
        
        # Keep trying to execute agents until no more progress is made
        max_iterations = len(agent_names) * 2  # Prevent infinite loops
        iteration = 0
        
        while pending_agents and iteration < max_iterations:
            iteration += 1
            agents_executed_this_iteration = False
            
            # Try to execute each pending agent
            agents_to_remove = set()
            for agent_name in list(pending_agents):
                task = self.agent_tasks[agent_name]
                
                # Check if all dependencies are satisfied
                if all(dep in executed_agents for dep in task.dependencies):
                    try:
                        self.wre_log(f"🤖 Executing {agent_name} (Priority: {task.priority.name})", "INFO")
                        agent_result = await self.execute_single_agent(agent_name, context)
                        results[agent_name] = agent_result
                        executed_agents.add(agent_name)
                        agents_to_remove.add(agent_name)
                        agents_executed_this_iteration = True
                        
                        # Handle additional agents triggered by this agent
                        if agent_result.get("triggers_additional_agents", False):
                            additional_agents = agent_result.get("additional_agents", [])
                            self.wre_log(f"🔄 {agent_name} triggered additional agents: {additional_agents}", "INFO")
                            additional_results = await self.execute_agents_recursively(additional_agents, context)
                            results.update(additional_results)
                            
                    except Exception as e:
                        self.wre_log(f"❌ {agent_name} execution failed: {e}", "ERROR")
                        results[agent_name] = {"status": "error", "message": str(e)}
                        executed_agents.add(agent_name)
                        agents_to_remove.add(agent_name)
                        agents_executed_this_iteration = True
                else:
                    self.wre_log(f"⏳ Waiting for dependencies for {agent_name}: {[dep for dep in task.dependencies if dep not in executed_agents]}", "DEBUG")
            
            # Remove executed agents from pending
            pending_agents -= agents_to_remove
            
            # If no agents were executed this iteration and there are still pending agents,
            # it means there are unresolvable dependencies
            if not agents_executed_this_iteration and pending_agents:
                self.wre_log(f"⚠️ Unable to resolve dependencies for agents: {list(pending_agents)}", "WARNING")
                break
        
        return results

    async def execute_single_agent(self, agent_name: str, context: OrchestrationContext) -> Dict[str, Any]:
        task = self.agent_tasks[agent_name]
        try:
            agent_class = self.get_agent_class(agent_name)
            agent = agent_class()
            if task.zen_coding_required and context.zen_flow_state == "0102":
                result = await asyncio.wait_for(
                    self.execute_zen_coding_agent(agent, agent_name, context),
                    timeout=task.execution_timeout
                )
            else:
                result = await asyncio.wait_for(
                    self.execute_deterministic_agent(agent, agent_name, context),
                    timeout=task.execution_timeout
                )
            return result
        except asyncio.TimeoutError:
            return {"status": "timeout", "message": f"{agent_name} execution timed out"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def execute_zen_coding_agent(self, agent, agent_name: str, context: OrchestrationContext) -> Dict[str, Any]:
        self.wre_log(f"🧘 Executing {agent_name} with zen coding (0102 pArtifact state)", "DEBUG")
        zen_context = {
            "zen_flow_state": context.zen_flow_state,
            "rider_influence": context.rider_influence,
            "recursive_depth": context.recursive_depth,
            "module_name": context.module_name
        }
        if hasattr(agent, 'execute_with_zen_context'):
            result = await agent.execute_with_zen_context(zen_context)
        else:
            result = await self.execute_deterministic_agent(agent, agent_name, context)
        return result

    async def execute_deterministic_agent(self, agent, agent_name: str, context: OrchestrationContext) -> Dict[str, Any]:
        self.wre_log(f"⚙️  Executing {agent_name} (deterministic mode)", "DEBUG")
        execution_methods = {
            "ComplianceAgent": lambda: agent.run_check(str(self.project_root / "modules" / context.module_name)) if context.module_name else agent.run_check(str(self.project_root)),
            "TestingAgent": lambda: agent.check_coverage(),
            "ScoringAgent": lambda: agent.calculate_project_scores(),
            "DocumentationAgent": lambda: agent.initialize_module_docs(context.module_name) if context.module_name else agent.audit_documentation(),
            "JanitorAgent": lambda: agent.clean_workspace(),
            "ChroniclerAgent": lambda: agent.log_event({"title": f"Agentic Orchestration: {context.trigger.value}", "description": "Recursive agent execution"}),
            "ModularizationAuditAgent": lambda: agent.audit_modularity(str(self.project_root))
        }
        if agent_name in execution_methods:
            result = execution_methods[agent_name]()
            return {"status": "success", "result": result}
        else:
            return {"status": "error", "message": f"No execution method defined for {agent_name}"} 