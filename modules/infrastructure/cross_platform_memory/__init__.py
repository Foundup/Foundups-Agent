# -*- coding: utf-8 -*-
"""
Cross-Platform Memory Orchestrator (WSP 60 Enhanced)

Provides unified memory architecture for cross-platform intelligence sharing
across all FoundUps modules and DAEs.

WSP 60: Module Memory Architecture Protocol
WSP 80: Cube-Level DAE Orchestration
"""

from .src.cross_platform_memory_orchestrator import CrossPlatformMemoryOrchestrator
from .src.pattern_memory import PatternMemory
from .src.breadcrumb_trail import BreadcrumbTrail
from .src.agent_coordination import AgentCoordination

__all__ = [
    'CrossPlatformMemoryOrchestrator',
    'PatternMemory',
    'BreadcrumbTrail',
    'AgentCoordination'
]





