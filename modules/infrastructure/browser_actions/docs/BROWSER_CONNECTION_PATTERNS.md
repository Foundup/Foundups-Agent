# Browser Connection Patterns - Port-Based vs Profile-Based

**WSP References**: WSP 91 (Observability), WSP 3 (Architecture)
**Purpose**: Prevent multiple browser window spawning via singleton pattern

---

## Problem: Multiple Chrome Windows

**Symptom**: Multiple browser windows opening for same profile
**Root Cause**: Bypassing BrowserManager singleton - creating browsers directly
**Solution**: Always use `get_browser_manager().get_browser()` for profile-based connections

**Health Check**:
```bash
python modules/infrastructure/browser_actions/tools/browser_health_check.py
```

---

## Architecture: 3-Layer Browser System

```
┌─────────────────────────────────────────────────────────┐
│ Layer 3: Consumer Layer (Tests, Production Code)       │
│ - Should ALWAYS use BrowserManager or port connection  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│ Layer 2: ActionRouter (Routing Layer)                  │
│ - Routes to Selenium OR UI-TARS Vision                 │
│ - Uses BrowserManager for profile-based connections    │
│ - Direct port connection for test/dev mode             │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│ Layer 1: BrowserManager (Singleton)                    │
│ - Thread-safe singleton instance                       │
│ - Reuses existing browsers via _browsers dict          │
│ - Prevents multiple windows for same profile           │
└─────────────────────────────────────────────────────────┘
```

---

## Pattern 1: Profile-Based Connection (Production)

**Use Case**: Production code, automated workflows, skills
**Browser Lifecycle**: Managed by BrowserManager singleton
**Benefits**: No duplicate windows, telemetry tracking, session reuse

### Correct Implementation

```python
from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager

# Get singleton browser manager
browser_manager = get_browser_manager()

# Get or reuse existing browser for profile
browser = browser_manager.get_browser('chrome', 'youtube_move2japan')

# Use with ActionRouter
from modules.infrastructure.browser_actions.src.action_router import ActionRouter
router = ActionRouter(
    profile='youtube_move2japan',
    selenium_driver=browser,  # ← Pass singleton browser
)

# Browser survives across multiple router instances
# No duplicate windows spawned
```

### Production Examples

**LinkedIn Agent**: [anti_detection_poster.py:120-130](modules/platform_integration/linkedin_agent/src/anti_detection_poster.py#L120-L130)
```python
browser_manager = get_browser_manager()
linkedin_profile = f"linkedin_{self.company_id}"
self.driver = browser_manager.get_browser(
    browser_type='chrome',
    profile_name=linkedin_profile,
    options={'disable_web_security': True}
)
```

**X/Twitter Agent**: [x_anti_detection_poster.py](modules/platform_integration/x_twitter/src/x_anti_detection_poster.py)
Same pattern

---

## Pattern 2: Port-Based Connection (Test/Dev)

**Use Case**: Manual testing, debugging, development
**Browser Lifecycle**: External (manually launched Chrome on port 9222)
**Benefits**: Attach to existing Chrome, inspect live automation

### Correct Implementation

**Step 1**: Launch Chrome with remote debugging
```bash
chrome.exe --remote-debugging-port=9222 --user-data-dir="O:/Foundups-Agent/modules/platform_integration/youtube_auth/data/chrome_profile_move2japan"
```

**Step 2**: Connect via FoundUpsDriver
```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)

# Pass to ActionRouter
from modules.infrastructure.browser_actions.src.action_router import ActionRouter
router = ActionRouter(
    profile="youtube_move2japan",
    selenium_driver=driver,  # ← Pass existing connection
)
```

**Step 3**: OR use environment variable
```bash
export FOUNDUPS_CHROME_PORT=9222
```

```python
# ActionRouter will auto-connect to port 9222
router = ActionRouter(profile="youtube_move2japan")
# No selenium_driver param needed - router detects FOUNDUPS_CHROME_PORT
```

### Test Examples

**YouTube Engagement**: [test_autonomous_with_validation.py:227-233](modules/platform_integration/social_media_orchestrator/tests/test_autonomous_with_validation.py#L227-L233)
```python
# Connect to existing Chrome on port 9222
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)

# Pass to ActionRouter
router = ActionRouter(
    profile="youtube_move2japan",
    selenium_driver=driver,
)
```

---

## Anti-Pattern: Direct Browser Creation ❌

**NEVER DO THIS** (bypasses singleton, creates duplicate windows):

```python
# ❌ WRONG: Creates duplicate browser
from selenium import webdriver
driver = webdriver.Chrome(options=chrome_options)

# ❌ WRONG: Creates duplicate browser
from modules.infrastructure.foundups_selenium.src.foundups_driver import FoundUpsDriver
driver = FoundUpsDriver(profile_dir="...", stealth_mode=True)

# ❌ WRONG: ActionRouter creates its own browser (duplicate)
router = ActionRouter(profile="youtube_move2japan")  # No selenium_driver param
```

**Result**: Multiple Chrome windows spawned for same profile

---

## Decision Matrix

| Scenario | Pattern | BrowserManager | Example |
|----------|---------|----------------|---------|
| Production skill execution | Profile-based | ✅ YES | LinkedIn agent, X agent |
| Automated workflow | Profile-based | ✅ YES | Social media orchestrator |
| Manual testing with existing Chrome | Port-based | ❌ NO | Test files with port 9222 |
| Development debugging | Port-based | ❌ NO | Manual Chrome + test |
| CI/CD pipeline | Profile-based | ✅ YES | Automated tests |

---

## ActionRouter Behavior

**File**: [action_router.py:156-190](modules/infrastructure/browser_actions/src/action_router.py#L156-L190)

### Logic Flow

```python
async def _ensure_selenium(self) -> Any:
    if self._selenium_driver is None:  # No pre-initialized driver
        # Check for port-based connection env var
        port_val = os.getenv("FOUNDUPS_CHROME_PORT") or os.getenv("BROWSER_DEBUG_PORT")

        if port_val:
            # Port-based: Create FoundUpsDriver with port param
            self._selenium_driver = FoundUpsDriver(port=int(port_val), ...)
        else:
            # Profile-based: Use BrowserManager singleton
            browser_manager = get_browser_manager()
            self._selenium_driver = browser_manager.get_browser('chrome', self.profile)

    return self._selenium_driver
```

### Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `FOUNDUPS_CHROME_PORT` | Connect to existing Chrome on port | `9222` |
| `BROWSER_DEBUG_PORT` | Alternative port env var | `9222` |
| `FOUNDUPS_VISION_ONLY` | Force vision driver (bypass Selenium) | `1` |
| `FOUNDUPS_DISABLE_FALLBACK` | Disable driver fallback | `1` |

---

## Health Check Tool

**Location**: [browser_health_check.py](tools/browser_health_check.py)

### Usage

```bash
# Check all browsers
python modules/infrastructure/browser_actions/tools/browser_health_check.py

# Filter by profile
python modules/infrastructure/browser_actions/tools/browser_health_check.py --profile youtube_move2japan

# List orphaned browsers (dry run)
python modules/infrastructure/browser_actions/tools/browser_health_check.py --kill-orphans --dry-run

# Kill orphaned browsers
python modules/infrastructure/browser_actions/tools/browser_health_check.py --kill-orphans
```

### Example Output

```
BROWSER HEALTH CHECK REPORT
================================================================================

Browser Instances:
  Chrome: 26
  Edge:   18
  Total:  44

ISSUES DETECTED (44):
  [WARN] Multiple Chrome instances for profile: default (PIDs: 8024, 22152, ...)
  [WARN] Multiple Edge instances for profile: default (PIDs: 7852, 8888, ...)

RECOMMENDATIONS:
  1. Multiple browser instances detected - use BrowserManager singleton
     from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager
     browser_manager = get_browser_manager()
     browser = browser_manager.get_browser('chrome', 'profile_name')
```

---

## Migration Guide

### Before (Multiple Windows)

```python
# Test file creating its own browser
driver = webdriver.Chrome(options=chrome_options)

# ActionRouter creates ANOTHER browser
router = ActionRouter(profile="youtube_move2japan")
# ❌ Result: 2 Chrome windows opened
```

### After (Singleton Pattern)

```python
# Use BrowserManager singleton
from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager

browser_manager = get_browser_manager()
browser = browser_manager.get_browser('chrome', 'youtube_move2japan')

# Pass to ActionRouter
router = ActionRouter(
    profile="youtube_move2japan",
    selenium_driver=browser,  # ← Reused singleton
)
# ✅ Result: 1 Chrome window, reused across tests
```

---

## WSP Compliance

**WSP 91 - Observability**:
BrowserManager emits telemetry events via observers for AI Overseer monitoring

**WSP 3 - Architecture**:
Singleton pattern enforces correct browser lifecycle management

**WSP 72 - Independence**:
Browser instances isolated by profile, preventing session conflicts

---

**Last Updated**: 2025-12-08
**Maintainer**: 0102 Agent
**Related**: [browser_manager.py](modules/infrastructure/foundups_selenium/src/browser_manager.py), [action_router.py](modules/infrastructure/browser_actions/src/action_router.py)
