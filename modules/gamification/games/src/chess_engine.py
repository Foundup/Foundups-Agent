"""
Chess Engine - Wrapper around python-chess for chat-based play.
"""
import logging
from typing import Dict

logger = logging.getLogger(__name__)

try:
    import chess
    CHESS_AVAILABLE = True
except ImportError:
    CHESS_AVAILABLE = False
    logger.warning("[CHESS] python-chess not installed. Run: pip install python-chess")


class ChessEngine:
    """Chess game logic using python-chess."""

    def __init__(self):
        if not CHESS_AVAILABLE:
            raise ImportError("python-chess required. Install with: pip install python-chess")
        self._board = None

    def new_game(self) -> str:
        """Start a new game, return initial FEN."""
        self._board = chess.Board()
        return self._board.fen()

    def make_move(self, fen: str, move_str: str) -> Dict:
        """
        Make a move on the board.

        Args:
            fen: Current board state in FEN notation
            move_str: Move in UCI format (e.g., 'e2e4') or SAN (e.g., 'Nf3')

        Returns:
            Dict with: valid, board (new FEN), check, checkmate, stalemate, error
        """
        board = chess.Board(fen)

        # Try to parse the move
        move = None
        move_str_clean = move_str.strip().lower()

        # Try UCI format first (e2e4)
        try:
            move = chess.Move.from_uci(move_str_clean)
            if move not in board.legal_moves:
                move = None
        except (ValueError, chess.InvalidMoveError):
            pass

        # Try SAN format (Nf3, e4, O-O)
        if move is None:
            try:
                move = board.parse_san(move_str.strip())
            except (ValueError, chess.InvalidMoveError, chess.AmbiguousMoveError):
                pass

        # Check if move is valid
        if move is None or move not in board.legal_moves:
            # Provide helpful error
            legal = [board.san(m) for m in list(board.legal_moves)[:10]]
            return {
                'valid': False,
                'error': f"Legal moves include: {', '.join(legal)}..."
            }

        # Make the move
        san = board.san(move)  # Get SAN before pushing
        board.push(move)

        result = {
            'valid': True,
            'board': board.fen(),
            'move_san': san,
            'check': board.is_check(),
            'checkmate': board.is_checkmate(),
            'stalemate': board.is_stalemate(),
            'draw': board.is_insufficient_material() or board.is_fifty_moves() or board.is_repetition()
        }

        return result

    def board_to_text(self, fen: str) -> str:
        """Convert board to ASCII text representation."""
        board = chess.Board(fen)
        return str(board)

    def get_legal_moves(self, fen: str) -> list:
        """Get list of legal moves in SAN notation."""
        board = chess.Board(fen)
        return [board.san(move) for move in board.legal_moves]
