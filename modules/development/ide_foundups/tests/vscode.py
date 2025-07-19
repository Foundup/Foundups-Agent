"""Mock VSCode module for testing."""

from unittest.mock import Mock

# Create mock objects
workspace = Mock()
window = Mock()
commands = Mock()

# Mock configuration
workspace.getConfiguration.return_value = Mock()
workspace.getConfiguration.return_value.get.return_value = "mock_value"

# Mock UI elements
window.createStatusBarItem.return_value = Mock()
window.createTreeView.return_value = Mock()
window.showInformationMessage = Mock()
window.showErrorMessage = Mock()

# Mock commands
commands.registerCommand = Mock()
commands.executeCommand = Mock()

# Mock constants
StatusBarAlignment = Mock()
StatusBarAlignment.Left = 1
StatusBarAlignment.Right = 2 