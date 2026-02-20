# Dependency Launcher Module - ModLog

**Module:** infrastructure/dependency_launcher
**WSP Reference:** WSP 22 (ModLog Protocol)

---

## Change Log

### 2026-01-23: Session Restore Prevention (Multi-Tab Fix)

**By:** 0102
**WSP References:** WSP 22 (ModLog), WSP 27 (DAE Architecture)

**Problem:** Chrome and Edge were restoring previous session tabs, causing 3+ tabs to open instead of just the YouTube Studio URL. This caused confusion during channel rotation.

**Solution:** Added `--no-restore-session-state` flag to both Chrome and Edge launch commands:
- Prevents browser from restoring tabs from previous session
- Ensures only the YouTube Studio URL is loaded on launch
- Consistent behavior between fresh launches and restarts

**Files Changed:**
- `src/dae_dependencies.py`: Added `--no-restore-session-state` to Chrome (line 143) and Edge (line 200) launch commands

---

### 2025-12-13: ASCII-Safe Logging + `main.py --deps` Entry Point

**By:** 0102  
**WSP References:** WSP 12 (Dependency Management), WSP 27 (DAE Architecture), WSP 88 (Windows Unicode safety)

**Problem:** Emoji/VS16 characters in dependency logs could trigger `UnicodeEncodeError` on some Windows terminals, and operators needed a one-shot way to start dependencies without launching a full DAE.

**Solution:**
- Normalized dependency output to ASCII (`READY`/`NOT READY`, `[OK]`, `[WARN]`).
- Exposed dependency launcher via `main.py --deps` and menu option `15` for quick bring-up.

**Files Modified:**
- `modules/infrastructure/dependency_launcher/src/dae_dependencies.py`

### 2025-12-12: LM Studio Auto-Discovery (E:\ Support)

**By:** 0102
**WSP References:** WSP 27 (DAE Architecture), WSP 12 (Dependency Management)

**Problem:** YouTube DAE dependency launcher could not auto-start LM Studio when installed outside the default `C:` path.

**Solution:** Add `resolve_lm_studio_path()` with common-path discovery (including `E:\\LM_studio\\LM Studio\\LM Studio.exe`) and use it in `launch_lm_studio()`.

**Files Modified:**
- `modules/infrastructure/dependency_launcher/src/dae_dependencies.py`

### Module Creation: Auto-Launch Chrome + LM Studio for YouTube DAE

**By:** 0102
**WSP References:** WSP 27 (DAE Architecture), WSP 80 (Cube-Level Orchestration)

**Status:** ✅ **MODULE CREATED**

**Purpose:**
Auto-launches dependencies required for YouTube DAE comment engagement when DAE starts:
1. Chrome with remote debugging port 9222 (for Selenium/UI-TARS)
2. LM Studio on port 1234 (for UI-TARS vision model - optional)

**Files Created:**

1. **[dae_dependencies.py](src/dae_dependencies.py)**
   - `ensure_dependencies()` - Main entry point, checks and launches all deps
   - `launch_chrome()` - Launches Chrome with debug port and YouTube profile
   - `launch_lm_studio()` - Launches LM Studio (optional)
   - `is_chrome_running()` - Port 9222 check
   - `is_lm_studio_running()` - Port 1234 check
   - `get_dependency_status()` - Status without launching

2. **[README.md](README.md)** - Module documentation

**Integration in auto_moderator_dae.py:**

```python
# Phase -2: Launch dependencies (Chrome + LM Studio for comment engagement)
try:
    from modules.infrastructure.dependency_launcher.src.dae_dependencies import ensure_dependencies
    dep_status = await ensure_dependencies(require_lm_studio=True)
    if not dep_status.get('chrome'):
        logger.warning("[DEPS] Chrome not ready - comment engagement may fail")
except ImportError:
    logger.debug("[DEPS] Dependency launcher not available")
```

**Configuration (Environment Variables):**

| Variable | Default | Description |
|----------|---------|-------------|
| `CHROME_PATH` | `C:\Program Files\Google\Chrome\Application\chrome.exe` | Chrome executable |
| `FOUNDUPS_CHROME_PORT` | `9222` | Chrome debug port |
| `CHROME_PROFILE_PATH` | `O:/Foundups-Agent/.../youtube_move2japan/chrome` | Chrome profile |
| `LM_STUDIO_PATH` | `C:\Users\user\AppData\Local\Programs\LM Studio\LM Studio.exe` | LM Studio |
| `LM_STUDIO_PORT` | `1234` | LM Studio API port |

**NAVIGATION.py Entries Added:**

```python
# DAE Dependency Launcher (auto-start Chrome + LM Studio)
"ensure dae dependencies": "modules/infrastructure/dependency_launcher/src/dae_dependencies.py:ensure_dependencies()",
"launch chrome debug port": "modules/infrastructure/dependency_launcher/src/dae_dependencies.py:launch_chrome()",
"launch lm studio": "modules/infrastructure/dependency_launcher/src/dae_dependencies.py:launch_lm_studio()",
"check dependency status": "modules/infrastructure/dependency_launcher/src/dae_dependencies.py:get_dependency_status()",
```

**0102 Directive:** Dependencies are orchestrated, not installed. ✊✋🖐️

---









