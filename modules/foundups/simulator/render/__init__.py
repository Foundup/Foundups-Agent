"""Render layer for FoundUps simulator.

Provides different visualization backends:
- terminal_view: ASCII grid + counters (default)
- pygame_view: Pixel tiles with HUD (optional)
"""

from .terminal_view import TerminalView

__all__ = ["TerminalView"]
