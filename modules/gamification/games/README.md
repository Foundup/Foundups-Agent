# Games Module

Chat-based board games for YouTube Live streams. Users play via chat commands, board displays on stream.

## Supported Games

- **Chess** - Full chess with move validation via python-chess
- **Checkers** - Standard 8x8 checkers

## How It Works

1. User types `!chess` or `!checkers` to join queue
2. Second user joins, colors randomly assigned
3. Agent prompts current player: "@player your move! (!move e2e4)"
4. Board updates on stream via OBS Browser Source
5. Game continues until win/draw/resign

## Commands

| Command | Description |
|---------|-------------|
| `!chess` | Join/start chess game |
| `!checkers` | Join/start checkers game |
| `!move xxx` | Make a move (e.g., `!move e2e4`) |
| `!resign` | Forfeit current game |
| `!board` | Show current board state |

## OBS Setup

Add Browser Source for each game:
- **Chess Board**: `file:///O:/Foundups-Agent/modules/gamification/games/assets/chess_board.html`
- **Checkers Board**: `file:///O:/Foundups-Agent/modules/gamification/games/assets/checkers_board.html`

Size: 800x800 recommended

## Architecture

```
Chat Command → game_manager.py → chess/checkers_engine.py
                    ↓
              game_state.json → Browser Source reads → Visual Board
```

## Dependencies

- `python-chess` - Chess move validation and game logic
