"""
Intent Manager - Meeting Intent Capture and Context Management

Captures meeting intents through natural language and follows up with
3 essential context questions for meeting orchestration.
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class IntentStatus(Enum):
    """Meeting intent lifecycle status"""
    CAPTURED = "captured"          # Initial intent detected
    CONTEXT_GATHERING = "context_gathering"  # Asking context questions
    READY = "ready"               # Ready for execution
    SCHEDULED = "scheduled"       # Meeting scheduled
    COMPLETED = "completed"       # Meeting completed
    CANCELLED = "cancelled"       # Intent cancelled


class ContextQuestion(Enum):
    """3 essential context questions for meeting orchestration"""
    WHO = "who"        # Who should attend?
    WHEN = "when"      # When should it happen?
    PURPOSE = "purpose"  # What's the specific purpose/agenda?


@dataclass
class MeetingIntent:
    """Meeting intent with context data"""
    intent_id: str
    user_id: str
    raw_text: str
    detected_at: datetime
    status: IntentStatus = IntentStatus.CAPTURED
    
    # Context answers
    context_answers: Dict[ContextQuestion, str] = field(default_factory=dict)
    confidence_score: float = 0.0
    
    # Extracted entities
    participants: List[str] = field(default_factory=list)
    proposed_time: Optional[datetime] = None
    duration: Optional[int] = None  # minutes
    purpose: Optional[str] = None
    platform: Optional[str] = None
    
    # Metadata
    updated_at: datetime = field(default_factory=datetime.now)
    processing_notes: List[str] = field(default_factory=list)


class IntentManager:
    """
    Manages meeting intent capture and context gathering workflow.
    
    Follows 3-question pattern:
    1. WHO should attend?
    2. WHEN should it happen?
    3. PURPOSE - what's the specific agenda?
    """
    
    def __init__(self):
        self.intents: Dict[str, MeetingIntent] = {}
        self.context_handlers = []
        self.intent_keywords = [
            "meeting", "call", "chat", "sync", "standup",
            "discuss", "review", "brainstorm", "catch up",
            "demo", "presentation", "interview"
        ]
    
    async def capture_intent(self, user_id: str, message: str) -> Optional[MeetingIntent]:
        """
        Analyze message for meeting intent and create MeetingIntent if detected.
        
        Args:
            user_id: User who expressed the intent
            message: Natural language message
            
        Returns:
            MeetingIntent if detected, None otherwise
        """
        try:
            # Detect if message contains meeting intent
            has_intent = await self._detect_meeting_intent(message)
            if not has_intent:
                return None
            
            # Create intent object
            intent_id = str(uuid.uuid4())
            intent = MeetingIntent(
                intent_id=intent_id,
                user_id=user_id,
                raw_text=message,
                detected_at=datetime.now(),
                confidence_score=await self._calculate_confidence(message)
            )
            
            # Extract initial entities
            await self._extract_entities(intent)
            
            # Store intent
            self.intents[intent_id] = intent
            
            # Start context gathering if not complete
            await self._initiate_context_gathering(intent)
            
            logger.info(f"Intent captured: {intent_id} from {user_id}")
            return intent
            
        except Exception as e:
            logger.error(f"Error capturing intent: {e}")
            return None
    
    async def process_context_response(self, intent_id: str, response: str) -> Dict[str, Any]:
        """
        Process user response to context question.
        
        Args:
            intent_id: Meeting intent ID
            response: User's response
            
        Returns:
            Status update with next question or completion
        """
        if intent_id not in self.intents:
            return {"error": "Intent not found"}
        
        intent = self.intents[intent_id]
        
        try:
            # Determine which context question this answers
            next_question = await self._determine_context_question(intent, response)
            
            if next_question:
                # Store the response and ask next question
                question_type = await self._get_current_question_type(intent)
                if question_type:
                    intent.context_answers[question_type] = response
                    await self._extract_context_entities(intent, question_type, response)
                
                return {
                    "status": "needs_context",
                    "next_question": next_question,
                    "question_type": await self._get_next_question_type(intent)
                }
            else:
                # All context gathered
                await self._complete_context_gathering(intent)
                return {
                    "status": "ready",
                    "message": "Intent ready for scheduling",
                    "intent": intent
                }
                
        except Exception as e:
            logger.error(f"Error processing context response: {e}")
            return {"error": str(e)}
    
    async def get_intent(self, intent_id: str) -> Optional[MeetingIntent]:
        """Retrieve intent by ID"""
        return self.intents.get(intent_id)
    
    async def get_user_intents(self, user_id: str, status: Optional[IntentStatus] = None) -> List[MeetingIntent]:
        """Get all intents for a user, optionally filtered by status"""
        intents = [intent for intent in self.intents.values() if intent.user_id == user_id]
        
        if status:
            intents = [intent for intent in intents if intent.status == status]
        
        return sorted(intents, key=lambda x: x.detected_at, reverse=True)
    
    async def update_intent_status(self, intent_id: str, status: IntentStatus, note: str = None) -> bool:
        """Update intent status with optional note"""
        if intent_id not in self.intents:
            return False
        
        intent = self.intents[intent_id]
        intent.status = status
        intent.updated_at = datetime.now()
        
        if note:
            intent.processing_notes.append(f"{datetime.now()}: {note}")
        
        logger.info(f"Intent {intent_id} status updated to {status}")
        return True
    
    async def get_ready_intents(self) -> List[MeetingIntent]:
        """Get all intents ready for scheduling"""
        return [intent for intent in self.intents.values() if intent.status == IntentStatus.READY]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get intent management statistics"""
        total = len(self.intents)
        by_status = {}
        
        for status in IntentStatus:
            count = len([i for i in self.intents.values() if i.status == status])
            by_status[status.value] = count
        
        avg_confidence = 0.0
        if self.intents:
            avg_confidence = sum(i.confidence_score for i in self.intents.values()) / total
        
        return {
            "total_intents": total,
            "by_status": by_status,
            "average_confidence": round(avg_confidence, 2),
            "ready_for_scheduling": by_status.get("ready", 0)
        }
    
    # Private methods
    
    async def _detect_meeting_intent(self, message: str) -> bool:
        """Detect if message contains meeting intent using keywords"""
        message_lower = message.lower()
        
        # Check for meeting keywords
        has_keywords = any(keyword in message_lower for keyword in self.intent_keywords)
        
        # Check for action words + time/people indicators
        action_words = ["let's", "can we", "should we", "want to", "need to", "schedule"]
        time_indicators = ["today", "tomorrow", "next week", "monday", "afternoon"]
        people_indicators = ["with", "team", "@", "everyone", "us"]
        
        has_action = any(action in message_lower for action in action_words)
        has_time = any(time in message_lower for time in time_indicators)
        has_people = any(people in message_lower for people in people_indicators)
        
        return has_keywords or (has_action and (has_time or has_people))
    
    async def _calculate_confidence(self, message: str) -> float:
        """Calculate confidence score for meeting intent detection"""
        score = 0.0
        message_lower = message.lower()
        
        # Keyword matching
        keyword_matches = sum(1 for keyword in self.intent_keywords if keyword in message_lower)
        score += min(keyword_matches * 0.3, 0.6)
        
        # Specific patterns
        if "let's schedule" in message_lower or "can we meet" in message_lower:
            score += 0.4
        
        # Time mentions
        if any(time in message_lower for time in ["today", "tomorrow", "next", "at", "pm", "am"]):
            score += 0.2
        
        return min(score, 1.0)
    
    async def _extract_entities(self, intent: MeetingIntent) -> None:
        """Extract initial entities from raw text"""
        text = intent.raw_text.lower()
        
        # Extract potential participants (mentions)
        if "@" in text:
            mentions = [word for word in text.split() if word.startswith("@")]
            intent.participants.extend([mention[1:] for mention in mentions])
        
        # Extract duration hints
        if "hour" in text:
            intent.duration = 60
        elif "30 min" in text or "half hour" in text:
            intent.duration = 30
        elif "15 min" in text:
            intent.duration = 15
        
        # Extract platform hints
        platforms = ["zoom", "teams", "discord", "slack", "whatsapp"]
        for platform in platforms:
            if platform in text:
                intent.platform = platform
                break
    
    async def _initiate_context_gathering(self, intent: MeetingIntent) -> None:
        """Start the 3-question context gathering process"""
        intent.status = IntentStatus.CONTEXT_GATHERING
        
        # Notify context handlers about new intent needing context
        for handler in self.context_handlers:
            try:
                await handler(intent, await self._get_first_context_question(intent))
            except Exception as e:
                logger.error(f"Error in context handler: {e}")
    
    async def _get_first_context_question(self, intent: MeetingIntent) -> str:
        """Get the first context question based on what's already known"""
        # Start with WHO if no participants identified
        if not intent.participants:
            return "Who should attend this meeting? (You can mention specific people or roles)"
        
        # Then WHEN if no time suggested
        if not intent.proposed_time:
            return "When would you like to schedule this? (e.g., 'tomorrow at 2pm', 'next Monday')"
        
        # Finally PURPOSE if not clear
        if not intent.purpose:
            return "What's the main purpose or agenda for this meeting?"
        
        # All context may already be present
        return None
    
    async def _determine_context_question(self, intent: MeetingIntent, response: str) -> Optional[str]:
        """Determine next context question based on current state"""
        # Check what context is still needed
        needed_context = []
        
        if not intent.context_answers.get(ContextQuestion.WHO) and not intent.participants:
            needed_context.append((ContextQuestion.WHO, "Who should attend this meeting?"))
        
        if not intent.context_answers.get(ContextQuestion.WHEN) and not intent.proposed_time:
            needed_context.append((ContextQuestion.WHEN, "When would you like to schedule this?"))
        
        if not intent.context_answers.get(ContextQuestion.PURPOSE) and not intent.purpose:
            needed_context.append((ContextQuestion.PURPOSE, "What's the main purpose or agenda?"))
        
        if needed_context:
            return needed_context[0][1]
        
        return None
    
    async def _get_current_question_type(self, intent: MeetingIntent) -> Optional[ContextQuestion]:
        """Determine which question type we're currently asking"""
        if not intent.context_answers.get(ContextQuestion.WHO):
            return ContextQuestion.WHO
        elif not intent.context_answers.get(ContextQuestion.WHEN):
            return ContextQuestion.WHEN
        elif not intent.context_answers.get(ContextQuestion.PURPOSE):
            return ContextQuestion.PURPOSE
        return None
    
    async def _get_next_question_type(self, intent: MeetingIntent) -> Optional[ContextQuestion]:
        """Get the next question type that needs to be asked"""
        return await self._get_current_question_type(intent)
    
    async def _extract_context_entities(self, intent: MeetingIntent, question_type: ContextQuestion, response: str) -> None:
        """Extract entities from context responses"""
        if question_type == ContextQuestion.WHO:
            # Extract participants from WHO response
            response_lower = response.lower()
            if "@" in response:
                mentions = [word[1:] for word in response.split() if word.startswith("@")]
                intent.participants.extend(mentions)
            
            # Simple name detection (very basic)
            names = [word for word in response.split() if word.istitle() and len(word) > 2]
            intent.participants.extend(names)
        
        elif question_type == ContextQuestion.WHEN:
            # Basic time extraction (would need proper NLP in production)
            intent.proposed_time = datetime.now() + timedelta(days=1)  # Default tomorrow
            
        elif question_type == ContextQuestion.PURPOSE:
            intent.purpose = response
    
    async def _complete_context_gathering(self, intent: MeetingIntent) -> None:
        """Mark context gathering as complete and intent as ready"""
        intent.status = IntentStatus.READY
        intent.updated_at = datetime.now()
        intent.processing_notes.append(f"{datetime.now()}: Context gathering completed")
        
        logger.info(f"Intent {intent.intent_id} ready for scheduling")
    
    async def add_context_handler(self, handler) -> None:
        """Add handler for context gathering events"""
        self.context_handlers.append(handler)


# Demo/Testing utilities
if __name__ == "__main__":
    async def demo():
        print("🎯 Intent Manager Demo")
        print("=" * 50)
        
        manager = IntentManager()
        
        # Demo intent detection
        test_messages = [
            "Let's schedule a team meeting for tomorrow",
            "Can we have a quick sync with the design team?",
            "I want to review the project with @alice and @bob",
            "This is just a regular message",  # Should not detect intent
            "Need to brainstorm ideas for the campaign"
        ]
        
        for msg in test_messages:
            print(f"\nMessage: '{msg}'")
            intent = await manager.capture_intent("demo_user", msg)
            if intent:
                print(f"✅ Intent detected (confidence: {intent.confidence_score:.2f})")
                print(f"   Status: {intent.status}")
                print(f"   Participants: {intent.participants}")
            else:
                print("❌ No intent detected")
        
        # Show statistics
        stats = await manager.get_statistics()
        print(f"\n📊 Statistics:")
        print(f"   Total intents: {stats['total_intents']}")
        print(f"   Average confidence: {stats['average_confidence']}")
        print(f"   Ready for scheduling: {stats['ready_for_scheduling']}")
        
        print("\n✨ Demo completed!")
    
    asyncio.run(demo()) 