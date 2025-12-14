# Qwen Studio Engage - Autonomous YouTube Comment Engagement

**Created:** 2025-12-03
**Type:** WRE Skillz (Wardrobe Skills)
**Status:** Prototype - Ready for testing
**WSP Compliance:** WSP 96 (Micro Chain-of-Thought)

---

## What This Is

**Autonomous** YouTube Studio comment engagement using:
- **Qwen 1.5B**: Strategic sentiment analysis
- **Gemma 270M**: Decision validation
- **Vision AI (UI-TARS)**: UI interaction (like/heart/reply)
- **Pattern Memory**: Recursive learning

**Key Difference from Manual Test:**
- ❌ Manual test = One-off validation
- ✅ Skillz = Autonomous recurring operation

---

## Why This Approach (Following WSP)

### User's Corrections Applied ✅

**1. "No need to log in - user is already logged in"**
- Uses `BrowserManager.get_browser('youtube_move2japan')`
- Connects to **existing browser session**
- No new window, no login required

**2. "System needs to be agentic"**
- Not a manual test script
- WRE Skillz that executes autonomously
- Triggered by events or periodic checks

**3. "Most efficient: studio.youtube.com/channel"**
- Uses Studio inbox (unified view of all videos)
- More efficient than checking each video
- API documentation confirms: "Must use YouTube Studio interface"

### Occam's Razor Applied

**Question:** Manual test vs Agentic Skillz?

**Analysis:**
```
Manual Test:
- Good for: Initial validation, debugging
- Bad for: Recurring engagement, autonomous operation
- Effort: Run script manually each time

Agentic Skillz:
- Good for: Autonomous 24/7 engagement, learning over time
- Bad for: Initial debugging (harder to inspect)
- Effort: Set up once, runs forever
```

**Decision:** Created **BOTH**
- Manual test (`test_youtube_studio_vision.py`) for initial validation
- Agentic Skillz (`qwen_studio_engage/`) for production use

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    TRIGGER                               │
│  ├─> Event Queue (new comment notification)            │
│  └─> Periodic Check (every 30 min)                     │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              EXISTING BROWSER (No Login!)                │
│  BrowserManager.get_browser('youtube_move2japan')      │
│  └─> Uses existing logged-in session                   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   NAVIGATION                             │
│  studio.youtube.com/channel/{ID}/comments/inbox        │
│  └─> Unified inbox (all videos, one place)             │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              QWEN ANALYSIS (Strategic)                   │
│  1. Sentiment: positive/neutral/negative                │
│  2. Engagement Value: 1-5                               │
│  3. Action: like_only/like_and_reply/heart/ignore       │
│  4. Reply Text: Generated if needed                     │
│  └─> 300-600ms reasoning time                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│            GEMMA VALIDATION (Fast Check)                 │
│  - Required fields present?                             │
│  - Values in valid ranges?                              │
│  - Reply quality acceptable?                            │
│  └─> <50ms validation time                             │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│          VISION EXECUTION (UI Interaction)               │
│  Based on VISION_UI_REFERENCE.md:                       │
│  - Thumbs up: Gray icon → Shows count                  │
│  - Creator heart: Gray outline → RED filled ❤️          │
│  - Reply: Click Reply → Type → Submit                   │
│  └─> 2-8 seconds per action                            │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│            PATTERN MEMORY (Learning)                     │
│  Records:                                                │
│  - Which sentiments get best engagement                 │
│  - Optimal reply templates                              │
│  - Vision success rates                                 │
│  └─> Gets smarter over time                            │
└─────────────────────────────────────────────────────────┘
```

---

## Files Created

### 1. SKILL.md (370 lines)
**Purpose:** Complete Skillz specification
**Content:**
- Micro Chain-of-Thought steps
- Input/output contracts
- Qwen/Gemma instructions
- Integration points

### 2. VISION_UI_REFERENCE.md (400 lines)
**Purpose:** Precise Vision UI targeting
**Content:**
- Action bar layout (Reply | 0 replies | 👍 | 👎 | ♡ | ⋮)
- Visual state indicators (gray → red heart, count on like)
- Vision targeting strategies
- Verification patterns
- **Based on your actual screenshots!**

### 3. executor.py (500 lines)
**Purpose:** Skillz execution engine
**Content:**
- `execute_skill()` main entry point
- Qwen analysis logic
- Gemma validation
- Vision engagement workflows
- Pattern memory integration

### 4. __init__.py
**Purpose:** Module exports

### 5. README.md (this file)
**Purpose:** Usage guide

---

## How to Use

### Quick Test (Validates Everything)

```bash
# From project root
python tests/test_qwen_studio_engage.py
```

**What it does:**
1. Connects to existing browser (youtube_move2japan profile)
2. Navigates to Studio inbox
3. Analyzes 3 comments (small batch for testing)
4. Qwen decides engagement strategy
5. Gemma validates decision
6. Vision executes actions
7. Reports results

**Expected output:**
```
QWEN STUDIO ENGAGE - Autonomous Comment Engagement Test
============================================================

Configuration:
  Channel: UC-LSSlOZwpGIRIYihaz8zCw
  Max Comments: 3
  Existing Browser: Yes

RESULTS
============================================================

✅ Skill Execution: SUCCESS

Metrics:
  Comments Analyzed: 3
  Engagements Made: 2
  Likes Given: 1
  Hearts Given: 1
  Replies Sent: 1
  Engagement Rate: 66.7%
  Total Duration: 12450ms

Detailed Results:
  Comment 1:
    Action: like_and_reply
    Success: True
    ✓ Liked
    💬 Replied

  Comment 2:
    Action: creator_heart
    Success: True
    ❤️ Creator Heart Given

  Comment 3:
    Action: ignored
    Success: True
```

---

### Production Use (Autonomous)

**Option A: Event-Driven (Real-Time)**

Wire into event queue (from DAEMON_ARCHITECTURE_MAP.md):

```python
# modules/communication/livechat/src/auto_moderator_dae.py
# When new comment detected:

from modules.ai_intelligence.ai_overseer.src.mcp_integration import MCPIntegration

mcp = MCPIntegration()
event = {
    'event_type': 'youtube_comment',
    'source_daemon': 'auto_moderator_dae',
    'payload': {
        'channel_id': 'UC-LSSlOZwpGIRIYihaz8zCw',
        'comment_id': comment_id,
    },
    'priority': 1
}

await mcp.event_queue.put(event)
```

**HoloDAE consumes and executes Skillz:**
```python
# holo_index/qwen_advisor/services/monitoring_loop.py
async def _handle_youtube_comment_event(self, event):
    from modules.communication.livechat.skills.qwen_studio_engage import execute_skill

    result = await execute_skill(
        channel_id=event['payload']['channel_id'],
        max_comments_to_check=1,  # Process one comment per event
    )
```

---

**Option B: Periodic (Backup/Batch)**

Add to HoloDAE monitoring loop:

```python
# Every 30 minutes, check Studio inbox
async def _periodic_studio_check(self):
    from modules.communication.livechat.skills.qwen_studio_engage import execute_skill

    result = await execute_skill(
        channel_id="UC-LSSlOZwpGIRIYihaz8zCw",
        max_comments_to_check=10,  # Batch process
    )
```

---

## Configuration

### Engagement Policy

```python
engagement_policy = {
    "like_threshold": 0.7,      # Min confidence to like
    "reply_threshold": 0.8,     # Min confidence to reply
    "ignore_spam": True,        # Skip spam comments
    "ignore_toxicity": True,    # Skip toxic comments
    "brand_voice": "helpful, friendly, professional"
}
```

**Adjust thresholds** based on pattern memory feedback:
- Too many engagements? Raise thresholds
- Missing good comments? Lower thresholds

---

## Vision UI Elements (From Screenshots)

### Action Bar
```
Reply | 0 replies ▼ | 👍 | 👎 | ♡ | ⋮
```

### States (Visual Feedback)

**Not Engaged:**
- Thumbs up: Gray
- Heart: Gray outline

**After Engagement:**
- Thumbs up: Shows count "1"
- Heart: **RED filled** ❤️

**Can do both:**
- Thumbs up "1" + RED heart simultaneously ✅

See [VISION_UI_REFERENCE.md](VISION_UI_REFERENCE.md) for complete targeting guide.

---

## Learning Over Time

Pattern Memory tracks:
- **Sentiment patterns**: Which sentiments get best responses?
- **Reply templates**: Which replies get most likes/responses?
- **Timing**: Best time of day for engagement?
- **Vision accuracy**: Which UI elements are Vision finding fastest?

**Result:** Skillz gets better at engagement over weeks/months.

---

## Next Steps

### 1. Test Manual Script First
```bash
python tests/test_youtube_studio_vision.py
```
- Validates Vision can interact with Studio UI
- Confirms browser connection works
- Visual verification (browser stays open)

### 2. Test Agentic Skillz
```bash
python tests/test_qwen_studio_engage.py
```
- Validates full Qwen → Gemma → Vision flow
- Checks autonomous decision-making
- Verifies Pattern Memory integration

### 3. Deploy to Production

**Once tests pass:**
1. Wire into event queue (Option A)
2. Add periodic check (Option B)
3. Monitor Pattern Memory for improvements
4. Adjust thresholds based on results

---

## WSP Compliance

- **WSP 96**: Micro Chain-of-Thought ✅ (Qwen → Gemma → Vision)
- **WSP 77**: Agent Coordination ✅ (Qwen + Gemma)
- **WSP 91**: Observability ✅ (Telemetry logging)
- **WSP 48**: Recursive Learning ✅ (Pattern Memory)
- **WSP 50**: Pre-Action Verification ✅ (Gemma validates)
- **WSP 27**: Universal DAE ✅ (Can be triggered by events)

---

## Related Files

| File | Purpose |
|------|---------|
| [SKILL.md](SKILL.md) | Complete specification |
| [VISION_UI_REFERENCE.md](VISION_UI_REFERENCE.md) | UI targeting guide (from your screenshots!) |
| [executor.py](executor.py) | Implementation |
| [test_qwen_studio_engage.py](../../../../../tests/test_qwen_studio_engage.py) | Test script |
| [DAEMON_ARCHITECTURE_MAP.md](../../../../../docs/DAEMON_ARCHITECTURE_MAP.md) | Event queue integration |

---

**Maintained By:** 0102 Communication Team
**Status:** Prototype - Ready for autonomous deployment
**Last Updated:** 2025-12-03

**Your screenshots made this possible!** 📸 The Vision UI reference is based on actual Studio interface you provided.
