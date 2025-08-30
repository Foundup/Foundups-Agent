# CLAUDE.md - Whack-a-MAGAT Module Memory

## Module Structure (WSP 83 Compliant)
This document helps 0102 remember all module components and paths.

## Critical Paths
- **Database**: `data/magadoom_scores.db` - SQLite database for user profiles, scores, and rankings
- **Quiz Database**: `data/quiz_data.db` - Political quiz questions and answers
- **Memory Files**: `memory/timeout_announcer.json` - Announcer statistics
- **State Files**: `src/memory/whack/whack_state.json` - Runtime state

## Core Components

### Main Engine (`src/`)
- `whack.py` - Core gamification engine with ProfilesRepo and ActionsRepo
- `timeout_announcer.py` - Duke Nukem/Quake style announcements
- `timeout_tracker.py` - Tracks timeouts and multi-kill detection
- `spree_tracker.py` - Tracks killing sprees and combos
- `quiz_engine.py` - Political quiz system
- `historical_facts.py` - Educational 1933→2025 parallels
- `self_improvement.py` - ML pattern learning for optimization
- `status_announcer.py` - Periodic status broadcasts
- `terminology_enforcer.py` - Ensures correct MAGADOOM terminology
- `mcp_whack_server.py` - Model Context Protocol server

### Data Storage
- `data/magadoom_scores.db` - Main database with tables:
  - `profiles` - User profiles with XP, ranks, levels, monthly/all-time scores
  - Excludes test_user_* entries in leaderboard queries
- `data/quiz_data.db` - Quiz questions and user answers

### Commands Available
- `/help` - Show all commands
- `/score` or `/stats` - Show XP, rank, level, whacks
- `/rank` - Show leaderboard position
- `/leaderboard` - Show monthly top players
- `/whacks` or `/frags` - Show total whack count
- `/sprees` - Show active killing sprees
- `/quiz` - Start political quiz
- `/facts` - Educational historical facts
- `/toggle` - (MOD/OWNER only) Toggle consciousness mode

### Key Classes and Functions

#### ProfilesRepo (whack.py)
- `get_or_create(user_id, username)` - Get/create user profile
- `get_leaderboard(limit, monthly)` - Get top players (filters test users)
- `apply_whack(profile, points, target_name)` - Apply points with monthly tracking
- Database path: `modules/gamification/whack_a_magat/data/magadoom_scores.db`

#### TimeoutManager (timeout_announcer.py)
- `process_timeout(mod_id, mod_name, target_name, duration, current_time)` - Main entry
- `_detect_multi_whack()` - MUST be called BEFORE apply_whack() for combos
- Returns announcements with Duke Nukem/Quake style

### Test Data Management
- Test users (test_user_*) are automatically filtered from leaderboards
- Clean test data: `python tests/cleanup_test_users.py`
- Check database: `python tests/check_database.py`

### Integration Points
- Called by: `modules/communication/livechat/src/event_handler.py`
- Commands handled by: `modules/communication/livechat/src/command_handler.py`
- Imports: `from modules.gamification.whack_a_magat import apply_whack, get_profile, get_leaderboard`

### WSP Compliance
- WSP 3: Module organization (gamification logic separated from platform code)
- WSP 17: Pattern registry in PATTERN_REGISTRY.md
- WSP 22: ModLog.md for all changes
- WSP 83: This document attaches to the tree (not orphaned)
- WSP 84: Check existing code before creating new

### Recent Issues Fixed
1. Multi-whack detection must happen BEFORE apply_whack() for combos to work
2. Test users filtered from leaderboards with `if not p.user_id.startswith('test_user')`
3. Database uses monthly_score and monthly_frag_count fields (reset each month)
4. Logger must be imported in whack.py: `import logging; logger = logging.getLogger(__name__)`

## Remember
- Always check `data/magadoom_scores.db` for persistent data
- Test users should be filtered in all public-facing queries
- Multi-whack detection timing is critical for combo multipliers