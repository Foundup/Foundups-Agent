# Comment Engagement Channel Rotation Issue

## Problem Statement

When running WITHOUT live chat, the comment engagement system:
1. ✅ Processes comments on Move2Japan channel
2. ❌ Does NOT switch to UnDaoDu/FoundUps after completing Move2Japan
3. ❌ Subprocess exits after first channel instead of rotating

## Expected Behavior

```
1. Process ALL Move2Japan community comments
2. Switch account to UnDaoDu
3. Process ALL UnDaoDu community comments
4. Switch account to FoundUps (if needed)
5. Process ALL FoundUps community comments
6. THEN check for live streams
```

## Current Behavior

```
1. Process ALL Move2Japan community comments
2. Subprocess exits
3. System goes back to stream detection loop
4. UnDaoDu/FoundUps comments are NEVER processed
```

## Root Cause Analysis

### File: `modules/communication/livechat/src/auto_moderator_dae.py`

**Line 1059-1066**: Startup launches ONE subprocess for default channel:
```python
self._comment_engagement_task = asyncio.create_task(
    self._run_comment_engagement(
        self.studio_runner,
        default_channel_id,  # UC-LSSlOZwpGIRIYihaz8zCw (Move2Japan)
        video_id=None,
        max_comments=startup_max,  # 0 = UNLIMITED
        mode=exec_mode
    )
)
```

**Line 915-960**: `_run_comment_engagement()` method:
```python
async def _run_comment_engagement(self, runner, channel_id, video_id, max_comments, mode):
    """Run comment engagement with pluggable execution strategy."""
    logger.info(f"[DAEMON][CARDIOVASCULAR] 🎬 _run_comment_engagement STARTED")

    result = await runner.run_engagement(
        channel_id=channel_id,  # Single channel only!
        video_id=video_id,
        max_comments=max_comments
    )

    logger.info(f"[DAEMON][CARDIOVASCULAR] ✅ runner.run_engagement() returned!")
    # Logs result and EXITS - no rotation logic!
```

**Missing Logic**: After subprocess completes, there is NO logic to:
1. Detect that all comments on Move2Japan are processed
2. Switch to UnDaoDu account
3. Launch new subprocess for UnDaoDu
4. Repeat for all accounts

### Account Switching Code Exists But Is Unused

**Line 717-728**: Account switching code exists but only runs during stream detection:
```python
# This code exists but only triggers when NO LIVE STREAM is found
logger.info(f"[ROTATE] Starting comment engagement for {target_account} ({target_channel_id})...")
self._comment_engagement_task = asyncio.create_task(
    self._run_comment_engagement(
        self.studio_runner,
        target_channel_id,
        video_id=None,
        max_comments=startup_max,
        mode=exec_mode
    )
)
```

This code is ONLY reachable when:
- System is searching for live streams
- NO live stream is found
- System decides to rotate to next account

It does NOT run when comment engagement subprocess completes!

## Observed Symptoms

From user logs:
```
2025-12-27 06:12:03,730 - Starting comment engagement for Move2Japan
2025-12-27 06:13:43,733 - [OFFLINE] No live streams found on any of the 3 channels
```

**Timeline**:
1. 06:12:03 - Comment engagement starts on Move2Japan
2. 06:13:43 - Stream detection finds NO live streams
3. **Missing**: No comment engagement for UnDaoDu
4. **Missing**: No comment engagement for FoundUps

## Like/Heart Action Issue

From screenshot: Reply was posted but Like/Heart were NOT executed.

**Need to verify**:
- Are `do_like=True` and `do_heart=True` being passed correctly?
- Is `--no-engagement` flag being set somewhere?
- Are DOM selectors working correctly?

Check engagement_runner.py command construction.

## Solution Architecture

### Option 1: Multi-Channel Engagement Loop (Recommended)

Add channel rotation logic to `_run_comment_engagement`:

```python
async def _run_comment_engagement_all_channels(self, runner, mode, max_comments):
    """Run comment engagement on ALL channels in rotation."""
    channels = [
        ("Move2Japan", "UC-LSSlOZwpGIRIYihaz8zCw"),
        ("UnDaoDu", "UCSNTUXjAgpd4sgWYP0xoJgw"),
        ("FoundUps", "UCfHM9Fw9HD-NwiS0seD_oIA"),
    ]

    for account_name, channel_id in channels:
        logger.info(f"[ROTATE] Processing {account_name} comments...")

        # Switch account (if not already on it)
        if account_name != "Move2Japan":  # Skip switch for first account
            switch_result = await switch_studio_account(account_name)
            if not switch_result.get("success"):
                logger.warning(f"[ROTATE] Failed to switch to {account_name}, skipping")
                continue

        # Process all comments on this channel
        result = await runner.run_engagement(
            channel_id=channel_id,
            video_id=None,
            max_comments=max_comments  # 0 = UNLIMITED
        )

        stats = result.get('stats', {})
        processed = stats.get('comments_processed', 0)
        logger.info(f"[ROTATE] {account_name} complete: {processed} comments processed")

    logger.info(f"[ROTATE] ✅ All channels processed")
```

### Option 2: Recursive Subprocess (Alternative)

Make `_run_comment_engagement` detect completion and auto-rotate:

```python
async def _run_comment_engagement(self, runner, channel_id, video_id, max_comments, mode):
    result = await runner.run_engagement(...)

    # After completion, check if we should rotate to next account
    current_account = self._get_account_from_channel_id(channel_id)
    next_account = self._get_next_account(current_account)

    if next_account:
        logger.info(f"[ROTATE] Switching from {current_account} to {next_account}...")
        switch_result = await switch_studio_account(next_account)

        if switch_result.get("success"):
            # Launch engagement for next account
            next_channel_id = self._get_channel_id(next_account)
            await self._run_comment_engagement(runner, next_channel_id, None, max_comments, mode)
```

## Implementation Steps

1. **Create multi-channel engagement method** in auto_moderator_dae.py
2. **Import studio_account_switcher** at top of file
3. **Replace single-channel launch** (line 1059) with multi-channel launcher
4. **Add channel mapping** helpers (account_name ↔ channel_id)
5. **Test account switching** with Sprint 1 test script
6. **Verify Like/Heart** actions are executing (check engagement_runner command flags)

## Files to Modify

- `modules/communication/livechat/src/auto_moderator_dae.py` (add channel rotation)
- `modules/communication/livechat/src/engagement_runner.py` (verify action flags)
- Test with: `python main.py` → Option 1 (YouTube DAE)

## Expected Result After Fix

```
[06:12:00] Starting multi-channel comment engagement...
[06:12:00] [1/3] Processing Move2Japan comments...
[06:12:30] Move2Japan: 15 comments processed ✓
[06:12:30] Switching to UnDaoDu...
[06:12:35] [2/3] Processing UnDaoDu comments...
[06:13:00] UnDaoDu: 8 comments processed ✓
[06:13:00] Switching to FoundUps...
[06:13:05] [3/3] Processing FoundUps comments...
[06:13:15] FoundUps: 3 comments processed ✓
[06:13:15] ✅ All channels processed (26 total comments)
[06:13:15] Checking for live streams...
```

## Priority

**HIGH** - Current system leaves UnDaoDu/FoundUps comments unprocessed indefinitely.

---

## Final Resolution (2025-12-28)

**Status:** ✅ **FIXED**

The Smart Rotation logic has been implemented and hardened. The system no longer defaults blindly to Move2Japan; it now detects the active browser session and reorders the processing queue to minimize account switching.

### Key Fixes:
1.  **Smart Session Detection**: Added `_detect_current_channel_id` using a hybrid of `window.ytcfg` extraction and URL regex.
2.  **Fast Path**: `TarsAccountSwapper` now skips redundant navigation if the browser is already on the target channel's comment page.
3.  **AttributeError Resolved**: Fixed missing `_vision_exists` internal helper in `CommentProcessor`.
4.  **Async Safety**: Wrapped blocking stream resolution calls in `asyncio.to_thread` to prevent event loop stalls during rotation.
5.  **Environment Sync**: Centralized all channel IDs in `.env` variables for cross-module consistency.

**Verification**:
- [x] UnDaoDu active session correctly detected at startup.
- [x] Initial redundant swap to Move2Japan skipped.
- [x] Multi-channel processing loop successfully cycles through M2J, UnDaoDu, and FoundUps.
- [x] Namespacing and import errors (`List`, `AttributeError`) resolved.

---

## Issue Recurrence (2025-12-30)

**Symptom:** UnDaoDu processed "0 comments" in 18 seconds, then switched to Move2Japan which processed 3 comments.

**Root Cause:** YouTube Studio uses **lazy loading** for comments. After account switch, the DOM query ran before JavaScript finished loading comment elements.

### New Fix: PHASE--1 Wait for Comments

**Problem:** The "Vision fallback REMOVED" comment at PHASE--1 explicitly trusted DOM as ground truth:
```python
# Vision fallback REMOVED - Occam's Razor principle:
# - If DOM says no comments → trust it (ground truth)
```
This was incorrect because DOM isn't ground truth until JavaScript finishes loading.

**Solution:** Added `_wait_for_comments_loaded()` method that:
1. Polls for `ytcp-comment-thread` elements (500ms intervals)
2. Checks for "empty inbox" indicators (truly no comments)
3. Times out after 15 seconds (fallback to DOM count)
4. Used on **first iteration only** (subsequent iterations use quick DOM check)

**Files Modified:**
- `modules/communication/video_comments/skills/tars_like_heart_reply/comment_engagement_dae.py`

**Expected Log Output:**
```
[ROTATE] Processing UnDaoDu comments...
[DAE-WAIT] Waiting for comments to load (timeout: 15s)...
[DAE-WAIT] ✅ Found 5 comment(s) after 3.2s
[ROTATE] ✅ UnDaoDu complete: 5 comments processed
```

**Status:** ✅ FIXED (2025-12-30)
