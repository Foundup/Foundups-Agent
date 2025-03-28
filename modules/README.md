# Core Agent Modules

This directory contains the primary functional modules for the FoundUps Agent.

## Module Overview

### `youtube_auth.py`
Handles authentication with Google/YouTube via OAuth2.

**Key Features:**
- OAuth2 flow management for YouTube API access
- Token storage and refresh handling
- Secure credential management
- Service object creation for API interactions

**Usage Example:**
```python
from modules.youtube_auth import get_authenticated_service

# Get an authenticated YouTube service object
youtube = get_authenticated_service()
```

### `livechat.py`
Manages connection, listening, logging, and sending messages to a YouTube Live Chat.

**Key Features:**
- Live chat connection and polling
- Message processing and logging
- User-specific message tracking
- Rate-limit aware message sending
- Error handling with exponential backoff

**Usage Example:**
```python
from modules.livechat import LiveChatListener

# Initialize and start the chat listener
listener = LiveChatListener(youtube_service, video_id)
listener.start_listening()
```

### `stream_resolver.py`
Handles YouTube stream identification and metadata management.

**Key Features:**
- Stream ID validation and resolution
- Metadata retrieval
- Stream status monitoring
- Error handling for invalid or ended streams

**Usage Example:**
```python
from modules.stream_resolver import get_stream_info

# Get information about a livestream
stream_info = get_stream_info(youtube_service, video_id)
```

## Dependencies

These modules depend on:
- `google-auth-oauthlib`
- `google-api-python-client`
- `python-dotenv`

All dependencies are listed in the root `requirements.txt` file.

## Configuration

Modules read configuration from environment variables defined in `.env`:
- `GOOGLE_CLIENT_SECRETS_FILE`: Path to OAuth client secrets
- `YOUTUBE_VIDEO_ID`: Target livestream ID
- `LOG_LEVEL`: Logging verbosity
- `AGENT_GREETING_MESSAGE`: Custom greeting on connection

## Error Handling

All modules implement comprehensive error handling:
- API quota management
- Network error recovery
- Token refresh handling
- Rate limiting compliance

## Logging

Modules use the centralized logging configuration from `utils.logging_config`:
```python
import logging
logger = logging.getLogger(__name__)
```

## Security Notes

- Never commit OAuth tokens or client secrets
- Use environment variables for sensitive data
- Mount credential files via Docker volumes
- Follow YouTube API usage guidelines

## Future Enhancements

- AI message composition integration
- Blockchain reward integration
- Enhanced user tracking
- Command system implementation

See `ModLog.md` in the root directory for version history and changes.

