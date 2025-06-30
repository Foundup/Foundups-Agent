"""
Agent Management Source Package
Core implementation of multi-agent management system.
"""

from .multi_agent_manager import (
    MultiAgentManager,
    AgentIdentity,
    AgentSession,
    SameAccountDetector,
    AgentRegistry,
    get_agent_manager,
    show_agent_status
)

__all__ = [
    'MultiAgentManager',
    'AgentIdentity',
    'AgentSession',
    'SameAccountDetector', 
    'AgentRegistry',
    'get_agent_manager',
    'show_agent_status'
] 