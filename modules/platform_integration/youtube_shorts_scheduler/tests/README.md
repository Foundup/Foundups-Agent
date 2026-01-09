# YouTube Shorts Scheduler - Test Documentation

> **WSP 34 Compliance**: Test documentation for the youtube_shorts_scheduler module.

## Test Overview

This module contains integration tests for YouTube Studio automation via Selenium.
Tests require a Chrome browser running in debug mode on port 9222.

## Selenium Test Suite (V0.7.0)

| Menu | Test File | Description |
|------|-----------|-------------|
| 4 | `test_full_chain.py` | Full L0→L3 flow (navigate → enhance → schedule) |
| 5 | `test_layer0_entry.py` | Navigate to unlisted, select video |
| 6 | `test_layer1_filter.py` | Apply unlisted filter |
| 7 | `test_layer2_edit.py` | Open edit page, find visibility |
| 8 | `test_layer3_schedule.py` | Visibility → Schedule → date/time → Done |

## Quick Run

```bash
python main.py → 1 → 3 → [4-8]
```

## Key Features (V0.7.0)

### Human Behavior Module
```python
from modules.infrastructure.foundups_selenium.src.human_behavior import get_human_behavior
human = get_human_behavior(driver)
human.human_click(element)  # Bezier curve mouse movement
```

### Ctrl+A Before Typing
```python
# CRITICAL: Select all existing text before typing new value
ActionChains(driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
element.send_keys("Jan 08, 2026")
```

## Test Modes

### Layer 1 Filter Tests

```bash
# URL-based filter (default, most reliable)
python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer1_filter

# URL-first with DOM fallback
python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer1_filter --fallback
```

### Layer 3 Schedule Test

```bash
# Full schedule flow with human behavior
python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer3_schedule --selenium
```

## Prerequisites

1. Chrome running with remote debugging:
   ```bash
   chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrome_profile"
   ```

2. Logged into YouTube Studio for the target channel

## Coverage Status (V0.7.0)

| Layer | Component | Status |
|-------|-----------|--------|
| L0 | Entry (navigate + select) | ✅ Selenium |
| L1 | Filter (URL-based) | ✅ Selenium |
| L2 | Edit (visibility section) | ✅ Selenium |
| L2.5 | SKILLz (FFCPLN enhance) | ✅ Selenium |
| L3.1 | Visibility button | ✅ Selenium |
| L3.2 | Schedule expand | ✅ Selenium + 3s wait |
| L3.3 | Date (Ctrl+A + type) | ✅ Selenium |
| L3.4 | Time (Ctrl+A + type) | ✅ Selenium |
| L4 | Done button | ✅ Selenium |
| L5 | Save + Return | ⚠️ In progress |

## Architecture Decisions

- **ADR-014**: Human Behavior for Popups (V0.7.0)
  - Standard JS `.click()` can close popups prematurely
  - `human_behavior` uses Bezier curves that trigger hover states properly
  - Slower but more reliable for YouTube Studio's reactive UI

- **ADR-015**: Ctrl+A Before Input (V0.7.0)
  - YouTube date/time inputs have existing values
  - Must select all before typing to replace (not append)
  - Critical for date formats: "Jan 08, 2026" not "Jan 01, 2026Jan 08, 2026"

## Last Updated

- **V0.7.0** (2026-01-01): Human behavior, Ctrl+A fix, aligned test menu

