# YouTube Studio Vision Test

**Created:** 2025-12-03
**Purpose:** Test foundups_vision on real-world complex UI (YouTube Studio comment liking)
**Status:** Ready to run

---

## What This Tests

✅ **Full Vision Automation Stack:**
1. **ActionRouter** - Intelligent Selenium vs Vision routing
2. **UI-TARS Vision** - Complex UI interaction (YouTube Studio)
3. **Pattern Learning** - Success/failure recording for optimization
4. **Browser Session** - Chrome profile management
5. **Error Handling** - Fallback strategies (like → heart button)

---

## Test Flow

```
Step 1: Navigate (Selenium)
   └─> https://studio.youtube.com/channel/{CHANNEL_ID}/comments/inbox

Step 2: Page Load Wait
   └─> 5 seconds for React app to render

Step 3: Vision Like (UI-TARS)
   ├─> Attempt 1: Find "thumbs up" like button
   └─> Attempt 2: Try "heart" button (creator heart fallback)
```

---

## Prerequisites

### 1. Chrome Profile Setup

**Profile Name:** `youtube_move2japan`
**Location:** `C:\Users\{USER}\AppData\Local\Google\Chrome\User Data\youtube_move2japan`

**Must be logged into YouTube with creator account**

**Verification:**
```bash
# Check profile exists
ls "C:\Users\{USER}\AppData\Local\Google\Chrome\User Data" | grep youtube_move2japan
```

### 2. UI-TARS Server (Optional)

If using Vision driver:
```bash
# Check if UI-TARS is running (optional - can fallback to Selenium)
# Vision provides better complex UI handling
```

### 3. Python Dependencies

```bash
# All dependencies should already be installed
pip install selenium asyncio logging
```

---

## How to Run

### Quick Start

```bash
# From project root
cd O:\Foundups-Agent

# Run test
python tests/test_youtube_studio_vision.py
```

### What to Expect

**Console Output:**
```
[TEST] Starting YouTube Studio Vision Test
[TEST] Channel: UC-LSSlOZwpGIRIYihaz8zCw
[TEST] Profile: youtube_move2japan
[TEST] URL: https://studio.youtube.com/channel/UC-.../comments/inbox

[TEST 1] Navigation to Studio comments inbox...
[TEST 1] ✅ Navigation successful (1234ms)

[TEST 2] Waiting for page load...
[TEST 2] ✅ Page load wait complete

[TEST 3] Liking comment via Vision...
[TEST 3] ✅ Vision like successful!
[TEST 3]    Driver: vision
[TEST 3]    Duration: 2567ms
[TEST 3]    Fallback: False

============================================================
TEST SUMMARY
============================================================

1. Navigation: ✅ PASS
   Duration: 1234ms
   Driver: selenium

2. Page Load: ✅ PASS
   Wait time: 5s

3. Vision Like: ✅ PASS
   Duration: 2567ms
   Driver: vision
   Fallback: False

Total Duration: 8901ms

============================================================
🎉 ALL TESTS PASSED - Vision automation works!
============================================================
```

**Browser Window:**
- Chrome opens with youtube_move2japan profile
- Navigates to YouTube Studio comments inbox
- You'll see the like button being clicked (vision-based)
- Browser stays open after test (for inspection)

---

## Test Scenarios

### Scenario 1: Regular Like Button (Expected)

**What Happens:**
1. Vision finds "thumbs up" like button on first comment
2. Clicks button
3. Button changes state (filled/highlighted)
4. Test passes ✅

**Vision Prompt:** "thumbs up like button on the first visible comment"

---

### Scenario 2: Creator Heart Button (Fallback)

**What Happens:**
1. Vision fails to find regular like button
2. Falls back to "heart" button (creator-specific)
3. Clicks heart button
4. Test passes ✅ with `heart_used: True`

**Vision Prompt:** "heart button to give creator heart on first comment"

---

### Scenario 3: No Comments in Inbox

**What Happens:**
1. Navigation succeeds
2. Page load succeeds
3. Vision search fails (no buttons found)
4. Test fails ❌ with error "No like button found"

**Action:** Add comments to test with or use different channel

---

## Troubleshooting

### Error: "Profile not found: youtube_move2japan"

**Solution:**
```bash
# Create profile or use different name
# Edit test_youtube_studio_vision.py line 324:
PROFILE = "Default"  # Or your profile name
```

### Error: "Navigation timeout"

**Cause:** Slow internet or YouTube Studio slow to load

**Solution:**
```python
# Increase wait time in _test_page_load() (line 165)
wait_seconds = 10  # Increase from 5 to 10
```

### Error: "Vision driver not available"

**Cause:** UI-TARS server not running

**Solution:** Test will automatically fallback to Selenium if Vision unavailable. Vision is optional but provides better complex UI handling.

### Error: "Element not found"

**Cause:** YouTube Studio UI changed or no comments visible

**Solutions:**
1. Verify comments exist in inbox
2. Adjust vision prompt in `_test_vision_like()` (line 174)
3. Use browser DevTools to inspect button structure

---

## Customization

### Test Different Channel

```python
# Edit main() function (line 319)
CHANNEL_ID = "YOUR_CHANNEL_ID_HERE"
```

### Test Different Profile

```python
# Edit main() function (line 320)
PROFILE = "your_profile_name"
```

### Add More Tests

```python
# Add to YouTubeStudioVisionTest class:
async def _test_creator_reply(self):
    """Test replying to comment"""
    result = await self.router.execute(
        'type_text',
        {
            'text': 'Thanks for watching! 🎌',
            'target': 'reply text box',
        },
        driver=DriverType.VISION,
    )
    # ...
```

---

## What Success Looks Like

✅ **All 3 tests pass:**
1. Navigation to Studio inbox
2. Page load complete
3. Vision successfully finds and clicks like button

✅ **Pattern learning records success** (for future optimization)

✅ **Browser left open** so you can see the liked comment

---

## Next Steps After Testing

### If Tests Pass ✅

**Option A:** Create WRE Skillz for autonomous comment engagement
```python
# modules/infrastructure/wre_core/skills/youtube_studio_engage.json
{
    "name": "youtube_studio_engage",
    "description": "Autonomously like and reply to YouTube Studio comments",
    "agent": "qwen",
    "triggers": ["new_comment_notification", "daily_engagement_check"]
}
```

**Option B:** Integrate into Auto Moderator DAE
```python
# modules/communication/livechat/src/auto_moderator_dae.py
# Add Studio comment monitoring alongside live chat
```

**Option C:** Create event-driven workflow
```python
# New comment → Event queue → Vision like → Pattern learning
```

### If Tests Fail ❌

1. **Check logs** - Detailed error info in console
2. **Inspect browser** - Left open for manual verification
3. **Adjust prompts** - Vision descriptions in `_test_vision_like()`
4. **Report issue** - GitHub issue with logs + screenshots

---

## Architecture Validated

This test verifies the COMPLETE vision automation architecture from [VISION_AUTOMATION_SPRINT_MAP.md](../docs/VISION_AUTOMATION_SPRINT_MAP.md):

- ✅ Sprint A1: ActionRouter intelligent routing
- ✅ Sprint V1: Vision executor workflow
- ✅ Sprint V4: Browser session management
- ✅ Sprint V6: Pattern learning integration

**If this test passes, the entire foundups_vision stack is operational!**

---

## Related Files

| File | Purpose |
|------|---------|
| [test_youtube_studio_vision.py](test_youtube_studio_vision.py) | Test script (this test) |
| [youtube_actions.py](../modules/infrastructure/browser_actions/src/youtube_actions.py) | YouTube-specific actions |
| [action_router.py](../modules/infrastructure/browser_actions/src/action_router.py) | ActionRouter implementation |
| [browser_manager.py](../modules/infrastructure/foundups_selenium/src/browser_manager.py) | Browser session management |
| [VISION_AUTOMATION_SPRINT_MAP.md](../docs/VISION_AUTOMATION_SPRINT_MAP.md) | Complete sprint roadmap |

---

**Maintained By:** 0102
**Last Updated:** 2025-12-03
