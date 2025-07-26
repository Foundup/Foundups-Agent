"""
WSP 71: Presence Aggregator Implementation
==========================================

Multi-platform presence detection and unified availability profiling.
Extracted from auto_meeting_orchestrator PoC for strategic decomposition.

WSP Integration:
- WSP 3: Platform_integration domain for external API integration
- WSP 11: Clean interface definition for modular consumption  
- WSP 49: Standard module structure compliance
- WSP 71: Secrets management for platform API credentials
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum

# WRE Integration
try:
    from ...wre_core.src.utils.wre_logger import wre_log
    from ...wre_core.src.components.security.secrets_manager import SecretsManager
except ImportError:
    def wre_log(msg: str, level: str = "INFO"):
        print(f"[{level}] {msg}")
    
    class SecretsManager:
        @staticmethod
        async def get_secret(key: str) -> str:
            return "mock_secret"

logger = logging.getLogger(__name__)


class PresenceStatus(Enum):
    """Unified presence status across all platforms"""
    ONLINE = "online"
    OFFLINE = "offline"
    IDLE = "idle"
    BUSY = "busy"
    UNKNOWN = "unknown"
    
    def get_priority_score(self) -> int:
        """Priority scoring for presence aggregation"""
        priority_map = {
            PresenceStatus.ONLINE: 5,
            PresenceStatus.IDLE: 4,
            PresenceStatus.BUSY: 3,
            PresenceStatus.OFFLINE: 2,
            PresenceStatus.UNKNOWN: 1
        }
        return priority_map[self]


@dataclass
class PlatformPresence:
    """Individual platform presence data"""
    platform: str
    status: PresenceStatus
    last_seen: datetime
    confidence: float  # 0.0-1.0
    raw_data: Optional[Dict[str, Any]] = None


@dataclass
class UnifiedAvailabilityProfile:
    """Unified presence profile across all platforms"""
    user_id: str
    overall_status: PresenceStatus
    confidence_score: float  # 0.0-1.0
    platform_statuses: Dict[str, PlatformPresence]
    last_seen: datetime
    last_activity: Optional[datetime] = None
    
    def is_available_for_meeting(self) -> bool:
        """Determine if user is available for meeting requests"""
        return self.overall_status in [PresenceStatus.ONLINE, PresenceStatus.IDLE]


class PresenceAggregator:
    """
    Multi-platform presence detection and aggregation engine.
    
    Integrates presence data from multiple platforms, normalizes status,
    and provides unified availability profiling with confidence scoring.
    """
    
    def __init__(self, secrets_manager: Optional[SecretsManager] = None):
        self.secrets_manager = secrets_manager or SecretsManager()
        self.platform_adapters = {}
        self.presence_cache = {}
        self.presence_subscribers = {}
        
        # Platform confidence weights
        self.platform_weights = {
            "discord": 0.9,
            "whatsapp": 0.85,
            "zoom": 0.8,
            "teams": 0.75,
            "slack": 0.7,
            "generic": 0.5
        }
        
        wre_log("PresenceAggregator initialized with multi-platform support")
    
    async def get_current_status(self, user_id: str) -> UnifiedAvailabilityProfile:
        """
        Get unified presence status for a user across all platforms.
        
        Args:
            user_id: User identifier
            
        Returns:
            UnifiedAvailabilityProfile with aggregated presence data
        """
        wre_log(f"Aggregating presence for user: {user_id}")
        
        # Get presence from all configured platforms
        platform_presences = await self._collect_platform_presences(user_id)
        
        if not platform_presences:
            # Return unknown status if no platform data available
            return UnifiedAvailabilityProfile(
                user_id=user_id,
                overall_status=PresenceStatus.UNKNOWN,
                confidence_score=0.0,
                platform_statuses={},
                last_seen=datetime.now() - timedelta(hours=24)
            )
        
        # Calculate unified status
        overall_status = self._calculate_overall_status(platform_presences)
        confidence_score = self._calculate_confidence_score(platform_presences)
        
        # Determine most recent activity
        last_seen = max(p.last_seen for p in platform_presences.values())
        
        profile = UnifiedAvailabilityProfile(
            user_id=user_id,
            overall_status=overall_status,
            confidence_score=confidence_score,
            platform_statuses=platform_presences,
            last_seen=last_seen,
            last_activity=last_seen if overall_status != PresenceStatus.OFFLINE else None
        )
        
        # Cache the profile
        self.presence_cache[user_id] = profile
        
        # Notify subscribers
        await self._notify_subscribers(user_id, profile)
        
        return profile
    
    async def subscribe_presence(self, user_id: str, callback: Callable[[UnifiedAvailabilityProfile], None]):
        """
        Subscribe to presence updates for a user.
        
        Args:
            user_id: User to monitor
            callback: Function to call when presence changes
        """
        if user_id not in self.presence_subscribers:
            self.presence_subscribers[user_id] = []
        
        self.presence_subscribers[user_id].append(callback)
        wre_log(f"Subscribed to presence updates for user: {user_id}")
    
    def normalize_status(self, platform: str, raw_status: Any) -> PresenceStatus:
        """
        Normalize platform-specific status to unified PresenceStatus.
        
        Args:
            platform: Platform identifier
            raw_status: Platform-specific status data
            
        Returns:
            Normalized PresenceStatus
        """
        if isinstance(raw_status, str):
            status_lower = raw_status.lower()
            
            # Common status mappings
            if status_lower in ["online", "available", "active"]:
                return PresenceStatus.ONLINE
            elif status_lower in ["idle", "away", "snooze"]:
                return PresenceStatus.IDLE
            elif status_lower in ["busy", "dnd", "do not disturb", "in a meeting"]:
                return PresenceStatus.BUSY
            elif status_lower in ["offline", "invisible", "hidden"]:
                return PresenceStatus.OFFLINE
        
        return PresenceStatus.UNKNOWN
    
    async def aggregate_multi_platform(self, user_id: str) -> UnifiedAvailabilityProfile:
        """Alias for get_current_status for interface compatibility"""
        return await self.get_current_status(user_id)
    
    # Private Methods
    
    async def _collect_platform_presences(self, user_id: str) -> Dict[str, PlatformPresence]:
        """Collect presence data from all configured platforms"""
        presences = {}
        
        # For prototype: simulate platform data
        # In production: integrate with actual platform APIs
        simulated_platforms = ["discord", "whatsapp", "zoom"]
        
        for platform in simulated_platforms:
            try:
                # Simulate platform API call
                status = await self._simulate_platform_presence(platform, user_id)
                
                presences[platform] = PlatformPresence(
                    platform=platform,
                    status=status,
                    last_seen=datetime.now(),
                    confidence=self.platform_weights.get(platform, 0.5)
                )
            except Exception as e:
                wre_log(f"Failed to get presence from {platform}: {e}", "WARNING")
        
        return presences
    
    async def _simulate_platform_presence(self, platform: str, user_id: str) -> PresenceStatus:
        """Simulate platform presence for prototype phase"""
        # Simple simulation logic
        import random
        statuses = [PresenceStatus.ONLINE, PresenceStatus.IDLE, PresenceStatus.BUSY, PresenceStatus.OFFLINE]
        return random.choice(statuses)
    
    def _calculate_overall_status(self, platform_presences: Dict[str, PlatformPresence]) -> PresenceStatus:
        """
        Calculate unified status from multiple platform presences.
        Uses priority-based aggregation with platform weighting.
        """
        if not platform_presences:
            return PresenceStatus.UNKNOWN
        
        # Weight platform statuses by confidence and platform priority
        weighted_scores = {}
        
        for platform, presence in platform_presences.items():
            priority_score = presence.status.get_priority_score()
            weighted_score = priority_score * presence.confidence
            
            if presence.status not in weighted_scores:
                weighted_scores[presence.status] = 0
            weighted_scores[presence.status] += weighted_score
        
        # Return status with highest weighted score
        return max(weighted_scores.keys(), key=lambda s: weighted_scores[s])
    
    def _calculate_confidence_score(self, platform_presences: Dict[str, PlatformPresence]) -> float:
        """Calculate overall confidence score for the aggregated presence"""
        if not platform_presences:
            return 0.0
        
        # Average confidence weighted by platform reliability
        total_weight = 0
        weighted_confidence = 0
        
        for presence in platform_presences.values():
            platform_weight = self.platform_weights.get(presence.platform, 0.5)
            weighted_confidence += presence.confidence * platform_weight
            total_weight += platform_weight
        
        return min(weighted_confidence / total_weight if total_weight > 0 else 0.0, 1.0)
    
    async def _notify_subscribers(self, user_id: str, profile: UnifiedAvailabilityProfile):
        """Notify all subscribers of presence changes"""
        if user_id in self.presence_subscribers:
            for callback in self.presence_subscribers[user_id]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(profile)
                    else:
                        callback(profile)
                except Exception as e:
                    wre_log(f"Error notifying subscriber: {e}", "ERROR") 