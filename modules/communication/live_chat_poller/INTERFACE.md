# Live Chat Poller Module Interface

## Overview
The Live Chat Poller module provides functionality to retrieve messages from YouTube Live Chat. It handles the polling mechanism, including pagination, rate limiting, and error recovery.

## Exports
This module exports:
- `LiveChatPoller`: Class for polling YouTube Live Chat messages

## Classes

### `LiveChatPoller`
Polls YouTube Live Chat for new messages, handling pagination, rate limiting, and error recovery.

#### Constructor

##### `__init__(youtube_service, video_id: str)`
Initializes a new LiveChatPoller instance.

**Parameters:**
- `youtube_service`: Authenticated YouTube API service object
- `video_id`: ID of the YouTube video/livestream to connect to

**Behavior:**
- Sets up the connection parameters with the provided YouTube service and video ID
- Initializes the state for chat ID and pagination tracking

#### Public Methods

##### `get_live_chat_id() -> str`
Fetches the live chat ID for the specified video.

**Parameters:**
- None

**Returns:**
- `str`: The live chat ID if found, None otherwise

**Behavior:**
- Makes an API call to retrieve the livestream details for the video
- Extracts the active live chat ID from the response
- Updates the internal chat ID and returns it
- Returns None if no chat ID is found or an error occurs

##### `poll_once() -> tuple`
Polls for new messages once.

**Parameters:**
- None

**Returns:**
- `tuple`: A tuple containing:
  - A list of message objects retrieved from the API
  - The recommended polling interval in milliseconds

**Behavior:**
- Fetches the live chat ID if not already available
- Makes an API call to retrieve new messages
- Updates the next page token for pagination
- Handles HTTP errors, including chat ended or access forbidden scenarios
- Returns an empty list and default interval (5000ms) on error

## Usage Example
```python
from modules.live_chat_poller import LiveChatPoller
from modules.youtube_auth import get_authenticated_service

# Get authenticated YouTube service
youtube = get_authenticated_service()

# Video ID of the livestream
video_id = "YOUR_YOUTUBE_VIDEO_ID"

# Create a poller instance
poller = LiveChatPoller(youtube, video_id)

# Get the live chat ID
chat_id = poller.get_live_chat_id()
if chat_id:
    print(f"Connected to live chat: {chat_id}")
    
    # Poll for messages
    messages, interval = poller.poll_once()
    print(f"Retrieved {len(messages)} messages")
    print(f"Next poll recommended in {interval}ms")
    
    # Process messages
    for message in messages:
        author = message["authorDetails"]["displayName"]
        text = message["snippet"]["displayMessage"]
        print(f"{author}: {text}")
```

## Dependencies
- googleapiclient.errors
- logging
- time 