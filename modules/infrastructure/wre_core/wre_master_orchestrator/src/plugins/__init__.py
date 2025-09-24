"""
WRE Master Orchestrator Plugins
Per WSP 65 (Component Consolidation)

All orchestrators become plugins to the master.
"""

from .holoindex_plugin import HoloIndexPlugin

__all__ = ['HoloIndexPlugin']