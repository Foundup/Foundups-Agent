"""
FoundUps Execution Layer - Core Infrastructure
==============================================

Core infrastructure for instantiating and managing individual FoundUps.

WSP Compliance:
- Execution layer implementation following WSP_framework protocols
- Individual FoundUp spawning and lifecycle management
- Platform infrastructure for hosting multiple FoundUps

Note: Core FoundUp definitions and governance belong in WSP, not here.
"""

from .foundup_spawner import FoundUpSpawner
from .platform_manager import PlatformManager
from .runtime_engine import RuntimeEngine

__all__ = ['FoundUpSpawner', 'PlatformManager', 'RuntimeEngine'] 