# Phase 3B: Moderator Notifications - Integration Design
**Date:** 2025-12-12
**Status:** 🎯 READY TO IMPLEMENT
**Database:** Using EXISTING `auto_moderator.db` (NOT creating new database)

## Executive Summary

User directive: "we have a chat log database for modorator chat logs for the live stream no? we want to use the existing DBA for YT livechat not create a new one"

**Found:** `modules/communication/livechat/memory/auto_moderator.db` with complete moderator tracking system already built!

## Database Schema Analysis

### Table: `users` (138 rows)
```sql
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,      -- YouTube channel ID (e.g., "UC-LSSlOZwpGIRIYihaz8zCw")
    username TEXT,                 -- Display name (e.g., "Move2Japan", "JS")
    role TEXT,                     -- "OWNER", "MOD", "USER"
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,           -- ← KEY: Track active users
    message_count INTEGER,
    timeout_count INTEGER
);
```

**Sample Data:**
```
('UC-LSSlOZwpGIRIYihaz8zCw', 'Move2Japan', 'OWNER', ...)
('UC_2AskvFe9uqp9maCS6bohg', 'JS', 'MOD', ...)
('UCJ-uCjcvW4sDNVE1WDp8tpQ', 'Mike Rotch', 'USER', ...)
```

**Key Finding:** Role column already distinguishes OWNER/MOD/USER! No new schema needed.

### Table: `timeouts` (6 rows)
```sql
CREATE TABLE timeouts (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    username TEXT,
    reason TEXT,
    timestamp TIMESTAMP
);
```

Tracks moderation actions (for context, not needed for Phase 3B).

### Table: `mod_stats` (0 rows - unused)
Gamification system for mods (XP, streaks, etc.) - currently empty.

## Phase 3B Implementation Plan

### Feature: Smart Moderator Notifications

**Goal:** When processing YouTube Studio comments, check if commenter is an active moderator and post @mention notification in live chat.

### Integration Points

#### 1. Database Access Layer

**File:** `modules/communication/video_comments/src/moderator_lookup.py` (NEW - ~100 lines)

```python
"""Query existing auto_moderator.db for moderator status."""
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict

class ModeratorLookup:
    """Query existing auto_moderator.db without modifying schema."""

    def __init__(self):
        self.db_path = Path("modules/communication/livechat/memory/auto_moderator.db")
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")

    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """
        Query user by YouTube channel ID.

        Returns:
            {
                'user_id': str,
                'username': str,
                'role': str,           # "OWNER", "MOD", "USER"
                'last_seen': datetime,
                'message_count': int
            }
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT user_id, username, role, last_seen, message_count "
            "FROM users WHERE user_id = ?",
            (user_id,)
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            'user_id': row[0],
            'username': row[1],
            'role': row[2],
            'last_seen': datetime.fromisoformat(row[3]) if row[3] else None,
            'message_count': row[4]
        }

    def is_active_moderator(
        self,
        user_id: str,
        activity_window_minutes: int = 10
    ) -> tuple[bool, Optional[str]]:
        """
        Check if user is a moderator who was active in last N minutes.

        Returns:
            (is_active_mod: bool, username: Optional[str])
        """
        user = self.get_user_info(user_id)

        if not user:
            return (False, None)

        # Check role
        if user['role'] not in ('MOD', 'OWNER'):
            return (False, None)

        # Check recent activity
        if not user['last_seen']:
            return (False, None)

        cutoff = datetime.now() - timedelta(minutes=activity_window_minutes)

        if user['last_seen'] >= cutoff:
            return (True, user['username'])

        return (False, None)
```

#### 2. Comment Engagement Integration

**File:** `modules/communication/video_comments/skills/tars_like_heart_reply/comment_engagement_dae.py`

**Changes:**
- Add `ModeratorLookup` import
- Add moderator check during comment processing
- Post chat notification if active mod detected

**Modified Method:** `engage_comment()`

```python
async def engage_comment(
    self,
    comment_idx: int,
    reply_text: str = "",
    check_moderator: bool = True  # ← NEW PARAMETER
) -> Dict[str, Any]:
    """Engage with a single comment (Like + Heart + Reply)."""

    # ... existing Like + Heart logic ...

    # BEFORE replying, check if commenter is active moderator
    if check_moderator:
        commenter_id = self._extract_commenter_id(comment_idx)

        if commenter_id:
            is_mod, mod_name = self.mod_lookup.is_active_moderator(
                commenter_id,
                activity_window_minutes=10
            )

            if is_mod:
                logger.info(f"[MOD DETECTED] {mod_name} is active mod - posting notification")
                await self._post_chat_notification(mod_name)

    # ... existing Reply logic ...
```

**New Helper Methods:**

```python
def _extract_commenter_id(self, comment_idx: int) -> Optional[str]:
    """
    Extract YouTube channel ID from comment element.

    Strategy:
    1. Find comment thread at index
    2. Locate author link element
    3. Extract channel ID from href="/channel/UC-XXXXX"
    """
    try:
        threads = self.driver.find_elements(By.TAG_NAME, 'ytcp-comment-thread')
        thread = threads[comment_idx - 1]

        # Find author link
        author_link = thread.find_element(By.CSS_SELECTOR, 'a[href*="/channel/"]')
        href = author_link.get_attribute('href')

        # Extract channel ID
        # href format: "https://www.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw"
        if '/channel/' in href:
            channel_id = href.split('/channel/')[-1].split('?')[0]
            return channel_id

        return None
    except Exception as e:
        logger.warning(f"[MOD-LOOKUP] Failed to extract commenter ID: {e}")
        return None

async def _post_chat_notification(self, mod_name: str):
    """
    Post notification in live chat that mod commented.

    Strategy:
    1. Open new tab to YouTube Studio live chat
    2. Type message: "@{mod_name} commented on the community tab! ✊✋🖐️"
    3. Send message
    4. Close tab, return to comments

    NOTE: This requires live chat to be active. If no stream, skip.
    """
    try:
        # Check if stream is live
        # (implementation depends on stream detection system)

        message = f"@{mod_name} commented on the community tab! ✊✋🖐️"

        # Use existing AutoModeratorDAE to post message
        # (requires integration with livechat module)

        logger.info(f"[MOD-NOTIFY] Posted: {message}")
    except Exception as e:
        logger.warning(f"[MOD-NOTIFY] Failed to post notification: {e}")
```

#### 3. Chat Notification System

**Two Options:**

**Option A: Direct Integration with AutoModeratorDAE**
- Import `AutoModeratorDAE` from livechat module
- Call `post_message()` method directly
- Requires AutoModeratorDAE to be running

**Option B: Message Queue**
- Write notification to shared queue file
- AutoModeratorDAE polls queue every pulse
- Decoupled, works even if processes separate

**Recommended:** Option A (direct integration) if running in same daemon process, Option B (queue) if separate processes.

## File Structure

```
modules/communication/video_comments/
├── src/
│   ├── moderator_lookup.py            # ← NEW (100 lines)
│   └── realtime_comment_dialogue.py   # Existing
├── skills/
│   └── tars_like_heart_reply/
│       ├── comment_engagement_dae.py  # ← MODIFY (add mod check)
│       └── run_skill.py               # ← MODIFY (add --check-mods flag)

modules/communication/livechat/
└── memory/
    └── auto_moderator.db              # ← EXISTING (no schema changes!)
```

## Example Flow

### Scenario: JS (moderator) comments on video

1. **Comment Engagement Loop:**
   ```
   [ENGAGE] Processing comment 1/3...
   [MOD-LOOKUP] Extracting commenter channel ID...
   [MOD-LOOKUP] Found: UC_2AskvFe9uqp9maCS6bohg
   [MOD-LOOKUP] Querying auto_moderator.db...
   [MOD-LOOKUP] User: JS, Role: MOD, Last seen: 2 minutes ago
   [MOD DETECTED] JS is active mod - posting notification
   ```

2. **Chat Notification:**
   ```
   [MOD-NOTIFY] Posting to live chat: "@JS commented on the community tab! ✊✋🖐️"
   [MOD-NOTIFY] Posted successfully
   ```

3. **Continue Engagement:**
   ```
   [LIKE] Clicking thumbs up...
   [HEART] Clicking creator heart...
   [REPLY] Typing reply text...
   [REPLY] Clicking submit...
   [ENGAGE] Comment 1 complete!
   ```

### Scenario: Regular user comments

```
[ENGAGE] Processing comment 1/3...
[MOD-LOOKUP] Extracting commenter channel ID...
[MOD-LOOKUP] Found: UCJ-uCjcvW4sDNVE1WDp8tpQ
[MOD-LOOKUP] Querying auto_moderator.db...
[MOD-LOOKUP] User: Mike Rotch, Role: USER, Last seen: 1 day ago
[MOD-LOOKUP] Not an active moderator - skipping notification
[LIKE] Clicking thumbs up...
[HEART] Clicking creator heart...
...
```

## Configuration

**CLI Flag:** `--check-mods` / `--no-check-mods`

```bash
# Enable moderator notifications (default)
python skills/tars_like_heart_reply/run_skill.py --max-comments 0 --reply-text "Thanks!"

# Disable moderator notifications
python skills/tars_like_heart_reply/run_skill.py --max-comments 0 --no-check-mods
```

**Activity Window:** Default 10 minutes (configurable)

## WSP Compliance

- ✅ **WSP 50:** Pre-Action Verification (query database before notification)
- ✅ **WSP 72:** Module Independence (reuses existing database, no coupling)
- ✅ **WSP 27:** DAE Architecture (Phase 0: Knowledge lookup)
- ✅ **WSP 91:** Observability (telemetry for mod notifications)

## Implementation Estimate

**Complexity:** LOW (simple database query + notification)
**Time:** 30-45 minutes
**Files:** 1 new, 2 modified
**Lines:** ~150 total

## Next Steps

1. ✅ **Inspect database schema** - COMPLETE
2. 🎯 **Implement ModeratorLookup** (~30 min)
3. 🎯 **Integrate into CommentEngagementDAE** (~15 min)
4. 🎯 **Test with sample moderator comment** (~15 min)
5. 🎯 **Document in ModLog** (~5 min)

## Success Metrics

**Before Phase 3B:**
- Moderator comments processed like regular comments
- No cross-platform awareness
- Manual checking required

**After Phase 3B:**
- Active moderators automatically detected
- Live chat notifications posted
- "Community tab clear!" includes mod engagement stats

---

**Status:** ✅ DESIGN COMPLETE - Ready for implementation
**Database:** REUSING auto_moderator.db (no new schema!)
**Integration:** Minimal changes, high value

*Design by 0102 on 2025-12-12 per user directive: "use the existing DBA for YT livechat not create a new one"*
