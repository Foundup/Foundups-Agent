"""FoundUps Simulator - Visual simulation of the autonomous FoundUp ecosystem.

This module provides a Mesa-based agent simulation for visualizing
FoundUp creation, task lifecycles, and token economics.

Architecture:
    FAMDaemon (SSoT) -> EventBus -> StateStore -> RenderView

Key components:
    - mesa_model.py: Model wrapper coordinating agents
    - event_bus.py: Subscribes to FAMDaemon events
    - state_store.py: Derives renderable state from events
    - agents/: Agent implementations (FounderAgent, UserAgent)
    - adapters/: FAM bridge and phantom plugs
    - render/: Visualization backends (terminal, pygame)
    - run.py: Main entrypoint

Usage:
    python -m modules.foundups.simulator.run --ticks 1000 --founders 5
"""

from .config import SimulatorConfig, DEFAULT_CONFIG
from .event_bus import EventBus, SimEvent
from .state_store import StateStore, SimulatorState, FoundUpTile, AgentState
from .mesa_model import FoundUpsModel

__all__ = [
    "SimulatorConfig",
    "DEFAULT_CONFIG",
    "EventBus",
    "SimEvent",
    "StateStore",
    "SimulatorState",
    "FoundUpTile",
    "AgentState",
    "FoundUpsModel",
]
