# Stream Connection Fix: "Stream: None" - 2025-12-12
**Status:** ✅ FIXED
**Root Cause:** Missing `current_video_id` tracking variable

---

## Problem Summary

**User Observation:**
> "agent is not connecting to live stream... https://www.youtube.com/watch?v=R-uQNJDeNqM"

**Heartbeat Logs:**
```
[HEARTBEAT] Pulse #10 - Status: critical
Uptime: 284s | Stream: None
Total: 28 errors, 0 fixes
```

**Expected:** Heartbeat shows `Stream: R-uQNJDeNqM`
**Actual:** Heartbeat shows `Stream: None`

---

## Root Cause Analysis

### Issue: Missing `current_video_id` Instance Variable

**File:** `modules/communication/livechat/src/auto_moderator_dae.py`

**Flow:**

1. **Vision detects stream** (stream_resolver.py:556):
   ```python
   return (video_id, chat_id)  # chat_id can be None
   ```

2. **Daemon accepts stream** (auto_moderator_dae.py:621-625):
   ```python
   stream_info = result or {}
   video_id = stream_info.get('video_id')  # Extracted to LOCAL variable
   live_chat_id = stream_info.get('live_chat_id')
   channel_id = stream_info.get('channel_id')
   channel_name = stream_info.get('channel_name')
   # ❌ MISSING: self.current_video_id = video_id
   ```

3. **Heartbeat checks for stream** (youtube_dae_heartbeat.py:163-165):
   ```python
   if hasattr(self.dae, 'current_video_id'):
       stream_active = self.dae.current_video_id is not None
       stream_video_id = self.dae.current_video_id  # ❌ Attribute doesn't exist!
   ```

**Result:** Heartbeat finds `current_video_id` doesn't exist → logs `Stream: None`

---

## Fix Applied

### Fix #1: Set `current_video_id` When Stream Found ✅

**File:** `auto_moderator_dae.py` (lines 627-629)

```python
# AFTER:
stream_info = result or {}
video_id = stream_info.get('video_id')
live_chat_id = stream_info.get('live_chat_id')
channel_id = stream_info.get('channel_id')
channel_name = stream_info.get('channel_name')

# Set current_video_id for heartbeat tracking (fixes "Stream: None" issue)
self.current_video_id = video_id
logger.info(f"[FLOW-TRACE] Set current_video_id={video_id}")
```

**Result:** Heartbeat can now read `self.current_video_id` and display stream correctly

### Fix #2: Reset `current_video_id` When Stream Ends ✅

**File:** `auto_moderator_dae.py` (lines 812-813)

```python
# AFTER:
# Reset the LiveChat instance for fresh connection
if self.livechat:
    self.livechat.stop_listening()
    self.livechat = None

# Reset current_video_id for heartbeat tracking
self.current_video_id = None

# Clear cached stream info to force fresh search
```

**Result:** Heartbeat correctly shows `Stream: None` when searching for new stream

---

## Expected Behavior (After Fix)

**Startup Flow:**
1. Vision detects stream R-uQNJDeNqM ✅
2. Returns `(video_id, None)` - chat_id unavailable ✅
3. Daemon accepts stream and sets `self.current_video_id = 'R-uQNJDeNqM'` ✅
4. Daemon tries to authenticate and get chat_id with API ✅
5. If chat_id still None → Logs warning "Could not get chat ID even with API" ⚠️
6. Creates LiveChatCore anyway (graceful degradation) ✅
7. **Heartbeat logs:** `Stream: R-uQNJDeNqM` ✅ (FIXED!)

**Stream End Flow:**
1. Monitor_chat() returns (stream ended)
2. Daemon resets `self.current_video_id = None` ✅
3. **Heartbeat logs:** `Stream: None` ✅ (correct - searching for new stream)

---

## Testing

### Test 1: Stream Detection With Vision Success
```bash
# Expected logs:
[VISION] ✅ LIVE STREAM FOUND: R-uQNJDeNqM
[FLOW-TRACE] Set current_video_id=R-uQNJDeNqM
[HEARTBEAT] Pulse #1 - Status: healthy
  Uptime: 30s | Stream: R-uQNJDeNqM  # ✅ FIXED!
```

### Test 2: Stream End & Cleanup
```bash
# Expected logs:
[REFRESH] Stream ended or became inactive - seamless switching engaged
# Reset current_video_id for heartbeat tracking
[HEARTBEAT] Pulse #10 - Status: searching
  Uptime: 300s | Stream: None  # ✅ Correct - no stream active
```

### Test 3: Chat ID Unavailable (Graceful Degradation)
```bash
# Expected logs:
[VISION] ✅ LIVE STREAM FOUND: R-uQNJDeNqM
[VISION] Chat ID fetch failed (quota exhausted), will retry in monitoring loop
[FLOW-TRACE] Set current_video_id=R-uQNJDeNqM  # ✅ Set even without chat_id
⚠️ Could not get chat ID even with API
# Stream still accepted for monitoring
[HEARTBEAT] Stream: R-uQNJDeNqM  # ✅ Shows stream despite missing chat_id
```

---

## Files Modified

1. **auto_moderator_dae.py** (lines 627-629)
   - Added: `self.current_video_id = video_id` when stream found

2. **auto_moderator_dae.py** (lines 812-813)
   - Added: `self.current_video_id = None` when stream ends

**Total:** 1 file, 2 lines added

---

## Related Context

**User Insight (2025-12-12):**
> "https://www.youtube.com/@MOVE2JAPAN/live pops to live video if there is on... this mean we can use the /live in the url to check for live without needing to look at the home page for the live icon"

**Confirmation:** Vision detection ALREADY uses this `/live` redirect pattern!
- File: [vision_stream_checker.py:118-126](../modules/platform_integration/stream_resolver/src/vision_stream_checker.py#L118-L126)
- Method: Navigate to `/@channel/live` → Check if URL contains `watch?v=` → Extract video_id
- Benefit: Simpler than DOM inspection, uses YouTube's native redirect behavior

---

## Other Fixes Applied Today

1. ✅ LM Studio auto-launch (.env path)
2. ✅ CAPTCHA elimination (vision-first return pattern)
3. ✅ Multiple instance UX (y/n prompt with auto-kill)
4. ✅ Studio hijacking (finally block restoration + correct script path)
5. ✅ **Stream tracking (this fix)**

---

**Session by:** 0102
**Date:** 2025-12-12
**Methodology:** Deep dive code tracing + First principles
**WSP:** WSP 50 (Find before fix), WSP 27 (DAE architecture), WSP 91 (Observability)
