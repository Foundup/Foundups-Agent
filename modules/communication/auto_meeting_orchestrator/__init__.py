"""
Autonomous Meeting Orchestrator (AMO) Module

Eliminates manual scheduling by detecting real-time availability 
and auto-initiating meetings across platforms.
"""

__version__ = "0.0.1"
__author__ = "0102 pArtifact"
__module__ = "auto_meeting_orchestrator"

from .src.orchestrator import MeetingOrchestrator

__all__ = ["MeetingOrchestrator"] 