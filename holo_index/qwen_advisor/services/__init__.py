# -*- coding: utf-8 -*-
"""
HoloDAE Extracted Services - WSP 62 Compliance

Services extracted from holodae_coordinator.py (2,167 → 780 lines):
- Sprint H1: PIDDetective (234 lines) - Process detection and health checks
- Sprint H2: MCPIntegration (95 lines) - MCP connector activity tracking
- Sprint H3: TelemetryFormatter (340 lines) - JSONL telemetry logging
- Sprint H4: ModuleMetrics (145 lines) - Module health and size analysis
- Sprint H5: MonitoringLoop (301 lines) - Background monitoring system

WSP Compliance:
- WSP 62: All services <500 lines
- WSP 49: Module structure compliance
- WSP 72: Independent services (no circular dependencies)
"""

from .file_system_watcher import FileSystemWatcher
from .context_analyzer import ContextAnalyzer
from .pid_detective import PIDDetective
from .mcp_integration import MCPIntegration
from .telemetry_formatter import TelemetryFormatter
from .module_metrics import ModuleMetrics
from .monitoring_loop import MonitoringLoop

__all__ = [
    "FileSystemWatcher",
    "ContextAnalyzer",
    "PIDDetective",
    "MCPIntegration",
    "TelemetryFormatter",
    "ModuleMetrics",
    "MonitoringLoop"
]
