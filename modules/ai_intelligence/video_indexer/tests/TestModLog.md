# Video Indexer Tests - ModLog
**WSP Compliance**: WSP 34 (Test Documentation), WSP 22 (Change Log)

## 2026-02-06

### Test Run
- **Command**: `python -m pytest modules/ai_intelligence/video_indexer/tests/test_studio_ask_indexer_persistence.py -v`
- **Result**: PASS (1 test)
- **Warnings**:
  - PytestConfigWarning: Unknown config option `asyncio_default_fixture_loop_scope`
  - PytestConfigWarning: Unknown config option `asyncio_mode`
  - Pydantic warning about `<built-in function any>` type

### Notes
- Validates Ask-Gemini JSON persistence path and IndexData conversion.

### Test Run
- **Command**: `python -m pytest modules/ai_intelligence/video_indexer/tests/test_studio_ask_indexer_persistence.py modules/ai_intelligence/video_indexer/tests/test_studio_ask_indexer_signals.py -v`
- **Result**: PASS (3 tests)
- **Warnings**:
  - PytestConfigWarning: Unknown config option `asyncio_default_fixture_loop_scope`
  - PytestConfigWarning: Unknown config option `asyncio_mode`
  - Pydantic warning about `<built-in function any>` type

### Notes
- Validates signal helpers (STOP/REINDEX) and index count telemetry helpers.

## 2026-03-11

### Browser Isolation Fix
- **Change**: Added `group_channels_by_browser()` filter in `studio_ask_indexer.py`
- **Purpose**: Prevent Chrome OOPS on Edge-only channels (antifaFM, FoundUps)
- **Test**: Manual verification of channel grouping
  ```
  CHROME: ['move2japan', 'undaodu']
  EDGE: ['foundups', 'antifafm']
  ```
- **Result**: PASS - Chrome no longer accesses antifaFM/FoundUps channels

### WSP Compliance
- WSP 50: Verified channel registry before modifying indexer
- WSP 72: Browser isolation respects module boundaries
