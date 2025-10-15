# NoQuotaStreamManager Interface Documentation

## Overview

The `NoQuotaStreamManager` handles NO-QUOTA operational mode for stream detection, implementing intelligent multi-channel rotation with QWEN integration and pattern-based predictions.

## Public API

### Class: NoQuotaStreamManager

#### Constructor
```python
NoQuotaStreamManager(
    no_quota_checker,      # Required: NoQuotaStreamChecker instance
    database=None,         # Optional: Database for pattern predictions
    qwen_integration=None, # Optional: QWEN for channel intelligence
    logger=None           # Optional: Logger instance
)
```

#### Methods

##### find_live_stream_no_quota(channel_id: Optional[str] = None) -> Optional[Tuple[str, None]]
**Purpose:** Execute complete NO-QUOTA stream detection with multi-channel rotation.

**Parameters:**
- `channel_id`: Specific channel ID to check (optional). If None, rotates through all configured channels.

**Returns:**
- `Tuple[str, None]`: (video_id, None) if live stream found
- `None`: If no live stream found on any channel

**Behavior:**
1. Gets channel list from environment variables
2. Sets up rotation strategy (single channel vs multi-channel)
3. Loops through channels with round-robin selection
4. Applies QWEN intelligence for prioritization when available
5. Checks environment variable video first if set
6. Searches each channel for live streams using web scraping
7. Handles rate limiting and updates QWEN state
8. Records results to database when available
9. Returns first live stream found

**Error Handling:**
- Rate limit detection and recovery
- QWEN integration failures (non-blocking)
- Database errors (non-blocking, logged as warnings)
- Channel search timeouts (continues to next channel)

## Dependencies

### Required
- `no_quota_checker`: Instance of `NoQuotaStreamChecker` for web scraping operations

### Optional
- `database`: Database instance with `predict_next_stream_time()`, `record_stream_start()`, `analyze_and_update_patterns()`, and `record_check()` methods
- `qwen_integration`: QWEN integration with `get_channel_profile()` method returning objects with `should_check_now()` and `record_429_error()` methods
- `logger`: Python logger instance (defaults to module logger)

## Environment Variables

The manager reads the following environment variables for channel configuration:

- `MOVE2JAPAN_CHANNEL_ID`: First priority channel (default: 'UCklMTNnu5POwRmQsg5JJumA')
- `CHANNEL_ID`: Second priority channel (default: 'UC-LSSlOZwpGIRIYihaz8zCw')
- `CHANNEL_ID2`: Third priority channel (default: 'UCSNTUXjAgpd4sgWYP0xoJgw')
- `YOUTUBE_VIDEO_ID`: Specific video ID to check first (optional)

## Logging

The manager uses structured logging with the following prefixes:
- `[NO-QUOTA]`: General NO-QUOTA operations
- `[TEST]`: Single channel testing mode
- `[QWEN]`: QWEN intelligence operations
- `[ENV]`: Environment variable video checking
- `[SEARCH]`: Channel search operations
- `[SUCCESS]`: Stream found
- `[RATELIMIT]`: Rate limiting events
- `[SKIP]`: Channel skipping (QWEN decision)
- `[WAIT]`: Inter-channel delays
- `[ERROR]`: Operation failures
- `[DB]`: Database operations

## Integration Example

```python
from modules.platform_integration.stream_resolver.src.no_quota_stream_manager import NoQuotaStreamManager
from modules.platform_integration.stream_resolver.src.no_quota_stream_checker import NoQuotaStreamChecker

# Setup dependencies
no_quota_checker = NoQuotaStreamChecker()
database = AgentDB()  # optional
qwen = get_qwen_youtube()  # optional

# Create manager
manager = NoQuotaStreamManager(
    no_quota_checker=no_quota_checker,
    database=database,
    qwen_integration=qwen
)

# Find live stream
result = manager.find_live_stream_no_quota()
if result:
    video_id, chat_id = result
    print(f"Found live stream: {video_id}")
else:
    print("No live streams found")
```

## Performance Characteristics

- **API Usage:** 0 API quota (web scraping only)
- **Typical Latency:** 2-5 seconds per channel check
- **Multi-channel Mode:** Up to 3 channels checked sequentially
- **Rate Limiting:** Automatic cooldown and QWEN state updates
- **Memory Usage:** Minimal (no caching, stateless operations)

## Error Recovery

- **Rate Limits:** Updates QWEN heat level, reduces channel confidence, continues to next channel
- **Network Errors:** Logged, continues to next channel
- **QWEN Failures:** Logged as debug, continues without intelligence
- **Database Failures:** Logged as warnings, continues without pattern recording
- **Channel Failures:** Logged, continues to next channel in rotation

## Testing

The module supports comprehensive testing through dependency injection:

```python
# Mock testing
mock_checker = Mock()
mock_db = Mock()
mock_qwen = Mock()

manager = NoQuotaStreamManager(
    no_quota_checker=mock_checker,
    database=mock_db,
    qwen_integration=mock_qwen
)

# Test specific scenarios
result = manager.find_live_stream_no_quota("UC123...")
```

## WSP Compliance

- **WSP 3:** Platform Integration domain for YouTube operations
- **WSP 11:** Clean interface with dependency injection
- **WSP 49:** Module structure with proper separation
- **WSP 62:** File size management (<200 lines target)
