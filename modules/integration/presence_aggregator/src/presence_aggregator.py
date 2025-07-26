# modules/integration/presence_aggregator/src/presence_aggregator.py

"""
Presence Aggregator Module
WSP Protocol: WSP 54 (Agent Coordination), WSP 42 (Cross-Domain Integration)

Aggregates and normalizes user presence across multiple platforms with confidence scoring.
Extracted from monolithic Auto Meeting Orchestrator for modular architecture.

Part of Meeting Orchestration Block strategic decomposition.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict

logger = logging.getLogger(__name__)

class PresenceStatus(Enum):
    """Standardized presence status across platforms"""
    ONLINE = "online"
    OFFLINE = "offline"
    IDLE = "idle"
    BUSY = "busy"
    UNKNOWN = "unknown"

class PlatformType(Enum):
    """Supported platform types for presence monitoring"""
    DISCORD = "discord"
    WHATSAPP = "whatsapp"
    ZOOM = "zoom"
    SLACK = "slack"
    TEAMS = "teams"
    LINKEDIN = "linkedin"
    TELEGRAM = "telegram"
    CUSTOM = "custom"

@dataclass
class PlatformPresence:
    """Individual platform presence information"""
    platform: PlatformType
    status: PresenceStatus
    last_updated: datetime
    confidence: float  # 0.0-1.0
    raw_data: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)

@dataclass
class UnifiedAvailabilityProfile:
    """Aggregated presence across all platforms with confidence scoring"""
    user_id: str
    platforms: Dict[str, PlatformPresence]
    overall_status: PresenceStatus
    last_updated: datetime
    confidence_score: float  # 0.0-1.0
    availability_strength: float  # How "available" they are (0.0-1.0)
    metadata: Dict = field(default_factory=dict)

    def is_available_for_meetings(self) -> bool:
        """Check if user is generally available for meetings"""
        return (self.overall_status in [PresenceStatus.ONLINE, PresenceStatus.IDLE] and
                self.confidence_score >= 0.5 and
                self.availability_strength >= 0.3)

    def get_best_contact_platform(self) -> Optional[str]:
        """Get the platform where user is most actively present"""
        if not self.platforms:
            return None
        
        # Sort platforms by status priority and confidence
        status_priority = {
            PresenceStatus.ONLINE: 5,
            PresenceStatus.IDLE: 4,
            PresenceStatus.BUSY: 3,
            PresenceStatus.OFFLINE: 2,
            PresenceStatus.UNKNOWN: 1
        }
        
        best_platform = max(
            self.platforms.values(),
            key=lambda p: (status_priority[p.status], p.confidence, p.last_updated.timestamp())
        )
        
        return best_platform.platform.value

class PresenceAggregator:
    """
    Cross-platform presence aggregation and normalization system
    
    Responsibilities:
    - Collect presence data from multiple platforms
    - Normalize status values across different platform formats
    - Calculate unified availability profiles with confidence scoring
    - Provide real-time presence monitoring and callbacks
    - Integration with other AMO modules for meeting coordination
    """
    
    def __init__(self):
        self.user_profiles: Dict[str, UnifiedAvailabilityProfile] = {}
        self.platform_adapters: Dict[PlatformType, Callable] = {}
        self.presence_callbacks: Dict[str, List[Callable]] = {
            'presence_updated': [],
            'availability_changed': [],
            'user_online': [],
            'user_offline': []
        }
        self.monitoring_sessions: Dict[str, Set[str]] = defaultdict(set)  # intent_id -> user_ids
        self.config = {
            'confidence_threshold': 0.5,
            'availability_threshold': 0.3,
            'status_expiry_minutes': 10,
            'update_interval_seconds': 30
        }
        
        # Platform-specific configuration
        self.platform_config = {
            PlatformType.DISCORD: {'weight': 1.0, 'reliability': 0.9},
            PlatformType.WHATSAPP: {'weight': 0.8, 'reliability': 0.7},
            PlatformType.ZOOM: {'weight': 0.9, 'reliability': 0.8},
            PlatformType.SLACK: {'weight': 0.9, 'reliability': 0.85},
            PlatformType.TEAMS: {'weight': 0.85, 'reliability': 0.8},
            PlatformType.LINKEDIN: {'weight': 0.6, 'reliability': 0.6},
            PlatformType.TELEGRAM: {'weight': 0.7, 'reliability': 0.75}
        }
        
        logger.info("📡 Presence Aggregator initialized")

    async def update_presence(
        self,
        user_id: str,
        platform: PlatformType,
        status: PresenceStatus,
        confidence: float = 1.0,
        raw_data: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Update user presence for a specific platform
        
        Args:
            user_id: User identifier
            platform: Platform where presence was detected
            status: Normalized presence status
            confidence: Confidence in this presence reading (0.0-1.0)
            raw_data: Original platform-specific data
            metadata: Additional metadata about the presence
            
        Returns:
            bool: True if update caused availability change
        """
        # Create or get existing profile
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UnifiedAvailabilityProfile(
                user_id=user_id,
                platforms={},
                overall_status=PresenceStatus.UNKNOWN,
                last_updated=datetime.now(),
                confidence_score=0.0,
                availability_strength=0.0
            )
        
        profile = self.user_profiles[user_id]
        previous_availability = profile.is_available_for_meetings()
        
        # Update platform presence
        platform_presence = PlatformPresence(
            platform=platform,
            status=status,
            last_updated=datetime.now(),
            confidence=confidence,
            raw_data=raw_data or {},
            metadata=metadata or {}
        )
        
        profile.platforms[platform.value] = platform_presence
        
        # Recalculate unified profile
        await self._recalculate_unified_profile(profile)
        
        logger.info(f"📊 Presence updated: {user_id} on {platform.value} = {status.value} ({confidence:.2f} confidence)")
        
        # Check for availability changes
        current_availability = profile.is_available_for_meetings()
        availability_changed = previous_availability != current_availability
        
        # Trigger callbacks
        await self._trigger_callbacks('presence_updated', profile, {
            'platform': platform.value,
            'previous_availability': previous_availability,
            'availability_changed': availability_changed
        })
        
        if availability_changed:
            await self._trigger_callbacks('availability_changed', profile, {
                'now_available': current_availability,
                'was_available': previous_availability
            })
            
            # Specific availability callbacks
            if current_availability and not previous_availability:
                await self._trigger_callbacks('user_online', profile, {'platform': platform.value})
            elif not current_availability and previous_availability:
                await self._trigger_callbacks('user_offline', profile, {'platform': platform.value})
        
        return availability_changed

    async def get_current_status(self, user_id: str) -> Optional[UnifiedAvailabilityProfile]:
        """Get current unified availability profile for a user"""
        profile = self.user_profiles.get(user_id)
        
        if profile:
            # Check for expired presence data
            await self._cleanup_expired_presence(profile)
            await self._recalculate_unified_profile(profile)
        
        return profile

    async def get_users_with_status(self, status: PresenceStatus, min_confidence: float = 0.5) -> List[str]:
        """Get all users currently showing a specific status"""
        matching_users = []
        
        for user_id, profile in self.user_profiles.items():
            if (profile.overall_status == status and 
                profile.confidence_score >= min_confidence):
                matching_users.append(user_id)
        
        return matching_users

    async def get_available_users(self, min_confidence: float = None) -> List[str]:
        """Get all users currently available for meetings"""
        min_confidence = min_confidence or self.config['confidence_threshold']
        available_users = []
        
        for user_id, profile in self.user_profiles.items():
            if profile.is_available_for_meetings() and profile.confidence_score >= min_confidence:
                available_users.append(user_id)
        
        return available_users

    async def check_mutual_availability(self, user1_id: str, user2_id: str) -> Dict:
        """
        Check if two users are mutually available for a meeting
        
        Returns comprehensive availability analysis
        """
        user1_profile = await self.get_current_status(user1_id)
        user2_profile = await self.get_current_status(user2_id)
        
        if not user1_profile or not user2_profile:
            return {
                'mutually_available': False,
                'reason': 'Missing presence data',
                'user1_available': user1_profile.is_available_for_meetings() if user1_profile else False,
                'user2_available': user2_profile.is_available_for_meetings() if user2_profile else False,
                'confidence': 0.0
            }
        
        user1_available = user1_profile.is_available_for_meetings()
        user2_available = user2_profile.is_available_for_meetings()
        mutually_available = user1_available and user2_available
        
        # Calculate combined confidence
        combined_confidence = (user1_profile.confidence_score * user2_profile.confidence_score) ** 0.5
        
        # Find common platforms for optimal communication
        common_platforms = set(user1_profile.platforms.keys()) & set(user2_profile.platforms.keys())
        best_platform = None
        
        if common_platforms:
            # Find platform where both users are most active
            platform_scores = {}
            for platform in common_platforms:
                user1_platform = user1_profile.platforms[platform]
                user2_platform = user2_profile.platforms[platform]
                
                combined_score = (
                    self._get_platform_priority_score(user1_platform.status) *
                    self._get_platform_priority_score(user2_platform.status) *
                    user1_platform.confidence * user2_platform.confidence
                )
                platform_scores[platform] = combined_score
            
            best_platform = max(platform_scores, key=platform_scores.get)
        
        result = {
            'mutually_available': mutually_available,
            'user1_available': user1_available,
            'user2_available': user2_available,
            'combined_confidence': combined_confidence,
            'common_platforms': list(common_platforms),
            'best_platform': best_platform,
            'user1_best_platform': user1_profile.get_best_contact_platform(),
            'user2_best_platform': user2_profile.get_best_contact_platform(),
            'analysis': {
                'user1_status': user1_profile.overall_status.value,
                'user2_status': user2_profile.overall_status.value,
                'user1_strength': user1_profile.availability_strength,
                'user2_strength': user2_profile.availability_strength
            }
        }
        
        logger.info(f"🤝 Mutual availability check: {user1_id} + {user2_id} = {mutually_available}")
        
        return result

    async def start_monitoring_session(self, intent_id: str, user_ids: List[str]) -> bool:
        """
        Start monitoring presence for specific users related to a meeting intent
        
        Args:
            intent_id: Meeting intent identifier
            user_ids: Users to monitor
            
        Returns:
            bool: True if monitoring started successfully
        """
        self.monitoring_sessions[intent_id] = set(user_ids)
        
        logger.info(f"🎯 Started presence monitoring for intent {intent_id}: {user_ids}")
        
        # Check initial availability
        for user_id in user_ids:
            profile = await self.get_current_status(user_id)
            if profile:
                logger.info(f"   {user_id}: {profile.overall_status.value} (confidence: {profile.confidence_score:.2f})")
        
        return True

    async def stop_monitoring_session(self, intent_id: str) -> bool:
        """Stop monitoring session for a meeting intent"""
        if intent_id in self.monitoring_sessions:
            user_ids = self.monitoring_sessions.pop(intent_id)
            logger.info(f"🔄 Stopped presence monitoring for intent {intent_id}: {list(user_ids)}")
            return True
        return False

    async def get_monitoring_sessions(self) -> Dict[str, List[str]]:
        """Get all active monitoring sessions"""
        return {intent_id: list(user_ids) for intent_id, user_ids in self.monitoring_sessions.items()}

    async def normalize_platform_status(self, platform: PlatformType, raw_status: Any) -> PresenceStatus:
        """
        Normalize platform-specific status to standardized format
        
        Args:
            platform: Platform type
            raw_status: Original platform status value
            
        Returns:
            PresenceStatus: Normalized status
        """
        # Platform-specific normalization logic
        if platform == PlatformType.DISCORD:
            status_mapping = {
                'online': PresenceStatus.ONLINE,
                'idle': PresenceStatus.IDLE,
                'dnd': PresenceStatus.BUSY,
                'invisible': PresenceStatus.OFFLINE,
                'offline': PresenceStatus.OFFLINE
            }
            return status_mapping.get(str(raw_status).lower(), PresenceStatus.UNKNOWN)
        
        elif platform == PlatformType.WHATSAPP:
            # WhatsApp has limited presence info
            if raw_status in ['online', 'available']:
                return PresenceStatus.ONLINE
            elif raw_status in ['last seen recently']:
                return PresenceStatus.IDLE
            else:
                return PresenceStatus.UNKNOWN
        
        elif platform == PlatformType.ZOOM:
            status_mapping = {
                'available': PresenceStatus.ONLINE,
                'away': PresenceStatus.IDLE,
                'busy': PresenceStatus.BUSY,
                'do_not_disturb': PresenceStatus.BUSY,
                'offline': PresenceStatus.OFFLINE
            }
            return status_mapping.get(str(raw_status).lower(), PresenceStatus.UNKNOWN)
        
        elif platform == PlatformType.SLACK:
            status_mapping = {
                'active': PresenceStatus.ONLINE,
                'away': PresenceStatus.IDLE,
                'busy': PresenceStatus.BUSY,
                'dnd': PresenceStatus.BUSY,
                'offline': PresenceStatus.OFFLINE
            }
            return status_mapping.get(str(raw_status).lower(), PresenceStatus.UNKNOWN)
        
        # Generic normalization for other platforms
        raw_lower = str(raw_status).lower()
        if raw_lower in ['online', 'available', 'active']:
            return PresenceStatus.ONLINE
        elif raw_lower in ['idle', 'away', 'inactive']:
            return PresenceStatus.IDLE
        elif raw_lower in ['busy', 'dnd', 'do_not_disturb']:
            return PresenceStatus.BUSY
        elif raw_lower in ['offline', 'unavailable']:
            return PresenceStatus.OFFLINE
        else:
            return PresenceStatus.UNKNOWN

    async def subscribe_to_presence(self, event_type: str, callback: Callable) -> bool:
        """
        Subscribe to presence events for integration with other modules
        
        Args:
            event_type: Type of presence event ('presence_updated', 'availability_changed', etc.)
            callback: Async callback function
        """
        if event_type in self.presence_callbacks:
            self.presence_callbacks[event_type].append(callback)
            logger.info(f"📡 Subscribed to {event_type} events")
            return True
        else:
            logger.warning(f"❌ Unknown presence event type: {event_type}")
            return False

    async def get_presence_statistics(self) -> Dict:
        """Get comprehensive presence statistics"""
        stats = {
            'total_users': len(self.user_profiles),
            'active_monitoring_sessions': len(self.monitoring_sessions),
            'platform_coverage': {},
            'status_distribution': {},
            'availability_metrics': {
                'available_users': 0,
                'average_confidence': 0.0,
                'average_availability_strength': 0.0
            }
        }
        
        # Calculate platform coverage
        all_platforms = set()
        for profile in self.user_profiles.values():
            all_platforms.update(profile.platforms.keys())
        
        for platform in all_platforms:
            stats['platform_coverage'][platform] = len([
                p for p in self.user_profiles.values() 
                if platform in p.platforms
            ])
        
        # Calculate status distribution
        for profile in self.user_profiles.values():
            status = profile.overall_status.value
            stats['status_distribution'][status] = stats['status_distribution'].get(status, 0) + 1
            
            # Availability metrics
            if profile.is_available_for_meetings():
                stats['availability_metrics']['available_users'] += 1
        
        # Calculate averages
        if self.user_profiles:
            total_confidence = sum(p.confidence_score for p in self.user_profiles.values())
            total_strength = sum(p.availability_strength for p in self.user_profiles.values())
            count = len(self.user_profiles)
            
            stats['availability_metrics']['average_confidence'] = total_confidence / count
            stats['availability_metrics']['average_availability_strength'] = total_strength / count
        
        return stats

    # Private methods
    
    async def _recalculate_unified_profile(self, profile: UnifiedAvailabilityProfile):
        """Recalculate unified presence from platform data"""
        if not profile.platforms:
            profile.overall_status = PresenceStatus.UNKNOWN
            profile.confidence_score = 0.0
            profile.availability_strength = 0.0
            return
        
        # Calculate overall status based on platform priorities and weights
        status_scores = defaultdict(float)
        total_weight = 0.0
        
        for platform_key, platform_presence in profile.platforms.items():
            try:
                platform_type = PlatformType(platform_key)
                config = self.platform_config.get(platform_type, {'weight': 0.5, 'reliability': 0.5})
                weight = config['weight'] * config['reliability'] * platform_presence.confidence
                
                status_scores[platform_presence.status] += weight
                total_weight += weight
                
            except ValueError:
                # Unknown platform type
                status_scores[platform_presence.status] += 0.3 * platform_presence.confidence
                total_weight += 0.3
        
        # Select status with highest weighted score
        if status_scores:
            profile.overall_status = max(status_scores, key=status_scores.get)
        else:
            profile.overall_status = PresenceStatus.UNKNOWN
        
        # Calculate confidence score
        profile.confidence_score = min(1.0, total_weight / len(profile.platforms))
        
        # Calculate availability strength
        availability_factors = []
        for platform_presence in profile.platforms.values():
            strength = self._get_platform_priority_score(platform_presence.status) * platform_presence.confidence
            availability_factors.append(strength)
        
        if availability_factors:
            profile.availability_strength = sum(availability_factors) / len(availability_factors)
        else:
            profile.availability_strength = 0.0
        
        profile.last_updated = datetime.now()

    def _get_platform_priority_score(self, status: PresenceStatus) -> float:
        """Get numeric priority score for status"""
        priority_scores = {
            PresenceStatus.ONLINE: 1.0,
            PresenceStatus.IDLE: 0.7,
            PresenceStatus.BUSY: 0.3,
            PresenceStatus.OFFLINE: 0.1,
            PresenceStatus.UNKNOWN: 0.0
        }
        return priority_scores[status]

    async def _cleanup_expired_presence(self, profile: UnifiedAvailabilityProfile):
        """Remove expired presence data"""
        expiry_threshold = datetime.now() - timedelta(minutes=self.config['status_expiry_minutes'])
        
        expired_platforms = [
            platform_key for platform_key, platform_presence in profile.platforms.items()
            if platform_presence.last_updated < expiry_threshold
        ]
        
        for platform_key in expired_platforms:
            del profile.platforms[platform_key]
            logger.info(f"🧹 Expired presence data: {profile.user_id} on {platform_key}")

    async def _trigger_callbacks(self, event_type: str, profile: UnifiedAvailabilityProfile, metadata: Dict):
        """Trigger registered callbacks for presence events"""
        callbacks = self.presence_callbacks.get(event_type, [])
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(profile, metadata)
                else:
                    callback(profile, metadata)
            except Exception as e:
                logger.error(f"❌ Presence callback error for {event_type}: {e}")

# Factory function for easy integration
def create_presence_aggregator() -> PresenceAggregator:
    """Factory function to create Presence Aggregator instance"""
    return PresenceAggregator()

# Example usage and testing
async def demo_presence_aggregator():
    """Demonstrate Presence Aggregator functionality"""
    print("=== Presence Aggregator Demo ===")
    
    aggregator = create_presence_aggregator()
    
    # Simulate presence updates for Alice
    await aggregator.update_presence("alice", PlatformType.DISCORD, PresenceStatus.ONLINE, 0.9)
    await aggregator.update_presence("alice", PlatformType.WHATSAPP, PresenceStatus.ONLINE, 0.7)
    await aggregator.update_presence("alice", PlatformType.ZOOM, PresenceStatus.IDLE, 0.8)
    
    # Simulate presence updates for Bob
    await aggregator.update_presence("bob", PlatformType.DISCORD, PresenceStatus.IDLE, 0.8)
    await aggregator.update_presence("bob", PlatformType.SLACK, PresenceStatus.ONLINE, 0.9)
    
    # Check individual status
    alice_profile = await aggregator.get_current_status("alice")
    print(f"✅ Alice profile: {alice_profile.overall_status.value} (confidence: {alice_profile.confidence_score:.2f})")
    print(f"   Available: {alice_profile.is_available_for_meetings()}")
    print(f"   Best platform: {alice_profile.get_best_contact_platform()}")
    
    # Check mutual availability
    mutual = await aggregator.check_mutual_availability("alice", "bob")
    print(f"🤝 Mutual availability: {mutual['mutually_available']}")
    print(f"   Best platform: {mutual['best_platform']}")
    print(f"   Combined confidence: {mutual['combined_confidence']:.2f}")
    
    # Start monitoring session
    await aggregator.start_monitoring_session("intent_123", ["alice", "bob"])
    
    # Get statistics
    stats = await aggregator.get_presence_statistics()
    print(f"📊 Statistics: {stats}")
    
    return aggregator

if __name__ == "__main__":
    asyncio.run(demo_presence_aggregator()) 