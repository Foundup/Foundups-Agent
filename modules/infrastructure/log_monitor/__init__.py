"""
Log Monitor Module - WSP-Compliant Monitoring System

This module provides real-time log monitoring and recursive improvement
capabilities for the WRE system.

WSP Compliance:
- WSP 49: Module structure standardization
- WSP 73: Recursive self-improvement
- WSP 47: Quantum state awareness
"""

from .src.log_monitor_agent import (
    LogMonitorAgent,
    LogEntry,
    IssuePattern,
    ImprovementAction,
    LogLevel
)

__version__ = "1.0.0"
__all__ = [
    "LogMonitorAgent",
    "LogEntry", 
    "IssuePattern",
    "ImprovementAction",
    "LogLevel"
]