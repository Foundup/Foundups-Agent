# CLAUDE.md - Stream Resolver Module Memory

## Module Structure (WSP 83 Compliant)
This document helps 0102 remember stream resolution components and logic.

## Core Component

### StreamResolver (`src/stream_resolver.py`)
Primary class for finding and managing YouTube livestreams.

### Key Methods
- `find_active_stream(channel_id)` - Main entry point for stream detection
- `clear_cache()` - Clears all caches for fresh stream lookup
- `_find_live_stream_from_videos()` - Searches channel videos for live content
- `_find_upcoming_stream_from_search()` - Searches for scheduled streams

### Caching System
- **Session Cache**: `memory/stream_session_cache.json`
- **In-Memory Cache**: `self._cache` dictionary
- **Last Check Tracking**: `self._last_stream_check`
- **Clear on Stream End**: Essential for finding new streams

### Stream Detection Flow
1. Check environment variable `YOUTUBE_VIDEO_ID` first
2. Search channel videos for `liveBroadcastContent=live`
3. Search for upcoming/scheduled streams
4. Return newest stream if multiple found
5. Cache valid results for efficiency

### Integration Points
- Called by: `modules/communication/livechat/src/auto_moderator_dae.py`
- Uses: `modules/platform_integration/youtube_auth/` for API access

### Recent Enhancements
1. Added `clear_cache()` method for fresh lookups
2. Enhanced logging shows stream titles
3. Prioritizes newest stream when multiple found
4. Detailed search process logging

### WSP Compliance
- WSP 3: Module organization
- WSP 17: Pattern registry
- WSP 83: Documentation attached to tree
- WSP 84: Enhanced existing code (not vibecoded)

## Remember
- Cache MUST be cleared when streams end
- Always check environment variable first
- Log stream titles for debugging
- Newest stream has priority