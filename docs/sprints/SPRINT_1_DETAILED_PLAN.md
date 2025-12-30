# Sprint 1: YouTube Account Switching + Comment Engagement Integration

**Sprint Goal**: Prove 0102 can switch between 012's YouTube accounts and enable comment engagement to rotate channels automatically

**Timeline**: 3-5 days
**Status**: Phase 1 (Pattern Learning)
**Risk Level**: LOW (building on existing infrastructure)

---

## Overview

**What We're Building**:
- Enable comment engagement to switch from Move2Japan → UnDaoDu when inbox empty
- Verify YouTube account switching works with current UI
- Record DOM interactions as UI-TARS training data
- Document pattern for replication on other platforms (LN, X, FB)

**What We're NOT Building**:
- Account creation automation
- Cross-platform switching (that's Sprint 2+)
- Fully autonomous operation (that's Phase 3)

---

## Current State Analysis

### Existing Infrastructure

**1. studio_account_switcher.py** (437 lines)
```
Location: modules/infrastructure/foundups_vision/src/studio_account_switcher.py
Status: EXISTS, UNTESTED
Coordinates: Hardcoded (may be outdated)
Accounts: Move2Japan, UnDaoDu, FoundUps
Success Rate: Claims 95%, needs verification
```

**2. Comment Engagement DAE** (video_comments/)
```
Location: modules/communication/video_comments/skills/tars_like_heart_reply/
Status: WORKS for single channel
Limitation: No channel switching capability
Current: Processes Move2Japan inbox only
```

**3. Live Chat Monitoring** (livechat/)
```
Location: modules/communication/livechat/
Status: WORKS for active live streams
Limitation: Stops when no live stream
Gap: Should fallback to comment engagement
```

### Coordinate Discrepancy (CRITICAL)

**User-Provided Coordinates** (from manual observation):
```python
# Step 1: Click avatar button
{"top": 12, "left": 355, "width": 32, "height": 32}
# Center: x=371, y=28

# Step 2: Click "Switch account" menu
{"top": 172, "left": 282, "width": 24, "height": 24}
# Center: x=294, y=184

# Step 3a: Select UnDaoDu (index 0)
{"top": 129, "left": 33, "width": 290, "height": 64}
# Center: x=178, y=161

# Step 3b: Select Move2Japan (index 1)
{"top": 193, "left": 33, "width": 290, "height": 64}
# Center: x=178, y=225
```

**Existing Code Coordinates** (studio_account_switcher.py):
```python
SWITCH_COORDINATES = {
    "avatar_button": {"x": 341, "y": 28},      # User: x=371, y=28 ❌ MISMATCH
    "switch_menu": {"x": 551, "y": 233},       # User: x=294, y=184 ❌ MISMATCH
    "account_UnDaoDu": {"x": 390, "y": 164},   # User: x=178, y=161 ❌ MISMATCH
    "account_Move2Japan": {"x": 390, "y": 95}  # User: x=178, y=225 ❌ MISMATCH
}
```

**Analysis**: ALL coordinates differ significantly. Likely causes:
- Screen resolution differences
- Browser zoom level
- Window size variations
- YouTube UI updates since code was written

**Decision Required from 012**: Which coordinates should we use?
- Option A: Update code to use 012's observed coordinates
- Option B: Make coordinates dynamic (detect elements first, then click)
- Option C: Test both sets and see which works

---

## Sprint 1 Phases (Detailed Breakdown)

### Phase 1A: Coordinate Verification (012 Interaction Method)

**Goal**: Verify YouTube account switching UI and coordinates

**Duration**: 30-60 minutes

**Prerequisites**:
```bash
1. Chrome running with remote debugging:
   chrome.exe --remote-debugging-port=9222 \
     --user-data-dir="O:/Foundups-Agent/modules/platform_integration/browser_profiles/youtube_move2japan/chrome"

2. Navigate to YouTube Studio:
   https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox

3. Ensure logged into Move2Japan account
```

**Task 1A.1: Manual Switch Test (Move2Japan → UnDaoDu)**

**Steps for 012**:
1. Open Chrome DevTools (F12)
2. Go to Elements tab
3. Click avatar button (top-right corner)
4. Note: Does menu appear? Record screenshot
5. Click "Switch account" menu item
6. Note: Does account list appear? Record screenshot
7. Click UnDaoDu account
8. Verify: URL changes to `UCSNTUXjAgpd4sgWYP0xoJgw`
9. Record: Total time taken

**Expected Outcome**:
- Account switch succeeds
- YouTube Studio reloads with UnDaoDu channel
- URL contains UnDaoDu channel ID

**If Fails**:
- Document error (screenshot + description)
- Check: Are you logged into multiple YouTube accounts?
- Check: Is the account list visible in the menu?

**Acceptance Criteria**:
- ✅ Switch completes in <10 seconds
- ✅ URL contains correct channel ID
- ✅ Studio interface shows UnDaoDu content

**Task 1A.2: Manual Switch Test (UnDaoDu → Move2Japan)**

**Steps for 012**:
1. Click avatar button
2. Click "Switch account"
3. Click Move2Japan
4. Verify: URL changes to `UC-LSSlOZwpGIRIYihaz8zCw`

**Expected Outcome**: Same as Task 1A.1 (reverse direction)

**Task 1A.3: Coordinate Measurement**

**Using Chrome DevTools**:
```javascript
// In Console, run this to get avatar button coordinates:
const avatar = document.querySelector('img#img[alt="Avatar image"]');
const rect = avatar.getBoundingClientRect();
console.log({
  top: rect.top,
  left: rect.left,
  width: rect.width,
  height: rect.height,
  centerX: rect.left + rect.width/2,
  centerY: rect.top + rect.height/2
});
```

**For 012 to Record**:
```
Avatar Button:
  - Measured top: ___px
  - Measured left: ___px
  - Measured centerX: ___px
  - Measured centerY: ___px

Switch Menu Item:
  - Measured top: ___px
  - Measured left: ___px
  - Measured centerX: ___px
  - Measured centerY: ___px

UnDaoDu Account:
  - Measured top: ___px
  - Measured left: ___px
  - Measured centerX: ___px
  - Measured centerY: ___px

Move2Japan Account:
  - Measured top: ___px
  - Measured left: ___px
  - Measured centerX: ___px
  - Measured centerY: ___px
```

**Deliverables**:
- ✅ 4 screenshots (avatar menu, switch menu, account list, switched state)
- ✅ Verified coordinates for all 4 click targets
- ✅ Total time measurement for switch sequence
- ✅ Confirmation that manual switching works 100%

---

### Phase 1B: Automated Switch Test

**Goal**: Verify existing `studio_account_switcher.py` works (or update coordinates)

**Duration**: 1-2 hours

**Prerequisites**:
- Phase 1A complete
- Chrome still running on port 9222
- Currently on Move2Japan account

**Decision Point for 012**:

**Option 1: Test Existing Code First**
```bash
cd O:\Foundups-Agent
python -c "
import asyncio
from modules.infrastructure.foundups_vision.src.studio_account_switcher import switch_studio_account

async def test():
    result = await switch_studio_account('UnDaoDu')
    print(f'Result: {result}')

asyncio.run(test())
"
```

**Expected Outcomes**:
- ✅ SUCCESS: Switch completes, result['success'] = True
- ❌ FAILURE: Coordinates mismatch, click doesn't hit target

**Option 2: Update Coordinates First**
```python
# If existing code fails, update coordinates based on Phase 1A measurements
# Edit: modules/infrastructure/foundups_vision/src/studio_account_switcher.py

SWITCH_COORDINATES = {
    "avatar_button": {
        "x": <012_measured_centerX>,
        "y": <012_measured_centerY>,
        "width": 32,
        "height": 32,
        "description": "YouTube Studio avatar button",
    },
    # ... update other coordinates
}
```

**Task 1B.1: Run Automated Test (UnDaoDu Switch)**

**Command**:
```bash
cd O:\Foundups-Agent\modules\infrastructure\foundups_vision
python -m pytest tests/test_account_switcher.py::test_switch_to_undaodu -v
```

**Expected Output**:
```
test_account_switcher.py::test_switch_to_undaodu PASSED [100%]

[ACCOUNT-SWITCH] 🔄 Switching to UnDaoDu...
[ACCOUNT-SWITCH] Step 1/3: Click avatar button
[ACCOUNT-SWITCH] Step 2/3: Click 'Switch account'
[ACCOUNT-SWITCH] Step 3/3: Click UnDaoDu
[ACCOUNT-SWITCH] ⏳ Waiting for Studio reload...
[ACCOUNT-SWITCH] ✅ Switch to UnDaoDu successful!
[ACCOUNT-SWITCH]   Channel ID: UCSNTUXjAgpd4sgWYP0xoJgw
```

**If Test Fails**:
- Check: Did coordinates get updated correctly?
- Check: Is Chrome still connected on port 9222?
- Debug: Add `logger.setLevel(logging.DEBUG)` for verbose output

**Task 1B.2: Run Automated Test (Reverse Switch)**

**Command**:
```bash
python -m pytest tests/test_account_switcher.py::test_switch_to_move2japan -v
```

**Task 1B.3: Training Data Verification**

**Check that UI-TARS training data was recorded**:
```bash
# Should see training examples exported
ls modules/infrastructure/foundups_vision/training_data/
# Expected: screenshot_*.png files + metadata.jsonl
```

**Acceptance Criteria**:
- ✅ Automated switch succeeds 3/3 times (test both directions + repeat)
- ✅ Switch completes in <5 seconds
- ✅ Training data recorded (screenshots + coordinates + metadata)
- ✅ No errors in logs

**Deliverables**:
- ✅ Updated coordinates (if needed)
- ✅ Passing pytest tests
- ✅ Training data files created
- ✅ Performance metrics (switch duration)

---

### Phase 1C: Comment Engagement Integration

**Goal**: Enable comment engagement to switch channels automatically

**Duration**: 2-3 hours

**Design Decision for 012**:

**When should switching happen?**

**Option A: Switch when Move2Japan inbox empty**
```python
# Pros: Simple logic, clear trigger
# Cons: Might switch too frequently if both empty
if no_comments_on_move2japan():
    switch_to_undaodu()
```

**Option B: Switch after N empty polls**
```python
# Pros: More stable, avoids thrashing
# Cons: Slower to switch, might miss comments
if empty_poll_count >= 3:  # 3 consecutive empty polls
    switch_to_undaodu()
```

**Option C: Round-robin with time-based rotation**
```python
# Pros: Fair distribution, predictable
# Cons: Might process one channel when other has activity
if time_on_current_channel > 300:  # 5 minutes
    rotate_to_next_channel()
```

**012's Decision**: Which option? (Recommend Option B for stability)

**Task 1C.1: Add Channel Rotation to Comment Processor**

**File to Modify**: `modules/communication/video_comments/skills/tars_like_heart_reply/src/comment_processor.py`

**Changes Required**:
```python
# Add import at top
from modules.infrastructure.foundups_vision.src.studio_account_switcher import switch_studio_account

# Add to CommentProcessor class
class CommentProcessor:
    def __init__(self, ...):
        # Existing init
        self.empty_poll_count = 0
        self.channel_rotation_enabled = True
        self.channels = ["Move2Japan", "UnDaoDu"]  # Rotation order
        self.current_channel_index = 0

    async def should_rotate_channel(self) -> bool:
        """Check if should switch to next channel."""
        if not self.channel_rotation_enabled:
            return False

        # Option B logic: Switch after 3 empty polls
        if self.empty_poll_count >= 3:
            logger.info(f"[ROTATION] Empty poll count: {self.empty_poll_count}, rotating...")
            return True

        return False

    async def rotate_to_next_channel(self):
        """Switch to next channel in rotation."""
        self.current_channel_index = (self.current_channel_index + 1) % len(self.channels)
        next_channel = self.channels[self.current_channel_index]

        logger.info(f"[ROTATION] Switching to {next_channel}...")
        result = await switch_studio_account(next_channel)

        if result["success"]:
            logger.info(f"[ROTATION] ✅ Switched to {next_channel}")
            self.empty_poll_count = 0  # Reset counter
            return True
        else:
            logger.error(f"[ROTATION] ❌ Switch failed: {result.get('error')}")
            return False

    async def process_comments(self):
        """Main comment processing loop with channel rotation."""
        comments = await self.fetch_comments()

        if not comments:
            self.empty_poll_count += 1
            logger.debug(f"[PROCESSOR] No comments, empty count: {self.empty_poll_count}")

            if await self.should_rotate_channel():
                await self.rotate_to_next_channel()
        else:
            self.empty_poll_count = 0  # Reset on successful fetch
            for comment in comments:
                await self.process_comment(comment)
```

**Task 1C.2: Add Configuration**

**File to Create**: `modules/communication/video_comments/config/channel_rotation.yaml`

```yaml
# Channel rotation configuration
enabled: true

# Rotation strategy
strategy: "empty_threshold"  # Options: empty_threshold, time_based, round_robin

# Empty threshold settings (for empty_threshold strategy)
empty_threshold:
  max_empty_polls: 3  # Switch after N consecutive empty polls
  reset_on_activity: true  # Reset counter when comments found

# Channel priority order
channels:
  - name: "Move2Japan"
    channel_id: "UC-LSSlOZwpGIRIYihaz8zCw"
    priority: 1  # Check first
  - name: "UnDaoDu"
    channel_id: "UCSNTUXjAgpd4sgWYP0xoJgw"
    priority: 2  # Check second
  - name: "FoundUps"
    channel_id: "UCfHM9Fw9HD-NwiS0seD_oIA"
    priority: 3  # Check third (future)
    enabled: false  # Not active yet

# Safety limits
safety:
  max_switches_per_hour: 12  # Prevent thrashing
  min_seconds_between_switches: 60  # Cooldown period
```

**Task 1C.3: Integration Test**

**Test Scenario**:
```
Initial State: Move2Japan inbox empty
Expected Flow:
  1. Process Move2Japan inbox → 0 comments (empty_count = 1)
  2. Wait 20s, poll again → 0 comments (empty_count = 2)
  3. Wait 20s, poll again → 0 comments (empty_count = 3)
  4. Trigger rotation → Switch to UnDaoDu
  5. Process UnDaoDu inbox → N comments found
  6. Process comments (Like/Heart/Reply)
  7. Continue monitoring UnDaoDu
```

**Test Command**:
```bash
cd O:\Foundups-Agent\modules\communication\video_comments\skills\tars_like_heart_reply
python run_skill.py \
  --channel UC-LSSlOZwpGIRIYihaz8zCw \
  --max-comments 5 \
  --profile full \
  --enable-rotation
```

**Expected Logs**:
```
[PROCESSOR] Processing Move2Japan inbox...
[PROCESSOR] No comments, empty count: 1
[PROCESSOR] No comments, empty count: 2
[PROCESSOR] No comments, empty count: 3
[ROTATION] Empty poll count: 3, rotating...
[ROTATION] Switching to UnDaoDu...
[ACCOUNT-SWITCH] 🔄 Switching to UnDaoDu...
[ACCOUNT-SWITCH] ✅ Switch to UnDaoDu successful!
[ROTATION] ✅ Switched to UnDaoDu
[PROCESSOR] Processing UnDaoDu inbox...
[PROCESSOR] Found 7 comments
[PROCESSOR] Processing comment 1/7...
```

**Acceptance Criteria**:
- ✅ Rotation triggers after configured threshold (3 empty polls)
- ✅ Account switch succeeds
- ✅ Comments processed on second channel
- ✅ No errors during rotation
- ✅ Safety limits respected (max switches per hour)

**Deliverables**:
- ✅ Comment processor with rotation logic
- ✅ Configuration file for rotation settings
- ✅ Integration test passing
- ✅ Logs showing successful rotation

---

### Phase 1D: Pattern Documentation

**Goal**: Document the account switching pattern for replication on other platforms

**Duration**: 1-2 hours

**Task 1D.1: Create Platform Navigator Template**

**File to Create**: `modules/infrastructure/account_navigation/PLATFORM_NAVIGATOR_TEMPLATE.md`

```markdown
# Platform Navigator Implementation Template

## Overview
This template guides implementation of account switching for any platform (LinkedIn, X, Facebook).
Based on proven YouTube navigator pattern.

## Prerequisites Checklist

- [ ] Platform supports multiple accounts per browser session
- [ ] Account switcher UI is accessible via DOM/UI
- [ ] Platform has unique identifiers for accounts (account ID, username, etc.)
- [ ] Chrome remote debugging enabled for platform's browser session

## Implementation Steps

### Step 1: Manual Discovery (012 Interaction Method)

**Goal**: Understand the UI flow and measure coordinates

**Tasks**:
1. Manually navigate through account switching UI
2. Record each click target (button, menu item, account selector)
3. Measure coordinates using Chrome DevTools
4. Take screenshots at each step
5. Verify account switch succeeds

**Deliverables**:
- Screenshots of each UI state
- Measured coordinates for all click targets
- Account identifiers (IDs, usernames, URLs)
- Total time for manual switch

### Step 2: Create Navigator Class

**File Structure**:
```
modules/infrastructure/account_navigation/src/platform_navigators/
├── __init__.py
├── {platform}_navigator.py  # e.g., linkedin_navigator.py
```

**Template Code**:
```python
"""
{Platform} Account Navigator - Phase 1 (Pattern Learning)

Switches between 012's {platform} accounts with DOM clicking + UI-TARS training.
"""

import logging
from typing import Optional, Dict, Any, Literal

logger = logging.getLogger(__name__)

# Account metadata
ACCOUNTS = {
    "Account1": {
        "id": "...",  # Platform-specific ID
        "display_name": "...",
        "handle": "...",
        "menu_index": 0,
        "menu_y": 100,  # Measured coordinate
    },
    # ... more accounts
}

# Fixed coordinates for switching sequence
SWITCH_COORDINATES = {
    "trigger_button": {
        "x": 0,  # Measured from DevTools
        "y": 0,
        "width": 0,
        "height": 0,
        "description": "Account switcher trigger button",
    },
    # ... more steps
}

class {Platform}AccountSwitcher:
    """Switches {platform} accounts with DOM + training."""

    def __init__(self):
        self.driver = None
        self.interaction = None

    async def switch_to_account(self, target_account: str) -> Dict[str, Any]:
        """Switch to target account."""
        # Implementation following YouTube pattern
        pass
```

### Step 3: Add Configuration

**File**: `modules/infrastructure/account_navigation/config/navigation_patterns.yaml`

```yaml
{platform}:
  enabled: true
  remote_debugging_port: 9223  # Different port per platform
  browser_profile: "data/chrome_profiles/{platform}_{account}"

  # Account switching coordinates
  coordinates:
    trigger_button: {x: 0, y: 0, width: 0, height: 0}
    # ... more coordinates

  # Accounts
  accounts:
    - name: "Account1"
      id: "..."
      # ... metadata
```

### Step 4: Write Tests

**File**: `tests/test_{platform}_navigation.py`

```python
import pytest
from modules.infrastructure.account_navigation.src.platform_navigators.{platform}_navigator import {Platform}AccountSwitcher

@pytest.mark.asyncio
async def test_switch_to_account1():
    switcher = {Platform}AccountSwitcher()
    result = await switcher.switch_to_account("Account1")
    assert result["success"] == True
    assert "Account1" in result["account"]
```

### Step 5: Validate Pattern

**Checklist**:
- [ ] Manual switching works 100%
- [ ] Automated switching works 95%+
- [ ] Training data recorded
- [ ] Tests passing
- [ ] Documentation complete
```

**Task 1D.2: Create Sprint Summary Report**

**File to Create**: `docs/sprints/SPRINT_1_SUMMARY.md`

```markdown
# Sprint 1 Summary: YouTube Account Switching

**Status**: COMPLETE / IN PROGRESS / BLOCKED
**Duration**: X days (planned: 3-5)
**Phase**: Phase 1 (Pattern Learning)

## Objectives Achieved

- [ ] Phase 1A: Manual switching verified
- [ ] Phase 1B: Automated switching working
- [ ] Phase 1C: Comment engagement integration complete
- [ ] Phase 1D: Pattern documented

## Metrics

**YouTube Account Switching**:
- Manual success rate: X/X (100%)
- Automated success rate: X/X (Y%)
- Average switch time: X seconds
- Training examples recorded: X

**Comment Engagement**:
- Rotation triggers: X times
- Successful rotations: X/X (Y%)
- Comments processed across channels: X

## Learnings

**What Worked**:
- [List successful approaches]

**What Didn't Work**:
- [List challenges encountered]

**Improvements for Next Sprint**:
- [List recommendations]

## Deliverables

- ✅ Updated studio_account_switcher.py with verified coordinates
- ✅ Comment processor with channel rotation
- ✅ Configuration system for rotation settings
- ✅ Platform navigator template
- ✅ Training data (X screenshots, Y examples)
- ✅ Tests passing (X/Y)

## Next Sprint Preview

**Sprint 2: Navigation Module Foundation**
- Create unified account_navigation module
- Wrap YouTube navigator
- Design navigation coordinator
- Prepare for X/Twitter integration
```

**Acceptance Criteria**:
- ✅ Template usable for LinkedIn navigator implementation
- ✅ Summary report captures all metrics and learnings
- ✅ Documentation clear enough for 012 to replicate on other platforms

**Deliverables**:
- ✅ PLATFORM_NAVIGATOR_TEMPLATE.md (ready for reuse)
- ✅ SPRINT_1_SUMMARY.md (complete metrics)

---

## Sprint 1 Success Criteria (Overall)

### Functional Requirements
- ✅ YouTube account switching works (Move2Japan ↔ UnDaoDu)
- ✅ Switching success rate ≥95% (19/20 attempts succeed)
- ✅ Comment engagement rotates channels automatically
- ✅ No infinite loops or thrashing (safety limits work)

### Non-Functional Requirements
- ✅ Switch completes in <10 seconds
- ✅ Training data recorded for all successful switches
- ✅ No errors in production logs
- ✅ Code follows WSP 49 (module structure)

### Documentation Requirements
- ✅ All coordinates verified and documented
- ✅ Platform navigator template created
- ✅ Sprint summary report complete
- ✅ Integration guide for next sprint

---

## Risk Mitigation

### Risk 1: Coordinates Change (UI Update)
**Probability**: MEDIUM (YouTube updates UI frequently)
**Impact**: HIGH (breaks automation)
**Mitigation**:
- Record multiple coordinate sets (different resolutions)
- Implement element detection fallback (next sprint)
- UI-TARS vision model provides backup (Phase 2)

### Risk 2: Switch Thrashing
**Probability**: LOW (safety limits in place)
**Impact**: MEDIUM (wasted quota, poor UX)
**Mitigation**:
- Max switches per hour: 12
- Min cooldown: 60 seconds
- Empty poll threshold: 3 consecutive

### Risk 3: Integration Breaks Existing Flow
**Probability**: LOW (minimal changes to comment processor)
**Impact**: MEDIUM (comment engagement stops working)
**Mitigation**:
- Feature flag: `channel_rotation_enabled: false` to disable
- Extensive testing before production
- Rollback plan: revert comment_processor.py changes

---

## Decision Points for 012

### Decision 1: Coordinate Strategy
**Question**: Should we use 012's measured coordinates or detect elements dynamically?

**Option A**: Hardcode 012's coordinates
- ✅ Pros: Fast, reliable on 012's setup
- ❌ Cons: Breaks on different screen resolutions

**Option B**: Detect elements first, then click
- ✅ Pros: Resolution-independent, future-proof
- ❌ Cons: Slower, more complex, requires element selectors

**Recommended**: Option A for Sprint 1 (speed), Option B for Sprint 2 (robustness)

**012's Choice**: A / B / Hybrid?

### Decision 2: Rotation Strategy
**Question**: When should comment engagement switch channels?

**Option A**: After 3 empty polls (~60 seconds)
**Option B**: After 5 empty polls (~100 seconds)
**Option C**: After 10 minutes on one channel (time-based)

**Recommended**: Option A (fast response, won't miss comments for long)

**012's Choice**: A / B / C / Custom threshold?

### Decision 3: Channel Priority
**Question**: What order should channels be checked?

**Option A**: Move2Japan → UnDaoDu → FoundUps (current priority)
**Option B**: Round-robin (equal priority)
**Option C**: Activity-based (prioritize channel with recent activity)

**Recommended**: Option A (Move2Japan is primary channel)

**012's Choice**: A / B / C?

### Decision 4: FoundUps Channel
**Question**: Should we enable FoundUps channel switching in Sprint 1?

**Option A**: Yes, enable all 3 channels
**Option B**: No, only Move2Japan ↔ UnDaoDu (add FoundUps in Sprint 2)

**Recommended**: Option B (validate pattern with 2 channels first)

**012's Choice**: A / B?

---

## Testing Plan

### Test 1: Manual Verification (Phase 1A)
**Owner**: 012
**Duration**: 30 min
**Steps**: See Phase 1A detailed tasks above
**Pass Criteria**: Manual switching works 100%

### Test 2: Automated Switching (Phase 1B)
**Owner**: 0102
**Duration**: 1 hour
**Command**: `pytest tests/test_account_switcher.py -v`
**Pass Criteria**: All tests pass, success rate ≥95%

### Test 3: Comment Rotation (Phase 1C)
**Owner**: 0102
**Duration**: 2 hours
**Command**: `python run_skill.py --enable-rotation`
**Pass Criteria**: Rotation triggers correctly, comments processed on both channels

### Test 4: Safety Limits (Phase 1C)
**Owner**: 0102
**Duration**: 30 min
**Test**: Trigger 15 rotations in 1 hour (should block after 12)
**Pass Criteria**: Safety limits prevent excessive switching

### Test 5: Training Data (Phase 1B)
**Owner**: 0102
**Duration**: 15 min
**Check**: `ls modules/infrastructure/foundups_vision/training_data/`
**Pass Criteria**: Screenshots + metadata.jsonl created

---

## Timeline Breakdown

### Day 1: Coordinate Verification
- **AM**: Phase 1A - 012 manual testing (Task 1A.1, 1A.2, 1A.3)
- **PM**: Phase 1B - Update coordinates if needed (Task 1B.1)

### Day 2: Automation Testing
- **AM**: Phase 1B - Run automated tests (Task 1B.2, 1B.3)
- **PM**: Phase 1C - Begin comment integration (Task 1C.1)

### Day 3: Integration
- **AM**: Phase 1C - Complete integration (Task 1C.2, 1C.3)
- **PM**: Phase 1D - Start documentation (Task 1D.1)

### Day 4-5: Testing & Documentation
- **Day 4**: End-to-end testing, bug fixes
- **Day 5**: Documentation completion, sprint summary

---

## Output Artifacts

### Code Changes
1. `studio_account_switcher.py` - Updated coordinates (if needed)
2. `comment_processor.py` - Channel rotation logic
3. `channel_rotation.yaml` - Configuration
4. `test_account_switcher.py` - Updated tests

### Documentation
1. `SPRINT_1_DETAILED_PLAN.md` - This document
2. `SPRINT_1_SUMMARY.md` - Results and metrics
3. `PLATFORM_NAVIGATOR_TEMPLATE.md` - Reusable pattern

### Data
1. Training screenshots (20+ examples)
2. Coordinate measurements
3. Performance metrics (CSV/JSON)

---

## 012 Feedback Required

### Questions for 012

1. **Coordinates**: Should we use your measured coordinates or test existing first?
2. **Rotation Strategy**: Empty threshold (3 polls) or time-based (5 min)?
3. **Channel Priority**: Move2Japan first or round-robin?
4. **FoundUps**: Enable in Sprint 1 or wait for Sprint 2?
5. **Timeline**: Is 3-5 days realistic or should we adjust?

### Areas Needing Clarification

1. **Testing Environment**:
   - Should tests run on your machine (your screen resolution)?
   - Or should we make coordinates resolution-independent immediately?

2. **Production Deployment**:
   - When should channel rotation go live?
   - Should it start disabled (manual toggle)?

3. **Monitoring**:
   - What metrics do you want to track?
   - Dashboard needed or logs sufficient?

### Success Definition

**012's Definition of Success for Sprint 1**:
- [ ] Manual switching verified (YOUR measurement)
- [ ] Automated switching works on YOUR machine
- [ ] Comment engagement rotates channels (OBSERVABLE behavior)
- [ ] No breaking changes to existing comment engagement
- [ ] Clear pattern documented for LinkedIn/X replication

**Is this definition correct? Any additions/changes needed?**

---

## Appendix: Technical Details

### Chrome Remote Debugging Setup

**Current Port Allocation**:
```
Port 9222: YouTube Studio (studio_account_switcher.py)
Port 9223: LinkedIn (future)
Port 9224: X/Twitter (future)
Port 9225: Facebook (future)
```

**Launch Command**:
```bash
chrome.exe \
  --remote-debugging-port=9222 \
  --user-data-dir="O:/Foundups-Agent/modules/platform_integration/browser_profiles/youtube_move2japan/chrome" \
  https://studio.youtube.com
```

### Training Data Format

**Screenshot Naming**:
```
training_data/
├── youtube_studio_avatar_button_001.png
├── youtube_studio_switch_menu_001.png
├── youtube_studio_account_undaodu_001.png
└── metadata.jsonl
```

**JSONL Format**:
```json
{
  "timestamp": "2025-12-26T10:30:00Z",
  "platform": "youtube_studio",
  "action": "click",
  "target": "avatar_button",
  "coordinates": [371, 28],
  "screenshot": "youtube_studio_avatar_button_001.png",
  "success": true,
  "duration_ms": 245,
  "resolution": "1920x1080",
  "browser_zoom": "100%"
}
```

### Integration Points

**Comment Engagement DAE**:
```
File: modules/communication/video_comments/skills/tars_like_heart_reply/comment_engagement_dae.py
Integration: Import studio_account_switcher, call switch_studio_account()
Impact: Minimal (add 50 lines, no breaking changes)
```

**Live Chat Monitor**:
```
File: modules/communication/livechat/src/livechat_core.py
Integration: Future (Sprint 5 - Master Engagement Coordinator)
Impact: None in Sprint 1
```

---

*Sprint 1 detailed plan complete. Awaiting 012 feedback and approval to proceed.*
