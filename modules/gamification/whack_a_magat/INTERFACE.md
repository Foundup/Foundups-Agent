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

apply_whack("mod123", "user456", 600, datetime.utcnow())
profile = get_profile("mod123")
```
