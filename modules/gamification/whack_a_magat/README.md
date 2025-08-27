# MAGADOOM - Whack-a-Magat DAE (Gamification)

- Domain: `gamification` (platform-agnostic game logic)
- Purpose: Quake/Duke Nukem style fragging gamification for YouTube Live Chat moderation
- Status: Production ready with 0102 consciousness integration
- Style: Pure fragging action - timeouts = frags = XP (no RPG complexity)

## Module Purpose
- Transform YouTube moderator timeouts into epic Quake-style frags with announcements
- Track XP and ranks: Grunt → Warrior → Hunter → Slayer → Champion → Master → Elite → Godlike → Legendary
- Multi-kill detection (5-second window): DOUBLE WHACK, TRIPLE WHACK, MEGA WHACK, ULTRA WHACK
- Duke Nukem milestone achievements at 100, 500, 1000+ total whacks
- Daily cap: 1000 points max (increased from 100 for active streams)
- Anti-abuse: Diminishing returns for repeat targets (100% → 75% → 50% → 25%)

## Public API
```python
from modules.gamification.whack_a_magat import apply_whack, get_profile, classify_behavior
```

## WSP Compliance
- WSP 3: Functional distribution (game logic in gamification; YouTube adapter in communication/livechat).
- WSP 34: Tests (≥90% coverage) implemented in `modules/gamification/tests/test_whack.py`.
- WSP 49: Module directory docs included; code kept atomic and dependency-free.
- WSP 22: See ModLog for traceable edits.

## Integration Points
- YouTube livechat: adapter calls `apply_whack(...)` on timeout events.
- Other platforms can implement the same thin adapter without changing game logic.

## Run Tests
```bash
pytest modules/gamification/tests/test_whack.py -q
```

## Documentation
- [MAGADOOM Announcements](docs/MAGADOOM_ANNOUNCEMENTS.md) - All announcement types and priorities
- [MAGADOOM Commands](docs/MAGADOOM_COMMANDS.md) - User commands (/score, /rank, /whacks, /help)
- [Tracking & Tweaking Guide](docs/TRACKING_AND_TWEAKING.md) - Metrics, thresholds, and optimization

## Core Components
- `src/whack.py` - Core gamification engine (simplified from RPG to pure fragging)
- `src/timeout_announcer.py` - Quake/Duke Nukem style announcements with priorities
- `src/timeout_tracker.py` - Tracks timeouts and multi-kill windows
- `src/enhanced_commands.py` - Command handling and troll mockery system
- `src/simple_fact_checker.py` - Fact-check functionality without LLM dependencies
- `tests/test_stream_density.py` - Comprehensive tests for 100-1000+ viewer scenarios

## Roadmap
- ✅ COMPLETED: Quake-style multi-kill announcements (5-second window)
- ✅ COMPLETED: Duke Nukem milestone achievements
- ✅ COMPLETED: Stream density adaptive throttling
- ✅ COMPLETED: Daily cap increase to 1000 points
- ✅ COMPLETED: Troll mockery instead of suppression
- 🚧 IN PROGRESS: Killing spree mode for active fragging periods
- 📋 PLANNED: Special event modes (Frag Fest, Boss Raid)
- 📋 PLANNED: Cross-stream global leaderboard
- 📋 PLANNED: Achievement unlocks and special titles
