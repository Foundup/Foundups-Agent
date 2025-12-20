# Instance Lock Module

## Purpose
Prevents multiple instances of YouTube monitor from running simultaneously.

## Features
- PID-based locking mechanism with heartbeat validation
- Process validation to detect stale locks
- Heartbeat-aware cleanup (preserves actively running daemons)
- Automatic detection of duplicate instances
- Clean shutdown with lock release

## Usage
```python
from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock

lock = get_instance_lock("youtube_monitor")
if not lock.acquire():
    print("Another instance already running!")
    exit(1)

try:
    # Your code here
    pass
finally:
    lock.release()
```

## Recent Changes

### 2025-12-15: Safety Gate for Browser Cleanup (Prevents Killing YouTube Chrome)
**Problem**: InstanceLock startup cleanup was terminating any `chrome.exe` process with broad markers like `--remote-debugging` / `user-data-dir`, which can kill the persistent YouTube Studio Chrome session (port `9222`) and break comment engagement/login.

**Fix**:
1. Added an explicit opt-in flag: `INSTANCE_LOCK_CLEANUP_BROWSERS=1`
2. Tightened “automation process” detection to only use explicit markers (e.g., `linkedin_agent`, `x_twitter`)
3. Always protect the primary YouTube Chrome debug session: `--remote-debugging-port=$FOUNDUPS_CHROME_PORT` (default `9222`)

**Result**: Default behavior is non-destructive; browser cleanup runs only when explicitly enabled and won’t kill the YouTube DAE’s primary Chrome session.

### 2025-12-12: 012 Duplicate-Termination + Python-Only Duplicate Detection
**Problem**: Duplicate detection was flagging parent shells (e.g., `bash.exe`) as "main.py instances", blocking launches; 012 non-interactive launches need deterministic auto-cleanup.

**Fix**:
1. Only treat **actual Python interpreter processes** (`python.exe`/`pythonw.exe`) as duplicates
2. Added a `kill_pids()` helper for best-effort duplicate termination and structured results

**Result**: 012 can terminate stale duplicate YouTube DAE processes and continue launching without interactive prompts; shells are no longer misclassified as duplicates.

### 2025-10-24: Heartbeat-Aware Cleanup Fix
**Problem**: Long-running YouTube DAE (64+ minutes) was killed when starting a new instance, despite active heartbeat.

**Root Cause**: `_cleanup_stale_processes()` only checked process age, not heartbeat status.

**Fix**: Added `_has_active_heartbeat()` method that verifies:
1. Process owns the lock file
2. Heartbeat updated within TTL (10 minutes)
3. Only kill if BOTH age > TTL AND heartbeat stale

**Result**: YouTube DAE can now run indefinitely (hours/days) without being killed by duplicate instance checks.

## WSP Compliance
- WSP 50: Pre-action verification
- WSP 84: Prevent duplicate processes
- WSP 3: Module organization
