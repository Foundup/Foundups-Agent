# Games Module - Interface

## Public API

### GameManager

```python
from modules.gamification.games.src.game_manager import get_game_manager

gm = get_game_manager()

# Join chess game (creates or waits for opponent)
result = gm.join_chess(username: str, user_id: str) -> Dict
# Returns: {status, message, game?}
# status: 'waiting', 'started', 'already_playing', 'game_in_progress'

# Join checkers game
result = gm.join_checkers(username: str, user_id: str) -> Dict

# Make a move
result = gm.make_move(username: str, user_id: str, move: str) -> Dict
# move format: 'e2e4' (chess UCI) or 'a3b4' (checkers)
# Returns: {status, message}
# status: 'moved', 'invalid_move', 'not_your_turn', 'checkmate', 'draw'

# Resign from current game
result = gm.resign(username: str, user_id: str) -> Dict

# Get board state as text
result = gm.get_board(username: str, game_type: str = None) -> Dict
```

## Chat Commands

| Command | Description |
|---------|-------------|
| `!chess` | Join/start chess game |
| `!checkers` | Join/start checkers game |
| `!move xxx` | Make move (e.g., `!move e2e4`) |
| `!resign` | Forfeit current game |
| `!board` | Display current board |

## State Files (for OBS Browser Source)

- `data/chess_state.json` - Current chess game state
- `data/checkers_state.json` - Current checkers game state

### State JSON Format

```json
{
  "game_type": "chess",
  "white_player": "Alice",
  "black_player": "Bob",
  "white_id": "UC...",
  "black_id": "UC...",
  "current_turn": "white",
  "board_fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
  "moves": ["e2e4"],
  "started_at": "2026-03-05T12:00:00",
  "status": "active",
  "last_move": "e2e4"
}
```

## OBS Browser Sources

- `assets/chess_board.html` - Chess board display (800x800)
- `assets/checkers_board.html` - Checkers board display (800x800)

Poll state files every 1 second for updates.
