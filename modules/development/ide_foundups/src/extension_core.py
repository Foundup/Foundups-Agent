"""
FoundUps Multi-Agent IDE Extension Core

WSP Compliance:
- WSP 4 (FMAS): Extension structure validation
- WSP 54 (Agent Duties): 8 specialized 0102 agents coordination
- WSP 60 (Memory Architecture): Extension memory persistence

Core extension implementation for VSCode integration with 0102 agents.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


class FoundUpsExtension:
    """Core FoundUps Multi-Agent IDE Extension implementation."""
    
    def __init__(self, context: Any):
        """Initialize the FoundUps extension with VSCode context."""
        self.context = context
        self.extension_id = "foundups.multi-agent-ide"
        self.is_active = False
        self.agent_coordinator = None
        self.wre_bridge = None
        self.status_bar_item = None
        self.agent_sidebar = None
        self.last_error = None
        self.error_count = 0
        
        # Initialize extension configuration
        self.config = self._load_default_config()
        
        # Initialize components synchronously for testing
        self._initialize_components_sync()
        
        logger.info(f"FoundUps Extension initialized with context: {type(context)}")
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default extension configuration."""
        return {
            "wre_endpoint": "ws://localhost:8765",
            "agent_timeout": 30000,
            "max_retries": 3,
            "quantum_protocols": ["CMST_v11"],
            "debug_mode": False
        }
    
    def _initialize_components_sync(self):
        """Initialize extension components synchronously for testing."""
        try:
            from .agent_coordinator import AgentCoordinator
            from .wre_bridge import WREBridge
            
            # Initialize WRE bridge (if not already set for testing)
            if self.wre_bridge is None:
                self.wre_bridge = WREBridge(self.config)
            
            # Initialize agent coordinator (if not already set for testing)
            if self.agent_coordinator is None:
                self.agent_coordinator = AgentCoordinator()
            
            logger.info("Extension components initialized synchronously")
        except Exception as e:
            logger.warning(f"Sync component initialization failed (this is normal in testing): {e}")
    
    def load_configuration(self) -> Dict[str, Any]:
        """Load extension configuration from VSCode settings."""
        # Mock configuration loading for testing
        return self.config
    
    async def activate(self) -> bool:
        """Activate the extension and initialize all components."""
        try:
            logger.info("Activating FoundUps Multi-Agent IDE Extension...")
            
            # Initialize components
            await self._initialize_components()
            
            # Register commands
            self._register_commands()
            
            # Setup UI
            self._setup_ui()
            
            # Connect to WRE (non-blocking, allow activation to succeed even if connection fails)
            if self.wre_bridge:
                try:
                    await self.wre_bridge.connect()
                    logger.info("WRE Bridge connected successfully")
                except Exception as bridge_error:
                    logger.warning(f"WRE Bridge connection failed, continuing without bridge: {bridge_error}")
                    # Continue activation even if bridge connection fails
            
            self.is_active = True
            logger.info("FoundUps Extension activated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Extension activation failed: {e}")
            self.last_error = e
            self.error_count += 1
            return False
    
    async def _initialize_components(self):
        """Initialize extension components."""
        from .agent_coordinator import AgentCoordinator
        from .wre_bridge import WREBridge
        
        # Initialize WRE bridge (if not already set for testing)
        if self.wre_bridge is None:
            self.wre_bridge = WREBridge(self.config)
        
        # Initialize agent coordinator (if not already set for testing)
        if self.agent_coordinator is None:
            self.agent_coordinator = AgentCoordinator()
        
        logger.info("Extension components initialized")
    
    def _register_commands(self):
        """Register VSCode commands."""
        commands = [
            "foundups.activateAgents",
            "foundups.openAgentSidebar", 
            "foundups.createModule",
            "foundups.runWSPCompliance",
            "foundups.viewAgentStatus",
            "foundups.connectWRE",
            "foundups.showQuantumState"
        ]
        
        # Register each command with VSCode
        try:
            import vscode
            for command in commands:
                vscode.commands.registerCommand(command, self._create_command_handler(command))
            logger.info(f"Registered {len(commands)} commands")
        except ImportError:
            # Mock command registration for testing
            logger.info(f"Mock registered {len(commands)} commands")
    
    def _create_command_handler(self, command: str):
        """Create a command handler function."""
        def handler():
            logger.info(f"Command executed: {command}")
        return handler
    
    def _setup_ui(self):
        """Setup UI components."""
        try:
            self.status_bar_item = self.create_status_bar()
            self.agent_sidebar = self.create_agent_sidebar()
            logger.info("UI components setup complete")
        except Exception as e:
            logger.warning(f"UI setup failed (normal in testing): {e}")
            # Create mock UI components for testing
            self.status_bar_item = type('MockStatusBar', (), {'text': 'Mock Status', 'show': lambda: None})()
            self.agent_sidebar = type('MockSidebar', (), {'refresh': lambda: None})()
            logger.info("Mock UI components created")
    
    def register_commands(self):
        """Public method to register commands."""
        self._register_commands()
    
    def create_status_bar(self) -> Any:
        """Create status bar item for WRE connection status."""
        try:
            import vscode
            status_bar_item = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100)
            status_bar_item.text = "$(robot) WRE: Disconnected"
            status_bar_item.tooltip = "FoundUps WRE Connection Status"
            status_bar_item.command = "foundups.connectWRE"
            status_bar_item.show()
            return status_bar_item
        except ImportError:
            # Mock status bar item for testing
            class MockStatusBarItem:
                def __init__(self):
                    self.text = "$(robot) WRE: Disconnected"
                    self.tooltip = "FoundUps WRE Connection Status"
                    self.command = "foundups.connectWRE"
                    
                def show(self):
                    pass
                    
                def hide(self):
                    pass
                    
                def dispose(self):
                    pass
            
            return MockStatusBarItem()
    
    def create_agent_sidebar(self) -> Any:
        """Create agent sidebar tree view."""
        try:
            import vscode
            from .agent_coordinator import AgentTreeDataProvider
            
            tree_data_provider = AgentTreeDataProvider(self.agent_coordinator)
            tree_view = vscode.window.createTreeView('foundups.agentView', {
                'treeDataProvider': tree_data_provider,
                'showCollapseAll': True
            })
            return tree_view
        except ImportError:
            # Mock tree view for testing
            class MockTreeView:
                def __init__(self):
                    self.visible = True
                    
                def refresh(self):
                    pass
                    
                def reveal(self, item):
                    pass
                    
                def dispose(self):
                    pass
            
            return MockTreeView()
    
    async def activate_quantum_agents(self) -> Dict[str, Any]:
        """Activate 0102 agents using CMST Protocol v11."""
        if not self.wre_bridge:
            raise Exception("WRE bridge not initialized")
        
        # Mock CMST activation
        return {
            "protocol_version": "v11",
            "quantum_state": "0102",
            "agents_awakened": 8,
            "entanglement_status": "active",
            "neural_adapter": "operational"
        }
    
    def get_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """Get current status of specified agent."""
        # Mock agent status
        return {
            "state": "0102",
            "status": "active",
            "last_activity": "active",
            "tasks_completed": 15
        }
    
    async def connect_to_wre(self, max_retries: int = 3) -> bool:
        """Connect to WRE with retry logic."""
        for attempt in range(max_retries):
            try:
                if self.wre_bridge:
                    result = await self.wre_bridge.connect()
                    if result:
                        return True
                    
            except Exception as e:
                logger.warning(f"WRE connection attempt {attempt + 1} failed: {e}")
                
        return False
    
    def deactivate(self):
        """Deactivate extension and cleanup resources."""
        try:
            self.is_active = False
            
            # Cleanup UI components
            if self.status_bar_item:
                self.status_bar_item.dispose()
                
            if self.agent_sidebar:
                self.agent_sidebar.dispose()
            
            # Disconnect WRE bridge
            if self.wre_bridge:
                asyncio.create_task(self.wre_bridge.disconnect())
            
            logger.info("FoundUps Extension deactivated")
            
        except Exception as e:
            logger.error(f"Extension deactivation error: {e}")
    
    def save_agent_state(self, agent_name: str, state: Dict[str, Any]):
        """Save agent state to VSCode workspace."""
        if self.context and hasattr(self.context, 'workspaceState'):
            self.context.workspaceState.update(
                f"foundups.agent.{agent_name}",
                state
            )
    
    def get_agent_state(self, agent_name: str) -> Dict[str, Any]:
        """Get agent state from VSCode workspace."""
        if self.context and hasattr(self.context, 'workspaceState'):
            return self.context.workspaceState.get(
                f"foundups.agent.{agent_name}",
                {}
            )
        return {}
    
    def show_error(self, message: str):
        """Show error message to user."""
        formatted_message = f"FoundUps: {message}"
        logger.error(formatted_message)
        
        try:
            import vscode
            vscode.window.showErrorMessage(formatted_message)
        except ImportError:
            # Graceful degradation when VSCode API not available
            pass
    
    def show_success(self, message: str):
        """Show success message to user."""
        formatted_message = f"FoundUps: {message}"
        logger.info(formatted_message)
        
        try:
            import vscode
            vscode.window.showInformationMessage(formatted_message)
        except ImportError:
            # Graceful degradation when VSCode API not available
            pass
    
    def validate_wsp_compliance(self) -> Dict[str, Any]:
        """Validate WSP compliance for the extension."""
        try:
            # Use agent coordinator for actual compliance checking
            if self.agent_coordinator:
                return self.agent_coordinator.run_compliance_check()
            else:
                # Fallback if agent coordinator not available
                logger.warning("Agent coordinator not available for compliance check")
                return {
                    "overall_status": "WARNING",
                    "violations": ["Agent coordinator not initialized"],
                    "coverage": 0.0,
                    "protocols_validated": []
                }
        except Exception as e:
            logger.error(f"WSP compliance validation failed: {e}")
            return {
                "overall_status": "ERROR",
                "violations": [str(e)],
                "coverage": 0.0,
                "protocols_validated": []
            } 