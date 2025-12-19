# WSP 62 Refactoring Plan: comment_engagement_dae.py

**Status:** In Progress
**Date:** 2025-12-19
**Violation:** 2064 lines (564 lines over 2000 line hard limit)
**Target:** < 1200 lines (OK threshold)
**Strategy:** Module Splitting (WSP 62 Section 3.3.2)

## Current Analysis

### File Size Breakdown
- **Total Lines:** 2064
- **Largest Methods:**
  1. `engage_comment()` - 321 lines
  2. `_execute_reply()` - 310 lines
  3. `engage_all_comments()` - 238 lines (orchestrator - keep)
  4. `_process_nested_replies()` - 216 lines
  5. `_extract_comment_data()` - 81 lines
  6. `_execute_nested_reply()` - 74 lines

### Functional Groups
1. **Reply Execution** (~600 lines):
   - `_execute_reply()` (310 lines)
   - `_execute_nested_reply()` (74 lines)
   - `_process_nested_replies()` (216 lines)

2. **Comment Processing** (~400 lines):
   - `engage_comment()` (321 lines)
   - `_extract_comment_data()` (81 lines)

3. **Break System** (~150 lines):
   - `_should_take_break()` (42 lines)
   - `_calculate_break_duration()` (33 lines)
   - `is_on_break()` (13 lines)
   - `_load_break_state()` (34 lines)
   - `_save_break_state()` (20 lines)

4. **Vision/Browser** (~200 lines):
   - `connect()` (49 lines)
   - `click_element_dom()` (68 lines)
   - `_vision_click_verified()` (49 lines)
   - `verify_with_vision()`, `_verify_action_with_vision()`, `_vision_exists()`

## Refactoring Strategy

### Phase 1: Extract Reply Executor
**File:** `src/reply_executor.py` (~600 lines)

**Extractions:**
- `_execute_reply(comment_idx, reply_text)` - DOM automation for reply submission
- `_execute_nested_reply(parent_thread_idx, reply_idx, reply_text)` - Nested reply logic
- `_process_nested_replies(comment_idx, replies_data)` - Process all nested replies

**Dependencies:**
- `self.driver` (Selenium WebDriver)
- `self.human` (HumanBehavior)
- `self.ui_tars_bridge` (Vision verification)
- `self.SELECTORS` (DOM selectors)

**New Class:** `BrowserReplyExecutor`
```python
class BrowserReplyExecutor:
    def __init__(self, driver, human, selectors, ui_tars_bridge=None):
        self.driver = driver
        self.human = human
        self.selectors = selectors
        self.ui_tars = ui_tars_bridge

    async def execute_reply(self, comment_idx: int, reply_text: str) -> bool:
        """Execute reply flow: Open box -> Type -> Submit."""
        ...

    async def execute_nested_reply(self, parent_thread_idx: int, reply_idx: int, reply_text: str) -> bool:
        """Execute reply to a nested comment."""
        ...

    async def process_nested_replies(self, comment_idx: int, replies_data: List[Dict]) -> Dict:
        """Process all nested replies for a thread."""
        ...
```

**Integration in DAE:**
```python
from .src.reply_executor import BrowserReplyExecutor

# In __init__:
self.reply_executor = None

# After driver connects:
self.reply_executor = BrowserReplyExecutor(
    driver=self.driver,
    human=self.human,
    selectors=self.SELECTORS,
    ui_tars_bridge=self.ui_tars_bridge
)

# Replace method calls:
# OLD: await self._execute_reply(idx, text)
# NEW: await self.reply_executor.execute_reply(idx, text)
```

**Lines Saved:** ~600
**New DAE Size:** 2064 - 600 = ~1464 lines

### Phase 2: Extract Comment Processor
**File:** `src/comment_processor.py` (~400 lines)

**Extractions:**
- `engage_comment(comment_idx, auto_like, auto_heart, auto_reply, reply_text)` - Main engagement logic
- `_extract_comment_data(comment_idx)` - Extract DOM data

**Dependencies:**
- `self.driver`
- `self.human`
- `self.reply_executor` (from Phase 1)
- `self.stats`

**New Class:** `CommentProcessor`
```python
class CommentProcessor:
    def __init__(self, driver, human, reply_executor, selectors, stats):
        self.driver = driver
        self.human = human
        self.reply_executor = reply_executor
        self.selectors = selectors
        self.stats = stats

    def extract_comment_data(self, comment_idx: int) -> Dict[str, Any]:
        """Extract comment data from DOM."""
        ...

    async def engage_comment(self, comment_idx: int, auto_like: bool, auto_heart: bool, auto_reply: bool, reply_text: str = None) -> Dict[str, Any]:
        """Main engagement orchestration for single comment."""
        ...
```

**Lines Saved:** ~400
**New DAE Size:** 1464 - 400 = ~1064 lines ✅ (under 1200!)

### Phase 3 (Optional): Further Optimization
If needed, extract:
- **Break Manager** (~150 lines) → `src/break_manager.py`
- **Vision Verifier** (~200 lines) → `src/vision_verifier.py`

## Rollback Plan

If refactoring fails:
1. Git revert to commit 4ac3c66d (Phase 3O-3R completion)
2. Keep extracted modules for reference
3. Document issues in ModLog.md

## Testing Strategy

1. **Unit Tests** (for extracted modules):
   - Test `BrowserReplyExecutor.execute_reply()` with mocked driver
   - Test `CommentProcessor.extract_comment_data()` with mocked DOM

2. **Integration Tests** (for refactored DAE):
   - Run existing `run_skill.py` end-to-end
   - Verify all actions (like, heart, reply) still work
   - Check telemetry output matches original

3. **Regression Tests**:
   - Compare engagement stats before/after refactoring
   - Verify anti-detection patterns preserved

## Success Criteria

- [ ] comment_engagement_dae.py < 1200 lines (OK threshold)
- [ ] All extracted modules < 800 lines each
- [ ] Zero functional regressions
- [ ] All integration tests pass
- [ ] ModLog.md updated with refactoring documentation
- [ ] Git commit created with refactored code

## Timeline

- **Phase 1** (Reply Executor): 30-45 min
- **Phase 2** (Comment Processor): 20-30 min
- **Testing**: 15-20 min
- **Documentation**: 10 min
- **Total**: ~90 minutes

## WSP Compliance

- **WSP 62:** Large File Refactoring Enforcement
- **WSP 49:** Module Directory Structure (src/ subdirectory)
- **WSP 3:** Functional Distribution
- **WSP 22:** ModLog Updates
- **WSP 50:** Pre-Action Research (HoloIndex search completed)

---

**Next Step:** Begin Phase 1 extraction (Reply Executor)
