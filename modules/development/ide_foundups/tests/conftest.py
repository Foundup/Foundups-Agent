import sys
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

# Add module path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock VSCode module before any imports
mock_vscode = Mock()
mock_vscode.workspace = Mock()
mock_vscode.window = Mock()
mock_vscode.commands = Mock()
mock_vscode.StatusBarAlignment = Mock()
mock_vscode.StatusBarAlignment.Left = 1
mock_vscode.StatusBarAlignment.Right = 2

# Configure workspace mock
mock_vscode.workspace.getConfiguration.return_value = Mock()
mock_vscode.workspace.getConfiguration.return_value.get = Mock(return_value="mock_value")

# Configure window mocks
mock_vscode.window.createStatusBarItem.return_value = Mock()
mock_vscode.window.createTreeView.return_value = Mock()
mock_vscode.window.showInformationMessage = Mock()
mock_vscode.window.showErrorMessage = Mock()
mock_vscode.window.showWarningMessage = Mock()

# Configure commands mock
mock_vscode.commands.registerCommand = Mock()
mock_vscode.commands.executeCommand = Mock()

# Install the mock in sys.modules
sys.modules['vscode'] = mock_vscode

@pytest.fixture
def vscode_mock():
    """Provide VSCode mock for tests."""
    return mock_vscode

@pytest.fixture  
def extension_context():
    """Mock VSCode extension context."""
    context = Mock()
    context.subscriptions = []
    context.workspaceState = Mock()
    context.globalState = Mock()
    context.extensionPath = "/mock/extension/path"
    return context

@pytest.fixture
def mock_config():
    """Default test configuration."""
    return {
        "wre_endpoint": "ws://localhost:8765",
        "agent_timeout": 30000,
        "max_retries": 3,
        "quantum_protocols": ["CMST_v11"],
        "debug_mode": True
    } 