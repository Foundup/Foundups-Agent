# -*- coding: utf-8 -*-
"""
Unit tests for ActivityRouter - Occam's Razor Per-Channel Model.

Tests cover:
- Per-channel activity flow (Comments -> Shorts -> Indexing -> Next Channel)
- Live stream interrupt priority
- Channel advancement logic
- Phase signaling

Run from repo root:
    python -m pytest modules/infrastructure/activity_control/tests/test_activity_router.py -v
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
import os

# Import the module under test
import sys

# Add module path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from activity_control import (
    ActivityRouter,
    ActivityDecision,
    ActivityType,
    ChannelPhase,
    ChannelState,
    BrowserState,
    get_activity_router,
)


class TestActivityDecision:
    """Test ActivityDecision dataclass."""

    def test_activity_decision_creation(self):
        """ActivityDecision stores all fields correctly."""
        decision = ActivityDecision(
            next_activity=ActivityType.COMMENT_ENGAGEMENT,
            channel_id="UC123",
            channel_name="TestChannel",
            browser="chrome",
            reason="Test reason",
            metadata={"key": "value"}
        )
        assert decision.next_activity == ActivityType.COMMENT_ENGAGEMENT
        assert decision.channel_id == "UC123"
        assert decision.channel_name == "TestChannel"
        assert decision.browser == "chrome"
        assert decision.reason == "Test reason"
        assert decision.metadata == {"key": "value"}


class TestChannelState:
    """Test ChannelState dataclass."""

    def test_channel_state_defaults(self):
        """ChannelState starts in COMMENTS phase."""
        state = ChannelState(channel_id="UC123", channel_name="Test")
        assert state.phase == ChannelPhase.COMMENTS
        assert not state.is_complete()

    def test_channel_state_complete(self):
        """ChannelState.is_complete() returns True when phase is COMPLETE."""
        state = ChannelState(channel_id="UC123", channel_name="Test")
        state.phase = ChannelPhase.COMPLETE
        assert state.is_complete()


class TestActivityRouter:
    """Test ActivityRouter per-channel model."""

    @pytest.fixture
    def router(self):
        """Create a fresh ActivityRouter instance."""
        import activity_control
        activity_control._router_instance = None
        return ActivityRouter()

    def test_initial_channel_is_first(self, router):
        """Router starts with first channel."""
        assert router.current_channel_name == "Move2Japan"
        assert router.current_channel.phase == ChannelPhase.COMMENTS

    def test_get_next_activity_starts_with_comments(self, router):
        """First activity is COMMENT_ENGAGEMENT for first channel."""
        decision = router.get_next_activity()
        assert decision.next_activity == ActivityType.COMMENT_ENGAGEMENT
        assert decision.channel_name == "Move2Japan"
        assert decision.browser == "chrome"

    def test_signal_comments_complete_advances_to_shorts(self, router):
        """After comments complete, channel advances to SHORTS phase."""
        channel_id = router.current_channel_id
        router.signal_comments_complete(channel_id, comments_processed=10)

        assert router.current_channel.phase == ChannelPhase.SHORTS

    @patch.dict(os.environ, {"YT_SHORTS_SCHEDULING_ENABLED": "true"})
    def test_shorts_phase_returns_shorts_activity(self, router):
        """When channel is in SHORTS phase, return SHORTS_SCHEDULING."""
        channel_id = router.current_channel_id
        router.signal_comments_complete(channel_id)

        decision = router.get_next_activity()
        assert decision.next_activity == ActivityType.SHORTS_SCHEDULING
        assert decision.channel_name == "Move2Japan"

    @patch.dict(os.environ, {"YT_SHORTS_SCHEDULING_ENABLED": "false"})
    def test_shorts_disabled_skips_to_indexing(self, router):
        """When shorts disabled, skip directly to INDEXING phase."""
        channel_id = router.current_channel_id
        router.signal_comments_complete(channel_id)

        # Shorts disabled, should skip to indexing or complete
        decision = router.get_next_activity()
        assert decision.next_activity in (ActivityType.VIDEO_INDEXING, ActivityType.COMMENT_ENGAGEMENT)

    def test_channel_advances_after_all_phases(self, router):
        """After all phases complete, advance to next channel."""
        channel_id = router.current_channel_id

        # Complete all phases for first channel
        router.signal_comments_complete(channel_id)
        router.signal_shorts_complete(channel_id)
        router.signal_indexing_complete(channel_id)

        # Should advance to UnDaoDu
        decision = router.get_next_activity()
        assert decision.channel_name == "UnDaoDu"
        assert decision.next_activity == ActivityType.COMMENT_ENGAGEMENT

    def test_live_stream_interrupts_any_activity(self, router):
        """Live stream takes priority over any other activity."""
        router.check_live_stream_active = MagicMock(return_value=True)

        decision = router.get_next_activity()
        assert decision.next_activity == ActivityType.LIVE_CHAT
        assert decision.browser == "edge"

    def test_live_chat_never_interrupted(self, router):
        """LIVE_CHAT activity cannot be interrupted."""
        router.check_live_stream_active = MagicMock(return_value=True)

        result = router.should_interrupt_for_higher_priority(ActivityType.LIVE_CHAT)
        assert result is None

    def test_full_cycle_returns_to_first_channel(self, router):
        """After all channels complete, cycle resets to first channel."""
        # Complete all 4 channels
        for _ in range(4):
            channel_id = router.current_channel_id
            router.signal_comments_complete(channel_id)
            router.signal_shorts_complete(channel_id)
            router.signal_indexing_complete(channel_id)
            router.get_next_activity()  # Advance to next channel

        # Should reset to Move2Japan
        decision = router.get_next_activity()
        # After IDLE, channels reset
        assert decision.next_activity in (ActivityType.IDLE, ActivityType.COMMENT_ENGAGEMENT)

    def test_get_status_returns_all_info(self, router):
        """get_status() returns comprehensive status."""
        status = router.get_status()

        assert "current_channel" in status
        assert "current_channel_id" in status
        assert "current_phase" in status
        assert "channels" in status
        assert "shorts_enabled" in status
        assert "indexing_enabled" in status
        assert len(status["channels"]) == 4


class TestActivityRouterSingleton:
    """Test singleton behavior."""

    def test_get_activity_router_returns_same_instance(self):
        """get_activity_router returns singleton instance."""
        import activity_control
        activity_control._router_instance = None

        router1 = get_activity_router()
        router2 = get_activity_router()
        assert router1 is router2


class TestActivityType:
    """Test ActivityType enum."""

    def test_all_activity_types_exist(self):
        """All expected activity types are defined."""
        assert hasattr(ActivityType, 'COMMENT_ENGAGEMENT')
        assert hasattr(ActivityType, 'SHORTS_SCHEDULING')
        assert hasattr(ActivityType, 'VIDEO_INDEXING')
        assert hasattr(ActivityType, 'CHANNEL_COMPLETE')
        assert hasattr(ActivityType, 'LIVE_CHAT')
        assert hasattr(ActivityType, 'IDLE')


class TestChannelPhase:
    """Test ChannelPhase enum."""

    def test_all_phases_exist(self):
        """All expected phases are defined."""
        assert hasattr(ChannelPhase, 'COMMENTS')
        assert hasattr(ChannelPhase, 'SHORTS')
        assert hasattr(ChannelPhase, 'INDEXING')
        assert hasattr(ChannelPhase, 'COMPLETE')
