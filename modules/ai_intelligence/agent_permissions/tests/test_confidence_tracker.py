# -*- coding: utf-8 -*-
"""
Unit Tests for Confidence Tracker

Tests decay-based confidence algorithm with time-weighted scoring,
failure multiplier, and JSONL audit trail.

WSP Compliance:
- WSP 5 (Test Coverage): Comprehensive unit tests
- WSP 6 (Test Audit): Documents test coverage
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

import sys
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.ai_intelligence.agent_permissions.src.confidence_tracker import (
    ConfidenceTracker,
    ConfidenceDecayEvent,
    ConfidenceBoostEvent
)


class TestConfidenceTracker(unittest.TestCase):
    """Test suite for ConfidenceTracker"""

    def setUp(self):
        """Set up test environment with temp directory"""
        import sqlite3
        self.test_dir = Path(tempfile.mkdtemp())
        # Create data/ directory for SQLite database
        (self.test_dir / "data").mkdir(parents=True, exist_ok=True)

        # Initialize database schema
        db_path = self.test_dir / "data" / "foundup.db"
        conn = sqlite3.connect(db_path)
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS confidence_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                confidence_before REAL,
                confidence_after REAL,
                event_type TEXT NOT NULL,
                success BOOLEAN,
                recorded_at TEXT NOT NULL,
                metadata_json TEXT
            );
        ''')
        conn.commit()
        conn.close()

        self.tracker = ConfidenceTracker(repo_root=self.test_dir)

    def tearDown(self):
        """Clean up test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_initialization(self):
        """Test tracker initialization"""
        self.assertEqual(self.tracker.decay_rate, 0.05)
        self.assertEqual(self.tracker.lookback_window_days, 30)
        self.assertTrue(self.tracker.db_path.parent.exists())
        # Database file created at initialization
        self.assertIsNotNone(self.tracker.db_path)
        self.assertTrue(self.tracker.db_path.exists())

    def test_default_confidence(self):
        """Test default confidence for new agent"""
        confidence = self.tracker.get_confidence("new_agent")
        self.assertEqual(confidence, 0.5)

    def test_boost_confidence_human_approval(self):
        """Test confidence boost from human approval"""
        agent_id = "test_agent"

        execution_result = {
            'success': True,
            'event_type': 'HUMAN_APPROVAL',
            'validation': 'Approved by 0102',
            'details': {'module': 'test_module'}
        }

        confidence = self.tracker.update_confidence(agent_id, execution_result)

        # Should be higher than default 0.5
        self.assertGreater(confidence, 0.5)
        self.assertLessEqual(confidence, 1.0)

    def test_decay_confidence_rollback(self):
        """Test confidence decay from rollback"""
        agent_id = "test_agent"

        # Start with approval
        self.tracker.update_confidence(agent_id, {
            'success': True,
            'event_type': 'HUMAN_APPROVAL',
            'validation': 'Approved'
        })

        confidence_before = self.tracker.get_confidence(agent_id)

        # Rollback event
        self.tracker.update_confidence(agent_id, {
            'success': False,
            'event_type': 'EDIT_ROLLED_BACK',
            'validation': 'Reverted by human',
            'rollback_reason': 'Incorrect implementation'
        })

        confidence_after = self.tracker.get_confidence(agent_id)

        # Should be lower after rollback
        self.assertLess(confidence_after, confidence_before)

    def test_wsp_violation_severe_decay(self):
        """Test severe decay from WSP violation"""
        agent_id = "test_agent"

        # Start with high confidence
        for _ in range(5):
            self.tracker.update_confidence(agent_id, {
                'success': True,
                'event_type': 'HUMAN_APPROVAL',
                'validation': 'Approved'
            })

        confidence_before = self.tracker.get_confidence(agent_id)

        # WSP violation (-0.20 decay)
        self.tracker.update_confidence(agent_id, {
            'success': False,
            'event_type': 'WSP_VIOLATION',
            'validation': 'Violated WSP 50',
            'details': {'wsp_id': 'WSP_50', 'violation': 'Modified without reading'}
        })

        confidence_after = self.tracker.get_confidence(agent_id)

        # Should have significant drop
        self.assertLess(confidence_after, confidence_before)

    def test_security_issue_critical_decay(self):
        """Test critical decay from security issue"""
        agent_id = "test_agent"

        # Start with moderate confidence (not maxed out)
        for _ in range(3):
            self.tracker.update_confidence(agent_id, {
                'success': True,
                'event_type': 'TESTS_PASSED',
                'validation': 'Tests passed'
            })

        confidence_before = self.tracker.get_confidence(agent_id)

        # Security issue (-0.50 decay - most severe)
        self.tracker.update_confidence(agent_id, {
            'success': False,
            'event_type': 'SECURITY_ISSUE',
            'validation': 'Created vulnerability',
            'details': {'issue': 'SQL injection possible'}
        })

        confidence_after = self.tracker.get_confidence(agent_id)

        # Should have significant drop
        self.assertLess(confidence_after, confidence_before)

    def test_failure_multiplier_effect(self):
        """Test failure multiplier reduces confidence"""
        agent_id = "test_agent"

        # Build up confidence
        for _ in range(5):
            self.tracker.update_confidence(agent_id, {
                'success': True,
                'event_type': 'TESTS_PASSED',
                'validation': 'All tests passed'
            })

        confidence_before_failures = self.tracker.get_confidence(agent_id)

        # Introduce 3 failures in last 7 days
        for _ in range(3):
            self.tracker.update_confidence(agent_id, {
                'success': False,
                'event_type': 'REGRESSION_CAUSED',
                'validation': 'Tests failed'
            })

        confidence_after_failures = self.tracker.get_confidence(agent_id)

        # Failure multiplier should have reduced confidence
        self.assertLess(confidence_after_failures, confidence_before_failures)

    def test_time_weighted_decay(self):
        """Test older events have less weight than recent events"""
        agent_id = "test_agent"

        # Start with old failure (30 days ago)
        old_failure = {
            'success': False,
            'event_type': 'FALSE_POSITIVE',
            'validation': 'Old failure',
            'timestamp': (datetime.now() - timedelta(days=30)).isoformat()
        }

        # Then recent success (1 day ago)
        recent_success = {
            'success': True,
            'event_type': 'TESTS_PASSED',
            'validation': 'Recent success',
            'timestamp': (datetime.now() - timedelta(days=1)).isoformat()
        }

        # Add old failure first
        self.tracker.update_confidence(agent_id, old_failure)

        # Add recent success
        self.tracker.update_confidence(agent_id, recent_success)
        confidence_after_recent = self.tracker.get_confidence(agent_id)

        # Recent success should outweigh old failure due to exponential time decay
        # Confidence should recover above neutral (0.5)
        self.assertGreater(confidence_after_recent, 0.5)

    def test_lookback_window_enforcement(self):
        """Test events older than 30 days are ignored"""
        agent_id = "test_agent"

        # Event from 31 days ago (should be ignored)
        old_event = {
            'success': False,
            'event_type': 'REGRESSION_CAUSED',
            'validation': 'Old failure',
            'timestamp': (datetime.now() - timedelta(days=31)).isoformat()
        }

        self.tracker.update_confidence(agent_id, old_event)

        # Should still be at neutral starting point (0.5)
        # because event is outside lookback window
        confidence = self.tracker.get_confidence(agent_id)
        self.assertEqual(confidence, 0.5)

    def test_confidence_bounds(self):
        """Test confidence stays within [0.0, 1.0] bounds"""
        agent_id = "test_agent"

        # Try to push confidence above 1.0
        for _ in range(20):
            self.tracker.update_confidence(agent_id, {
                'success': True,
                'event_type': 'PRODUCTION_STABLE',
                'validation': 'Production stable'
            })

        confidence = self.tracker.get_confidence(agent_id)
        self.assertLessEqual(confidence, 1.0)

        # Try to push confidence below 0.0
        for _ in range(20):
            self.tracker.update_confidence(agent_id, {
                'success': False,
                'event_type': 'SECURITY_ISSUE',
                'validation': 'Security issue'
            })

        confidence = self.tracker.get_confidence(agent_id)
        self.assertGreaterEqual(confidence, 0.0)

    def test_jsonl_audit_trail(self):
        """Test SQLite audit trail is written correctly"""
        import sqlite3
        agent_id = "test_agent"

        self.tracker.update_confidence(agent_id, {
            'success': True,
            'event_type': 'HUMAN_APPROVAL',
            'validation': 'Approved by 0102'
        })

        # Read from SQLite database
        conn = sqlite3.connect(self.tracker.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM confidence_events WHERE agent_id = ?', (agent_id,))
        rows = cursor.fetchall()
        conn.close()

        self.assertEqual(len(rows), 1)
        row = rows[0]

        # Verify event structure (id, agent_id, conf_before, conf_after, event_type, success, recorded_at, metadata_json)
        self.assertEqual(row[1], agent_id)  # agent_id
        self.assertTrue(row[5])  # success
        self.assertEqual(row[4], 'HUMAN_APPROVAL')  # event_type
        self.assertIsNotNone(row[2])  # confidence_before
        self.assertIsNotNone(row[3])  # confidence_after
        self.assertIsNotNone(row[6])  # recorded_at

    def test_confidence_persistence(self):
        """Test confidence events persist in SQLite across tracker instances"""
        import sqlite3
        agent_id = "test_agent"

        # Update confidence
        self.tracker.update_confidence(agent_id, {
            'success': True,
            'event_type': 'HUMAN_APPROVAL',
            'validation': 'Approved'
        })

        # Verify event persisted to SQLite
        conn = sqlite3.connect(self.tracker.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM confidence_events WHERE agent_id = ?', (agent_id,))
        count_before = cursor.fetchone()[0]
        conn.close()

        self.assertGreater(count_before, 0)

        # Create new tracker instance - events should still be in SQLite
        new_tracker = ConfidenceTracker(repo_root=self.test_dir)

        conn = sqlite3.connect(new_tracker.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM confidence_events WHERE agent_id = ?', (agent_id,))
        count_after = cursor.fetchone()[0]
        conn.close()

        # Events persisted across instances
        self.assertEqual(count_before, count_after)

    def test_get_confidence_trajectory(self):
        """Test confidence trajectory retrieval"""
        agent_id = "test_agent"

        # Create multiple events
        for i in range(5):
            self.tracker.update_confidence(agent_id, {
                'success': True,
                'event_type': 'TESTS_PASSED',
                'validation': f'Test {i}'
            })

        trajectory = self.tracker.get_confidence_trajectory(agent_id, days=30)

        self.assertEqual(len(trajectory), 5)

        # Verify structure
        for point in trajectory:
            self.assertIn('timestamp', point)
            self.assertIn('confidence', point)
            self.assertIn('event_type', point)
            self.assertIn('success', point)

    def test_multiple_agents_isolation(self):
        """Test multiple agents have isolated confidence scores"""
        agent1 = "gemma_dead_code_detection"
        agent2 = "qwen_code_quality_investigator"

        # Agent 1: High confidence
        for _ in range(5):
            self.tracker.update_confidence(agent1, {
                'success': True,
                'event_type': 'PRODUCTION_STABLE',
                'validation': 'Stable'
            })

        # Agent 2: Low confidence
        for _ in range(3):
            self.tracker.update_confidence(agent2, {
                'success': False,
                'event_type': 'REGRESSION_CAUSED',
                'validation': 'Failed'
            })

        confidence1 = self.tracker.get_confidence(agent1)
        confidence2 = self.tracker.get_confidence(agent2)

        # Should be different
        self.assertNotEqual(confidence1, confidence2)
        self.assertGreater(confidence1, confidence2)

    def test_recent_failures_counting(self):
        """Test recent failures are counted correctly"""
        agent_id = "test_agent"

        # Add 5 failures in last 7 days
        for i in range(5):
            self.tracker.update_confidence(agent_id, {
                'success': False,
                'event_type': 'FALSE_POSITIVE',
                'validation': f'Failure {i}',
                'timestamp': (datetime.now() - timedelta(days=i)).isoformat()
            })

        # Count recent failures (internal method test via side effects)
        recent_count = self.tracker._count_recent_failures(agent_id, days=7)
        self.assertEqual(recent_count, 5)

        # Add old failure (8 days ago) - should not be counted
        self.tracker.update_confidence(agent_id, {
            'success': False,
            'event_type': 'FALSE_POSITIVE',
            'validation': 'Old failure',
            'timestamp': (datetime.now() - timedelta(days=8)).isoformat()
        })

        recent_count = self.tracker._count_recent_failures(agent_id, days=7)
        self.assertEqual(recent_count, 5)  # Still 5, not 6

    def test_atomic_write_confidence_scores(self):
        """Test confidence scores are written atomically"""
        agent_id = "test_agent"

        self.tracker.update_confidence(agent_id, {
            'success': True,
            'event_type': 'HUMAN_APPROVAL',
            'validation': 'Approved'
        })

        # Verify database write succeeded
        import sqlite3
        conn = sqlite3.connect(self.tracker.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM confidence_events WHERE agent_id = ?', (agent_id,))
        count = cursor.fetchone()[0]
        conn.close()

        self.assertGreater(count, 0)

    def test_production_stable_highest_boost(self):
        """Test PRODUCTION_STABLE gives highest confidence boost"""
        # Verify enum values directly
        stable_boost = ConfidenceBoostEvent.PRODUCTION_STABLE.value
        test_boost = ConfidenceBoostEvent.TESTS_PASSED.value

        # PRODUCTION_STABLE (+0.15) should be higher than TESTS_PASSED (+0.05)
        self.assertGreater(stable_boost, test_boost)
        self.assertEqual(stable_boost, 0.15)
        self.assertEqual(test_boost, 0.05)


class TestConfidenceDecayEvent(unittest.TestCase):
    """Test suite for ConfidenceDecayEvent enum"""

    def test_decay_event_values(self):
        """Test decay event values are negative"""
        self.assertLess(ConfidenceDecayEvent.EDIT_ROLLED_BACK.value, 0)
        self.assertLess(ConfidenceDecayEvent.HUMAN_REJECTION.value, 0)
        self.assertLess(ConfidenceDecayEvent.WSP_VIOLATION.value, 0)
        self.assertLess(ConfidenceDecayEvent.REGRESSION_CAUSED.value, 0)
        self.assertLess(ConfidenceDecayEvent.SECURITY_ISSUE.value, 0)

    def test_security_issue_most_severe(self):
        """Test SECURITY_ISSUE has most severe decay"""
        security_decay = abs(ConfidenceDecayEvent.SECURITY_ISSUE.value)

        for event in ConfidenceDecayEvent:
            if event != ConfidenceDecayEvent.SECURITY_ISSUE:
                self.assertGreater(security_decay, abs(event.value))


class TestConfidenceBoostEvent(unittest.TestCase):
    """Test suite for ConfidenceBoostEvent enum"""

    def test_boost_event_values(self):
        """Test boost event values are positive"""
        self.assertGreater(ConfidenceBoostEvent.HUMAN_APPROVAL.value, 0)
        self.assertGreater(ConfidenceBoostEvent.TESTS_PASSED.value, 0)
        self.assertGreater(ConfidenceBoostEvent.WSP_COMPLIANT.value, 0)
        self.assertGreater(ConfidenceBoostEvent.PEER_VALIDATION.value, 0)
        self.assertGreater(ConfidenceBoostEvent.PRODUCTION_STABLE.value, 0)

    def test_production_stable_highest_boost(self):
        """Test PRODUCTION_STABLE gives highest boost"""
        stable_boost = ConfidenceBoostEvent.PRODUCTION_STABLE.value

        for event in ConfidenceBoostEvent:
            if event != ConfidenceBoostEvent.PRODUCTION_STABLE:
                self.assertGreater(stable_boost, event.value)


if __name__ == '__main__':
    unittest.main()
