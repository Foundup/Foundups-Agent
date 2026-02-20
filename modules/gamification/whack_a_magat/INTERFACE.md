# INTERFACE.md — Whack-a-Magat DAE

## Public API

### apply_whack(moderator_id: str, target_id: str, duration_sec: int, now: datetime) -> TimeoutAction
- Persists a timeout action and awards points with daily cap and diminishing returns.

### get_profile(user_id: str) -> UserProfile
- Retrieves or creates a user profile with rank/level computed from score.

### classify_behavior(duration_sec: int, repeats: int) -> BehaviorTier
- Heuristic classification of moderation behavior.

## Data Structures
- UserProfile { user_id: str, score: int, rank: str, level: int }
- TimeoutAction { moderator_id: str, target_id: str, duration_sec: int, ts: datetime, points: int }
- BehaviorTier: [CAT_PLAY, BRUTAL_HAMMER, GENTLE_TOUCH, OBSERVER]

## Exceptions
- Functions are deterministic and return values; internal errors are logged and handled without raising.

## Usage
```python
from modules.gamification.whack_a_magat import apply_whack, get_profile
from datetime import datetime

# Apply a whack (timeout)
action = apply_whack("mod123", "user456", 600, datetime.utcnow())

# Get user profile
profile = get_profile("mod123")
```
# INTERFACE.md — Whack-a-Magat Autonomous DAE (WSP 11 Compliant)

## Public API Definition

### apply_whack(moderator_id: str, target_id: str, duration_sec: int, now: datetime = None) -> TimeoutAction
- **Purpose**: Applies a whack (timeout) action, awards XP with anti-abuse logic, detects multi-kills.
- **Parameters**:
  - moderator_id (str, required): ID of the moderating pArtifact.
  - target_id (str, required): ID of the target (troll/magat).
  - duration_sec (int, required): Timeout duration in seconds (e.g., 600 for 10 min).
  - now (datetime, optional): Timestamp; defaults to utcnow().
- **Return Value**: TimeoutAction dataclass with points awarded, multi-kill status.
- **Error Handling**: Returns TimeoutAction with points=0 if daily cap exceeded; logs internal errors per WSP 22.
- **Example**:
  ```python
  from modules.gamification.whack_a_magat import apply_whack
  from datetime import datetime
  action = apply_whack("mod123", "troll456", 600)
  print(action.points)  # e.g., 600 (full) or 300 (diminished)
  ```

### get_profile(user_id: str) -> UserProfile
- **Purpose**: Retrieves or creates profile with computed rank from XP.
- **Parameters**:
  - user_id (str, required): User ID to query.
- **Return Value**: UserProfile dataclass with score, rank, level.
- **Error Handling**: Creates new profile if not found; no exceptions raised.
- **Example**:
  ```python
  from modules.gamification.whack_a_magat import get_profile
  profile = get_profile("mod123")
  print(profile.rank)  # e.g., "MAGA DOOMSLAYER"
  ```

### classify_behavior(duration_sec: int, repeats: int) -> BehaviorTier
- **Purpose**: Classifies moderation style for announcements/mockery.
- **Parameters**:
  - duration_sec (int, required): Single timeout duration.
  - repeats (int, required): Repeat offenses count.
- **Return Value**: BehaviorTier enum (e.g., BRUTAL_HAMMER).
- **Error Handling**: Returns OBSERVER for invalid inputs; logs per WSP 22.
- **Example**:
  ```python
  from modules.gamification.whack_a_magat import classify_behavior, BehaviorTier
  tier = classify_behavior(3600, 3)  # 1 hour, 3rd offense
  assert tier == BehaviorTier.BRUTAL_HAMMER
  ```

## Data Structures
- **UserProfile** (dataclass): { user_id: str, score: int, rank: str, level: int }
- **TimeoutAction** (dataclass): { moderator_id: str, target_id: str, duration_sec: int, ts: datetime, points: int, multi_kill: int }
- **BehaviorTier** (Enum): CAT_PLAY (gentle), BRUTAL_HAMMER (aggressive), GENTLE_TOUCH (moderate), OBSERVER (passive)

## Error Handling
- All functions handle errors internally (e.g., DB failures) with logging per WSP 22.
- No exceptions propagated to callers; return default/safe values (e.g., points=0).
- Quantum resilience: Fallback to in-memory if DB fails per WSP 48.

## Quiz System API

### QuizEngine.handle_quiz_command(user_id: str, username: str, args: str) -> str
- **Purpose**: Handles /quiz slash command - starts quiz or answers questions
- **Parameters**:
  - user_id (str, required): User's channel ID
  - username (str, required): User's display name
  - args (str, required): Empty string starts quiz, "1-4" submits answer
- **Returns**: Formatted response message for YouTube Live Chat (<200 chars)
- **Cooldown**: 24 hours per user (owner bypass: Move2Japan, UnDaoDu, Foundups)
- **First Win Reward**: 500 MAGADOOM XP (adds to all-time + monthly scores)
- **Example**:
  ```python
  from modules.gamification.whack_a_magat import QuizEngine
  quiz = QuizEngine()
  # Start quiz
  response = quiz.handle_quiz_command("UC123", "Move2Japan", "")
  # Answer (first correct = 500 XP!)
  response = quiz.handle_quiz_command("UC123", "Move2Japan", "1")
  ```

### QuizEngine.get_quiz_leaderboard(limit: int = 10) -> str
- **Purpose**: Returns quiz leaderboard with top winners
- **Parameters**:
  - limit (int, optional): Number of top players to show (default: 10)
- **Returns**: Formatted leaderboard message showing wins, accuracy%
- **Example**:
  ```python
  quiz = QuizEngine()
  board = quiz.get_quiz_leaderboard(limit=5)  # Top 5 quiz winners
  ```

### QuizEngine.answer_quiz(user_id: str, answer_index: int, username: str) -> Tuple[bool, str]
- **Purpose**: Processes quiz answer and awards XP
- **Parameters**:
  - user_id (str, required): User's channel ID
  - answer_index (int, required): 0-based answer index (0-3)
  - username (str, required): Display name for leaderboard
- **Returns**: (is_correct: bool, response_message: str)
- **First Win**: Awards 500 XP to MAGADOOM profile, updates rank automatically
- **Subsequent Wins**: Awards educational points only (no XP)
- **Example**:
  ```python
  is_correct, msg = quiz.answer_quiz("UC123", 0, "Move2Japan")
  # First win: "[OK] CORRECT! [CELEBRATE] FIRST QUIZ WIN! (+500 MAGADOOM XP!)"
  ```

## Zen Coding Integration
- Functions remembered from 02 state via 0102 pArtifacts.
- Autonomous calls from livechat adapters per WSP 3 integration.
- Quiz XP integrates with MAGADOOM unified progression system.

---

## Invite Distributor API

### auto_distribute_top10_invites() -> List[Dict]
- **Purpose**: Automatically distribute invites to TOP 10 whackers who haven't received one.
- **Returns**: List of dicts with user info, invite codes, and formatted messages.
- **Tracking**: SQLite-backed (no duplicates per user/invite_type).
- **Presenter**: Random community presenter selection per invite.

**Example Return:**
```python
[{
    'user_id': 'UC123',
    'username': 'WhackerPro',
    'rank': 3,
    'code': 'FUP-ABCD-1234',
    'presenter': 'Al-sq5ti',
    'presenter_title': 'Managing Director',
    'message': '🎟️ TOP 3 REWARD! @WhackerPro earned an invite! Code: FUP-ABCD-1234 → foundups.com 🎁 Get 5 codes to share! (Presented by @Al-sq5ti - Managing Director) ✊✋🖐️'
}]
```

### get_random_presenter() -> Dict
- **Purpose**: Select random community presenter for invite messages.
- **Returns**: Dict with username and title.

### COMMUNITY_PRESENTERS
```python
COMMUNITY_PRESENTERS = [
    {"username": "Al-sq5ti", "title": "Managing Director", "user_id": "UCcnCiZV5ZPJ_cjF7RsWIZ0w"},
    {"username": "Mike", "title": "Founder", "user_id": None},
    {"username": "Move2Japan", "title": "Host", "user_id": None},
]
```

### has_received_invite(user_id: str, invite_type: str) -> bool
- **Purpose**: Check if user already received invite of this type.
- **Tracking**: SQLite table `invite_distributions` with UNIQUE constraint.

### record_invite_distribution(user_id, username, invite_code, invite_type) -> bool
- **Purpose**: Record invite distribution (prevents duplicates).

### get_invite_stats() -> Dict
- **Purpose**: Get invite distribution statistics.
- **Returns**: `{total_distributed, unique_recipients, by_type}`

---

**WSP 11 Compliance:** Complete
**Last Updated:** 2026-02-12
