# -*- coding: utf-8 -*-
"""
Test Selenium Run History Mission

Tests the selenium run history mission with in-memory SQLite database.
Validates data aggregation and summary generation.

WSP 77: Agent Coordination Protocol
"""

import unittest
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from missions.selenium_run_history import SeleniumRunHistoryMission


class TestSeleniumRunHistoryMission(unittest.TestCase):
    """Test cases for selenium run history mission"""

    def setUp(self):
        """Set up test database with sample data"""
        self.db_fd, self.db_path = tempfile.mkstemp()

        # Create in-memory database for testing
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        # Create selenium_sessions table
        self.conn.execute("""
            CREATE TABLE selenium_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                status TEXT CHECK(status IN ('success', 'failed', 'timeout', 'error')),
                hash TEXT,
                duration_seconds INTEGER,
                user_agent TEXT,
                browser TEXT DEFAULT 'chrome',
                session_id TEXT,
                error_message TEXT,
                page_title TEXT,
                screenshot_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert sample test data
        base_time = datetime.now() - timedelta(days=3)

        test_sessions = [
            # Successful runs
            ('https://example.com/page1', base_time, 'success', 'hash1', 30, 'chrome'),
            ('https://example.com/page1', base_time + timedelta(hours=1), 'success', 'hash1', 25, 'chrome'),
            ('https://example.com/page2', base_time + timedelta(hours=2), 'success', 'hash2', 45, 'firefox'),

            # Failed runs
            ('https://example.com/page1', base_time + timedelta(hours=3), 'failed', 'hash1', 60, 'chrome'),
            ('https://example.com/page3', base_time + timedelta(hours=4), 'timeout', 'hash3', 120, 'chrome'),

            # Recent runs (within last day)
            ('https://example.com/page1', datetime.now() - timedelta(hours=12), 'success', 'hash4', 28, 'chrome'),
            ('https://example.com/page2', datetime.now() - timedelta(hours=6), 'success', 'hash5', 35, 'firefox'),
        ]

        for url, start_time, status, hash_val, duration, browser in test_sessions:
            end_time = start_time + timedelta(seconds=duration)
            self.conn.execute("""
                INSERT INTO selenium_sessions
                (url, start_time, end_time, status, hash, duration_seconds, browser)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (url, start_time.isoformat(), end_time.isoformat(), status, hash_val, duration, browser))

        self.conn.commit()

    def tearDown(self):
        """Clean up test database"""
        if hasattr(self, 'conn'):
            self.conn.close()
        if hasattr(self, 'db_fd'):
            os.close(self.db_fd)
        if hasattr(self, 'db_path') and os.path.exists(self.db_path):
            # Try to close any remaining connections
            try:
                os.unlink(self.db_path)
            except PermissionError:
                # File might still be in use, skip cleanup
                pass

    def test_mission_execution(self):
        """Test basic mission execution"""
        mission = SeleniumRunHistoryMission(self.db_path)
        result = mission.execute_mission(days=7)

        # Validate result structure
        self.assertTrue(result['summary_ready'])
        self.assertEqual(result['mission'], 'selenium_run_history')
        self.assertIn('overall_stats', result)
        self.assertIn('url_breakdown', result)
        self.assertIn('raw_session_count', result)

    def test_overall_stats_calculation(self):
        """Test overall statistics calculation"""
        mission = SeleniumRunHistoryMission(self.db_path)
        result = mission.execute_mission(days=7)

        overall = result['overall_stats']

        # We inserted 7 sessions total
        self.assertEqual(overall['total_sessions'], 7)

        # 5 success, 1 failed, 1 timeout = 71.4% success rate
        self.assertAlmostEqual(overall['success_rate'], 71.43, places=1)

        # 3 unique URLs
        self.assertEqual(overall['unique_urls'], 3)

        # Time range should be calculated
        self.assertIsNotNone(overall['time_range'])

    def test_url_breakdown(self):
        """Test URL-specific breakdown"""
        mission = SeleniumRunHistoryMission(self.db_path)
        result = mission.execute_mission(days=7)

        url_stats = result['url_breakdown']

        # Should have 3 URLs
        self.assertEqual(len(url_stats), 3)

        # Check page1 stats (4 runs: 3 success, 1 failed)
        page1_stats = url_stats['https://example.com/page1']
        self.assertEqual(page1_stats['total_runs'], 4)
        self.assertEqual(page1_stats['success_count'], 3)
        self.assertEqual(page1_stats['failed_count'], 1)
        self.assertEqual(page1_stats['success_rate'], 75.0)

        # Check browsers used
        self.assertIn('chrome', page1_stats['browsers_used'])

    def test_empty_database(self):
        """Test mission with empty database"""
        # Create empty database
        empty_fd, empty_path = tempfile.mkstemp()
        empty_conn = sqlite3.connect(empty_path)
        empty_conn.close()
        empty_conn = None  # Ensure connection is closed

        try:
            mission = SeleniumRunHistoryMission(empty_path)
            result = mission.execute_mission(days=7)

            # Should handle empty database gracefully
            self.assertTrue(result['summary_ready'])
            self.assertEqual(result['raw_session_count'], 0)
            self.assertEqual(result['overall_stats']['total_sessions'], 0)

        finally:
            if empty_conn:
                empty_conn.close()
            os.close(empty_fd)
            try:
                os.unlink(empty_path)
            except PermissionError:
                pass

    def test_table_creation(self):
        """Test automatic table creation"""
        # Create database without selenium_sessions table
        no_table_fd, no_table_path = tempfile.mkstemp()
        no_table_conn = sqlite3.connect(no_table_path)
        no_table_conn.close()
        no_table_conn = None  # Ensure connection is closed

        try:
            mission = SeleniumRunHistoryMission(no_table_path)
            result = mission.execute_mission(days=7)

            # Should create table and return empty results
            self.assertTrue(result['summary_ready'])
            self.assertFalse(result['parameters']['table_existed'])
            self.assertEqual(result['raw_session_count'], 0)

        finally:
            if no_table_conn:
                no_table_conn.close()
            os.close(no_table_fd)
            try:
                os.unlink(no_table_path)
            except PermissionError:
                pass

    def test_recent_sessions_filtering(self):
        """Test filtering by recent days"""
        mission = SeleniumRunHistoryMission(self.db_path)

        # Test with 1 day (should get fewer results)
        result_1day = mission.execute_mission(days=1)
        result_7days = mission.execute_mission(days=7)

        # 1-day should have fewer sessions than 7-day
        self.assertLess(result_1day['raw_session_count'], result_7days['raw_session_count'])

    def test_sample_sessions(self):
        """Test sample sessions inclusion"""
        mission = SeleniumRunHistoryMission(self.db_path)
        result = mission.execute_mission(days=7)

        # Should include sample sessions
        self.assertIn('sample_sessions', result)
        self.assertIsInstance(result['sample_sessions'], list)
        self.assertLessEqual(len(result['sample_sessions']), 5)  # Max 5 samples

        # Each sample should have required fields
        for session in result['sample_sessions']:
            self.assertIn('url', session)
            self.assertIn('start_time', session)
            self.assertIn('status', session)


if __name__ == '__main__':
    unittest.main()
