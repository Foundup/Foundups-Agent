# -*- coding: utf-8 -*-
"""
HoloDAE Coordinator Package - Legacy Shim for Staged WSP 62 Refactoring

This package provides a re-export layer for the HoloDAECoordinator class
to enable staged extraction without breaking external callers.

WSP 62 Remediation Plan:
- Current: holodae_coordinator.py (2166 lines - VIOLATION)
- Target: <500 lines (thin integration layer)
- Method: Extract to submodules, this shim re-exports

Sprint Order (low coupling first):
  H1: pid_detective.py (PID/process detection)
  H3: telemetry_formatter.py (output formatting)
  H6: wre_integration/ (WRE skill execution seam)
  H2: mcp_integration.py (MCP hooks)
  H4: module_metrics.py (module analysis)
  H5: monitoring_daemon.py (background monitoring)

Usage (unchanged for callers):
    from holo_index.qwen_advisor.holodae_coordinator_pkg import HoloDAECoordinator

After full extraction, this shim will be removed and the package
becomes the primary interface.
"""

# Re-export from the monolithic file (legacy path)
# As methods are extracted, imports will shift to submodules
from holo_index.qwen_advisor.holodae_coordinator import (
    HoloDAECoordinator,
    start_holodae,
    stop_holodae,
)

__all__ = [
    "HoloDAECoordinator",
    "start_holodae",
    "stop_holodae",
]

