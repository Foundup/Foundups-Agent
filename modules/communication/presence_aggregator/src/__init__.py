"""
Presence Aggregator Module - Cross-Platform Presence Normalization

Part of the Autonomous Meeting Orchestrator (AMO) ecosystem.
Normalizes and streams presence data from Discord, WhatsApp, LinkedIn, Zoom.
"""

from .presence_aggregator import PresenceAggregator, PresenceStatus, Platform, PresenceData

__version__ = "0.0.1"
__all__ = ["PresenceAggregator", "PresenceStatus", "Platform", "PresenceData"] 