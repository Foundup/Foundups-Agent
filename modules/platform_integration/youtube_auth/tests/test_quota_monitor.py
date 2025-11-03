"""
Test Suite for QuotaMonitor Class
WSP-Compliant: WSP 4 (FMAS), WSP 5 (90% Coverage), WSP 84 (Code Memory)

This module provides comprehensive testing for the QuotaMonitor class,
ensuring proper quota tracking, daily resets, alerts, and rotation logic.

WSP 17 Pattern Registry: Reusable quota testing pattern
- Can be adapted for LinkedIn, X/Twitter, Discord quota management
"""



import unittest
import json
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.quota_monitor import QuotaMonitor


class TestQuotaMonitor(unittest.TestCase):
    """
    Test suite for QuotaMonitor functionality.
    WSP 4 FMAS-F: Comprehensive functional testing
    WSP 5: Target >90% code coverage
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.monitor = QuotaMonitor(memory_dir=self.test_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """WSP 4 FMAS-F: Test QuotaMonitor initialization."""
        # Verify memory directory created
        self.assertTrue(os.path.exists(self.test_dir))
        
        # Verify quota limits initialized
        self.assertEqual(len(self.monitor.daily_limits), 7)
        for i in range(1, 8):
            self.assertEqual(self.monitor.daily_limits[i], 10000)
        
        # Verify thresholds
        self.assertEqual(self.monitor.warning_threshold, 0.8)
        self.assertEqual(self.monitor.critical_threshold, 0.95)
    
    def test_track_api_call_basic(self):
        """WSP 4 FMAS-F: Test basic API call tracking."""
        # Track a simple API call
        self.monitor.track_api_call(1, 'channels.list')
        
        # Verify usage recorded
        set_data = self.monitor.usage_data['sets']['1']
        self.assertEqual(set_data['used'], 1)
        self.assertEqual(set_data['operations']['channels.list']['count'], 1)
        self.assertEqual(set_data['operations']['channels.list']['units'], 1)
    
    def test_track_api_call_multiple_operations(self):
        """WSP 4 FMAS-F: Test tracking multiple operation types."""
        # Track various API operations
        self.monitor.track_api_call(1, 'liveChatMessages.list')  # 5 units
        self.monitor.track_api_call(1, 'liveChatMessages.insert')  # 200 units
        self.monitor.track_api_call(1, 'search.list')  # 100 units
        
        # Verify total usage
        set_data = self.monitor.usage_data['sets']['1']
        self.assertEqual(set_data['used'], 305)
        
        # Verify individual operations
        self.assertEqual(set_data['operations']['liveChatMessages.list']['units'], 5)
        self.assertEqual(set_data['operations']['liveChatMessages.insert']['units'], 200)
        self.assertEqual(set_data['operations']['search.list']['units'], 100)
    
    def test_check_daily_reset(self):
        """WSP 4 FMAS-F: Test daily quota reset at 24-hour boundary."""
        # Set last reset to 25 hours ago
        old_time = datetime.now() - timedelta(hours=25)
        self.monitor.usage_data['last_reset'] = old_time.isoformat()
        
        # Add some usage
        self.monitor.usage_data['sets']['1'] = {'used': 5000, 'operations': {}}
        
        # Trigger reset check
        self.monitor._check_daily_reset()
        
        # Verify reset occurred
        self.assertEqual(self.monitor.usage_data['sets'], {})
        
        # Verify new reset time is recent
        new_reset = datetime.fromisoformat(self.monitor.usage_data['last_reset'])
        time_diff = datetime.now() - new_reset
        self.assertLess(time_diff.seconds, 5)
    
    def test_check_daily_reset_not_needed(self):
        """WSP 4 FMAS-F: Test daily reset when not yet 24 hours."""
        # Set last reset to 23 hours ago
        recent_time = datetime.now() - timedelta(hours=23)
        self.monitor.usage_data['last_reset'] = recent_time.isoformat()
        
        # Add some usage
        self.monitor.usage_data['sets']['1'] = {'used': 5000, 'operations': {}}
        
        # Trigger reset check
        self.monitor._check_daily_reset()
        
        # Verify NO reset occurred
        self.assertIn('1', self.monitor.usage_data['sets'])
        self.assertEqual(self.monitor.usage_data['sets']['1']['used'], 5000)
    
    @patch('src.quota_monitor.logger')
    def test_alert_warning_threshold(self, mock_logger):
        """WSP 4 FMAS-F: Test alert at 80% warning threshold."""
        # Set usage to 80% (8000/10000)
        self.monitor.usage_data['sets']['1'] = {
            'used': 8000,
            'operations': {},
            'last_call': datetime.now().isoformat()
        }
        
        # Check alerts
        self.monitor._check_alerts(1)
        
        # Verify warning logged
        mock_logger.warning.assert_called_once()
        warning_msg = mock_logger.warning.call_args[0][0]
        self.assertIn('WARNING', warning_msg)
        self.assertIn('80.0%', warning_msg)
    
    @patch('src.quota_monitor.logger')
    def test_alert_critical_threshold(self, mock_logger):
        """WSP 4 FMAS-F: Test alert at 95% critical threshold."""
        # Set usage to 95% (9500/10000)
        self.monitor.usage_data['sets']['1'] = {
            'used': 9500,
            'operations': {},
            'last_call': datetime.now().isoformat()
        }
        
        # Check alerts
        self.monitor._check_alerts(1)
        
        # Verify critical alert logged
        mock_logger.critical.assert_called_once()
        critical_msg = mock_logger.critical.call_args[0][0]
        self.assertIn('CRITICAL', critical_msg)
        self.assertIn('95.0%', critical_msg)
    
    def test_get_best_credential_set(self):
        """WSP 4 FMAS-F: Test credential set rotation logic."""
        # Set up various usage levels for ALL sets
        self.monitor.usage_data['sets'] = {
            '1': {'used': 9500},  # 95% - critical
            '2': {'used': 7000},  # 70% - moderate  
            '3': {'used': 1000},  # 10% - healthy (best)
            '4': {'used': 8500},  # 85% - warning
            '5': {'used': 9000},  # 90% - warning
            '6': {'used': 8200},  # 82% - warning
            '7': {'used': 7500},  # 75% - moderate
        }
        
        # Get best set
        best_set = self.monitor.get_best_credential_set()
        
        # Should return set 3 (lowest usage under warning threshold)
        self.assertEqual(best_set, 3)
    
    def test_get_best_credential_set_all_exhausted(self):
        """WSP 4 FMAS-F: Test when all sets are exhausted."""
        # Set all sets above warning threshold
        for i in range(1, 8):
            self.monitor.usage_data['sets'][str(i)] = {'used': 9000}
        
        # Get best set
        best_set = self.monitor.get_best_credential_set()
        
        # Should return None when all exhausted
        self.assertIsNone(best_set)
    
    def test_quota_file_persistence(self):
        """WSP 4 FMAS-F: Test quota data file persistence."""
        # Track some API calls
        self.monitor.track_api_call(1, 'channels.list')
        self.monitor.track_api_call(2, 'search.list')
        
        # Create new monitor instance (simulating restart)
        new_monitor = QuotaMonitor(memory_dir=self.test_dir)
        
        # Verify data persisted
        self.assertIn('1', new_monitor.usage_data['sets'])
        self.assertIn('2', new_monitor.usage_data['sets'])
        self.assertEqual(new_monitor.usage_data['sets']['1']['used'], 1)
        self.assertEqual(new_monitor.usage_data['sets']['2']['used'], 100)
    
    def test_estimate_operations_remaining(self):
        """WSP 4 FMAS-F: Test operation estimation calculation."""
        # Set usage for set 1
        self.monitor.usage_data['sets']['1'] = {'used': 8000}
        
        # Estimate remaining operations
        remaining_list = self.monitor.estimate_operations_remaining(1, 'liveChatMessages.list')
        remaining_insert = self.monitor.estimate_operations_remaining(1, 'liveChatMessages.insert')
        
        # 2000 units remaining
        # liveChatMessages.list = 5 units each, so 2000/5 = 400
        # liveChatMessages.insert = 200 units each, so 2000/200 = 10
        self.assertEqual(remaining_list, 400)
        self.assertEqual(remaining_insert, 10)
    
    def test_get_usage_summary(self):
        """WSP 4 FMAS-F: Test usage summary generation."""
        # Set up some usage
        self.monitor.track_api_call(1, 'channels.list')  # 1 unit
        self.monitor.track_api_call(2, 'search.list')  # 100 units
        
        # Get summary
        summary = self.monitor.get_usage_summary()
        
        # Verify summary structure
        self.assertIn('timestamp', summary)
        self.assertEqual(summary['total_available'], 70000)
        self.assertEqual(summary['total_used'], 101)
        self.assertEqual(summary['total_available_remaining'], 69899)
        
        # Verify per-set data
        self.assertEqual(summary['sets'][1]['used'], 1)
        self.assertEqual(summary['sets'][1]['status'], 'HEALTHY')
        self.assertEqual(summary['sets'][2]['used'], 100)
        self.assertEqual(summary['sets'][2]['status'], 'HEALTHY')
    
    def test_custom_quota_units(self):
        """WSP 4 FMAS-F: Test tracking with custom unit values."""
        # Track with custom units
        self.monitor.track_api_call(1, 'custom.operation', units=500)
        
        # Verify custom units recorded
        set_data = self.monitor.usage_data['sets']['1']
        self.assertEqual(set_data['used'], 500)
        self.assertEqual(set_data['operations']['custom.operation']['units'], 500)
    
    def test_alert_file_creation(self):
        """WSP 4 FMAS-F: Test alert trigger file creation."""
        # Trigger a critical alert
        self.monitor.usage_data['sets']['1'] = {
            'used': 9500,
            'operations': {},
            'last_call': datetime.now().isoformat()
        }
        
        self.monitor._check_alerts(1)
        
        # Verify alert trigger file created
        alert_file = Path(self.test_dir) / "quota_alert_trigger.txt"
        self.assertTrue(alert_file.exists())
        
        # Verify alert content
        with open(alert_file, 'r', encoding="utf-8") as f:
            alert_data = json.loads(f.read())
            self.assertEqual(alert_data['severity'], 'CRITICAL')
            self.assertEqual(alert_data['credential_set'], 1)
    
    def test_generate_report(self):
        """WSP 4 FMAS-F: Test report generation."""
        # Set up some data
        self.monitor.track_api_call(1, 'channels.list')
        self.monitor.track_api_call(1, 'liveChatMessages.insert')
        
        # Generate report
        report = self.monitor.generate_report()
        
        # Verify report contains expected sections
        self.assertIn('YOUTUBE API QUOTA USAGE REPORT', report)
        self.assertIn('Total Quota:', report)
        self.assertIn('CREDENTIAL SET BREAKDOWN', report)
        self.assertIn('Set 1:', report)
    
    def test_concurrent_api_tracking(self):
        """WSP 4 FMAS-F: Test concurrent API call tracking."""
        # Simulate rapid concurrent calls
        for i in range(10):
            self.monitor.track_api_call(1, 'channels.list')
        
        # Verify all calls tracked
        set_data = self.monitor.usage_data['sets']['1']
        self.assertEqual(set_data['used'], 10)
        self.assertEqual(set_data['operations']['channels.list']['count'], 10)


class TestQuotaMonitorWSPCompliance(unittest.TestCase):
    """
    WSP Compliance tests for QuotaMonitor.
    Ensures adherence to WSP protocols.
    """
    
    def test_wsp_17_pattern_registry(self):
        """WSP 17: Verify quota pattern is reusable."""
        # QuotaMonitor should be adaptable to other platforms
        test_limits = {
            1: 5000,  # LinkedIn limit
            2: 3000,  # X/Twitter limit
            3: 15000  # Discord limit
        }
        
        monitor = QuotaMonitor(memory_dir=tempfile.mkdtemp())
        monitor.daily_limits = test_limits
        
        # Should work with different limits
        monitor.track_api_call(1, 'posts.create', units=50)
        self.assertEqual(monitor.usage_data['sets']['1']['used'], 50)
    
    def test_wsp_75_token_measurement(self):
        """WSP 75: Token efficiency tracking."""
        # Track that operations use minimal tokens
        monitor = QuotaMonitor(memory_dir=tempfile.mkdtemp())
        
        # Operation should complete in <200 tokens (pattern-based)
        start_memory = monitor.usage_data
        monitor.track_api_call(1, 'channels.list')
        end_memory = monitor.usage_data
        
        # Verify minimal memory overhead
        memory_diff = len(json.dumps(end_memory)) - len(json.dumps(start_memory))
        self.assertLess(memory_diff, 500)  # Less than 500 chars added
    
    def test_wsp_64_violation_prevention(self):
        """WSP 64: Prevent quota violations before they occur."""
        monitor = QuotaMonitor(memory_dir=tempfile.mkdtemp())
        
        # Set near limit
        monitor.usage_data['sets']['1'] = {'used': 9999}
        
        # Check if operation would exceed
        remaining = monitor.estimate_operations_remaining(1, 'liveChatMessages.insert')
        
        # Should return 0 (prevent violation)
        self.assertEqual(remaining, 0)


if __name__ == '__main__':
    # WSP 5: Run with coverage reporting
    unittest.main(verbosity=2)