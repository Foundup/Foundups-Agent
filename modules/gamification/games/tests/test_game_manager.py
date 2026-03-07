"""Tests for game manager."""
import pytest


class TestGameManagerChess:
    """Test chess game management."""

    @pytest.fixture
    def manager(self):
        """Create fresh game manager for each test."""
        from modules.gamification.games.src.game_manager import GameManager
        return GameManager()

    def test_first_player_waits(self, manager):
        """First player to join waits for opponent."""
        result = manager.join_chess("Alice", "UC_alice")
        assert result['status'] == 'waiting'
        assert 'waiting' in result['message'].lower()

    def test_second_player_starts_game(self, manager):
        """Second player starts the game with random colors."""
        manager.join_chess("Alice", "UC_alice")
        result = manager.join_chess("Bob", "UC_bob")

        assert result['status'] == 'started'
        assert result['game'] is not None
        assert result['game'].white_player in ['Alice', 'Bob']
        assert result['game'].black_player in ['Alice', 'Bob']
        assert result['game'].white_player != result['game'].black_player

    def test_cant_join_twice(self, manager):
        """Same player can't join twice."""
        manager.join_chess("Alice", "UC_alice")
        result = manager.join_chess("Alice", "UC_alice")
        assert result['status'] == 'already_waiting'

    def test_cant_join_during_game(self, manager):
        """Third player can't join during active game."""
        manager.join_chess("Alice", "UC_alice")
        manager.join_chess("Bob", "UC_bob")
        result = manager.join_chess("Charlie", "UC_charlie")
        assert result['status'] == 'game_in_progress'

    def test_make_move_valid(self, manager):
        """Valid move updates game state."""
        manager.join_chess("Alice", "UC_alice")
        result = manager.join_chess("Bob", "UC_bob")
        game = result['game']

        # Determine who is white
        white_name = game.white_player
        white_id = game.white_id

        result = manager.make_move(white_name, white_id, "e2e4")
        assert result['status'] == 'moved'
        assert 'e2e4' in result['message'] or 'e4' in result['message']

    def test_wrong_turn_rejected(self, manager):
        """Can't move when it's not your turn."""
        manager.join_chess("Alice", "UC_alice")
        result = manager.join_chess("Bob", "UC_bob")
        game = result['game']

        # Black tries to move first
        black_name = game.black_player
        black_id = game.black_id

        result = manager.make_move(black_name, black_id, "e7e5")
        assert result['status'] == 'not_your_turn'

    def test_resign(self, manager):
        """Player can resign."""
        manager.join_chess("Alice", "UC_alice")
        result = manager.join_chess("Bob", "UC_bob")
        game = result['game']

        result = manager.resign("Alice", "UC_alice")
        assert result['status'] == 'resigned'
        assert 'wins' in result['message']


class TestGameManagerCheckers:
    """Test checkers game management."""

    @pytest.fixture
    def manager(self):
        from modules.gamification.games.src.game_manager import GameManager
        return GameManager()

    def test_checkers_game_starts(self, manager):
        """Checkers game starts with two players."""
        manager.join_checkers("Alice", "UC_alice")
        result = manager.join_checkers("Bob", "UC_bob")

        assert result['status'] == 'started'
        assert result['game'].game_type == 'checkers'

    def test_checkers_move(self, manager):
        """Can make moves in checkers."""
        manager.join_checkers("Alice", "UC_alice")
        result = manager.join_checkers("Bob", "UC_bob")
        game = result['game']

        white_name = game.white_player
        white_id = game.white_id

        # Try a valid opening move
        result = manager.make_move(white_name, white_id, "b3c4")
        assert result['status'] == 'moved'


class TestGameManagerSingleton:
    """Test singleton behavior."""

    def test_get_game_manager_returns_same_instance(self):
        """get_game_manager returns singleton."""
        from modules.gamification.games.src.game_manager import get_game_manager

        gm1 = get_game_manager()
        gm2 = get_game_manager()
        assert gm1 is gm2


class TestGameManagerNoGame:
    """Test behavior when no game is active."""

    @pytest.fixture
    def manager(self):
        from modules.gamification.games.src.game_manager import GameManager
        return GameManager()

    def test_move_without_game(self, manager):
        """Move fails gracefully when no game."""
        result = manager.make_move("Alice", "UC_alice", "e2e4")
        assert result['status'] == 'no_game'

    def test_resign_without_game(self, manager):
        """Resign fails gracefully when no game."""
        result = manager.resign("Alice", "UC_alice")
        assert result['status'] == 'no_game'

    def test_board_without_game(self, manager):
        """Board request fails gracefully when no game."""
        result = manager.get_board("Alice")
        assert result['status'] == 'no_game'
