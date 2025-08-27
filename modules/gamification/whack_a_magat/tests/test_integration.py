"""
Integration Tests for Whack-a-MAGA System - WSP Compliant
Tests the complete flow from timeout detection to announcement generation
"""

import pytest
import time
from datetime import datetime
from unittest.mock import patch, MagicMock
from modules.gamification.whack_a_magat.src.timeout_tracker import TimeoutTracker
from modules.gamification.whack_a_magat.src.timeout_announcer import TimeoutManager


class TestWhackSystemIntegration:
    """Integration tests for the complete whack-a-MAGA system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch('os.makedirs'):
            self.manager = TimeoutManager(memory_dir="/tmp/test_memory")
            self.tracker = TimeoutTracker()
            # Link tracker to manager
            self.manager.tracker = self.tracker
    
    @patch('modules.gamification.whack_a_magat.src.whack.get_profile')
    @patch('modules.gamification.whack_a_magat.src.whack.apply_whack')
    def test_complete_timeout_flow(self, mock_apply_whack, mock_get_profile):
        """Test complete flow from timeout to announcement."""
        # Setup mocks
        mock_profile = MagicMock()
        mock_profile.score = 0
        mock_profile.rank = "Bronze"
        mock_profile.level = 1
        mock_get_profile.return_value = mock_profile
        
        mock_action = MagicMock()
        mock_action.points = 5
        mock_apply_whack.return_value = mock_action
        
        # Process a timeout
        result = self.manager.record_timeout(
            mod_id="mod_123",
            mod_name="TestMod",
            target_id="target_456",
            target_name="MAGAt",
            duration=10,  # 10 second timeout for HUMILIATION
            reason="Test"
        )
        
        # Verify announcement generated
        assert result["announcement"] is not None
        assert "HUMILIATION" in result["announcement"] or "WHACK" in result["announcement"]
        assert result["points_gained"] == 5
        
        # Verify tracker recorded the frag
        stats = self.tracker.get_mod_stats("mod_123")
        assert stats["frag_count"] == 1
        assert stats["mod_name"] == "TestMod"
    
    @patch('modules.gamification.whack_a_magat.src.whack.get_profile')
    @patch('modules.gamification.whack_a_magat.src.whack.apply_whack')
    def test_multi_whack_integration(self, mock_apply_whack, mock_get_profile):
        """Test multi-whack detection across system."""
        # Setup mocks
        mock_profile = MagicMock()
        mock_profile.score = 0
        mock_profile.rank = "Bronze"
        mock_profile.level = 1
        mock_get_profile.return_value = mock_profile
        
        mock_action = MagicMock()
        mock_action.points = 1
        mock_apply_whack.return_value = mock_action
        
        mod_id = "mod_123"
        mod_name = "MultiWhacker"
        
        # Process multiple timeouts rapidly
        announcements = []
        for i in range(4):
            result = self.manager.record_timeout(
                mod_id=mod_id,
                mod_name=mod_name,
                target_id=f"target_{i}",
                target_name=f"MAGAt{i}",
                duration=10,
                reason="Multi-whack test"
            )
            announcements.append(result["announcement"])
        
        # Verify multi-whack announcements
        assert any("DOUBLE WHACK" in a for a in announcements)
        assert any("TRIPLE WHACK" in a for a in announcements)
        assert any("MEGA WHACK" in a for a in announcements)
        
        # Verify tracker counted all frags
        stats = self.tracker.get_mod_stats(mod_id)
        assert stats["frag_count"] == 4
    
    @patch('modules.gamification.whack_a_magat.src.whack.get_profile')
    @patch('modules.gamification.whack_a_magat.src.whack.apply_whack')
    def test_level_up_detection(self, mock_apply_whack, mock_get_profile):
        """Test level up announcement generation."""
        # Mock profile that changes level
        old_profile = MagicMock()
        old_profile.score = 95
        old_profile.rank = "Bronze"
        old_profile.level = 1
        
        new_profile = MagicMock()
        new_profile.score = 105
        new_profile.rank = "Silver"
        new_profile.level = 2
        
        mock_get_profile.side_effect = [old_profile, new_profile]
        
        mock_action = MagicMock()
        mock_action.points = 10
        mock_apply_whack.return_value = mock_action
        
        result = self.manager.record_timeout(
            mod_id="mod_123",
            mod_name="LevelUpper",
            target_id="target_456",
            target_name="MAGAt",
            duration=300,
            reason="Level up test"
        )
        
        # Should detect rank change
        assert result["level_up"] is not None
        assert "RANKED UP" in result["level_up"]
        assert "Silver" in result["level_up"]
    
    def test_deduplication_across_system(self):
        """Test deduplication works across tracker and manager."""
        # Process same event twice
        event_id = "duplicate_event_123"
        
        # First process through tracker
        is_valid1, _ = self.tracker.process_ban_event(
            event_id=event_id,
            mod_id="mod_123",
            mod_name="TestMod",
            target_id="target_456",
            target_name="MAGAt",
            timestamp=datetime.now().isoformat(),
            duration_seconds=300,
            is_permanent=False
        )
        
        # Try to process same event again
        is_valid2, _ = self.tracker.process_ban_event(
            event_id=event_id,
            mod_id="mod_123",
            mod_name="TestMod",
            target_id="target_456",
            target_name="MAGAt",
            timestamp=datetime.now().isoformat(),
            duration_seconds=300,
            is_permanent=False
        )
        
        assert is_valid1 is True
        assert is_valid2 is False
        
        # Verify only counted once
        stats = self.tracker.get_mod_stats("mod_123")
        assert stats["frag_count"] == 1
    
    @patch('modules.gamification.whack_a_magat.src.whack.get_profile')
    def test_leaderboard_generation(self, mock_get_profile):
        """Test leaderboard generation across multiple moderators."""
        # Setup profiles for different mods
        profiles = {
            "mod_1": MagicMock(score=100, rank="Silver", level=3, user_id="mod_1"),
            "mod_2": MagicMock(score=50, rank="Bronze", level=2, user_id="mod_2"),
            "mod_3": MagicMock(score=150, rank="Gold", level=4, user_id="mod_3"),
        }
        
        def get_profile_side_effect(mod_id):
            return profiles.get(mod_id, MagicMock(score=0, rank="Bronze", level=1))
        
        mock_get_profile.side_effect = get_profile_side_effect
        
        # Add frags for each mod through tracker
        for mod_id, mod_name in [("mod_1", "Alice"), ("mod_2", "Bob"), ("mod_3", "Charlie")]:
            for i in range(3):  # 3 frags each
                self.tracker.process_ban_event(
                    event_id=f"{mod_id}_event_{i}",
                    mod_id=mod_id,
                    mod_name=mod_name,
                    target_id=f"target_{i}",
                    target_name=f"MAGAt{i}",
                    timestamp=datetime.now().isoformat(),
                    duration_seconds=300,
                    is_permanent=False
                )
        
        # Get leaderboard from tracker
        leaderboard = self.tracker.get_leaderboard()
        
        # All should have 3 frags (sorted by frag count, then by name)
        assert len(leaderboard) == 3
        assert all(entry["frag_count"] == 3 for entry in leaderboard)
        
        # Store mod names in manager
        self.manager.mod_names = {
            "mod_1": "Alice",
            "mod_2": "Bob", 
            "mod_3": "Charlie"
        }
        self.manager.kill_streaks = {
            "mod_1": 0,
            "mod_2": 0,
            "mod_3": 0
        }
        
        # Get stats through manager
        all_stats = self.manager.get_all_mod_stats()
        
        # Should be sorted by score (from profiles)
        assert all_stats[0]["name"] == "Charlie"  # 150 score
        assert all_stats[0]["score"] == 150
        assert all_stats[1]["name"] == "Alice"    # 100 score
        assert all_stats[2]["name"] == "Bob"      # 50 score
    
    @patch('time.time')
    @patch('modules.gamification.whack_a_magat.src.whack.get_profile')
    @patch('modules.gamification.whack_a_magat.src.whack.apply_whack')
    def test_streak_tracking(self, mock_apply_whack, mock_get_profile, mock_time):
        """Test kill streak tracking and milestone announcements."""
        # Setup mocks
        mock_profile = MagicMock(score=0, rank="Bronze", level=1)
        mock_get_profile.return_value = mock_profile
        mock_action = MagicMock(points=1)
        mock_apply_whack.return_value = mock_action
        
        mod_id = "streak_master"
        mod_name = "StreakMaster"
        mock_time.return_value = 1000.0
        
        # Build up a streak
        announcements = []
        for i in range(6):
            # Keep within streak window
            mock_time.return_value = 1000.0 + (i * 2)  # 2 seconds apart
            
            result = self.manager.record_timeout(
                mod_id=mod_id,
                mod_name=mod_name,
                target_id=f"target_{i}",
                target_name=f"MAGAt{i}",
                duration=300,
                reason="Streak test"
            )
            announcements.append(result["announcement"])
        
        # Should have hit 5-kill milestone
        assert any("WHACKING SPREE" in a for a in announcements)
        
        # Verify streak count
        assert self.manager.kill_streaks[mod_id] >= 5
    
    def test_ban_type_classification(self):
        """Test different ban durations are classified correctly."""
        test_cases = [
            (10, "10s timeout", "HUMILIATION"),
            (60, "1m timeout", None),
            (300, "5m timeout", None),
            (3600, "1h ban", None),
            (86400, "1d ban", None),
        ]
        
        for duration, expected_type, special_announcement in test_cases:
            # Process through tracker
            _, event = self.tracker.process_ban_event(
                event_id=f"ban_test_{duration}",
                mod_id="mod_123",
                mod_name="TestMod",
                target_id="target_456",
                target_name="MAGAt",
                timestamp=datetime.now().isoformat(),
                duration_seconds=duration,
                is_permanent=False
            )
            
            assert event["ban_type"] == expected_type
            
            # If expecting special announcement, verify through manager
            if special_announcement:
                self.manager._last_duration = duration
                announcement = self.manager._get_timeout_announcement(
                    "mod_123", "TestMod", "MAGAt"
                )
                if duration == 10:
                    assert special_announcement in announcement
    
    def test_error_handling(self):
        """Test system handles errors gracefully."""
        # Test with invalid data
        with patch('modules.gamification.whack_a_magat.src.whack.get_profile') as mock_get_profile:
            mock_get_profile.side_effect = Exception("Database error")
            
            # Should handle error and return None stats
            stats = self.manager.get_player_stats("error_user")
            assert stats is None
            
            # Format stats should handle None gracefully
            formatted = self.manager.format_stats("error_user")
            assert "No stats yet" in formatted
    
    def test_command_handling_integration(self):
        """Test chat command handling through the system."""
        with patch('modules.gamification.whack_a_magat.src.whack.get_profile') as mock_get_profile:
            mock_profile = MagicMock()
            mock_profile.score = 25
            mock_profile.rank = "Bronze"
            mock_profile.level = 1
            mock_get_profile.return_value = mock_profile
            
            # Test various commands
            commands = [
                ("/level", True, "Level"),
                ("/stats", True, "Bronze"),
                ("/smacks", True, "Total score"),
                ("/frags", True, "LEADERBOARD"),
                ("/level", False, None),  # Non-mod should get None
            ]
            
            for command, is_mod, expected in commands:
                response = self.manager.handle_chat_command(
                    command, "user_123", "TestUser", is_mod=is_mod
                )
                
                if expected:
                    assert response is not None
                    assert expected in response or "No frags recorded" in response
                else:
                    assert response is None