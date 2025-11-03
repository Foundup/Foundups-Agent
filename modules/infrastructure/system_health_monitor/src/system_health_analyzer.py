#!/usr/bin/env python3
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

System Health Analyzer - WSP Compliant
Monitors for duplicate messages, errors, and improvement opportunities
Integrates with self-improvement engine for autonomous optimization
"""

import logging
import time
import re
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class SystemIssue:
    """Represents a detected system issue"""
    issue_id: str
    issue_type: str  # 'duplicate', 'error', 'timeout', 'rate_limit', 'performance'
    severity: str    # 'low', 'medium', 'high', 'critical'
    description: str
    occurrences: int
    first_seen: float
    last_seen: float
    context: Dict
    suggested_fix: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass  
class PerformanceMetric:
    """Performance tracking metric"""
    metric_name: str
    value: float
    threshold: float
    timestamp: float
    
    @property
    def is_degraded(self) -> bool:
        return self.value > self.threshold


class SystemHealthAnalyzer:
    """
    Monitors system health and detects issues for self-improvement.
    WSP 48 compliant - enables recursive self-improvement.
    """
    
    def __init__(self, memory_dir: str = "memory/system_health"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Issue tracking
        self.issues: Dict[str, SystemIssue] = {}
        self.resolved_issues: List[SystemIssue] = []
        
        # Duplicate detection
        self.message_cache = deque(maxlen=100)  # Last 100 messages
        self.duplicate_window = 5  # seconds
        self.duplicate_threshold = 2  # same message 2+ times = issue (prevent duplicates)
        
        # Error tracking
        self.error_patterns = {
            'api_quota': r'quotaExceeded|429|rate.?limit',
            'timeout': r'timeout|timed out|TimeoutError',
            'connection': r'connection|refused|reset|broken pipe',
            'permission': r'permission|denied|unauthorized|403',
            'not_found': r'not found|404|missing',
            'syntax': r'SyntaxError|IndentationError|TabError',
            'type': r'TypeError|AttributeError|KeyError',
            'value': r'ValueError|IndexError|ZeroDivision',
            'import': r'ImportError|ModuleNotFoundError',
            'async': r'await.*expression|async.*def'
        }
        self.error_counts = defaultdict(int)
        
        # Performance tracking
        self.performance_metrics = {}
        self.response_times = deque(maxlen=50)
        self.operation_times = defaultdict(deque)  # operation -> times
        
        # Pattern detection
        self.command_patterns = defaultdict(list)  # command -> timestamps
        self.user_patterns = defaultdict(list)     # user -> activity timestamps
        
        # Health thresholds
        self.thresholds = {
            'max_duplicates': 2,
            'error_rate': 0.1,  # 10% error rate
            'response_time_ms': 2000,
            'api_calls_per_minute': 60,
            'memory_usage_mb': 500,
            'duplicate_window_sec': 5
        }
        
        logger.info(f"[U+1F3E5] System Health Analyzer initialized")
    
    def analyze_message(self, message: str, timestamp: float = None) -> List[SystemIssue]:
        """
        Analyze a message for issues.
        
        Returns:
            List of detected issues
        """
        timestamp = timestamp or time.time()
        issues = []
        
        # Check for duplicates
        duplicate_issue = self._check_duplicate_message(message, timestamp)
        if duplicate_issue:
            issues.append(duplicate_issue)
        
        # Check for errors
        error_issues = self._check_error_patterns(message, timestamp)
        issues.extend(error_issues)
        
        # Add to cache
        self.message_cache.append({
            'message': message,
            'timestamp': timestamp
        })
        
        return issues
    
    def _check_duplicate_message(self, message: str, timestamp: float) -> Optional[SystemIssue]:
        """Check if message is a duplicate within time window."""
        duplicates = []
        
        for cached in self.message_cache:
            # Check if within time window
            if timestamp - cached['timestamp'] <= self.duplicate_window:
                # Check if message is similar (ignoring timestamps)
                if self._messages_similar(message, cached['message']):
                    duplicates.append(cached)
        
        if len(duplicates) >= self.duplicate_threshold - 1:
            issue_id = f"duplicate_{hash(message) % 10000}"
            
            if issue_id in self.issues:
                # Update existing issue
                self.issues[issue_id].occurrences += 1
                self.issues[issue_id].last_seen = timestamp
            else:
                # Create new issue
                issue = SystemIssue(
                    issue_id=issue_id,
                    issue_type='duplicate',
                    severity='medium' if len(duplicates) < 5 else 'high',
                    description=f"Message sent {len(duplicates) + 1} times in {self.duplicate_window}s",
                    occurrences=len(duplicates) + 1,
                    first_seen=duplicates[0]['timestamp'] if duplicates else timestamp,
                    last_seen=timestamp,
                    context={
                        'message_preview': message[:100],
                        'duplicate_count': len(duplicates) + 1
                    },
                    suggested_fix="Add duplicate detection cache or increase cooldown"
                )
                self.issues[issue_id] = issue
                return issue
        
        return None
    
    def _messages_similar(self, msg1: str, msg2: str, threshold: float = 0.9) -> bool:
        """Check if two messages are similar (ignoring dynamic parts)."""
        # Remove timestamps, IDs, and numbers for comparison
        pattern = r'\d+|[a-f0-9]{8,}|\d{4}-\d{2}-\d{2}'
        clean1 = re.sub(pattern, '', msg1.lower())
        clean2 = re.sub(pattern, '', msg2.lower())
        
        # Simple similarity check
        if clean1 == clean2:
            return True
        
        # Check if one contains most of the other
        if len(clean1) > 20 and len(clean2) > 20:
            shorter = clean1 if len(clean1) < len(clean2) else clean2
            longer = clean2 if shorter == clean1 else clean1
            if shorter in longer:
                return True
        
        return False
    
    def _check_error_patterns(self, message: str, timestamp: float) -> List[SystemIssue]:
        """Check message for error patterns."""
        issues = []
        
        for error_type, pattern in self.error_patterns.items():
            if re.search(pattern, message, re.IGNORECASE):
                self.error_counts[error_type] += 1
                
                # Create issue if error is frequent
                if self.error_counts[error_type] >= 3:
                    issue_id = f"error_{error_type}"
                    
                    if issue_id in self.issues:
                        self.issues[issue_id].occurrences += 1
                        self.issues[issue_id].last_seen = timestamp
                    else:
                        severity = self._determine_error_severity(error_type)
                        issue = SystemIssue(
                            issue_id=issue_id,
                            issue_type='error',
                            severity=severity,
                            description=f"{error_type} errors detected",
                            occurrences=self.error_counts[error_type],
                            first_seen=timestamp,
                            last_seen=timestamp,
                            context={
                                'error_type': error_type,
                                'pattern': pattern,
                                'sample': message[:200]
                            },
                            suggested_fix=self._get_error_fix(error_type)
                        )
                        self.issues[issue_id] = issue
                        issues.append(issue)
        
        return issues
    
    def _determine_error_severity(self, error_type: str) -> str:
        """Determine severity based on error type."""
        critical_errors = ['api_quota', 'permission', 'import']
        high_errors = ['timeout', 'connection', 'syntax']
        medium_errors = ['type', 'value', 'async']
        
        if error_type in critical_errors:
            return 'critical'
        elif error_type in high_errors:
            return 'high'
        elif error_type in medium_errors:
            return 'medium'
        else:
            return 'low'
    
    def _get_error_fix(self, error_type: str) -> str:
        """Get suggested fix for error type."""
        fixes = {
            'api_quota': "Implement exponential backoff and rotate API keys",
            'timeout': "Increase timeout values or add retry logic",
            'connection': "Add connection pooling and retry mechanism",
            'permission': "Check authentication tokens and permissions",
            'not_found': "Verify file paths and API endpoints",
            'syntax': "Run linter and fix syntax issues",
            'type': "Add type checking and validation",
            'value': "Add input validation and bounds checking",
            'import': "Check module dependencies and imports",
            'async': "Fix async/await syntax and add proper error handling"
        }
        return fixes.get(error_type, "Review error logs and add error handling")
    
    def track_operation(self, operation: str, duration_ms: float):
        """Track operation performance."""
        self.operation_times[operation].append(duration_ms)
        if len(self.operation_times[operation]) > 100:
            self.operation_times[operation].popleft()
        
        # Check if operation is slow
        if duration_ms > self.thresholds['response_time_ms']:
            issue_id = f"perf_{operation}"
            
            if issue_id not in self.issues:
                issue = SystemIssue(
                    issue_id=issue_id,
                    issue_type='performance',
                    severity='medium' if duration_ms < 5000 else 'high',
                    description=f"Operation {operation} took {duration_ms}ms",
                    occurrences=1,
                    first_seen=time.time(),
                    last_seen=time.time(),
                    context={
                        'operation': operation,
                        'duration_ms': duration_ms,
                        'threshold_ms': self.thresholds['response_time_ms']
                    },
                    suggested_fix=f"Optimize {operation} or add caching"
                )
                self.issues[issue_id] = issue
    
    def analyze_pattern(self, pattern_type: str, pattern_data: Dict) -> Optional[str]:
        """
        Analyze patterns for optimization opportunities.
        
        Returns:
            Optimization suggestion or None
        """
        if pattern_type == 'command_burst':
            # Check for command spam
            commands_per_second = pattern_data.get('rate', 0)
            if commands_per_second > 2:
                return "Add rate limiting to prevent command spam"
        
        elif pattern_type == 'user_activity':
            # Check for unusual user patterns
            messages_per_minute = pattern_data.get('rate', 0)
            if messages_per_minute > 10:
                return "User may be spamming - consider timeout"
        
        elif pattern_type == 'error_spike':
            # Check for error spikes
            error_rate = pattern_data.get('rate', 0)
            if error_rate > self.thresholds['error_rate']:
                return "High error rate detected - review error handling"
        
        return None
    
    def get_health_report(self) -> Dict:
        """Generate comprehensive health report."""
        # Calculate metrics
        total_errors = sum(self.error_counts.values())
        active_issues = [i for i in self.issues.values() 
                        if time.time() - i.last_seen < 300]  # Active in last 5 min
        
        # Average response times
        avg_response = (sum(self.response_times) / len(self.response_times) 
                       if self.response_times else 0)
        
        # Operation performance
        slow_operations = {}
        for op, times in self.operation_times.items():
            if times:
                avg_time = sum(times) / len(times)
                if avg_time > self.thresholds['response_time_ms']:
                    slow_operations[op] = avg_time
        
        return {
            'timestamp': datetime.now().isoformat(),
            'health_score': self._calculate_health_score(),
            'active_issues': len(active_issues),
            'total_errors': total_errors,
            'error_breakdown': dict(self.error_counts),
            'avg_response_ms': avg_response,
            'slow_operations': slow_operations,
            'critical_issues': [i.to_dict() for i in active_issues 
                               if i.severity == 'critical'],
            'recommendations': self._generate_recommendations()
        }
    
    def _calculate_health_score(self) -> float:
        """Calculate overall system health score (0-100)."""
        score = 100.0
        
        # Deduct for issues
        for issue in self.issues.values():
            if time.time() - issue.last_seen < 300:  # Recent issue
                if issue.severity == 'critical':
                    score -= 20
                elif issue.severity == 'high':
                    score -= 10
                elif issue.severity == 'medium':
                    score -= 5
                else:
                    score -= 2
        
        # Deduct for errors
        total_errors = sum(self.error_counts.values())
        if total_errors > 10:
            score -= min(20, total_errors)
        
        return max(0, score)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        # Check for duplicate issues
        dup_issues = [i for i in self.issues.values() 
                     if i.issue_type == 'duplicate']
        if dup_issues:
            recommendations.append(
                "Implement message deduplication cache to prevent duplicate sends"
            )
        
        # Check for error patterns
        if self.error_counts['timeout'] > 5:
            recommendations.append(
                "Increase timeout values or implement retry logic with backoff"
            )
        
        if self.error_counts['api_quota'] > 0:
            recommendations.append(
                "Implement API key rotation and rate limiting"
            )
        
        # Check performance
        if self.operation_times:
            slow_ops = [op for op, times in self.operation_times.items()
                       if times and sum(times)/len(times) > 1000]
            if slow_ops:
                recommendations.append(
                    f"Optimize slow operations: {', '.join(slow_ops)}"
                )
        
        return recommendations
    
    def integrate_with_self_improvement(self, self_improvement_engine):
        """
        Integrate with self-improvement engine for autonomous optimization.
        WSP 48 compliant integration.
        """
        # Share health data with self-improvement
        health_report = self.get_health_report()
        
        for issue in self.issues.values():
            if issue.severity in ['high', 'critical']:
                # Trigger self-improvement observation
                self_improvement_engine.observe_system_issue(
                    issue_type=issue.issue_type,
                    severity=issue.severity,
                    context=issue.context
                )
        
        # Apply recommendations
        for recommendation in health_report['recommendations']:
            logger.info(f"[TOOL] Health recommendation: {recommendation}")
        
        return health_report