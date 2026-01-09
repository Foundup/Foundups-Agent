# YouTube Shorts Scheduler - ModLog

## V0.1.0 - Initial Module Creation (2025-12-31)

### Created
- Module structure following WSP 49
- README.md with architecture overview
- INTERFACE.md with public API documentation
- Channel configuration for Move2Japan, UnDaoDu, FoundUps
- DOM automation layer with comprehensive selectors
- Schedule tracker with JSON persistence
- Core scheduler orchestrator

### Architecture Decisions
- **ADR-001**: Use Selenium over YouTube API for scheduling
  - Reason: YouTube Data API doesn't support scheduling - only visibility changes
  - Trade-off: More fragile (DOM changes) but enables full automation

- **ADR-002**: Time slots based on audience geography
  - Move2Japan/UnDaoDu: Japan timezone, targeting US viewers
  - FoundUps: EST timezone, targeting US viewers

### WSP Compliance
- WSP 3: Platform Integration domain
- WSP 49: Standard module structure
- WSP 80: DAE pattern ready
- WSP 22: This ModLog

### Implementation Complete
- [x] channel_config.py - Multi-channel support (Move2Japan, UnDaoDu, FoundUps)
- [x] dom_automation.py - Comprehensive Selenium selectors for YouTube Studio
- [x] schedule_tracker.py - JSON persistence with smart slot allocation
- [x] content_generator.py - FFCPLN clickbait titles/descriptions
- [x] scheduler.py - Main orchestrator with DAE entry point
- [x] tests/test_scheduler.py - Unit tests (integration tests require browser)

### Next Steps
- [x] Integration with existing Chrome debug sessions (port 9222/9223)
- [ ] UI-TARS visual verification for complex dialogs
- [ ] Queue management for multi-channel scheduling
- [ ] Add memory/ directory for schedule persistence

## V0.2.0 - Layer Cake Testing (2026-01-01)

### Layer 1: Navigation + Filter - COMPLETE
- **URL-based filter (RECOMMENDED)**: `filter=[{"name":"VISIBILITY","value":["UNLISTED"]}]`
- **UI-based filter**: Click `input[placeholder='Filter']` → Click "Visibility" (index 9) → Click "Unlisted" SPAN → ESC
- Test: `python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer1_filter`
- Test with UI: `python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer1_filter --ui`

### Layer 2: Video Edit Page - COMPLETE
- Navigate to: `https://studio.youtube.com/video/{VIDEO_ID}/edit`
- Visibility section: `ytcp-video-metadata-visibility`
- Select button: `#select-button` with `aria-label='Edit video visibility status'`
- Test: `python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer2_edit`

### Layer 3: Visibility Change - DISCOVERED
- **Key Finding**: The visibility button TOGGLES/CYCLES visibility states rather than opening a dialog
- Clicking `#select-button` changes visibility (observed: Unlisted → Scheduled)
- "Made for kids" section is part of main page, not a separate dialog
- No modal dialog for visibility selection
- Test: `python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer3_schedule`

### Architecture Decision
- **ADR-003**: Visibility toggle button behavior
  - YouTube Studio uses a toggle button for visibility changes
  - Clicking cycles through: Public → Unlisted → Private → Scheduled
  - Need to detect current state and click appropriate number of times
  - Alternative: May need to explore different UI path for explicit scheduling with date/time

### DOM Element Reference
```
ytcp-video-metadata-visibility
  └── #container
      └── #content
          └── #icon-and-type
              └── #visibility-text (shows: "Unlisted", "Scheduled", etc.)
      └── #select-button (YTCP-ICON-BUTTON, aria='Edit video visibility status')
```

## V0.2.1 - UI-TARS Visual Verification Integration (2026-01-01)

### Added
- `--uitars` flag for test_layer1_filter.py
- UI-TARS vision model integration for complex dialog navigation
- Fallback from UI-TARS to DOM selectors if vision model can't find elements

### UI-TARS Integration
- Uses `modules/infrastructure/foundups_vision/src/ui_tars_bridge.py`
- Connects to LM Studio API at port 1234
- Model: UI-TARS 1.5 7B (vision-language model)
- Verified working: Found Filter input at coordinates (174, 115) in 1000x1000 space

### Test Modes
```bash
# URL-based filter (most reliable, no UI interaction)
python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer1_filter

# UI-based filter (DOM selectors)
python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer1_filter --ui

# UI-TARS vision-based filter (requires LM Studio with ui-tars-1.5-7b)
python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer1_filter --uitars
```

### Architecture Decision
- **ADR-004**: UI-TARS for Shadow DOM workaround
  - YouTube Studio uses heavy Shadow DOM which blocks standard selectors
  - UI-TARS screenshots the entire page and uses vision to find elements
  - Provides natural language descriptions: "Filter input in the toolbar"
  - Falls back to DOM selectors if vision fails
  - Trade-off: Slower (20-30s inference) but more robust for complex dialogs

### Technical Details
- Screenshot resizing: 2560x1202 → 1280x601 (for faster inference)
- Coordinate mapping: 1000x1000 box → viewport CSS pixels
- Model output format: `click(start_box='<|box_start|>(x,y)<|box_end|>')`
- Timeout: 120s (allows for CPU-based inference)

## V0.2.2 - Visibility Filter Dialog Deep Dive (2026-01-01)

### Key Findings

**ADR-005**: Visibility Filter Dialog Structure
- The `<ytcp-filter-dialog>` contains a `<tp-yt-paper-dialog id="dialog">` that is **hidden by default**
- Inner dialog has `display: none` and `aria-hidden="true"` until properly triggered
- Dialog contains 6 checkboxes: Public, Private, Unlisted, Members, Has schedule, Draft
- Apply/Cancel buttons at the bottom

**ADR-006**: JavaScript .click() vs ActionChains
- YouTube Studio's `ytcp-checkbox-lit` elements do NOT respond to JavaScript `.click()`
- Must use Selenium ActionChains with coordinate-based clicks for checkbox interaction
- Verified: `aria-checked` changes from `false` to `true` with ActionChains click

**ADR-007**: Force-Opening Dialog Bypasses Event System
- Force-opening the dialog via JS (`display: block`, `opened=true`) shows the checkboxes
- However, clicking Apply doesn't apply the filter because YouTube's event handlers weren't initialized
- The dialog must be opened through YouTube's native click handlers for the filter to work

### Visibility Dialog DOM Structure
```
ytcp-filter-dialog
  └── tp-yt-paper-dialog#dialog (display: none by default)
      └── .header (title: "Visibility", close button)
      └── form#contentsForm
          └── ytcp-checkbox-group.selection-list
              └── ul
                  └── li.row (x6)
                      └── label.ytcp-checkbox-label
                          └── ytcp-checkbox-lit
                              └── #checkbox (role="checkbox", aria-checked)
                          └── span.checkbox-label (text: "Public"/"Unlisted"/etc.)
      └── .buttons-row
          └── ytcp-button (text: "Apply")
          └── ytcp-button (text: "Cancel")
```

### Checkbox Click Pattern
```python
# Working pattern for ytcp-checkbox-lit clicks:
from selenium.webdriver.common.action_chains import ActionChains

# Get checkbox center coordinates via JS
coords = driver.execute_script('''
    const checkbox = ...;  // Find the checkbox
    const rect = checkbox.getBoundingClientRect();
    return {x: rect.left + rect.width/2, y: rect.top + rect.height/2};
''')

# Click using ActionChains (moves to viewport coords)
actions = ActionChains(driver)
actions.move_by_offset(coords['x'], coords['y']).click().perform()
actions.move_by_offset(-coords['x'], -coords['y']).perform()  # Reset
```

### Recommendation
**Use URL-based filtering for reliability:**
```python
filter_param = '[{"name":"VISIBILITY","value":["UNLISTED"]}]'
url = f"https://studio.youtube.com/channel/{channel_id}/videos/short?filter={quote(filter_param)}"
```

UI-based filtering is complex due to:
1. Shadow DOM blocking standard selectors
2. Dialog requiring proper event initialization
3. Checkbox clicks requiring ActionChains (not JS .click())

### Test Files Created
- `test_visibility_filter_complete.py` - Full 6-step filter flow (force-open approach)
- `test_visibility_natural_click.py` - Attempted natural click approach
- `debug_visibility_dialog*.py` - Diagnostic scripts
- `debug_checkbox_click.py` - Checkbox click testing
- `debug_filter_dialog.py` - Dialog structure exploration

## V0.3.0 - URL-First with DOM Fallback (2026-01-01)

### Added
- `navigate_to_shorts_with_fallback()` method in `dom_automation.py`
- `_apply_filter_via_dom()` private method for fallback logic
- New DOM selectors for filter UI interaction
- `--fallback` test mode in `test_layer1_filter.py`

### Architecture Decision
- **ADR-008**: URL-First with DOM Fallback Strategy
  - Primary: Use pre-filtered URL with encoded `filter` parameter (instant, reliable)
  - Fallback: Click through Filter UI via DOM/ActionChains if URL filter chip not detected
  - Rationale: URL approach is faster and bypasses Shadow DOM issues; DOM fallback provides resilience

### Implementation Details
```python
# URL-first approach (preferred)
url = build_studio_url(channel_id, "short", "UNLISTED")
# Generates: https://studio.youtube.com/channel/{ID}/videos/short?filter=%5B%7B%22name%22%3A%22VISIBILITY%22%2C%22value%22%3A%5B%22UNLISTED%22%5D%7D%5D

# DOM fallback (if URL filter chip not detected)
1. Click filter area at (170, 104) using ActionChains
2. Click "Visibility" menu item
3. Select "Unlisted" checkbox
4. Click "Apply" button
5. Verify filter chip appeared
```

### Test Command
```bash
python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer1_filter --fallback
```

## V0.4.0 - Layer 2: Video Edit + Content Enhancement (2026-01-01)

### Added
- Layer 2 DOM selectors for video edit page (title/description textboxes)
- `click_first_video_edit_button()` method in `dom_automation.py`
- `get_current_title()` and `get_current_description()` extraction methods
- `set_title()` and `set_description()` modification methods
- `enhance_title()` and `enhance_description()` functions in `content_generator.py`
- `--enhance` test mode in `test_layer2_edit.py`

### Architecture Decision
- **ADR-009**: Layer 2 Edit Workflow
  - Navigate to filtered shorts → Click edit button → Extract content → Enhance → Preview
  - Enhancement preserves original content hooks while adding FFCPLN branding
  - Title limited to 100 chars, description includes SEO hashtags

### Test Commands
```bash
# Basic Layer 2 navigation test
python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer2_edit

# Full enhancement workflow (preview only, no save)
python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer2_edit --enhance
```

## V0.4.1 - Selector Fixes for Layer 1/2 (2026-01-01)

### Fixed
- **ADR-009**: VIDEO_TABLE selector fixed
  - Old: `table[aria-label='Video list']` (doesn't exist on page)
  - New: `ytcp-video-row` (actual video row elements)
- **ADR-010**: Filter chip selector fixed
  - Old: `button[aria-label*='Visibility: Unlisted']`
  - New: JavaScript-based detection of `ytcp-chip` with text content matching
- **ADR-011**: Filter input wait added
  - Added WebDriverWait for Filter input in DOM fallback
  - Increased timeout to 10 seconds

### Test Results (2026-01-01)
| Test | Mode | Status | Notes |
|------|------|--------|-------|
| Layer 1 | `--fallback` | PASS | URL-first with DOM fallback, 30 videos found |
| Layer 2 | basic | PASS | Direct URL navigation to edit page |
| Layer 2 | `--enhance` | FAIL | `click_first_video_edit_button` needs selector fix |

### Key Finding: URL Filter is Reliable
- URL-based filtering: `?filter=[{"name":"VISIBILITY","value":["UNLISTED"]}]`
- Chip detection: `ytcp-chip` element with text "Visibility: Unlisted"
- Filter input disappears when filter is applied (replaced by chip)

### Diagnostic Script Added
- `tests/diagnose_page.py` - Quick page state inspection tool

## V0.5.0 - Complete WRE Stack + CLI Integration (2026-01-01)

### Added
- **ROADMAP.md**: 3-phase development plan (layer tests → linking → DAE)
- **scripts/launch.py**: WSP 62 extraction for main.py integration
- **main.py option 6**: YouTube Shorts Scheduler submenu
- **Layer 3 selectors**: Full scheduling DOM elements (visibility, date, time, done)
- **WSP 95 SKILLz.md**: FFCPLN title enhancement skill

### WRE Layer Stack Validated

| Layer | Action | Status |
|-------|--------|--------|
| L0 | Entry (select video) | ✅ |
| L1 | Open visibility dialog | ✅ |
| L1.1 | Expand schedule | ✅ |
| L2 | Set DATE | ✅ |
| L3 | Set TIME | ✅ |
| L4 | Click Done | ✅ |
| L5.1 | Related Video modal | ⚠️ Selector needs fix |
| L5.2 | Select top-left video | ⚠️ Coordinate issue |
| L5.3 | SAVE | ✅ |
| L5.4 | Return to list | ✅ |
| L5.5 | REFRESH (F5) | ✅ CRITICAL |

### Videos Scheduled (Demo)
1. `gdTtl3c3rtA` → Feb 17, 2026 at 5:00 PM
2. `7ww5-6me4zg` → Feb 18, 2026 at 6:00 PM

### Architecture Decision
- **ADR-012**: Visual-First, Selenium-Later
  - Phase 1: Validate DOM selectors via browser subagent (visual)
  - Phase 2: Convert to pure Selenium once selectors verified
  - Phase 3: DAE loop with self-monitoring

### Known Issues
- **L5.1-5.2**: Related video selector clicks arbitrary position, not top-left
- **TODO**: Add search feature support for related video selection

### CLI Integration
```bash
python main.py
# Select 1 (YouTube) → 6 (Shorts Scheduler)
# Options: 1=Enhance, 2=Dry Run, 3=Schedule
```

### Test Commands
```bash
# Layer 1 with fallback
python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer1_filter --fallback

# Layer 2 with enhancement
python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer2_edit --enhance
```

## V0.6.0 - Full Chain Test + Menu Restructure (2026-01-01)

### Added
- **test_full_chain.py**: Concatenated L1 → L2 → L3 → L4 test
- **ADR-013**: main.py YouTube menu restructure (Occam's Razor)

### Full Chain Test
```bash
# Dry run (preview only)
python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_full_chain --dry-run

# Live run (saves changes)
python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_full_chain
```

**Chain Flow:**
1. L1: Navigate to unlisted shorts (URL filter)
2. L2: Click first video → edit page
3. L3: Open visibility → Schedule → Set date/time → Done → Save
4. L4: Return to list → Refresh (F5)

### Architecture Decision
- **ADR-013**: YouTube Menu Restructure (Occam's Razor)
  - main.py → 1 (YouTube DAEs) → Independent DAEs at 1.x level
  - Option 1 = Live Chat Monitor (direct launch with 012 profile)
  - Option 2 = Comment Engagement DAE
  - Option 3 = Shorts Scheduler (submenu)
  - Option 4 = Shorts Generator (Veo3/Sora2 submenu)
  - Option 5 = YouTube Stats
  - Option 6 = Full Production Mode
  - Option 7 = AI Overseer Mode

### CLI Integration Updated
```bash
python main.py
# Select 1 (YouTube) → 3 (Shorts Scheduler)
# Options: 1=Enhance, 2=Dry Run, 3=Schedule
```

## V0.7.0 - Human Behavior + Selenium Fixes (2026-01-01)

### Added
- **human_behavior module integration** in `test_layer3_schedule.py`
- **Ctrl+A before typing** for date/time inputs (replaces, not appends)
- **set_schedule_date_time()** function with validation logging
- **Aligned test menu** - Options 4-8 now match actual layer tests

### Architecture Decisions

- **ADR-014**: Human Behavior for Popup Stability
  - Standard JS `.click()` can close popups prematurely
  - `human_behavior` uses Bezier curve mouse movements
  - Triggers proper hover states before clicking
  - Slower but more reliable for reactive YouTube UI

- **ADR-015**: Ctrl+A Before Input
  - YouTube date/time inputs have existing values
  - Must select all (Ctrl+A) before typing to replace
  - Prevents "Jan 01, 2026Jan 08, 2026" errors

### Test Menu (main.py → 1 → 3)
```
== SELENIUM TESTS ==
4. [TEST] Full Chain (navigate → enhance → schedule → save)
5. [TEST] L0: Entry (navigate to unlisted, select video)
6. [TEST] L1: Filter (apply unlisted filter)
7. [TEST] L2: Edit (open edit page, find visibility)
8. [TEST] L3: Schedule (visibility → schedule → date/time → done)
```

### Test File Mapping
| Option | Test File | Description |
|--------|-----------|-------------|
| 4 | `test_full_chain.py` | Full L0→L3 |
| 5 | `test_layer0_entry.py` | Entry/navigation |
| 6 | `test_layer1_filter.py` | URL filter |
| 7 | `test_layer2_edit.py` | Edit page |
| 8 | `test_layer3_schedule.py` | Schedule dialog |

### Key Code Pattern
```python
# Import human behavior
from modules.infrastructure.foundups_selenium.src.human_behavior import get_human_behavior
human = get_human_behavior(driver)

# Click with human-like movement
human.human_click(date_input)

# Ctrl+A before typing to replace existing value
ActionChains(driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
date_input.send_keys("Jan 08, 2026")
```

### Coverage Status
| Layer | Status |
|-------|--------|
| L0 Entry | ✅ Selenium |
| L1 Filter | ✅ Selenium |
| L2 Edit | ✅ Selenium |
| L2.5 SKILLz | ✅ FFCPLN |
| L3 Schedule | ✅ Selenium + human_behavior |
| L4 Done | ✅ Selenium |
| L5 Save/Return | ⚠️ In progress |

## V0.8.0 - WRE-TARS Visual Verification (2026-01-01)

### Added
- **WREVisualTestRunner** (`foundups_selenium/src/wre_visual_runner.py`)
  - Visual-first test execution with UI-TARS verification gates
  - Each step: action → screenshot → verify → record → proceed/retry
  - Integrates with pattern_memory for recursive learning (WSP 48/60)
- **`--wre-tars` flag** for test_layer3_schedule.py
- **`run_with_visual_verification()`** function

### Architecture Decisions
- **ADR-016**: Pure UI-TARS Verification (Option 1)
  - Speed is not a factor for testing - correctness matters
  - Visual verification = DOM-agnostic robustness
  - Natural language prompts: "Is the date picker visible?"
  - Each step becomes training data for pattern_memory

### WREVisualTestRunner API
```python
runner = create_wre_runner(driver, skill_name="youtube_schedule_l3")

runner.step(
    "L3.2 Expand Schedule",
    action=lambda: click_schedule_expand(driver),
    verify_prompt="Is the Schedule section showing date and time inputs?"
)

runner.print_summary()  # Shows ✅/❌ for each step
```

### Test Command
```bash
# Standard DOM-based test
python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer3_schedule

# WRE-TARS visual verification mode
python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer3_schedule --wre-tars
```

### Pattern Memory Integration
- Outcomes stored in `wre_core/data/pattern_memory.db`
- Skill name: `youtube_schedule_l3`
- Fields: step name, verify prompt, success, screenshot path, execution_ms
