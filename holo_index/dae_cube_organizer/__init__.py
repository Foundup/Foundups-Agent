"""
DAE Cube Organizer - HoloIndex DAE Rampup Server

Provides immediate DAE context and structure understanding for 0102 agents.
Acts as the foundational intelligence layer that all modules plug into,
forming DAE Cubes that connect in main.py.

WSP Compliance: WSP 80 (Cube-Level DAE Orchestration)
"""

from .dae_cube_organizer import DAECubeOrganizer

__version__ = "1.0.0"
__all__ = ["DAECubeOrganizer"]
