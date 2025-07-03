"""
Tests for WRE Core POC orchestration

Tests the minimal POC orchestration layer:
- Initialization and clean state
- Module menu functionality  
- Session management
- Workflow orchestration
- Error handling

WSP 33 Implementation - POC Testing
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.wre_core_poc import WRECorePOC
from modules.wre_core.src.components.agentic_orchestrator.orchestration_context import OrchestrationTrigger


class TestWRECorePOCInitialization:
    """Test WRE Core POC initialization and setup."""
    
    def test_poc_initialization(self):
        """Test POC initializes correctly with required components."""
        poc = WRECorePOC(project_root)
        
        assert poc.project_root == project_root
        assert poc.session_manager is not None
        assert poc.available_modules is not None
        assert poc.active_session_id is None
        assert len(poc.available_modules) == 8  # Updated for WSP2 modules (5 + 3 WSP2)
    
    def test_available_modules_structure(self):
        """Test available modules have correct structure."""
        poc = WRECorePOC(project_root)
        
        for key, module in poc.available_modules.items():
            assert "name" in module
            assert "description" in module
            assert "trigger" in module
            assert "requires_module_name" in module
            # WSP2 modules use string triggers, others use OrchestrationTrigger
            trigger = module["trigger"]
            assert isinstance(trigger, OrchestrationTrigger) or (isinstance(trigger, str) and trigger.startswith("wsp2_"))
            assert isinstance(module["requires_module_name"], bool)
    
    def test_module_triggers_mapping(self):
        """Test module triggers are correctly mapped."""
        poc = WRECorePOC(project_root)
        
        expected_triggers = {
            "1": OrchestrationTrigger.COMPLIANCE_AUDIT,
            "2": OrchestrationTrigger.MODULE_BUILD,
            "3": OrchestrationTrigger.HEALTH_CHECK,
            "4": OrchestrationTrigger.TESTING_CYCLE,
            "5": OrchestrationTrigger.DOCUMENTATION_SYNC
        }
        
        for key, expected_trigger in expected_triggers.items():
            assert poc.available_modules[key]["trigger"] == expected_trigger


class TestSessionManagement:
    """Test POC session management functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.poc = WRECorePOC(project_root)
    
    def test_session_status_no_active_session(self):
        """Test session status when no session is active."""
        status = self.poc.get_session_status()
        
        assert status["status"] == "no_active_session"
    
    @patch('modules.wre_core.src.wre_core_poc.SessionManager')
    def test_session_status_active_session(self, mock_session_manager):
        """Test session status with active session."""
        # Mock active session
        mock_manager = Mock()
        mock_manager.sessions = {
            "test_session": {
                "start_time": "2025-01-01T10:00:00",
                "operations_count": 3,
                "modules_accessed": ["module1", "module2"],
                "achievements": ["achievement1"]
            }
        }
        mock_session_manager.return_value = mock_manager
        
        poc = WRECorePOC(project_root)
        poc.active_session_id = "test_session"
        
        status = poc.get_session_status()
        
        assert status["status"] == "active"
        assert status["session_id"] == "test_session"
        assert status["operations_count"] == 3
        assert status["modules_accessed"] == 2
        assert status["achievements"] == 1
    
    def test_session_status_session_not_found(self):
        """Test session status when session ID exists but session data doesn't."""
        self.poc.active_session_id = "nonexistent_session"
        
        status = self.poc.get_session_status()
        
        assert status["status"] == "session_not_found"


class TestModuleWorkflowOrchestration:
    """Test module workflow orchestration functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.poc = WRECorePOC(project_root)
    
    @pytest.mark.asyncio
    async def test_initiate_workflow_invalid_module(self):
        """Test workflow initiation with invalid module key."""
        result = await self.poc.initiate_module_workflow("invalid")
        
        assert "error" in result
        assert "Invalid module key" in result["error"]
    
    @pytest.mark.asyncio
    @patch('modules.wre_core.src.wre_core_poc.orchestrate_wsp54_agents')
    async def test_initiate_workflow_success_no_module_name(self, mock_orchestrate):
        """Test successful workflow initiation without module name requirement."""
        # Mock orchestration result
        mock_orchestrate.return_value = {
            "orchestration_context": {"trigger": "compliance_audit"},
            "agent_results": {"ComplianceAgent": {"status": "success"}},
            "orchestration_metrics": {"total_agents_executed": 1}
        }
        
        result = await self.poc.initiate_module_workflow("1")  # Compliance check
        
        assert result["status"] == "completed"
        assert result["workflow"] == "Module Compliance Check"
        assert "result" in result
        mock_orchestrate.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('builtins.input', return_value="test_module")
    @patch('modules.wre_core.src.wre_core_poc.orchestrate_wsp54_agents')
    async def test_initiate_workflow_success_with_module_name(self, mock_orchestrate, mock_input):
        """Test successful workflow initiation with module name requirement."""
        # Mock orchestration result
        mock_orchestrate.return_value = {
            "orchestration_context": {"trigger": "module_build"},
            "agent_results": {"TestingAgent": {"status": "success"}},
            "orchestration_metrics": {"total_agents_executed": 2}
        }
        
        result = await self.poc.initiate_module_workflow("2")  # New module build
        
        assert result["status"] == "completed"
        assert result["workflow"] == "New Module Build"
        mock_orchestrate.assert_called_once_with(
            trigger=OrchestrationTrigger.MODULE_BUILD,
            module_name="test_module"
        )
    
    @pytest.mark.asyncio
    @patch('builtins.input', return_value="")
    async def test_initiate_workflow_missing_module_name(self, mock_input):
        """Test workflow initiation with missing required module name."""
        result = await self.poc.initiate_module_workflow("2")  # New module build
        
        assert "error" in result
        assert "Module name is required" in result["error"]
    
    @pytest.mark.asyncio
    @patch('modules.wre_core.src.wre_core_poc.orchestrate_wsp54_agents')
    async def test_initiate_workflow_orchestration_error(self, mock_orchestrate):
        """Test workflow initiation with orchestration error."""
        # Mock orchestration error
        mock_orchestrate.side_effect = Exception("Orchestration failed")
        
        result = await self.poc.initiate_module_workflow("1")
        
        assert result["status"] == "error"
        assert "Orchestration failed" in result["error"]
    
    def test_display_workflow_result_success(self, capsys):
        """Test displaying successful workflow results."""
        result = {
            "status": "completed",
            "workflow": "Test Workflow",
            "result": {
                "orchestration_metrics": {
                    "total_agents_executed": 3,
                    "success_rate": 0.9
                }
            }
        }
        
        self.poc.display_workflow_result(result)
        
        captured = capsys.readouterr()
        assert "✅ Workflow Completed Successfully" in captured.out
        assert "Test Workflow" in captured.out
        assert "Agents Executed: 3" in captured.out
    
    def test_display_workflow_result_error(self, capsys):
        """Test displaying error workflow results."""
        result = {
            "status": "error",
            "workflow": "Failed Workflow",
            "error": "Something went wrong"
        }
        
        self.poc.display_workflow_result(result)
        
        captured = capsys.readouterr()
        assert "❌ Workflow Failed" in captured.out
        assert "Failed Workflow" in captured.out
        assert "Something went wrong" in captured.out


class TestMenuDisplay:
    """Test menu display functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.poc = WRECorePOC(project_root)
    
    def test_display_bare_board_menu(self, capsys):
        """Test bare board menu display."""
        self.poc.display_bare_board_menu()
        
        captured = capsys.readouterr()
        assert "🟢 WRE Core POC - Module Orchestration" in captured.out
        assert "Available Workflows:" in captured.out
        assert "Module Compliance Check" in captured.out
        assert "New Module Build" in captured.out
        assert "System Health Check" in captured.out
        assert "0. Exit POC" in captured.out
        assert "s. Session Status" in captured.out
        assert "h. Orchestration History" in captured.out
    
    def test_display_session_status_no_session(self, capsys):
        """Test session status display with no active session."""
        self.poc.display_session_status()
        
        captured = capsys.readouterr()
        assert "📊 Session Status" in captured.out
        assert "No active session" in captured.out
    
    @patch('modules.wre_core.src.wre_core_poc.get_orchestration_stats')
    def test_display_orchestration_history_no_history(self, mock_get_stats, capsys):
        """Test orchestration history display with no history."""
        mock_get_stats.return_value = {"status": "no_history"}
        
        self.poc.display_orchestration_history()
        
        captured = capsys.readouterr()
        assert "📈 Orchestration History" in captured.out
        assert "No orchestration history available" in captured.out
    
    @patch('modules.wre_core.src.wre_core_poc.get_orchestration_stats')
    def test_display_orchestration_history_with_data(self, mock_get_stats, capsys):
        """Test orchestration history display with historical data."""
        mock_get_stats.return_value = {
            "total_orchestrations": 5,
            "recent_success_rate": 0.8,
            "average_agents_per_orchestration": 2.5,
            "zen_flow_state_distribution": {
                "01(02)": 3,
                "0102": 2
            }
        }
        
        self.poc.display_orchestration_history()
        
        captured = capsys.readouterr()
        assert "Total Orchestrations: 5" in captured.out
        assert "Success Rate: 80.0%" in captured.out
        assert "Avg Agents/Session: 2.5" in captured.out
        assert "Zen Flow States:" in captured.out


class TestPOCCompliance:
    """Test POC compliance with 0102 requirements."""
    
    def test_minimalism_enforcement(self):
        """Test that POC implements only essential features."""
        poc = WRECorePOC(project_root)
        
        # Should have minimal module count (not excessive)
        assert len(poc.available_modules) <= 10
        
        # Should not have automated features
        assert not hasattr(poc, 'auto_orchestration')
        assert not hasattr(poc, 'background_processes')
        assert not hasattr(poc, 'agent_auto_instantiation')
    
    def test_manual_control_only(self):
        """Test that all workflows require manual initiation."""
        poc = WRECorePOC(project_root)
        
        # All modules should be manually triggered
        for module in poc.available_modules.values():
            # No auto-trigger mechanisms
            assert "auto_trigger" not in module
            assert "schedule" not in module
            assert "background" not in module
    
    def test_clean_state_initialization(self):
        """Test POC initializes in clean state."""
        poc = WRECorePOC(project_root)
        
        # Should start with no active sessions
        assert poc.active_session_id is None
        
        # Should have minimal state
        assert len(poc.__dict__) <= 5  # project_root, session_manager, available_modules, active_session_id
    
    def test_no_agent_auto_instantiation(self):
        """Test that agents are not auto-instantiated."""
        poc = WRECorePOC(project_root)
        
        # Should not have pre-instantiated agents
        assert not hasattr(poc, 'active_agents')
        assert not hasattr(poc, 'agent_pool')
        assert not hasattr(poc, 'background_agents')


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 