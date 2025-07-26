"""
Presence Aggregator Module - Multi-platform presence detection

Public API for unified availability profiling across platforms.
Extracted from auto_meeting_orchestrator strategic decomposition.
"""

from .src.presence_aggregator import (
    PresenceAggregator,
    PresenceStatus,
    PlatformPresence,
    UnifiedAvailabilityProfile
)

__all__ = [
    'PresenceAggregator',
    'PresenceStatus', 
    'PlatformPresence',
    'UnifiedAvailabilityProfile'
]

# Module metadata
__version__ = "0.1.0"
__domain__ = "platform_integration"
__purpose__ = "Multi-platform presence detection and unified availability profiling" 