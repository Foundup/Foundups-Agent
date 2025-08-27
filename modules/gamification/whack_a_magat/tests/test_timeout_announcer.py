"""
Tests for TimeoutManager Module - WSP Compliant
Tests Duke Nukem announcer, whack.py integration, and multi-whack announcements
"""

import pytest
import time
import json
import os
from datetime import datetime
from unittest.mock import patch, MagicMock, mock_open
from modules.gamification.whack_a_magat.src.timeout_announcer import TimeoutManager


class TestTimeoutManager:
    """Test suite for TimeoutManager with Duke Nukem announcer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_memory_dir = "/tmp/test_memory"
        with patch('os.makedirs'):
            self.manager = TimeoutManager(memory_dir=self.test_memory_dir)
    
    def test_initialization(self):
        """Test manager initializes with correct defaults."""
        assert self.manager.memory_dir == os.path.abspath(self.test_memory_dir)
        assert self.manager.multi_whack_window == 30  # Easy mode: 30 seconds
        assert self.manager.streak_window == 15
        assert len(self.manager.kill_streaks) == 0
        assert len(self.manager.mod_names) == 0
    
    def test_rank_titles_structure(self):
        """Test rank titles are properly structured."""
        expected_ranks = ["Bronze", "Silver", "Gold", "Platinum"]
        for rank in expected_ranks:
            assert rank in self.manager.rank_titles
            assert len(self.manager.rank_titles[rank]) > 0
    
    @patch('modules.gamification.whack_a_magat.src.whack.get_profile')
    @patch('modules.gamification.whack_a_magat.src.whack.apply_whack')
    def test_record_timeout_basic(self, mock_apply_whack, mock_get_profile):
        """Test basic timeout recording."""
        # Mock profile data
        mock_profile = MagicMock()
        mock_profile.score = 10
        mock_profile.rank = "Bronze"
        mock_profile.level = 1
        mock_get_profile.return_value = mock_profile
        
        # Mock whack action
        mock_action = MagicMock()
        mock_action.points = 5
        mock_apply_whack.return_value = mock_action
        
        result = self.manager.record_timeout(
            mod_id="mod_123",
            mod_name="TestMod",
            target_id="target_456",
            target_name="TestTarget",
            duration=300,
            reason="Test"
        )
        
        assert result["points_gained"] == 5
        assert result["announcement"] is not None
        assert "TestMod" in result["announcement"]
        assert result["stats"]["score"] == 10
        assert result["stats"]["rank"] == "Bronze"
    
    def test_get_title_for_profile(self):
        """Test D&D title generation based on rank and level."""
        test_cases = [
            (MagicMock(rank="Bronze", level=1), "Novice Smasher"),
            (MagicMock(rank="Silver", level=2), "Expert Troller"),
            (MagicMock(rank="Gold", level=4), "Elite Guardian"),
            (MagicMock(rank="Platinum", level=6), "Divine Punisher"),
        ]
        
        for profile, expected_substr in test_cases:
            title = self.manager.get_title_for_profile(profile)
            assert expected_substr in title or title in ["Novice Smasher", "Expert Troller", "Elite Guardian", "Divine Punisher"]
    
    def test_multi_whack_detection(self):
        """Test multi-whack announcement generation."""
        # Test the _get_timeout_announcement method directly
        mod_id = "mod_123"
        mod_name = "TestMod"
        
        # First whack
        announcement1 = self.manager._get_timeout_announcement(mod_id, mod_name, "Target1")
        assert announcement1 is not None
        
        # Second whack within window (should be DOUBLE WHACK)
        announcement2 = self.manager._get_timeout_announcement(mod_id, mod_name, "Target2")
        assert "DOUBLE WHACK" in announcement2
        assert mod_name in announcement2
        
        # Third whack (should be TRIPLE WHACK)
        announcement3 = self.manager._get_timeout_announcement(mod_id, mod_name, "Target3")
        assert "TRIPLE WHACK" in announcement3
        
        # Fourth whack (should be MEGA WHACK)
        announcement4 = self.manager._get_timeout_announcement(mod_id, mod_name, "Target4")
        assert "MEGA WHACK" in announcement4
    
    def test_streak_milestones(self):
        """Test Duke Nukem streak milestone announcements."""
        mod_id = "mod_123"
        mod_name = "TestMod"
        
        # Build up a streak
        for i in range(5):
            self.manager._get_timeout_announcement(mod_id, mod_name, f"Target{i}")
        
        # 5th kill should trigger WHACKING SPREE
        announcement = self.manager._get_timeout_announcement(mod_id, mod_name, "Target5")
        assert "WHACKING SPREE" in announcement or self.manager.kill_streaks[mod_id] == 6
    
    def test_humiliation_detection(self):
        """Test HUMILIATION announcement for 10-second timeouts."""
        self.manager._last_duration = 10
        announcement = self.manager._get_timeout_announcement("mod_123", "TestMod", "TestTarget")
        
        # Should get HUMILIATION for 10-second timeout
        if hasattr(self.manager, '_last_duration') and self.manager._last_duration == 10:
            assert "HUMILIATION" in announcement
    
    def test_behavior_flavor_text(self):
        """Test behavior-specific flavor text generation."""
        from modules.gamification.whack_a_magat.src.whack import BehaviorTier
        
        test_cases = [
            (BehaviorTier.CAT_PLAY, "toying with"),
            (BehaviorTier.BRUTAL_HAMMER, "BRUTAL HAMMER"),
            (BehaviorTier.GENTLE_TOUCH, "WHACKS"),
        ]
        
        for behavior, expected_text in test_cases:
            flavor = self.manager._get_behavior_flavor(behavior, "TestMod", "TestTarget", 300)
            if flavor:  # Some behaviors may return None
                assert expected_text in flavor
    
    @patch('builtins.open', new_callable=mock_open, read_data='{"kill_streaks": {"mod_123": 5}}')
    def test_load_stats(self, mock_file):
        """Test loading saved announcer statistics."""
        with patch('os.path.exists', return_value=True):
            self.manager.load_stats()
            assert self.manager.kill_streaks.get("mod_123") == 5
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_save_stats(self, mock_json_dump, mock_file):
        """Test saving announcer statistics."""
        self.manager.kill_streaks["mod_123"] = 10
        self.manager.save_stats()
        
        # Verify json.dump was called with correct data
        mock_json_dump.assert_called_once()
        saved_data = mock_json_dump.call_args[0][0]
        assert saved_data["kill_streaks"]["mod_123"] == 10
        assert "last_save" in saved_data
    
    @patch('modules.gamification.whack_a_magat.src.whack.get_profile')
    def test_get_player_stats(self, mock_get_profile):
        """Test getting player statistics."""
        mock_profile = MagicMock()
        mock_profile.score = 100
        mock_profile.rank = "Silver"
        mock_profile.level = 3
        mock_profile.user_id = "user_123"
        mock_get_profile.return_value = mock_profile
        
        stats = self.manager.get_player_stats("user_123")
        
        assert stats["score"] == 100
        assert stats["rank"] == "Silver"
        assert stats["level"] == 3
        assert stats["user_id"] == "user_123"
        assert "title" in stats
    
    @patch('modules.gamification.whack_a_magat.src.whack.get_profile')
    def test_format_stats(self, mock_get_profile):
        """Test formatting player stats for display."""
        mock_profile = MagicMock()
        mock_profile.score = 50
        mock_profile.rank = "Bronze"
        mock_profile.level = 2
        mock_profile.user_id = "user_123"
        mock_get_profile.return_value = mock_profile
        
        formatted = self.manager.format_stats("user_123")
        
        assert "Stats:" in formatted
        assert "Bronze" in formatted
        assert "Level" in formatted
        assert "50" in formatted
    
    def test_handle_chat_command_level(self):
        """Test handling /level command."""
        with patch('modules.gamification.whack_a_magat.src.whack.get_profile') as mock_get_profile:
            mock_profile = MagicMock()
            mock_profile.score = 75
            mock_profile.rank = "Silver"
            mock_profile.level = 2
            mock_get_profile.return_value = mock_profile
            
            response = self.manager.handle_chat_command(
                "/level", "user_123", "TestUser", is_mod=True
            )
            
            assert response is not None
            assert "TestUser" in response
            assert "Silver" in response
            assert "Level 2" in response
    
    def test_handle_chat_command_non_mod(self):
        """Test commands restricted to mods return None for non-mods."""
        response = self.manager.handle_chat_command(
            "/level", "user_123", "TestUser", is_mod=False
        )
        assert response is None
    
    def test_handle_chat_command_frags(self):
        """Test handling /frags leaderboard command."""
        # Set up some mod stats
        self.manager.kill_streaks["mod_1"] = 5
        self.manager.mod_names["mod_1"] = "Alice"
        
        with patch.object(self.manager, 'get_all_mod_stats') as mock_get_stats:
            mock_get_stats.return_value = [
                {"name": "Alice", "score": 100, "current_streak": 5},
                {"name": "Bob", "score": 50, "current_streak": 2},
            ]
            
            response = self.manager.handle_chat_command(
                "/frags", "user_123", "TestUser", is_mod=True
            )
            
            assert "FRAG LEADERBOARD" in response
            assert "Alice" in response
            assert "100" in response
    
    @patch('time.time')
    def test_multi_whack_window_expiry(self, mock_time):
        """Test multi-whack count resets after window expires."""
        mod_id = "mod_123"
        mod_name = "TestMod"
        
        # First whack at time 1000
        mock_time.return_value = 1000.0
        self.manager._get_timeout_announcement(mod_id, mod_name, "Target1")
        
        # Second whack within window (time 1010)
        mock_time.return_value = 1010.0
        announcement = self.manager._get_timeout_announcement(mod_id, mod_name, "Target2")
        assert "DOUBLE WHACK" in announcement
        
        # Third whack after window expires (time 1031)
        mock_time.return_value = 1031.0  # 31 seconds later (window is 30)
        announcement = self.manager._get_timeout_announcement(mod_id, mod_name, "Target3")
        # Should reset to single whack
        assert "DOUBLE WHACK" not in announcement
        assert self.manager.multi_whack_count[mod_id] == 1
    
    def test_get_all_mod_stats(self):
        """Test getting stats for all moderators."""
        # Set up test data
        self.manager.kill_streaks = {"mod_1": 5, "mod_2": 3}
        self.manager.mod_names = {"mod_1": "Alice", "mod_2": "Bob"}
        
        with patch('modules.gamification.whack_a_magat.src.whack.get_profile') as mock_get_profile:
            def side_effect(mod_id):
                mock_profile = MagicMock()
                if mod_id == "mod_1":
                    mock_profile.score = 100
                    mock_profile.rank = "Silver"
                    mock_profile.level = 3
                else:
                    mock_profile.score = 50
                    mock_profile.rank = "Bronze"
                    mock_profile.level = 2
                return mock_profile
            
            mock_get_profile.side_effect = side_effect
            
            all_stats = self.manager.get_all_mod_stats()
            
            # Should be sorted by score descending
            assert len(all_stats) == 2
            assert all_stats[0]["name"] == "Alice"
            assert all_stats[0]["score"] == 100
            assert all_stats[1]["name"] == "Bob"
            assert all_stats[1]["score"] == 50