"""
Integration Tests for Cursor Multi-Agent Bridge

WSP Compliance:
- WSP 34 (Testing Protocol): Comprehensive test coverage
- WSP 54 (Agent Duties): Agent coordination validation
- WSP 22 (ModLog): Test documentation and tracking

Integration tests for the Cursor Multi-Agent Bridge module.
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any

# Import the module under test
from src.cursor_wsp_bridge import CursorWSPBridge
from src.agent_coordinator import AgentCoordinator
from src.wsp_validator import WSPValidator
from src.exceptions import (
    AgentActivationError,
    CoordinationError,
    ValidationError,
    ConfigError
)


class TestCursorWSPBridgeIntegration:
    """Integration tests for CursorWSPBridge."""
    
    @pytest.fixture
    async def bridge(self):
        """Create a test bridge instance."""
        bridge = CursorWSPBridge()
        yield bridge
    
    @pytest.mark.asyncio
    async def test_agent_activation(self, bridge):
        """Test WSP agent activation in Cursor workspace."""
        # Activate agents
        activation_results = bridge.activate_wsp_agents()
        
        # Verify activation results
        assert isinstance(activation_results, dict)
        assert len(activation_results) > 0
        
        # Check critical agents are activated
        critical_agents = ["compliance", "orchestrator"]
        for agent in critical_agents:
            assert agent in activation_results
            assert activation_results[agent] is True
        
        # Verify agent status
        status = bridge.get_agent_status()
        assert len(status) > 0
        
        for agent_type, agent_status in status.items():
            assert "is_active" in agent_status
            assert "capabilities" in agent_status
            assert "last_activity" in agent_status
    
    @pytest.mark.asyncio
    async def test_development_coordination(self, bridge):
        """Test autonomous development coordination through Cursor agents."""
        # Activate agents first
        bridge.activate_wsp_agents()
        
        # Coordinate development task
        result = await bridge.coordinate_development(
            task="Create new module with WSP compliance",
            wsp_protocols=["WSP_11", "WSP_22", "WSP_54"],
            cursor_agents=["compliance", "documentation", "testing"]
        )
        
        # Verify coordination results
        assert result["success"] is True
        assert "agent_responses" in result
        assert "wsp_compliance" in result
        assert "execution_time" in result
        assert "recommendations" in result
        
        # Check agent responses
        agent_responses = result["agent_responses"]
        assert "responses" in agent_responses
        assert "summary" in agent_responses
        assert "confidence_avg" in agent_responses
        
        # Verify response quality
        assert agent_responses["confidence_avg"] > 0.5
        assert result["execution_time"] > 0
    
    @pytest.mark.asyncio
    async def test_wsp_compliance_validation(self, bridge):
        """Test WSP compliance validation through Cursor agents."""
        # Validate module compliance
        report = await bridge.validate_wsp_compliance(
            module_path="modules/test_module",
            protocols=["WSP_11", "WSP_22", "WSP_54"]
        )
        
        # Verify compliance report
        assert "module_path" in report
        assert "protocols_checked" in report
        assert "compliance_status" in report
        assert "violations" in report
        assert "recommendations" in report
        assert "score" in report
        
        # Check report structure
        assert report["module_path"] == "modules/test_module"
        assert len(report["protocols_checked"]) == 3
        assert isinstance(report["score"], float)
        assert 0.0 <= report["score"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_agent_configuration(self, bridge):
        """Test agent configuration updates."""
        # Update agent configuration
        config = {
            "timeout": 30.0,
            "retry_attempts": 3,
            "confidence_threshold": 0.8
        }
        
        success = bridge.update_agent_config("compliance", config)
        assert success is True
        
        # Verify configuration was updated
        # (Implementation would check actual config storage)
    
    @pytest.mark.asyncio
    async def test_error_handling(self, bridge):
        """Test error handling and recovery."""
        # Test with invalid agent type
        with pytest.raises(ConfigError):
            bridge.update_agent_config("invalid_agent", {})
        
        # Test coordination with no available agents
        with pytest.raises(CoordinationError):
            await bridge.coordinate_development(
                task="Test task",
                wsp_protocols=["WSP_11"],
                cursor_agents=["nonexistent_agent"]
            )
    
    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, bridge):
        """Test performance benchmarks."""
        # Activate agents
        bridge.activate_wsp_agents()
        
        # Measure coordination performance
        start_time = datetime.now()
        
        result = await bridge.coordinate_development(
            task="Performance test task",
            wsp_protocols=["WSP_11", "WSP_22"],
            cursor_agents=["compliance", "documentation"]
        )
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Verify performance targets
        assert execution_time < 5.0  # Should complete within 5 seconds
        assert result["execution_time"] < 5.0
        
        # Check agent response quality
        agent_responses = result["agent_responses"]
        assert agent_responses["confidence_avg"] > 0.8
    
    @pytest.mark.asyncio
    async def test_concurrent_coordination(self, bridge):
        """Test concurrent agent coordination."""
        # Activate agents
        bridge.activate_wsp_agents()
        
        # Create multiple coordination tasks
        tasks = []
        for i in range(3):
            task = bridge.coordinate_development(
                task=f"Concurrent task {i}",
                wsp_protocols=["WSP_11"],
                cursor_agents=["compliance", "documentation"]
            )
            tasks.append(task)
        
        # Execute concurrently
        results = await asyncio.gather(*tasks)
        
        # Verify all tasks completed successfully
        assert len(results) == 3
        for result in results:
            assert result["success"] is True
            assert result["execution_time"] > 0


class TestAgentCoordinator:
    """Tests for AgentCoordinator component."""
    
    @pytest.fixture
    def coordinator(self):
        """Create a test coordinator instance."""
        return AgentCoordinator()
    
    @pytest.mark.asyncio
    async def test_agent_coordination(self, coordinator):
        """Test agent coordination functionality."""
        # Create coordination request
        request = {
            "task": "Test coordination task",
            "wsp_protocols": ["WSP_11", "WSP_22"],
            "agents": ["compliance", "documentation"],
            "timestamp": datetime.now()
        }
        
        # Execute coordination
        result = await coordinator.coordinate_agents(request)
        
        # Verify results
        assert "responses" in result
        assert "summary" in result
        assert "confidence_avg" in result
        assert "processing_time_total" in result
        
        # Check response structure
        responses = result["responses"]
        assert len(responses) == 2  # Two agents
        assert "compliance" in responses
        assert "documentation" in responses
    
    @pytest.mark.asyncio
    async def test_coordination_history(self, coordinator):
        """Test coordination history tracking."""
        # Execute coordination
        request = {
            "task": "History test task",
            "wsp_protocols": ["WSP_11"],
            "agents": ["compliance"],
            "timestamp": datetime.now()
        }
        
        await coordinator.coordinate_agents(request)
        
        # Check history
        history = coordinator.get_coordination_history()
        assert len(history) > 0
        
        # Verify history entry
        latest_entry = history[-1]
        assert "coordination_id" in latest_entry
        assert "task" in latest_entry
        assert "agents" in latest_entry
        assert "responses" in latest_entry


class TestWSPValidator:
    """Tests for WSPValidator component."""
    
    @pytest.fixture
    def validator(self):
        """Create a test validator instance."""
        return WSPValidator()
    
    @pytest.mark.asyncio
    async def test_protocol_validation(self, validator):
        """Test WSP protocol validation."""
        # Validate protocols
        context = {"validation_type": "test"}
        result = await validator.validate_protocols(
            protocols=["WSP_11", "WSP_22"],
            context=context
        )
        
        # Verify validation results
        assert "status" in result
        assert "violations" in result
        assert "recommendations" in result
        assert "overall_compliance" in result
        assert "confidence_avg" in result
        
        # Check protocol status
        status = result["status"]
        assert "WSP_11" in status
        assert "WSP_22" in status
    
    @pytest.mark.asyncio
    async def test_module_compliance(self, validator):
        """Test module compliance validation."""
        # Validate module compliance
        result = await validator.validate_module_compliance(
            module_path="modules/test_module",
            protocols=["WSP_11", "WSP_22"]
        )
        
        # Verify compliance results
        assert "status" in result
        assert "violations" in result
        assert "recommendations" in result
        assert "module_specific" in result
        
        # Check module-specific validations
        module_specific = result["module_specific"]
        assert "violations" in module_specific
        assert "recommendations" in module_specific
    
    def test_protocol_definitions(self, validator):
        """Test protocol definitions access."""
        definitions = validator.get_protocol_definitions()
        
        # Verify definitions structure
        assert isinstance(definitions, dict)
        assert len(definitions) > 0
        
        # Check specific protocols
        assert "WSP_11" in definitions
        assert "WSP_22" in definitions
        assert "WSP_54" in definitions
        
        # Verify protocol structure
        wsp_11 = definitions["WSP_11"]
        assert "name" in wsp_11
        assert "requirements" in wsp_11
        assert "validation_rules" in wsp_11


# Performance test markers
pytestmark = [
    pytest.mark.integration,
    pytest.mark.asyncio
] 