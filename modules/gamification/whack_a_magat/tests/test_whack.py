import pytest
import sys
import os
from datetime import datetime, timedelta

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.whack import ProfilesRepo, ActionsRepo, apply_whack, get_profile


def setup_function():
    """Reset state before each test"""
    # Clear any existing test data
    pass  # Tests will create their own instances


def test_apply_whack_basic():
    """Test basic whack functionality"""
    now = datetime.utcnow()
    
    # Test basic whack application
    result = apply_whack("test_mod", "test_target", 120, now)  # 2 minutes = 2 points
    
    assert result is not None
    assert hasattr(result, 'points')
    assert result.points > 0


def test_get_profile_creation():
    """Test profile creation and retrieval"""
    profile = get_profile("test_user", "TestUser")
    
    assert profile is not None
    assert profile.user_id == "test_user"
    assert profile.username in ["TestUser", "Test"]  # Username may be truncated
    assert profile.score >= 0
    assert profile.rank is not None


def test_timeout_points_scaling():
    """Test that timeout duration affects points awarded"""
    now = datetime.utcnow()
    
    # Short timeout (under 60s) should give minimal/no points
    short_result = apply_whack("mod1", "target1", 30, now)
    
    # Medium timeout (2 minutes) should give some points  
    medium_result = apply_whack("mod1", "target2", 120, now)
    
    # Long timeout (1 hour) should give more points
    long_result = apply_whack("mod1", "target3", 3600, now)
    
    # Points should scale with timeout duration
    assert short_result.points <= medium_result.points
    assert medium_result.points <= long_result.points


def test_profile_persistence():
    """Test that profiles persist across multiple operations"""
    # Create profile through first whack
    apply_whack("test_mod", "target1", 120, datetime.utcnow())
    profile1 = get_profile("test_mod", "TestMod")
    initial_score = profile1.score
    
    # Apply second whack
    apply_whack("test_mod", "target2", 180, datetime.utcnow())
    profile2 = get_profile("test_mod", "TestMod")
    
    # Score should have increased
    assert profile2.score > initial_score
    assert profile2.user_id == profile1.user_id


def test_module_imports():
    """Test that all required components can be imported"""
    from src.whack import ProfilesRepo, ActionsRepo, apply_whack, get_profile
    from src.timeout_announcer import TimeoutManager
    from src.timeout_tracker import TimeoutTracker
    
    # Basic instantiation test
    profiles_repo = ProfilesRepo()
    actions_repo = ActionsRepo()
    
    assert profiles_repo is not None
    assert actions_repo is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])