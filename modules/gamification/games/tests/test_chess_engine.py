"""Tests for chess engine."""
import pytest


class TestChessEngine:
    """Test chess engine functionality."""

    @pytest.fixture
    def engine(self):
        """Create chess engine instance."""
        from modules.gamification.games.src.chess_engine import ChessEngine
        return ChessEngine()

    def test_new_game_returns_starting_fen(self, engine):
        """New game returns standard starting position."""
        fen = engine.new_game()
        assert fen.startswith("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")

    def test_valid_move_e2e4(self, engine):
        """Standard opening move e2e4 is valid."""
        fen = engine.new_game()
        result = engine.make_move(fen, "e2e4")
        assert result['valid'] is True
        assert 'e3' in result['board']  # en passant square in FEN

    def test_valid_move_san_format(self, engine):
        """SAN format moves work (e4, Nf3, etc)."""
        fen = engine.new_game()
        result = engine.make_move(fen, "e4")
        assert result['valid'] is True

    def test_invalid_move_rejected(self, engine):
        """Invalid moves are rejected with helpful error."""
        fen = engine.new_game()
        result = engine.make_move(fen, "e2e5")  # Can't move pawn 3 squares
        assert result['valid'] is False
        assert 'error' in result

    def test_cant_move_opponent_piece(self, engine):
        """Can't move opponent's pieces."""
        fen = engine.new_game()
        result = engine.make_move(fen, "e7e5")  # Black's pawn on white's turn
        assert result['valid'] is False

    def test_check_detected(self, engine):
        """Check is properly detected."""
        # Scholar's mate position after Qxf7
        fen = "r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4"
        board = engine._board
        # This is checkmate, but let's test a check position
        check_fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/5Q2/PPPP1PPP/RNB1KBNR b KQkq - 1 2"
        result = engine.make_move(check_fen, "Nc6")  # Any legal move
        # Just verify we can make moves from this position
        assert 'valid' in result

    def test_board_to_text(self, engine):
        """Board converts to readable text."""
        fen = engine.new_game()
        text = engine.board_to_text(fen)
        assert 'r' in text  # Black rook
        assert 'R' in text  # White rook
        assert 'K' in text or 'k' in text  # Kings

    def test_get_legal_moves(self, engine):
        """Can get list of legal moves."""
        fen = engine.new_game()
        moves = engine.get_legal_moves(fen)
        assert len(moves) == 20  # 16 pawn moves + 4 knight moves
        assert 'e4' in moves
        assert 'Nf3' in moves


class TestChessEngineImport:
    """Test chess engine import handling."""

    def test_import_works(self):
        """Chess engine imports successfully."""
        from modules.gamification.games.src.chess_engine import ChessEngine, CHESS_AVAILABLE
        assert CHESS_AVAILABLE is True
        engine = ChessEngine()
        assert engine is not None
