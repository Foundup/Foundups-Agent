"""
Emoji Response Limiter Module - WSP Compliant
Limits responses to emoji triggers to prevent spam and quota exhaustion
"""

import time
import logging
from typing import Dict, Optional
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class EmojiResponseLimiter:
    """Intelligent rate limiting for emoji-triggered responses."""
    
    def __init__(self):
        # Per-user limits
        self.user_response_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10))
        self.user_daily_counts: Dict[str, int] = defaultdict(int)
        self.last_reset = time.time()
        
        # Global limits
        self.global_emoji_responses = deque(maxlen=50)
        self.global_hourly_limit = 20  # Max 20 emoji responses per hour globally
        self.global_daily_limit = 100  # Max 100 emoji responses per day
        
        # Per-user limits
        self.user_hourly_limit = 3  # Max 3 responses per user per hour
        self.user_daily_limit = 10  # Max 10 responses per user per day
        
        # Cooldown periods
        self.user_cooldown = 300  # 5 minutes between responses to same user
        self.global_cooldown = 60  # 1 minute between any emoji responses
        
        # Track daily count
        self.daily_count = 0
        
    def should_respond_to_emoji(self, user_id: str, username: str) -> tuple[bool, str]:
        """
        Check if we should respond to an emoji trigger from this user.
        
        Returns:
            (should_respond, reason_if_not)
        """
        now = time.time()
        
        # Reset daily counts if needed
        if now - self.last_reset > 86400:  # 24 hours
            self.user_daily_counts.clear()
            self.daily_count = 0
            self.last_reset = now
            logger.info("[REFRESH] Reset daily emoji response counts")
        
        # Check global daily limit
        if self.daily_count >= self.global_daily_limit:
            logger.warning(f"[FORBIDDEN] Global daily emoji limit reached ({self.global_daily_limit})")
            return False, "daily_limit"
        
        # Check global hourly limit
        hour_ago = now - 3600
        recent_global = [t for t in self.global_emoji_responses if t > hour_ago]
        if len(recent_global) >= self.global_hourly_limit:
            logger.warning(f"[FORBIDDEN] Global hourly emoji limit reached ({self.global_hourly_limit}/hr)")
            return False, "hourly_limit"
        
        # Check global cooldown
        if self.global_emoji_responses and now - self.global_emoji_responses[-1] < self.global_cooldown:
            remaining = self.global_cooldown - (now - self.global_emoji_responses[-1])
            logger.debug(f"⏳ Global emoji cooldown: {remaining:.1f}s remaining")
            return False, "global_cooldown"
        
        # Check user daily limit
        if self.user_daily_counts[user_id] >= self.user_daily_limit:
            logger.info(f"[FORBIDDEN] User {username} reached daily emoji limit ({self.user_daily_limit})")
            return False, "user_daily_limit"
        
        # Check user hourly limit
        user_history = self.user_response_history[user_id]
        recent_user = [t for t in user_history if t > hour_ago]
        if len(recent_user) >= self.user_hourly_limit:
            logger.info(f"[FORBIDDEN] User {username} reached hourly emoji limit ({self.user_hourly_limit}/hr)")
            return False, "user_hourly_limit"
        
        # Check user cooldown
        if user_history and now - user_history[-1] < self.user_cooldown:
            remaining = self.user_cooldown - (now - user_history[-1])
            logger.debug(f"⏳ User {username} cooldown: {remaining:.1f}s remaining")
            return False, "user_cooldown"
        
        # All checks passed
        logger.info(f"[OK] Emoji response approved for {username}")
        return True, "approved"
    
    def record_emoji_response(self, user_id: str, username: str):
        """Record that an emoji response was sent."""
        now = time.time()
        
        # Record in histories
        self.user_response_history[user_id].append(now)
        self.global_emoji_responses.append(now)
        
        # Update counts
        self.user_daily_counts[user_id] += 1
        self.daily_count += 1
        
        logger.info(f"[DATA] Emoji response recorded for {username}: "
                   f"User daily: {self.user_daily_counts[user_id]}/{self.user_daily_limit}, "
                   f"Global daily: {self.daily_count}/{self.global_daily_limit}")
    
    def get_status(self) -> Dict:
        """Get current limiter status."""
        now = time.time()
        hour_ago = now - 3600
        
        recent_global = [t for t in self.global_emoji_responses if t > hour_ago]
        
        return {
            'global_hourly': f"{len(recent_global)}/{self.global_hourly_limit}",
            'global_daily': f"{self.daily_count}/{self.global_daily_limit}",
            'top_users': sorted(
                [(user, count) for user, count in self.user_daily_counts.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5],
            'next_reset': self.last_reset + 86400 - now
        }
    
    def adjust_limits_based_on_quota(self, quota_percentage: float):
        """
        Dynamically adjust limits based on remaining quota.
        
        Args:
            quota_percentage: 0.0 to 1.0 representing remaining quota
        """
        if quota_percentage < 0.2:  # Less than 20% quota remaining
            # Emergency mode - drastically reduce limits
            self.global_hourly_limit = 5
            self.global_daily_limit = 20
            self.user_hourly_limit = 1
            self.user_daily_limit = 3
            self.user_cooldown = 1800  # 30 minutes
            self.global_cooldown = 300  # 5 minutes
            logger.warning("[ALERT] EMERGENCY: Emoji limits reduced due to low quota")
            
        elif quota_percentage < 0.5:  # Less than 50% quota
            # Conservative mode
            self.global_hourly_limit = 10
            self.global_daily_limit = 50
            self.user_hourly_limit = 2
            self.user_daily_limit = 5
            self.user_cooldown = 600  # 10 minutes
            self.global_cooldown = 120  # 2 minutes
            logger.info("[U+26A0]️ Conservative emoji limits due to moderate quota")
            
        else:
            # Normal mode (default values)
            self.global_hourly_limit = 20
            self.global_daily_limit = 100
            self.user_hourly_limit = 3
            self.user_daily_limit = 10
            self.user_cooldown = 300  # 5 minutes
            self.global_cooldown = 60  # 1 minute
            logger.info("[OK] Normal emoji limits - quota healthy")