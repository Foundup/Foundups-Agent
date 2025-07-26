"""
Intent Manager Module
WSP Protocol: WSP 54 (Agent Coordination), WSP 3 (Enterprise Domain Distribution)

Manages meeting intents with structured context capture, storage, and retrieval.
Extracted from monolithic Auto Meeting Orchestrator for modular architecture.

Part of Meeting Orchestration Block strategic decomposition.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)

class Priority(Enum):
    """Meeting priority levels (000-222 scale integration with WSP 25/44)"""
    LOW = 1      # 000-001 - Basic coordination needs
    MEDIUM = 5   # 010-111 - Standard business importance  
    HIGH = 8     # 200-222 - Critical business coordination
    URGENT = 10  # Emergency - Immediate response required

class IntentStatus(Enum):
    """Intent processing status"""
    PENDING = "pending"
    MONITORING = "monitoring"  # Actively monitoring for mutual availability
    PROMPTED = "prompted"      # Consent prompt sent
    ACCEPTED = "accepted"      # Recipient accepted
    DECLINED = "declined"      # Recipient declined
    EXPIRED = "expired"        # Intent timed out
    COMPLETED = "completed"    # Meeting successfully launched

@dataclass
class MeetingContext:
    """Rich context for meeting intentions"""
    purpose: str
    expected_outcome: str
    duration_minutes: int
    agenda_items: List[str] = field(default_factory=list)
    background_info: Optional[str] = None
    preparation_required: bool = False
    urgency_reason: Optional[str] = None

@dataclass
class MeetingIntent:
    """Structured meeting request with rich context"""
    intent_id: str
    requester_id: str
    recipient_id: str
    context: MeetingContext
    priority: Priority
    status: IntentStatus = IntentStatus.PENDING
    preferred_time_range: Optional[Tuple[datetime, datetime]] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    response_deadline: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if self.expires_at is None:
            # Default: intents expire after 24 hours
            self.expires_at = self.created_at + timedelta(hours=24)
        
        if self.response_deadline is None:
            # Default: expect response within 2 hours for high priority
            hours_to_respond = 1 if self.priority == Priority.URGENT else 2
            self.response_deadline = self.created_at + timedelta(hours=hours_to_respond)

    def is_expired(self) -> bool:
        """Check if intent has expired"""
        return datetime.now() > self.expires_at

    def is_response_overdue(self) -> bool:
        """Check if response deadline has passed"""
        return datetime.now() > self.response_deadline

    def update_status(self, new_status: IntentStatus, metadata: Optional[Dict] = None):
        """Update intent status with optional metadata"""
        self.status = new_status
        self.last_updated = datetime.now()
        if metadata:
            self.metadata.update(metadata)

class IntentManager:
    """
    Manages meeting intents with structured context and lifecycle tracking
    
    Responsibilities:
    - Create and validate meeting intents
    - Track intent lifecycle and status
    - Provide intent queries and filtering
    - Handle intent expiration and cleanup
    - Integration with other AMO modules
    """
    
    def __init__(self):
        self.active_intents: Dict[str, MeetingIntent] = {}
        self.intent_history: List[MeetingIntent] = []
        self.event_callbacks: Dict[str, List[Callable]] = {
            'intent_created': [],
            'intent_updated': [],
            'intent_expired': [],
            'intent_completed': []
        }
        
        logger.info("🎯 Intent Manager initialized")

    async def create_intent(
        self,
        requester_id: str,
        recipient_id: str,
        context: MeetingContext,
        priority: Priority,
        preferred_time_range: Optional[Tuple[datetime, datetime]] = None,
        custom_expiry: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Create a new meeting intent with structured context
        
        Args:
            requester_id: ID of person requesting the meeting
            recipient_id: ID of person being requested to meet
            context: Rich meeting context with purpose, outcome, etc.
            priority: Meeting priority level (WSP 25/44 integration)
            preferred_time_range: Optional preferred time window
            custom_expiry: Optional custom expiration time
            metadata: Additional metadata for the intent
            
        Returns:
            intent_id: Unique identifier for the created intent
        """
        intent_id = str(uuid.uuid4())
        
        intent = MeetingIntent(
            intent_id=intent_id,
            requester_id=requester_id,
            recipient_id=recipient_id,
            context=context,
            priority=priority,
            preferred_time_range=preferred_time_range,
            expires_at=custom_expiry
        )
        
        if metadata:
            intent.metadata.update(metadata)
        
        self.active_intents[intent_id] = intent
        
        logger.info(f"📝 Meeting intent created: {intent_id}")
        logger.info(f"   Purpose: {context.purpose}")
        logger.info(f"   Expected outcome: {context.expected_outcome}")
        logger.info(f"   Duration: {context.duration_minutes} minutes")
        logger.info(f"   Priority: {priority.name}")
        logger.info(f"   Requester: {requester_id} → Recipient: {recipient_id}")
        
        # Trigger callbacks
        await self._trigger_callbacks('intent_created', intent)
        
        return intent_id

    async def get_intent(self, intent_id: str) -> Optional[MeetingIntent]:
        """Retrieve a specific intent by ID"""
        return self.active_intents.get(intent_id)

    async def get_pending_intents(self, recipient_id: str) -> List[MeetingIntent]:
        """Get all pending intents for a specific recipient"""
        return [
            intent for intent in self.active_intents.values()
            if intent.recipient_id == recipient_id and intent.status == IntentStatus.PENDING
        ]

    async def get_intents_by_requester(self, requester_id: str) -> List[MeetingIntent]:
        """Get all intents created by a specific requester"""
        return [
            intent for intent in self.active_intents.values()
            if intent.requester_id == requester_id
        ]

    async def get_intents_by_priority(self, priority: Priority) -> List[MeetingIntent]:
        """Get all intents with specific priority level"""
        return [
            intent for intent in self.active_intents.values()
            if intent.priority == priority
        ]

    async def get_intents_requiring_attention(self) -> List[MeetingIntent]:
        """Get intents that require immediate attention (overdue responses, high priority)"""
        urgent_intents = []
        
        for intent in self.active_intents.values():
            if (intent.priority == Priority.URGENT or 
                intent.is_response_overdue() or
                (intent.status == IntentStatus.PENDING and intent.priority == Priority.HIGH)):
                urgent_intents.append(intent)
        
        # Sort by priority and creation time
        urgent_intents.sort(key=lambda x: (x.priority.value, x.created_at), reverse=True)
        return urgent_intents

    async def update_intent_status(
        self, 
        intent_id: str, 
        new_status: IntentStatus,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Update the status of an intent
        
        Args:
            intent_id: Intent to update
            new_status: New status to set
            metadata: Optional additional metadata
            
        Returns:
            bool: True if update successful, False if intent not found
        """
        intent = self.active_intents.get(intent_id)
        if not intent:
            logger.warning(f"❌ Attempt to update non-existent intent: {intent_id}")
            return False
        
        old_status = intent.status
        intent.update_status(new_status, metadata)
        
        logger.info(f"📊 Intent status updated: {intent_id}")
        logger.info(f"   {old_status.value} → {new_status.value}")
        
        # If intent is completed or declined, move to history
        if new_status in [IntentStatus.COMPLETED, IntentStatus.DECLINED, IntentStatus.EXPIRED]:
            await self._archive_intent(intent_id)
        
        # Trigger callbacks
        await self._trigger_callbacks('intent_updated', intent)
        
        return True

    async def mark_intent_processed(
        self, 
        intent_id: str, 
        outcome: str,
        session_info: Optional[Dict] = None
    ) -> bool:
        """Mark an intent as processed with outcome information"""
        metadata = {'outcome': outcome}
        if session_info:
            metadata['session_info'] = session_info
            
        if outcome.lower() in ['accepted', 'completed', 'launched']:
            return await self.update_intent_status(intent_id, IntentStatus.COMPLETED, metadata)
        elif outcome.lower() in ['declined', 'rejected']:
            return await self.update_intent_status(intent_id, IntentStatus.DECLINED, metadata)
        else:
            # Generic update with outcome info
            return await self.update_intent_status(intent_id, intent.status, metadata)

    async def expire_old_intents(self) -> List[str]:
        """Check for and expire old intents, returns list of expired intent IDs"""
        expired_ids = []
        
        for intent_id, intent in list(self.active_intents.items()):
            if intent.is_expired():
                await self.update_intent_status(intent_id, IntentStatus.EXPIRED)
                expired_ids.append(intent_id)
                logger.info(f"⏰ Intent expired: {intent_id}")
        
        return expired_ids

    async def get_intent_statistics(self) -> Dict:
        """Get statistics about intent management"""
        active_count = len(self.active_intents)
        history_count = len(self.intent_history)
        
        status_counts = {}
        priority_counts = {}
        
        for intent in self.active_intents.values():
            status_counts[intent.status.value] = status_counts.get(intent.status.value, 0) + 1
            priority_counts[intent.priority.name] = priority_counts.get(intent.priority.name, 0) + 1
        
        return {
            'active_intents': active_count,
            'historical_intents': history_count,
            'status_breakdown': status_counts,
            'priority_breakdown': priority_counts,
            'overdue_responses': len([i for i in self.active_intents.values() if i.is_response_overdue()])
        }

    async def subscribe_to_events(self, event_type: str, callback: Callable):
        """Subscribe to intent events for integration with other modules"""
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type].append(callback)
            logger.info(f"📡 Subscribed to {event_type} events")
        else:
            logger.warning(f"❌ Unknown event type: {event_type}")

    async def _archive_intent(self, intent_id: str):
        """Move completed intent to history"""
        intent = self.active_intents.pop(intent_id, None)
        if intent:
            self.intent_history.append(intent)
            
            # Trigger completion callback
            if intent.status == IntentStatus.COMPLETED:
                await self._trigger_callbacks('intent_completed', intent)
            elif intent.status == IntentStatus.EXPIRED:
                await self._trigger_callbacks('intent_expired', intent)

    async def _trigger_callbacks(self, event_type: str, intent: MeetingIntent):
        """Trigger registered callbacks for intent events"""
        callbacks = self.event_callbacks.get(event_type, [])
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(intent)
                else:
                    callback(intent)
            except Exception as e:
                logger.error(f"❌ Callback error for {event_type}: {e}")

    # Integration methods for other AMO modules
    
    async def get_intents_for_presence_monitoring(self) -> List[MeetingIntent]:
        """Get intents that need presence monitoring"""
        return [
            intent for intent in self.active_intents.values()
            if intent.status in [IntentStatus.PENDING, IntentStatus.MONITORING]
        ]

    async def get_high_priority_intents(self) -> List[MeetingIntent]:
        """Get high and urgent priority intents for priority scorer integration"""
        return [
            intent for intent in self.active_intents.values()
            if intent.priority in [Priority.HIGH, Priority.URGENT]
        ]

    def to_dict(self, intent: MeetingIntent) -> Dict:
        """Convert intent to dictionary for serialization"""
        return {
            'intent_id': intent.intent_id,
            'requester_id': intent.requester_id,
            'recipient_id': intent.recipient_id,
            'context': {
                'purpose': intent.context.purpose,
                'expected_outcome': intent.context.expected_outcome,
                'duration_minutes': intent.context.duration_minutes,
                'agenda_items': intent.context.agenda_items,
                'background_info': intent.context.background_info,
                'preparation_required': intent.context.preparation_required,
                'urgency_reason': intent.context.urgency_reason
            },
            'priority': intent.priority.name,
            'status': intent.status.value,
            'created_at': intent.created_at.isoformat(),
            'last_updated': intent.last_updated.isoformat(),
            'expires_at': intent.expires_at.isoformat() if intent.expires_at else None,
            'metadata': intent.metadata
        }

# Factory function for easy integration
def create_intent_manager() -> IntentManager:
    """Factory function to create Intent Manager instance"""
    return IntentManager()

# Example usage and testing
async def demo_intent_manager():
    """Demonstrate Intent Manager functionality"""
    print("=== Intent Manager Demo ===")
    
    manager = create_intent_manager()
    
    # Create sample meeting context
    context = MeetingContext(
        purpose="Strategic partnership discussion",
        expected_outcome="Agreement on collaboration framework",
        duration_minutes=45,
        agenda_items=["Partnership scope", "Resource allocation", "Timeline"],
        background_info="Follow-up from initial conversation",
        preparation_required=True,
        urgency_reason="Board presentation next week"
    )
    
    # Create intent
    intent_id = await manager.create_intent(
        requester_id="alice",
        recipient_id="bob", 
        context=context,
        priority=Priority.HIGH
    )
    
    print(f"✅ Created intent: {intent_id}")
    
    # Demo various queries
    pending = await manager.get_pending_intents("bob")
    print(f"📋 Pending intents for bob: {len(pending)}")
    
    high_priority = await manager.get_intents_by_priority(Priority.HIGH)
    print(f"🔥 High priority intents: {len(high_priority)}")
    
    # Demo status update
    await manager.update_intent_status(intent_id, IntentStatus.MONITORING)
    
    # Demo statistics
    stats = await manager.get_intent_statistics()
    print(f"📊 Intent statistics: {stats}")
    
    return manager

if __name__ == "__main__":
    asyncio.run(demo_intent_manager()) 