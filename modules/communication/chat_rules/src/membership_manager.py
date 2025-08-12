#!/usr/bin/env python3
"""
Membership Manager - Fetches and manages YouTube membership tiers
WSP Compliant module for handling YouTube's 6-tier membership system
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class MembershipLevel:
    """Represents a YouTube membership level/tier"""
    level_id: str
    display_name: str
    price_micros: int  # Price in micros (1M = $1)
    currency: str
    perks: List[str]
    badge_url: Optional[str] = None
    emoji: Optional[str] = None
    tier_number: int = 1  # 1-6
    
    @property
    def price_dollars(self) -> float:
        """Get price in dollars"""
        return self.price_micros / 1000000
    
    @property
    def tier_emoji(self) -> str:
        """Get tier emoji for display"""
        tier_emojis = {
            1: "🥉",  # Bronze - Basic
            2: "🥈",  # Silver - Standard
            3: "🥇",  # Gold - Advanced
            4: "💎",  # Diamond - Premium
            5: "💠",  # Platinum - Elite
            6: "👑"   # Crown - Ultimate
        }
        return tier_emojis.get(self.tier_number, "⭐")

class MembershipManager:
    """
    Manages YouTube membership levels and member benefits
    Integrates with YouTube API to fetch tier information
    """
    
    def __init__(self, youtube_service=None):
        """
        Initialize membership manager
        
        Args:
            youtube_service: Authenticated YouTube API service
        """
        self.youtube_service = youtube_service
        self.membership_levels: Dict[str, MembershipLevel] = {}
        self.cached_levels_time: Optional[datetime] = None
        self.cache_duration_hours = 24  # Cache for 24 hours
        
    def fetch_membership_levels(self) -> List[MembershipLevel]:
        """
        Fetch membership levels from YouTube API
        
        Returns:
            List of MembershipLevel objects
        """
        if not self.youtube_service:
            logger.warning("No YouTube service available, using defaults")
            return self._get_default_levels()
        
        try:
            # Check cache
            if self._is_cache_valid():
                return list(self.membership_levels.values())
            
            # Fetch from API
            request = self.youtube_service.membershipsLevels().list(
                part="id,snippet"
            )
            response = request.execute()
            
            levels = []
            tier_number = 1
            
            for item in response.get('items', []):
                level_id = item['id']
                snippet = item['snippet']
                
                # Extract level details
                level = MembershipLevel(
                    level_id=level_id,
                    display_name=snippet.get('displayName', f'Tier {tier_number}'),
                    price_micros=snippet.get('priceMicros', 0),
                    currency=snippet.get('currency', 'USD'),
                    perks=self._extract_perks(snippet),
                    badge_url=snippet.get('badgeUrl'),
                    tier_number=tier_number
                )
                
                levels.append(level)
                self.membership_levels[level_id] = level
                tier_number += 1
            
            # Update cache time
            self.cached_levels_time = datetime.now()
            
            logger.info(f"✅ Fetched {len(levels)} membership levels from YouTube")
            return levels
            
        except Exception as e:
            logger.error(f"Failed to fetch membership levels: {e}")
            return self._get_default_levels()
    
    def get_member_details(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed member information including their tier
        
        Args:
            channel_id: YouTube channel ID of the member
            
        Returns:
            Member details including tier information
        """
        if not self.youtube_service:
            return None
        
        try:
            # Fetch member details
            request = self.youtube_service.members().list(
                part="snippet",
                filterByMemberChannelId=channel_id,
                maxResults=1
            )
            response = request.execute()
            
            if not response.get('items'):
                return None
            
            member = response['items'][0]
            snippet = member['snippet']
            
            # Extract membership details
            details = {
                'channel_id': channel_id,
                'display_name': snippet.get('memberDetails', {}).get('displayName'),
                'membership_duration_months': snippet.get('membershipDurationMonths', 0),
                'highest_level_id': snippet.get('highestAccessibleLevel'),
                'highest_level_name': snippet.get('highestAccessibleLevelDisplayName'),
                'accessible_levels': snippet.get('accessibleLevels', []),
                'member_since': snippet.get('memberSince'),
                'total_revenue_cents': snippet.get('totalCentsFromMember', 0)
            }
            
            # Map to tier number
            if details['highest_level_id'] in self.membership_levels:
                level = self.membership_levels[details['highest_level_id']]
                details['tier_number'] = level.tier_number
                details['tier_emoji'] = level.tier_emoji
            else:
                # Estimate tier from duration
                details['tier_number'] = self._estimate_tier_from_duration(
                    details['membership_duration_months']
                )
            
            return details
            
        except Exception as e:
            logger.error(f"Failed to get member details: {e}")
            return None
    
    def classify_member_tier(self, member_data: Dict[str, Any]) -> int:
        """
        Classify a member into tier 1-6 based on available data
        
        Args:
            member_data: Member data from YouTube API
            
        Returns:
            Tier number (1-6)
        """
        # Check explicit tier from API
        if 'highestAccessibleLevel' in member_data:
            level_id = member_data['highestAccessibleLevel']
            if level_id in self.membership_levels:
                return self.membership_levels[level_id].tier_number
        
        # Check membership duration (fallback method)
        duration_months = member_data.get('membershipDurationMonths', 0)
        return self._estimate_tier_from_duration(duration_months)
    
    def _estimate_tier_from_duration(self, months: int) -> int:
        """
        Estimate tier based on membership duration
        This is a fallback when exact tier isn't available
        
        Args:
            months: Membership duration in months
            
        Returns:
            Estimated tier (1-6)
        """
        if months >= 24:
            return 6  # 2+ years = highest tier
        elif months >= 12:
            return 5  # 1-2 years
        elif months >= 6:
            return 4  # 6-12 months
        elif months >= 3:
            return 3  # 3-6 months
        elif months >= 1:
            return 2  # 1-3 months
        else:
            return 1  # New member
    
    def _extract_perks(self, snippet: Dict) -> List[str]:
        """Extract perks from membership level snippet"""
        perks = []
        
        # Standard perks based on YouTube's system
        perks.append("Loyalty badge next to name")
        perks.append("Custom emoji in chat")
        
        # Check for additional perks in description
        description = snippet.get('description', '')
        if 'early access' in description.lower():
            perks.append("Early access to videos")
        if 'exclusive' in description.lower():
            perks.append("Exclusive content")
        if 'shoutout' in description.lower():
            perks.append("Shoutouts")
        if 'discord' in description.lower():
            perks.append("Discord access")
        
        return perks
    
    def _get_default_levels(self) -> List[MembershipLevel]:
        """
        Get default membership levels when API is unavailable
        Based on common YouTube membership structure
        """
        defaults = [
            MembershipLevel(
                level_id="tier1",
                display_name="Supporter",
                price_micros=990000,  # $0.99
                currency="USD",
                perks=["Badge", "Custom emoji"],
                tier_number=1
            ),
            MembershipLevel(
                level_id="tier2",
                display_name="Fan",
                price_micros=1990000,  # $1.99
                currency="USD",
                perks=["Badge", "Custom emoji", "Members-only posts"],
                tier_number=2
            ),
            MembershipLevel(
                level_id="tier3",
                display_name="Super Fan",
                price_micros=4990000,  # $4.99
                currency="USD",
                perks=["Badge", "Custom emoji", "Members-only posts", "Early access"],
                tier_number=3
            ),
            MembershipLevel(
                level_id="tier4",
                display_name="VIP",
                price_micros=9990000,  # $9.99
                currency="USD",
                perks=["Badge", "Custom emoji", "Members-only posts", "Early access", "Monthly shoutout"],
                tier_number=4
            ),
            MembershipLevel(
                level_id="tier5",
                display_name="Elite",
                price_micros=19990000,  # $19.99
                currency="USD",
                perks=["Badge", "Custom emoji", "Members-only posts", "Early access", "Shoutouts", "Discord"],
                tier_number=5
            ),
            MembershipLevel(
                level_id="tier6",
                display_name="Legend",
                price_micros=49990000,  # $49.99
                currency="USD",
                perks=["All perks", "Direct access", "Special events", "Co-stream privileges"],
                tier_number=6
            )
        ]
        
        for level in defaults:
            self.membership_levels[level.level_id] = level
        
        return defaults
    
    def _is_cache_valid(self) -> bool:
        """Check if cached levels are still valid"""
        if not self.cached_levels_time or not self.membership_levels:
            return False
        
        hours_elapsed = (datetime.now() - self.cached_levels_time).total_seconds() / 3600
        return hours_elapsed < self.cache_duration_hours
    
    def get_tier_benefits(self, tier_number: int) -> Dict[str, Any]:
        """
        Get benefits for a specific tier
        
        Args:
            tier_number: Tier number (1-6)
            
        Returns:
            Dictionary of benefits
        """
        benefits = {
            'tier_number': tier_number,
            'tier_emoji': self._get_tier_emoji(tier_number),
            'can_trigger_emoji': tier_number >= 2,
            'can_use_commands': True,
            'can_receive_responses': True,
            'priority_queue': tier_number >= 4,
            'premium_responses': tier_number >= 5,
            'direct_ai_access': tier_number >= 3,
            'response_cooldown': max(5, 60 - (tier_number * 10)),  # 50s for T1, 5s for T6
            'timeout_immunity': tier_number >= 6,
            'special_greetings': tier_number >= 3,
            'consciousness_boost': tier_number * 0.2  # Consciousness level multiplier
        }
        
        return benefits
    
    def _get_tier_emoji(self, tier_number: int) -> str:
        """Get emoji for tier display"""
        tier_emojis = {
            1: "🥉", 2: "🥈", 3: "🥇",
            4: "💎", 5: "💠", 6: "👑"
        }
        return tier_emojis.get(tier_number, "⭐")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize manager
    manager = MembershipManager()
    
    # Get default levels
    levels = manager.fetch_membership_levels()
    
    print("YouTube Membership Tiers:")
    print("=" * 60)
    for level in levels:
        print(f"{level.tier_emoji} Tier {level.tier_number}: {level.display_name}")
        print(f"  Price: ${level.price_dollars:.2f}")
        print(f"  Perks: {', '.join(level.perks)}")
        print()
    
    # Show tier benefits
    print("\nTier Benefits:")
    print("=" * 60)
    for tier in range(1, 7):
        benefits = manager.get_tier_benefits(tier)
        print(f"Tier {tier} {benefits['tier_emoji']}:")
        print(f"  AI Access: {benefits['direct_ai_access']}")
        print(f"  Cooldown: {benefits['response_cooldown']}s")
        print(f"  Premium: {benefits['premium_responses']}")
        print()