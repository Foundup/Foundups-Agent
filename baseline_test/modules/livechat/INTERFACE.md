# LiveChat Module Interface

## Overview
The LiveChat module provides functionality to connect to a YouTube livestream chat, listen for messages, log them, and send responses. It integrates with other modules like BanterEngine for automated responses and token_manager for credential rotation.

## Exports
This module exports:
- `LiveChatListener`: Class for connecting to and interacting with YouTube livestream chats

## Classes

### `LiveChatListener`
Connects to a YouTube livestream chat, listens for messages, logs them, and provides hooks for sending messages and AI interaction.

#### Constructor

##### `__init__(youtube_service, video_id, live_chat_id=None)`
Initializes a new LiveChatListener instance.

**Parameters:**
- `youtube_service`: Authenticated YouTube API service object
- `video_id`: ID of the YouTube video/livestream to connect to
- `live_chat_id`: Optional. If provided, uses this chat ID directly. Otherwise, it will be retrieved from the video details.

**Behavior:**
- Sets up the connection parameters with the provided YouTube service and video ID
- Initializes memory directory for chat logs
- Sets up trigger detection with BanterEngine
- Configures rate limiting for user interactions

#### Public Methods

##### `async start_listening()`
Starts the chat listener loop to poll for and process messages.

**Parameters:**
- None

**Returns:**
- None

**Behavior:**
- If not already running, retrieves the live chat ID if not provided
- Sends a greeting message if configured
- Enters a continuous polling loop to fetch and process messages
- Updates viewer count periodically to adjust polling intervals
- Processes and logs incoming messages
- Detects emoji triggers and responds with appropriate banter

##### `async send_chat_message(message_text)`
Sends a text message to the live chat.

**Parameters:**
- `message_text`: The text message to send to the chat

**Returns:**
- `bool`: True if message was sent successfully, False otherwise

**Behavior:**
- Truncates messages that exceed the maximum length
- Sends the message via the YouTube API
- Handles authentication errors with token rotation
- Returns success/failure status

## Usage Example
```python
import asyncio
from modules.livechat import LiveChatListener
from modules.youtube_auth import get_authenticated_service

async def main():
    # Get authenticated YouTube service
    youtube = get_authenticated_service()
    
    # Video ID of the livestream
    video_id = "YOUR_YOUTUBE_VIDEO_ID"
    
    # Create and start a listener
    listener = LiveChatListener(youtube, video_id)
    
    try:
        # Start listening for messages
        await listener.start_listening()
    except KeyboardInterrupt:
        print("Interrupted by user, shutting down...")
    except Exception as e:
        print(f"Error occurred: {e}")

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
```

## Internal Methods
The class contains several internal methods not intended for direct public use:
- `_get_live_chat_id()`: Retrieves the liveChatId for the specified video_id
- `_update_viewer_count()`: Updates viewer count from livestream statistics
- `_poll_chat_messages()`: Polls the YouTube API for new chat messages
- `_process_message(message)`: Processes a single chat message and handles triggers
- `_log_to_user_file(message)`: Appends a log entry to a user-specific file
- `_is_rate_limited(user_id)`: Checks if a user is rate limited
- `_update_trigger_time(user_id)`: Updates the last trigger time for a user
- `_handle_auth_error(error)`: Handles authentication errors with token rotation

## Dependencies
- googleapiclient.errors
- asyncio
- time
- datetime
- dotenv
- os
- logging
- modules.token_manager
- modules.banter_engine
- utils.throttling
- utils.oauth_manager 