"""
Test Suite for Autonomous Meeting Orchestrator (AMO)

Tests cover all core functionality:
- Meeting intent creation and management
- Presence aggregation and monitoring
- Priority scoring and mutual availability detection
- Meeting session orchestration
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.orchestrator import (
    MeetingOrchestrator,
    MeetingIntent,
    UnifiedAvailabilityProfile,
    PresenceStatus,
    Priority
)


class TestMeetingOrchestrator:
    """Test suite for the main MeetingOrchestrator class"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create a fresh orchestrator instance for each test"""
        return MeetingOrchestrator()
    
    @pytest.mark.asyncio
    async def test_create_meeting_intent(self, orchestrator):
        """Test creation of meeting intents with proper structure"""
        intent_id = await orchestrator.create_meeting_intent(
            requester_id="alice",
            recipient_id="bob", 
            purpose="Discuss project requirements",
            expected_outcome="Align on deliverables",
            duration_minutes=45,
            priority=Priority.MEDIUM
        )
        
        assert intent_id == "intent_1"
        assert len(orchestrator.active_intents) == 1
        
        intent = orchestrator.active_intents[0]
        assert intent.requester_id == "alice"
        assert intent.recipient_id == "bob"
        assert intent.purpose == "Discuss project requirements"
        assert intent.expected_outcome == "Align on deliverables"
        assert intent.duration_minutes == 45
        assert intent.priority == Priority.MEDIUM
        assert intent.created_at is not None
    
    @pytest.mark.asyncio
    async def test_presence_update_new_user(self, orchestrator):
        """Test presence updates for a new user"""
        await orchestrator.update_presence("alice", "discord", PresenceStatus.ONLINE)
        
        assert "alice" in orchestrator.user_profiles
        profile = orchestrator.user_profiles["alice"]
        assert profile.user_id == "alice"
        assert profile.platforms["discord"] == PresenceStatus.ONLINE
        assert profile.overall_status == PresenceStatus.ONLINE
        assert profile.confidence_score > 0.0
    
    @pytest.mark.asyncio 
    async def test_presence_aggregation(self, orchestrator):
        """Test aggregation of presence across multiple platforms"""
        await orchestrator.update_presence("alice", "discord", PresenceStatus.ONLINE)
        await orchestrator.update_presence("alice", "whatsapp", PresenceStatus.IDLE)
        await orchestrator.update_presence("alice", "zoom", PresenceStatus.OFFLINE)
        
        profile = orchestrator.user_profiles["alice"]
        # Should prioritize ONLINE over IDLE and OFFLINE
        assert profile.overall_status == PresenceStatus.ONLINE
        assert len(profile.platforms) == 3
        assert profile.confidence_score == 1.0  # Max confidence with 3+ platforms
    
    def test_overall_status_calculation(self, orchestrator):
        """Test the priority-based overall status calculation"""
        # Test priority: ONLINE > IDLE > BUSY > OFFLINE > UNKNOWN
        platforms_online = {"discord": PresenceStatus.ONLINE, "slack": PresenceStatus.OFFLINE}
        assert orchestrator._calculate_overall_status(platforms_online) == PresenceStatus.ONLINE
        
        platforms_idle = {"discord": PresenceStatus.IDLE, "slack": PresenceStatus.BUSY}
        assert orchestrator._calculate_overall_status(platforms_idle) == PresenceStatus.IDLE
        
        platforms_busy = {"discord": PresenceStatus.BUSY, "slack": PresenceStatus.OFFLINE}
        assert orchestrator._calculate_overall_status(platforms_busy) == PresenceStatus.BUSY
    
    def test_confidence_calculation(self, orchestrator):
        """Test confidence score calculation based on platform count"""
        # Single platform = reduced confidence
        one_platform = {"discord": PresenceStatus.ONLINE}
        confidence = orchestrator._calculate_confidence(one_platform, 1.0)
        assert confidence < 1.0
        
        # Three platforms = full confidence
        three_platforms = {
            "discord": PresenceStatus.ONLINE,
            "whatsapp": PresenceStatus.IDLE,
            "zoom": PresenceStatus.OFFLINE
        }
        confidence = orchestrator._calculate_confidence(three_platforms, 1.0)
        assert confidence == 1.0
    
    def test_user_availability_check(self, orchestrator):
        """Test availability checking logic"""
        # User not in profiles = not available
        assert not orchestrator._is_user_available("nonexistent")
        
        # Set up user profiles
        orchestrator.user_profiles["alice"] = UnifiedAvailabilityProfile(
            user_id="alice",
            platforms={"discord": PresenceStatus.ONLINE},
            overall_status=PresenceStatus.ONLINE,
            last_updated=datetime.now(),
            confidence_score=0.8
        )
        
        orchestrator.user_profiles["bob"] = UnifiedAvailabilityProfile(
            user_id="bob",
            platforms={"discord": PresenceStatus.BUSY},
            overall_status=PresenceStatus.BUSY,
            last_updated=datetime.now(),
            confidence_score=0.8
        )
        
        assert orchestrator._is_user_available("alice")  # ONLINE = available
        assert not orchestrator._is_user_available("bob")  # BUSY = not available
    
    @pytest.mark.asyncio
    async def test_mutual_availability_detection(self, orchestrator):
        """Test detection of mutual availability triggering meeting prompts"""
        # Create a meeting intent
        await orchestrator.create_meeting_intent(
            requester_id="alice",
            recipient_id="bob",
            purpose="Quick sync",
            expected_outcome="Status update",
            duration_minutes=15,
            priority=Priority.LOW
        )
        
        # Mock the meeting prompt trigger to verify it gets called
        orchestrator._trigger_meeting_prompt = AsyncMock()
        
        # Set both users as available
        await orchestrator.update_presence("alice", "discord", PresenceStatus.ONLINE)
        await orchestrator.update_presence("bob", "discord", PresenceStatus.IDLE)
        
        # Should trigger meeting prompt
        orchestrator._trigger_meeting_prompt.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_meeting_session_creation(self, orchestrator):
        """Test full meeting session orchestration flow"""
        intent = MeetingIntent(
            requester_id="alice",
            recipient_id="bob",
            purpose="Project kickoff",
            expected_outcome="Project plan agreement",
            duration_minutes=60,
            priority=Priority.HIGH
        )
        orchestrator.active_intents.append(intent)
        
        session_id = await orchestrator._launch_meeting_session(intent)
        
        # Verify session was created
        assert session_id is not None
        assert len(orchestrator.meeting_history) == 1
        
        session = orchestrator.meeting_history[0]
        assert session["session_id"] == session_id
        assert session["intent"] == intent
        assert session["platform"] == "discord"  # PoC default
        assert session["status"] == "active"
        
        # Verify intent was removed from active list
        assert intent not in orchestrator.active_intents
    
    @pytest.mark.asyncio
    async def test_priority_levels(self, orchestrator):
        """Test different priority levels and their values"""
        # Test all priority levels
        priorities = [Priority.LOW, Priority.MEDIUM, Priority.HIGH, Priority.URGENT]
        expected_values = [1, 5, 8, 10]
        
        for priority, expected_value in zip(priorities, expected_values):
            await orchestrator.create_meeting_intent(
                requester_id="alice",
                recipient_id="bob",
                purpose=f"Test {priority.name}",
                expected_outcome="Test outcome",
                duration_minutes=30,
                priority=priority
            )
        
        # Verify all intents were created with correct priorities
        assert len(orchestrator.active_intents) == 4
        for i, intent in enumerate(orchestrator.active_intents):
            assert intent.priority.value == expected_values[i]
    
    def test_get_methods(self, orchestrator):
        """Test getter methods for accessing orchestrator state"""
        # Test empty state
        assert orchestrator.get_active_intents() == []
        assert orchestrator.get_user_profile("alice") is None
        assert orchestrator.get_meeting_history() == []
        
        # Add some data
        intent = MeetingIntent(
            requester_id="alice",
            recipient_id="bob",
            purpose="Test",
            expected_outcome="Test outcome",
            duration_minutes=30,
            priority=Priority.LOW
        )
        orchestrator.active_intents.append(intent)
        
        profile = UnifiedAvailabilityProfile(
            user_id="alice",
            platforms={"discord": PresenceStatus.ONLINE},
            overall_status=PresenceStatus.ONLINE,
            last_updated=datetime.now(),
            confidence_score=1.0
        )
        orchestrator.user_profiles["alice"] = profile
        
        meeting = {"test": "meeting"}
        orchestrator.meeting_history.append(meeting)
        
        # Test getters return copies (not references)
        active_intents = orchestrator.get_active_intents()
        assert len(active_intents) == 1
        assert active_intents[0] == intent
        assert active_intents is not orchestrator.active_intents  # Different object
        
        user_profile = orchestrator.get_user_profile("alice")
        assert user_profile == profile
        assert user_profile is profile  # This one should be the same object
        
        history = orchestrator.get_meeting_history()
        assert len(history) == 1
        assert history[0] == meeting
        assert history is not orchestrator.meeting_history  # Different object


class TestIntegration:
    """Integration tests for complete AMO workflows"""
    
    @pytest.mark.asyncio
    async def test_full_meeting_orchestration_flow(self):
        """Test the complete flow from intent creation to meeting launch"""
        orchestrator = MeetingOrchestrator()
        
        # Step 1: Create meeting intent
        intent_id = await orchestrator.create_meeting_intent(
            requester_id="alice",
            recipient_id="bob",
            purpose="Integration test meeting",
            expected_outcome="Successful test completion",
            duration_minutes=30,
            priority=Priority.MEDIUM
        )
        
        assert len(orchestrator.active_intents) == 1
        
        # Step 2: Set users as available
        await orchestrator.update_presence("alice", "discord", PresenceStatus.ONLINE)
        await orchestrator.update_presence("bob", "zoom", PresenceStatus.ONLINE)
        
        # Step 3: Verify mutual availability triggers meeting
        # (This is tested via the automatic trigger in update_presence)
        
        # Allow time for async processing
        await asyncio.sleep(3)  # Accounts for the 2-second simulation delay
        
        # Step 4: Verify meeting was orchestrated
        assert len(orchestrator.active_intents) == 0  # Intent should be consumed
        assert len(orchestrator.meeting_history) == 1  # Meeting should be launched
        
        meeting = orchestrator.meeting_history[0]
        assert meeting["platform"] == "discord"
        assert meeting["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_multiple_intents_priority_handling(self):
        """Test handling multiple meeting intents with different priorities"""
        orchestrator = MeetingOrchestrator()
        
        # Create multiple intents with different priorities
        await orchestrator.create_meeting_intent(
            requester_id="alice", recipient_id="bob",
            purpose="Low priority check-in", expected_outcome="Quick update",
            duration_minutes=15, priority=Priority.LOW
        )
        
        await orchestrator.create_meeting_intent(
            requester_id="alice", recipient_id="charlie",
            purpose="Urgent crisis meeting", expected_outcome="Crisis resolution",
            duration_minutes=60, priority=Priority.URGENT
        )
        
        assert len(orchestrator.active_intents) == 2
        
        # Make all users available
        await orchestrator.update_presence("alice", "discord", PresenceStatus.ONLINE)
        await orchestrator.update_presence("bob", "discord", PresenceStatus.ONLINE)
        await orchestrator.update_presence("charlie", "discord", PresenceStatus.ONLINE)
        
        # Allow time for processing
        await asyncio.sleep(5)
        
        # Both meetings should be orchestrated
        assert len(orchestrator.meeting_history) == 2


# Test fixtures and utilities
@pytest.fixture
def sample_meeting_intent():
    """Provide a sample meeting intent for testing"""
    return MeetingIntent(
        requester_id="test_user_1",
        recipient_id="test_user_2",
        purpose="Test meeting purpose",
        expected_outcome="Test outcome",
        duration_minutes=30,
        priority=Priority.MEDIUM
    )


@pytest.fixture 
def sample_availability_profile():
    """Provide a sample availability profile for testing"""
    return UnifiedAvailabilityProfile(
        user_id="test_user",
        platforms={"discord": PresenceStatus.ONLINE, "zoom": PresenceStatus.IDLE},
        overall_status=PresenceStatus.ONLINE,
        last_updated=datetime.now(),
        confidence_score=0.8
    )


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 