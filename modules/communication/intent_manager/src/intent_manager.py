"""
WSP 54: Intent Manager Implementation
=====================================

Meeting intent capture, storage, and retrieval with structured context.
Extracted from auto_meeting_orchestrator PoC for strategic decomposition.

WSP Integration:
- WSP 3: Communication domain for meeting intent coordination
- WSP 11: Clean interface definition for modular consumption
- WSP 49: Standard module structure compliance
- WSP 60: Module memory architecture for intent persistence
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

# WRE Integration
try:
    from ...wre_core.src.utils.wre_logger import wre_log
except ImportError:
    def wre_log(msg: str, level: str = "INFO"):
        print(f"[{level}] {msg}")

logger = logging.getLogger(__name__)


class Priority(Enum):
    """Meeting priority levels with scoring for urgency calculation"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    
    def get_urgency_score(self) -> int:
        """Get numeric urgency score for prioritization"""
        priority_scores = {
            Priority.LOW: 1,
            Priority.MEDIUM: 2,
            Priority.HIGH: 3,
            Priority.URGENT: 4
        }
        return priority_scores[self]


class IntentStatus(Enum):
    """Intent lifecycle status"""
    PENDING = "pending"
    MONITORING = "monitoring"
    TRIGGERED = "triggered"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"
    COMPLETED = "completed"


@dataclass
class MeetingContext:
    """Structured meeting context for enhanced intent clarity"""
    purpose: str
    expected_outcome: str
    duration_minutes: int
    priority: Priority
    preferred_time_range: Optional[Tuple[datetime, datetime]] = None
    agenda_items: Optional[List[str]] = None
    meeting_type: str = "general"  # general, brainstorm, decision, update
    
    def calculate_urgency_factor(self) -> float:
        """Calculate urgency based on context"""
        base_urgency = self.priority.get_urgency_score() / 4.0
        
        # Increase urgency for shorter meetings (assume more focused)
        if self.duration_minutes <= 15:
            base_urgency *= 1.2
        elif self.duration_minutes <= 30:
            base_urgency *= 1.1
            
        # Increase urgency for decision meetings
        if self.meeting_type == "decision":
            base_urgency *= 1.15
            
        return min(base_urgency, 1.0)


@dataclass
class MeetingIntent:
    """Structured meeting intent with context and tracking"""
    intent_id: str
    requester_id: str
    recipient_id: str
    context: MeetingContext
    created_at: datetime
    status: IntentStatus = IntentStatus.PENDING
    expires_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    attempts: int = 0
    
    def __post_init__(self):
        if self.expires_at is None:
            # Default expiration: 24 hours for urgent, 72 hours for others
            hours = 24 if self.context.priority == Priority.URGENT else 72
            self.expires_at = self.created_at + timedelta(hours=hours)
    
    def is_expired(self) -> bool:
        """Check if intent has expired"""
        return datetime.now() > self.expires_at
    
    def get_priority_score(self) -> float:
        """Get weighted priority score including urgency factors"""
        base_score = self.context.priority.get_urgency_score()
        urgency_factor = self.context.calculate_urgency_factor()
        
        # Time decay factor - more urgent as expiration approaches
        time_remaining = (self.expires_at - datetime.now()).total_seconds()
        total_duration = (self.expires_at - self.created_at).total_seconds()
        time_pressure = 1.0 + (1.0 - time_remaining / total_duration) * 0.5
        
        return base_score * urgency_factor * time_pressure


class IntentManager:
    """
    Meeting intent capture, storage, and retrieval engine.
    
    Manages the full lifecycle of meeting intents with structured context,
    priority scoring, and persistent storage using WSP 60 memory architecture.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("memory/intent_manager")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.active_intents: Dict[str, MeetingIntent] = {}
        self.intent_history: List[MeetingIntent] = []
        self.intent_counter = 0
        
        # Load existing intents from storage
        self._load_intents_from_storage()
        
        wre_log("IntentManager initialized with persistent storage")
    
    async def create_intent(
        self,
        requester_id: str,
        recipient_id: str,
        context: MeetingContext
    ) -> str:
        """
        Create a new meeting intent with structured context.
        
        Args:
            requester_id: User requesting the meeting
            recipient_id: Target meeting participant
            context: Structured meeting context and details
            
        Returns:
            Intent ID for tracking and reference
        """
        self.intent_counter += 1
        intent_id = f"intent_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.intent_counter}"
        
        intent = MeetingIntent(
            intent_id=intent_id,
            requester_id=requester_id,
            recipient_id=recipient_id,
            context=context,
            created_at=datetime.now()
        )
        
        self.active_intents[intent_id] = intent
        
        # Persist to storage
        await self._persist_intent(intent)
        
        wre_log(f"Meeting intent created: {intent_id}")
        wre_log(f"Purpose: {context.purpose}")
        wre_log(f"Priority: {context.priority.name}")
        wre_log(f"Duration: {context.duration_minutes} minutes")
        
        return intent_id
    
    async def get_pending_intents(self, recipient_id: str) -> List[MeetingIntent]:
        """
        Get all pending intents for a recipient.
        
        Args:
            recipient_id: User to get intents for
            
        Returns:
            List of pending MeetingIntents sorted by priority
        """
        pending_intents = [
            intent for intent in self.active_intents.values()
            if intent.recipient_id == recipient_id 
            and intent.status == IntentStatus.PENDING
            and not intent.is_expired()
        ]
        
        # Sort by priority score (highest first)
        pending_intents.sort(key=lambda i: i.get_priority_score(), reverse=True)
        
        wre_log(f"Retrieved {len(pending_intents)} pending intents for {recipient_id}")
        return pending_intents
    
    async def get_active_intents(self, user_id: str) -> List[MeetingIntent]:
        """
        Get all active intents involving a user (as requester or recipient).
        
        Args:
            user_id: User to get intents for
            
        Returns:
            List of active MeetingIntents
        """
        active_intents = [
            intent for intent in self.active_intents.values()
            if (intent.requester_id == user_id or intent.recipient_id == user_id)
            and intent.status in [IntentStatus.PENDING, IntentStatus.MONITORING, IntentStatus.TRIGGERED]
            and not intent.is_expired()
        ]
        
        return active_intents
    
    async def mark_intent_processed(self, intent_id: str, outcome: str, notes: Optional[str] = None):
        """
        Mark an intent as processed with outcome.
        
        Args:
            intent_id: Intent to mark as processed
            outcome: Result outcome (accepted, declined, completed, etc.)
            notes: Optional processing notes
        """
        if intent_id not in self.active_intents:
            raise ValueError(f"Intent {intent_id} not found")
        
        intent = self.active_intents[intent_id]
        
        # Update status based on outcome
        status_mapping = {
            "accepted": IntentStatus.ACCEPTED,
            "declined": IntentStatus.DECLINED,
            "completed": IntentStatus.COMPLETED,
            "expired": IntentStatus.EXPIRED
        }
        
        intent.status = status_mapping.get(outcome, IntentStatus.COMPLETED)
        intent.last_updated = datetime.now()
        
        # Move to history if final status
        if intent.status in [IntentStatus.ACCEPTED, IntentStatus.DECLINED, IntentStatus.COMPLETED, IntentStatus.EXPIRED]:
            self.intent_history.append(intent)
            del self.active_intents[intent_id]
        
        # Persist changes
        await self._persist_intent(intent)
        
        wre_log(f"Intent {intent_id} marked as {outcome}")
    
    async def update_intent_status(self, intent_id: str, status: IntentStatus):
        """Update intent status during lifecycle management"""
        if intent_id in self.active_intents:
            self.active_intents[intent_id].status = status
            self.active_intents[intent_id].last_updated = datetime.now()
            await self._persist_intent(self.active_intents[intent_id])
    
    async def cleanup_expired_intents(self):
        """Clean up expired intents and move to history"""
        expired_intents = []
        
        for intent_id, intent in list(self.active_intents.items()):
            if intent.is_expired():
                intent.status = IntentStatus.EXPIRED
                self.intent_history.append(intent)
                expired_intents.append(intent_id)
                del self.active_intents[intent_id]
        
        if expired_intents:
            wre_log(f"Cleaned up {len(expired_intents)} expired intents")
        
        return len(expired_intents)
    
    def get_intent_by_id(self, intent_id: str) -> Optional[MeetingIntent]:
        """Get intent by ID from active intents or history"""
        if intent_id in self.active_intents:
            return self.active_intents[intent_id]
        
        for intent in self.intent_history:
            if intent.intent_id == intent_id:
                return intent
        
        return None
    
    # Private Methods
    
    async def _persist_intent(self, intent: MeetingIntent):
        """Persist intent to storage using WSP 60 memory architecture"""
        try:
            intent_file = self.storage_path / f"{intent.intent_id}.json"
            
            # Convert to serializable format
            intent_data = {
                "intent_id": intent.intent_id,
                "requester_id": intent.requester_id,
                "recipient_id": intent.recipient_id,
                "context": asdict(intent.context),
                "created_at": intent.created_at.isoformat(),
                "status": intent.status.value,
                "expires_at": intent.expires_at.isoformat() if intent.expires_at else None,
                "last_updated": intent.last_updated.isoformat() if intent.last_updated else None,
                "attempts": intent.attempts
            }
            
            with open(intent_file, 'w') as f:
                json.dump(intent_data, f, indent=2)
                
        except Exception as e:
            wre_log(f"Failed to persist intent {intent.intent_id}: {e}", "ERROR")
    
    def _load_intents_from_storage(self):
        """Load existing intents from storage on initialization"""
        try:
            for intent_file in self.storage_path.glob("*.json"):
                with open(intent_file, 'r') as f:
                    intent_data = json.load(f)
                
                # Reconstruct intent object
                context_data = intent_data["context"]
                context_data["priority"] = Priority(context_data["priority"])
                
                if context_data.get("preferred_time_range"):
                    time_range = context_data["preferred_time_range"]
                    context_data["preferred_time_range"] = (
                        datetime.fromisoformat(time_range[0]),
                        datetime.fromisoformat(time_range[1])
                    )
                
                context = MeetingContext(**context_data)
                
                intent = MeetingIntent(
                    intent_id=intent_data["intent_id"],
                    requester_id=intent_data["requester_id"],
                    recipient_id=intent_data["recipient_id"],
                    context=context,
                    created_at=datetime.fromisoformat(intent_data["created_at"]),
                    status=IntentStatus(intent_data["status"]),
                    expires_at=datetime.fromisoformat(intent_data["expires_at"]) if intent_data.get("expires_at") else None,
                    last_updated=datetime.fromisoformat(intent_data["last_updated"]) if intent_data.get("last_updated") else None,
                    attempts=intent_data.get("attempts", 0)
                )
                
                # Load into appropriate collection based on status
                if intent.status in [IntentStatus.PENDING, IntentStatus.MONITORING, IntentStatus.TRIGGERED]:
                    self.active_intents[intent.intent_id] = intent
                else:
                    self.intent_history.append(intent)
                    
                self.intent_counter = max(self.intent_counter, int(intent.intent_id.split('_')[-1]))
                    
        except Exception as e:
            wre_log(f"Error loading intents from storage: {e}", "WARNING") 