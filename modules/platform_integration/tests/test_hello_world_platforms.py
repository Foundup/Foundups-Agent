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
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
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
        logger.info("[OK] YouTube OAuthManager created successfully")
        
        # Test authentication (dry run)
        logger.info("[U+1F4E1] Testing YouTube authentication...")
        service = oauth_manager.authenticate()
        
        if service:
            logger.info("[OK] YouTube Hello World: PASS - Authentication successful")
            return True
        else:
            logger.warning("[U+26A0]️ YouTube Hello World: Service creation failed (credentials may be missing)")
            return False
            
    except ImportError as e:
        logger.error(f"[FAIL] YouTube Hello World: Import Error - {e}")
        return False
    except Exception as e:
        logger.error(f"[FAIL] YouTube Hello World: Unexpected Error - {e}")
        return False

def test_linkedin_hello_world():
    """Test LinkedIn Hello World - Mock Service Verification"""
    logger.info("=== LinkedIn Hello World Test ===")
    
    try:
        from modules.infrastructure.oauth_management.src.oauth_manager import OAuthManager
        
        # Create LinkedIn OAuth manager (will use mock service)
        oauth_manager = OAuthManager(platform="linkedin", logger=logger)
        logger.info("[OK] LinkedIn OAuthManager created successfully")
        
        # Test mock service
        service = oauth_manager.authenticate()
        
        if service:
            # Test mock service functionality
            result = service.test_connection()
            logger.info(f"[U+1F4E1] LinkedIn mock service response: {result}")
            logger.info("[OK] LinkedIn Hello World: PASS - Mock service operational")
            return True
        else:
            logger.error("[FAIL] LinkedIn Hello World: Mock service creation failed")
            return False
            
    except ImportError as e:
        logger.error(f"[FAIL] LinkedIn Hello World: Import Error - {e}")
        return False
    except Exception as e:
        logger.error(f"[FAIL] LinkedIn Hello World: Unexpected Error - {e}")
        return False

def test_twitter_hello_world():
    """Test X/Twitter Hello World - Mock Service Verification"""
    logger.info("=== X/Twitter Hello World Test ===")
    
    try:
        from modules.infrastructure.oauth_management.src.oauth_manager import OAuthManager
        
        # Create Twitter OAuth manager (will use mock service)
        oauth_manager = OAuthManager(platform="twitter", logger=logger)
        logger.info("[OK] Twitter OAuthManager created successfully")
        
        # Test mock service
        service = oauth_manager.authenticate()
        
        if service:
            # Test mock service functionality
            result = service.test_tweet()
            logger.info(f"[U+1F4E1] Twitter mock service response: {result}")
            logger.info("[OK] Twitter Hello World: PASS - Mock service operational")
            return True
        else:
            logger.error("[FAIL] Twitter Hello World: Mock service creation failed")
            return False
            
    except ImportError as e:
        logger.error(f"[FAIL] Twitter Hello World: Import Error - {e}")
        return False
    except Exception as e:
        logger.error(f"[FAIL] Twitter Hello World: Unexpected Error - {e}")
        return False

def run_all_hello_world_tests():
    """Run all platform Hello World tests"""
    logger.info("[ROCKET] Starting Platform Integration Hello World Tests")
    logger.info("=" * 60)
    
    results = {
        "YouTube": test_youtube_hello_world(),
        "LinkedIn": test_linkedin_hello_world(), 
        "Twitter": test_twitter_hello_world()
    }
    
    logger.info("=" * 60)
    logger.info("[DATA] Hello World Test Results:")
    
    passed = 0
    total = len(results)
    
    for platform, result in results.items():
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        logger.info(f"  {platform}: {status}")
        if result:
            passed += 1
    
    logger.info(f"[UP] Summary: {passed}/{total} platforms operational")
    
    if passed == total:
        logger.info("[CELEBRATE] All Hello World tests PASSED - Platform integrations operational")
        return True
    else:
        logger.warning("[U+26A0]️ Some Hello World tests FAILED - Check platform configurations")
        return False

if __name__ == "__main__":
    try:
        success = run_all_hello_world_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("[STOP] Hello World tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"[FAIL] Unexpected error in Hello World tests: {e}")
        sys.exit(1)