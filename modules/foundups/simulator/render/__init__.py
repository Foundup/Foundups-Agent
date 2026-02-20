"""Render layer for FoundUps simulator.

Provides different visualization backends:
- terminal_view: ASCII grid + counters (default)
- cube_view: 3D ASCII cube animation with agents (new)
- pygame_view: Pixel tiles with HUD (optional)
"""

from .terminal_view import TerminalView
from .cube_view import CubeView

__all__ = ["TerminalView", "CubeView"]
