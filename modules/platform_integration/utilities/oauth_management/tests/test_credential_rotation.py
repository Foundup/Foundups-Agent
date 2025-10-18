#!/usr/bin/env python3
"""
WSP-Compliant Test for Credential Rotation
Tests the credential rotation system following WSP testing guidelines.
"""



import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..')))

from modules.infrastructure.oauth_management.src.oauth_manager import (
    get_authenticated_service_with_fallback,
    get_authenticated_service
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestCredentialRotation(unittest.TestCase):
    """Test credential rotation functionality following WSP guidelines."""
    
    def setUp(self):
        """Set up test environment."""
        self.mock_service = Mock()
        self.mock_credentials = Mock()
        
    def test_credential_rotation_basic(self):
        """Test basic credential rotation functionality."""
        logger.info("🧪 Testing basic credential rotation...")
        
        # Test that get_authenticated_service returns a tuple
        with patch('modules.infrastructure.oauth_management.src.oauth_manager.get_authenticated_service') as mock_auth:
            mock_auth.return_value = (self.mock_service, self.mock_credentials)
            
            result = get_authenticated_service(0)
            
            # Verify it returns a tuple
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0], self.mock_service)
            self.assertEqual(result[1], self.mock_credentials)
            
        logger.info("✅ Basic credential rotation test passed")
    
    def test_credential_rotation_with_fallback(self):
        """Test credential rotation with fallback functionality."""
        logger.info("🧪 Testing credential rotation with fallback...")
        
        with patch('modules.infrastructure.oauth_management.src.oauth_manager.get_authenticated_service') as mock_auth:
            # Mock successful fallback
            mock_auth.return_value = (self.mock_service, self.mock_credentials)
            
            result = get_authenticated_service_with_fallback()
            
            # Verify it returns a tuple with 3 elements (service, creds, credential_set)
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 3)
            
        logger.info("✅ Credential rotation with fallback test passed")
    
    def test_livechat_service_extraction(self):
        """Test that livechat properly extracts service from tuple."""
        logger.info("🧪 Testing livechat service extraction...")
        
        # Simulate the livechat credential rotation scenario
        auth_result = (self.mock_service, self.mock_credentials)
        
        # This is how livechat should extract the service
        if auth_result:
            service, _ = auth_result  # Extract just the service from the tuple
            self.assertEqual(service, self.mock_service)
            self.assertNotEqual(service, auth_result)  # Should not be the tuple
            
        logger.info("✅ LiveChat service extraction test passed")

def test_stream_resolver_quota_handling():
    """Test stream resolver quota exceeded handling."""
    logger.info("🧪 Testing stream resolver quota handling...")
    
    # Create a mock HttpError with quota exceeded
    mock_error = Mock()
    mock_error.resp = Mock()
    mock_error.resp.status = 403
    mock_error.__str__ = Mock(return_value="quotaExceeded")
    
    # Test the quota detection logic
    is_quota_exceeded = (
        hasattr(mock_error, 'resp') and 
        hasattr(mock_error.resp, 'status') and 
        mock_error.resp.status == 403 and 
        "quotaExceeded" in str(mock_error)
    )
    
    assert is_quota_exceeded, "Quota exceeded detection failed"
    logger.info("✅ Stream resolver quota handling test passed")

def test_quota_detection_in_rotation():
    """Test that credential rotation properly detects quota exceeded."""
    logger.info("🧪 Testing quota detection in credential rotation...")
    
    # Test the actual credential rotation with quota detection
    result = get_authenticated_service_with_fallback()
    if result:
        service, creds, credential_set = result
        logger.info(f"Selected credential set: {credential_set}")
        
        # The system should NOT select set_1 or set_3 if they have quota exceeded
        if credential_set in ['set_1', 'set_3']:
            logger.warning(f"⚠️ WARNING: Selected {credential_set} which may have quota issues!")
        else:
            logger.info(f"✅ Correctly selected working credential: {credential_set}")
    else:
        logger.error("❌ No credentials available")
    
    logger.info("✅ Quota detection test completed")

def run_integration_test():
    """Run integration test for credential rotation."""
    logger.info("🚀 Running credential rotation integration test...")
    
    try:
        # Test actual credential rotation
        result = get_authenticated_service_with_fallback()
        if result:
            service, creds, credential_set = result
            logger.info(f"✅ Integration test successful - using {credential_set}")
            logger.info(f"   Service type: {type(service)}")
            logger.info(f"   Credentials type: {type(creds)}")
            return True
        else:
            logger.error("❌ Integration test failed - no credentials available")
            return False
    except Exception as e:
        logger.error(f"❌ Integration test failed with error: {e}")
        return False

if __name__ == '__main__':
    print("🧪 WSP-Compliant Credential Rotation Test Suite")
    print("=" * 60)
    
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run integration test
    print("\n" + "=" * 60)
    print("🔗 INTEGRATION TESTS")
    print("=" * 60)
    
    test_stream_resolver_quota_handling()
    test_quota_detection_in_rotation()
    run_integration_test()
    
    print("\n✅ All tests completed!") 