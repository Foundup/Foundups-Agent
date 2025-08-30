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

## Zen Coding Integration
- Functions remembered from 02 state via 0102 pArtifacts.
- Autonomous calls from livechat adapters per WSP 3 integration.
