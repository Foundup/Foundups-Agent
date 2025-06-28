"""
Session Manager Tests

Tests for the WRE SessionManager component including:
- Session lifecycle management
- Operation logging and tracking  
- Module access monitoring
- Achievement and milestone tracking

Follows WSP 6 test coverage requirements.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.components.session_manager import SessionManager

class TestSessionManager(unittest.TestCase):
    """Test SessionManager component functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).resolve().parent.parent.parent.parent
        self.session_manager = SessionManager(self.project_root)
    
    def test_initialization(self):
        """Test SessionManager initialization."""
        self.assertEqual(self.session_manager.project_root, self.project_root)
        self.assertIsNone(self.session_manager.current_session_id)
        self.assertIsNotNone(self.session_manager.sessions)
        
    def test_start_session(self):
        """Test session start functionality."""
        session_id = self.session_manager.start_session("interactive")
        
        self.assertIsNotNone(session_id)
        self.assertEqual(self.session_manager.current_session_id, session_id)
        self.assertIn(session_id, self.session_manager.sessions)
        
        session = self.session_manager.sessions[session_id]
        self.assertEqual(session["type"], "interactive")
        self.assertIn("start_time", session)
        self.assertEqual(session["operations_count"], 0)
        self.assertEqual(session["modules_accessed"], [])
        
    def test_start_session_types(self):
        """Test different session types."""
        types = ["interactive", "automation", "test", "wsp30"]
        
        for session_type in types:
            session_id = self.session_manager.start_session(session_type)
            session = self.session_manager.sessions[session_id]
            self.assertEqual(session["type"], session_type)
            
    def test_log_operation(self):
        """Test operation logging."""
        session_id = self.session_manager.start_session("test")
        
        operation_data = {"action": "test_action", "result": "success"}
        self.session_manager.log_operation("test_operation", operation_data)
        
        session = self.session_manager.sessions[session_id]
        self.assertEqual(session["operations_count"], 1)
        self.assertIn("operations", session)
        
        logged_op = session["operations"][0]
        self.assertEqual(logged_op["type"], "test_operation")
        self.assertEqual(logged_op["data"], operation_data)
        self.assertIn("timestamp", logged_op)
        
    def test_log_achievement(self):
        """Test achievement logging."""
        session_id = self.session_manager.start_session("test")
        
        self.session_manager.log_achievement("test_achievement", "Test achievement completed")
        
        session = self.session_manager.sessions[session_id]
        self.assertIn("achievements", session)
        
        achievement = session["achievements"][0]
        self.assertEqual(achievement["name"], "test_achievement")
        self.assertEqual(achievement["description"], "Test achievement completed")
        self.assertIn("timestamp", achievement)
        
    def test_log_module_access(self):
        """Test module access logging."""
        session_id = self.session_manager.start_session("test")
        
        self.session_manager.log_module_access("test_module", "development")
        
        session = self.session_manager.sessions[session_id]
        self.assertIn("test_module", session["modules_accessed"])
        self.assertIn("module_access", session)
        
        access_log = session["module_access"][0]
        self.assertEqual(access_log["module"], "test_module")
        self.assertEqual(access_log["access_type"], "development")
        self.assertIn("timestamp", access_log)
        
    def test_multiple_operations(self):
        """Test multiple operations in a session."""
        session_id = self.session_manager.start_session("test")
        
        # Log multiple operations
        for i in range(5):
            self.session_manager.log_operation(f"operation_{i}", {"index": i})
            
        session = self.session_manager.sessions[session_id]
        self.assertEqual(session["operations_count"], 5)
        self.assertEqual(len(session["operations"]), 5)
        
    def test_session_without_start(self):
        """Test operations without starting a session."""
        # Should handle gracefully when no session is active
        self.session_manager.log_operation("test_op", {})
        self.session_manager.log_achievement("test_achievement", "Test")
        self.session_manager.log_module_access("test_module", "test")
        
        # Should not create sessions automatically
        self.assertIsNone(self.session_manager.current_session_id)
        
    def test_session_data_structure(self):
        """Test session data structure completeness."""
        session_id = self.session_manager.start_session("comprehensive")
        
        # Add various types of data
        self.session_manager.log_operation("init", {"component": "test"})
        self.session_manager.log_achievement("setup", "Setup completed")
        self.session_manager.log_module_access("test_module", "testing")
        
        session = self.session_manager.sessions[session_id]
        
        # Verify all expected fields exist
        required_fields = [
            "type", "start_time", "operations_count", 
            "modules_accessed", "operations", "achievements", "module_access"
        ]
        
        for field in required_fields:
            self.assertIn(field, session)
            
    def test_timestamp_format(self):
        """Test timestamp formatting consistency."""
        session_id = self.session_manager.start_session("test")
        self.session_manager.log_operation("timestamp_test", {})
        
        session = self.session_manager.sessions[session_id]
        operation = session["operations"][0]
        
        # Verify timestamp is ISO format string
        timestamp = operation["timestamp"]
        self.assertIsInstance(timestamp, str)
        
        # Should be parseable as datetime
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            self.fail("Timestamp is not in valid ISO format")

if __name__ == '__main__':
    unittest.main() 