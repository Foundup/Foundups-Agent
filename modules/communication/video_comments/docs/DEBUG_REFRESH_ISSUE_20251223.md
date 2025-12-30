# DEBUG: Refresh Between Actions Issue - 2025-12-23

**Reporter**: User (Foundups Agent operator)
**Issue**: Page refreshing between Like and Heart actions instead of Like → Heart → Reply → 1 Refresh

---

## Expected Behavior

```
Comment #1:
  ├─ LIKE ✓
  ├─ HEART ✓
  ├─ REPLY ✓
  └─ REFRESH ↻

Comment #2:
  ├─ LIKE ✓
  ├─ HEART ✓
  ├─ REPLY ✓
  └─ REFRESH ↻
```

---

## Actual Behavior (User Report)

```
Action: LIKE ✓
↻ REFRESH (unexpected!)
Action: HEART ✓
↻ REFRESH (unexpected!)
```

---

## Code Analysis

### Refresh Trigger Points

**Only ONE refresh location**: [comment_engagement_dae.py:812](O:\Foundups-Agent\modules\communication\video_comments\skills\tars_like_heart_reply\comment_engagement_dae.py#L812)

```python
# Line 812 - ONLY refresh point
self.driver.refresh()
```

**Refresh Logic** (lines 785-828):
- **Standard 012 mode**: Refresh every 5 comments (batching enabled)
- **FAST/MEDIUM mode**: Refresh every 1 comment (no batching)
- **Probabilistic**: 70% chance refresh, 30% batch

**Current Setting**: `YT_ENGAGEMENT_TEMPO=012` → Should batch 5 comments

---

## Action Execution Flow

[comment_processor.py:433-978](O:\Foundups-Agent\modules\communication\video_comments\skills\tars_like_heart_reply\src\comment_processor.py#L433-L978)

```
engage_comment(comment_idx):
  ├─ Lines 532-573: LIKE execution
  │   └─ Lines 553-557: Vision verification (30s timeout)
  ├─ Lines 575-579: Delay between actions (0.4s-1.6s)
  ├─ Lines 581-621: HEART execution
  │   └─ Lines 601-605: Vision verification (30s timeout)
  ├─ Lines 623-627: Delay between actions (0.4s-1.6s)
  └─ Lines 629+: REPLY execution
```

**NO refresh calls between actions** - they execute sequentially.

---

## Possible Causes

### 1. Vision Verification Timeout

**Lines 553-557** (LIKE verification) and **Lines 601-605** (HEART verification):
```python
like_ok = await self._verify_action_with_vision(
    "LIKE",
    self.VISION_DESCRIPTIONS["like_verify"],
    timeout=30.0,  # 30 second timeout!
)
```

**If vision times out**: Page might appear "frozen" then suddenly jump to next state (looks like refresh).

---

### 2. Multiple Comment Loops

**Scenario**: System processing multiple comments in parallel or rapid succession:
- Comment #1: LIKE → loops back → processes Comment #2
- Comment #2: HEART → appears as "refreshed after Like"

**Check**: Are multiple `engage_comment()` calls happening simultaneously?

---

### 3. YouTube SPA Navigation

**YouTube Studio uses SPA (Single Page Application)**:
- Clicking buttons might trigger internal navigation
- DOM updates might look like "refreshes"
- Shadow DOM changes could cause visual reloads

**Check**: Is `driver.refresh()` being called OR is YouTube's SPA updating the DOM?

---

### 4. Nested Reply Processing

[comment_engagement_dae.py:766-778](O:\Foundups-Agent\modules\communication\video_comments\skills\tars_like_heart_reply\comment_engagement_dae.py#L766-L778):

```python
# Process nested replies (BEFORE refresh!)
nested_results = await self.reply_executor.process_nested_replies(
    parent_thread_idx=1,
    do_like=do_like,
    do_heart=do_heart,
    use_intelligent_reply=use_intelligent_reply
)
```

**Scenario**: After top-level comment engagement, system processes nested replies. User might see:
- Top comment: LIKE ✓
- Switch to nested reply processing
- Nested comment: HEART ✓
- **Appears as "refreshed between Like and Heart"**

---

## Diagnostic Steps

### Step 1: Add Detailed Logging

Add to [comment_processor.py:542](O:\Foundups-Agent\modules\communication\video_comments\skills\tars_like_heart_reply\src\comment_processor.py#L542):

```python
logger.info(f"[ACTION-TRACE] ═══ LIKE START ═══")
logger.info(f"[ACTION-TRACE]   Comment Index: {comment_idx}")
logger.info(f"[ACTION-TRACE]   Comment Author: {comment_data.get('author_name')}")
like_ok = await self.click_element_dom(comment_idx, 'like')
logger.info(f"[ACTION-TRACE] ═══ LIKE END (result: {like_ok}) ═══")
```

Add to [comment_processor.py:591](O:\Foundups-Agent\modules\communication\video_comments\skills\tars_like_heart_reply\src\comment_processor.py#L591):

```python
logger.info(f"[ACTION-TRACE] ═══ HEART START ═══")
logger.info(f"[ACTION-TRACE]   Comment Index: {comment_idx}")
logger.info(f"[ACTION-TRACE]   Comment Author: {comment_data.get('author_name')}")
heart_ok = await self.click_element_dom(comment_idx, 'heart')
logger.info(f"[ACTION-TRACE] ═══ HEART END (result: {heart_ok}) ═══")
```

---

### Step 2: Monitor Driver Calls

Wrap [comment_engagement_dae.py:812](O:\Foundups-Agent\modules\communication\video_comments\skills\tars_like_heart_reply\comment_engagement_dae.py#L812):

```python
import traceback
logger.info(f"[REFRESH-TRACE] ═══ REFRESH TRIGGERED ═══")
logger.info(f"[REFRESH-TRACE]   Reason: {reason}")
logger.info(f"[REFRESH-TRACE]   Comments processed: {total_processed}")
logger.info(f"[REFRESH-TRACE]   Call stack:")
for line in traceback.format_stack():
    logger.info(f"[REFRESH-TRACE]     {line.strip()}")
self.driver.refresh()
logger.info(f"[REFRESH-TRACE] ═══ REFRESH COMPLETE ═══")
```

---

### Step 3: Check Nested Reply Processing

Disable nested replies temporarily to isolate issue:

```python
# Line 766-778 - COMMENT OUT
# nested_results = await self.reply_executor.process_nested_replies(...)
nested_results = []  # Disable nested processing
```

---

### Step 4: Disable Vision Verification

Set vision timeout to 0 to skip verification:

```python
# Line 553-557
# like_ok = await self._verify_action_with_vision(...)
# Skip vision verification for testing
```

---

## Questions for User

1. **Are you seeing browser URL change** when "refresh" happens?
2. **Is the page visually reloading** (loading spinner, white flash)?
3. **Or is it just DOM elements disappearing/reappearing** (no actual reload)?
4. **Are you processing nested replies** (replies to replies)?
5. **What tempo mode are you running** (check logs for `YT_ENGAGEMENT_TEMPO`)?
6. **How many comments are you processing** (`--max-comments` value)?

---

## Next Steps

1. **Add diagnostic logging** (Step 1 above)
2. **Run single comment** (`--max-comments 1`)
3. **Capture full logs** showing Like → "Refresh" → Heart sequence
4. **Check browser DevTools Network tab** - are there XHR calls between actions?
5. **Verify comment_idx** - is it the same comment or different ones?

---

**Status**: INVESTIGATING
**Priority**: HIGH (breaks core engagement flow)
**Impact**: Actions split across refreshes → inefficient + potential YouTube rate limiting
