"""
Tests for the modularized agentic_orchestrator components.
Tests each module individually and integration between modules.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

# Import the modularized components
from modules.wre_core.src.components.agentic_orchestrator.orchestration_context import (
    OrchestrationTrigger, AgentPriority, OrchestrationContext, AgentTask
)
from modules.wre_core.src.components.agentic_orchestrator.agent_task_registry import initialize_agent_tasks
from modules.wre_core.src.components.agentic_orchestrator.agent_executor import AgentExecutor
from modules.wre_core.src.components.agentic_orchestrator.recursive_orchestration import AgenticOrchestrator
from modules.wre_core.src.components.agentic_orchestrator.entrypoints import orchestrate_wsp54_agents, get_orchestration_stats
from modules.infrastructure.agent_activation.src.agent_activation import AgentActivationModule

# Patch agent activation in orchestrator tests to avoid real activation logic
@pytest.fixture(autouse=True)
def patch_agent_activation(monkeypatch):
    monkeypatch.setattr(
        'modules.wre_core.src.components.agentic_orchestrator.recursive_orchestration.AgentActivationModule',
        lambda *args, **kwargs: Mock(activate_wsp54_agents=Mock(return_value={"ComplianceAgent": True}))
    )
    yield


class TestOrchestrationContext:
    """Test orchestration context dataclasses and enums."""
    
    def test_orchestration_trigger_enum(self):
        """Test OrchestrationTrigger enum values."""
        assert OrchestrationTrigger.SYSTEM_STARTUP.value == "system_startup"
        assert OrchestrationTrigger.MODULE_BUILD.value == "module_build"
        assert OrchestrationTrigger.ZEN_CODING_FLOW.value == "zen_coding_flow"
        assert len(OrchestrationTrigger) == 12  # All triggers defined
    
    def test_agent_priority_enum(self):
        """Test AgentPriority enum values and ordering."""
        assert AgentPriority.CRITICAL.value == 1
        assert AgentPriority.HIGH.value == 2
        assert AgentPriority.MEDIUM.value == 3
        assert AgentPriority.LOW.value == 4
        assert AgentPriority.BACKGROUND.value == 5
        assert AgentPriority.CRITICAL < AgentPriority.HIGH  # Priority ordering
    
    def test_orchestration_context_creation(self):
        """Test OrchestrationContext dataclass creation."""
        context = OrchestrationContext(
            trigger=OrchestrationTrigger.MODULE_BUILD,
            module_name="test_module",
            rider_influence=1.5,
            zen_flow_state="0102"
        )
        assert context.trigger == OrchestrationTrigger.MODULE_BUILD
        assert context.module_name == "test_module"
        assert context.rider_influence == 1.5
        assert context.zen_flow_state == "0102"
        assert context.recursive_depth == 0
        assert context.max_recursive_depth == 5
    
    def test_agent_task_creation(self):
        """Test AgentTask dataclass creation."""
        task = AgentTask(
            agent_name="TestAgent",
            priority=AgentPriority.HIGH,
            trigger_conditions=[OrchestrationTrigger.MODULE_BUILD],
            dependencies=["OtherAgent"],
            recursive_improvement_candidate=True,
            zen_coding_required=True
        )
        assert task.agent_name == "TestAgent"
        assert task.priority == AgentPriority.HIGH
        assert OrchestrationTrigger.MODULE_BUILD in task.trigger_conditions
        assert "OtherAgent" in task.dependencies
        assert task.recursive_improvement_candidate is True
        assert task.zen_coding_required is True


class TestAgentTaskRegistry:
    """Test agent task registry functionality."""
    
    def test_initialize_agent_tasks(self):
        """Test agent task initialization."""
        tasks = initialize_agent_tasks()
        
        # Check all expected agents are registered
        expected_agents = [
            "ComplianceAgent", "ModularizationAuditAgent", "TestingAgent",
            "ScoringAgent", "DocumentationAgent", "JanitorAgent", "ChroniclerAgent"
        ]
        for agent in expected_agents:
            assert agent in tasks
            assert isinstance(tasks[agent], AgentTask)
    
    def test_compliance_agent_configuration(self):
        """Test ComplianceAgent specific configuration."""
        tasks = initialize_agent_tasks()
        compliance_task = tasks["ComplianceAgent"]
        
        assert compliance_task.priority == AgentPriority.CRITICAL
        assert compliance_task.recursive_improvement_candidate is True
        assert compliance_task.zen_coding_required is True
        assert OrchestrationTrigger.SYSTEM_STARTUP in compliance_task.trigger_conditions
        assert OrchestrationTrigger.MODULE_BUILD in compliance_task.trigger_conditions
    
    def test_agent_dependencies(self):
        """Test agent dependency relationships."""
        tasks = initialize_agent_tasks()
        
        # ModularizationAuditAgent should depend on ComplianceAgent
        modularization_task = tasks["ModularizationAuditAgent"]
        assert "ComplianceAgent" in modularization_task.dependencies
        
        # Most agents should have no dependencies
        for agent_name, task in tasks.items():
            if agent_name != "ModularizationAuditAgent":
                assert len(task.dependencies) == 0 or task.dependencies == []


class TestAgentExecutor:
    """Test agent executor functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_agent_tasks = {
            "TestAgent": AgentTask(
                agent_name="TestAgent",
                priority=AgentPriority.HIGH,
                trigger_conditions=[OrchestrationTrigger.MODULE_BUILD],
                dependencies=[],
                recursive_improvement_candidate=False,
                zen_coding_required=False
            )
        }
        self.mock_get_agent_class = Mock()
        self.mock_wre_log = Mock()
        self.mock_project_root = Path("/test/project")
        self.executor = AgentExecutor(
            self.mock_agent_tasks,
            self.mock_get_agent_class,
            self.mock_wre_log,
            self.mock_project_root
        )
    
    @pytest.mark.asyncio
    async def test_execute_agents_recursively_single_agent(self):
        """Test executing a single agent recursively."""
        # Mock agent class and instance
        mock_agent_class = Mock()
        mock_agent_instance = Mock()
        mock_agent_class.return_value = mock_agent_instance
        mock_agent_instance.clean_workspace.return_value = {"status": "success"}
        self.mock_get_agent_class.return_value = mock_agent_class
        
        context = OrchestrationContext(trigger=OrchestrationTrigger.MODULE_BUILD)
        
        with patch.object(self.executor, 'execute_single_agent') as mock_execute:
            mock_execute.return_value = {"status": "success", "result": {"files_deleted": 5}}
            
            results = await self.executor.execute_agents_recursively(["TestAgent"], context)
            
            assert "TestAgent" in results
            assert results["TestAgent"]["status"] == "success"
            mock_execute.assert_called_once_with("TestAgent", context)
    
    @pytest.mark.asyncio
    async def test_execute_agents_with_dependencies(self):
        """Test executing agents with dependency resolution."""
        # Set up tasks with dependencies
        self.mock_agent_tasks["AgentA"] = AgentTask(
            agent_name="AgentA",
            priority=AgentPriority.HIGH,
            trigger_conditions=[OrchestrationTrigger.MODULE_BUILD],
            dependencies=[],
            recursive_improvement_candidate=False,
            zen_coding_required=False
        )
        self.mock_agent_tasks["AgentB"] = AgentTask(
            agent_name="AgentB",
            priority=AgentPriority.MEDIUM,
            trigger_conditions=[OrchestrationTrigger.MODULE_BUILD],
            dependencies=["AgentA"],
            recursive_improvement_candidate=False,
            zen_coding_required=False
        )
        
        context = OrchestrationContext(trigger=OrchestrationTrigger.MODULE_BUILD)
        
        with patch.object(self.executor, 'execute_single_agent') as mock_execute:
            mock_execute.return_value = {"status": "success"}
            
            results = await self.executor.execute_agents_recursively(["AgentB", "AgentA"], context)
            
            # AgentA should execute first (no dependencies)
            # AgentB should execute second (depends on AgentA)
            assert "AgentA" in results
            assert "AgentB" in results
            assert mock_execute.call_count == 2
    
    @pytest.mark.asyncio
    async def test_execute_deterministic_agent(self):
        """Test deterministic agent execution."""
        mock_agent = Mock()
        mock_agent.clean_workspace.return_value = {"files_deleted": 3}
        
        context = OrchestrationContext(trigger=OrchestrationTrigger.MODULE_BUILD)
        
        result = await self.executor.execute_deterministic_agent(mock_agent, "JanitorAgent", context)
        
        assert result["status"] == "success"
        assert result["result"]["files_deleted"] == 3
        mock_agent.clean_workspace.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_zen_coding_agent(self):
        """Test zen coding agent execution."""
        mock_agent = Mock()
        mock_agent.execute_with_zen_context = AsyncMock(return_value={"zen_result": "success"})
        
        context = OrchestrationContext(
            trigger=OrchestrationTrigger.ZEN_CODING_FLOW,
            zen_flow_state="0102",
            rider_influence=2.0
        )
        
        result = await self.executor.execute_zen_coding_agent(mock_agent, "ScoringAgent", context)
        
        assert result["zen_result"] == "success"
        mock_agent.execute_with_zen_context.assert_called_once()
        zen_context = mock_agent.execute_with_zen_context.call_args[0][0]
        assert zen_context["zen_flow_state"] == "0102"
        assert zen_context["rider_influence"] == 2.0


class TestRecursiveOrchestration:
    """Test the main AgenticOrchestrator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch('modules.wre_core.src.components.agentic_orchestrator.recursive_orchestration.check_agent_health'):
            with patch('modules.wre_core.src.components.agentic_orchestrator.recursive_orchestration.activate_agents_01_to_0102'):
                self.orchestrator = AgenticOrchestrator()
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        assert hasattr(self.orchestrator, 'agent_tasks')
        assert hasattr(self.orchestrator, 'executor')
        assert hasattr(self.orchestrator, 'orchestration_history')
        assert hasattr(self.orchestrator, 'zen_flow_state')
        assert self.orchestrator.zen_flow_state == "01(02)"
    
    def test_determine_required_agents(self):
        """Test determining required agents based on trigger."""
        context = OrchestrationContext(trigger=OrchestrationTrigger.MODULE_BUILD)
        
        required_agents = self.orchestrator._determine_required_agents(context)
        
        # Should include agents triggered by MODULE_BUILD
        expected_agents = ["ComplianceAgent", "ModularizationAuditAgent", "TestingAgent", 
                          "ScoringAgent", "DocumentationAgent", "ChroniclerAgent"]
        for agent in expected_agents:
            assert agent in required_agents
    
    def test_determine_required_agents_with_rider_influence(self):
        """Test agent selection with high rider influence."""
        context = OrchestrationContext(
            trigger=OrchestrationTrigger.MODULE_BUILD,
            rider_influence=2.0  # High rider influence
        )
        
        required_agents = self.orchestrator._determine_required_agents(context)
        
        # Should include more zen coding agents with high rider influence
        zen_coding_agents = ["ComplianceAgent", "ModularizationAuditAgent", "ScoringAgent", "DocumentationAgent"]
        for agent in zen_coding_agents:
            assert agent in required_agents
    
    def test_analyze_recursive_opportunities(self):
        """Test analyzing results for recursive improvement opportunities."""
        results = {
            "ComplianceAgent": {
                "status": "success",
                "result": {"violations": [{"id": "V001", "description": "Test violation"}]}
            },
            "TestingAgent": {
                "status": "success",
                "result": {"coverage": 85}
            }
        }
        
        context = OrchestrationContext(trigger=OrchestrationTrigger.COMPLIANCE_AUDIT)
        
        opportunities = self.orchestrator._analyze_recursive_opportunities(results, context)
        
        # Should find compliance fix opportunity
        assert len(opportunities) == 1
        assert opportunities[0]["agent"] == "ComplianceAgent"
        assert opportunities[0]["type"] == "compliance_fix"
    
    def test_update_zen_flow_state(self):
        """Test zen flow state transitions."""
        results = {
            "ComplianceAgent": {"status": "success"},
            "ScoringAgent": {"status": "success"},
            "DocumentationAgent": {"status": "success"}
        }
        
        context = OrchestrationContext(
            trigger=OrchestrationTrigger.MODULE_BUILD,
            zen_flow_state="01(02)"
        )
        
        self.orchestrator._update_zen_flow_state(results, context)
        
        # Should transition to 0102 state
        assert self.orchestrator.zen_flow_state == "0102"
    
    def test_get_orchestration_stats_no_history(self):
        """Test getting orchestration stats with no history."""
        stats = self.orchestrator.get_orchestration_stats()
        assert stats["status"] == "no_history"
    
    def test_get_orchestration_stats_with_history(self):
        """Test getting orchestration stats with history."""
        # Add some mock history
        self.orchestrator.orchestration_history = [
            {
                "timestamp": "2025-06-30T10:00:00",
                "trigger": "module_build",
                "zen_flow_state": "0102",
                "rider_influence": 1.0,
                "recursive_depth": 0,
                "agents_executed": ["ComplianceAgent", "TestingAgent"],
                "successful_agents": 2,
                "total_agents": 2
            }
        ]
        
        stats = self.orchestrator.get_orchestration_stats()
        
        assert stats["total_orchestrations"] == 1
        assert stats["recent_success_rate"] == 1.0
        assert stats["average_agents_per_orchestration"] == 2.0
        assert "zen_flow_state_distribution" in stats
        assert "most_common_triggers" in stats


class TestEntrypoints:
    """Test the entrypoint functions."""
    
    @pytest.mark.asyncio
    async def test_orchestrate_wsp54_agents(self):
        """Test the main orchestration entrypoint."""
        with patch('modules.wre_core.src.components.agentic_orchestrator.entrypoints.agentic_orchestrator') as mock_orchestrator:
            mock_orchestrator.orchestrate_recursively.return_value = {
                "orchestration_context": {"trigger": "module_build"},
                "agent_results": {"TestAgent": {"status": "success"}},
                "orchestration_metrics": {"total_agents_executed": 1}
            }
            
            result = await orchestrate_wsp54_agents(
                OrchestrationTrigger.MODULE_BUILD,
                module_name="test_module",
                rider_influence=1.5
            )
            
            assert result["orchestration_context"]["trigger"] == "module_build"
            assert result["agent_results"]["TestAgent"]["status"] == "success"
            mock_orchestrator.orchestrate_recursively.assert_called_once()
    
    def test_get_orchestration_stats(self):
        """Test getting orchestration statistics."""
        with patch('modules.wre_core.src.components.agentic_orchestrator.entrypoints.agentic_orchestrator') as mock_orchestrator:
            mock_orchestrator.get_orchestration_stats.return_value = {
                "total_orchestrations": 5,
                "recent_success_rate": 0.8
            }
            
            stats = get_orchestration_stats()
            
            assert stats["total_orchestrations"] == 5
            assert stats["recent_success_rate"] == 0.8
            mock_orchestrator.get_orchestration_stats.assert_called_once()


class TestIntegration:
    """Integration tests for the complete agentic orchestrator system."""
    
    @pytest.mark.asyncio
    async def test_full_orchestration_flow(self):
        """Test the complete orchestration flow from entrypoint to completion."""
        with patch('modules.wre_core.src.components.agentic_orchestrator.recursive_orchestration.check_agent_health') as mock_health:
            with patch('modules.wre_core.src.components.agentic_orchestrator.recursive_orchestration.activate_agents_01_to_0102') as mock_activate:
                mock_health.return_value = {"ComplianceAgent": True, "TestingAgent": True}
                mock_activate.return_value = {"status": "success"}
                
                with patch('modules.wre_core.src.components.agentic_orchestrator.recursive_orchestration.AgenticOrchestrator._get_agent_class') as mock_get_class:
                    mock_agent_class = Mock()
                    mock_agent_instance = Mock()
                    mock_agent_class.return_value = mock_agent_instance
                    mock_agent_instance.run_check.return_value = {"status": "success", "violations": []}
                    mock_agent_instance.check_coverage.return_value = {"coverage": 90}
                    mock_get_class.return_value = mock_agent_class
                    
                    result = await orchestrate_wsp54_agents(
                        OrchestrationTrigger.MODULE_BUILD,
                        module_name="test_module"
                    )
                    
                    assert "orchestration_context" in result
                    assert "agent_results" in result
                    assert "orchestration_metrics" in result
                    assert result["orchestration_context"]["trigger"] == "module_build"
    
    def test_modular_imports(self):
        """Test that all modular components can be imported correctly."""
        # Test that all modules can be imported
        from modules.wre_core.src.components.agentic_orchestrator import (
            orchestrate_wsp54_agents, get_orchestration_stats
        )
        from modules.wre_core.src.components.agentic_orchestrator.orchestration_context import (
            OrchestrationTrigger, AgentPriority, OrchestrationContext, AgentTask
        )
        from modules.wre_core.src.components.agentic_orchestrator.agent_task_registry import initialize_agent_tasks
        from modules.wre_core.src.components.agentic_orchestrator.agent_executor import AgentExecutor
        from modules.wre_core.src.components.agentic_orchestrator.recursive_orchestration import AgenticOrchestrator
        
        # Test that classes can be instantiated
        context = OrchestrationContext(trigger=OrchestrationTrigger.MODULE_BUILD)
        tasks = initialize_agent_tasks()
        
        assert isinstance(context, OrchestrationContext)
        assert isinstance(tasks, dict)
        assert len(tasks) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 