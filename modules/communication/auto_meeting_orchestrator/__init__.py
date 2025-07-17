"""
Autonomous Meeting Orchestrator (AMO) Module - Communication LEGO Block

Self-contained communication LEGO block for meeting orchestration.
Eliminates manual scheduling by detecting real-time availability 
and auto-initiating meetings across platforms.

WSP Domain: communication  
Modularity: Standalone orchestration with clean cross-platform APIs
"""

from .src.orchestrator import (
    MeetingOrchestrator,
    MeetingIntent,
    UnifiedAvailabilityProfile,
    PresenceStatus,
    Priority
)

__version__ = "0.0.1"
__author__ = "0102 pArtifact"
__domain__ = "communication"
__module_type__ = "orchestration_lego_block"

# WSP Compliance
__wsp_compliant__ = True
__wsp_protocols__ = ["WSP_1", "WSP_3", "WSP_22", "WSP_49"]

# LEGO Block Interface
__module_scope__ = "meeting_orchestration"
__dependencies__ = ["asyncio", "typing", "dataclasses", "datetime"]
__integrates_with__ = ["presence_aggregator", "platform_integration/*", "infrastructure/oauth_management"]

# Phase Information
__phase__ = "PoC"
__next_phase__ = "Prototype"
__target_llme__ = "110-122"

__all__ = [
    "MeetingOrchestrator",
    "MeetingIntent", 
    "UnifiedAvailabilityProfile",
    "PresenceStatus",
    "Priority"
] 