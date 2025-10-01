#!/usr/bin/env python3
"""
HoloIndex Qwen Advisor - Modular AI Intelligence System

Clean API exports for the refactored HoloDAE architecture.

WSP Compliance: WSP 80 (Cube-Level DAE Orchestration)
"""

# Main coordinator (replaces monolithic autonomous_holodae.py)
from .holodae_coordinator import HoloDAECoordinator

# Legacy compatibility functions
from .holodae_coordinator import (
    start_holodae,
    stop_holodae,
    get_holodae_status,
    show_holodae_menu
)

# Core models
from .models.work_context import WorkContext
from .models.monitoring_types import (
    MonitoringResult,
    HealthViolation,
    PatternAlert,
    MonitoringState
)

# Orchestration layer
from .orchestration.qwen_orchestrator import QwenOrchestrator

# Arbitration layer
from .arbitration.mps_arbitrator import (
    MPSArbitrator,
    ArbitrationDecision,
    MPSAnalysis,
    PriorityLevel,
    ActionType
)

# Core services
from .services.file_system_watcher import FileSystemWatcher
from .services.context_analyzer import ContextAnalyzer

# UI components
from .ui.menu_system import HoloDAEMenuSystem, StatusDisplay

__all__ = [
    # Main components
    'HoloDAECoordinator',

    # Legacy functions
    'start_holodae',
    'stop_holodae',
    'get_holodae_status',
    'show_holodae_menu',

    # Models
    'WorkContext',
    'MonitoringResult',
    'HealthViolation',
    'PatternAlert',
    'MonitoringState',

    # Orchestration
    'QwenOrchestrator',

    # Arbitration
    'MPSArbitrator',
    'ArbitrationDecision',
    'MPSAnalysis',
    'PriorityLevel',
    'ActionType',

    # Services
    'FileSystemWatcher',
    'ContextAnalyzer',

    # UI
    'HoloDAEMenuSystem',
    'StatusDisplay'
]

__version__ = "2.0.0"  # Modular architecture version