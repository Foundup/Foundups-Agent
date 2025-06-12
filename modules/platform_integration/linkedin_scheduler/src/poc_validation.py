"""
LinkedIn Scheduler POC Validation
Test script to validate proof of concept functionality
"""

import sys
import logging
from datetime import datetime, timedelta
from linkedin_scheduler import LinkedInScheduler, PostQueue

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def validate_scheduler_initialization():
    """Test LinkedInScheduler initialization"""
    logger.info("=== Testing LinkedInScheduler Initialization ===")
    
    try:
        # Test empty initialization
        scheduler = LinkedInScheduler()
        assert scheduler.profiles == []
        assert not scheduler.authenticated
        logger.info("✅ Empty initialization successful")
        
        # Test initialization with profiles
        test_profiles = ['profile1', 'profile2']
        scheduler = LinkedInScheduler(profiles=test_profiles)
        assert scheduler.profiles == test_profiles
        logger.info("✅ Profile initialization successful")
        
        return True
    except Exception as e:
        logger.error(f"❌ Initialization test failed: {e}")
        return False


def validate_authentication():
    """Test authentication functionality"""
    logger.info("=== Testing Authentication ===")
    
    try:
        scheduler = LinkedInScheduler()
        
        # Test authentication
        result = scheduler.authenticate_profile('test_profile')
        assert result is True
        assert scheduler.authenticated is True
        logger.info("✅ Authentication test successful")
        
        return True
    except Exception as e:
        logger.error(f"❌ Authentication test failed: {e}")
        return False


def validate_post_scheduling():
    """Test post scheduling functionality"""
    logger.info("=== Testing Post Scheduling ===")
    
    try:
        scheduler = LinkedInScheduler(profiles=['profile1'])
        scheduler.authenticate_profile('profile1')
        
        # Test valid post scheduling
        future_time = datetime.now() + timedelta(hours=1)
        result = scheduler.schedule_post(
            content="Test post content",
            target_time=future_time,
            profiles=['profile1']
        )
        
        assert result['success'] is True
        assert result['scheduled_posts'] == 1
        logger.info("✅ Valid post scheduling successful")
        
        # Test scheduling without authentication
        scheduler.authenticated = False
        result = scheduler.schedule_post(
            content="Test content",
            target_time=future_time
        )
        assert result['success'] is False
        assert 'Not authenticated' in result['error']
        logger.info("✅ Authentication check successful")
        
        # Test scheduling in the past
        scheduler.authenticated = True
        past_time = datetime.now() - timedelta(hours=1)
        result = scheduler.schedule_post(
            content="Test content",
            target_time=past_time
        )
        assert result['success'] is False
        assert 'past' in result['error']
        logger.info("✅ Past scheduling validation successful")
        
        # Test content length validation
        long_content = "A" * 3001  # Exceeds LinkedIn limit
        result = scheduler.schedule_post(
            content=long_content,
            target_time=future_time
        )
        assert result['success'] is False
        assert 'character limit' in result['error']
        logger.info("✅ Content length validation successful")
        
        return True
    except Exception as e:
        logger.error(f"❌ Post scheduling test failed: {e}")
        return False


def validate_connection():
    """Test connection validation"""
    logger.info("=== Testing Connection Validation ===")
    
    try:
        scheduler = LinkedInScheduler()
        result = scheduler.validate_connection()
        assert result is True
        logger.info("✅ Connection validation successful")
        
        return True
    except Exception as e:
        logger.error(f"❌ Connection validation test failed: {e}")
        return False


def validate_post_queue():
    """Test PostQueue functionality"""
    logger.info("=== Testing PostQueue ===")
    
    try:
        queue = PostQueue()
        
        # Test adding posts
        future_time = datetime.now() + timedelta(minutes=30)
        post_id = queue.add_post(
            content="Test queue post",
            schedule_time=future_time,
            profiles=['profile1']
        )
        
        assert post_id is not None
        assert len(queue.queue) == 1
        logger.info("✅ Post addition successful")
        
        # Test getting pending posts (should be empty - future time)
        pending = queue.get_pending_posts()
        assert len(pending) == 0
        logger.info("✅ Future post filtering successful")
        
        # Test with past time
        past_time = datetime.now() - timedelta(minutes=5)
        post_id_2 = queue.add_post(
            content="Past post",
            schedule_time=past_time,
            profiles=['profile1']
        )
        
        pending = queue.get_pending_posts()
        assert len(pending) == 1
        assert pending[0]['id'] == post_id_2
        logger.info("✅ Pending post retrieval successful")
        
        # Test marking as processed
        result = queue.mark_processed(post_id_2, success=True)
        assert result is True
        assert len(queue.processed) == 1
        logger.info("✅ Post processing successful")
        
        return True
    except Exception as e:
        logger.error(f"❌ PostQueue test failed: {e}")
        return False


def run_poc_validation():
    """Run complete POC validation suite"""
    logger.info("🚀 Starting LinkedIn Scheduler POC Validation")
    logger.info("=" * 50)
    
    tests = [
        validate_scheduler_initialization,
        validate_authentication,
        validate_post_scheduling,
        validate_connection,
        validate_post_queue
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
        logger.info("")  # Empty line for readability
    
    logger.info("=" * 50)
    logger.info(f"📊 POC Validation Results:")
    logger.info(f"✅ Tests Passed: {passed}")
    logger.info(f"❌ Tests Failed: {failed}")
    logger.info(f"📈 Success Rate: {(passed/(passed+failed))*100:.1f}%")
    
    if failed == 0:
        logger.info("🎉 POC Validation SUCCESSFUL - All tests passed!")
        return True
    else:
        logger.error("⚠️  POC Validation INCOMPLETE - Some tests failed!")
        return False


if __name__ == "__main__":
    success = run_poc_validation()
    sys.exit(0 if success else 1)
