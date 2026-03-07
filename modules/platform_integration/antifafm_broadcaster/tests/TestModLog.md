# antifaFM Broadcaster - Test Module Log

## Test Suite Overview

| Test File | Status | Last Run | Purpose |
|-----------|--------|----------|---------|
| `test_obs_controller_startup.py` | NEW | 2026-03-06 | OBS start verification (no false-positive stream started) |
| `test_suno_stt_extractor.py` | NEW | 2026-03-05 | Suno STT lyrics extraction pipeline tests |
| `test_go_live_steps.py` | UPDATED | 2026-02-28 | Step-by-step Go Live debugging + DOM verification |

---

## 2026-03-06: OBS Startup Verification + Broadcast Setup Guard

### Added: `test_obs_controller_startup.py`
**Purpose**: Ensure OBS auto-start only reports success when stream output becomes active.

**Test Cases**:
1. `test_start_streaming_already_active`: returns success without redundant StartStream call.
2. `test_start_streaming_waits_until_active`: waits/polls until `output_active=True`.
3. `test_start_streaming_reports_inactive_timeout`: fails with deterministic error when output never activates.
4. `test_ensure_stream_service_custom_updates_service`: configures `rtmp_custom` server/key in OBS service settings.
5. `test_ensure_stream_service_custom_noop_when_already_set`: avoids unnecessary reconfiguration when target already matches.

**Why**:
- Fixed false-positive startup where logs said `Streaming started!` while OBS was still waiting on
  "Create broadcast and start streaming" UI flow.

**Run Tests**:
```bash
pytest modules/platform_integration/antifafm_broadcaster/tests/test_obs_controller_startup.py -v
```

---

## 2026-03-05: Suno STT Lyrics Extractor Tests

### Added: `test_suno_stt_extractor.py`
**Purpose**: Test fully automated Suno lyrics extraction via Speech-to-Text

**Test Classes**:
1. `TestSunoAudioDownloader` - CDN URL construction, cache directory
2. `TestLyricsDeduplicator` - Hash generation, normalization, duplicate detection
3. `TestSunoSTTTranscriber` - WSP 84 FasterWhisperSTT reuse verification
4. `TestSunoSTTLyricsExtractor` - Full pipeline integration
5. `TestCLIIntegration` - CLI --help, --stats commands
6. `TestLaunchIntegration` - launch.py import, SKILLz JSON validation

**Key Tests**:
- `test_hash_normalization`: Verifies lyrics with different whitespace/case produce same hash
- `test_deduplicator_detects_duplicate`: Verifies duplicate lyrics are detected across songs
- `test_wsp84_reuse_import`: Verifies FasterWhisperSTT imported from voice_command_ingestion
- `test_skill_json_valid`: Verifies suno_stt_extract.json SKILLz file is valid

**WSP Compliance**:
- WSP 5: Test coverage for new STT functionality
- WSP 72: Module independence (no cross-module test dependencies)
- WSP 84: Validates code reuse of FasterWhisperSTT

**Run Tests**:
```bash
pytest modules/platform_integration/antifafm_broadcaster/tests/test_suno_stt_extractor.py -v
```

---

## 2026-02-28: Exact DOM Selectors (012-provided)

### Updated: `src/youtube_go_live.py`
**Changes**:
- Edit button: Now uses `#edit-button` (exact selector from 012)
- Title input: Now uses `#title-textarea` inside `#title-wrapper`
- Description: Now uses `#description-textarea` inside `#description-wrapper`
- Save button: Now uses `#save-button` (exact selector from 012)
- CLI: Added `--json` and `--status` flags for OpenClaw/IronClaw

**Selector Priority**:
```
Method 1: Direct ID (#edit-button, #title-textarea, etc.)
Method 2: Wrapper + nested ID (#title-wrapper > #title-textarea)
Method 3: Fallback (aria-label, text match)
```

---

## 2026-02-28: Stream Edit Testing + 15s Studio Wait

### Updated: `test_go_live_steps.py`
**Changes**:
- Added `test_edit_stream()` function - scans for Edit buttons and input fields
- Increased studio load wait: 3s → 15s (YouTube Studio is slow)
- Added screenshot after studio loads
- Added screenshot of edit dialog

**New Test Step (6b)**:
```
[STEP 6b] Testing stream edit functionality...
  - Scans for edit buttons (aria-label, icon)
  - Clicks Edit button if found
  - Scans input fields in dialog
  - Takes screenshot of edit dialog
```

---

## 2026-02-28: DOM Polling Verification

### Updated: `test_go_live_steps.py`
**Change**: Replaced fixed 2-second wait with DOM polling verification

**Before**:
```python
print("  [INFO] Waiting 2 seconds for dropdown menu...")
time.sleep(2)
```

**After**:
```python
dropdown_verified = verify_dropdown_appeared(driver, timeout=5)
# Polls DOM every 300ms for menu items
```

**Why Changed**:
- Fixed delays are fragile (too fast = miss dropdown, too slow = waste time)
- DOM polling verifies dropdown actually appeared
- Reports item count and detection time for debugging
- Fails gracefully if dropdown doesn't appear

**New Function**: `verify_dropdown_appeared(driver, timeout=5)`
- Polls every 300ms for menu items
- Returns True when items detected, False on timeout
- Prints detection time and item list

---

## 2026-02-27: Initial Test Suite Creation

### Added: `test_go_live_steps.py`
**Purpose**: Debug YouTube Go Live automation step-by-step

**Test Steps**:
1. Check Chrome debug port 9222
2. Connect via Selenium
3. Navigate to YouTube Studio `/livestreaming/dashboard`
4. Scan and print all visible buttons
5. Click CREATE button
6. Scan and print menu items
7. Click "Go live" in dropdown
8. Check stream status
9. Take screenshots at each step

**Why Created**:
- Go Live automation not clicking buttons
- Need visibility into what buttons exist on page
- YouTube Studio UI uses shadow DOM and custom elements
- Screenshots help debug without manual inspection

**Output**:
- Console: Step-by-step progress with button lists
- Screenshots: `logs/screenshot_*.png`

---

## Planned Tests

### `test_ffmpeg_stream.py` (TODO)
- Test FFmpeg command generation
- Test RTMP connection to YouTube
- Verify keyframe settings
- Check bitrate/buffer configuration

### `test_stream_verification.py` (TODO)
- Test `verify_stream_connected()` function
- Mock DOM responses
- Test timeout handling

### `test_login_detection.py` (TODO)
- Test all 5 login detection methods
- Test signed-out state detection
- Test Studio vs regular YouTube detection

---

## Test Infrastructure

### Chrome Debug Mode
Tests require Chrome running with debug port:
```powershell
chrome.exe --remote-debugging-port=9222
```

### Dependencies
- `selenium` - Browser automation
- Chrome browser with YouTube login

### Screenshot Storage
Screenshots saved to `logs/` with timestamps for debugging.
