"""Tests for checkers engine."""
import pytest


class TestCheckersEngine:
    """Test checkers engine functionality."""

    @pytest.fixture
    def engine(self):
        """Create checkers engine instance."""
        from modules.gamification.games.src.checkers_engine import CheckersEngine
        return CheckersEngine()

    def test_new_game_has_24_pieces(self, engine):
        """New game has 12 pieces per side."""
        board = engine.new_game()
        white_count = board.count('w')
        black_count = board.count('b')
        assert white_count == 12
        assert black_count == 12

    def test_new_game_correct_placement(self, engine):
        """Pieces start in correct positions."""
        board = engine.new_game()
        # White pieces on rows 1-3 (indices 0-2 in board string)
        # Row 1 (index 0-7): .w.w.w.w pattern
        # Actually rows are stored as 64 chars, row by row
        # Row 0: positions 0-7, Row 1: 8-15, etc.
        # Dark squares only have pieces
        assert board[1] == 'w'  # a1 is light, b1 is dark
        assert board[3] == 'w'
        assert board[5] == 'w'
        assert board[7] == 'w'

    def test_valid_simple_move(self, engine):
        """Valid diagonal move works."""
        board = engine.new_game()
        # White piece at b3 (row 2, col 1) can move to a4 or c4
        # b3 = row 2, col 1 = index 2*8 + 1 = 17
        # Actually let's use the move notation
        result = engine.make_move(board, "b3c4")
        assert result['valid'] is True

    def test_invalid_move_wrong_direction(self, engine):
        """Regular pieces can't move backward."""
        board = engine.new_game()
        # Try to move white piece backward (lower row)
        # First make a valid move to get a piece we can try to move back
        result1 = engine.make_move(board, "b3c4")
        assert result1['valid'] is True
        # Now try to move it back
        result2 = engine.make_move(result1['board'], "c4b3")
        assert result2['valid'] is False
        assert 'must move up' in result2['error'].lower() or 'invalid' in result2['error'].lower()

    def test_invalid_move_to_occupied(self, engine):
        """Can't move to occupied square."""
        board = engine.new_game()
        # Try to move to a square with another piece
        # All starting pieces are blocked by friendly pieces above
        result = engine.make_move(board, "b1c2")  # c2 should have a piece
        # Actually c2 is row 1, col 2 = light square, no piece
        # Let's check the board layout more carefully
        # Pieces are on dark squares: (row+col) % 2 == 1
        # b1 = row 0, col 1 -> (0+1)%2 = 1 -> dark, has piece
        # c2 = row 1, col 2 -> (1+2)%2 = 1 -> dark, has piece
        assert result['valid'] is False

    def test_jump_capture(self, engine):
        """Jump captures opponent piece."""
        # Set up a position where white can jump black
        # Create a custom board with one white piece and one black piece
        board = '.' * 64
        board_list = list(board)
        # White at c3 (row 2, col 2)
        board_list[2 * 8 + 2] = 'w'
        # Black at d4 (row 3, col 3)
        board_list[3 * 8 + 3] = 'b'
        board = ''.join(board_list)

        result = engine.make_move(board, "c3e5")  # Jump over d4
        assert result['valid'] is True
        # Black piece should be gone
        assert result['board'][3 * 8 + 3] == '.'
        # White piece should be at e5
        assert result['board'][4 * 8 + 4] == 'w'

    def test_king_promotion(self, engine):
        """Piece becomes king when reaching last row."""
        # Set up white piece near promotion
        board = '.' * 64
        board_list = list(board)
        # White at b7 (row 6, col 1)
        board_list[6 * 8 + 1] = 'w'
        board = ''.join(board_list)

        result = engine.make_move(board, "b7a8")  # Move to last row
        assert result['valid'] is True
        # Should be promoted to king
        assert result['board'][7 * 8 + 0] == 'W'

    def test_king_can_move_backward(self, engine):
        """Kings can move in any diagonal direction."""
        board = '.' * 64
        board_list = list(board)
        # White king at d4 (row 3, col 3)
        board_list[3 * 8 + 3] = 'W'
        board = ''.join(board_list)

        # Move backward
        result = engine.make_move(board, "d4c3")
        assert result['valid'] is True

    def test_board_to_text(self, engine):
        """Board converts to readable text."""
        board = engine.new_game()
        text = engine.board_to_text(board)
        assert 'w' in text  # White pieces
        assert 'b' in text  # Black pieces
        assert 'a' in text and 'h' in text  # Column labels
        assert '1' in text and '8' in text  # Row labels

    def test_get_legal_moves(self, engine):
        """Can get list of legal moves for a player."""
        board = engine.new_game()
        moves = engine.get_legal_moves(board, is_white_turn=True)
        assert len(moves) > 0
        # White's front row pieces should have moves
        assert any('3' in m and '4' in m for m in moves)  # Moving from row 3 to row 4


class TestCheckersWinCondition:
    """Test win conditions."""

    @pytest.fixture
    def engine(self):
        from modules.gamification.games.src.checkers_engine import CheckersEngine
        return CheckersEngine()

    def test_capture_last_piece_wins(self, engine):
        """Capturing opponent's last piece wins the game."""
        board = '.' * 64
        board_list = list(board)
        # White at c3
        board_list[2 * 8 + 2] = 'w'
        # Black's last piece at d4
        board_list[3 * 8 + 3] = 'b'
        board = ''.join(board_list)

        result = engine.make_move(board, "c3e5")  # Jump and capture
        assert result['valid'] is True
        assert result.get('no_pieces') is True
        assert result.get('winner') == 'white'
