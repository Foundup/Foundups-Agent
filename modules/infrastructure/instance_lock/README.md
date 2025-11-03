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