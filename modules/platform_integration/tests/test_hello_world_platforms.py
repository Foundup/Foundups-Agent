#!/usr/bin/env python3
"""
Platform Integration Hello World Tests
WSP Compliance: Tests located in proper module structure

Tests basic "Hello World" functionality for:
1. YouTube - Authentication and basic API access
2. LinkedIn - Mock service verification
3. X/Twitter - Mock service verification

These tests prove the platform integrations are operational at a basic level.
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import sys
import logging
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_youtube_hello_world():
    """Test YouTube Hello World - Basic Authentication"""
    logger.info("=== YouTube Hello World Test ===")
    
    try:
        from modules.infrastructure.oauth_management.src.oauth_manager import OAuthManager
        
        # Create YouTube OAuth manager
        oauth_manager = OAuthManager(platform="youtube", logger=logger)
        logger.info("✅ YouTube OAuthManager created successfully")
        
        # Test authentication (dry run)
        logger.info("📡 Testing YouTube authentication...")
        service = oauth_manager.authenticate()
        
        if service:
            logger.info("✅ YouTube Hello World: PASS - Authentication successful")
            return True
        else:
            logger.warning("⚠️ YouTube Hello World: Service creation failed (credentials may be missing)")
            return False
            
    except ImportError as e:
        logger.error(f"❌ YouTube Hello World: Import Error - {e}")
        return False
    except Exception as e:
        logger.error(f"❌ YouTube Hello World: Unexpected Error - {e}")
        return False

def test_linkedin_hello_world():
    """Test LinkedIn Hello World - Mock Service Verification"""
    logger.info("=== LinkedIn Hello World Test ===")
    
    try:
        from modules.infrastructure.oauth_management.src.oauth_manager import OAuthManager
        
        # Create LinkedIn OAuth manager (will use mock service)
        oauth_manager = OAuthManager(platform="linkedin", logger=logger)
        logger.info("✅ LinkedIn OAuthManager created successfully")
        
        # Test mock service
        service = oauth_manager.authenticate()
        
        if service:
            # Test mock service functionality
            result = service.test_connection()
            logger.info(f"📡 LinkedIn mock service response: {result}")
            logger.info("✅ LinkedIn Hello World: PASS - Mock service operational")
            return True
        else:
            logger.error("❌ LinkedIn Hello World: Mock service creation failed")
            return False
            
    except ImportError as e:
        logger.error(f"❌ LinkedIn Hello World: Import Error - {e}")
        return False
    except Exception as e:
        logger.error(f"❌ LinkedIn Hello World: Unexpected Error - {e}")
        return False

def test_twitter_hello_world():
    """Test X/Twitter Hello World - Mock Service Verification"""
    logger.info("=== X/Twitter Hello World Test ===")
    
    try:
        from modules.infrastructure.oauth_management.src.oauth_manager import OAuthManager
        
        # Create Twitter OAuth manager (will use mock service)
        oauth_manager = OAuthManager(platform="twitter", logger=logger)
        logger.info("✅ Twitter OAuthManager created successfully")
        
        # Test mock service
        service = oauth_manager.authenticate()
        
        if service:
            # Test mock service functionality
            result = service.test_tweet()
            logger.info(f"📡 Twitter mock service response: {result}")
            logger.info("✅ Twitter Hello World: PASS - Mock service operational")
            return True
        else:
            logger.error("❌ Twitter Hello World: Mock service creation failed")
            return False
            
    except ImportError as e:
        logger.error(f"❌ Twitter Hello World: Import Error - {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Twitter Hello World: Unexpected Error - {e}")
        return False

def run_all_hello_world_tests():
    """Run all platform Hello World tests"""
    logger.info("🚀 Starting Platform Integration Hello World Tests")
    logger.info("=" * 60)
    
    results = {
        "YouTube": test_youtube_hello_world(),
        "LinkedIn": test_linkedin_hello_world(), 
        "Twitter": test_twitter_hello_world()
    }
    
    logger.info("=" * 60)
    logger.info("📊 Hello World Test Results:")
    
    passed = 0
    total = len(results)
    
    for platform, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {platform}: {status}")
        if result:
            passed += 1
    
    logger.info(f"📈 Summary: {passed}/{total} platforms operational")
    
    if passed == total:
        logger.info("🎉 All Hello World tests PASSED - Platform integrations operational")
        return True
    else:
        logger.warning("⚠️ Some Hello World tests FAILED - Check platform configurations")
        return False

if __name__ == "__main__":
    try:
        success = run_all_hello_world_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("🛑 Hello World tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error in Hello World tests: {e}")
        sys.exit(1)