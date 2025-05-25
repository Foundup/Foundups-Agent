# Live Chat Processor Module Interface

## Overview
The Live Chat Processor module handles the processing of YouTube live chat messages, including detecting trigger sequences, managing cooldowns, and sending response messages. It integrates with the BanterEngine for generating themed responses and uses LiveChatPoller for retrieving messages.

## Exports
This module exports:
- `LiveChatProcessor`: The main class for processing live chat messages

## Classes

### `LiveChatProcessor`
Processes live chat messages and manages banter responses. Handles trigger detection, cooldown management, and message sending.

#### Constructor

##### `__init__(youtube_service, video_id: str, config: Optional[Dict[str, Any]] = None)`
Initializes a new LiveChatProcessor instance.

**Parameters:**
- `youtube_service`: Authenticated YouTube service instance (googleapiclient.discovery.Resource)
- `video_id`: ID of the livestream video
- `config`: Optional configuration dictionary with the following possible keys:
  - `memory_dir`: Directory for storing chat logs (default: "memory")
  - `AGENT_GREETING_MESSAGE`: Message to send when connecting to chat

**Behavior:**
- Creates necessary directories for storing chat logs
- Initializes BanterEngine for generating responses
- Sets up cooldown mechanism for rate-limiting responses
- Prepares LiveChatPoller for retrieving messages

#### Public Methods

##### `start_listening() -> None`
Starts the message polling and processing loop in a background thread.

**Parameters:**
- None

**Returns:**
- None

**Behavior:**
- Creates and starts a daemon thread for polling and processing messages
- Fetches the live chat ID for the specified video
- Sends a greeting message if configured
- Begins continuous polling until stopped

##### `stop_listening() -> None`
Stops the message polling and processing loop.

**Parameters:**
- None

**Returns:**
- None

**Behavior:**
- Sets the running flag to False
- Waits for the polling thread to finish (with timeout)

##### `send_chat_message(message_text: str) -> bool`
Sends a message to the live chat.

**Parameters:**
- `message_text`: The message text to send

**Returns:**
- `bool`: True if the message was sent successfully, False otherwise

**Behavior:**
- Truncates messages that exceed the maximum length (200 characters)
- Handles HTTP errors and possible chat ID invalidation
- Returns success/failure status

##### `process_message_batch(messages: list) -> int`
Processes a list of chat messages.

**Parameters:**
- `messages`: List of message objects to process

**Returns:**
- `int`: Number of messages processed

**Behavior:**
- Processes each message in the list
- Returns the count of processed messages

#### Internal Methods

The following methods are used internally and are not part of the public interface:

- `_get_new_cooldown() -> float`: Generates a new random cooldown time
- `_log_to_user_file(message: Dict[str, Any]) -> None`: Logs messages to user-specific files
- `_check_banter_trigger(message_text: str, author_name: str) -> None`: Checks for trigger sequences
- `process_single_message(message: Dict[str, Any]) -> None`: Processes one chat message
- `_poll_messages() -> None`: Main polling loop for retrieving messages

## Usage Example
```python
from modules.live_chat_processor import LiveChatProcessor
from modules.youtube_auth import get_authenticated_service

# Get authenticated YouTube service
youtube = get_authenticated_service()

# Configure the processor
video_id = "YOUR_YOUTUBE_VIDEO_ID"
config = {
    "memory_dir": "memory",
    "AGENT_GREETING_MESSAGE": "Hello, I'm the FoundUps Agent!"
}

# Create and start the processor
processor = LiveChatProcessor(youtube, video_id, config)
processor.start_listening()

# ... Your application logic here ...

# When done, stop the processor
processor.stop_listening()
```

## Dependencies
- modules.banter_engine.BanterEngine
- modules.live_chat_poller.LiveChatPoller
- googleapiclient.errors
- threading
- json
- time
- logging
- random
- os
- datetime 