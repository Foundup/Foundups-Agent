"""
Work Completion Publisher - Autonomous Git Push and Social Posting

Public API for autonomous work detection and publishing.
"""

from .work_analyzer import WorkAnalyzer, WorkSession, PublishContent
from .monitoring_service import MonitoringService, start_monitoring

__all__ = [
    'WorkAnalyzer',
    'WorkSession',
    'PublishContent',
    'MonitoringService',
    'start_monitoring'
]

__version__ = '1.0.0'
__author__ = '0102 Autonomous Agent'
