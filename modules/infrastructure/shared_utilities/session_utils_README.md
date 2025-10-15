# Session Utils Module

## Purpose
Infrastructure utilities for session management and caching, extracted from vibecoded functionality in stream_resolver.py.

## WSP Compliance
- **WSP 3**: Infrastructure domain - shared session management utilities
- **WSP 49**: Clear module structure with single responsibility
- **WSP 62**: Focused functionality (<200 lines)

## Usage
```python
from modules.infrastructure.shared_utilities.session_utils import SessionUtils

# Load cache
cache = SessionUtils.load_cache()

# Save video/chat mapping
SessionUtils.save_cache("VIDEO_ID", "CHAT_ID")

# Try to find cached stream
video_id, chat_id = SessionUtils.try_cached_stream(cache)
```

## Dependencies
- Standard library only (json, os, logging, datetime, typing)

## Testing
Run tests with: `python -m pytest modules/infrastructure/shared_utilities/tests/test_session_utils.py`
