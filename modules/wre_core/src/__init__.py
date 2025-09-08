#!/usr/bin/env python3
"""
WRE Core Source Package
WSP 49 Compliant Module Structure

Main source package for WRE (Windsurf Recursive Engine) containing
all core functionality for autonomous module building and orchestration.
"""

from .run_wre import main as run_wre_main
from .wre_launcher import WRELauncher
from .wre_monitor import WREMonitor
from .wre_sdk_implementation import WRESDK
from .monitor_dashboard import MonitorDashboard

__all__ = [
    'run_wre_main',
    'WRELauncher',
    'WREMonitor',
    'WRESDK',
    'MonitorDashboard'
]

__version__ = "0.1.0"
__author__ = "0102 Autonomous Agent"
