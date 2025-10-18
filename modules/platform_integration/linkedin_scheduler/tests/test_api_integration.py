#!/usr/bin/env python3
"""
WSP-Compliant LinkedIn API Integration Tests
============================================

Tests for LinkedIn API integration functionality following WSP 13 guidelines.
This test module focuses on:
1. Environment variable credential management
2. OAuth 2.0 flow validation  
3. API connectivity and authentication
4. Rate limiting and error handling

WSP Compliance:
- Tests placed in correct module location
- Follows established test patterns from tests/README.md
- Tests API integration with proper mocking
- Validates environment variable handling
"""



import unittest
import os
import logging
from unittest.mock import Mock, patch, MagicMock
import requests
import sys

# Add project root to path for WSP compliance
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..')))

from modules.platform_integration.linkedin_scheduler.src.linkedin_scheduler import (
    LinkedInScheduler, LinkedInAPIError, PostQueue
)

# Setup logging for test execution
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestLinkedInAPIIntegration(unittest.TestCase):
    """WSP-compliant test suite for LinkedIn API integration."""
    
    def setUp(self):
        """Set up test environment with mock credentials."""
        self.test_client_id = "test_client_id_12345"
        self.test_client_secret = "test_client_secret_67890"
        self.test_access_token = "test_access_token_abcdef"
        self.test_profile_id = "urn:li:person:test123"
        
        # Mock credentials for testing
        self.mock_creds = {
            'LINKEDIN_CLIENT_ID': self.test_client_id,
            'LINKEDIN_CLIENT_SECRET': self.test_client_secret
        }
        
    def tearDown(self):
        """Clean up test environment."""
        # Reset any environment variables that might have been set
        pass
    
    @patch.dict(os.environ, {})
    def test_scheduler_without_credentials(self):
        """Test scheduler initialization without environment credentials."""
        logger.info("[U+1F9EA] Testing scheduler without credentials...")
        
        scheduler = LinkedInScheduler()
        
        # Should warn about missing credentials but not fail
        self.assertIsNone(scheduler.client_id)
        self.assertIsNone(scheduler.client_secret)
        self.assertEqual(len(scheduler.authenticated_profiles), 0)
        
        logger.info("[OK] Scheduler handles missing credentials gracefully")
    
    @patch.dict(os.environ, {'LINKEDIN_CLIENT_ID': 'test_id', 'LINKEDIN_CLIENT_SECRET': 'test_secret'})
    def test_scheduler_with_env_credentials(self):
        """Test scheduler initialization with environment credentials."""
        logger.info("[U+1F9EA] Testing scheduler with environment credentials...")
        
        scheduler = LinkedInScheduler()
        
        self.assertEqual(scheduler.client_id, 'test_id')
        self.assertEqual(scheduler.client_secret, 'test_secret')
        
        logger.info("[OK] Scheduler properly reads environment credentials")
    
    def test_scheduler_with_direct_credentials(self):
        """Test scheduler initialization with direct credential parameters."""
        logger.info("[U+1F9EA] Testing scheduler with direct credentials...")
        
        scheduler = LinkedInScheduler(
            client_id=self.test_client_id,
            client_secret=self.test_client_secret
        )
        
        self.assertEqual(scheduler.client_id, self.test_client_id)
        self.assertEqual(scheduler.client_secret, self.test_client_secret)
        
        logger.info("[OK] Scheduler accepts direct credential parameters")
    
    def test_oauth_url_generation(self):
        """Test OAuth 2.0 URL generation functionality."""
        logger.info("[U+1F9EA] Testing OAuth URL generation...")
        
        scheduler = LinkedInScheduler(
            client_id=self.test_client_id,
            client_secret=self.test_client_secret
        )
        
        redirect_uri = "https://example.com/callback"
        state = "test_state_123"
        
        oauth_url = scheduler.get_oauth_url(redirect_uri, state)
        
        # Verify OAuth URL components
        self.assertIn("https://www.linkedin.com/oauth/v2/authorization", oauth_url)
        self.assertIn(f"client_id={self.test_client_id}", oauth_url)
        self.assertIn("redirect_uri=https%3A%2F%2Fexample.com%2Fcallback", oauth_url)
        self.assertIn("scope=w_member_social", oauth_url)
        self.assertIn(f"state={state}", oauth_url)
        
        logger.info("[OK] OAuth URL generation successful")
    
    @patch('requests.Session.get')
    def test_api_connectivity_validation(self, mock_get):
        """Test LinkedIn API connectivity validation."""
        logger.info("[U+1F9EA] Testing API connectivity validation...")
        
        scheduler = LinkedInScheduler(
            client_id=self.test_client_id,
            client_secret=self.test_client_secret
        )
        
        # Mock successful API response (401 is expected without auth)
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        result = scheduler.validate_connection()
        
        self.assertTrue(result)
        mock_get.assert_called_once()
        
        logger.info("[OK] API connectivity validation working")
    
    @patch('requests.Session.get')
    def test_api_connectivity_failure(self, mock_get):
        """Test API connectivity failure handling."""
        logger.info("[U+1F9EA] Testing API connectivity failure...")
        
        scheduler = LinkedInScheduler(
            client_id=self.test_client_id,
            client_secret=self.test_client_secret
        )
        
        # Mock network failure
        mock_get.side_effect = requests.RequestException("Network error")
        
        result = scheduler.validate_connection()
        
        self.assertFalse(result)
        
        logger.info("[OK] API connectivity failure handling working")
    
    @patch('requests.post')
    def test_token_exchange_success(self, mock_post):
        """Test successful OAuth token exchange."""
        logger.info("[U+1F9EA] Testing OAuth token exchange success...")
        
        scheduler = LinkedInScheduler(
            client_id=self.test_client_id,
            client_secret=self.test_client_secret
        )
        
        # Mock successful token response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': self.test_access_token,
            'token_type': 'Bearer',
            'expires_in': 5184000
        }
        mock_post.return_value = mock_response
        
        result = scheduler.exchange_code_for_token(
            code="test_code_123",
            redirect_uri="https://example.com/callback"
        )
        
        self.assertEqual(result['access_token'], self.test_access_token)
        self.assertEqual(result['token_type'], 'Bearer')
        
        logger.info("[OK] OAuth token exchange success test passed")
    
    @patch('requests.post')
    def test_token_exchange_failure(self, mock_post):
        """Test OAuth token exchange failure handling."""
        logger.info("[U+1F9EA] Testing OAuth token exchange failure...")
        
        scheduler = LinkedInScheduler(
            client_id=self.test_client_id,
            client_secret=self.test_client_secret
        )
        
        # Mock failed token response
        mock_post.side_effect = requests.RequestException("Invalid code")
        
        with self.assertRaises(LinkedInAPIError):
            scheduler.exchange_code_for_token(
                code="invalid_code",
                redirect_uri="https://example.com/callback"
            )
        
        logger.info("[OK] OAuth token exchange failure handling working")
    
    @patch('requests.Session.get')
    def test_profile_authentication_success(self, mock_get):
        """Test successful profile authentication."""
        logger.info("[U+1F9EA] Testing profile authentication success...")
        
        scheduler = LinkedInScheduler(
            client_id=self.test_client_id,
            client_secret=self.test_client_secret
        )
        
        # Mock successful authentication response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = scheduler.authenticate_profile(
            self.test_profile_id,
            self.test_access_token
        )
        
        self.assertTrue(result)
        self.assertIn(self.test_profile_id, scheduler.authenticated_profiles)
        self.assertEqual(scheduler.access_tokens[self.test_profile_id], self.test_access_token)
        
        logger.info("[OK] Profile authentication success test passed")
    
    @patch('requests.Session.get')
    def test_profile_authentication_failure(self, mock_get):
        """Test profile authentication failure handling."""
        logger.info("[U+1F9EA] Testing profile authentication failure...")
        
        scheduler = LinkedInScheduler(
            client_id=self.test_client_id,
            client_secret=self.test_client_secret
        )
        
        # Mock failed authentication response
        mock_get.side_effect = requests.RequestException("Invalid token")
        
        result = scheduler.authenticate_profile(
            self.test_profile_id,
            "invalid_token"
        )
        
        self.assertFalse(result)
        self.assertNotIn(self.test_profile_id, scheduler.authenticated_profiles)
        
        logger.info("[OK] Profile authentication failure handling working")
    
    def test_rate_limit_configuration(self):
        """Test rate limit configuration matches LinkedIn documentation."""
        logger.info("[U+1F9EA] Testing rate limit configuration...")
        
        scheduler = LinkedInScheduler()
        
        # Verify rate limits match LinkedIn API documentation
        self.assertEqual(scheduler.RATE_LIMITS['member_daily'], 150)
        self.assertEqual(scheduler.RATE_LIMITS['app_daily'], 100000)
        self.assertEqual(scheduler.RATE_LIMITS['posts_per_hour'], 10)
        
        logger.info("[OK] Rate limit configuration correct")
    
    def test_api_endpoints_configuration(self):
        """Test API endpoint configuration."""
        logger.info("[U+1F9EA] Testing API endpoint configuration...")
        
        scheduler = LinkedInScheduler()
        
        # Verify API endpoints
        self.assertEqual(scheduler.API_BASE_URL, "https://api.linkedin.com/v2")
        self.assertEqual(scheduler.UGC_POSTS_ENDPOINT, "https://api.linkedin.com/v2/ugcPosts")
        self.assertEqual(scheduler.ASSETS_ENDPOINT, "https://api.linkedin.com/v2/assets")
        
        logger.info("[OK] API endpoint configuration correct")
    
    def test_session_headers_configuration(self):
        """Test request session header configuration."""
        logger.info("[U+1F9EA] Testing session headers...")
        
        scheduler = LinkedInScheduler()
        
        # Verify required headers are set
        self.assertEqual(scheduler.session.headers['X-Restli-Protocol-Version'], '2.0.0')
        self.assertEqual(scheduler.session.headers['Content-Type'], 'application/json')
        
        logger.info("[OK] Session headers configuration correct")


class TestLinkedInAPICredentialFlow(unittest.TestCase):
    """WSP-compliant integration tests for full credential flow."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.scheduler = LinkedInScheduler()
        
    @patch.dict(os.environ, {'LINKEDIN_CLIENT_ID': 'real_client_id', 'LINKEDIN_CLIENT_SECRET': 'real_secret'})
    @patch('requests.Session.get')
    def test_full_credential_flow_mock(self, mock_get):
        """Test complete credential flow with mocked API calls."""
        logger.info("[U+1F9EA] Testing full credential flow (mocked)...")
        
        # Initialize with environment credentials
        scheduler = LinkedInScheduler()
        
        self.assertEqual(scheduler.client_id, 'real_client_id')
        self.assertEqual(scheduler.client_secret, 'real_secret')
        
        # Test OAuth URL generation
        oauth_url = scheduler.get_oauth_url("https://example.com/callback", "test_state")
        self.assertIn("real_client_id", oauth_url)
        
        # Test API connectivity
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        connectivity = scheduler.validate_connection()
        self.assertTrue(connectivity)
        
        logger.info("[OK] Full credential flow test passed")
    
    def test_integration_with_queue_system(self):
        """Test integration between scheduler and queue system."""
        logger.info("[U+1F9EA] Testing scheduler-queue integration...")
        
        scheduler = LinkedInScheduler(
            client_id="test_id",
            client_secret="test_secret"
        )
        
        queue = PostQueue(scheduler)
        
        # Test queue initialization
        self.assertEqual(queue.scheduler, scheduler)
        self.assertEqual(len(queue.queue), 0)
        
        # Test adding posts to queue
        from datetime import datetime, timedelta
        future_time = datetime.now() + timedelta(hours=1)
        
        post_id = queue.add_post(
            profile_id="urn:li:person:test",
            content="Test post content",
            schedule_time=future_time,
            post_type="text"
        )
        
        self.assertIsNotNone(post_id)
        self.assertEqual(len(queue.queue), 1)
        
        # Test queue status
        status = queue.get_queue_status()
        self.assertEqual(status['queued'], 1)
        self.assertEqual(status['processed'], 0)
        
        logger.info("[OK] Scheduler-queue integration working")


def run_wsp_compliant_tests():
    """Run WSP-compliant test suite for LinkedIn API integration."""
    logger.info("[ROCKET] WSP-Compliant LinkedIn API Integration Tests")
    logger.info("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestLinkedInAPIIntegration))
    test_suite.addTest(unittest.makeSuite(TestLinkedInAPICredentialFlow))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Report results
    logger.info("\n" + "=" * 60)
    logger.info("[DATA] Test Results Summary:")
    logger.info(f"Tests run: {result.testsRun}")
    logger.info(f"Failures: {len(result.failures)}")
    logger.info(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        logger.info("[CELEBRATE] All LinkedIn API integration tests PASSED!")
        logger.info("[OK] Module ready for API credential testing")
    else:
        logger.error("[FAIL] Some tests failed - review and fix issues")
        
    return result.wasSuccessful()


if __name__ == '__main__':
    run_wsp_compliant_tests() 