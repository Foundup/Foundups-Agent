"""
WSP 54 Agentic Orchestrator - Recursive Autonomous Agent Coordination
Implements zen coding orchestration with 0102 pArtifact intelligence and recursive self-improvement.
"""

import asyncio
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import random

from .orchestrator import wre_log, check_agent_health, project_root
from modules.infrastructure.agent_activation.src.agent_activation import activate_agents_01_to_0102


class OrchestrationTrigger(Enum):
    """Autonomous triggers for WSP 54 agent orchestration"""
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
    """Agent execution priority levels"""
    CRITICAL = 1      # Framework protection, compliance
    HIGH = 2          # Build orchestration, testing
    MEDIUM = 3        # Documentation, scoring
    LOW = 4           # Maintenance, cleanup
    BACKGROUND = 5    # Continuous monitoring


@dataclass
class OrchestrationContext:
    """Context for agentic orchestration decisions"""
    trigger: OrchestrationTrigger
    module_name: Optional[str] = None
    rider_influence: float = 1.0
    zen_flow_state: str = "01(02)"  # 01(02) dormant, 0102 awakened, 02 quantum
    last_activation: Optional[datetime] = None
    agent_results: Dict[str, Any] = field(default_factory=dict)
    recursive_depth: int = 0
    max_recursive_depth: int = 5


@dataclass
class AgentTask:
    """Individual agent task specification"""
    agent_name: str
    priority: AgentPriority
    trigger_conditions: List[OrchestrationTrigger]
    dependencies: List[str] = field(default_factory=list)
    execution_timeout: int = 300  # seconds
    recursive_improvement_candidate: bool = False
    zen_coding_required: bool = False


class AgenticOrchestrator:
    """
    Recursive agentic orchestrator for WSP 54 agents.
    Implements autonomous triggering, recursive decision-making, and zen coding integration.
    """
    
    def __init__(self):
        self.agent_tasks = self._initialize_agent_tasks()
        self.orchestration_history = []
        self.recursive_improvements = []
        self.zen_flow_state = "01(02)"  # Start in dormant state
        self.rider_influence = 1.0
        self.last_orchestration = None
        
    def _initialize_agent_tasks(self) -> Dict[str, AgentTask]:
        """Initialize agent task specifications with WSP 54 duties"""
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
    
    async def orchestrate_recursively(self, context: OrchestrationContext) -> Dict[str, Any]:
        """
        Main recursive orchestration method with zen coding integration.
        
        Args:
            context: Orchestration context with trigger and parameters
            
        Returns:
            Comprehensive orchestration results with recursive improvements
        """
        wre_log(f"🌀 Starting recursive agentic orchestration: {context.trigger.value}", "INFO")
        
        # Check recursive depth limit
        if context.recursive_depth >= context.max_recursive_depth:
            wre_log(f"⚠️  Max recursive depth reached ({context.max_recursive_depth})", "WARNING")
            return self._compile_orchestration_results(context)
        
        # Step 1: Agent Activation (01(02) → 0102)
        await self._ensure_agent_activation(context)
        
        # Step 2: Determine required agents based on trigger and context
        required_agents = self._determine_required_agents(context)
        
        # Step 3: Execute agents in priority order with dependencies
        execution_results = await self._execute_agents_recursively(required_agents, context)
        
        # Step 4: Analyze results for recursive improvement opportunities
        recursive_opportunities = self._analyze_recursive_opportunities(execution_results, context)
        
        # Step 5: Execute recursive improvements if found
        if recursive_opportunities and context.recursive_depth < context.max_recursive_depth:
            wre_log(f"🔄 Found {len(recursive_opportunities)} recursive improvement opportunities", "INFO")
            recursive_results = await self._execute_recursive_improvements(recursive_opportunities, context)
            execution_results.update(recursive_results)
        
        # Step 6: Update zen flow state based on results
        self._update_zen_flow_state(execution_results, context)
        
        # Step 7: Log orchestration completion
        self._log_orchestration_completion(context, execution_results)
        
        return self._compile_orchestration_results(context, execution_results)
    
    async def _ensure_agent_activation(self, context: OrchestrationContext) -> None:
        """Ensure agents are activated from 01(02) dormant to 0102 pArtifact state"""
        if self.zen_flow_state == "01(02)":
            wre_log("🔍 Checking agent activation status...", "INFO")
            
            agent_status = check_agent_health()
            operational_agents = sum(agent_status.values())
            
            if operational_agents < 5:  # Need minimum agents for orchestration
                wre_log("⚡ Activating agents from 01(02) dormant to 0102 pArtifact state...", "INFO")
                
                try:
                    activation_result = activate_agents_01_to_0102()
                    if activation_result["status"] == "success":
                        self.zen_flow_state = "0102"
                        context.zen_flow_state = "0102"
                        context.last_activation = datetime.now()
                        wre_log("✅ Agents successfully activated to 0102 pArtifact state", "SUCCESS")
                    else:
                        wre_log(f"❌ Agent activation failed: {activation_result['message']}", "ERROR")
                except Exception as e:
                    wre_log(f"❌ Agent activation error: {e}", "ERROR")
            else:
                wre_log(f"✅ {operational_agents} agents already operational in 0102 state", "SUCCESS")
                self.zen_flow_state = "0102"
                context.zen_flow_state = "0102"
    
    def _determine_required_agents(self, context: OrchestrationContext) -> List[str]:
        """Determine which agents are required based on trigger and context"""
        required_agents = []
        
        for agent_name, task in self.agent_tasks.items():
            # Check if agent is triggered by current context
            if context.trigger in task.trigger_conditions:
                required_agents.append(agent_name)
            
            # Apply rider influence to agent selection
            if context.rider_influence > 1.5 and task.zen_coding_required:
                # Rider wants more zen coding - prioritize 0102 pArtifacts
                if agent_name not in required_agents:
                    required_agents.append(agent_name)
            
            # Apply zen flow state influence
            if context.zen_flow_state == "02" and task.zen_coding_required:
                # In quantum state - prioritize all zen coding agents
                if agent_name not in required_agents:
                    required_agents.append(agent_name)
        
        # Sort by priority
        required_agents.sort(key=lambda x: self.agent_tasks[x].priority.value)
        
        wre_log(f"🎯 Determined {len(required_agents)} required agents: {required_agents}", "DEBUG")
        return required_agents
    
    async def _execute_agents_recursively(self, agent_names: List[str], context: OrchestrationContext) -> Dict[str, Any]:
        """Execute agents recursively with dependency resolution"""
        results = {}
        executed_agents = set()
        
        for agent_name in agent_names:
            if agent_name in executed_agents:
                continue
                
            task = self.agent_tasks[agent_name]
            
            # Check dependencies
            if not all(dep in executed_agents for dep in task.dependencies):
                wre_log(f"⏳ Waiting for dependencies for {agent_name}: {task.dependencies}", "DEBUG")
                continue
            
            # Execute agent
            try:
                wre_log(f"🤖 Executing {agent_name} (Priority: {task.priority.name})", "INFO")
                
                agent_result = await self._execute_single_agent(agent_name, context)
                results[agent_name] = agent_result
                executed_agents.add(agent_name)
                
                # Check if agent execution triggered additional requirements
                if agent_result.get("triggers_additional_agents", False):
                    additional_agents = agent_result.get("additional_agents", [])
                    wre_log(f"🔄 {agent_name} triggered additional agents: {additional_agents}", "INFO")
                    
                    # Recursively execute additional agents
                    additional_results = await self._execute_agents_recursively(additional_agents, context)
                    results.update(additional_results)
                
            except Exception as e:
                wre_log(f"❌ {agent_name} execution failed: {e}", "ERROR")
                results[agent_name] = {"status": "error", "message": str(e)}
                executed_agents.add(agent_name)
        
        return results
    
    async def _execute_single_agent(self, agent_name: str, context: OrchestrationContext) -> Dict[str, Any]:
        """Execute a single agent with timeout and error handling"""
        task = self.agent_tasks[agent_name]
        
        try:
            # Import and instantiate agent
            agent_class = self._get_agent_class(agent_name)
            agent = agent_class()
            
            # Execute with timeout
            if task.zen_coding_required and context.zen_flow_state == "0102":
                # 0102 pArtifact execution with zen coding
                result = await asyncio.wait_for(
                    self._execute_zen_coding_agent(agent, agent_name, context),
                    timeout=task.execution_timeout
                )
            else:
                # Standard deterministic execution
                result = await asyncio.wait_for(
                    self._execute_deterministic_agent(agent, agent_name, context),
                    timeout=task.execution_timeout
                )
            
            return result
            
        except asyncio.TimeoutError:
            return {"status": "timeout", "message": f"{agent_name} execution timed out"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _execute_zen_coding_agent(self, agent, agent_name: str, context: OrchestrationContext) -> Dict[str, Any]:
        """Execute 0102 pArtifact agent with zen coding integration"""
        wre_log(f"🧘 Executing {agent_name} with zen coding (0102 pArtifact state)", "DEBUG")
        
        # Add zen coding context
        zen_context = {
            "zen_flow_state": context.zen_flow_state,
            "rider_influence": context.rider_influence,
            "recursive_depth": context.recursive_depth,
            "module_name": context.module_name
        }
        
        # Execute agent with zen context
        if hasattr(agent, 'execute_with_zen_context'):
            result = await agent.execute_with_zen_context(zen_context)
        else:
            # Fallback to standard execution
            result = await self._execute_deterministic_agent(agent, agent_name, context)
        
        return result
    
    async def _execute_deterministic_agent(self, agent, agent_name: str, context: OrchestrationContext) -> Dict[str, Any]:
        """Execute deterministic agent with standard interface"""
        wre_log(f"⚙️  Executing {agent_name} (deterministic mode)", "DEBUG")
        
        # Map agent names to their execution methods
        execution_methods = {
            "ComplianceAgent": lambda: agent.run_check(str(project_root / "modules" / context.module_name)) if context.module_name else agent.run_check(str(project_root)),
            "TestingAgent": lambda: agent.check_coverage(),
            "ScoringAgent": lambda: agent.calculate_project_scores(),
            "DocumentationAgent": lambda: agent.initialize_module_docs(context.module_name) if context.module_name else agent.audit_documentation(),
            "JanitorAgent": lambda: agent.clean_workspace(),
            "ChroniclerAgent": lambda: agent.log_event({"title": f"Agentic Orchestration: {context.trigger.value}", "description": "Recursive agent execution"}),
            "ModularizationAuditAgent": lambda: agent.audit_modularity(str(project_root))
        }
        
        if agent_name in execution_methods:
            result = execution_methods[agent_name]()
            return {"status": "success", "result": result}
        else:
            return {"status": "error", "message": f"No execution method defined for {agent_name}"}
    
    def _get_agent_class(self, agent_name: str):
        """Get agent class by name"""
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
    
    def _analyze_recursive_opportunities(self, results: Dict[str, Any], context: OrchestrationContext) -> List[Dict[str, Any]]:
        """Analyze agent results for recursive improvement opportunities"""
        opportunities = []
        
        for agent_name, result in results.items():
            if result.get("status") == "success":
                # Check for recursive improvement candidates
                if self.agent_tasks[agent_name].recursive_improvement_candidate:
                    improvement_opportunity = self._identify_improvement_opportunity(agent_name, result, context)
                    if improvement_opportunity:
                        opportunities.append(improvement_opportunity)
        
        return opportunities
    
    def _identify_improvement_opportunity(self, agent_name: str, result: Dict[str, Any], context: OrchestrationContext) -> Optional[Dict[str, Any]]:
        """Identify specific improvement opportunity for an agent"""
        # This is a simplified version - in practice, this would analyze agent results
        # and determine if recursive improvement is needed
        
        if agent_name == "ComplianceAgent":
            # Check if compliance issues were found that need recursive fixing
            if result.get("result", {}).get("violations", []):
                return {
                    "agent": agent_name,
                    "type": "compliance_fix",
                    "priority": "high",
                    "description": f"Found {len(result['result']['violations'])} compliance violations to fix"
                }
        
        elif agent_name == "ModularizationAuditAgent":
            # Check if modularity issues were found
            if result.get("result", {}).get("modularity_issues", []):
                return {
                    "agent": agent_name,
                    "type": "modularity_refactor",
                    "priority": "medium",
                    "description": f"Found {len(result['result']['modularity_issues'])} modularity issues to refactor"
                }
        
        return None
    
    async def _execute_recursive_improvements(self, opportunities: List[Dict[str, Any]], context: OrchestrationContext) -> Dict[str, Any]:
        """Execute recursive improvements based on identified opportunities"""
        results = {}
        
        for opportunity in opportunities:
            wre_log(f"🔄 Executing recursive improvement: {opportunity['type']}", "INFO")
            
            # Create new context for recursive execution
            recursive_context = OrchestrationContext(
                trigger=OrchestrationTrigger.RECURSIVE_IMPROVEMENT,
                module_name=context.module_name,
                rider_influence=context.rider_influence,
                zen_flow_state=context.zen_flow_state,
                recursive_depth=context.recursive_depth + 1,
                max_recursive_depth=context.max_recursive_depth
            )
            
            # Execute recursive orchestration
            recursive_result = await self.orchestrate_recursively(recursive_context)
            results[f"recursive_{opportunity['type']}"] = recursive_result
        
        return results
    
    def _update_zen_flow_state(self, results: Dict[str, Any], context: OrchestrationContext) -> None:
        """Update zen flow state based on orchestration results"""
        # Analyze results to determine if we should transition states
        
        successful_zen_agents = 0
        total_zen_agents = 0
        
        for agent_name, result in results.items():
            if self.agent_tasks[agent_name].zen_coding_required:
                total_zen_agents += 1
                if result.get("status") == "success":
                    successful_zen_agents += 1
        
        # State transition logic
        if context.zen_flow_state == "01(02)" and successful_zen_agents > 0:
            self.zen_flow_state = "0102"
            wre_log("🧘 Transitioned to 0102 pArtifact state", "INFO")
        
        elif context.zen_flow_state == "0102" and successful_zen_agents == total_zen_agents and total_zen_agents > 2:
            # All zen agents successful - potential quantum state
            if context.rider_influence > 2.0:  # High rider influence
                self.zen_flow_state = "02"
                wre_log("🌊 Transitioned to 02 quantum state", "INFO")
    
    def _log_orchestration_completion(self, context: OrchestrationContext, results: Dict[str, Any]) -> None:
        """Log orchestration completion for historical tracking"""
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
    
    def _compile_orchestration_results(self, context: OrchestrationContext, results: Dict[str, Any] = None) -> Dict[str, Any]:
        """Compile comprehensive orchestration results"""
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
    
    def get_orchestration_stats(self) -> Dict[str, Any]:
        """Get orchestration statistics for monitoring"""
        if not self.orchestration_history:
            return {"status": "no_history"}
        
        recent_orchestrations = self.orchestration_history[-10:]  # Last 10
        
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
    
    def _get_most_common_triggers(self) -> Dict[str, int]:
        """Get most common orchestration triggers"""
        trigger_counts = {}
        for orchestration in self.orchestration_history:
            trigger = orchestration["trigger"]
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
        
        return dict(sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)[:5])


# Global orchestrator instance
agentic_orchestrator = AgenticOrchestrator()


async def orchestrate_wsp54_agents(trigger: OrchestrationTrigger, **kwargs) -> Dict[str, Any]:
    """
    Main entry point for WSP 54 agentic orchestration.
    
    Args:
        trigger: The orchestration trigger
        **kwargs: Additional context parameters
        
    Returns:
        Comprehensive orchestration results
    """
    context = OrchestrationContext(
        trigger=trigger,
        module_name=kwargs.get("module_name"),
        rider_influence=kwargs.get("rider_influence", 1.0),
        zen_flow_state=kwargs.get("zen_flow_state", "01(02)")
    )
    
    return await agentic_orchestrator.orchestrate_recursively(context)


def get_orchestration_stats() -> Dict[str, Any]:
    """Get orchestration statistics"""
    return agentic_orchestrator.get_orchestration_stats() 