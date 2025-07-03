"""
Autonomous Meeting Orchestrator (AMO) - Core Module

Handles cross-platform meeting orchestration with real-time presence detection,
priority scoring, and automatic channel selection.

Current Phase: PoC (v0.0.x)
- Focus: Minimal proof of concept for presence aggregation and auto-handshake
- Success Criterion: Detect presence and trigger acceptance prompts
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PresenceStatus(Enum):
    """User presence status across platforms"""
    ONLINE = "online"
    OFFLINE = "offline"
    IDLE = "idle"
    BUSY = "busy"
    UNKNOWN = "unknown"


class Priority(Enum):
    """Meeting priority levels (000-222 scale)"""
    LOW = 1      # 000-001
    MEDIUM = 5   # 010-111
    HIGH = 8     # 200-222
    URGENT = 10  # Emergency


@dataclass
class MeetingIntent:
    """Meeting request structure"""
    requester_id: str
    recipient_id: str
    purpose: str
    expected_outcome: str
    duration_minutes: int
    priority: Priority
    preferred_time_range: Optional[Tuple[datetime, datetime]] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class UnifiedAvailabilityProfile:
    """Aggregated presence across all platforms"""
    user_id: str
    platforms: Dict[str, PresenceStatus]
    overall_status: PresenceStatus
    last_updated: datetime
    confidence_score: float  # 0.0-1.0


class MeetingOrchestrator:
    """
    Main orchestrator for autonomous meeting coordination
    
    PoC Implementation:
    - Simulated presence detection
    - Basic handshake protocol
    - Local storage for intents
    """
    
    def __init__(self):
        self.active_intents: List[MeetingIntent] = []
        self.user_profiles: Dict[str, UnifiedAvailabilityProfile] = {}
        self.meeting_history: List[Dict] = []
        
    async def create_meeting_intent(
        self,
        requester_id: str,
        recipient_id: str,
        purpose: str,
        expected_outcome: str,
        duration_minutes: int,
        priority: Priority,
        preferred_time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> str:
        """
        Step 1: Intent Declaration
        Creates a new meeting request with structured context
        """
        intent = MeetingIntent(
            requester_id=requester_id,
            recipient_id=recipient_id,
            purpose=purpose,
            expected_outcome=expected_outcome,
            duration_minutes=duration_minutes,
            priority=priority,
            preferred_time_range=preferred_time_range
        )
        
        self.active_intents.append(intent)
        intent_id = f"intent_{len(self.active_intents)}"
        
        logger.info(f"Meeting intent created: {intent_id}")
        logger.info(f"Purpose: {purpose}")
        logger.info(f"Expected outcome: {expected_outcome}")
        logger.info(f"Duration: {duration_minutes} minutes")
        logger.info(f"Priority: {priority.name}")
        
        # Trigger presence monitoring for both parties
        await self._monitor_mutual_availability(intent)
        
        return intent_id
    
    async def update_presence(
        self,
        user_id: str,
        platform: str,
        status: PresenceStatus,
        confidence: float = 1.0
    ):
        """
        Step 2: Presence Aggregation
        Updates user presence for a specific platform
        """
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UnifiedAvailabilityProfile(
                user_id=user_id,
                platforms={},
                overall_status=PresenceStatus.UNKNOWN,
                last_updated=datetime.now(),
                confidence_score=0.0
            )
        
        profile = self.user_profiles[user_id]
        profile.platforms[platform] = status
        profile.last_updated = datetime.now()
        
        # Calculate overall status and confidence
        profile.overall_status = self._calculate_overall_status(profile.platforms)
        profile.confidence_score = self._calculate_confidence(profile.platforms, confidence)
        
        logger.info(f"Presence updated: {user_id} on {platform} = {status.value}")
        
        # Check if this triggers any meeting opportunities
        await self._check_meeting_opportunities()
    
    def _calculate_overall_status(self, platforms: Dict[str, PresenceStatus]) -> PresenceStatus:
        """Calculate unified presence from multiple platform signals"""
        if not platforms:
            return PresenceStatus.UNKNOWN
            
        # Priority order: ONLINE > IDLE > BUSY > OFFLINE > UNKNOWN
        status_priority = {
            PresenceStatus.ONLINE: 5,
            PresenceStatus.IDLE: 4,
            PresenceStatus.BUSY: 3,
            PresenceStatus.OFFLINE: 2,
            PresenceStatus.UNKNOWN: 1
        }
        
        highest_status = max(platforms.values(), key=lambda s: status_priority[s])
        return highest_status
    
    def _calculate_confidence(self, platforms: Dict[str, PresenceStatus], base_confidence: float) -> float:
        """Calculate confidence score based on number of signals and recency"""
        platform_count = len(platforms)
        confidence = base_confidence * min(1.0, platform_count / 3.0)  # Max confidence with 3+ platforms
        return round(confidence, 2)
    
    async def _monitor_mutual_availability(self, intent: MeetingIntent):
        """Monitor both parties for mutual availability"""
        logger.info(f"Monitoring availability for {intent.requester_id} and {intent.recipient_id}")
        # In PoC: This would hook into real platform APIs
        # For now, we'll simulate this check
    
    async def _check_meeting_opportunities(self):
        """
        Step 3-4: Priority Scoring & Service Selection
        Check if any active intents can be fulfilled based on current availability
        """
        for intent in self.active_intents:
            requester_available = self._is_user_available(intent.requester_id)
            recipient_available = self._is_user_available(intent.recipient_id)
            
            if requester_available and recipient_available:
                logger.info(f"Mutual availability detected for {intent.requester_id} and {intent.recipient_id}")
                await self._trigger_meeting_prompt(intent)
    
    def _is_user_available(self, user_id: str) -> bool:
        """Check if user is currently available for meetings"""
        if user_id not in self.user_profiles:
            return False
            
        profile = self.user_profiles[user_id]
        return profile.overall_status in [PresenceStatus.ONLINE, PresenceStatus.IDLE]
    
    async def _trigger_meeting_prompt(self, intent: MeetingIntent):
        """
        Step 5: Consent & Reminder
        Send meeting prompt to recipient with full context
        """
        prompt = f"""
🤝 Meeting Request Available Now

{intent.requester_id} is available to meet about:
• Purpose: {intent.purpose}
• Expected outcome: {intent.expected_outcome}
• Duration: {intent.duration_minutes} minutes
• Priority: {intent.priority.name}

Both parties are currently online. Accept this meeting?
        """.strip()
        
        logger.info("Meeting prompt triggered:")
        logger.info(prompt)
        
        # In real implementation, this would send to the recipient via their preferred channel
        # For PoC, we'll simulate acceptance after a brief delay
        await asyncio.sleep(2)
        await self._simulate_response(intent, accepted=True)
    
    async def _simulate_response(self, intent: MeetingIntent, accepted: bool):
        """Simulate recipient response for PoC testing"""
        if accepted:
            logger.info(f"Meeting accepted! Launching session...")
            await self._launch_meeting_session(intent)
        else:
            logger.info(f"Meeting declined. Will reschedule.")
            # In real implementation: trigger auto-rescheduling
    
    async def _launch_meeting_session(self, intent: MeetingIntent):
        """
        Step 6: Handshake + Session Launch
        Launch the meeting on the optimal platform
        """
        # Determine best platform based on both users' active platforms
        optimal_platform = self._select_optimal_platform(intent.requester_id, intent.recipient_id)
        
        meeting_session = {
            "session_id": f"session_{datetime.now().isoformat()}",
            "intent": intent,
            "platform": optimal_platform,
            "started_at": datetime.now(),
            "status": "active"
        }
        
        self.meeting_history.append(meeting_session)
        
        logger.info(f"Meeting session launched on {optimal_platform}")
        logger.info(f"Session ID: {meeting_session['session_id']}")
        
        # Remove from active intents
        if intent in self.active_intents:
            self.active_intents.remove(intent)
        
        # In real implementation: Create calendar entries, launch platform-specific meeting
        return meeting_session["session_id"]
    
    def _select_optimal_platform(self, user1_id: str, user2_id: str) -> str:
        """Select the best platform for the meeting based on user presence"""
        # PoC logic: Simple platform selection
        platforms = ["discord", "zoom", "whatsapp"]
        
        # In real implementation: Check both users' active platforms and preferences
        # For PoC: Return the first available option
        return "discord"  # Simplified for PoC
    
    def get_active_intents(self) -> List[MeetingIntent]:
        """Get all active meeting intents"""
        return self.active_intents.copy()
    
    def get_user_profile(self, user_id: str) -> Optional[UnifiedAvailabilityProfile]:
        """Get user's current availability profile"""
        return self.user_profiles.get(user_id)
    
    def get_meeting_history(self) -> List[Dict]:
        """Get history of completed meetings"""
        return self.meeting_history.copy()


# PoC Test Functions
async def demo_amo_poc():
    """
    Demonstrate PoC functionality:
    - Create meeting intent
    - Simulate presence updates
    - Trigger automatic meeting coordination
    """
    amo = MeetingOrchestrator()
    
    print("=== AMO PoC Demo ===")
    
    # Step 1: Create meeting intent
    intent_id = await amo.create_meeting_intent(
        requester_id="alice",
        recipient_id="bob",
        purpose="Brainstorm partnership idea",
        expected_outcome="Agreement on next steps",
        duration_minutes=30,
        priority=Priority.HIGH
    )
    
    print(f"\n✅ Meeting intent created: {intent_id}")
    
    # Step 2: Simulate presence updates
    print("\n📡 Simulating presence updates...")
    await amo.update_presence("alice", "discord", PresenceStatus.ONLINE)
    await amo.update_presence("alice", "whatsapp", PresenceStatus.ONLINE)
    await amo.update_presence("bob", "discord", PresenceStatus.IDLE)
    await amo.update_presence("bob", "zoom", PresenceStatus.ONLINE)
    
    # Allow time for meeting orchestration
    await asyncio.sleep(1)
    
    print("\n📊 Final Status:")
    print(f"Active intents: {len(amo.get_active_intents())}")
    print(f"Completed meetings: {len(amo.get_meeting_history())}")
    
    return amo


if __name__ == "__main__":
    # Run PoC demo
    asyncio.run(demo_amo_poc()) 