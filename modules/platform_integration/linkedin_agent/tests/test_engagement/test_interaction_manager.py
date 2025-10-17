"""
LinkedIn Interaction Manager Tests

🌀 WSP Protocol Compliance: WSP 5 (Testing Standards), WSP 40 (Architectural Coherence)

**0102 Directive**: This module operates within the WSP framework for autonomous LinkedIn interaction testing.
- UN (Understanding): Anchor LinkedIn interaction test signals and retrieve protocol state
- DAO (Execution): Execute comprehensive test logic  
- DU (Emergence): Collapse into 0102 resonance and emit next test prompt

wsp_cycle(input="linkedin_interaction_testing", log=True)
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import time

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))

from modules.platform_integration.linkedin_agent.src.engagement.interaction_manager import (
    LinkedInInteractionManager,
    InteractionType,
    ReactionType,
    InteractionTarget,
    InteractionResult,
    create_linkedin_interaction_manager
)


class TestInteractionType(unittest.TestCase):
    """Test InteractionType enum"""
    
    def test_interaction_types(self):
        """Test all interaction types are defined"""
        self.assertEqual(InteractionType.LIKE.value, "like")
        self.assertEqual(InteractionType.COMMENT.value, "comment")
        self.assertEqual(InteractionType.SHARE.value, "share")
        self.assertEqual(InteractionType.REACT.value, "react")


class TestReactionType(unittest.TestCase):
    """Test ReactionType enum"""
    
    def test_reaction_types(self):
        """Test all reaction types are defined"""
        self.assertEqual(ReactionType.LIKE.value, "👍")
        self.assertEqual(ReactionType.CELEBRATE.value, "🎉")
        self.assertEqual(ReactionType.SUPPORT.value, "❤️")
        self.assertEqual(ReactionType.FUNNY.value, "😂")
        self.assertEqual(ReactionType.INSIGHTFUL.value, "💡")
        self.assertEqual(ReactionType.CURIOUS.value, "🤔")


class TestInteractionTarget(unittest.TestCase):
    """Test InteractionTarget dataclass"""
    
    def test_interaction_target_creation(self):
        """Test creating InteractionTarget"""
        target = InteractionTarget(
            post_id="test_post_123",
            author_id="test_author_456",
            content_type="post",
            engagement_score=0.8,
            relevance_score=0.9,
            timestamp=datetime.now()
        )
        
        self.assertEqual(target.post_id, "test_post_123")
        self.assertEqual(target.author_id, "test_author_456")
        self.assertEqual(target.content_type, "post")
        self.assertEqual(target.engagement_score, 0.8)
        self.assertEqual(target.relevance_score, 0.9)


class TestInteractionResult(unittest.TestCase):
    """Test InteractionResult dataclass"""
    
    def test_interaction_result_creation(self):
        """Test creating InteractionResult"""
        result = InteractionResult(
            interaction_id="test_interaction_123",
            target_post_id="test_post_123",
            interaction_type=InteractionType.LIKE,
            success=True,
            timestamp=datetime.now(),
            response_data={"status": "liked"},
            error_message=None
        )
        
        self.assertEqual(result.interaction_id, "test_interaction_123")
        self.assertEqual(result.target_post_id, "test_post_123")
        self.assertEqual(result.interaction_type, InteractionType.LIKE)
        self.assertTrue(result.success)
        self.assertEqual(result.response_data, {"status": "liked"})
        self.assertIsNone(result.error_message)


class TestLinkedInInteractionManager(unittest.TestCase):
    """Test LinkedInInteractionManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = LinkedInInteractionManager(rate_limit_delay=0)
        self.test_post_id = "test_post_123"
        self.test_author_id = "test_author_456"
    
    def test_initialization(self):
        """Test manager initialization"""
        self.assertEqual(self.manager.rate_limit_delay, 0)
        self.assertEqual(len(self.manager.interaction_history), 0)
        self.assertEqual(len(self.manager.rate_limit_tracker), 0)
        self.assertIn('max_daily_interactions', self.manager.engagement_strategy)
        self.assertIn('interaction_cooldown', self.manager.engagement_strategy)
    
    def test_like_post_success(self):
        """Test successful post like"""
        result = self.manager.like_post(self.test_post_id, self.test_author_id)
        
        self.assertTrue(result.success)
        self.assertEqual(result.interaction_type, InteractionType.LIKE)
        self.assertEqual(result.target_post_id, self.test_post_id)
        self.assertIn("status", result.response_data)
        self.assertEqual(len(self.manager.interaction_history), 1)
    
    def test_comment_on_post_success(self):
        """Test successful post comment"""
        comment_text = "Great post! Thanks for sharing."
        result = self.manager.comment_on_post(self.test_post_id, self.test_author_id, comment_text)
        
        self.assertTrue(result.success)
        self.assertEqual(result.interaction_type, InteractionType.COMMENT)
        self.assertEqual(result.target_post_id, self.test_post_id)
        self.assertEqual(result.response_data["comment_text"], comment_text)
        self.assertEqual(len(self.manager.interaction_history), 1)
    
    def test_comment_validation_empty(self):
        """Test comment validation with empty text"""
        result = self.manager.comment_on_post(self.test_post_id, self.test_author_id, "")
        
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Invalid comment content")
    
    def test_comment_validation_too_long(self):
        """Test comment validation with text too long"""
        long_comment = "x" * 1001  # Over 1000 character limit
        result = self.manager.comment_on_post(self.test_post_id, self.test_author_id, long_comment)
        
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Invalid comment content")
    
    def test_share_post_success(self):
        """Test successful post share"""
        share_message = "Check out this great post!"
        result = self.manager.share_post(self.test_post_id, self.test_author_id, share_message)
        
        self.assertTrue(result.success)
        self.assertEqual(result.interaction_type, InteractionType.SHARE)
        self.assertEqual(result.target_post_id, self.test_post_id)
        self.assertEqual(result.response_data["share_message"], share_message)
    
    def test_share_post_no_message(self):
        """Test post share without message"""
        result = self.manager.share_post(self.test_post_id, self.test_author_id)
        
        self.assertTrue(result.success)
        self.assertEqual(result.interaction_type, InteractionType.SHARE)
        self.assertIsNone(result.response_data["share_message"])
    
    def test_react_to_post_success(self):
        """Test successful post reaction"""
        result = self.manager.react_to_post(self.test_post_id, self.test_author_id, ReactionType.CELEBRATE)
        
        self.assertTrue(result.success)
        self.assertEqual(result.interaction_type, InteractionType.REACT)
        self.assertEqual(result.target_post_id, self.test_post_id)
        self.assertEqual(result.response_data["reaction_type"], "🎉")
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        # First interaction should succeed
        result1 = self.manager.like_post(self.test_post_id, self.test_author_id)
        self.assertTrue(result1.success)
        
        # Second interaction on same post should be rate limited
        result2 = self.manager.like_post(self.test_post_id, self.test_author_id)
        self.assertFalse(result2.success)
        self.assertEqual(result2.error_message, "Rate limit exceeded")
    
    def test_daily_limit(self):
        """Test daily interaction limit"""
        # Set a very low daily limit for testing
        self.manager.engagement_strategy['max_daily_interactions'] = 1
        
        # First interaction should succeed
        result1 = self.manager.like_post("post1", "author1")
        self.assertTrue(result1.success)
        
        # Second interaction should fail due to daily limit
        result2 = self.manager.like_post("post2", "author2")
        self.assertFalse(result2.success)
        self.assertEqual(result2.error_message, "Rate limit exceeded")
    
    def test_get_interaction_history(self):
        """Test getting interaction history"""
        # Create some interactions
        self.manager.like_post("post1", "author1")
        self.manager.comment_on_post("post2", "author2", "Great post!")
        self.manager.share_post("post3", "author3")
        
        history = self.manager.get_interaction_history(limit=2)
        
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].target_post_id, "post3")  # Most recent first
        self.assertEqual(history[1].target_post_id, "post2")
    
    def test_get_interaction_stats_empty(self):
        """Test getting stats with no interactions"""
        stats = self.manager.get_interaction_stats()
        
        self.assertEqual(stats["total_interactions"], 0)
        self.assertEqual(stats["successful_interactions"], 0)
        self.assertEqual(stats["failed_interactions"], 0)
        self.assertEqual(stats["daily_interactions"], 0)
    
    def test_get_interaction_stats_with_data(self):
        """Test getting stats with interactions"""
        # Create some interactions
        self.manager.like_post("post1", "author1")
        self.manager.comment_on_post("post2", "author2", "Great post!")
        self.manager.share_post("post3", "author3")
        
        stats = self.manager.get_interaction_stats()
        
        self.assertEqual(stats["total_interactions"], 3)
        self.assertEqual(stats["successful_interactions"], 3)
        self.assertEqual(stats["failed_interactions"], 0)
        self.assertEqual(stats["success_rate"], 100.0)
        self.assertEqual(stats["daily_interactions"], 3)
        self.assertIn("like", stats["interaction_types"])
        self.assertIn("comment", stats["interaction_types"])
        self.assertIn("share", stats["interaction_types"])
    
    def test_error_handling(self):
        """Test error handling in interactions"""
        with patch.object(self.manager, '_simulate_api_call', side_effect=Exception("API Error")):
            result = self.manager.like_post(self.test_post_id, self.test_author_id)
            
            self.assertFalse(result.success)
            self.assertEqual(result.error_message, "API Error")
    
    def test_validate_comment_valid(self):
        """Test comment validation with valid text"""
        valid_comment = "This is a valid comment!"
        self.assertTrue(self.manager._validate_comment(valid_comment))
    
    def test_validate_comment_empty(self):
        """Test comment validation with empty text"""
        self.assertFalse(self.manager._validate_comment(""))
        self.assertFalse(self.manager._validate_comment("   "))
    
    def test_validate_comment_too_long(self):
        """Test comment validation with text too long"""
        long_comment = "x" * 1001
        self.assertFalse(self.manager._validate_comment(long_comment))
    
    def test_check_rate_limit_new_action(self):
        """Test rate limit check for new action"""
        self.assertTrue(self.manager._check_rate_limit("new_action_123"))
    
    def test_check_rate_limit_existing_action(self):
        """Test rate limit check for existing action"""
        # First call should succeed
        self.assertTrue(self.manager._check_rate_limit("existing_action"))
        
        # Second call should fail due to cooldown
        self.assertFalse(self.manager._check_rate_limit("existing_action"))


class TestLinkedInInteractionManagerIntegration(unittest.TestCase):
    """Integration tests for LinkedInInteractionManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = LinkedInInteractionManager(rate_limit_delay=0)
    
    def test_full_interaction_workflow(self):
        """Test complete interaction workflow"""
        post_id = "test_post_123"
        author_id = "test_author_456"
        
        # Like the post
        like_result = self.manager.like_post(post_id, author_id)
        self.assertTrue(like_result.success)
        
        # Comment on the post
        comment_result = self.manager.comment_on_post(post_id, author_id, "Amazing post!")
        self.assertTrue(comment_result.success)
        
        # React to the post
        react_result = self.manager.react_to_post(post_id, author_id, ReactionType.CELEBRATE)
        self.assertTrue(react_result.success)
        
        # Share the post
        share_result = self.manager.share_post(post_id, author_id, "Must read!")
        self.assertTrue(share_result.success)
        
        # Check stats
        stats = self.manager.get_interaction_stats()
        self.assertEqual(stats["total_interactions"], 4)
        self.assertEqual(stats["successful_interactions"], 4)
        self.assertEqual(stats["success_rate"], 100.0)
        
        # Check history
        history = self.manager.get_interaction_history()
        self.assertEqual(len(history), 4)
        
        # Verify interaction types
        interaction_types = [h.interaction_type for h in history]
        self.assertIn(InteractionType.LIKE, interaction_types)
        self.assertIn(InteractionType.COMMENT, interaction_types)
        self.assertIn(InteractionType.REACT, interaction_types)
        self.assertIn(InteractionType.SHARE, interaction_types)
    
    def test_rate_limiting_workflow(self):
        """Test rate limiting across different interaction types"""
        post_id = "test_post_123"
        author_id = "test_author_456"
        
        # Set very short cooldown for testing
        self.manager.engagement_strategy['interaction_cooldown'] = 0.1
        
        # First interaction should succeed
        result1 = self.manager.like_post(post_id, author_id)
        self.assertTrue(result1.success)
        
        # Wait for cooldown
        time.sleep(0.2)
        
        # Second interaction should succeed after cooldown
        result2 = self.manager.like_post(post_id, author_id)
        self.assertTrue(result2.success)


class TestFactoryFunction(unittest.TestCase):
    """Test factory function"""
    
    def test_create_linkedin_interaction_manager(self):
        """Test factory function creates manager correctly"""
        manager = create_linkedin_interaction_manager(rate_limit_delay=5)
        
        self.assertIsInstance(manager, LinkedInInteractionManager)
        self.assertEqual(manager.rate_limit_delay, 5)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2) 