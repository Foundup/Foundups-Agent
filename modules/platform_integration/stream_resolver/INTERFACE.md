# Stream Resolver Module Interface

## Overview
The Stream Resolver module is responsible for finding and validating YouTube livestreams. It handles API interactions to detect active or upcoming livestreams for a channel and retrieve their associated chat IDs.

It also includes a no-quota scraping path (NoQuotaStreamChecker) that checks `/live` and `/streams` indicators with optional API confirmation. When the API is disabled or unavailable, strong indicators can be trusted to avoid false negatives.

**Note:** Since 2025-12-28, all potentially blocking I/O calls in this module are wrapped in `asyncio.to_thread` to prevent event loop stalls.

## Exports
This module exports:
- `get_active_livestream_video_id`: Function to find an active livestream and its chat ID
- `check_video_details`: Function to retrieve details about a specific video
- `search_livestreams`: Function to search for livestreams of a specific type

## Functions

### `get_active_livestream_video_id(youtube_client: Resource, channel_id: str) -> Optional[Tuple[str, str]]`
Finds the active livestream and its associated live chat ID for a specified YouTube channel.

**Parameters:**
- `youtube_client`: An authenticated YouTube API client (googleapiclient.discovery.Resource)
- `channel_id`: YouTube channel ID to check for livestreams

**Returns:**
- `Optional[Tuple[str, str]]`: A tuple containing (video_id, live_chat_id) if found, None otherwise

**Behavior:**
- First checks for a YOUTUBE_VIDEO_ID override in environment variables
- Searches for active livestreams, then upcoming livestreams if no active ones found
- Retrieves the live chat ID for the found livestream
- Uses exponential backoff with jitter for retries
- Tracks consecutive failures to adapt retry behavior
- May raise QuotaExceededError if YouTube API quota is exhausted

### `check_video_details(youtube_client: Resource, video_id: str, retry_count: int = 0, previous_delay: float = None) -> Optional[dict]`
Retrieves detailed information about a specific YouTube video, including its livestream status.

**Parameters:**
- `youtube_client`: An authenticated YouTube API client
- `video_id`: ID of the YouTube video to check
- `retry_count`: Number of retries attempted so far (internal use)
- `previous_delay`: Previous delay used for smoothing (internal use)

**Returns:**
- `Optional[dict]`: Dictionary containing video details if found, None otherwise

**Behavior:**
- Makes an API call to retrieve video details including livestream information
- Implements throttling to respect API rate limits
- Handles quota exceeded errors with retries and fallback API keys
- Returns full video details from the YouTube API response

### `search_livestreams(youtube_client: Resource, event_type: str = "live", retry_count: int = 0, previous_delay: float = None, consecutive_failures: int = 0) -> Optional[str]`
Searches for livestreams of a specific type (live or upcoming) for the configured channel.

**Parameters:**
- `youtube_client`: An authenticated YouTube API client
- `event_type`: Type of livestream to search for ("live" or "upcoming")
- `retry_count`: Number of retries attempted so far (internal use)
- `previous_delay`: Previous delay used for smoothing (internal use)
- `consecutive_failures`: Number of consecutive failed attempts (internal use)

**Returns:**
- `Optional[str]`: Video ID of the first found livestream, None if none found

**Behavior:**
- Searches for livestreams of the specified type for the configured channel
- Implements throttling and backoff strategies for API rate limits
- Handles quota exceeded errors with retries
- May raise QuotaExceededError if YouTube API quota is exhausted after maximum retries

## Custom Exceptions

### `QuotaExceededError`
Custom exception raised when YouTube API quota is exceeded after maximum retry attempts.

## Usage Example
```python
from modules.stream_resolver import get_active_livestream_video_id
from modules.youtube_auth import get_authenticated_service

# Get authenticated YouTube API client
youtube = get_authenticated_service()

# Get channel ID from environment or configuration
channel_id = "UC-CHANNEL-ID"

# Get active livestream and chat ID
try:
    result = get_active_livestream_video_id(youtube, channel_id)
    if result:
        video_id, chat_id = result
        print(f"Found livestream: {video_id} with chat: {chat_id}")
    else:
        print("No active livestream found")
except QuotaExceededError:
    print("YouTube API quota exceeded")
```

## Dependencies
- googleapiclient.discovery
- googleapiclient.errors
- utils.oauth_manager
- utils.env_loader
- time
- random 
