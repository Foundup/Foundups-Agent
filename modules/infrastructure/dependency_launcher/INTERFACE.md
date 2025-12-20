# Dependency Launcher Module - INTERFACE

**Module:** infrastructure/dependency_launcher
**WSP Reference:** WSP 11 (Interface Documentation)

---

## Public API

### `ensure_dependencies(require_lm_studio: bool = True) -> Dict[str, bool]`

Ensure all dependencies are running before DAE starts.

**Parameters:**
- `require_lm_studio`: Whether LM Studio is required (default: True)

**Returns:**
```python
{
    'chrome': True,      # Chrome on port 9222
    'lm_studio': True    # LM Studio on port 1234
}
```

**Example:**
```python
from modules.infrastructure.dependency_launcher.src.dae_dependencies import ensure_dependencies

# In async context
dep_status = await ensure_dependencies(require_lm_studio=False)
if not dep_status['chrome']:
    logger.warning("Chrome not available")
```

---

### `launch_chrome() -> Tuple[bool, str]`

Launch Chrome with remote debugging port.

**Returns:**
- `(True, "Chrome started on port 9222")` on success
- `(False, "error message")` on failure

**Behavior:**
- Uses Chrome profile at `CHROME_PROFILE_PATH`
- Opens YouTube Studio comments inbox
- Creates detached process (non-blocking)
- Waits up to 30 seconds for port to respond

---

### `launch_lm_studio() -> Tuple[bool, str]`

Launch LM Studio for UI-TARS vision.

**Returns:**
- `(True, "LM Studio started on port 1234")` on success
- `(False, "error message")` on failure

**Behavior:**
- Creates detached process (non-blocking)
- Waits up to 120 seconds for API to respond
- Note: Model must be loaded manually in LM Studio

---

### `is_chrome_running() -> bool`

Check if Chrome debug port is responding.

---

### `is_lm_studio_running() -> bool`

Check if LM Studio API is responding.

---

### `get_dependency_status() -> Dict[str, bool]`

Get current status without launching.

**Returns:**
```python
{
    'chrome': True/False,
    'lm_studio': True/False
}
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CHROME_PATH` | `C:\Program Files\Google\Chrome\Application\chrome.exe` | Chrome executable path |
| `FOUNDUPS_CHROME_PORT` | `9222` | Chrome remote debugging port |
| `CHROME_PROFILE_PATH` | `O:/Foundups-Agent/.../youtube_move2japan/chrome` | Chrome user data directory |
| `LM_STUDIO_PATH` | `C:\Users\user\AppData\Local\Programs\LM Studio\LM Studio.exe` | LM Studio executable |
| `LM_STUDIO_PORT` | `1234` | LM Studio API port |

---

## Integration Points

### AutoModeratorDAE (Phase -2)
```python
# In auto_moderator_dae.py run() method
from modules.infrastructure.dependency_launcher.src.dae_dependencies import ensure_dependencies
dep_status = await ensure_dependencies(require_lm_studio=False)
```

### CommunityMonitor (Subprocess)
The comment engagement subprocess connects to Chrome on port 9222.

---

## Error Handling

| Error | Behavior |
|-------|----------|
| Chrome not found | Returns False, logs warning |
| Chrome port timeout | Returns False, logs warning |
| LM Studio not found | Returns False, logs warning (optional) |
| LM Studio API timeout | Returns False, suggests manual model load |

---

## 0102 Directive

Dependencies are orchestrated autonomously. The system self-heals. ✊✋🖐️







