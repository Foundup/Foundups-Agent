"""
Tests for TimeoutTracker Module - WSP Compliant
Tests deduplication, multi-whack detection, and frag counting
"""

import pytest
import time
from datetime import datetime
from unittest.mock import patch, MagicMock
from modules.gamification.whack_a_magat.src.timeout_tracker import TimeoutTracker


class TestTimeoutTracker:
    """Test suite for TimeoutTracker functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = TimeoutTracker()
    
    def test_initialization(self):
        """Test tracker initializes with correct defaults."""
        assert self.tracker.dedup_window_seconds == 2
        assert self.tracker.multi_whack_window == 10
        assert len(self.tracker.seen_event_ids) == 0
        assert len(self.tracker.mod_frag_counts) == 0
    
    def test_process_ban_event_valid_frag(self):
        """Test processing a valid new frag."""
        is_valid, event_info = self.tracker.process_ban_event(
            event_id="test_event_1",
            mod_id="mod_123",
            mod_name="TestMod",
            target_id="target_456",
            target_name="TestTarget",
            timestamp=datetime.now().isoformat(),
            duration_seconds=300,
            is_permanent=False
        )
        
        assert is_valid is True
        assert event_info is not None
        assert event_info["mod_name"] == "TestMod"
        assert event_info["target_name"] == "TestTarget"
        assert event_info["frag_count"] == 1
        assert event_info["ban_type"] == "5m timeout"
    
    def test_duplicate_event_id_detection(self):
        """Test duplicate event ID is properly rejected."""
        # First event
        is_valid1, _ = self.tracker.process_ban_event(
            event_id="duplicate_id",
            mod_id="mod_123",
            mod_name="TestMod",
            target_id="target_456",
            target_name="TestTarget",
            timestamp=datetime.now().isoformat(),
            duration_seconds=300,
            is_permanent=False
        )
        
        # Duplicate event
        is_valid2, event_info2 = self.tracker.process_ban_event(
            event_id="duplicate_id",
            mod_id="mod_123",
            mod_name="TestMod",
            target_id="target_789",
            target_name="AnotherTarget",
            timestamp=datetime.now().isoformat(),
            duration_seconds=300,
            is_permanent=False
        )
        
        assert is_valid1 is True
        assert is_valid2 is False
        assert event_info2 is None
    
    def test_deduplication_window(self):
        """Test deduplication within time window."""
        timestamp = datetime.now().isoformat()
        
        # First event
        is_valid1, _ = self.tracker.process_ban_event(
            event_id="event_1",
            mod_id="mod_123",
            mod_name="TestMod",
            target_id="target_456",
            target_name="TestTarget",
            timestamp=timestamp,
            duration_seconds=300,
            is_permanent=False
        )
        
        # Same mod/target/time without event_id (within window)
        is_valid2, event_info2 = self.tracker.process_ban_event(
            event_id=None,
            mod_id="mod_123",
            mod_name="TestMod",
            target_id="target_456",
            target_name="TestTarget",
            timestamp=timestamp,
            duration_seconds=300,
            is_permanent=False
        )
        
        assert is_valid1 is True
        assert is_valid2 is False
        assert event_info2 is None
    
    def test_multi_whack_detection(self):
        """Test multi-whack detection within window."""
        mod_id = "mod_123"
        mod_name = "TestMod"
        
        # First whack
        _, event1 = self.tracker.process_ban_event(
            event_id="event_1",
            mod_id=mod_id,
            mod_name=mod_name,
            target_id="target_1",
            target_name="Target1",
            timestamp=datetime.now().isoformat(),
            duration_seconds=10,
            is_permanent=False
        )
        
        # Second whack (should be multi-whack)
        _, event2 = self.tracker.process_ban_event(
            event_id="event_2",
            mod_id=mod_id,
            mod_name=mod_name,
            target_id="target_2",
            target_name="Target2",
            timestamp=datetime.now().isoformat(),
            duration_seconds=10,
            is_permanent=False
        )
        
        assert event1["is_multi_whack"] is False
        assert event2["is_multi_whack"] is True
        assert event2["multi_whack_count"] == 2
    
    def test_frag_count_increment(self):
        """Test frag count properly increments for moderator."""
        mod_id = "mod_123"
        
        for i in range(1, 4):
            _, event = self.tracker.process_ban_event(
                event_id=f"event_{i}",
                mod_id=mod_id,
                mod_name="TestMod",
                target_id=f"target_{i}",
                target_name=f"Target{i}",
                timestamp=datetime.now().isoformat(),
                duration_seconds=300,
                is_permanent=False
            )
            assert event["frag_count"] == i
    
    def test_ban_type_classification(self):
        """Test different ban types are classified correctly."""
        test_cases = [
            (10, False, "10s timeout"),
            (60, False, "1m timeout"),
            (300, False, "5m timeout"),
            (3600, False, "1h ban"),
            (86400, False, "1d ban"),
            (0, True, "PERMABAN"),
        ]
        
        for duration, is_perm, expected_type in test_cases:
            _, event = self.tracker.process_ban_event(
                event_id=f"event_{duration}_{is_perm}",
                mod_id="mod_123",
                mod_name="TestMod",
                target_id="target_456",
                target_name="TestTarget",
                timestamp=datetime.now().isoformat(),
                duration_seconds=duration,
                is_permanent=is_perm
            )
            assert event["ban_type"] == expected_type
    
    def test_get_mod_stats(self):
        """Test getting statistics for specific moderator."""
        # Add some frags
        for i in range(3):
            self.tracker.process_ban_event(
                event_id=f"event_{i}",
                mod_id="mod_123",
                mod_name="TestMod",
                target_id=f"target_{i}",
                target_name=f"Target{i}",
                timestamp=datetime.now().isoformat(),
                duration_seconds=300,
                is_permanent=False
            )
        
        stats = self.tracker.get_mod_stats("mod_123")
        assert stats["mod_id"] == "mod_123"
        assert stats["mod_name"] == "TestMod"
        assert stats["frag_count"] == 3
        
        # Test unknown mod
        unknown_stats = self.tracker.get_mod_stats("unknown_mod")
        assert unknown_stats["mod_name"] == "Unknown"
        assert unknown_stats["frag_count"] == 0
    
    def test_get_leaderboard(self):
        """Test leaderboard generation and sorting."""
        # Add frags for multiple mods
        mods = [
            ("mod_1", "Alice", 5),
            ("mod_2", "Bob", 3),
            ("mod_3", "Charlie", 7),
        ]
        
        for mod_id, mod_name, frag_count in mods:
            for i in range(frag_count):
                self.tracker.process_ban_event(
                    event_id=f"{mod_id}_event_{i}",
                    mod_id=mod_id,
                    mod_name=mod_name,
                    target_id=f"target_{i}",
                    target_name=f"Target{i}",
                    timestamp=datetime.now().isoformat(),
                    duration_seconds=300,
                    is_permanent=False
                )
        
        leaderboard = self.tracker.get_leaderboard()
        
        # Check sorting (descending by frag count)
        assert len(leaderboard) == 3
        assert leaderboard[0]["mod_name"] == "Charlie"
        assert leaderboard[0]["frag_count"] == 7
        assert leaderboard[1]["mod_name"] == "Alice"
        assert leaderboard[1]["frag_count"] == 5
        assert leaderboard[2]["mod_name"] == "Bob"
        assert leaderboard[2]["frag_count"] == 3
    
    def test_reset_stats(self):
        """Test stats reset functionality."""
        # Add some data
        self.tracker.process_ban_event(
            event_id="test_event",
            mod_id="mod_123",
            mod_name="TestMod",
            target_id="target_456",
            target_name="TestTarget",
            timestamp=datetime.now().isoformat(),
            duration_seconds=300,
            is_permanent=False
        )
        
        # Verify data exists
        assert len(self.tracker.seen_event_ids) > 0
        assert len(self.tracker.mod_frag_counts) > 0
        
        # Reset
        self.tracker.reset_stats()
        
        # Verify all cleared
        assert len(self.tracker.seen_event_ids) == 0
        assert len(self.tracker.event_dedup_window) == 0
        assert len(self.tracker.recent_targets) == 0
        assert len(self.tracker.mod_frag_counts) == 0
    
    @patch('time.time')
    def test_dedup_window_cleanup(self, mock_time):
        """Test old deduplication entries are cleaned up."""
        # Set initial time
        mock_time.return_value = 1000.0
        
        # Add event
        self.tracker.process_ban_event(
            event_id="event_1",
            mod_id="mod_123",
            mod_name="TestMod",
            target_id="target_456",
            target_name="TestTarget",
            timestamp=datetime.now().isoformat(),
            duration_seconds=300,
            is_permanent=False
        )
        
        # Move time forward 61 seconds
        mock_time.return_value = 1061.0
        
        # Add another event to trigger cleanup
        self.tracker.process_ban_event(
            event_id="event_2",
            mod_id="mod_456",
            mod_name="TestMod2",
            target_id="target_789",
            target_name="TestTarget2",
            timestamp=datetime.now().isoformat(),
            duration_seconds=300,
            is_permanent=False
        )
        
        # Old entry should be cleaned up
        assert len(self.tracker.event_dedup_window) == 1