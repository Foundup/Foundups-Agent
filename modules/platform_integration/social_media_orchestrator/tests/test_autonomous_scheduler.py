#!/usr/bin/env python3
"""
Test suite for AutonomousActionScheduler
WSP Compliance: WSP 5 (Testing Coverage), WSP 6 (Test Audit)
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
import asyncio
from datetime import datetime, timedelta
from autonomous_action_scheduler import AutonomousActionScheduler, ActionType

class TestAutonomousActionScheduler(unittest.TestCase):
    """Test natural language understanding for 0102"""

    def setUp(self):
        self.scheduler = AutonomousActionScheduler()

    def test_time_parsing_minutes(self):
        """Test parsing 'in X minutes' format"""
        action = self.scheduler.understand_command("Post 'test' in 30 minutes")
        expected_time = datetime.now() + timedelta(minutes=30)

        # Allow 1 second tolerance for test execution time
        time_diff = abs((action.scheduled_time - expected_time).total_seconds())
        self.assertLess(time_diff, 2)

    def test_time_parsing_hours(self):
        """Test parsing 'in X hours' format"""
        action = self.scheduler.understand_command("Remind me in 2 hours")
        expected_time = datetime.now() + timedelta(hours=2)

        time_diff = abs((action.scheduled_time - expected_time).total_seconds())
        self.assertLess(time_diff, 2)

    def test_action_type_detection(self):
        """Test correct action type detection"""
        # Test post detection
        action = self.scheduler.understand_command("Post to LinkedIn")
        self.assertEqual(action.action_type, ActionType.POST_SOCIAL)

        # Test remind detection
        action = self.scheduler.understand_command("Remind me to check")
        self.assertEqual(action.action_type, ActionType.REMIND)

        # Test stream check detection
        action = self.scheduler.understand_command("Check the stream status")
        self.assertEqual(action.action_type, ActionType.CHECK_STREAM)

    def test_platform_detection(self):
        """Test platform extraction from command"""
        # LinkedIn detection
        action = self.scheduler.understand_command("Post to LinkedIn in 1 hour")
        self.assertIn('linkedin', action.parameters['platforms'])

        # X/Twitter detection
        action = self.scheduler.understand_command("Tweet this in 30 minutes")
        self.assertIn('x_twitter', action.parameters['platforms'])

        # Both platforms
        action = self.scheduler.understand_command("Post to both platforms now")
        self.assertIn('linkedin', action.parameters['platforms'])
        self.assertIn('x_twitter', action.parameters['platforms'])

    def test_content_extraction(self):
        """Test extracting quoted content from command"""
        action = self.scheduler.understand_command("Post 'Going live soon!' to LinkedIn")
        self.assertEqual(action.parameters['content'], "Going live soon!")

        # Test with double quotes
        action = self.scheduler.understand_command('Post "Hello World" to X')
        self.assertEqual(action.parameters['content'], "Hello World")

    def test_immediate_execution(self):
        """Test 'now' and 'immediately' parsing"""
        action = self.scheduler.understand_command("Post this now")
        time_diff = (action.scheduled_time - datetime.now()).total_seconds()
        self.assertLess(time_diff, 2)  # Should be within 2 seconds

        action = self.scheduler.understand_command("Post immediately")
        time_diff = (action.scheduled_time - datetime.now()).total_seconds()
        self.assertLess(time_diff, 2)

    def test_persistence(self):
        """Test schedule persistence"""
        # Create an action
        action = self.scheduler.understand_command("Post 'test' in 5 minutes")

        # Verify it's saved
        self.assertIn(action.id, self.scheduler.scheduled_actions)

        # Test cancellation
        result = self.scheduler.cancel_action(action.id)
        self.assertTrue(result)
        self.assertEqual(self.scheduler.scheduled_actions[action.id].status, "cancelled")

    async def test_pending_actions(self):
        """Test getting pending actions"""
        # Schedule multiple actions
        self.scheduler.understand_command("Post 'first' in 1 minute")
        self.scheduler.understand_command("Post 'second' in 2 minutes")
        self.scheduler.understand_command("Post 'third' in 3 minutes")

        pending = self.scheduler.get_pending_actions()
        self.assertEqual(len(pending), 3)

        # Verify they're sorted by time
        for i in range(len(pending) - 1):
            self.assertLess(pending[i].scheduled_time, pending[i+1].scheduled_time)

def run_tests():
    """Run the test suite"""
    unittest.main(argv=[''], exit=False, verbosity=2)

if __name__ == "__main__":
    run_tests()