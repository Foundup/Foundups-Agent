"""
Tests for YouTube Shorts Scheduler.

Unit tests for channel config, schedule tracker, and content generator.
Integration tests require live browser session.
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import json

from modules.platform_integration.youtube_shorts_scheduler.src.channel_config import (
    get_channel_config,
    build_studio_url,
    get_studio_urls,
    CHANNELS,
)
from modules.platform_integration.youtube_shorts_scheduler.src.schedule_tracker import (
    ScheduleTracker,
)
from modules.platform_integration.youtube_shorts_scheduler.src.content_generator import (
    generate_clickbait_title,
    get_standard_description,
    generate_description_with_context,
    get_hashtags,
)


class TestChannelConfig:
    """Tests for channel configuration."""

    def test_get_channel_config_move2japan(self):
        """Test Move2Japan channel config."""
        config = get_channel_config("move2japan")
        assert config is not None
        assert config["id"] == "UC-LSSlOZwpGIRIYihaz8zCw"
        assert config["chrome_port"] == 9222
        assert len(config["time_slots"]) == 3

    def test_get_channel_config_undaodu(self):
        """Test UnDaoDu channel config."""
        config = get_channel_config("undaodu")
        assert config is not None
        assert config["id"] == "UCfHM9Fw9HD-NwiS0seD_oIA"
        assert config["chrome_port"] == 9222  # Shared with Move2Japan

    def test_get_channel_config_foundups(self):
        """Test FoundUps channel config."""
        config = get_channel_config("foundups")
        assert config is not None
        assert config["id"] == "UCSNTUXjAgpd4sgWYP0xoJgw"
        assert config["chrome_port"] == 9223  # Edge browser

    def test_get_channel_config_case_insensitive(self):
        """Test case insensitive lookup."""
        config1 = get_channel_config("MOVE2JAPAN")
        config2 = get_channel_config("Move2Japan")
        config3 = get_channel_config("move2japan")
        assert config1 == config2 == config3

    def test_get_channel_config_unknown(self):
        """Test unknown channel returns None."""
        config = get_channel_config("unknown_channel")
        assert config is None

    def test_build_studio_url_basic(self):
        """Test basic Studio URL building."""
        url = build_studio_url("UC123", "short")
        assert "studio.youtube.com/channel/UC123/videos/short" in url

    def test_build_studio_url_with_visibility(self):
        """Test URL with visibility filter."""
        url = build_studio_url("UC123", "short", "UNLISTED")
        assert "UNLISTED" in url
        assert "filter=" in url

    def test_get_studio_urls(self):
        """Test pre-built URL generation."""
        urls = get_studio_urls("move2japan")
        assert "unlisted_shorts" in urls
        assert "scheduled_shorts" in urls
        assert "public_shorts" in urls
        assert "all_shorts" in urls
        assert "base" in urls


class TestScheduleTracker:
    """Tests for schedule tracking."""

    def test_tracker_initialization(self):
        """Test tracker creates storage directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ScheduleTracker("test_channel", Path(tmpdir))
            assert tracker.channel_id == "test_channel"
            assert tracker.tracker_file.parent.exists()

    def test_tracker_increment(self):
        """Test incrementing video count."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ScheduleTracker("test_channel", Path(tmpdir))
            tracker.increment("Jan 5, 2026", "video123")
            assert tracker.get_count("Jan 5, 2026") == 1
            tracker.increment("Jan 5, 2026", "video456")
            assert tracker.get_count("Jan 5, 2026") == 2

    def test_tracker_persistence(self):
        """Test schedule persists to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and populate tracker
            tracker1 = ScheduleTracker("test_channel", Path(tmpdir))
            tracker1.increment("Jan 5, 2026", "video123")
            tracker1.increment("Jan 6, 2026", "video456")

            # Load fresh tracker
            tracker2 = ScheduleTracker("test_channel", Path(tmpdir))
            assert tracker2.get_count("Jan 5, 2026") == 1
            assert tracker2.get_count("Jan 6, 2026") == 1

    def test_get_next_available_slot_empty(self):
        """Test finding slot with empty schedule."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ScheduleTracker("test_channel", Path(tmpdir))
            time_slots = ["5:00 AM", "11:00 AM", "5:00 PM"]

            slot = tracker.get_next_available_slot(time_slots, max_per_day=3)
            assert slot is not None
            date_str, time_str = slot
            assert time_str == "5:00 AM"  # First slot on empty day

    def test_get_next_available_slot_partial(self):
        """Test finding slot with partially filled day."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ScheduleTracker("test_channel", Path(tmpdir))
            time_slots = ["5:00 AM", "11:00 AM", "5:00 PM"]

            # Fill first slot of tomorrow
            tomorrow = datetime.now() + timedelta(days=1)
            date_str = tomorrow.strftime("%b %d, %Y").replace(" 0", " ")
            tracker.increment(date_str, "video1")

            slot = tracker.get_next_available_slot(time_slots, max_per_day=3)
            assert slot is not None
            returned_date, time_str = slot
            # Should get second slot (11:00 AM) on same day
            assert time_str == "11:00 AM"

    def test_get_summary(self):
        """Test schedule summary."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = ScheduleTracker("test_channel", Path(tmpdir))
            tracker.increment("Jan 5, 2026", "v1")
            tracker.increment("Jan 5, 2026", "v2")
            tracker.increment("Jan 6, 2026", "v3")

            summary = tracker.get_summary()
            assert summary["total_scheduled"] == 3
            assert summary["dates_with_videos"] == 2


class TestContentGenerator:
    """Tests for content generation."""

    def test_generate_clickbait_title(self):
        """Test title generation."""
        title = generate_clickbait_title()
        assert len(title) <= 100
        assert "#FFCPLN" in title or "#MAGA" in title

    def test_generate_clickbait_title_with_hint(self):
        """Test title with song hint."""
        title = generate_clickbait_title(song_hint="Test Song")
        assert len(title) <= 100

    def test_get_standard_description_ffcpln(self):
        """Test FFCPLN description."""
        desc = get_standard_description("ffcpln")
        assert "FFCPLN" in desc
        assert "https://ffcpln.foundups.com" in desc

    def test_get_standard_description_alt(self):
        """Test alternative description."""
        desc = get_standard_description("alt")
        assert "FFCPLN" in desc

    def test_generate_description_with_context(self):
        """Test contextual description."""
        desc = generate_description_with_context(
            song_name="Test Song",
            artist="Test Artist",
        )
        assert "Test Song" in desc
        assert "Test Artist" in desc

    def test_get_hashtags(self):
        """Test hashtag generation."""
        hashtags = get_hashtags()
        assert "#FFCPLN" in hashtags


class TestSchedulerIntegration:
    """Integration tests (require browser connection)."""

    @pytest.mark.skip(reason="Requires live browser session")
    def test_scheduler_connect(self):
        """Test browser connection."""
        from modules.platform_integration.youtube_shorts_scheduler.src.scheduler import (
            YouTubeShortsScheduler,
        )

        scheduler = YouTubeShortsScheduler("move2japan", dry_run=True)
        connected = scheduler.connect_browser()
        assert connected
        scheduler.disconnect()

    @pytest.mark.skip(reason="Requires live browser session")
    def test_scheduler_dry_run(self):
        """Test dry run scheduling."""
        from modules.platform_integration.youtube_shorts_scheduler.src.scheduler import (
            run_scheduler_dae,
        )
        import asyncio

        results = asyncio.run(run_scheduler_dae(
            "move2japan",
            max_videos=1,
            dry_run=True,
        ))
        assert "channel" in results
