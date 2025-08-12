#!/usr/bin/env python3
"""
User Classification Module - WSP Compliant
Classifies YouTube users into tiers with permissions
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum

logger = logging.getLogger(__name__)

class UserType(Enum):
    """User classification types - supports YouTube's 6 tier system"""
    OWNER = "owner"
    MODERATOR = "moderator"
    # YouTube supports up to 6 membership levels
    MEMBER_TIER_6 = "member_t6"  # Highest tier - Ultimate supporters
    MEMBER_TIER_5 = "member_t5"  # Elite tier
    MEMBER_TIER_4 = "member_t4"  # Premium tier
    MEMBER_TIER_3 = "member_t3"  # Advanced tier
    MEMBER_TIER_2 = "member_t2"  # Standard tier
    MEMBER_TIER_1 = "member_t1"  # Basic tier
    VERIFIED = "verified"
    REGULAR = "regular"
    BANNED = "banned"
    TROLL = "troll"  # Identified MAGA/spam

@dataclass
class UserProfile:
    """Complete user profile with all attributes"""
    # Basic info
    user_id: str
    channel_id: str
    display_name: str
    
    # YouTube attributes
    is_owner: bool = False
    is_moderator: bool = False
    is_member: bool = False
    is_verified: bool = False
    is_sponsor: bool = False  # Has channel membership
    
    # Membership details
    member_months: int = 0
    member_tier: Optional[str] = None
    membership_start: Optional[datetime] = None
    
    # User classification
    user_type: UserType = UserType.REGULAR
    
    # Interaction tracking
    message_count: int = 0
    violation_count: int = 0
    timeout_count: int = 0
    last_message: Optional[datetime] = None
    last_timeout: Optional[datetime] = None
    
    # Financial contributions
    total_superchat: float = 0.0
    total_gifts_given: int = 0
    last_superchat: Optional[datetime] = None
    
    # Bot interaction
    can_trigger_emoji: bool = False
    can_use_commands: bool = False
    can_receive_responses: bool = False
    response_cooldown: int = 30  # seconds
    
    # Consciousness tracking
    consciousness_level: str = "111"  # Default conscious state
    consciousness_history: List[str] = field(default_factory=list)
    
    # Special flags
    is_whitelisted: bool = False
    is_blacklisted: bool = False
    bypass_cooldown: bool = False
    priority_queue: bool = False
    
    def __post_init__(self):
        """Set permissions based on user type"""
        self._update_permissions()
    
    def _update_permissions(self):
        """Update permissions based on user type"""
        if self.user_type == UserType.OWNER:
            self.can_trigger_emoji = True
            self.can_use_commands = True
            self.can_receive_responses = True
            self.bypass_cooldown = True
            self.priority_queue = True
            self.response_cooldown = 0
            
        elif self.user_type == UserType.MODERATOR:
            self.can_trigger_emoji = True
            self.can_use_commands = True
            self.can_receive_responses = True
            self.priority_queue = True
            self.response_cooldown = 15
            
        elif self.user_type in [UserType.MEMBER_TIER_6, UserType.MEMBER_TIER_5]:
            # Highest tier members - almost owner privileges
            self.can_trigger_emoji = True
            self.can_use_commands = True
            self.can_receive_responses = True
            self.bypass_cooldown = True
            self.priority_queue = True
            self.response_cooldown = 5
            
        elif self.user_type in [UserType.MEMBER_TIER_4, UserType.MEMBER_TIER_3]:
            # Premium members
            self.can_trigger_emoji = True
            self.can_use_commands = True
            self.can_receive_responses = True
            self.priority_queue = True
            self.response_cooldown = 10 if self.user_type == UserType.MEMBER_TIER_4 else 15
            
        elif self.user_type == UserType.MEMBER_TIER_2:
            # Standard members
            self.can_trigger_emoji = True
            self.can_use_commands = True
            self.can_receive_responses = True
            self.priority_queue = False
            self.response_cooldown = 30
            
        elif self.user_type == UserType.MEMBER_TIER_1:
            self.can_trigger_emoji = False  # Must earn it
            self.can_use_commands = True
            self.can_receive_responses = True
            self.response_cooldown = 45
            
        elif self.user_type == UserType.VERIFIED:
            self.can_trigger_emoji = False
            self.can_use_commands = False
            self.can_receive_responses = True  # Get responses but limited
            self.response_cooldown = 90
            
        elif self.user_type == UserType.REGULAR:
            self.can_trigger_emoji = False
            self.can_use_commands = False
            self.can_receive_responses = False
            self.response_cooldown = 120
            
        elif self.user_type in [UserType.BANNED, UserType.TROLL]:
            self.can_trigger_emoji = False
            self.can_use_commands = False
            self.can_receive_responses = False
            self.response_cooldown = 999999

class UserClassifier:
    """Classify users based on YouTube API data"""
    
    @staticmethod
    def classify(author_details: Dict) -> UserProfile:
        """
        Classify a user from YouTube API authorDetails
        
        Args:
            author_details: YouTube API authorDetails object
            
        Returns:
            UserProfile with classified user type
        """
        # Extract basic info
        user_id = author_details.get('channelId', '')
        display_name = author_details.get('displayName', 'Unknown')
        
        # Create profile
        profile = UserProfile(
            user_id=user_id,
            channel_id=user_id,
            display_name=display_name
        )
        
        # Set YouTube attributes
        profile.is_owner = author_details.get('isChatOwner', False)
        profile.is_moderator = author_details.get('isChatModerator', False)
        profile.is_sponsor = author_details.get('isChatSponsor', False)
        profile.is_verified = author_details.get('isVerified', False)
        
        # Determine user type
        if profile.is_owner:
            profile.user_type = UserType.OWNER
        elif profile.is_moderator:
            profile.user_type = UserType.MODERATOR
        elif profile.is_sponsor:
            # Determine member tier based on badge or other indicators
            profile.is_member = True
            profile.user_type = UserClassifier._get_member_tier(author_details)
        elif profile.is_verified:
            profile.user_type = UserType.VERIFIED
        else:
            profile.user_type = UserType.REGULAR
        
        # Update permissions based on type
        profile._update_permissions()
        
        return profile
    
    @staticmethod
    def _get_member_tier(author_details: Dict) -> UserType:
        """
        Determine member tier from badge or other indicators
        
        YouTube provides membership badges that indicate duration:
        - New member: < 1 month
        - 1 month badge
        - 2 months badge
        - 6 months badge
        - 12 months badge (1 year)
        - 24 months badge (2 years)
        """
        # This would need to parse the badge URL or metadata
        # For now, return a default
        # In production, would check:
        # - profileImageUrl for badge indicators
        # - sponsorDetails if available
        # - Historical data from our database
        
        return UserType.MEMBER_TIER_1  # Default to tier 1
    
    @staticmethod
    def classify_from_message(message: Dict) -> UserProfile:
        """
        Classify user from a complete message object
        
        Args:
            message: Complete YouTube message object
            
        Returns:
            UserProfile with all available data
        """
        author_details = message.get('authorDetails', {})
        profile = UserClassifier.classify(author_details)
        
        # Add message-specific data
        snippet = message.get('snippet', {})
        
        # Check for Super Chat
        if snippet.get('type') == 'superChatEvent':
            super_chat_details = snippet.get('superChatDetails', {})
            amount = super_chat_details.get('amountMicros', 0) / 1000000
            profile.total_superchat = amount
            profile.last_superchat = datetime.now()
        
        # Check for membership gift
        if snippet.get('type') == 'newSponsorEvent':
            profile.total_gifts_given += 1
        
        return profile
    
    @staticmethod
    def is_maga_troll(message: str, user: UserProfile) -> bool:
        """
        Check if user is a MAGA troll based on message content
        
        Args:
            message: Message text
            user: User profile
            
        Returns:
            True if MAGA troll detected
        """
        maga_keywords = [
            "maga", "trump2024", "trump2028", "stopthesteal",
            "trump train", "america first", "lets go brandon",
            "fake news", "witch hunt", "deep state", "q anon",
            "rigged election", "stolen election", "save america"
        ]
        
        message_lower = message.lower()
        
        # Check for MAGA keywords
        maga_score = sum(1 for keyword in maga_keywords if keyword in message_lower)
        
        # Higher threshold for members/mods (could be ironic)
        if user.user_type in [UserType.OWNER, UserType.MODERATOR]:
            return False  # Never mark mods as trolls
        elif user.is_member:
            return maga_score >= 3  # Need multiple keywords
        else:
            return maga_score >= 1  # Single keyword triggers
    
    @staticmethod
    def update_user_stats(profile: UserProfile, action: str, details: Dict = None):
        """
        Update user statistics based on actions
        
        Args:
            profile: User profile to update
            action: Action type (message, timeout, gift, etc)
            details: Additional action details
        """
        if action == "message":
            profile.message_count += 1
            profile.last_message = datetime.now()
            
        elif action == "timeout":
            profile.timeout_count += 1
            profile.violation_count += 1
            profile.last_timeout = datetime.now()
            
        elif action == "superchat":
            amount = details.get('amount', 0) if details else 0
            profile.total_superchat += amount
            profile.last_superchat = datetime.now()
            
        elif action == "gift":
            profile.total_gifts_given += 1
            
        elif action == "consciousness_change":
            new_level = details.get('level', '111') if details else '111'
            profile.consciousness_level = new_level
            profile.consciousness_history.append({
                'level': new_level,
                'timestamp': datetime.now().isoformat()
            })