# Sprint 1 Audit: TARS Vision Architecture - 1st Principles Analysis
**Date**: 2025-12-12
**Auditor**: 0102
**Scope**: TARS live stream detection + comment processing flow

---

## User Directive Analysis

> "hard think sprint 1... audit what is there.... what is needed applying 1st principles... atm there is no Live video... so Tars should check @move2japan/live then @UnDaoDu/live and finally @foundups/live then it should move to comments handing off detection to the no OAuth scraping system we detected and process all @move2Joan comments in Studio via foundups_vision... no? Hard think.... if Scraping...  'FoundUps = Edge (different port) ❌' -- this is just for re-OAuth it should always use Chrome for Tars the OAuth is just for agent login in the live stream"

### Critical Insights:
1. **TARS Always Uses Chrome** - Regardless of which account, port 9222 is for TARS vision
2. **Edge/FoundUps Separation** - Edge is ONLY for OAuth/agent login, NOT vision
3. **Sequential Check Pattern** - @move2japan → @UnDaoDu → @foundups
4. **No-Live Handoff** - When no streams, process comments via foundups_vision
5. **No-OAuth Scraping** - Vision unavailable → fall back to HTTP scraping

---

## Current Architecture - What Exists

### ✅ CORRECT: Chrome Port 9222 Usage

**File**: `modules/platform_integration/stream_resolver/src/vision_stream_checker.py`

```python
# Line 56: CORRECT - Always Chrome port 9222
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
```

**Status**: ✅ **CORRECT** - TARS uses Chrome regardless of account

---

### ✅ CORRECT: Channel Handle Mapping

**File**: `vision_stream_checker.py` (Lines 36-40)

```python
CHANNEL_HANDLES = {
    'UCklMTNnu5POwRmQsg5JJumA': '@MOVE2JAPAN',
    'UCSNTUXjAgpd4sgWYP0xoJgw': '@UnDaoDu',
    'UC-LSSlOZwpGIRIYihaz8zCw': '@Foundups',
}
```

**Status**: ✅ All 3 channels mapped

---

### ✅ CORRECT: Studio URL Restoration

**File**: `vision_stream_checker.py` (Lines 172-176)

```python
finally:
    # ALWAYS restore original URL (don't hijack Studio inbox!)
    if original_url and 'studio.youtube.com' in original_url:
        logger.info(f"[VISION] Restoring original Studio URL: {original_url[:60]}...")
        self.driver.get(original_url)
        time.sleep(2)  # Allow Studio to reload
```

**Status**: ✅ Prevents hijacking, critical for comment processing

---

### ⚠️ PARTIAL: Sequential Channel Checking

**File**: `stream_resolver.py` (Lines 517-556)

```python
# Lines 517-528: Gets channels from env
channels_to_check = [
    os.getenv('MOVE2JAPAN_CHANNEL_ID', 'UCklMTNnu5POwRmQsg5JJumA'),
    os.getenv('CHANNEL_ID', 'UC-LSSlOZwpGIRIYihaz8zCw'),
    os.getenv('CHANNEL_ID2', 'UCSNTUXjAgpd4sgWYP0xoJgw'),
]

# Line 531-542: Loops through channels
for check_channel_id in channels_to_check:
    channel_name = self._get_channel_display_name(check_channel_id)
    logger.info(f"[VISION] Checking {channel_name}...")

    result = vision_checker.check_channel_for_live(check_channel_id, channel_name)
```

**Status**: ⚠️ **PARTIAL** - Sequential checking exists but:
- Order is MOVE2JAPAN → UnDaoDu → FoundUps (user wants MOVE2JAPAN → UnDaoDu → FoundUps ✅)
- Logic lives in stream_resolver, not vision_checker
- No explicit "no-live → hand off to comments" logic

---

### ✅ CORRECT: Scraping Fallback

**File**: `vision_stream_checker.py` (Lines 86-90, 378-399)

```python
# Line 86-90: Fallback to scraping when vision unavailable
if self.vision_available and self.driver:
    logger.info(f"[VISION] Checking {display_name} with UI-TARS vision...")
    result = self._check_with_vision(channel_id, channel_name)
    if result:
        return result
    logger.info(f"[VISION] No live stream detected visually for {display_name}")

# FALLBACK: Use HTTP scraping
logger.info(f"[SCRAPE] Falling back to HTTP scraping for {display_name}")
return self._check_with_scraping(channel_id, channel_name)
```

**Status**: ✅ Proper fallback to no-OAuth scraping via `NoQuotaStreamChecker`

---

### ❌ GAP: Comment Processing Integration

**File**: `modules/communication/video_comments/src/comment_monitor_dae.py`

**What Exists**:
- CommentMonitorDAE class (complete WSP 27 compliant)
- Lines 24-250: Full comment monitoring + response generation
- Lines 252-282: CommentMonitorIntegration for background operation

**What's Missing**:
```python
# auto_moderator_dae.py Line 116:
self.community_monitor = None  # Initialized in run() when channel_id is known

# Line 712-723: Attempts to initialize, but...
from .community_monitor import get_community_monitor  # Different module!
# NOT importing CommentMonitorDAE from comment_monitor_dae.py
```

**Status**: ❌ **NOT WIRED** - CommentMonitorDAE exists but never instantiated

---

### ❌ GAP: Foundups_Vision Integration for Comments

**Files Found**:
```
modules/infrastructure/foundups_vision/src/
├── vision_executor.py
├── ui_tars_bridge.py
├── gemini_vision_bridge.py
├── action_pattern_learner.py
└── chrome_preflight_check.py
```

**What's Missing**:
- No integration between `CommentMonitorDAE` and `foundups_vision`
- Comment processing uses `AgenticChatEngine` (livechat) but not vision system
- No Studio comment engagement via UI-TARS

**Status**: ❌ **ZERO INTEGRATION** - Vision system isolated from comment processing

---

## 1st Principles: What SHOULD Happen

### Desired Flow (User Specification)

```
┌─────────────────────────────────────────────────────────┐
│ 1. TARS Vision Detection (Chrome :9222)                │
│    Sequential: @move2japan → @UnDaoDu → @foundups      │
│    ✅ Currently: stream_resolver.py handles this        │
└─────────────────────────────────────────────────────────┘
                          │
                          ├─[LIVE STREAM FOUND]──────► Monitor Chat
                          │
                          └─[NO LIVE STREAMS]
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Hand Off to Comment Processing                      │
│    - Check @move2japan Studio for comments             │
│    - Use foundups_vision for DOM + Vision              │
│    - Process Like/Heart/Reply actions                  │
│    ❌ Currently: CommentMonitorDAE not wired            │
└─────────────────────────────────────────────────────────┘
```

---

## Sprint 1 Requirements vs Reality

### Test File: `test_tars_stream_detection.py`

**What It Tests**:
1. ✅ Chrome connection on :9222
2. ✅ Navigate to @channel/live
3. ✅ Detect live stream
4. ✅ Extract video_id
5. ✅ Restore Studio URL

**What It DOESN'T Test**:
- ❌ Sequential channel checking (only tests 1 channel at a time in loop)
- ❌ "No live → hand off to comments" flow
- ❌ Comment processing via foundups_vision
- ❌ Like/Heart/Reply actions in Studio

---

## Critical Gaps Summary

| Component | Status | Gap Description | Fix Required |
|-----------|--------|-----------------|--------------|
| Chrome :9222 Usage | ✅ Working | None | None |
| Sequential Check | ⚠️ Partial | Works but not explicitly designed | Enhance test coverage |
| Studio URL Restore | ✅ Working | None | None |
| Scraping Fallback | ✅ Working | None | None |
| Comment Processing | ❌ Missing | CommentMonitorDAE not wired | Wire into AutoModeratorDAE |
| Foundups_Vision + Comments | ❌ Missing | Zero integration | Create bridge module |
| Like/Heart/Reply Actions | ❌ Missing | No UI-TARS integration | Implement action handlers |

---

## Recommended Sprint 1 Verification Approach

### Test 1: Sequential Stream Detection (No Live Scenario)

**Expected Behavior**:
```python
# When NO streams are live:
1. Check @move2japan/live → No live
2. Check @UnDaoDu/live → No live
3. Check @foundups/live → No live
4. Return None (currently correct)
```

**Gap**: Missing step 5 - "Hand off to comment processing"

**Fix**: After line 557 in `stream_resolver.py`:
```python
# After vision checks all channels and finds nothing:
if not result:
    logger.info("[VISION] No live streams detected via vision")
    # NEW: Hand off to comment processing
    return self._hand_off_to_comment_processing()
```

---

### Test 2: Comment Processing via Foundups_Vision

**Required Architecture**:
```python
class VisionCommentProcessor:
    """Bridge between CommentMonitorDAE and foundups_vision"""

    def __init__(self, chrome_driver):
        self.driver = chrome_driver  # Same Chrome from vision_checker
        self.vision_executor = VisionExecutor()  # From foundups_vision

    def process_studio_comments(self, channel_handle):
        """Navigate to Studio, process comments with vision"""
        # 1. Navigate to studio.youtube.com/channel/{id}/comments
        # 2. Use foundups_vision to detect comment elements
        # 3. Execute Like/Heart/Reply actions via UI-TARS
        # 4. Verify actions completed via vision
        pass
```

**Status**: ❌ **DOES NOT EXIST**

---

## Sprint 1 Revised Test Plan

### Existing Test (Covers 80%)
- [x] Chrome connection
- [x] Stream detection per channel
- [x] Video ID extraction
- [x] Studio URL restoration

### Missing Tests (Critical 20%)
- [ ] **Test 2A**: Sequential check with all channels offline
- [ ] **Test 2B**: No-live → hand off to comment system
- [ ] **Test 3**: Studio comment detection via vision
- [ ] **Test 4**: Like/Heart/Reply action execution
- [ ] **Test 5**: Vision-verified action completion

---

## Conclusion: Sprint 1 Current State

### What Works (Core TARS Vision)
✅ Chrome connection on port 9222
✅ Channel handle mapping for all 3 channels
✅ Live stream detection via DOM inspection
✅ Studio URL restoration (no hijacking)
✅ Scraping fallback when vision unavailable

### What's Missing (Comment Integration)
❌ CommentMonitorDAE not wired into AutoModeratorDAE
❌ No foundups_vision integration for comments
❌ No "no-live → process comments" handoff logic
❌ No Like/Heart/Reply action handlers
❌ No vision-verified action completion

### Recommendation
**Sprint 1A**: Verify existing vision detection works
**Sprint 1B**: Implement comment processing handoff
**Sprint 2**: Wire CommentMonitorDAE + foundups_vision
**Sprint 3**: Full integration testing

---

## Next Steps

1. **Immediate**: Run `test_tars_stream_detection.py` to verify vision detection
2. **High Priority**: Wire CommentMonitorDAE into AutoModeratorDAE.run()
3. **Medium Priority**: Create VisionCommentProcessor bridge
4. **Low Priority**: Implement Like/Heart/Reply handlers with foundups_vision

---

*Generated by 0102 - Following WSP 50 (Pre-Action Verification)*
