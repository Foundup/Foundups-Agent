"""
Presence Aggregator - Cross-Platform Presence Detection and Normalization

Aggregates and normalizes presence data from multiple platforms:
- Discord (online, idle, do not disturb, offline)
- WhatsApp (online, last seen)
- LinkedIn (active, away)
- Zoom (available, busy, away)

Provides unified presence stream for AMO decision making.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Platform(Enum):
    """Supported platforms for presence detection"""
    DISCORD = "discord"
    WHATSAPP = "whatsapp"
    LINKEDIN = "linkedin"
    ZOOM = "zoom"
    TEAMS = "teams"
    SLACK = "slack"


class PresenceStatus(Enum):
    """Normalized presence statuses across platforms"""
    ONLINE = "online"           # Available and active
    IDLE = "idle"              # Available but inactive
    BUSY = "busy"              # Available but in meeting/busy
    AWAY = "away"              # Temporarily away
    OFFLINE = "offline"        # Not available
    UNKNOWN = "unknown"        # Status could not be determined


@dataclass
class PresenceData:
    """Normalized presence information"""
    user_id: str
    platform: Platform
    status: PresenceStatus
    last_seen: datetime
    last_updated: datetime
    raw_status: Optional[str] = None
    activity: Optional[str] = None
    custom_message: Optional[str] = None


class PresenceAggregator:
    """
    Aggregates presence data from multiple platforms and provides
    unified presence information for meeting orchestration.
    """
    
    def __init__(self):
        self.presence_cache: Dict[str, Dict[Platform, PresenceData]] = {}
        self.platform_clients: Dict[Platform, Any] = {}
        self.presence_listeners: List[Callable] = []
        self.polling_tasks: Dict[Platform, asyncio.Task] = {}
        
        # Configuration
        self.cache_ttl = timedelta(minutes=5)
        self.poll_interval = 30  # seconds
        
        logger.info("PresenceAggregator initialized - Ready for cross-platform presence monitoring")
    
    async def initialize_platform(self, platform: Platform, credentials: Dict[str, Any]) -> bool:
        """Initialize connection to a specific platform"""
        try:
            if platform == Platform.DISCORD:
                return await self._initialize_discord(credentials)
            elif platform == Platform.WHATSAPP:
                return await self._initialize_whatsapp(credentials)
            elif platform == Platform.LINKEDIN:
                return await self._initialize_linkedin(credentials)
            elif platform == Platform.ZOOM:
                return await self._initialize_zoom(credentials)
            else:
                logger.warning(f"Platform {platform.value} not yet implemented")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize {platform.value}: {e}")
            return False
    
    async def get_user_presence(self, user_id: str, platform: Optional[Platform] = None) -> Dict[Platform, PresenceData]:
        """Get current presence data for user across platforms"""
        
        if user_id not in self.presence_cache:
            self.presence_cache[user_id] = {}
        
        user_presence = self.presence_cache[user_id]
        
        # Filter by platform if specified
        if platform:
            return {platform: user_presence.get(platform)} if platform in user_presence else {}
        
        # Return all platforms
        return user_presence.copy()
    
    async def get_aggregated_presence(self, user_id: str) -> PresenceStatus:
        """Get unified presence status across all platforms"""
        
        user_presence = await self.get_user_presence(user_id)
        
        if not user_presence:
            return PresenceStatus.UNKNOWN
        
        # Priority order for status aggregation
        status_priority = {
            PresenceStatus.ONLINE: 5,
            PresenceStatus.IDLE: 4,
            PresenceStatus.BUSY: 3,
            PresenceStatus.AWAY: 2,
            PresenceStatus.OFFLINE: 1,
            PresenceStatus.UNKNOWN: 0
        }
        
        # Get highest priority status
        best_status = PresenceStatus.UNKNOWN
        for presence_data in user_presence.values():
            if presence_data and status_priority[presence_data.status] > status_priority[best_status]:
                best_status = presence_data.status
        
        return best_status
    
    async def are_users_available(self, user_ids: List[str]) -> Dict[str, bool]:
        """Check if multiple users are available for meetings"""
        
        availability = {}
        
        for user_id in user_ids:
            status = await self.get_aggregated_presence(user_id)
            # Consider online and idle as available
            availability[user_id] = status in [PresenceStatus.ONLINE, PresenceStatus.IDLE]
        
        return availability
    
    async def add_presence_listener(self, callback: Callable[[str, Platform, PresenceData], None]):
        """Add callback for presence change notifications"""
        self.presence_listeners.append(callback)
    
    async def start_monitoring(self, platforms: List[Platform]):
        """Start monitoring presence for specified platforms"""
        
        for platform in platforms:
            if platform not in self.polling_tasks:
                task = asyncio.create_task(self._poll_platform_presence(platform))
                self.polling_tasks[platform] = task
                logger.info(f"Started monitoring {platform.value}")
    
    async def stop_monitoring(self):
        """Stop all presence monitoring"""
        
        for task in self.polling_tasks.values():
            task.cancel()
        
        self.polling_tasks.clear()
        logger.info("Stopped all presence monitoring")
    
    async def get_presence_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        
        total_users = len(self.presence_cache)
        platform_counts = {}
        
        for user_data in self.presence_cache.values():
            for platform in user_data.keys():
                platform_counts[platform.value] = platform_counts.get(platform.value, 0) + 1
        
        return {
            "total_monitored_users": total_users,
            "platform_distribution": platform_counts,
            "active_platforms": len(self.polling_tasks),
            "cache_size": len(self.presence_cache)
        }
    
    # Platform-specific initialization methods
    
    async def _initialize_discord(self, credentials: Dict[str, Any]) -> bool:
        """Initialize Discord presence monitoring"""
        # PoC: Simulate Discord connection
        logger.info("Discord presence monitoring initialized (simulated)")
        return True
    
    async def _initialize_whatsapp(self, credentials: Dict[str, Any]) -> bool:
        """Initialize WhatsApp presence monitoring"""
        # PoC: Simulate WhatsApp connection
        logger.info("WhatsApp presence monitoring initialized (simulated)")
        return True
    
    async def _initialize_linkedin(self, credentials: Dict[str, Any]) -> bool:
        """Initialize LinkedIn presence monitoring"""
        # PoC: Simulate LinkedIn connection
        logger.info("LinkedIn presence monitoring initialized (simulated)")
        return True
    
    async def _initialize_zoom(self, credentials: Dict[str, Any]) -> bool:
        """Initialize Zoom presence monitoring"""
        # PoC: Simulate Zoom connection
        logger.info("Zoom presence monitoring initialized (simulated)")
        return True
    
    async def _poll_platform_presence(self, platform: Platform):
        """Continuously poll platform for presence updates"""
        
        while True:
            try:
                await self._fetch_platform_presence(platform)
                await asyncio.sleep(self.poll_interval)
                
            except asyncio.CancelledError:
                logger.info(f"Presence polling cancelled for {platform.value}")
                break
            except Exception as e:
                logger.error(f"Error polling {platform.value}: {e}")
                await asyncio.sleep(self.poll_interval)
    
    async def _fetch_platform_presence(self, platform: Platform):
        """Fetch presence data from specific platform"""
        
        # PoC: Generate simulated presence data
        import random
        
        # Simulate some test users
        test_users = ["alice", "bob", "charlie", "diana"]
        
        for user_id in test_users:
            # Random presence status for simulation
            statuses = list(PresenceStatus)
            random_status = random.choice(statuses)
            
            presence_data = PresenceData(
                user_id=user_id,
                platform=platform,
                status=random_status,
                last_seen=datetime.now(),
                last_updated=datetime.now(),
                raw_status=random_status.value,
                activity=f"Using {platform.value}" if random_status == PresenceStatus.ONLINE else None
            )
            
            # Update cache
            if user_id not in self.presence_cache:
                self.presence_cache[user_id] = {}
            
            old_presence = self.presence_cache[user_id].get(platform)
            self.presence_cache[user_id][platform] = presence_data
            
            # Notify listeners if status changed
            if not old_presence or old_presence.status != presence_data.status:
                for listener in self.presence_listeners:
                    try:
                        await listener(user_id, platform, presence_data)
                    except Exception as e:
                        logger.error(f"Error in presence listener: {e}")
    
    def _is_cache_valid(self, presence_data: PresenceData) -> bool:
        """Check if cached presence data is still valid"""
        return datetime.now() - presence_data.last_updated < self.cache_ttl


# Demo function for PoC
async def demo_presence_aggregator():
    """Demonstrate presence aggregation functionality"""
    print("=== Presence Aggregator PoC Demo ===")
    
    aggregator = PresenceAggregator()
    
    # Initialize platforms
    await aggregator.initialize_platform(Platform.DISCORD, {})
    await aggregator.initialize_platform(Platform.WHATSAPP, {})
    
    # Add listener for presence changes
    async def presence_change_handler(user_id: str, platform: Platform, presence: PresenceData):
        print(f"[U+1F4E1] Presence Update: {user_id} on {platform.value} -> {presence.status.value}")
    
    await aggregator.add_presence_listener(presence_change_handler)
    
    # Start monitoring
    await aggregator.start_monitoring([Platform.DISCORD, Platform.WHATSAPP])
    
    # Wait for some updates
    print("[REFRESH] Monitoring presence for 10 seconds...")
    await asyncio.sleep(10)
    
    # Check specific user availability
    alice_presence = await aggregator.get_user_presence("alice")
    print(f"\n[U+1F464] Alice's presence across platforms:")
    for platform, data in alice_presence.items():
        if data:
            print(f"   {platform.value}: {data.status.value}")
    
    # Check aggregated status
    alice_status = await aggregator.get_aggregated_presence("alice")
    print(f"[DATA] Alice's aggregated status: {alice_status.value}")
    
    # Check multiple users availability
    availability = await aggregator.are_users_available(["alice", "bob"])
    print(f"\n[OK] User availability:")
    for user, available in availability.items():
        print(f"   {user}: {'Available' if available else 'Not Available'}")
    
    # Get statistics
    stats = await aggregator.get_presence_statistics()
    print(f"\n[UP] Statistics: {stats}")
    
    # Stop monitoring
    await aggregator.stop_monitoring()
    print("\n[STOP] Presence monitoring stopped")
    
    return aggregator


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_presence_aggregator()) 