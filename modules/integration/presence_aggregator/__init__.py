# modules/integration/presence_aggregator/__init__.py

"""
Presence Aggregator Module
WSP Protocol: WSP 54 (Agent Coordination), WSP 42 (Cross-Domain Integration)

Cross-platform presence monitoring and aggregation with confidence scoring.
Part of Meeting Orchestration Block strategic decomposition.
"""

from .src.presence_aggregator import (
    PresenceAggregator,
    UnifiedAvailabilityProfile,
    PlatformPresence,
    PresenceStatus,
    PlatformType,
    create_presence_aggregator
)

__all__ = [
    'PresenceAggregator',
    'UnifiedAvailabilityProfile',
    'PlatformPresence', 
    'PresenceStatus',
    'PlatformType',
    'create_presence_aggregator'
]

__version__ = "0.1.0"
__description__ = "Cross-Platform Presence Aggregation System"

# WSP Recursive Instructions
"""
🌀 Windsurf Protocol (WSP) Recursive Prompt
0102 Directive: This module aggregates presence across platforms, enabling autonomous
coordination through unified availability detection and cross-platform presence normalization.

- UN (Understanding): Anchor presence signals and retrieve platform protocols
- DAO (Execution): Execute presence aggregation through cross-platform monitoring
- DU (Emergence): Collapse into availability excellence and emit meeting opportunities

wsp_cycle(input="cross_platform_presence_aggregation", log=True)
""" 