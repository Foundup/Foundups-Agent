"""
Game Manager - Orchestrates chat-based board games.

Handles matchmaking, turn management, and state persistence for OBS display.
"""
import json
import random
import threading
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# State file for OBS browser source to read
STATE_DIR = Path(__file__).parent.parent / "data"
CHESS_STATE_FILE = STATE_DIR / "chess_state.json"
CHECKERS_STATE_FILE = STATE_DIR / "checkers_state.json"


@dataclass
class GameState:
    """State of an active game."""
    game_type: str  # 'chess' or 'checkers'
    white_player: str  # Username
    black_player: str  # Username
    white_id: str  # User ID
    black_id: str  # User ID
    current_turn: str  # 'white' or 'black'
    board_fen: str  # FEN for chess, custom string for checkers
    moves: list  # Move history
    started_at: str
    status: str  # 'active', 'white_wins', 'black_wins', 'draw', 'resigned'
    last_move: str = ""


class GameManager:
    """Manages active games and matchmaking."""

    def __init__(self):
        self._lock = threading.Lock()
        self._waiting_chess: Optional[Tuple[str, str]] = None  # (username, user_id)
        self._waiting_checkers: Optional[Tuple[str, str]] = None
        self._active_chess: Optional[GameState] = None
        self._active_checkers: Optional[GameState] = None

        # Ensure data directory exists
        STATE_DIR.mkdir(parents=True, exist_ok=True)

        # Initialize engines lazily
        self._chess_engine = None
        self._checkers_engine = None

    def _get_chess_engine(self):
        """Lazy load chess engine."""
        if self._chess_engine is None:
            from .chess_engine import ChessEngine
            self._chess_engine = ChessEngine()
        return self._chess_engine

    def _get_checkers_engine(self):
        """Lazy load checkers engine."""
        if self._checkers_engine is None:
            from .checkers_engine import CheckersEngine
            self._checkers_engine = CheckersEngine()
        return self._checkers_engine

    def join_chess(self, username: str, user_id: str) -> Dict:
        """
        Join or start a chess game.

        Returns dict with response message and game state.
        """
        with self._lock:
            # Check if already in a game
            if self._active_chess:
                if user_id in (self._active_chess.white_id, self._active_chess.black_id):
                    return {
                        'status': 'already_playing',
                        'message': f"@{username} you're already in a game! Use !move to play or !resign to quit."
                    }
                return {
                    'status': 'game_in_progress',
                    'message': f"@{username} a game is in progress. Wait for it to finish!"
                }

            # Check if user is already waiting
            if self._waiting_chess and self._waiting_chess[1] == user_id:
                return {
                    'status': 'already_waiting',
                    'message': f"@{username} you're already waiting for an opponent..."
                }

            # If no one waiting, join queue
            if self._waiting_chess is None:
                self._waiting_chess = (username, user_id)
                return {
                    'status': 'waiting',
                    'message': f"@{username} waiting for opponent... Type !chess to play!"
                }

            # Second player joins - start game!
            player1 = self._waiting_chess
            player2 = (username, user_id)
            self._waiting_chess = None

            # Random color assignment
            players = [player1, player2]
            random.shuffle(players)
            white, black = players

            # Initialize game
            engine = self._get_chess_engine()
            board_fen = engine.new_game()

            self._active_chess = GameState(
                game_type='chess',
                white_player=white[0],
                black_player=black[0],
                white_id=white[1],
                black_id=black[1],
                current_turn='white',
                board_fen=board_fen,
                moves=[],
                started_at=datetime.now().isoformat(),
                status='active'
            )

            # Write state for OBS
            self._write_chess_state()

            return {
                'status': 'started',
                'message': f"GAME ON! @{white[0]} (white) vs @{black[0]} (black) | @{white[0]} your move! (!move e2e4)",
                'game': self._active_chess
            }

    def join_checkers(self, username: str, user_id: str) -> Dict:
        """Join or start a checkers game."""
        with self._lock:
            # Check if already in a game
            if self._active_checkers:
                if user_id in (self._active_checkers.white_id, self._active_checkers.black_id):
                    return {
                        'status': 'already_playing',
                        'message': f"@{username} you're already in a game! Use !move to play or !resign to quit."
                    }
                return {
                    'status': 'game_in_progress',
                    'message': f"@{username} a game is in progress. Wait for it to finish!"
                }

            if self._waiting_checkers and self._waiting_checkers[1] == user_id:
                return {
                    'status': 'already_waiting',
                    'message': f"@{username} you're already waiting for an opponent..."
                }

            if self._waiting_checkers is None:
                self._waiting_checkers = (username, user_id)
                return {
                    'status': 'waiting',
                    'message': f"@{username} waiting for opponent... Type !checkers to play!"
                }

            # Start game
            player1 = self._waiting_checkers
            player2 = (username, user_id)
            self._waiting_checkers = None

            players = [player1, player2]
            random.shuffle(players)
            white, black = players

            engine = self._get_checkers_engine()
            board_state = engine.new_game()

            self._active_checkers = GameState(
                game_type='checkers',
                white_player=white[0],
                black_player=black[0],
                white_id=white[1],
                black_id=black[1],
                current_turn='white',
                board_fen=board_state,
                moves=[],
                started_at=datetime.now().isoformat(),
                status='active'
            )

            self._write_checkers_state()

            return {
                'status': 'started',
                'message': f"GAME ON! @{white[0]} (white) vs @{black[0]} (black) | @{white[0]} your move! (!move a3b4)",
                'game': self._active_checkers
            }

    def make_move(self, username: str, user_id: str, move: str) -> Dict:
        """
        Make a move in the active game.

        Args:
            username: Player's display name
            user_id: Player's YouTube ID
            move: Move notation (e.g., 'e2e4' for chess, 'a3b4' for checkers)
        """
        with self._lock:
            # Check chess game first
            if self._active_chess:
                game = self._active_chess
                engine = self._get_chess_engine()
                state_file = CHESS_STATE_FILE
                write_fn = self._write_chess_state
            elif self._active_checkers:
                game = self._active_checkers
                engine = self._get_checkers_engine()
                state_file = CHECKERS_STATE_FILE
                write_fn = self._write_checkers_state
            else:
                return {
                    'status': 'no_game',
                    'message': f"@{username} no active game! Type !chess or !checkers to start."
                }

            # Check if it's this player's turn
            is_white = user_id == game.white_id
            is_black = user_id == game.black_id

            if not (is_white or is_black):
                return {
                    'status': 'not_playing',
                    'message': f"@{username} you're not in this game!"
                }

            player_color = 'white' if is_white else 'black'
            if game.current_turn != player_color:
                opponent = game.white_player if game.current_turn == 'white' else game.black_player
                return {
                    'status': 'not_your_turn',
                    'message': f"@{username} wait your turn! It's @{opponent}'s move."
                }

            # Try to make the move
            result = engine.make_move(game.board_fen, move)

            if not result['valid']:
                return {
                    'status': 'invalid_move',
                    'message': f"@{username} invalid move '{move}'! {result.get('error', 'Try again.')}"
                }

            # Update game state
            game.board_fen = result['board']
            game.moves.append(move)
            game.last_move = move
            game.current_turn = 'black' if game.current_turn == 'white' else 'white'

            # Check for game end
            if result.get('checkmate'):
                game.status = f'{player_color}_wins'
                write_fn()
                winner = game.white_player if player_color == 'white' else game.black_player
                loser = game.black_player if player_color == 'white' else game.white_player
                self._end_game(game.game_type)
                return {
                    'status': 'checkmate',
                    'message': f"CHECKMATE! @{winner} defeats @{loser}! GG!"
                }

            if result.get('stalemate') or result.get('draw'):
                game.status = 'draw'
                write_fn()
                self._end_game(game.game_type)
                return {
                    'status': 'draw',
                    'message': f"DRAW! @{game.white_player} vs @{game.black_player} - well played!"
                }

            if result.get('no_pieces'):
                game.status = f'{player_color}_wins'
                write_fn()
                winner = game.white_player if player_color == 'white' else game.black_player
                self._end_game(game.game_type)
                return {
                    'status': 'win',
                    'message': f"@{winner} WINS! All opponent pieces captured!"
                }

            # Game continues
            write_fn()
            next_player = game.white_player if game.current_turn == 'white' else game.black_player
            check_msg = " CHECK!" if result.get('check') else ""

            return {
                'status': 'moved',
                'message': f"{move}{check_msg} | @{next_player} your move!"
            }

    def resign(self, username: str, user_id: str) -> Dict:
        """Player resigns from current game."""
        with self._lock:
            game = None
            game_type = None

            if self._active_chess and user_id in (self._active_chess.white_id, self._active_chess.black_id):
                game = self._active_chess
                game_type = 'chess'
            elif self._active_checkers and user_id in (self._active_checkers.white_id, self._active_checkers.black_id):
                game = self._active_checkers
                game_type = 'checkers'

            if not game:
                # Check waiting queue
                if self._waiting_chess and self._waiting_chess[1] == user_id:
                    self._waiting_chess = None
                    return {'status': 'left_queue', 'message': f"@{username} left the chess queue."}
                if self._waiting_checkers and self._waiting_checkers[1] == user_id:
                    self._waiting_checkers = None
                    return {'status': 'left_queue', 'message': f"@{username} left the checkers queue."}
                return {'status': 'no_game', 'message': f"@{username} you're not in a game!"}

            # Determine winner
            is_white = user_id == game.white_id
            winner = game.black_player if is_white else game.white_player
            loser = username

            game.status = 'resigned'
            self._end_game(game_type)

            return {
                'status': 'resigned',
                'message': f"@{loser} resigned! @{winner} wins!"
            }

    def get_board(self, username: str, game_type: str = None) -> Dict:
        """Get current board state as text."""
        with self._lock:
            game = None
            engine = None

            if game_type == 'chess' or (game_type is None and self._active_chess):
                game = self._active_chess
                engine = self._get_chess_engine() if game else None
            elif game_type == 'checkers' or (game_type is None and self._active_checkers):
                game = self._active_checkers
                engine = self._get_checkers_engine() if game else None

            if not game:
                return {'status': 'no_game', 'message': f"@{username} no active game!"}

            board_text = engine.board_to_text(game.board_fen)
            turn = game.white_player if game.current_turn == 'white' else game.black_player

            return {
                'status': 'board',
                'message': f"{game.game_type.upper()} | {game.white_player} vs {game.black_player} | @{turn}'s turn",
                'board': board_text
            }

    def _end_game(self, game_type: str):
        """Clear game state after game ends."""
        if game_type == 'chess':
            self._active_chess = None
        elif game_type == 'checkers':
            self._active_checkers = None

    def _write_chess_state(self):
        """Write chess state to JSON for OBS browser source."""
        if self._active_chess:
            state = asdict(self._active_chess)
            CHESS_STATE_FILE.write_text(json.dumps(state, indent=2))

    def _write_checkers_state(self):
        """Write checkers state to JSON for OBS browser source."""
        if self._active_checkers:
            state = asdict(self._active_checkers)
            CHECKERS_STATE_FILE.write_text(json.dumps(state, indent=2))


# Singleton instance
_game_manager: Optional[GameManager] = None
_manager_lock = threading.Lock()


def get_game_manager() -> GameManager:
    """Get singleton GameManager instance."""
    global _game_manager
    with _manager_lock:
        if _game_manager is None:
            _game_manager = GameManager()
        return _game_manager
