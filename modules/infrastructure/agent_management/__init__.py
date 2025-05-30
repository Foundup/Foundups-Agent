"""
Agent Management Module
Handles multi-agent coordination and identity management for FoundUps Agent.
"""

from .agent_management.src.multi_agent_manager import (
    MultiAgentManager,
    AgentIdentity,
    AgentSession,
    get_agent_manager,
    show_agent_status
)

__all__ = [
    'MultiAgentManager',
    'AgentIdentity', 
    'AgentSession',
    'get_agent_manager',
    'show_agent_status'
] 