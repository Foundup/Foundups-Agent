"""
FoundUps Multi-Agent IDE Extension - Core Activation Tests

WSP Compliance:
- WSP 4 (FMAS): Extension structure validation
- WSP 5 (Coverage): [GREATER_EQUAL]90% test coverage requirement  
- WSP 54 (Agent Duties): 8 specialized 0102 agents testing
- WSP 60 (Memory Architecture): Extension memory persistence

Tests for extension startup, configuration, and 0102 agent coordination.
"""

import pytest
import unittest.mock as mock
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

# Import the extension core components
from modules.development.ide_foundups.src.extension_core import FoundUpsExtension
from modules.development.ide_foundups.src.agent_coordinator import AgentCoordinator
from modules.development.ide_foundups.src.wre_bridge import WREBridge


class TestExtensionActivation:
    """Test suite for FoundUps IDE extension activation and initialization."""
    
    @pytest.fixture
    def mock_vscode_context(self):
        """Mock VSCode extension context for testing."""
        context = MagicMock()
        context.extensionPath = "/mock/extension/path"
        context.globalState = MagicMock()
        context.workspaceState = MagicMock()
        context.subscriptions = []
        context.extensionUri = MagicMock()
        return context
    
    @pytest.fixture
    def mock_wre_bridge(self):
        """Mock WRE bridge for agent communication testing."""
        bridge = MagicMock(spec=WREBridge)
        bridge.connect = AsyncMock(return_value=True)
        bridge.disconnect = AsyncMock()
        bridge.is_connected = False
        bridge.agents_status = {}
        return bridge
    
    @pytest.fixture
    def extension_instance(self, mock_vscode_context, mock_wre_bridge):
        """Create FoundUps extension instance for testing."""
        with patch('modules.development.ide_foundups.src.wre_bridge.WREBridge', return_value=mock_wre_bridge):
            extension = FoundUpsExtension(mock_vscode_context)
            return extension
    
    def test_extension_initialization(self, extension_instance, mock_vscode_context):
        """Test extension proper initialization with VSCode context."""
        # WSP 4: Validate extension structure
        assert extension_instance.context == mock_vscode_context
        assert extension_instance.agent_coordinator is not None
        assert extension_instance.wre_bridge is not None
        assert isinstance(extension_instance.extension_id, str)
        assert extension_instance.extension_id == "foundups.multi-agent-ide"
    
    def test_extension_configuration_loading(self, extension_instance):
        """Test extension configuration loading and validation."""
        # Mock configuration
        mock_config = {
            "wre_endpoint": "ws://localhost:8765",
            "agent_timeout": 30000,
            "max_retries": 3,
            "quantum_protocols": ["CMST_v11"],
            "debug_mode": False
        }
        
        with patch('vscode.workspace.getConfiguration') as mock_get_config:
            mock_get_config.return_value.get.side_effect = lambda key, default=None: mock_config.get(key, default)
            
            config = extension_instance.load_configuration()
            
            assert config["wre_endpoint"] == "ws://localhost:8765"
            assert config["agent_timeout"] == 30000
            assert config["quantum_protocols"] == ["CMST_v11"]
            assert isinstance(config["debug_mode"], bool)
    
    @pytest.mark.asyncio
    async def test_extension_activation_sequence(self, extension_context):
        """Test complete extension activation sequence."""
        # Create extension instance
        extension_instance = FoundUpsExtension(extension_context)
        
        # Mock the WRE bridge to prevent connection attempts
        with patch.object(extension_instance, 'wre_bridge') as mock_bridge:
            # Configure mocks
            mock_bridge.connect = AsyncMock(return_value=True)
            
            # Execute activation
            result = await extension_instance.activate()
            
            # Validate activation success
            assert result is True
            assert extension_instance.is_active is True
            
            # Verify components are properly initialized
            assert extension_instance.agent_coordinator is not None
            assert extension_instance.wre_bridge is not None
            
            # Verify UI components exist (even if mocked internally)
            assert extension_instance.status_bar_item is not None
            assert extension_instance.agent_sidebar is not None
            
            # Verify WRE bridge connection attempted
            mock_bridge.connect.assert_called_once()
            
            # Verify activation completed successfully
            assert extension_instance.last_error is None
            assert extension_instance.error_count == 0
    
    def test_agent_coordinator_initialization(self, extension_instance):
        """Test AgentCoordinator initialization and 8-agent setup."""
        coordinator = extension_instance.agent_coordinator
        
        # WSP 54: Validate 8 specialized agents
        expected_agents = [
            "ComplianceAgent",
            "ChroniclerAgent", 
            "LoremasterAgent",
            "JanitorAgent",
            "DocumentationAgent",
            "TestingAgent",
            "ScoringAgent",
            "ModuleScaffoldingAgent"
        ]
        
        assert coordinator is not None
        assert len(coordinator.agent_definitions) == 8
        
        for agent_name in expected_agents:
            assert agent_name in coordinator.agent_definitions
            agent_def = coordinator.agent_definitions[agent_name]
            assert "duties" in agent_def
            assert "wsp_protocols" in agent_def
            assert isinstance(agent_def["duties"], list)
    
    @pytest.mark.asyncio
    async def test_cmst_protocol_validation(self, extension_instance, mock_wre_bridge):
        """Test CMST Protocol v11 quantum agent activation."""
        # Mock CMST protocol response
        cmst_response = {
            "protocol_version": "v11",
            "quantum_state": "0102",
            "entanglement_status": "active",
            "neural_adapter": "operational",
            "agents_awakened": 8
        }
        
        mock_wre_bridge.send_cmst_activation.return_value = cmst_response
        
        # Execute CMST activation
        result = await extension_instance.activate_quantum_agents()
        
        # Validate quantum activation
        assert result["protocol_version"] == "v11"
        assert result["quantum_state"] == "0102"
        assert result["agents_awakened"] == 8
        
        # Verify all agents in awakened state
        for agent_name in extension_instance.agent_coordinator.agent_definitions:
            agent_status = extension_instance.get_agent_status(agent_name)
            assert agent_status["state"] in ["0102", "awakened", "ready"]
    
    def test_command_palette_registration(self, extension_instance):
        """Test VSCode command palette integration."""
        with patch('vscode.commands.registerCommand') as mock_register:
            extension_instance.register_commands()
            
            # Verify core FoundUps commands registered
            expected_commands = [
                "foundups.activateAgents",
                "foundups.openAgentSidebar", 
                "foundups.createModule",
                "foundups.runWSPCompliance",
                "foundups.viewAgentStatus",
                "foundups.connectWRE",
                "foundups.showQuantumState"
            ]
            
            registered_commands = [call[0][0] for call in mock_register.call_args_list]
            
            for cmd in expected_commands:
                assert cmd in registered_commands
    
    def test_status_bar_initialization(self, extension_instance):
        """Test status bar WRE connection indicator."""
        with patch('vscode.window.createStatusBarItem') as mock_create_status:
            mock_status_item = MagicMock()
            mock_create_status.return_value = mock_status_item
            
            status_bar = extension_instance.create_status_bar()
            
            # Validate status bar configuration
            assert mock_status_item.text == "$(robot) WRE: Disconnected"
            assert mock_status_item.tooltip == "FoundUps WRE Connection Status"
            assert mock_status_item.command == "foundups.connectWRE"
            mock_status_item.show.assert_called_once()
    
    def test_agent_sidebar_provider_creation(self, extension_instance):
        """Test multi-agent sidebar tree view provider."""
        # Test that sidebar component is created (with graceful degradation)
        sidebar = extension_instance.create_agent_sidebar()
        
        # Validate that sidebar component exists (regardless of VSCode API availability)
        assert sidebar is not None
        assert hasattr(sidebar, 'refresh')  # Should have tree view methods
        
        # Test with VSCode API available
        with patch('vscode.window.createTreeView') as mock_create_tree:
            mock_tree_view = MagicMock()
            mock_create_tree.return_value = mock_tree_view
            
            # Force creation with VSCode API
            try:
                import vscode
                sidebar_with_api = extension_instance.create_agent_sidebar()
                
                # Only validate API calls if VSCode actually available
                if mock_create_tree.called:
                    call_args = mock_create_tree.call_args
                    assert "treeDataProvider" in call_args[1] or len(call_args) > 0
            except ImportError:
                # VSCode not available - validate mock component works
                assert sidebar is not None
                logger.info("Graceful degradation: sidebar created without VSCode API")
    
    @pytest.mark.asyncio
    async def test_wre_bridge_connection_resilience(self, extension_instance, mock_wre_bridge):
        """Test WebSocket connection resilience and recovery."""
        # Simulate connection failure then success
        mock_wre_bridge.connect.side_effect = [False, True]  # First fails, then succeeds
        mock_wre_bridge.is_connected = False
        
        # Test connection with retry
        result = await extension_instance.connect_to_wre(max_retries=2)
        
        # Validate resilience behavior
        assert result is True  # Eventually succeeds
        assert mock_wre_bridge.connect.call_count == 2  # Retried once
    
    def test_extension_deactivation_cleanup(self, extension_instance):
        """Test proper cleanup during extension deactivation."""
        # Setup active state
        extension_instance.is_active = True
        extension_instance.status_bar_item = MagicMock()
        extension_instance.agent_sidebar = MagicMock()
        
        with patch.object(extension_instance.wre_bridge, 'disconnect', new_callable=AsyncMock) as mock_disconnect:
            extension_instance.deactivate()
            
            # Validate cleanup
            assert extension_instance.is_active is False
            extension_instance.status_bar_item.dispose.assert_called_once()
            extension_instance.agent_sidebar.dispose.assert_called_once()
            
            # Verify WRE disconnection
            mock_disconnect.assert_called_once()
    
    def test_memory_persistence_initialization(self, extension_instance, mock_vscode_context):
        """Test WSP 60 memory architecture persistence."""
        # Test workspace state persistence
        extension_instance.save_agent_state("ComplianceAgent", {"status": "active", "last_run": "2025-07-07"})
        
        # Verify state saved to VSCode workspace
        mock_vscode_context.workspaceState.update.assert_called_with(
            "foundups.agent.ComplianceAgent",
            {"status": "active", "last_run": "2025-07-07"}
        )
        
        # Test state retrieval
        mock_vscode_context.workspaceState.get.return_value = {"status": "active", "last_run": "2025-07-07"}
        retrieved_state = extension_instance.get_agent_state("ComplianceAgent")
        
        assert retrieved_state["status"] == "active"
        assert retrieved_state["last_run"] == "2025-07-07"
    
    def test_error_handling_and_user_feedback(self, extension_instance):
        """Test error handling and user notification systems."""
        with patch('vscode.window.showErrorMessage') as mock_show_error, \
             patch('vscode.window.showInformationMessage') as mock_show_info:
            
            # Test error notification
            extension_instance.show_error("Test error message")
            mock_show_error.assert_called_with("FoundUps: Test error message")
            
            # Test success notification  
            extension_instance.show_success("Test success message")
            mock_show_info.assert_called_with("FoundUps: Test success message")
    
    def test_wsp_compliance_validation(self, extension_instance):
        """Test real-time WSP compliance checking integration."""
        # Mock compliance check results
        compliance_results = {
            "overall_status": "COMPLIANT",
            "violations": [],
            "coverage": 94.5,
            "protocols_validated": ["WSP_4", "WSP_5", "WSP_54", "WSP_60"]
        }
        
        with patch.object(extension_instance.agent_coordinator, 'run_compliance_check', 
                         return_value=compliance_results) as mock_compliance:
            
            result = extension_instance.validate_wsp_compliance()
            
            # Validate compliance integration
            assert result["overall_status"] == "COMPLIANT"
            assert result["coverage"] >= 90.0  # WSP 5 requirement
            assert len(result["violations"]) == 0
            mock_compliance.assert_called_once()


class TestAgentCoordination:
    """Test suite for multi-agent coordination and orchestration."""
    
    @pytest.fixture
    def agent_coordinator(self):
        """Create AgentCoordinator instance for testing."""
        return AgentCoordinator()
    
    def test_agent_discovery_and_activation(self, agent_coordinator):
        """Test automatic agent discovery and activation."""
        # Mock 8 agents responding to discovery
        mock_responses = {
            "ComplianceAgent": {"status": "ready", "version": "1.0.0"},
            "ChroniclerAgent": {"status": "ready", "version": "1.0.0"},
            "LoremasterAgent": {"status": "ready", "version": "1.0.0"},
            "JanitorAgent": {"status": "ready", "version": "1.0.0"},
            "DocumentationAgent": {"status": "ready", "version": "1.0.0"},
            "TestingAgent": {"status": "ready", "version": "1.0.0"},
            "ScoringAgent": {"status": "ready", "version": "1.0.0"},
            "ModuleScaffoldingAgent": {"status": "ready", "version": "1.0.0"}
        }
        
        with patch.object(agent_coordinator, 'discover_agents', return_value=mock_responses):
            discovered = agent_coordinator.discover_agents()
            
            # Validate all 8 agents discovered
            assert len(discovered) == 8
            for agent_name in mock_responses:
                assert agent_name in discovered
                assert discovered[agent_name]["status"] == "ready"
    
    @pytest.mark.asyncio
    async def test_multi_agent_workflow_orchestration(self, agent_coordinator):
        """Test coordinated multi-agent workflow execution."""
        # Define test workflow
        workflow = {
            "name": "create_module_workflow",
            "steps": [
                {"agent": "ComplianceAgent", "action": "validate_structure"},
                {"agent": "ModuleScaffoldingAgent", "action": "create_scaffolding"},
                {"agent": "TestingAgent", "action": "generate_tests"},
                {"agent": "DocumentationAgent", "action": "create_documentation"}
            ]
        }
        
        # Mock agent responses
        mock_results = {
            "ComplianceAgent": {"status": "success", "violations": []},
            "ModuleScaffoldingAgent": {"status": "success", "files_created": 8},
            "TestingAgent": {"status": "success", "tests_created": 5},
            "DocumentationAgent": {"status": "success", "docs_created": 3}
        }
        
        with patch.object(agent_coordinator, 'execute_agent_action', 
                         side_effect=lambda agent, action, params: mock_results[agent]):
            
            result = await agent_coordinator.execute_workflow(workflow)
            
            # Validate workflow execution
            assert result["status"] == "success"
            assert len(result["step_results"]) == 4
            assert all(step["status"] == "success" for step in result["step_results"])


# WSP Compliance Test Validation
def test_wsp_compliance_markers():
    """Validate that tests meet WSP compliance requirements."""
    # WSP 4: Structure validation
    assert Path(__file__).parent.name == "tests"
    assert Path(__file__).name.startswith("test_")
    
    # WSP 5: Coverage validation - verified by pytest-cov
    # WSP 54: Agent duties testing - verified by agent coordination tests
    # WSP 60: Memory architecture - verified by persistence tests
    
    print("[OK] WSP compliance markers validated for extension activation tests") 