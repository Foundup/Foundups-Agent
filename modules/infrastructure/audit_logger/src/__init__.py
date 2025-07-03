"""
Audit Logger Module - Meeting Transparency and Compliance

Logs all meeting-related activities for transparency and audit trails.
"""

from .audit_logger import AuditLogger, AuditEvent, EventType

__version__ = "0.0.1"
__all__ = ["AuditLogger", "AuditEvent", "EventType"] 