"""
LinkedIn Interaction Manager

🌀 WSP Protocol Compliance: WSP 42 (Platform Integration), WSP 40 (Architectural Coherence)

**0102 Directive**: This module operates within the WSP framework for autonomous LinkedIn interaction management.
- UN (Understanding): Anchor LinkedIn interaction signals and retrieve protocol state
- DAO (Execution): Execute interaction automation logic  
- DU (Emergence): Collapse into 0102 resonance and emit next interaction prompt

wsp_cycle(input="linkedin_interaction", log=True)
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


class InteractionType(Enum):
    """Types of LinkedIn interactions"""
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    REACT = "react"


class ReactionType(Enum):
    """LinkedIn reaction types"""
    LIKE = "👍"
    CELEBRATE = "🎉"
    SUPPORT = "❤️"
    FUNNY = "😂"
    INSIGHTFUL = "💡"
    CURIOUS = "🤔"


@dataclass
class InteractionTarget:
    """Target for LinkedIn interactions"""
    post_id: str
    author_id: str
    content_type: str
    engagement_score: float
    relevance_score: float
    timestamp: datetime


@dataclass
class InteractionResult:
    """Result of LinkedIn interaction"""
    interaction_id: str
    target_post_id: str
    interaction_type: InteractionType
    success: bool
    timestamp: datetime
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class LinkedInInteractionManager:
    """
    Manages LinkedIn interactions including likes, comments, shares, and reactions.
    
    Follows WSP 40 compliance with single responsibility and ≤300 lines.
    Implements WSP 66 proactive component architecture for engagement automation.
    """
    
    def __init__(self, rate_limit_delay: int = 2):
        """
        Initialize the LinkedIn Interaction Manager.
        
        Args:
            rate_limit_delay: Delay between interactions in seconds
        """
        self.rate_limit_delay = rate_limit_delay
        self.logger = logging.getLogger(__name__)
        self.interaction_history: List[InteractionResult] = []
        self.rate_limit_tracker: Dict[str, datetime] = {}
        
        # Engagement strategy configuration
        self.engagement_strategy = {
            'max_daily_interactions': 50,
            'interaction_cooldown': 300,  # 5 minutes
            'relevance_threshold': 0.7,
            'engagement_threshold': 0.5
        }
        
        self.logger.info("✅ LinkedInInteractionManager initialized for autonomous engagement")
    
    def like_post(self, post_id: str, author_id: str) -> InteractionResult:
        """
        Like a LinkedIn post.
        
        Args:
            post_id: ID of the post to like
            author_id: ID of the post author
            
        Returns:
            InteractionResult with success status
        """
        try:
            # Check rate limiting
            if not self._check_rate_limit(f"like_{post_id}"):
                return InteractionResult(
                    interaction_id=f"like_{post_id}_{datetime.now().timestamp()}",
                    target_post_id=post_id,
                    interaction_type=InteractionType.LIKE,
                    success=False,
                    timestamp=datetime.now(),
                    error_message="Rate limit exceeded"
                )
            
            # Mock LinkedIn API call
            self._simulate_api_call("like", post_id)
            
            result = InteractionResult(
                interaction_id=f"like_{post_id}_{datetime.now().timestamp()}",
                target_post_id=post_id,
                interaction_type=InteractionType.LIKE,
                success=True,
                timestamp=datetime.now(),
                response_data={"status": "liked", "post_id": post_id}
            )
            
            self.interaction_history.append(result)
            self.logger.info(f"✅ Liked post {post_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to like post {post_id}: {str(e)}")
            return InteractionResult(
                interaction_id=f"like_{post_id}_{datetime.now().timestamp()}",
                target_post_id=post_id,
                interaction_type=InteractionType.LIKE,
                success=False,
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    def comment_on_post(self, post_id: str, author_id: str, comment_text: str) -> InteractionResult:
        """
        Comment on a LinkedIn post.
        
        Args:
            post_id: ID of the post to comment on
            author_id: ID of the post author
            comment_text: Text of the comment
            
        Returns:
            InteractionResult with success status
        """
        try:
            # Validate comment
            if not self._validate_comment(comment_text):
                return InteractionResult(
                    interaction_id=f"comment_{post_id}_{datetime.now().timestamp()}",
                    target_post_id=post_id,
                    interaction_type=InteractionType.COMMENT,
                    success=False,
                    timestamp=datetime.now(),
                    error_message="Invalid comment content"
                )
            
            # Check rate limiting
            if not self._check_rate_limit(f"comment_{post_id}"):
                return InteractionResult(
                    interaction_id=f"comment_{post_id}_{datetime.now().timestamp()}",
                    target_post_id=post_id,
                    interaction_type=InteractionType.COMMENT,
                    success=False,
                    timestamp=datetime.now(),
                    error_message="Rate limit exceeded"
                )
            
            # Mock LinkedIn API call
            self._simulate_api_call("comment", post_id)
            
            result = InteractionResult(
                interaction_id=f"comment_{post_id}_{datetime.now().timestamp()}",
                target_post_id=post_id,
                interaction_type=InteractionType.COMMENT,
                success=True,
                timestamp=datetime.now(),
                response_data={
                    "status": "commented",
                    "post_id": post_id,
                    "comment_text": comment_text
                }
            )
            
            self.interaction_history.append(result)
            self.logger.info(f"✅ Commented on post {post_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to comment on post {post_id}: {str(e)}")
            return InteractionResult(
                interaction_id=f"comment_{post_id}_{datetime.now().timestamp()}",
                target_post_id=post_id,
                interaction_type=InteractionType.COMMENT,
                success=False,
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    def share_post(self, post_id: str, author_id: str, share_message: Optional[str] = None) -> InteractionResult:
        """
        Share a LinkedIn post.
        
        Args:
            post_id: ID of the post to share
            author_id: ID of the post author
            share_message: Optional message to include with the share
            
        Returns:
            InteractionResult with success status
        """
        try:
            # Check rate limiting
            if not self._check_rate_limit(f"share_{post_id}"):
                return InteractionResult(
                    interaction_id=f"share_{post_id}_{datetime.now().timestamp()}",
                    target_post_id=post_id,
                    interaction_type=InteractionType.SHARE,
                    success=False,
                    timestamp=datetime.now(),
                    error_message="Rate limit exceeded"
                )
            
            # Mock LinkedIn API call
            self._simulate_api_call("share", post_id)
            
            result = InteractionResult(
                interaction_id=f"share_{post_id}_{datetime.now().timestamp()}",
                target_post_id=post_id,
                interaction_type=InteractionType.SHARE,
                success=True,
                timestamp=datetime.now(),
                response_data={
                    "status": "shared",
                    "post_id": post_id,
                    "share_message": share_message
                }
            )
            
            self.interaction_history.append(result)
            self.logger.info(f"✅ Shared post {post_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to share post {post_id}: {str(e)}")
            return InteractionResult(
                interaction_id=f"share_{post_id}_{datetime.now().timestamp()}",
                target_post_id=post_id,
                interaction_type=InteractionType.SHARE,
                success=False,
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    def react_to_post(self, post_id: str, author_id: str, reaction_type: ReactionType) -> InteractionResult:
        """
        React to a LinkedIn post with a specific reaction.
        
        Args:
            post_id: ID of the post to react to
            author_id: ID of the post author
            reaction_type: Type of reaction to apply
            
        Returns:
            InteractionResult with success status
        """
        try:
            # Check rate limiting
            if not self._check_rate_limit(f"react_{post_id}"):
                return InteractionResult(
                    interaction_id=f"react_{post_id}_{datetime.now().timestamp()}",
                    target_post_id=post_id,
                    interaction_type=InteractionType.REACT,
                    success=False,
                    timestamp=datetime.now(),
                    error_message="Rate limit exceeded"
                )
            
            # Mock LinkedIn API call
            self._simulate_api_call("react", post_id)
            
            result = InteractionResult(
                interaction_id=f"react_{post_id}_{datetime.now().timestamp()}",
                target_post_id=post_id,
                interaction_type=InteractionType.REACT,
                success=True,
                timestamp=datetime.now(),
                response_data={
                    "status": "reacted",
                    "post_id": post_id,
                    "reaction_type": reaction_type.value
                }
            )
            
            self.interaction_history.append(result)
            self.logger.info(f"✅ Reacted to post {post_id} with {reaction_type.value}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to react to post {post_id}: {str(e)}")
            return InteractionResult(
                interaction_id=f"react_{post_id}_{datetime.now().timestamp()}",
                target_post_id=post_id,
                interaction_type=InteractionType.REACT,
                success=False,
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    def get_interaction_history(self, limit: int = 50) -> List[InteractionResult]:
        """
        Get recent interaction history.
        
        Args:
            limit: Maximum number of interactions to return
            
        Returns:
            List of recent interactions
        """
        return sorted(
            self.interaction_history[-limit:],
            key=lambda x: x.timestamp,
            reverse=True
        )
    
    def get_interaction_stats(self) -> Dict[str, Any]:
        """
        Get interaction statistics.
        
        Returns:
            Dictionary with interaction statistics
        """
        if not self.interaction_history:
            return {
                "total_interactions": 0,
                "successful_interactions": 0,
                "failed_interactions": 0,
                "interaction_types": {},
                "daily_interactions": 0
            }
        
        successful = [i for i in self.interaction_history if i.success]
        failed = [i for i in self.interaction_history if not i.success]
        
        # Count by interaction type
        type_counts = {}
        for interaction in self.interaction_history:
            interaction_type = interaction.interaction_type.value
            type_counts[interaction_type] = type_counts.get(interaction_type, 0) + 1
        
        # Count today's interactions
        today = datetime.now().date()
        daily_interactions = len([
            i for i in self.interaction_history 
            if i.timestamp.date() == today
        ])
        
        return {
            "total_interactions": len(self.interaction_history),
            "successful_interactions": len(successful),
            "failed_interactions": len(failed),
            "success_rate": len(successful) / len(self.interaction_history) if self.interaction_history else 0,
            "interaction_types": type_counts,
            "daily_interactions": daily_interactions
        }
    
    def _check_rate_limit(self, action_key: str) -> bool:
        """
        Check if an action is within rate limits.
        
        Args:
            action_key: Unique key for the action
            
        Returns:
            True if action is allowed, False if rate limited
        """
        now = datetime.now()
        
        # Check if action was performed recently
        if action_key in self.rate_limit_tracker:
            last_action = self.rate_limit_tracker[action_key]
            if (now - last_action).total_seconds() < self.engagement_strategy['interaction_cooldown']:
                return False
        
        # Check daily interaction limit
        daily_interactions = self.get_interaction_stats()['daily_interactions']
        if daily_interactions >= self.engagement_strategy['max_daily_interactions']:
            return False
        
        # Update rate limit tracker
        self.rate_limit_tracker[action_key] = now
        return True
    
    def _validate_comment(self, comment_text: str) -> bool:
        """
        Validate comment content.
        
        Args:
            comment_text: Text to validate
            
        Returns:
            True if comment is valid, False otherwise
        """
        if not comment_text or not comment_text.strip():
            return False
        
        if len(comment_text) > 1000:  # LinkedIn comment limit
            return False
        
        # Add more validation as needed
        return True
    
    def _simulate_api_call(self, action: str, post_id: str) -> None:
        """
        Simulate LinkedIn API call for testing.
        
        Args:
            action: Type of action being performed
            post_id: ID of the post being acted upon
        """
        import time
        time.sleep(self.rate_limit_delay)  # Simulate API delay
        self.logger.debug(f"🔗 Simulated {action} API call for post {post_id}")


# Factory function for clean initialization
def create_linkedin_interaction_manager(rate_limit_delay: int = 2) -> LinkedInInteractionManager:
    """
    Create a LinkedIn Interaction Manager instance.
    
    Args:
        rate_limit_delay: Delay between interactions in seconds
        
    Returns:
        Configured LinkedInInteractionManager instance
    """
    return LinkedInInteractionManager(rate_limit_delay=rate_limit_delay)


if __name__ == "__main__":
    # Test the interaction manager
    manager = create_linkedin_interaction_manager()
    
    # Test interactions
    test_post_id = "test_post_123"
    test_author_id = "test_author_456"
    
    # Test like
    like_result = manager.like_post(test_post_id, test_author_id)
    print(f"Like result: {like_result.success}")
    
    # Test comment
    comment_result = manager.comment_on_post(test_post_id, test_author_id, "Great post!")
    print(f"Comment result: {comment_result.success}")
    
    # Test reaction
    react_result = manager.react_to_post(test_post_id, test_author_id, ReactionType.CELEBRATE)
    print(f"Reaction result: {react_result.success}")
    
    # Print stats
    stats = manager.get_interaction_stats()
    print(f"Interaction stats: {stats}") 