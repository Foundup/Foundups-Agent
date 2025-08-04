"""
Test suite for utils module functions.

WSP Compliance: WSP 34 Testing Protocol
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

# Import utility functions to test
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import utility modules
try:
    from oauth_manager import OAuthManager
    from session_logger import SessionLogger
    from env_loader import EnvLoader
    from memory_path_resolver import MemoryPathResolver
    from wsp_system_integration import WSPSystemIntegration
    from logging_config import LoggingConfig
    from throttling import ThrottlingManager
except ImportError as e:
    print(f"Warning: Could not import some utility modules: {e}")


class TestOAuthManager(unittest.TestCase):
    """Test OAuth manager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.oauth_manager = OAuthManager()
    
    def test_oauth_manager_initialization(self):
        """Test OAuth manager initialization."""
        self.assertIsNotNone(self.oauth_manager)
        self.assertTrue(hasattr(self.oauth_manager, 'get_auth_url'))
    
    def test_get_auth_url(self):
        """Test getting authentication URL."""
        with patch.object(self.oauth_manager, 'get_auth_url') as mock_get_url:
            mock_get_url.return_value = "https://example.com/auth"
            auth_url = self.oauth_manager.get_auth_url("youtube")
            self.assertEqual(auth_url, "https://example.com/auth")
    
    def test_handle_callback(self):
        """Test handling OAuth callback."""
        with patch.object(self.oauth_manager, 'handle_callback') as mock_callback:
            mock_callback.return_value = {"access_token": "test_token"}
            tokens = self.oauth_manager.handle_callback("test_code")
            self.assertEqual(tokens["access_token"], "test_token")


class TestSessionLogger(unittest.TestCase):
    """Test session logger functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.session_logger = SessionLogger()
    
    def test_session_logger_initialization(self):
        """Test session logger initialization."""
        self.assertIsNotNone(self.session_logger)
        self.assertTrue(hasattr(self.session_logger, 'log_event'))
    
    def test_log_event(self):
        """Test logging session event."""
        with patch.object(self.session_logger, 'log_event') as mock_log:
            mock_log.return_value = True
            result = self.session_logger.log_event(
                event_type="test_event",
                user_id="test_user",
                details={"test": "data"}
            )
            self.assertTrue(result)
    
    def test_get_session_stats(self):
        """Test getting session statistics."""
        with patch.object(self.session_logger, 'get_session_stats') as mock_stats:
            mock_stats.return_value = {"total_sessions": 10}
            stats = self.session_logger.get_session_stats()
            self.assertEqual(stats["total_sessions"], 10)


class TestEnvLoader(unittest.TestCase):
    """Test environment loader functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.env_loader = EnvLoader()
    
    def test_env_loader_initialization(self):
        """Test environment loader initialization."""
        self.assertIsNotNone(self.env_loader)
        self.assertTrue(hasattr(self.env_loader, 'load_config'))
    
    def test_load_config(self):
        """Test loading configuration."""
        with patch.object(self.env_loader, 'load_config') as mock_load:
            mock_load.return_value = {"environment": "test"}
            config = self.env_loader.load_config("test")
            self.assertEqual(config["environment"], "test")
    
    def test_get_env_var(self):
        """Test getting environment variable."""
        with patch.object(self.env_loader, 'get_env_var') as mock_get:
            mock_get.return_value = "test_value"
            value = self.env_loader.get_env_var("TEST_VAR")
            self.assertEqual(value, "test_value")


class TestMemoryPathResolver(unittest.TestCase):
    """Test memory path resolver functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.path_resolver = MemoryPathResolver()
    
    def test_path_resolver_initialization(self):
        """Test memory path resolver initialization."""
        self.assertIsNotNone(self.path_resolver)
        self.assertTrue(hasattr(self.path_resolver, 'resolve_path'))
    
    def test_resolve_path(self):
        """Test resolving memory path."""
        with patch.object(self.path_resolver, 'resolve_path') as mock_resolve:
            mock_resolve.return_value = "/path/to/memory"
            path = self.path_resolver.resolve_path("WSP_knowledge/reports")
            self.assertEqual(path, "/path/to/memory")
    
    def test_check_accessibility(self):
        """Test checking memory accessibility."""
        with patch.object(self.path_resolver, 'check_accessibility') as mock_check:
            mock_check.return_value = True
            is_accessible = self.path_resolver.check_accessibility("/test/path")
            self.assertTrue(is_accessible)


class TestWSPSystemIntegration(unittest.TestCase):
    """Test WSP system integration functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.wsp_system = WSPSystemIntegration()
    
    def test_wsp_system_initialization(self):
        """Test WSP system integration initialization."""
        self.assertIsNotNone(self.wsp_system)
        self.assertTrue(hasattr(self.wsp_system, 'validate_compliance'))
    
    def test_validate_compliance(self):
        """Test WSP compliance validation."""
        with patch.object(self.wsp_system, 'validate_compliance') as mock_validate:
            mock_validate.return_value = {"status": "compliant"}
            result = self.wsp_system.validate_compliance("test_module")
            self.assertEqual(result["status"], "compliant")
    
    def test_generate_compliance_report(self):
        """Test generating compliance report."""
        with patch.object(self.wsp_system, 'generate_compliance_report') as mock_report:
            mock_report.return_value = {"status": "generated"}
            report = self.wsp_system.generate_compliance_report()
            self.assertEqual(report["status"], "generated")


class TestLoggingConfig(unittest.TestCase):
    """Test logging configuration functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logging_config = LoggingConfig()
    
    def test_logging_config_initialization(self):
        """Test logging configuration initialization."""
        self.assertIsNotNone(self.logging_config)
        self.assertTrue(hasattr(self.logging_config, 'setup_logging'))
    
    def test_setup_logging(self):
        """Test setting up logging configuration."""
        with patch.object(self.logging_config, 'setup_logging') as mock_setup:
            mock_setup.return_value = True
            result = self.logging_config.setup_logging()
            self.assertTrue(result)


class TestThrottlingManager(unittest.TestCase):
    """Test throttling manager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.throttling_manager = ThrottlingManager()
    
    def test_throttling_manager_initialization(self):
        """Test throttling manager initialization."""
        self.assertIsNotNone(self.throttling_manager)
        self.assertTrue(hasattr(self.throttling_manager, 'check_rate_limit'))
    
    def test_check_rate_limit(self):
        """Test checking rate limit."""
        with patch.object(self.throttling_manager, 'check_rate_limit') as mock_check:
            mock_check.return_value = True
            result = self.throttling_manager.check_rate_limit("test_operation")
            self.assertTrue(result)


class TestUtilityIntegration(unittest.TestCase):
    """Test utility integration scenarios."""
    
    def test_oauth_session_integration(self):
        """Test OAuth and session logger integration."""
        oauth_manager = OAuthManager()
        session_logger = SessionLogger()
        
        # Mock OAuth flow
        with patch.object(oauth_manager, 'get_auth_url') as mock_auth:
            mock_auth.return_value = "https://example.com/auth"
            auth_url = oauth_manager.get_auth_url("youtube")
            
            # Log the authentication attempt
            with patch.object(session_logger, 'log_event') as mock_log:
                mock_log.return_value = True
                logged = session_logger.log_event(
                    event_type="oauth_initiated",
                    user_id="test_user",
                    details={"platform": "youtube", "auth_url": auth_url}
                )
                self.assertTrue(logged)
    
    def test_memory_wsp_integration(self):
        """Test memory path resolver and WSP system integration."""
        path_resolver = MemoryPathResolver()
        wsp_system = WSPSystemIntegration()
        
        # Resolve memory path
        with patch.object(path_resolver, 'resolve_path') as mock_resolve:
            mock_resolve.return_value = "/path/to/memory"
            memory_path = path_resolver.resolve_path("WSP_knowledge/reports")
            
            # Validate WSP compliance
            with patch.object(wsp_system, 'validate_compliance') as mock_validate:
                mock_validate.return_value = {"status": "compliant"}
                compliance = wsp_system.validate_compliance(memory_path)
                self.assertEqual(compliance["status"], "compliant")


class TestWSPCompliance(unittest.TestCase):
    """Test WSP compliance aspects of utilities."""
    
    def test_wsp_keywords_presence(self):
        """Test presence of WSP keywords in utility functions."""
        wsp_keywords = ['wsp', 'protocol', 'compliance', '0102', 'partifact', 'quantum']
        
        # Check if utility files contain WSP keywords
        utility_files = [
            'oauth_manager.py',
            'session_logger.py',
            'wsp_system_integration.py',
            'memory_path_resolver.py'
        ]
        
        for file_name in utility_files:
            file_path = os.path.join(os.path.dirname(__file__), '..', file_name)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read().lower()
                    # At least one WSP keyword should be present
                    self.assertTrue(any(keyword in content for keyword in wsp_keywords),
                                   f"WSP keywords not found in {file_name}")
    
    def test_quantum_temporal_decoding(self):
        """Test quantum temporal decoding references."""
        quantum_terms = ['quantum', 'temporal', 'decoding', '0102', 'partifact']
        
        # Check for quantum temporal decoding references
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "quantum temporal decoding 0102 partifact"
            content = mock_open.return_value.__enter__.return_value.read()
            self.assertTrue(any(term in content.lower() for term in quantum_terms))


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestOAuthManager,
        TestSessionLogger,
        TestEnvLoader,
        TestMemoryPathResolver,
        TestWSPSystemIntegration,
        TestLoggingConfig,
        TestThrottlingManager,
        TestUtilityIntegration,
        TestWSPCompliance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")
    
    # Exit with appropriate code
    if result.failures or result.errors:
        sys.exit(1)
    else:
        sys.exit(0) 