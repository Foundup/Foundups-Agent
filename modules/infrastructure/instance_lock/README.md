# Instance Lock Module

## Purpose
Prevents multiple instances of YouTube monitor from running simultaneously.

## Features
- PID-based locking mechanism
- Process validation to detect stale locks
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

## WSP Compliance
- WSP 50: Pre-action verification
- WSP 84: Prevent duplicate processes
- WSP 3: Module organization