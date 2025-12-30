# Livechat Notification for Comment Engagement - 2025-12-24

**Status**: DESIGN PHASE

---

## Problem

**User Issue**: "there is no more posts... it should send a message to the live chat if one is running with message all comments... how does it know all comments are processed? hard think... otherwise the system will remain spanning page with no comments?"

**Current Behavior**:
- Comment engagement DAE detects "no comments" ([comment_engagement_dae.py:732-735](O:\Foundups-Agent\modules\communication\video_comments\skills\tars_like_heart_reply\comment_engagement_dae.py#L732-L735))
- Breaks loop silently
- Session ends with no notification
- Community unaware that inbox was cleared

**Detection Concern**: Infinite page refreshing with zero comments = massive bot signature

---

## Current Stop Logic

**Code** ([comment_engagement_dae.py:732-735](O:\Foundups-Agent\modules\communication\video_comments\skills\tars_like_heart_reply\comment_engagement_dae.py#L732-L735)):

```python
if not has_comment:
    logger.info(f"[DAEMON][PHASE--1] ⚪ NO COMMENTS FOUND - Inbox is clear!")
    logger.info("[DAE] No comments found")
    break
```

**Session Summary** ([comment_engagement_dae.py:863-869](O:\Foundups-Agent\modules\communication\video_comments\skills\tars_like_heart_reply\comment_engagement_dae.py#L863-L869)):

```python
logger.info(f"\n{'='*60}")
logger.info(f" SESSION COMPLETE")
logger.info(f" Processed: {self.stats['comments_processed']}")
logger.info(f" Likes: {self.stats['likes']}")
logger.info(f" Hearts: {self.stats['hearts']}")
logger.info(f" Replies: {self.stats['replies']}")
logger.info(f"{'='*60}\n")
```

**Outputs to**: Logs only (not livechat)

---

## Solution Design

### Pattern: Livechat Integration (from youtube_dae_heartbeat.py)

**How YouTube DAE sends messages**:

```python
# 1. DAE has reference to livechat instance
if hasattr(self.dae, 'livechat') and self.dae.livechat is not None:
    # 2. Use throttled send_chat_message
    await self.dae.livechat.send_chat_message(
        message_text="✊✋🖐️ Message here",
        response_type='general',
        skip_delay=False
    )
```

### Implementation Plan

**Step 1: Add Livechat Reference to __init__()**

**File**: `comment_engagement_dae.py`
**Location**: `__init__()` method (around line 170)

```python
def __init__(
    self,
    channel_id: str,
    video_id: str = None,
    use_vision: bool = True,
    use_dom: bool = True,
    check_moderators: bool = False,
    parent_pid: Optional[int] = None,
    livechat_sender=None,  # NEW: Optional livechat reference for notifications
):
    # ... existing init code ...
    self.livechat_sender = livechat_sender  # Store reference
```

**Step 2: Send Notification When No Comments Found**

**File**: `comment_engagement_dae.py`
**Location**: After line 735 (in the "no comments" detection block)

```python
if not has_comment:
    logger.info(f"[DAEMON][PHASE--1] ⚪ NO COMMENTS FOUND - Inbox is clear!")
    logger.info("[DAE] No comments found")

    # ANTI-SPAM: Notify livechat that inbox is clear
    if self.livechat_sender and total_processed > 0:
        try:
            message = f"✊✋🖐️ Comment inbox cleared! Processed {total_processed} comment{'s' if total_processed != 1 else ''} this session."
            await self.livechat_sender.send_chat_message(
                message_text=message,
                response_type='general',
                skip_delay=True  # Priority notification
            )
            logger.info(f"[DAEMON][NOTIFY] Sent completion message to livechat")
        except Exception as e:
            logger.error(f"[DAEMON][NOTIFY] Failed to send livechat notification: {e}")

    break
```

**Step 3: Send Summary at Session End (Optional Enhancement)**

**File**: `comment_engagement_dae.py`
**Location**: After line 869 (in session summary section)

```python
# Send session summary to livechat (if processing 3+ comments)
if self.livechat_sender and self.stats['comments_processed'] >= 3:
    try:
        summary = f"✊✋🖐️ Session complete! {self.stats['comments_processed']} comments | {self.stats['likes']} likes | {self.stats['hearts']} hearts | {self.stats['replies']} replies"
        await self.livechat_sender.send_chat_message(
            message_text=summary,
            response_type='general',
            skip_delay=True
        )
        logger.info(f"[DAEMON][NOTIFY] Sent session summary to livechat")
    except Exception as e:
        logger.error(f"[DAEMON][NOTIFY] Failed to send session summary: {e}")
```

**Step 4: Wire Up from community_monitor.py**

**File**: `community_monitor.py`
**Location**: Where CommentEngagementDAE is instantiated (needs research to find exact line)

```python
# Pass livechat reference when creating DAE
dae = CommentEngagementDAE(
    channel_id=self.channel_id,
    use_vision=False,
    use_dom=True,
    check_moderators=True,
    parent_pid=os.getpid(),
    livechat_sender=self.livechat  # NEW: Wire up livechat for notifications
)
```

---

## Message Examples

### Scenario 1: No Comments Found (Empty Inbox)

**Current**: Silent break
**New**:
```
✊✋🖐️ Comment inbox cleared! Processed 0 comments this session.
```

### Scenario 2: 1-2 Comments Processed

**Current**: Silent break
**New**:
```
✊✋🖐️ Comment inbox cleared! Processed 2 comments this session.
```

### Scenario 3: 3+ Comments Processed

**Current**: Silent break
**New**:
```
✊✋🖐️ Comment inbox cleared! Processed 5 comments this session.
✊✋🖐️ Session complete! 5 comments | 5 likes | 5 hearts | 5 replies
```

---

## Anti-Spam Considerations

**When to Notify**:
- ✅ Always notify when "no comments found" AND `total_processed > 0`
- ✅ Send session summary only if 3+ comments processed (avoid spam for small batches)
- ✅ Use `skip_delay=True` for priority notifications (won't trigger throttle)

**When NOT to Notify**:
- ❌ Empty inbox from start (0 processed) - silent operation
- ❌ Single comment runs (test mode)
- ❌ If livechat is offline (graceful degradation)

---

## Benefits

**For Users**:
- ✅ Know when inbox is clear (transparency)
- ✅ See engagement stats in real-time
- ✅ Confirms bot is working

**For Anti-Detection**:
- ✅ Prevents infinite refresh loops (user knows it stopped)
- ✅ Human-like behavior (announce completion of tasks)
- ✅ Adds authenticity (bot communicates status)

**For Monitoring**:
- ✅ Easy to verify bot is running correctly
- ✅ Session metrics visible to community
- ✅ Moderators can track activity

---

## Implementation Checklist

- [ ] Add `livechat_sender` parameter to `CommentEngagementDAE.__init__()`
- [ ] Send notification when "no comments found" (line 735)
- [ ] Send session summary for 3+ comments (line 869)
- [ ] Wire up livechat reference from `community_monitor.py`
- [ ] Test with live stream running
- [ ] Update ModLog.md

---

## Testing Plan

**Test 1: Empty Inbox**
```
Condition: No comments in inbox
Expected: "✊✋🖐️ Comment inbox cleared! Processed 0 comments this session."
```

**Test 2: Single Comment**
```
Condition: 1 comment processed
Expected: "✊✋🖐️ Comment inbox cleared! Processed 1 comment this session."
(No summary - avoid spam)
```

**Test 3: Multiple Comments**
```
Condition: 5 comments processed
Expected:
  - "✊✋🖐️ Comment inbox cleared! Processed 5 comments this session."
  - "✊✋🖐️ Session complete! 5 comments | 5 likes | 5 hearts | 5 replies"
```

**Test 4: Livechat Offline**
```
Condition: No livechat running
Expected: Silent operation (graceful degradation, logs only)
```

---

**Status**: READY FOR IMPLEMENTATION
**Priority**: HIGH (prevents infinite refresh loops + improves transparency)
**WSP Compliance**: WSP 91 (DAEmon Observability), WSP 50 (Pre-Action Research)
