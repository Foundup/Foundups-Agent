"""
Agent Management Package
Multi-agent coordination and identity management system.
"""

from .src.multi_agent_manager import (
    MultiAgentManager,
    AgentIdentity,
    AgentSession,
    SameAccountDetector,
    AgentRegistry,
    get_agent_manager,
    show_agent_status
)

__version__ = "1.0.0"
__all__ = [
    'MultiAgentManager',
    'AgentIdentity',
    'AgentSession', 
    'SameAccountDetector',
    'AgentRegistry',
    'get_agent_manager',
    'show_agent_status'
] 