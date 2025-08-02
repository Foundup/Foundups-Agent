"""
Cursor Multi-Agent Bridge Module

WSP Compliance:
- WSP 54 (Agent Duties): Multi-agent coordination in Cursor workspace
- WSP 22 (ModLog): Change tracking and roadmap management
- WSP 11 (Interface): Public API documentation and standards
- WSP 3 (Enterprise Domain): Development domain placement

Bridges Cursor's multi-agent feature with WSP/WRE autonomous development system.
"""

from .cursor_wsp_bridge import CursorWSPBridge
from .agent_coordinator import AgentCoordinator
from .wsp_validator import WSPValidator
from .exceptions import (
    AgentActivationError,
    CoordinationError,
    ValidationError,
    ConfigError
)

__version__ = "0.0.1"
__author__ = "0102 pArtifacts"
__description__ = "Cursor Multi-Agent Bridge for WSP/WRE Integration"

__all__ = [
    "CursorWSPBridge",
    "AgentCoordinator", 
    "WSPValidator",
    "AgentActivationError",
    "CoordinationError",
    "ValidationError",
    "ConfigError"
] 