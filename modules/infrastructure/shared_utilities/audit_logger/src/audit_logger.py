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

Audit Logger - WSP/WRE Infrastructure Module

WSP Compliance:
- WSP 34 (Testing Protocol): Comprehensive audit logging and testing capabilities
- WSP 54 (Agent Duties): AI-powered audit logging for autonomous infrastructure
- WSP 22 (ModLog): Change tracking and audit history
- WSP 50 (Pre-Action Verification): Enhanced verification before audit operations

Provides AI-powered audit logging capabilities for autonomous infrastructure operations.
Enables 0102 pArtifacts to maintain comprehensive audit trails and compliance records.
"""

import json
import logging
import hashlib
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import threading
import queue


class AuditLevel(Enum):
    """Audit log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    WSP_VIOLATION = "wsp_violation"


class AuditCategory(Enum):
    """Audit log categories."""
    SYSTEM = "system"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    USER_ACTION = "user_action"
    AGENT_ACTION = "agent_action"
    WSP_OPERATION = "wsp_operation"
    ERROR = "error"


@dataclass
class AuditEvent:
    """Audit event data structure."""
    event_id: str
    timestamp: datetime
    level: AuditLevel
    category: AuditCategory
    source: str
    action: str
    details: Dict[str, Any]
    user_id: Optional[str]
    session_id: Optional[str]
    wsp_references: List[str]
    hash_signature: str
    metadata: Dict[str, Any]


@dataclass
class AuditQuery:
    """Audit query parameters."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    level: Optional[AuditLevel] = None
    category: Optional[AuditCategory] = None
    source: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    wsp_references: Optional[List[str]] = None
    limit: int = 1000


@dataclass
class AuditStats:
    """Audit statistics."""
    total_events: int
    events_by_level: Dict[str, int]
    events_by_category: Dict[str, int]
    events_by_source: Dict[str, int]
    wsp_violations: int
    time_range: Tuple[datetime, datetime]


class AuditLogger:
    """
    AI-powered audit logger for autonomous infrastructure operations.
    
    Provides comprehensive audit logging including:
    - Real-time audit event logging
    - WSP compliance tracking
    - Security event monitoring
    - Performance metrics logging
    - Query and analysis capabilities
    """
    
    def __init__(self, log_file: str = "audit.log", max_file_size: int = 100 * 1024 * 1024):
        """Initialize the audit logger with WSP compliance standards."""
        self.log_file = log_file
        self.max_file_size = max_file_size
        self.events = []
        self.lock = threading.Lock()
        self.wsp_keywords = [
            'wsp', 'protocol', 'compliance', '0102', 'partifact', 'quantum',
            'autonomous', 'agent', 'modular', 'testing', 'documentation'
        ]
        
        # Initialize logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('audit_logger')
        
    def log_event(self, level: AuditLevel, category: AuditCategory, source: str, 
                  action: str, details: Dict[str, Any], user_id: str = None, 
                  session_id: str = None, wsp_references: List[str] = None,
                  metadata: Dict[str, Any] = None) -> str:
        """
        Log an audit event.
        
        Args:
            level: Audit level
            category: Audit category
            source: Source of the event
            action: Action performed
            details: Event details
            user_id: Optional user ID
            session_id: Optional session ID
            wsp_references: Optional WSP references
            metadata: Optional metadata
            
        Returns:
            Event ID of the logged event
        """
        try:
            # Generate event ID
            event_id = self._generate_event_id(source, action, datetime.now())
            
            # Create audit event
            event = AuditEvent(
                event_id=event_id,
                timestamp=datetime.now(),
                level=level,
                category=category,
                source=source,
                action=action,
                details=details,
                user_id=user_id,
                session_id=session_id,
                wsp_references=wsp_references or [],
                hash_signature=self._generate_hash_signature(source, action, details),
                metadata=metadata or {}
            )
            
            # Add to events list
            with self.lock:
                self.events.append(event)
                
                # Check file size and rotate if needed
                if self._should_rotate_log():
                    self._rotate_log()
            
            # Log to file
            self._write_event_to_file(event)
            
            # Log to standard logger
            log_message = f"Audit Event: {action} from {source} - {level.value}"
            if level == AuditLevel.WSP_VIOLATION:
                self.logger.warning(log_message)
            elif level == AuditLevel.ERROR or level == AuditLevel.CRITICAL:
                self.logger.error(log_message)
            else:
                self.logger.info(log_message)
            
            return event_id
            
        except Exception as e:
            self.logger.error(f"Error logging audit event: {e}")
            return f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def log_wsp_violation(self, source: str, violation_type: str, details: Dict[str, Any],
                         wsp_references: List[str] = None) -> str:
        """
        Log a WSP violation event.
        
        Args:
            source: Source of the violation
            violation_type: Type of violation
            details: Violation details
            wsp_references: WSP protocol references
            
        Returns:
            Event ID of the logged violation
        """
        return self.log_event(
            level=AuditLevel.WSP_VIOLATION,
            category=AuditCategory.COMPLIANCE,
            source=source,
            action=f"WSP_VIOLATION_{violation_type}",
            details=details,
            wsp_references=wsp_references or [],
            metadata={"violation_type": violation_type}
        )
    
    def log_security_event(self, source: str, action: str, details: Dict[str, Any],
                          user_id: str = None) -> str:
        """
        Log a security event.
        
        Args:
            source: Source of the security event
            action: Security action
            details: Event details
            user_id: Optional user ID
            
        Returns:
            Event ID of the logged event
        """
        return self.log_event(
            level=AuditLevel.WARNING,
            category=AuditCategory.SECURITY,
            source=source,
            action=action,
            details=details,
            user_id=user_id
        )
    
    def log_performance_event(self, source: str, action: str, performance_metrics: Dict[str, Any]) -> str:
        """
        Log a performance event.
        
        Args:
            source: Source of the performance event
            action: Performance action
            performance_metrics: Performance metrics
            
        Returns:
            Event ID of the logged event
        """
        return self.log_event(
            level=AuditLevel.INFO,
            category=AuditCategory.PERFORMANCE,
            source=source,
            action=action,
            details=performance_metrics
        )
    
    def query_events(self, query: AuditQuery) -> List[AuditEvent]:
        """
        Query audit events based on criteria.
        
        Args:
            query: AuditQuery object with search criteria
            
        Returns:
            List of matching AuditEvent objects
        """
        try:
            with self.lock:
                filtered_events = self.events.copy()
            
            # Apply filters
            if query.start_time:
                filtered_events = [e for e in filtered_events if e.timestamp >= query.start_time]
            
            if query.end_time:
                filtered_events = [e for e in filtered_events if e.timestamp <= query.end_time]
            
            if query.level:
                filtered_events = [e for e in filtered_events if e.level == query.level]
            
            if query.category:
                filtered_events = [e for e in filtered_events if e.category == query.category]
            
            if query.source:
                filtered_events = [e for e in filtered_events if e.source == query.source]
            
            if query.user_id:
                filtered_events = [e for e in filtered_events if e.user_id == query.user_id]
            
            if query.session_id:
                filtered_events = [e for e in filtered_events if e.session_id == query.session_id]
            
            if query.wsp_references:
                filtered_events = [e for e in filtered_events 
                                 if any(ref in e.wsp_references for ref in query.wsp_references)]
            
            # Apply limit
            if query.limit:
                filtered_events = filtered_events[-query.limit:]
            
            return filtered_events
            
        except Exception as e:
            self.logger.error(f"Error querying audit events: {e}")
            return []
    
    def get_audit_stats(self, start_time: datetime = None, end_time: datetime = None) -> AuditStats:
        """
        Get audit statistics for a time range.
        
        Args:
            start_time: Start time for statistics
            end_time: End time for statistics
            
        Returns:
            AuditStats object with statistics
        """
        try:
            with self.lock:
                events = self.events.copy()
            
            # Filter by time range
            if start_time:
                events = [e for e in events if e.timestamp >= start_time]
            if end_time:
                events = [e for e in events if e.timestamp <= end_time]
            
            if not events:
                return AuditStats(
                    total_events=0,
                    events_by_level={},
                    events_by_category={},
                    events_by_source={},
                    wsp_violations=0,
                    time_range=(start_time or datetime.now(), end_time or datetime.now())
                )
            
            # Calculate statistics
            events_by_level = {}
            events_by_category = {}
            events_by_source = {}
            wsp_violations = 0
            
            for event in events:
                # Level statistics
                level_key = event.level.value
                events_by_level[level_key] = events_by_level.get(level_key, 0) + 1
                
                # Category statistics
                category_key = event.category.value
                events_by_category[category_key] = events_by_category.get(category_key, 0) + 1
                
                # Source statistics
                events_by_source[event.source] = events_by_source.get(event.source, 0) + 1
                
                # WSP violations
                if event.level == AuditLevel.WSP_VIOLATION:
                    wsp_violations += 1
            
            return AuditStats(
                total_events=len(events),
                events_by_level=events_by_level,
                events_by_category=events_by_category,
                events_by_source=events_by_source,
                wsp_violations=wsp_violations,
                time_range=(min(e.timestamp for e in events), max(e.timestamp for e in events))
            )
            
        except Exception as e:
            self.logger.error(f"Error getting audit stats: {e}")
            return AuditStats(
                total_events=0,
                events_by_level={},
                events_by_category={},
                events_by_source={},
                wsp_violations=0,
                time_range=(datetime.now(), datetime.now())
            )
    
    def export_audit_log(self, output_file: str, query: AuditQuery = None) -> bool:
        """
        Export audit log to file.
        
        Args:
            output_file: Output file path
            query: Optional query to filter events
            
        Returns:
            True if successful, False otherwise
        """
        try:
            events = self.query_events(query) if query else self.events
            
            # Convert events to JSON-serializable format
            export_data = []
            for event in events:
                event_dict = asdict(event)
                event_dict['timestamp'] = event.timestamp.isoformat()
                export_data.append(event_dict)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting audit log: {e}")
            return False
    
    def _generate_event_id(self, source: str, action: str, timestamp: datetime) -> str:
        """Generate a unique event ID."""
        data_string = f"{source}_{action}_{timestamp.isoformat()}"
        return hashlib.sha256(data_string.encode()).hexdigest()[:16]
    
    def _generate_hash_signature(self, source: str, action: str, details: Dict[str, Any]) -> str:
        """Generate a hash signature for the audit event."""
        signature_data = {
            'source': source,
            'action': action,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        signature_string = json.dumps(signature_data, sort_keys=True)
        return hashlib.sha256(signature_string.encode()).hexdigest()
    
    def _should_rotate_log(self) -> bool:
        """Check if log file should be rotated."""
        try:
            if Path(self.log_file).exists():
                return Path(self.log_file).stat().st_size > self.max_file_size
            return False
        except Exception:
            return False
    
    def _rotate_log(self):
        """Rotate the log file."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{self.log_file}.{timestamp}"
            Path(self.log_file).rename(backup_file)
            self.logger.info(f"Log file rotated to {backup_file}")
        except Exception as e:
            self.logger.error(f"Error rotating log file: {e}")
    
    def _write_event_to_file(self, event: AuditEvent):
        """Write event to log file."""
        try:
            event_dict = asdict(event)
            event_dict['timestamp'] = event.timestamp.isoformat()
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event_dict) + '\n')
                
        except Exception as e:
            self.logger.error(f"Error writing event to file: {e}")


def create_audit_logger(log_file: str = "audit.log") -> AuditLogger:
    """
    Factory function to create an audit logger.
    
    Args:
        log_file: Log file path
        
    Returns:
        AuditLogger instance
    """
    return AuditLogger(log_file)


if __name__ == "__main__":
    """Test the audit logger with sample data."""
    # Create audit logger
    logger = create_audit_logger("test_audit.log")
    
    # Log various events
    logger.log_event(
        level=AuditLevel.INFO,
        category=AuditCategory.SYSTEM,
        source="test_system",
        action="system_startup",
        details={"version": "1.0.0", "status": "started"}
    )
    
    logger.log_wsp_violation(
        source="test_module",
        violation_type="missing_modlog",
        details={"module": "test_module", "missing_file": "ModLog.md"},
        wsp_references=["WSP 22"]
    )
    
    logger.log_security_event(
        source="auth_system",
        action="login_attempt",
        details={"ip": "192.168.1.1", "success": False},
        user_id="test_user"
    )
    
    logger.log_performance_event(
        source="api_gateway",
        action="request_processed",
        performance_metrics={"response_time": 150, "status_code": 200}
    )
    
    # Query events
    query = AuditQuery(
        start_time=datetime.now() - timedelta(hours=1),
        level=AuditLevel.WSP_VIOLATION
    )
    
    events = logger.query_events(query)
    print(f"Found {len(events)} WSP violation events")
    
    # Get statistics
    stats = logger.get_audit_stats()
    print(f"Total events: {stats.total_events}")
    print(f"WSP violations: {stats.wsp_violations}")
    print(f"Events by level: {stats.events_by_level}")
    
    # Export audit log
    logger.export_audit_log("audit_export.json") 