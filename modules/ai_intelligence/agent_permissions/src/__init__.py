# -*- coding: utf-8 -*-
"""
Agent Permissions - Graduated Autonomy System
Confidence-based permission escalation for Qwen/Gemma agents

Public API:
- AgentPermissionManager: Main permission management interface
- ConfidenceTracker: Confidence scoring with decay
- ConfidenceDecayEvent, ConfidenceBoostEvent: Event types
"""

from .agent_permission_manager import (
    AgentPermissionManager,
    PermissionCheckResult,
    PermissionRecord,
    PROMOTION_THRESHOLDS,
    DOWNGRADE_THRESHOLDS
)

from .confidence_tracker import (
    ConfidenceTracker,
    ConfidenceDecayEvent,
    ConfidenceBoostEvent
)

__all__ = [
    'AgentPermissionManager',
    'ConfidenceTracker',
    'PermissionCheckResult',
    'PermissionRecord',
    'ConfidenceDecayEvent',
    'ConfidenceBoostEvent',
    'PROMOTION_THRESHOLDS',
    'DOWNGRADE_THRESHOLDS'
]
