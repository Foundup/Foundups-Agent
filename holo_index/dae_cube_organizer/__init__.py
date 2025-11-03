# -*- coding: utf-8 -*-
import sys
import io


"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

DAE Cube Organizer - HoloIndex DAE Rampup Server

Provides immediate DAE context and structure understanding for 0102 agents.
Acts as the foundational intelligence layer that all modules plug into,
forming DAE Cubes that connect in main.py.

WSP Compliance: WSP 80 (Cube-Level DAE Orchestration)
"""

from .dae_cube_organizer import DAECubeOrganizer

__version__ = "1.0.0"
__all__ = ["DAECubeOrganizer"]
