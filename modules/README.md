# Foundups Agent Modules

This directory contains the core functional modules of the Foundups Agent. The structure and development process follow the **Windsurf Protocol (WSP)** to ensure modularity, testability, and atomic changes.

## Foundups Modular Framework

The system is designed like a **stack of expanding cubes**, where each layer (module or feature) is built, tested, and locked before the next one begins. This is enforced by a methodical dev-test flow driven by WSP prompts.

### Core Principles:

1.  **Windsurf Protocol (WSP):**
    *   Every change is defined through a **WSP prompt**.
    *   WSPs represent **atomic tasks**: one file, one function, one logical change, with no side effects outside the defined scope.
    *   Each WSP is like a clean commit, including its own specific testing logic (unit and integration).

2.  **Modular Architecture:**
    *   The Agent is composed of distinct, plug-and-play **modules**, each residing in its own subdirectory within `modules/`. Examples include:
        *   `banter_engine/` (Handles emoji-tone mapping and responses)
        *   `live_chat_listener/` (Monitors input streams)
        *   `oauth_manager/` (Manages credentials and authentication)
        *   `twin_trainer/` (Builds personality models)
        *   `stream_resolver/`
        *   `emoji_mapper/`
        *   *(add other modules as they are created)*
    *   **Module Structure:** Each module directory (`modules/<module_name>/`) should contain:
        *   `src/`: Main source code for the module.
        *   `tests/`: Unit and integration tests specific to the module.
        *   `__init__.py`: Makes the directory a Python package and exposes necessary components.
        *   *(Optionally)* `config/`, `handlers/`, `assets/`, etc., as needed by the module.
    *   **Lifecycle:** Modules progress through phases: POC (`0.0.x`) → Prototype (`0.1.x – 0.9.x`) → MVP/Production (`1.x.x+`).

3.  **Strict Change Logs (`MODLOG`):**
    *   All significant changes, especially those corresponding to WSPs, should be tracked in a `MODLOG` file (likely at the project root).
    *   Use tags like `[+WSP]`, `[+todo]`, or `[+UPDATES]` for clarity.

4.  **Clean Reference Baseline:**
    *   All changes and behaviors are validated against a pristine baseline branch (e.g., `Foundups-Agent-CleanX`). This prevents regression and unscoped changes.

5.  **Testing by Phase:**
    *   Each WSP must complete its cycle: code update → unit test → integration/live test → lock-in.
    *   Work does not proceed to the next WSP or phase until all tests pass and the scope is verified against the baseline.

### Why This Structure?

This approach ensures:
*   **Decoupling:** Modules operate independently, minimizing unforeseen interactions.
*   **Testability:** Atomic units are easier to test thoroughly.
*   **Traceability:** WSPs and MODLOG make changes easy to follow.
*   **Scalability:** The system scales horizontally like snap-together blocks, avoiding central failure points.
*   **Alignment:** Conforms to the principles of modular AI alignment.

---

*This document reflects the standard structure and protocol for developing modules within the Foundups Agent.*

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

