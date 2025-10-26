# -*- coding: utf-8 -*-
"""
Confidence Tracker - Decay-Based Confidence Algorithm
Tracks agent confidence with time-weighted scoring and automatic downgrade

WSP Compliance:
- WSP 77 (Agent Coordination): Confidence-based permission escalation
- WSP 91 (Observability): SQLite telemetry for confidence events
- WSP 50 (Pre-Action Verification): Verify confidence before operations
"""

import json
import math
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from enum import Enum


logger = logging.getLogger(__name__)


class ConfidenceDecayEvent(Enum):
    """Events that trigger confidence decay"""
    EDIT_ROLLED_BACK = -0.15        # Human reverted the change
    HUMAN_REJECTION = -0.10         # Report rejected by 0102
    WSP_VIOLATION = -0.20           # Broke WSP compliance
    REGRESSION_CAUSED = -0.25       # Tests failed after change
    SECURITY_ISSUE = -0.50          # Created security vulnerability
    FALSE_POSITIVE = -0.05          # Gemma detection was wrong
    DUPLICATE_WORK = -0.03          # Redundant with existing


class ConfidenceBoostEvent(Enum):
    """Events that boost confidence"""
    HUMAN_APPROVAL = 0.10           # 0102 approved recommendation
    TESTS_PASSED = 0.05             # All tests passed after change
    WSP_COMPLIANT = 0.03            # No violations detected
    PEER_VALIDATION = 0.08          # Another agent verified work
    PRODUCTION_STABLE = 0.15        # Change stable after 7 days


class ConfidenceTracker:
    """
    Track agent confidence with decay-based weighting

    Features:
    - Exponential time decay (recent events weighted higher)
    - Failure decay multiplier (automatic downgrade)
    - Lookback window (30 days)
    - SQLite telemetry for audit trail
    """

    def __init__(self, repo_root: Optional[Path] = None):
        """
        Initialize confidence tracker

        Args:
            repo_root: Repository root directory
        """
        self.decay_rate = 0.05  # 5% decay per day for old events
        self.lookback_window_days = 30

        # Database path
        if repo_root is None:
            repo_root = Path(__file__).parent.parent.parent.parent.parent
        self.repo_root = Path(repo_root)
        self.db_path = self.repo_root / "data" / "foundup.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # In-memory cache for performance
        self.confidence_scores = {}

    def _append_event(self, event: Dict[str, Any]) -> None:
        """Append confidence event to SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT INTO confidence_events (
                    agent_id, confidence_before, confidence_after,
                    event_type, success, recorded_at, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                event['agent_id'],
                event['confidence_before'],
                event['confidence_after'],
                event['event_type'],
                event.get('success', True),
                event['timestamp'],
                json.dumps(event.get('metadata', {}))
            ))
            conn.commit()
            conn.close()
            logger.debug(f"[CONFIDENCE_EVENT] {event['agent_id']}: {event['confidence_before']:.2f} -> {event['confidence_after']:.2f}")
        except Exception as e:
            logger.error(f"Failed to append confidence event: {e}")

    def _get_agent_history(self, agent_id: str, days: int = None) -> List[Dict[str, Any]]:
        """
        Get agent event history from SQLite

        Args:
            agent_id: Agent identifier
            days: Number of days to look back (default: lookback_window_days)

        Returns:
            List of events for this agent
        """
        if days is None:
            days = self.lookback_window_days

        cutoff = datetime.now() - timedelta(days=days)
        events = []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT agent_id, confidence_before, confidence_after,
                       event_type, success, recorded_at, metadata_json
                FROM confidence_events
                WHERE agent_id = ? AND recorded_at >= ?
                ORDER BY recorded_at ASC
            ''', (agent_id, cutoff.isoformat()))

            for row in cursor.fetchall():
                events.append({
                    'agent_id': row[0],
                    'confidence_before': row[1],
                    'confidence_after': row[2],
                    'event_type': row[3],
                    'success': bool(row[4]),
                    'timestamp': row[5],
                    'metadata': json.loads(row[6]) if row[6] else {}
                })

            conn.close()
        except Exception as e:
            logger.error(f"Failed to read event history: {e}")

        return events

    def _count_recent_failures(self, agent_id: str, days: int = 7) -> int:
        """Count failures in recent days"""
        events = self._get_agent_history(agent_id, days=days)
        return sum(1 for e in events if not e.get('success', True))

    def update_confidence(
        self,
        agent_id: str,
        execution_result: Dict[str, Any]
    ) -> float:
        """
        Update confidence with decay-based weighting

        Args:
            execution_result: {
                'success': bool,
                'timestamp': ISO datetime (optional, defaults to now),
                'event_type': str (ConfidenceDecayEvent or ConfidenceBoostEvent name),
                'validation': str,
                'rollback_reason': Optional[str],
                'details': Optional[Dict]
            }

        Returns:
            Updated confidence score (0.0 to 1.0)
        """
        # Parse event
        success = execution_result.get('success', False)
        timestamp_str = execution_result.get('timestamp')
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str)
        else:
            timestamp = datetime.now()

        event_type = execution_result.get('event_type', '')

        # Calculate confidence adjustment
        confidence_adjustment = 0.0

        if event_type:
            # Try decay events
            try:
                decay_event = ConfidenceDecayEvent[event_type]
                confidence_adjustment = decay_event.value
            except KeyError:
                pass

            # Try boost events
            try:
                boost_event = ConfidenceBoostEvent[event_type]
                confidence_adjustment = boost_event.value
            except KeyError:
                pass

        # Get agent history
        history = self._get_agent_history(agent_id)

        # Add current event to history
        current_event = {
            'agent_id': agent_id,
            'success': success,
            'timestamp': timestamp.isoformat(),
            'event_type': event_type,
            'confidence_adjustment': confidence_adjustment,
            'validation': execution_result.get('validation', ''),
            'details': execution_result.get('details', {})
        }
        history.append(current_event)

        # Calculate time-weighted success rate
        now = datetime.now()
        weighted_successes = 0.0
        weighted_total = 0.0

        for event in history:
            event_time = datetime.fromisoformat(event['timestamp'])
            days_ago = (now - event_time).days

            if days_ago > self.lookback_window_days:
                continue

            # Exponential decay: recent events weighted higher
            time_weight = math.exp(-self.decay_rate * days_ago)
            weighted_total += time_weight

            if event['success']:
                # Apply boost from event type
                adjustment = event.get('confidence_adjustment', 0.0)
                weighted_successes += time_weight * (1.0 + max(0, adjustment))
            else:
                # Apply decay from event type
                adjustment = event.get('confidence_adjustment', 0.0)
                weighted_successes += time_weight * min(0, adjustment)

        # Calculate base confidence
        if weighted_total == 0:
            base_confidence = 0.5  # Neutral starting point
        else:
            base_confidence = max(0.0, min(1.0, weighted_successes / weighted_total))

        # Apply recent failure multiplier
        recent_failures = self._count_recent_failures(agent_id, days=7)
        failure_multiplier = max(0.5, 1.0 - (recent_failures * 0.1))

        final_confidence = base_confidence * failure_multiplier

        # Store confidence in-memory cache
        old_confidence = self.confidence_scores.get(agent_id, 0.5)
        self.confidence_scores[agent_id] = final_confidence

        # Append event to audit trail
        audit_event = {
            **current_event,
            'confidence_before': old_confidence,
            'confidence_after': final_confidence,
            'base_confidence': base_confidence,
            'failure_multiplier': failure_multiplier,
            'recent_failures': recent_failures
        }
        self._append_event(audit_event)

        logger.info(
            f"[CONFIDENCE] {agent_id}: {old_confidence:.3f} → {final_confidence:.3f} "
            f"(event: {event_type}, success: {success})"
        )

        return final_confidence

    def get_confidence(self, agent_id: str) -> float:
        """
        Get current confidence score for agent

        Args:
            agent_id: Agent identifier

        Returns:
            Confidence score (0.0 to 1.0), default 0.5
        """
        return self.confidence_scores.get(agent_id, 0.5)

    def get_confidence_trajectory(
        self,
        agent_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get confidence trajectory over time

        Args:
            agent_id: Agent identifier
            days: Number of days to look back

        Returns:
            List of {timestamp, confidence, event_type}
        """
        events = self._get_agent_history(agent_id, days=days)
        return [
            {
                'timestamp': e['timestamp'],
                'confidence': e.get('confidence_after', 0.5),
                'event_type': e.get('event_type', ''),
                'success': e.get('success', False)
            }
            for e in events
            if 'confidence_after' in e
        ]
