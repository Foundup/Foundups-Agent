# Sprint 1 Phase 1C: Multi-Channel Engagement Implementation (REVISED)

## Problem Solved

**Issue**: Comment engagement only processed Move2Japan channel, then exited. UnDaoDu and FoundUps comments were never processed.

**Expected Behavior**: Process ALL comments on ALL channels before checking for live streams.

## Solution Implemented (REVISED to use TarsAccountSwapper)

### Files Modified
1. `modules/communication/livechat/src/auto_moderator_dae.py`
2. `modules/communication/video_comments/skills/tars_account_swapper/account_swapper_skill.py`

### Changes Made

#### 1. Added FoundUps Support to TarsAccountSwapper

Updated `account_swapper_skill.py` to support 3 channels (previously only 2):
- Added FoundUps channel configuration
- Updated docstrings

**Rationale**: TarsAccountSwapper is domain-aligned (video_comments skills) and has cleaner swap + navigate pattern.

#### 2. Added Multi-Channel Engagement Method (Lines 961-1065)

```python
async def _run_multi_channel_engagement(
    self,
    runner,
    max_comments: int,
    mode: str
):
    """
    Run comment engagement across ALL channels with account switching.

    Sprint 1 Phase 1C: Multi-channel rotation
    - Process all Move2Japan comments
    - Switch to UnDaoDu, process all comments
    - Switch to FoundUps, process all comments
    - THEN check for live streams
    """
```

**Features**:
- Processes 3 channels in sequence: Move2Japan → UnDaoDu → FoundUps
- Uses `TarsAccountSwapper.swap_to()` to switch between accounts
- Handles switch failures gracefully (skips channel if switch fails)
- Direct navigation to comments inbox URLs (no manual navigation)
- Aggregates total comments processed across all channels
- Waits 2 seconds after account switch for Studio to stabilize
- Uses human_behavior for anti-detection (Bezier curves, variance)

#### 3. Updated Startup Logic (Lines 1147-1160)

**Before**:
```python
self._comment_engagement_task = asyncio.create_task(
    self._run_comment_engagement(
        self.studio_runner,
        default_channel_id,  # Only Move2Japan
        video_id=None,
        max_comments=startup_max,
        mode=exec_mode
    )
)
```

**After**:
```python
self._comment_engagement_task = asyncio.create_task(
    self._run_multi_channel_engagement(
        self.studio_runner,
        max_comments=startup_max,  # Applied to EACH channel
        mode=exec_mode
    )
)
```

## Expected Flow

```
[06:12:00] ============================================================
[06:12:00] [ROTATE] MULTI-CHANNEL COMMENT ENGAGEMENT
[06:12:00] [ROTATE] Processing 3 channels in sequence
[06:12:00] [ROTATE] Mode: subprocess | Max per channel: UNLIMITED
[06:12:00] ============================================================

[06:12:00] [ROTATE] [1/3] Processing Move2Japan comments...
[06:12:30] [ROTATE] ✅ Move2Japan complete: 15 comments processed

[06:12:30] [ROTATE] Switching to UnDaoDu...
[06:12:30] [TARS-SWAP] STARTING IMPROVED SWAP TO UnDaoDu
[06:12:32] [TARS-SWAP] ✅ Account switch selected. Waiting for session update...
[06:12:37] [TARS-SWAP] 🚀 Successfully transitioned to UnDaoDu comments.
[06:12:37] [ROTATE] ✅ Switched to UnDaoDu successfully

[06:12:39] [ROTATE] [2/3] Processing UnDaoDu comments...
[06:13:00] [ROTATE] ✅ UnDaoDu complete: 8 comments processed

[06:13:00] [ROTATE] Switching to FoundUps...
[06:13:00] [TARS-SWAP] STARTING IMPROVED SWAP TO FoundUps
[06:13:02] [TARS-SWAP] ✅ Account switch selected. Waiting for session update...
[06:13:07] [TARS-SWAP] 🚀 Successfully transitioned to FoundUps comments.
[06:13:07] [ROTATE] ✅ Switched to FoundUps successfully

[06:13:04] [ROTATE] [3/3] Processing FoundUps comments...
[06:13:15] [ROTATE] ✅ FoundUps complete: 3 comments processed

[06:13:15] ============================================================
[06:13:15] [ROTATE] ✅ MULTI-CHANNEL ENGAGEMENT COMPLETE
[06:13:15] [ROTATE] Total comments processed: 26
[06:13:15] [ROTATE] Channels processed: 3
[06:13:15] ============================================================

[06:13:15] [SEARCH] Looking for livestream...
```

## Integration with TarsAccountSwapper Skill

**Uses**:
- `modules/communication/video_comments/skills/tars_account_swapper/account_swapper_skill.py`
- `modules/infrastructure/foundups_selenium/src/human_behavior.py` (anti-detection)

**Why TarsAccountSwapper instead of studio_account_switcher?**:
1. Domain-aligned: video_comments skill vs foundups_vision infrastructure
2. Simpler: 174 lines vs 401 lines
3. Built-in swap + navigate pattern
4. Already uses human_behavior for anti-detection
5. No vision training overhead (focused on task execution)

**Account Switch Sequence** (via DOM JavaScript execution):
1. Click avatar button (shadow DOM piercing)
2. Click "Switch account" menu item (text search)
3. Click target account (text search for account name)
4. Navigate directly to comments inbox URL

**Direct Navigation URLs**:
- Move2Japan: `https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox`
- UnDaoDu: `https://studio.youtube.com/channel/UCfHM9Fw9HD-NwiS0seD_oIA/comments/inbox`
- FoundUps: `https://studio.youtube.com/channel/UCSNTUXjAgpd4sgWYP0xoJgw/comments/inbox`

## Error Handling

**Switch Failures**:
- If account switch fails, logs warning and skips that channel
- Continues to next account in rotation
- Does NOT abort entire process

**Import Errors**:
- If `TarsAccountSwapper` not available, aborts multi-channel engagement
- Logs error and returns early (cannot proceed without account switching)

**Subprocess Failures**:
- Logs error with full traceback
- Continues to next channel
- Aggregates stats for all successful channels

## Testing

### Test Multi-Channel Engagement

```bash
# Run YouTube DAE with multi-channel engagement
python main.py
# Select: 1 (YouTube DAE) → 1 (Live Chat Monitor) → 1 (012 System)
```

**Expected Results**:
1. Move2Japan inbox cleared
2. Account switches to UnDaoDu (DOM clicks visible in Chrome)
3. UnDaoDu inbox cleared
4. Account switches to FoundUps
5. FoundUps inbox cleared
6. System checks for live streams

### Verify Account Switching

```bash
# Test account switcher in isolation
python test_account_switch.py
```

**Expected Results**:
- All 3 clicks execute (avatar → switch menu → account)
- Account switch verified (URL contains expected channel ID)
- Training data recorded (3 examples per switch)

## Configuration

**Environment Variables** (no changes needed):
- `COMMUNITY_STARTUP_ENGAGE=true` - Enable comment engagement at startup
- `COMMUNITY_STARTUP_MAX_COMMENTS=0` - UNLIMITED mode (process all comments)
- `COMMUNITY_EXEC_MODE=subprocess` - Use subprocess for isolation

**Account Configuration** (hardcoded in method):
```python
accounts = [
    ("Move2Japan", "UC-LSSlOZwpGIRIYihaz8zCw"),
    ("UnDaoDu", "UCSNTUXjAgpd4sgWYP0xoJgw"),
    ("FoundUps", "UCfHM9Fw9HD-NwiS0seD_oIA"),
]
```

## Known Limitations

1. **DOM Selectors**: Account switching uses text-based search (more resilient than coordinates)
   - If YouTube changes element text or structure, selectors may need updates
   - Shadow DOM piercing may break if YouTube changes framework

2. **Chrome Session**: Requires Chrome on port 9222 with YouTube logged in
   - System navigates directly to comments inbox URLs
   - Account switches hijack active tab (expected behavior)

3. **Like/Heart Actions**: Need to verify in subprocess logs
   - Check if actions are executing correctly
   - May need DOM selector updates

## WSP Compliance

- **WSP 27**: DAE Architecture (Phase -2 → Phase 3 orchestration)
- **WSP 77**: Multi-tier coordination (TarsAccountSwapper + Comment engagement)
- **WSP 96**: WRE Skills Protocol (Subprocess execution + Skill coordination)
- **WSP 49**: Platform Integration Safety (Anti-detection via human_behavior)
- **WSP 87**: Navigation Protocol (Direct URL navigation to comments inbox)

## Next Steps

1. **Test Multi-Channel Flow**: Run full test to verify all 3 accounts process
2. **Verify Like/Heart**: Check subprocess logs for action execution
3. **Test Account Switching**: Verify TarsAccountSwapper switches work reliably
4. **Monitor Logs**: Check for any DOM selector failures or timeouts
5. **Sprint 1 Phase 1D**: Document patterns for other platforms (LinkedIn, X, Facebook)

## Files Modified

1. `modules/communication/livechat/src/auto_moderator_dae.py` (~105 lines changed)
   - Added `_run_multi_channel_engagement()` method (lines 961-1065)
   - Updated startup to use multi-channel version (lines 1147-1160)
   - Changed from `studio_account_switcher` to `TarsAccountSwapper`

2. `modules/communication/video_comments/skills/tars_account_swapper/account_swapper_skill.py` (+5 lines)
   - Added FoundUps channel configuration
   - Updated docstrings to include FoundUps

## Files Referenced

- `modules/infrastructure/foundups_selenium/src/human_behavior.py` (anti-detection)
- `modules/communication/video_comments/skills/tars_account_swapper/tars_practice_swap.py` (testing tool)

---

**Status**: ✅ IMPLEMENTED - Ready for testing

**Sprint**: Sprint 1 Phase 1C Complete

**Next**: Sprint 1 Phase 1D (Pattern Documentation) OR Sprint 2 (Platform Navigator Module)
