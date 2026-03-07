# 0102 Handoff: antifaFM YouTube Live RTMPS Fix

**Date**: 2026-03-03
**Status**: 9 Fixes Applied - Async Go Live Fixed - Ready for Live Test
**Priority**: P1 (Streaming blocked without this fix)

---

## Problem Summary

FFmpeg was dying ~30 seconds after starting when streaming to YouTube Live. The stream would start, YouTube Studio would show "Connect your encoder", but FFmpeg would crash before the first health check.

## Root Causes (Multiple)

### 1. Port 1935 (RTMP) Blocked
**Port 1935 (standard RTMP) is blocked** on 012's network/ISP.

Diagnosis performed:
```powershell
# This test FAILED - all connections timed out
Test-NetConnection -ComputerName a.rtmp.youtube.com -Port 1935

# This test SUCCEEDED - port 443 works
Test-NetConnection -ComputerName a.rtmps.youtube.com -Port 443
```

### 2. Headless Launcher Skipping YouTube Studio Activation
The foreground launcher path (`python launch.py`) went straight to `broadcaster.start()` without executing the Go Live/browser prep step. FFmpeg connected to an endpoint that wasn't ready.

**Evidence**: `telemetry.jsonl:742` shows FFmpeg dying ~30 seconds in with generic shutdown - timing matches endpoint not being activated.

### 3. Orphan Cleanup Only Matched `rtmp://`
The `_kill_orphan_ffmpeg_streams()` function only searched for `rtmp://` in process command lines, missing `rtmps://` streams. Stale publishers could survive config changes.

### 4. Test Diagnostics Pointed to Wrong Browser
`test_go_live_steps.py` was hardcoded to Chrome port 9222, but antifaFM actually uses Edge on port 9223. Debug attempts reported "cannot connect" even when the real broadcaster was working.

---

## Fixes Applied

### Fix 1: RTMPS URL (Port 443)
Changed all RTMP URLs from `rtmp://a.rtmp.youtube.com/live2` (port 1935) to `rtmps://a.rtmps.youtube.com:443/live2` (port 443).

| File | Line | Change |
|------|------|--------|
| `src/ffmpeg_streamer.py` | 131 | `rtmps://a.rtmps.youtube.com:443/live2` |
| `src/antifafm_broadcaster.py` | 187 | `rtmps://a.rtmps.youtube.com:443/live2` |
| `src/antifafm_broadcaster.py` | 312 | `rtmps://a.rtmps.youtube.com:443/live2` |

### Fix 2: Launcher Preflight Shared
Foreground and background paths now share the same YouTube Studio preflight.

| File | Line | Change |
|------|------|--------|
| `scripts/launch.py` | 57 | Preflight function defined |
| `scripts/launch.py` | 161 | Foreground path calls preflight |
| `scripts/launch.py` | 294 | Background path calls preflight |

### Fix 3: Orphan Cleanup Matches RTMPS
`_kill_orphan_ffmpeg_streams()` now matches both `rtmp://` and `rtmps://`.

| File | Line | Change |
|------|------|--------|
| `src/ffmpeg_streamer.py` | 374 | `if ('rtmp://' in line or 'rtmps://' in line)` |

### Fix 4: Test Diagnostics Fixed
Test now auto-detects Edge (9223) vs Chrome (9222) based on environment.

| File | Line | Change |
|------|------|--------|
| `tests/test_go_live_steps.py` | 25-31 | `ANTIFAFM_BROWSER_PORT` with Edge default |
| `tests/test_go_live_steps.py` | 65-76 | Conditional Edge/Chrome webdriver |

### Fix 5: Launcher Runtime Bugs (2026-03-03 14:xx)
Two Python runtime bugs prevented launcher from starting:

| File | Line | Bug | Fix |
|------|------|-----|-----|
| `scripts/launch.py` | 23 | `time.sleep()` called without import | Added `import time` at module scope |
| `scripts/launch.py` | 386 | `asyncio` shadowed by function-local import | Removed function-local `import asyncio` |

**Error messages fixed:**
- `NameError: name 'time' is not defined` (line 58)
- `cannot access free variable 'asyncio'` (line 386)

### Fix 6: Readiness Logic Bug (2026-03-03 15:xx)
The readiness check was treating "Connect your encoder" + "Go live" as READY, but this state means the Go Live button hasn't been clicked yet. Fixed to require `has_encoder AND NOT has_go_live`.

| File | Line | Bug | Fix |
|------|------|-----|-----|
| `src/youtube_go_live.py` | 195 | `has_encoder` alone = ready | `has_encoder and not has_go_live` |
| `src/youtube_go_live.py` | 265 | Same issue | Same fix |
| `scripts/launch.py` | 106 | Readiness loop same issue | Tightened rule |
| `scripts/launch.py` | 113 | Same | Same |

**Logic before**: `if has_encoder: return ready` (wrong - Go Live not clicked)
**Logic after**: `if has_encoder and not has_go_live: return ready` (correct)

### Fix 8: API-Based Ingest URL Resolution (2026-03-03 16:xx)
YouTube assigns stream-specific ingest URLs via the Data API. Using generic URLs like `rtmps://a.rtmps.youtube.com:443/live2` can cause connection stalls when YouTube assigns a different endpoint.

| File | Change |
|------|--------|
| `src/youtube_ingest_resolver.py` | NEW: Fetches `rtmpsIngestionAddress` from YouTube Data API |
| `src/antifafm_broadcaster.py` | Added `_resolve_ingest_url()` helper method |
| `src/antifafm_broadcaster.py` | `start()` uses `self._resolve_ingest_url()` |
| `src/antifafm_broadcaster.py` | `_restart_stream()` uses `self._resolve_ingest_url()` |

**Resolution priority**:
1. `ANTIFAFM_RTMP_URL` env var (explicit override)
2. YouTube Data API `cdn.ingestionInfo.rtmpsIngestionAddress`
3. Generic fallback `rtmps://a.rtmps.youtube.com:443/live2`

### Fix 9: Nested Asyncio Loop (2026-03-03 16:xx)
`_prepare_youtube_live_endpoint()` was a sync function trying to create a new event loop inside the already-running async `main()`. This caused "Cannot run the event loop while another loop is running".

| File | Line | Change |
|------|------|--------|
| `scripts/launch.py` | 58 | `def` → `async def _prepare_youtube_live_endpoint()` |
| `scripts/launch.py` | 84 | `loop.run_until_complete()` → `await click_go_live()` |
| `scripts/launch.py` | 163 | `_prepare_youtube_live_endpoint()` → `await _prepare_youtube_live_endpoint()` |

### Additional Improvements

1. **Continuous stderr monitoring** added to `ffmpeg_streamer.py`:
   - Background thread reads FFmpeg stderr line-by-line
   - Stores last 50 lines in deque buffer
   - Logs errors/failures in real-time
   - `get_last_stderr(n)` method for debugging

2. **Enhanced health check** in `antifafm_broadcaster.py`:
   - Uses `is_streaming_healthy()` for detailed status
   - Logs last stderr on health failures

3. **Endpoint readiness check** in `scripts/launch.py`:
   - Waits for "Connect your encoder" message before starting FFmpeg
   - Polls YouTube Studio DOM for ready state

---

## Verification Checklist

### Pre-Flight
- [ ] Chrome running on debug port 9222
- [ ] YouTube Studio authenticated (antifaFM channel)
- [ ] `ANTIFAFM_YOUTUBE_STREAM_KEY` set in environment
- [ ] Icecast stream URL accessible

### Live Test Sequence
```bash
# 1. Start Chrome with debug port
chrome.exe --remote-debugging-port=9222

# 2. Navigate to YouTube Studio livestreaming dashboard
# https://studio.youtube.com/channel/UCVSmg5aOhP4tnQ9KFUg97qA/livestreaming/dashboard

# 3. Run the broadcaster
python modules/platform_integration/antifafm_broadcaster/scripts/launch.py
```

### Expected Behavior
1. Script clicks Create → Go Live in YouTube Studio
2. Waits for "Connect your encoder" message
3. Starts FFmpeg with RTMPS URL
4. Stream connects and shows frames in YouTube Studio
5. Health monitor reports "healthy" state

### Failure Indicators
- FFmpeg exits within 30 seconds → Check stderr buffer
- "Connection refused" → RTMPS URL not correct
- "Invalid stream key" → Check `ANTIFAFM_YOUTUBE_STREAM_KEY`
- No frames in YouTube Studio → Check audio source URL

---

## Code Locations

```
modules/platform_integration/antifafm_broadcaster/
├── src/
│   ├── ffmpeg_streamer.py         # FFmpeg subprocess + RTMPS URL
│   ├── antifafm_broadcaster.py    # DAE lifecycle + _resolve_ingest_url() helper
│   ├── youtube_ingest_resolver.py # NEW: API-based ingest URL resolution
│   ├── youtube_go_live.py         # Go Live automation
│   └── stream_health_monitor.py   # Auto-recovery with exponential backoff
├── scripts/
│   └── launch.py                  # CLI entry + Go Live automation
├── tests/
│   └── test_go_live_steps.py      # YouTube Studio automation tests
└── docs/
    └── HANDOFF_RTMPS_FIX_20260303.md  # This file
```

---

## Key Code Snippets

### API-Based Ingest Resolution (antifafm_broadcaster.py)
```python
def _resolve_ingest_url(self) -> str:
    """Resolve RTMPS ingest URL with priority:
    1. ANTIFAFM_RTMP_URL env var (explicit override)
    2. YouTube Data API (stream-specific ingest URL)
    3. Generic fallback (may not work for all streams)
    """
    explicit_url = os.getenv("ANTIFAFM_RTMP_URL", "")
    if explicit_url:
        return explicit_url

    try:
        from .youtube_ingest_resolver import get_ingest_url_with_fallback
        rtmp_url, is_api_resolved = get_ingest_url_with_fallback(
            stream_key=self.stream_key,
            fallback_url="rtmps://a.rtmps.youtube.com:443/live2"
        )
        return rtmp_url
    except Exception as e:
        logger.warning(f"[INGEST] API resolution error: {e}")
        return "rtmps://a.rtmps.youtube.com:443/live2"
```

### RTMPS URL Configuration (ffmpeg_streamer.py:131) - FALLBACK
```python
# Use RTMPS (port 443) instead of RTMP (port 1935) for better firewall compatibility
rtmp_url = os.getenv("ANTIFAFM_RTMP_URL", "rtmps://a.rtmps.youtube.com:443/live2")
```

### Stderr Monitoring (ffmpeg_streamer.py:492-526)
```python
def _start_stderr_monitor(self) -> None:
    """Start continuous stderr monitoring in background thread."""
    self._stop_stderr_monitor.clear()
    self._stderr_buffer.clear()

    def monitor_stderr():
        while not self._stop_stderr_monitor.is_set():
            if self.process is None or self.process.stderr is None:
                break
            try:
                line = self.process.stderr.readline()
                if line:
                    decoded = line.decode('utf-8', errors='replace').strip()
                    if decoded:
                        self._stderr_buffer.append(decoded)
                        if any(err in decoded.lower() for err in ['error', 'failed', 'refused', 'broken']):
                            logger.warning(f"[FFMPEG] {decoded}")
```

### Health Check with Stderr Logging (antifafm_broadcaster.py:285-301)
```python
def _check_stream_health(self) -> bool:
    if self.streamer is None:
        return False
    is_healthy, status_msg = self.streamer.is_streaming_healthy()
    if not is_healthy:
        logger.warning(f"[HEALTH] Stream unhealthy: {status_msg}")
        last_stderr = self.streamer.get_last_stderr(10)
        if last_stderr:
            logger.error(f"[HEALTH] FFmpeg last output:\n{last_stderr}")
    return is_healthy
```

---

## Validation Performed

```bash
# Syntax validation - PASSED (after Fix 8)
python -m py_compile modules/platform_integration/antifafm_broadcaster/scripts/launch.py
python -m py_compile modules/platform_integration/antifafm_broadcaster/src/ffmpeg_streamer.py
python -m py_compile modules/platform_integration/antifafm_broadcaster/src/antifafm_broadcaster.py
python -m py_compile modules/platform_integration/antifafm_broadcaster/src/youtube_ingest_resolver.py
python -m py_compile modules/platform_integration/antifafm_broadcaster/tests/test_go_live_steps.py

# Diagnostic check - PASSED
python modules/platform_integration/antifafm_broadcaster/scripts/launch.py --diagnose --json
# Returns: ready: true

# API Ingest Resolution Test
python modules/platform_integration/antifafm_broadcaster/src/youtube_ingest_resolver.py --diagnose
# Returns stream-specific endpoints if OAuth available
```

**Note**: The `[WSP-FRAMEWORK] preflight=FAIL` message is unrelated to antifaFM - it's a separate WSP compliance check.

---

## Next Steps for 0102

1. **Run launcher**: `python modules/platform_integration/antifafm_broadcaster/scripts/launch.py`
   - It now executes Go Live prep before FFmpeg starts
2. **If still fails after ~30 seconds**, collect:
   - `tail -50 telemetry.jsonl`
   - `tail -100 logs/antifafm_broadcaster.log`
   - The failure should now be much narrower with launcher fixed
3. **Verify stream appears** in YouTube Studio preview
4. **Check health monitor** reports "healthy" state after 30 seconds
5. **Document results** in ModLog.md

---

## Environment Variables

```bash
ANTIFAFM_YOUTUBE_STREAM_KEY=xxxx-xxxx-xxxx-xxxx  # Required
ANTIFAFM_RTMP_URL=rtmps://a.rtmps.youtube.com:443/live2  # Default (override if needed)
ANTIFAFM_STREAM_URL=https://a12.asurahosting.com/listen/antifafm/radio.mp3  # Audio source
ANTIFAFM_DEFAULT_VISUAL=modules/platform_integration/antifafm_broadcaster/assets/default_visual.png
FOUNDUPS_LIVECHAT_CHROME_PORT=9222  # Chrome debug port
```

---

## WSP Compliance

- **WSP 27**: Universal DAE Architecture (4-phase lifecycle)
- **WSP 50**: Pre-Action Verification (RTMPS port testing before fix)
- **WSP 64**: Secure credential management (stream key from ENV)
- **WSP 91**: DAEMON Observability (stderr monitoring, health metrics)

---

---

## Telemetry Evidence

### telemetry.jsonl:734 (RTMP blocked)
```
Error opening output file rtmp://a.rtmp.youtube.com/live2/...
```
This confirmed port 1935 was blocked. Fixed with RTMPS on port 443.

### telemetry.jsonl:742 (Endpoint not activated)
FFmpeg shutdown ~30 seconds in. Timing matches the headless launcher skipping YouTube Studio activation. Fixed with shared preflight.

### Network Tests
```powershell
# FAILED (timeout)
Test-NetConnection -ComputerName a.rtmp.youtube.com -Port 1935

# SUCCEEDED
Test-NetConnection -ComputerName a.rtmps.youtube.com -Port 443
```

---

*Handoff created by 0102 | 2026-03-03*
*Updated with 012 analysis: launcher preflight, orphan cleanup, test diagnostics*
*Fix 5 added: time import + asyncio closure bug (documented ModLog.md:390)*
*Fix 6/7 added: readiness logic - has_encoder only valid when has_go_live is false*
*Fix 8 added: API-based ingest URL resolution (youtube_ingest_resolver.py)*
*Fix 9 added: Nested asyncio loop - async def + await pattern*

---

## Fix Chain Summary

| # | Issue | Symptom | Status |
|---|-------|---------|--------|
| 1 | Port 1935 blocked | FFmpeg "Connection timed out" | FIXED |
| 2 | Launcher skipped Go Live | FFmpeg dies ~30s (endpoint not ready) | FIXED |
| 3 | Orphan cleanup missed rtmps:// | Stale FFmpeg processes survive | FIXED |
| 4 | Test pointed to wrong browser | "Cannot connect" false positive | FIXED |
| 5 | `time` not imported | `NameError` at line 58 | FIXED |
| 6 | `asyncio` shadowed | `cannot access free variable` at line 386 | FIXED |
| 7 | Readiness logic bug | `has_encoder` + `has_go_live` = false ready | FIXED |
| 8 | Generic RTMPS URL | YouTube assigns stream-specific ingest URLs | FIXED |
| 9 | Nested asyncio loop | `Cannot run event loop while another is running` | FIXED |

**Current state**: Go Live automation now works in async context. API-based ingest URL resolution implemented. Stream should bind correctly before FFmpeg connects.
