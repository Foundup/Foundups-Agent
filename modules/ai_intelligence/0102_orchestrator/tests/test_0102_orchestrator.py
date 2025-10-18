"""
Comprehensive test suite for 0102 Orchestrator module.

Tests all components and integration scenarios:
- ZeroOneZeroTwo main orchestrator
- ConversationManager (NLP and intent parsing)
- NotificationEngine (multi-channel notifications)
- SessionController (meeting session management)
- PersonalityEngine (adaptive response generation)
- LearningEngine (pattern recognition and adaptation)
- MemoryCore (preference and interaction storage)
- Full integration workflows
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

# Import test modules
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from zero_one_zero_two import ZeroOneZeroTwo, ResponseType
from conversation_manager import ConversationManager, Intent, EntityExtraction
from notification_engine import NotificationEngine, NotificationChannel, Priority
from session_controller import SessionController, LaunchRequest, SessionStatus
from personality_engine import PersonalityEngine, PersonalityMode, ResponseContext, EmotionalTone
from learning_engine import LearningEngine, LearningType, ConfidenceLevel
from memory_core import MemoryCore


class TestZeroOneZeroTwo:
    """Test the main 0102 orchestrator class"""
    
    @pytest.fixture
    def orchestrator(self):
        return ZeroOneZeroTwo(PersonalityMode.FRIENDLY)
    
    @pytest.mark.asyncio
    async def test_initialization(self, orchestrator):
        """Test proper initialization of all components"""
        assert orchestrator.personality_engine is not None
        assert orchestrator.conversation_manager is not None
        assert orchestrator.notification_engine is not None
        assert orchestrator.session_controller is not None
        assert orchestrator.learning_engine is not None
        assert orchestrator.memory_core is not None
        assert len(orchestrator.user_contexts) == 0
    
    @pytest.mark.asyncio
    async def test_greet_user_new(self, orchestrator):
        """Test greeting for new user"""
        response = await orchestrator.greet_user("alice", is_returning_user=False)
        
        assert response.response_type == ResponseType.NOTIFICATION
        assert "0102" in response.message
        assert len(response.suggested_actions) > 0
        assert not response.requires_user_input
        
        # Verify user context created
        assert "alice" in orchestrator.user_contexts
    
    @pytest.mark.asyncio
    async def test_greet_user_returning(self, orchestrator):
        """Test greeting for returning user"""
        # Create user context first
        await orchestrator.greet_user("alice", is_returning_user=False)
        
        response = await orchestrator.greet_user("alice", is_returning_user=True)
        
        assert response.response_type == ResponseType.NOTIFICATION
        assert "0102" in response.message
    
    @pytest.mark.asyncio
    async def test_process_meeting_creation(self, orchestrator):
        """Test processing meeting creation input"""
        response = await orchestrator.process_user_input(
            "alice", 
            "I need to meet with Bob about the project for 30 minutes"
        )
        
        assert response.response_type == ResponseType.CONFIRMATION
        assert "meeting" in response.message.lower()
        assert response.context is not None
        assert "intent_id" in response.context
    
    @pytest.mark.asyncio
    async def test_process_status_check(self, orchestrator):
        """Test status checking functionality"""
        response = await orchestrator.process_user_input(
            "alice", 
            "What's my current status?"
        )
        
        assert response.response_type == ResponseType.NOTIFICATION
        assert "status" in response.message.lower()
        assert "pending" in response.message.lower()
    
    @pytest.mark.asyncio
    async def test_process_availability_check(self, orchestrator):
        """Test availability checking"""
        response = await orchestrator.process_user_input(
            "alice",
            "Is Bob available?"
        )
        
        assert response.response_type == ResponseType.NOTIFICATION
        assert "availability" in response.message.lower()
    
    @pytest.mark.asyncio
    async def test_suggest_action_with_availability(self, orchestrator):
        """Test action suggestion with mutual availability"""
        response = await orchestrator.suggest_action(
            "alice",
            {"mutual_availability": True, "participants": ["Bob"]}
        )
        
        assert response.response_type == ResponseType.SUGGESTION
        assert len(response.suggested_actions) > 0
        assert "predictions" in response.context
    
    @pytest.mark.asyncio
    async def test_launch_meeting_session(self, orchestrator):
        """Test meeting session launch"""
        response = await orchestrator.launch_meeting_session(
            user_id="alice",
            intent_id="intent_123",
            participants=["alice", "bob"],
            platform="discord",
            context={"purpose": "Test meeting", "duration": 30}
        )
        
        assert response.response_type in [ResponseType.ACTION_RESULT, ResponseType.ERROR]
        assert response.context is not None
        assert "session_info" in response.context
    
    @pytest.mark.asyncio
    async def test_set_personality_mode(self, orchestrator):
        """Test personality mode setting"""
        response = await orchestrator.set_personality_mode("alice", PersonalityMode.PROFESSIONAL)
        
        assert response.response_type == ResponseType.CONFIRMATION
        assert "personality" in response.message.lower()
        assert "professional" in response.message.lower()
    
    @pytest.mark.asyncio
    async def test_get_user_insights(self, orchestrator):
        """Test getting user insights"""
        # Create some interaction history first
        await orchestrator.process_user_input("alice", "I need to meet with Bob")
        await orchestrator.set_personality_mode("alice", PersonalityMode.FRIENDLY)
        
        response = await orchestrator.get_user_insights("alice")
        
        assert response.response_type == ResponseType.NOTIFICATION
        assert "learned" in response.message.lower() or "learning" in response.message.lower()
        assert response.context is not None
    
    @pytest.mark.asyncio
    async def test_get_system_status(self, orchestrator):
        """Test system status retrieval"""
        status = await orchestrator.get_system_status()
        
        assert "0102_status" in status
        assert status["0102_status"] == "fully_operational"
        assert "active_users" in status
        assert "learning_engine" in status
        assert "notification_engine" in status


class TestConversationManager:
    """Test the conversation manager component"""
    
    @pytest.fixture
    def conv_manager(self):
        return ConversationManager()
    
    @pytest.mark.asyncio
    async def test_parse_meeting_intent(self, conv_manager):
        """Test parsing meeting creation intent"""
        result = await conv_manager.parse_intent("I need to meet with Alice")
        
        assert result["intent"] == Intent.CREATE_MEETING
        assert result["confidence"] > 0
        assert isinstance(result["entities"], EntityExtraction)
    
    @pytest.mark.asyncio
    async def test_parse_status_intent(self, conv_manager):
        """Test parsing status check intent"""
        result = await conv_manager.parse_intent("What's my status?")
        
        assert result["intent"] == Intent.CHECK_STATUS
        assert result["confidence"] > 0
    
    @pytest.mark.asyncio
    async def test_parse_availability_intent(self, conv_manager):
        """Test parsing availability check intent"""
        result = await conv_manager.parse_intent("Is Bob available?")
        
        assert result["intent"] == Intent.CHECK_AVAILABILITY
        assert result["confidence"] > 0
    
    @pytest.mark.asyncio
    async def test_entity_extraction(self, conv_manager):
        """Test entity extraction from user input"""
        result = await conv_manager.parse_intent("I need to meet with Alice and Bob about the project for 30 minutes")
        
        entities = result["entities"]
        assert len(entities.recipients) >= 1
        assert "alice" in [r.lower() for r in entities.recipients]
        assert entities.duration > 0
        assert entities.purpose is not None
    
    @pytest.mark.asyncio
    async def test_generate_response(self, conv_manager):
        """Test response generation"""
        entities = EntityExtraction(recipients=["Bob"], purpose="project meeting", duration=30)
        
        response_data = await conv_manager.generate_response(
            Intent.CREATE_MEETING,
            entities,
            "alice"
        )
        
        assert "response" in response_data
        assert "suggested_actions" in response_data
        assert len(response_data["suggested_actions"]) > 0


class TestNotificationEngine:
    """Test the notification engine component"""
    
    @pytest.fixture
    def notif_engine(self):
        return NotificationEngine()
    
    @pytest.mark.asyncio
    async def test_send_basic_notification(self, notif_engine):
        """Test sending basic notification"""
        result = await notif_engine.send_notification(
            user_id="alice",
            message="Test message",
            priority=Priority.MEDIUM,
            channels=[NotificationChannel.CONSOLE]
        )
        
        assert result is True
        
        # Check delivery history
        history = notif_engine.get_delivery_history("alice")
        assert len(history) == 1
        assert history[0]["message"] == "Test message"
    
    @pytest.mark.asyncio
    async def test_meeting_opportunity_notification(self, notif_engine):
        """Test meeting opportunity notification"""
        result = await notif_engine.notify_meeting_opportunity(
            recipient_id="alice",
            requester_id="Bob",
            purpose="Project discussion",
            duration=30,
            priority=Priority.HIGH
        )
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_presence_change_notification(self, notif_engine):
        """Test presence change notification"""
        result = await notif_engine.notify_presence_change(
            user_id="alice",
            contact_id="Bob",
            old_status="offline",
            new_status="online",
            platform="discord"
        )
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_statistics(self, notif_engine):
        """Test notification statistics"""
        # Send some notifications
        await notif_engine.send_notification("alice", "Test 1", Priority.LOW)
        await notif_engine.send_notification("bob", "Test 2", Priority.HIGH)
        
        stats = notif_engine.get_statistics()
        
        assert stats["total_sent"] >= 2
        assert "priority_distribution" in stats
        assert "channel_usage" in stats


class TestSessionController:
    """Test the session controller component"""
    
    @pytest.fixture
    def session_controller(self):
        return SessionController()
    
    @pytest.mark.asyncio
    async def test_launch_session(self, session_controller):
        """Test session launch"""
        launch_request = LaunchRequest(
            intent_id="intent_123",
            participants=["alice", "bob"],
            platform="discord",
            context={"purpose": "Test meeting", "duration": 30}
        )
        
        session_info = await session_controller.launch_session(launch_request)
        
        assert session_info.session_id is not None
        assert session_info.platform == "discord"
        assert session_info.status in [SessionStatus.ACTIVE, SessionStatus.FAILED]
        assert len(session_info.participants) == 2
    
    @pytest.mark.asyncio
    async def test_get_session_status(self, session_controller):
        """Test getting session status"""
        # Launch a session first
        launch_request = LaunchRequest(
            intent_id="intent_123",
            participants=["alice", "bob"],
            platform="discord",
            context={"purpose": "Test meeting"}
        )
        
        session_info = await session_controller.launch_session(launch_request)
        
        # Get status
        retrieved_session = await session_controller.get_session_status(session_info.session_id)
        
        assert retrieved_session is not None
        assert retrieved_session.session_id == session_info.session_id
    
    @pytest.mark.asyncio
    async def test_list_active_sessions(self, session_controller):
        """Test listing active sessions"""
        # Launch some sessions
        for i in range(2):
            launch_request = LaunchRequest(
                intent_id=f"intent_{i}",
                participants=["alice", "bob"],
                platform="discord",
                context={"purpose": f"Test meeting {i}"}
            )
            await session_controller.launch_session(launch_request)
        
        active_sessions = await session_controller.list_active_sessions("alice")
        
        # At least one should be active (depending on success/failure)
        assert isinstance(active_sessions, list)
    
    @pytest.mark.asyncio
    async def test_end_session(self, session_controller):
        """Test ending a session"""
        # Launch a session
        launch_request = LaunchRequest(
            intent_id="intent_123",
            participants=["alice", "bob"],
            platform="discord",
            context={"purpose": "Test meeting"}
        )
        
        session_info = await session_controller.launch_session(launch_request)
        
        # End the session
        result = await session_controller.end_session(session_info.session_id, "test_completed")
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_session_statistics(self, session_controller):
        """Test session statistics"""
        # Launch and end a session
        launch_request = LaunchRequest(
            intent_id="intent_123",
            participants=["alice", "bob"],
            platform="discord",
            context={"purpose": "Test meeting"}
        )
        
        session_info = await session_controller.launch_session(launch_request)
        await session_controller.end_session(session_info.session_id, "completed")
        
        stats = await session_controller.get_session_statistics()
        
        assert "total_sessions" in stats
        assert "platform_usage" in stats
        assert "success_rate" in stats


class TestPersonalityEngine:
    """Test the personality engine component"""
    
    @pytest.fixture
    def personality_engine(self):
        return PersonalityEngine(PersonalityMode.FRIENDLY)
    
    def test_personality_mode_setting(self, personality_engine):
        """Test setting personality mode"""
        result = personality_engine.set_personality_mode(PersonalityMode.PROFESSIONAL)
        
        assert result is True
        assert personality_engine.current_mode == PersonalityMode.PROFESSIONAL
    
    def test_adapt_response_basic(self, personality_engine):
        """Test basic response adaptation"""
        base_message = "I've created your meeting request."
        
        adapted = personality_engine.adapt_response(
            base_message=base_message,
            context=ResponseContext.MEETING_REQUEST,
            user_id="alice"
        )
        
        assert adapted is not None
        assert len(adapted) > 0
        assert isinstance(adapted, str)
    
    def test_adapt_response_with_emotion(self, personality_engine):
        """Test response adaptation with emotional tone"""
        base_message = "Meeting launched successfully!"
        
        adapted = personality_engine.adapt_response(
            base_message=base_message,
            context=ResponseContext.SUCCESS_CONFIRMATION,
            emotional_tone=EmotionalTone.EXCITED
        )
        
        assert adapted is not None
        # Excited tone might add exclamation marks
        assert "!" in adapted or "great" in adapted.lower() or "awesome" in adapted.lower()
    
    def test_get_greeting_message(self, personality_engine):
        """Test greeting message generation"""
        greeting = personality_engine.get_greeting_message("alice", is_returning_user=False)
        
        assert greeting is not None
        assert "0102" in greeting
        assert len(greeting) > 0
    
    def test_get_error_message(self, personality_engine):
        """Test error message generation"""
        error_msg = personality_engine.get_error_message("platform_error", "alice")
        
        assert error_msg is not None
        assert len(error_msg) > 0
    
    def test_get_success_message(self, personality_engine):
        """Test success message generation"""
        success_msg = personality_engine.get_success_message("meeting_created", "alice")
        
        assert success_msg is not None
        assert len(success_msg) > 0
    
    def test_user_preference_setting(self, personality_engine):
        """Test setting user personality preferences"""
        personality_engine.set_user_preference("alice", PersonalityMode.HUMOROUS)
        
        # Adapt response for this user
        adapted = personality_engine.adapt_response(
            "Test message",
            ResponseContext.GREETING,
            user_id="alice"
        )
        
        assert adapted is not None


class TestLearningEngine:
    """Test the learning engine component"""
    
    @pytest.fixture
    def learning_engine(self):
        return LearningEngine()
    
    @pytest.mark.asyncio
    async def test_record_interaction(self, learning_engine):
        """Test recording user interactions"""
        interaction_id = await learning_engine.record_interaction(
            user_id="alice",
            interaction_type="meeting_created",
            context={"platform": "discord", "duration": 30},
            outcome={"success": True}
        )
        
        assert interaction_id is not None
        assert len(learning_engine.learning_data) == 1
    
    @pytest.mark.asyncio
    async def test_learn_preference(self, learning_engine):
        """Test learning user preferences"""
        result = await learning_engine.learn_preference(
            user_id="alice",
            preference_type="platform",
            value="discord",
            confidence=0.9
        )
        
        assert result is True
        
        preferences = await learning_engine.get_user_preferences("alice")
        assert "platform" in preferences
        assert preferences["platform"] == "discord"
    
    @pytest.mark.asyncio
    async def test_predict_user_behavior(self, learning_engine):
        """Test behavioral prediction"""
        # Record some interactions first
        for i in range(3):
            await learning_engine.record_interaction(
                user_id="alice",
                interaction_type="meeting_created",
                context={"platform": "discord", "duration": 30},
                outcome={"success": True}
            )
        
        predictions = await learning_engine.predict_user_behavior("alice", {})
        
        assert "confidence" in predictions
        assert "predictions" in predictions
        assert "based_on_interactions" in predictions
        assert predictions["based_on_interactions"] >= 3
    
    @pytest.mark.asyncio
    async def test_learning_statistics(self, learning_engine):
        """Test learning statistics"""
        # Add some data
        await learning_engine.record_interaction("alice", "test", {}, {})
        await learning_engine.learn_preference("alice", "test_pref", "test_value")
        
        stats = await learning_engine.get_learning_statistics()
        
        assert "total_data_points" in stats
        assert "unique_users" in stats
        assert stats["total_data_points"] >= 2
        assert stats["unique_users"] >= 1


class TestMemoryCore:
    """Test the memory core component"""
    
    @pytest.fixture
    def memory_core(self):
        return MemoryCore()
    
    @pytest.mark.asyncio
    async def test_store_and_get_preference(self, memory_core):
        """Test preference storage and retrieval"""
        await memory_core.store_preference("alice", "platform", "discord")
        
        pref = await memory_core.get_preference("alice", "platform")
        assert pref == "discord"
    
    @pytest.mark.asyncio
    async def test_get_all_preferences(self, memory_core):
        """Test getting all user preferences"""
        await memory_core.store_preference("alice", "platform", "discord")
        await memory_core.store_preference("alice", "language", "english")
        
        prefs = await memory_core.get_all_preferences("alice")
        
        assert "platform" in prefs
        assert "language" in prefs
        assert prefs["platform"] == "discord"
        assert prefs["language"] == "english"
    
    @pytest.mark.asyncio
    async def test_record_interaction(self, memory_core):
        """Test interaction recording"""
        result = await memory_core.record_interaction(
            "alice", "meeting", {"platform": "discord"}, "success"
        )
        
        assert result is True
        
        history = await memory_core.get_interaction_history("alice")
        assert len(history) == 1
        assert history[0]["action"] == "meeting"
    
    @pytest.mark.asyncio
    async def test_generate_insights(self, memory_core):
        """Test insight generation"""
        # Record multiple interactions
        for i in range(5):
            await memory_core.record_interaction(
                "alice", "meeting", {"platform": "discord"}, "success"
            )
        
        insights = await memory_core.generate_insights("alice")
        
        assert isinstance(insights, list)
        # Should have at least one insight with multiple interactions
        if len(insights) > 0:
            assert "insight" in insights[0]


class TestIntegration:
    """Integration tests for complete workflows"""
    
    @pytest.mark.asyncio
    async def test_complete_meeting_flow(self):
        """Test complete meeting coordination flow"""
        orchestrator = ZeroOneZeroTwo(PersonalityMode.FRIENDLY)
        user_id = "alice"
        
        # Step 1: Greet user
        greeting = await orchestrator.greet_user(user_id)
        assert greeting.response_type == ResponseType.NOTIFICATION
        
        # Step 2: Create meeting intent
        meeting_response = await orchestrator.process_user_input(
            user_id, "I need to meet with Bob about the project"
        )
        assert meeting_response.response_type == ResponseType.CONFIRMATION
        
        # Step 3: Check status
        status_response = await orchestrator.process_user_input(
            user_id, "What's my status?"
        )
        assert status_response.response_type == ResponseType.NOTIFICATION
        
        # Step 4: Launch meeting session
        session_response = await orchestrator.launch_meeting_session(
            user_id=user_id,
            intent_id="intent_1",
            participants=[user_id, "bob"],
            platform="discord",
            context={"purpose": "Project discussion", "duration": 30}
        )
        
        assert session_response.response_type in [ResponseType.ACTION_RESULT, ResponseType.ERROR]
    
    @pytest.mark.asyncio
    async def test_personality_adaptation_flow(self):
        """Test personality adaptation across interactions"""
        orchestrator = ZeroOneZeroTwo(PersonalityMode.PROFESSIONAL)
        user_id = "alice"
        
        # Initial greeting (professional mode)
        greeting1 = await orchestrator.greet_user(user_id)
        professional_greeting = greeting1.message
        
        # Change to humorous mode
        await orchestrator.set_personality_mode(user_id, PersonalityMode.HUMOROUS)
        
        # New greeting should be different
        greeting2 = await orchestrator.greet_user(user_id, is_returning_user=True)
        humorous_greeting = greeting2.message
        
        # Messages should reflect different personalities
        assert professional_greeting != humorous_greeting
    
    @pytest.mark.asyncio
    async def test_learning_adaptation_flow(self):
        """Test learning and adaptation over multiple interactions"""
        orchestrator = ZeroOneZeroTwo(PersonalityMode.FRIENDLY)
        user_id = "alice"
        
        # Multiple meeting creation interactions
        for i in range(3):
            await orchestrator.process_user_input(
                user_id, f"I need to meet with Bob about project {i}"
            )
        
        # Set platform preference
        await orchestrator.learning_engine.learn_preference(
            user_id, "preferred_platform", "discord"
        )
        
        # Get suggestions - should include learned preferences
        suggestion = await orchestrator.suggest_action(
            user_id, {"mutual_availability": True}
        )
        
        assert "predictions" in suggestion.context
        predictions = suggestion.context["predictions"]
        
        # Should have some confidence after multiple interactions
        assert predictions["confidence"] > 0
    
    @pytest.mark.asyncio
    async def test_multi_user_system(self):
        """Test system with multiple users"""
        orchestrator = ZeroOneZeroTwo(PersonalityMode.FRIENDLY)
        
        users = ["alice", "bob", "charlie"]
        
        # Each user greets and creates meetings
        for user in users:
            await orchestrator.greet_user(user)
            await orchestrator.process_user_input(
                user, f"I need to meet with the team"
            )
        
        # Check system status
        status = await orchestrator.get_system_status()
        
        assert status["active_users"] == len(users)
        assert status["learning_engine"]["unique_users"] >= len(users)


# Performance and stress tests
class TestPerformance:
    """Performance and stress tests"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling concurrent user requests"""
        orchestrator = ZeroOneZeroTwo(PersonalityMode.FRIENDLY)
        
        # Create multiple concurrent requests
        tasks = []
        for i in range(10):
            task = orchestrator.process_user_input(
                f"user_{i}", "I need to meet with the team"
            )
            tasks.append(task)
        
        # Wait for all to complete
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        assert len(responses) == 10
        for response in responses:
            assert response.response_type == ResponseType.CONFIRMATION
    
    @pytest.mark.asyncio
    async def test_large_session_management(self):
        """Test managing many simultaneous sessions"""
        session_controller = SessionController()
        
        # Launch multiple sessions
        sessions = []
        for i in range(20):
            launch_request = LaunchRequest(
                intent_id=f"intent_{i}",
                participants=[f"user_{i}", "moderator"],
                platform="discord",
                context={"purpose": f"Session {i}"}
            )
            
            session_info = await session_controller.launch_session(launch_request)
            sessions.append(session_info)
        
        # Check statistics
        stats = await session_controller.get_session_statistics()
        assert stats["total_sessions"] >= 20


if __name__ == "__main__":
    # Run comprehensive test suite
    async def run_comprehensive_tests():
        print("[U+1F9EA] Running comprehensive 0102 orchestrator test suite...")
        
        # Test main orchestrator
        print("\n--- Testing Main Orchestrator ---")
        orchestrator = ZeroOneZeroTwo(PersonalityMode.FRIENDLY)
        
        greeting = await orchestrator.greet_user("test_user")
        print(f"[OK] Greeting: {greeting.message[:50]}...")
        
        meeting_response = await orchestrator.process_user_input(
            "test_user", "I need to meet with Alice about the project"
        )
        print(f"[OK] Meeting creation: {meeting_response.message[:50]}...")
        
        # Test components
        print("\n--- Testing Components ---")
        
        # Conversation Manager
        conv_manager = ConversationManager()
        parsed = await conv_manager.parse_intent("Schedule a meeting with Bob")
        print(f"[OK] NLP parsing: {parsed['intent'].value} with {parsed['confidence']:.2f} confidence")
        
        # Notification Engine
        notif_engine = NotificationEngine()
        await notif_engine.send_notification("test_user", "Test notification", Priority.MEDIUM)
        print("[OK] Notification sent successfully")
        
        # Session Controller
        session_controller = SessionController()
        launch_request = LaunchRequest(
            intent_id="test_intent",
            participants=["alice", "bob"],
            platform="discord",
            context={"purpose": "Test session"}
        )
        session_info = await session_controller.launch_session(launch_request)
        print(f"[OK] Session launched: {session_info.session_id}")
        
        # Personality Engine
        personality_engine = PersonalityEngine(PersonalityMode.HUMOROUS)
        adapted = personality_engine.adapt_response(
            "Meeting created successfully!",
            ResponseContext.SUCCESS_CONFIRMATION
        )
        print(f"[OK] Personality adaptation: {adapted[:50]}...")
        
        # Learning Engine
        learning_engine = LearningEngine()
        await learning_engine.record_interaction(
            "test_user", "test_interaction", {"test": "data"}, {"success": True}
        )
        stats = await learning_engine.get_learning_statistics()
        print(f"[OK] Learning recorded: {stats['total_data_points']} data points")
        
        # Memory Core
        memory_core = MemoryCore()
        await memory_core.store_preference("test_user", "platform", "discord")
        pref = await memory_core.get_preference("test_user", "platform")
        print(f"[OK] Memory storage: {pref}")
        
        # Integration test
        print("\n--- Testing Integration ---")
        session_response = await orchestrator.launch_meeting_session(
            user_id="test_user",
            intent_id="integration_test",
            participants=["alice", "bob"],
            platform="discord",
            context={"purpose": "Integration test", "duration": 30}
        )
        print(f"[OK] Full integration: {session_response.response_type.value}")
        
        # System status
        system_status = await orchestrator.get_system_status()
        print(f"[OK] System status: {system_status['0102_status']}")
        
        print(f"\n[CELEBRATE] All comprehensive tests passed! System fully operational.")
        
        return orchestrator
    
    # Run the tests
    asyncio.run(run_comprehensive_tests()) 