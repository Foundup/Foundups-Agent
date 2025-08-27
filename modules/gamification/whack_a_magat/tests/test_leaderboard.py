"""
Tests for Leaderboard and Persistence - WSP Compliant
Tests the enhanced scoring system with persistence and leaderboard features
"""

import pytest
import os
import tempfile
from datetime import datetime
from modules.gamification.whack_a_magat.src.whack import (
    get_profile,
    get_leaderboard,
    get_user_position,
    apply_whack,
    _reset_state_for_tests,
    _profiles_repo
)


class TestLeaderboardFunctionality:
    """Test the leaderboard and position tracking."""
    
    def setup_method(self):
        """Reset state before each test."""
        _reset_state_for_tests()
        # Disable persistence for tests
        _profiles_repo.persist = False
    
    def test_empty_leaderboard(self):
        """Test leaderboard when no players exist."""
        leaderboard = get_leaderboard(10)
        assert leaderboard == []
    
    def test_single_player_leaderboard(self):
        """Test leaderboard with one player."""
        # Create a player with some score
        profile = get_profile("player1")
        profile.score = 100
        _profiles_repo.save(profile)
        
        leaderboard = get_leaderboard(10)
        assert len(leaderboard) == 1
        assert leaderboard[0]['position'] == 1
        assert leaderboard[0]['user_id'] == "player1"
        assert leaderboard[0]['score'] == 100
    
    def test_multiple_players_leaderboard(self):
        """Test leaderboard with multiple players."""
        # Create players with different scores
        players = [
            ("player1", 500),
            ("player2", 300),
            ("player3", 700),
            ("player4", 100),
            ("player5", 450)
        ]
        
        for user_id, score in players:
            profile = get_profile(user_id)
            profile.score = score
            _profiles_repo.save(profile)
        
        leaderboard = get_leaderboard(3)  # Get top 3
        
        assert len(leaderboard) == 3
        # Check correct ordering
        assert leaderboard[0]['user_id'] == "player3"  # 700 XP
        assert leaderboard[0]['score'] == 700
        assert leaderboard[0]['position'] == 1
        
        assert leaderboard[1]['user_id'] == "player1"  # 500 XP
        assert leaderboard[1]['score'] == 500
        assert leaderboard[1]['position'] == 2
        
        assert leaderboard[2]['user_id'] == "player5"  # 450 XP
        assert leaderboard[2]['score'] == 450
        assert leaderboard[2]['position'] == 3
    
    def test_user_position_tracking(self):
        """Test getting a user's position on the leaderboard."""
        # Create players
        players = [
            ("player1", 500),
            ("player2", 300),
            ("player3", 700),
            ("player4", 100),
        ]
        
        for user_id, score in players:
            profile = get_profile(user_id)
            profile.score = score
            _profiles_repo.save(profile)
        
        # Test positions
        pos, total = get_user_position("player3")
        assert pos == 1  # Highest score
        assert total == 4
        
        pos, total = get_user_position("player1")
        assert pos == 2  # Second highest
        assert total == 4
        
        pos, total = get_user_position("player2")
        assert pos == 3  # Third
        assert total == 4
        
        pos, total = get_user_position("player4")
        assert pos == 4  # Lowest
        assert total == 4
        
        # Test non-existent player
        pos, total = get_user_position("unknown")
        assert pos == 0
        assert total == 4
    
    def test_leaderboard_with_apply_whack(self):
        """Test that apply_whack updates leaderboard correctly."""
        now = datetime.utcnow()
        
        # Player1 does some whacks
        apply_whack("player1", "target1", 300, now)  # 5 points
        apply_whack("player1", "target2", 600, now)  # 10 points
        
        # Player2 does more whacks
        apply_whack("player2", "target3", 1800, now)  # 30 points
        apply_whack("player2", "target4", 300, now)  # 5 points
        
        leaderboard = get_leaderboard(10)
        
        assert len(leaderboard) == 2
        assert leaderboard[0]['user_id'] == "player2"  # 35 points
        assert leaderboard[0]['score'] == 35
        assert leaderboard[1]['user_id'] == "player1"  # 15 points
        assert leaderboard[1]['score'] == 15
    
    def test_tier_progression_in_leaderboard(self):
        """Test that tiers are correctly shown in leaderboard."""
        # Create players at different tiers
        tiers = [
            ("bronze_player", 25, "Bronze"),
            ("silver_player", 75, "Silver"),
            ("gold_player", 250, "Gold"),
            ("platinum_player", 600, "Platinum")
        ]
        
        for user_id, score, expected_tier in tiers:
            profile = get_profile(user_id)
            profile.score = score
            # Tier should auto-update
            if score >= 500:
                profile.rank = "Platinum"
            elif score >= 200:
                profile.rank = "Gold"
            elif score >= 50:
                profile.rank = "Silver"
            else:
                profile.rank = "Bronze"
            _profiles_repo.save(profile)
        
        leaderboard = get_leaderboard(10)
        
        # Check tiers are correct
        for entry in leaderboard:
            if entry['user_id'] == "platinum_player":
                assert entry['rank'] == "Platinum"
            elif entry['user_id'] == "gold_player":
                assert entry['rank'] == "Gold"
            elif entry['user_id'] == "silver_player":
                assert entry['rank'] == "Silver"
            elif entry['user_id'] == "bronze_player":
                assert entry['rank'] == "Bronze"


class TestPersistence:
    """Test database persistence functionality."""
    
    def setup_method(self):
        """Create temp database for each test."""
        _reset_state_for_tests()
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_scores.db")
    
    def teardown_method(self):
        """Clean up temp files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_persistence_saves_and_loads(self):
        """Test that profiles persist to database and reload."""
        # Create repo with persistence
        from modules.gamification.whack_a_magat.src.whack import ProfilesRepo
        
        # First session - create profiles
        repo1 = ProfilesRepo(persist=True)
        repo1.db_path = self.db_path
        repo1._init_db()
        
        profile1 = repo1.get_or_create("user1")
        profile1.score = 150
        profile1.rank = "Silver"
        profile1.level = 2
        repo1.save(profile1)
        
        profile2 = repo1.get_or_create("user2")
        profile2.score = 300
        profile2.rank = "Gold"
        profile2.level = 4
        repo1.save(profile2)
        
        # Second session - load from database
        repo2 = ProfilesRepo(persist=True)
        repo2.db_path = self.db_path
        repo2._init_db()
        repo2._load_from_db()
        
        # Check profiles loaded correctly
        loaded1 = repo2.get_or_create("user1")
        assert loaded1.score == 150
        assert loaded1.rank == "Silver"
        assert loaded1.level == 2
        
        loaded2 = repo2.get_or_create("user2")
        assert loaded2.score == 300
        assert loaded2.rank == "Gold"
        assert loaded2.level == 4
    
    def test_leaderboard_persists(self):
        """Test that leaderboard data persists across sessions."""
        from modules.gamification.whack_a_magat.src.whack import ProfilesRepo
        
        # First session
        repo1 = ProfilesRepo(persist=True)
        repo1.db_path = self.db_path
        repo1._init_db()
        
        # Create some players
        for i in range(5):
            profile = repo1.get_or_create(f"player{i}")
            profile.score = (5 - i) * 100  # Decreasing scores
            repo1.save(profile)
        
        leaderboard1 = repo1.get_leaderboard(10)
        
        # Second session
        repo2 = ProfilesRepo(persist=True)
        repo2.db_path = self.db_path
        repo2._init_db()
        repo2._load_from_db()
        
        leaderboard2 = repo2.get_leaderboard(10)
        
        # Leaderboards should match
        assert len(leaderboard1) == len(leaderboard2)
        for i in range(len(leaderboard1)):
            assert leaderboard1[i]['user_id'] == leaderboard2[i]['user_id']
            assert leaderboard1[i]['score'] == leaderboard2[i]['score']
    
    def test_position_tracking_persists(self):
        """Test that position tracking works after reload."""
        from modules.gamification.whack_a_magat.src.whack import ProfilesRepo
        
        # First session - create players
        repo1 = ProfilesRepo(persist=True)
        repo1.db_path = self.db_path
        repo1._init_db()
        
        profiles = [
            ("alpha", 1000),
            ("beta", 500),
            ("gamma", 250)
        ]
        
        for user_id, score in profiles:
            profile = repo1.get_or_create(user_id)
            profile.score = score
            repo1.save(profile)
        
        # Second session - check positions
        repo2 = ProfilesRepo(persist=True)
        repo2.db_path = self.db_path
        repo2._init_db()
        repo2._load_from_db()
        
        pos, total = repo2.get_user_position("alpha")
        assert pos == 1
        assert total == 3
        
        pos, total = repo2.get_user_position("beta")
        assert pos == 2
        assert total == 3
        
        pos, total = repo2.get_user_position("gamma")
        assert pos == 3
        assert total == 3