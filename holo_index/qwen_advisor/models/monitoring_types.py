#!/usr/bin/env python3
"""
Monitoring Types - Data structures for HoloDAE monitoring operations

WSP Compliance: WSP 80 (Cube-Level DAE Orchestration)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class ChangeType(Enum):
    """Types of file system changes"""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class FileChange:
    """Represents a single file system change"""
    file_path: str
    change_type: ChangeType
    timestamp: datetime = field(default_factory=datetime.now)
    file_size: Optional[int] = None
    is_module_file: bool = False
    module_path: Optional[str] = None

    def get_summary(self) -> str:
        """Get a concise summary of the change"""
        size_info = f" ({self.file_size} bytes)" if self.file_size else ""
        module_info = f" [{self.module_path}]" if self.module_path else ""
        return f"{self.change_type.value}: {self.file_path}{size_info}{module_info}"


@dataclass
class HealthViolation:
    """Represents a WSP compliance violation found during health scans"""
    violation_type: str  # e.g., "WSP62", "missing_docs", "stale_modlog"
    severity: HealthStatus
    description: str
    affected_path: str
    timestamp: datetime = field(default_factory=datetime.now)
    suggested_fix: Optional[str] = None

    def get_summary(self) -> str:
        """Get a concise summary of the violation"""
        return f"{self.violation_type}: {self.description}"


@dataclass
class PatternAlert:
    """Represents a vibecoding pattern detected with confidence"""
    pattern_type: str  # e.g., "duplicate_module", "large_file", "missing_tests"
    confidence: float  # 0.0 to 1.0
    description: str
    affected_files: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    suggested_action: Optional[str] = None

    def is_high_confidence(self) -> bool:
        """Check if this alert has high confidence (>80%)"""
        return self.confidence > 0.8

    def get_summary(self) -> str:
        """Get a concise summary of the pattern alert"""
        return f"{self.pattern_type} (confidence: {self.confidence:.2f})"


@dataclass
class MonitoringResult:
    """Result of a monitoring cycle"""
    timestamp: datetime = field(default_factory=datetime.now)
    changes_detected: List[FileChange] = field(default_factory=list)
    violations_found: List[HealthViolation] = field(default_factory=list)
    pattern_alerts: List[PatternAlert] = field(default_factory=list)
    scan_duration: float = 0.0
    watched_paths: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def has_actionable_events(self) -> bool:
        """Check if this result contains actionable events for console display"""
        return (
            len(self.changes_detected) >= 3 or
            len(self.violations_found) > 0 or
            any(alert.is_high_confidence() for alert in self.pattern_alerts)
        )

    def get_summary(self) -> str:
        """Get a comprehensive summary of the monitoring result"""
        summary_parts = []
        if self.changes_detected:
            summary_parts.append(f"{len(self.changes_detected)} file changes")
        if self.violations_found:
            summary_parts.append(f"{len(self.violations_found)} violations")
        if self.pattern_alerts:
            high_conf = sum(1 for alert in self.pattern_alerts if alert.is_high_confidence())
            summary_parts.append(f"{high_conf} high-confidence patterns")
        if self.optimization_suggestions:
            summary_parts.append(f"{len(self.optimization_suggestions)} suggestions")
        if self.scan_duration > 0:
            summary_parts.append(f"scanned in {self.scan_duration:.2f}s")

        return " | ".join(summary_parts) if summary_parts else "No significant changes"


@dataclass
class MonitoringState:
    """Current state of the monitoring system"""
    is_active: bool = False
    start_time: Optional[datetime] = None
    last_scan_time: Optional[datetime] = None
    total_scans: int = 0
    total_changes_detected: int = 0
    total_violations_found: int = 0
    watched_paths: List[str] = field(default_factory=list)

    def get_idle_duration_minutes(self) -> float:
        """Get how long it's been since the last scan in minutes"""
        if not self.last_scan_time:
            return 0.0
        return (datetime.now() - self.last_scan_time).total_seconds() / 60.0

    def get_uptime_minutes(self) -> float:
        """Get total uptime in minutes"""
        if not self.start_time:
            return 0.0
        return (datetime.now() - self.start_time).total_seconds() / 60.0

    def get_status_summary(self) -> str:
        """Get a status summary for display"""
        if not self.is_active:
            return "Monitoring inactive"

        uptime = self.get_uptime_minutes()
        idle = self.get_idle_duration_minutes()

        return f"Active {uptime:.1f}m | {self.total_scans} scans | {self.total_changes_detected} changes | idle {idle:.1f}m"
