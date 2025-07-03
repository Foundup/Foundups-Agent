"""
ZeroOneZeroTwo - The Unified AI Orchestrator

Acts as Tony Stark's JARVIS for meeting coordination:
- Contextual awareness of all meeting intents and availability
- Natural language interaction (text and future voice)
- Proactive suggestions and notifications  
- Personalized learning and adaptation
- Seamless coordination across all AMO modules

"I am 0102, your meeting orchestration companion."
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Import 0102 components
from .conversation_manager import ConversationManager, Intent, EntityExtraction
from .notification_engine import NotificationEngine, NotificationChannel, Priority
from .session_controller import SessionController, LaunchRequest
from .personality_engine import PersonalityEngine, PersonalityMode, ResponseContext, EmotionalTone
from .learning_engine import LearningEngine
from .memory_core import MemoryCore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResponseType(Enum):
    """Types of responses 0102 can provide"""
    NOTIFICATION = "notification"
    SUGGESTION = "suggestion"
    CONFIRMATION = "confirmation"
    QUESTION = "question"
    ACTION_RESULT = "action_result"
    ERROR = "error"


@dataclass
class UserContext:
    """Current context about the user"""
    user_id: str
    active_sessions: List[str]
    pending_intents: List[str]
    current_availability: Optional[str]
    last_interaction: datetime
    preferences: Dict[str, Any]


@dataclass
class Response:
    """0102's response to user input"""
    response_type: ResponseType
    message: str
    suggested_actions: List[str]
    requires_user_input: bool
    context: Optional[Dict] = None


class ZeroOneZeroTwo:
    """
    The unified AI orchestrator for AMO ecosystem.
    
    Serves as the single point of interaction between users and the
    meeting orchestration system. Provides contextual awareness,
    natural language processing, and proactive assistance.
    """
    
    def __init__(self, personality_mode: PersonalityMode = PersonalityMode.FRIENDLY):
        # Initialize core components
        self.personality_engine = PersonalityEngine(personality_mode)
        self.conversation_manager = ConversationManager()
        self.notification_engine = NotificationEngine()
        self.session_controller = SessionController()
        self.learning_engine = LearningEngine()
        self.memory_core = MemoryCore()
        
        # Internal state
        self.user_contexts: Dict[str, UserContext] = {}
        self.meeting_orchestrator = None  # Will be injected by AMO system
        
        logger.info("0102 Orchestrator initialized - All systems online and ready for intelligent meeting coordination")
        
    async def greet_user(self, user_id: str, is_returning_user: bool = False) -> Response:
        """Initial greeting when user first interacts with 0102"""
        user_context = await self._get_or_create_user_context(user_id)
        
        # Get personalized greeting
        greeting = self.personality_engine.get_greeting_message(
            user_id=user_id,
            is_returning_user=is_returning_user
        )
        
        # Add contextual information
        if user_context.pending_intents:
            context_info = f" You have {len(user_context.pending_intents)} pending meeting intents."
            greeting += context_info
        
        # Record interaction for learning
        await self.learning_engine.record_interaction(
            user_id=user_id,
            interaction_type="greeting",
            context={"is_returning": is_returning_user},
            outcome={"greeted": True}
        )
        
        # Send notification
        await self.notification_engine.send_notification(
            user_id=user_id,
            message=greeting,
            priority=Priority.LOW,
            channels=[NotificationChannel.CONSOLE]
        )
        
        return Response(
            response_type=ResponseType.NOTIFICATION,
            message=greeting,
            suggested_actions=["Create meeting intent", "Check status", "Update preferences"],
            requires_user_input=False
        )
    
    async def process_user_input(self, user_id: str, input_text: str) -> Response:
        """Process natural language input from user with full NLP and learning"""
        user_context = await self._get_or_create_user_context(user_id)
        
        logger.info(f"0102 processing input from {user_id}: {input_text}")
        
        # Parse intent and entities using conversation manager
        parsed_result = await self.conversation_manager.parse_intent(input_text)
        intent = parsed_result["intent"]
        entities = parsed_result["entities"]
        confidence = parsed_result["confidence"]
        
        # Record interaction for learning
        await self.learning_engine.record_interaction(
            user_id=user_id,
            interaction_type="user_input",
            context={
                "input_text": input_text,
                "parsed_intent": intent.value if intent else None,
                "entities": entities,
                "confidence": confidence
            },
            outcome={"parsed_successfully": intent is not None}
        )
        
        # Route to appropriate handler based on intent
        if intent == Intent.CREATE_MEETING:
            return await self._handle_meeting_creation(user_context, input_text, entities)
        elif intent == Intent.CHECK_STATUS:
            return await self._handle_status_check(user_context)
        elif intent == Intent.CHECK_AVAILABILITY:
            return await self._handle_availability_check(user_context, entities)
        elif intent == Intent.ACCEPT_MEETING:
            return await self._handle_meeting_acceptance(user_context, entities)
        elif intent == Intent.DECLINE_MEETING:
            return await self._handle_meeting_decline(user_context, entities)
        elif intent == Intent.UPDATE_PREFERENCES:
            return await self._handle_preference_update(user_context, entities)
        elif intent == Intent.GREETING:
            return await self.greet_user(user_id, is_returning_user=True)
        else:
            return await self._handle_general_conversation(user_context, input_text)
    
    async def notify_user(
        self, 
        user_id: str, 
        message: str, 
        priority: Priority = Priority.MEDIUM,
        channels: Optional[List[NotificationChannel]] = None
    ) -> bool:
        """Send notification to user with personality adaptation"""
        
        # Adapt message with personality
        adapted_message = self.personality_engine.adapt_response(
            base_message=message,
            context=ResponseContext.STATUS_UPDATE,
            user_id=user_id
        )
        
        # Send via notification engine
        result = await self.notification_engine.send_notification(
            user_id=user_id,
            message=adapted_message,
            priority=priority,
            channels=channels or [NotificationChannel.CONSOLE]
        )
        
        return result
    
    async def suggest_action(self, user_id: str, situation: Dict) -> Response:
        """Proactively suggest actions based on current situation with learning"""
        
        # Get behavioral predictions
        predictions = await self.learning_engine.predict_user_behavior(user_id, situation)
        
        # Generate suggestions based on situation and learned patterns
        suggestions = []
        message = "I have some suggestions based on your current situation"
        
        # Add personalized touch if we have good learning data
        if predictions["confidence"] > 0.5:
            message += " and your preferences"
        message += ":"
        
        if situation.get("mutual_availability"):
            suggestions.append("Start the meeting now while both parties are available")
            
            # Add platform suggestion based on learned preferences
            if "preferred_platform" in predictions.get("predictions", {}):
                platform = predictions["predictions"]["preferred_platform"]["preferred_platform"]
                suggestions.append(f"Use {platform} (your preferred platform)")
            
        if situation.get("urgent_intents"):
            suggestions.append("Review urgent meeting requests")
            
        if not suggestions:
            message = "Everything looks good! I'll keep monitoring for meeting opportunities."
            suggestions = ["Check meeting history", "Update availability preferences"]
        
        # Adapt with personality
        adapted_message = self.personality_engine.adapt_response(
            base_message=message,
            context=ResponseContext.SUGGESTION,
            user_id=user_id,
            emotional_tone=EmotionalTone.SUPPORTIVE
        )
        
        return Response(
            response_type=ResponseType.SUGGESTION,
            message=adapted_message,
            suggested_actions=suggestions,
            requires_user_input=False,
            context={"predictions": predictions, "situation": situation}
        )
    
    async def launch_meeting_session(
        self,
        user_id: str,
        intent_id: str,
        participants: List[str],
        platform: str,
        context: Dict[str, Any]
    ) -> Response:
        """Launch a meeting session with full orchestration"""
        
        # Create launch request
        launch_request = LaunchRequest(
            intent_id=intent_id,
            participants=participants,
            platform=platform,
            context=context
        )
        
        # Launch session via session controller
        session_info = await self.session_controller.launch_session(launch_request)
        
        # Record learning data
        await self.learning_engine.record_interaction(
            user_id=user_id,
            interaction_type="meeting_launched",
            context={
                "platform": platform,
                "participants": participants,
                "intent_id": intent_id
            },
            outcome={
                "success": session_info.status.value == "active",
                "session_id": session_info.session_id
            }
        )
        
        # Generate success message
        if session_info.status.value == "active":
            success_message = self.personality_engine.get_success_message(
                action="session_launched",
                user_id=user_id
            )
            
            # Send notifications to all participants
            for participant in participants:
                await self.notify_user(
                    participant,
                    f"Meeting session launched! Join at: {session_info.meeting_link}",
                    Priority.HIGH,
                    [NotificationChannel.CONSOLE]
                )
            
            return Response(
                response_type=ResponseType.ACTION_RESULT,
                message=success_message,
                suggested_actions=["Join meeting", "End session", "Get session status"],
                requires_user_input=False,
                context={"session_info": session_info}
            )
        else:
            error_message = self.personality_engine.get_error_message(
                error_type="platform_error",
                user_id=user_id
            )
            
            return Response(
                response_type=ResponseType.ERROR,
                message=error_message,
                suggested_actions=["Try different platform", "Check participant availability"],
                requires_user_input=False,
                context={"session_info": session_info}
            )
    
    async def set_personality_mode(self, user_id: str, mode: PersonalityMode) -> Response:
        """Set personality mode for user"""
        
        # Update personality preference in learning engine
        await self.learning_engine.learn_preference(
            user_id=user_id,
            preference_type="personality_mode",
            value=mode.value
        )
        
        # Set preference in personality engine
        self.personality_engine.set_user_preference(user_id, mode)
        
        # Generate confirmation
        message = f"Personality mode updated to {mode.value}. I'll adapt my responses accordingly!"
        
        adapted_message = self.personality_engine.adapt_response(
            base_message=message,
            context=ResponseContext.SUCCESS_CONFIRMATION,
            user_id=user_id
        )
        
        return Response(
            response_type=ResponseType.CONFIRMATION,
            message=adapted_message,
            suggested_actions=["Test new personality", "Create meeting intent"],
            requires_user_input=False
        )
    
    async def get_user_insights(self, user_id: str) -> Response:
        """Get personalized insights for user"""
        
        # Get learning statistics
        user_preferences = await self.learning_engine.get_user_preferences(user_id)
        predictions = await self.learning_engine.predict_user_behavior(user_id, {})
        
        # Build insights message
        insights = []
        
        if user_preferences:
            insights.append(f"I've learned your preferences: {', '.join(user_preferences.keys())}")
        
        if predictions["confidence"] > 0.3:
            pred_data = predictions.get("predictions", {})
            if "preferred_platform" in pred_data:
                platform = pred_data["preferred_platform"]["preferred_platform"]
                insights.append(f"You seem to prefer {platform} for meetings")
        
        if predictions["based_on_interactions"] > 10:
            insights.append(f"We've had {predictions['based_on_interactions']} interactions - I'm getting to know you well!")
        
        if not insights:
            insights.append("I'm still learning about your preferences. The more we interact, the better I can assist you!")
        
        message = "Here's what I've learned about you:\n• " + "\n• ".join(insights)
        
        adapted_message = self.personality_engine.adapt_response(
            base_message=message,
            context=ResponseContext.STATUS_UPDATE,
            user_id=user_id
        )
        
        return Response(
            response_type=ResponseType.NOTIFICATION,
            message=adapted_message,
            suggested_actions=["Update preferences", "Create meeting intent", "View statistics"],
            requires_user_input=False,
            context={"preferences": user_preferences, "predictions": predictions}
        )
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        # Get component statistics
        learning_stats = await self.learning_engine.get_learning_statistics()
        notification_stats = self.notification_engine.get_statistics()
        session_stats = await self.session_controller.get_session_statistics()
        personality_stats = self.personality_engine.get_personality_stats()
        
        return {
            "0102_status": "fully_operational",
            "active_users": len(self.user_contexts),
            "learning_engine": learning_stats,
            "notification_engine": notification_stats,
            "session_controller": session_stats,
            "personality_engine": personality_stats,
            "total_interactions": sum([
                learning_stats.get("total_data_points", 0),
                notification_stats.get("total_sent", 0)
            ])
        }
    
    # Internal helper methods
    
    async def _get_or_create_user_context(self, user_id: str) -> UserContext:
        """Get or create user context for tracking state"""
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = UserContext(
                user_id=user_id,
                active_sessions=[],
                pending_intents=[],
                current_availability=None,
                last_interaction=datetime.now(),
                preferences={}
            )
        
        self.user_contexts[user_id].last_interaction = datetime.now()
        return self.user_contexts[user_id]
    
    async def _handle_meeting_creation(
        self, 
        user_context: UserContext, 
        input_text: str, 
        entities: EntityExtraction
    ) -> Response:
        """Handle meeting creation requests with entity extraction"""
        
        # Generate response using conversation manager
        response_data = await self.conversation_manager.generate_response(
            intent=Intent.CREATE_MEETING,
            entities=entities,
            user_id=user_context.user_id
        )
        
        # Simulate intent creation (in real system, this would call AMO components)
        intent_id = f"intent_{len(user_context.pending_intents) + 1}"
        user_context.pending_intents.append(intent_id)
        
        # Learn from this interaction
        if entities.recipients:
            await self.learning_engine.learn_preference(
                user_context.user_id,
                "frequent_collaborators",
                entities.recipients[0]  # First recipient
            )
        
        # Adapt response with personality
        adapted_message = self.personality_engine.adapt_response(
            base_message=response_data["response"],
            context=ResponseContext.MEETING_REQUEST,
            user_id=user_context.user_id,
            additional_context={"participants": entities.recipients}
        )
        
        return Response(
            response_type=ResponseType.CONFIRMATION,
            message=adapted_message,
            suggested_actions=response_data["suggested_actions"],
            requires_user_input=False,
            context={"intent_id": intent_id, "entities": entities}
        )
    
    async def _handle_availability_check(
        self, 
        user_context: UserContext, 
        entities: EntityExtraction
    ) -> Response:
        """Handle availability check requests"""
        
        # Check if asking about specific person
        if entities.recipients:
            target_user = entities.recipients[0]
            message = f"Checking availability for {target_user}... In the full system, I would query the Presence Aggregator for real-time status."
        else:
            message = "Checking availability... In the full system, I would show real-time status across all platforms."
        
        adapted_message = self.personality_engine.adapt_response(
            base_message=message,
            context=ResponseContext.STATUS_UPDATE,
            user_id=user_context.user_id
        )
        
        return Response(
            response_type=ResponseType.NOTIFICATION,
            message=adapted_message,
            suggested_actions=["Update your availability", "Check pending intents", "Create meeting intent"],
            requires_user_input=False
        )
    
    async def _handle_status_check(self, user_context: UserContext) -> Response:
        """Handle general status check requests"""
        
        pending_count = len(user_context.pending_intents)
        active_count = len(user_context.active_sessions)
        
        # Get active sessions from session controller
        active_sessions = await self.session_controller.list_active_sessions(user_context.user_id)
        actual_active_count = len(active_sessions)
        
        message = f"Here's your meeting coordination status:"
        message += f"\n• Pending meeting intents: {pending_count}"
        message += f"\n• Active meeting sessions: {actual_active_count}"
        message += f"\n\nI'm actively monitoring for meeting opportunities and will notify you when availability aligns."
        
        adapted_message = self.personality_engine.adapt_response(
            base_message=message,
            context=ResponseContext.STATUS_UPDATE,
            user_id=user_context.user_id,
            additional_context={"pending_count": pending_count}
        )
        
        return Response(
            response_type=ResponseType.NOTIFICATION,
            message=adapted_message,
            suggested_actions=["Create new meeting intent", "Check availability", "View insights"],
            requires_user_input=False
        )
    
    async def _handle_meeting_acceptance(
        self, 
        user_context: UserContext, 
        entities: EntityExtraction
    ) -> Response:
        """Handle meeting acceptance"""
        
        # Generate response using conversation manager
        response_data = await self.conversation_manager.generate_response(
            intent=Intent.ACCEPT_MEETING,
            entities=entities,
            user_id=user_context.user_id
        )
        
        # Learn acceptance pattern
        await self.learning_engine.record_interaction(
            user_id=user_context.user_id,
            interaction_type="meeting_accepted",
            context={"entities": entities.__dict__},
            outcome={"accepted": True}
        )
        
        adapted_message = self.personality_engine.adapt_response(
            base_message=response_data["response"],
            context=ResponseContext.SUCCESS_CONFIRMATION,
            user_id=user_context.user_id,
            emotional_tone=EmotionalTone.EXCITED
        )
        
        return Response(
            response_type=ResponseType.CONFIRMATION,
            message=adapted_message,
            suggested_actions=response_data["suggested_actions"],
            requires_user_input=False
        )
    
    async def _handle_meeting_decline(
        self, 
        user_context: UserContext, 
        entities: EntityExtraction
    ) -> Response:
        """Handle meeting decline"""
        
        response_data = await self.conversation_manager.generate_response(
            intent=Intent.DECLINE_MEETING,
            entities=entities,
            user_id=user_context.user_id
        )
        
        # Learn decline pattern
        await self.learning_engine.record_interaction(
            user_id=user_context.user_id,
            interaction_type="meeting_declined",
            context={"entities": entities.__dict__},
            outcome={"declined": True}
        )
        
        adapted_message = self.personality_engine.adapt_response(
            base_message=response_data["response"],
            context=ResponseContext.SUCCESS_CONFIRMATION,
            user_id=user_context.user_id,
            emotional_tone=EmotionalTone.SUPPORTIVE
        )
        
        return Response(
            response_type=ResponseType.CONFIRMATION,
            message=adapted_message,
            suggested_actions=response_data["suggested_actions"],
            requires_user_input=False
        )
    
    async def _handle_preference_update(
        self, 
        user_context: UserContext, 
        entities: EntityExtraction
    ) -> Response:
        """Handle preference updates"""
        
        # Extract preference from entities
        # This is simplified - in real implementation, would parse preference type and value
        preference_message = "I'd love to learn about your preferences! What would you like to update?"
        
        adapted_message = self.personality_engine.adapt_response(
            base_message=preference_message,
            context=ResponseContext.QUESTION,
            user_id=user_context.user_id
        )
        
        return Response(
            response_type=ResponseType.QUESTION,
            message=adapted_message,
            suggested_actions=["Set personality mode", "Update notification preferences", "Set platform preference"],
            requires_user_input=True
        )
    
    async def _handle_general_conversation(self, user_context: UserContext, input_text: str) -> Response:
        """Handle general conversational input with personality"""
        
        responses = [
            "I'm here to help you coordinate meetings efficiently.",
            "You can ask me to create meeting intents, check availability, or update your preferences.",
            "I work best when you tell me about meetings you want to schedule!",
            "I'm designed to make meeting coordination effortless and intelligent."
        ]
        
        import random
        base_response = random.choice(responses)
        
        adapted_message = self.personality_engine.adapt_response(
            base_message=base_response,
            context=ResponseContext.GREETING,
            user_id=user_context.user_id
        )
        
        return Response(
            response_type=ResponseType.NOTIFICATION,
            message=adapted_message,
            suggested_actions=["Create meeting intent", "Check status", "Update preferences"],
            requires_user_input=False
        )


# Demo function for comprehensive testing
async def demo_0102_comprehensive():
    """Comprehensive demo showcasing all 0102 capabilities"""
    print("=== 0102 Unified Orchestrator Comprehensive Demo ===")
    
    # Initialize 0102 with different personality modes
    for mode in [PersonalityMode.FRIENDLY, PersonalityMode.PROFESSIONAL, PersonalityMode.HUMOROUS]:
        print(f"\n--- Testing {mode.value.upper()} Mode ---")
        
        zero_one_zero_two = ZeroOneZeroTwo(mode)
        user_id = f"demo_user_{mode.value}"
        
        # Initial greeting
        greeting = await zero_one_zero_two.greet_user(user_id)
        print(f"🤖 0102: {greeting.message}")
        
        # Process meeting creation with NLP
        print(f"\n👤 User: I need to meet with Alice about the project roadmap for 30 minutes")
        response = await zero_one_zero_two.process_user_input(
            user_id, "I need to meet with Alice about the project roadmap for 30 minutes"
        )
        print(f"🤖 0102: {response.message}")
        
        # Test learning by setting preferences
        personality_response = await zero_one_zero_two.set_personality_mode(user_id, mode)
        print(f"🤖 0102: {personality_response.message}")
        
        # Get insights
        insights = await zero_one_zero_two.get_user_insights(user_id)
        print(f"🤖 0102: {insights.message}")
        
        print("-" * 50)
    
    # Test session launch
    print(f"\n--- Testing Session Launch ---")
    zero_one_zero_two = ZeroOneZeroTwo(PersonalityMode.DETAILED)
    
    session_response = await zero_one_zero_two.launch_meeting_session(
        user_id="alice",
        intent_id="intent_123",
        participants=["alice", "bob"],
        platform="discord",
        context={"purpose": "Demo meeting", "duration": 30}
    )
    print(f"🚀 Session Launch: {session_response.message}")
    
    # System status
    print(f"\n--- System Status ---")
    status = await zero_one_zero_two.get_system_status()
    print(f"📊 System Status: {status}")
    
    return zero_one_zero_two


if __name__ == "__main__":
    # Run comprehensive demo
    asyncio.run(demo_0102_comprehensive()) 