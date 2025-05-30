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
    *   The Agent is composed of distinct, plug-and-play **modules**, organized in a hierarchical Enterprise Domain structure within `modules/`. The structure follows the "cube-based philosophy" with four levels:
        *   **Enterprise Domains (Level 1):** `communication/`, `ai_intelligence/`, `platform_integration/`, `infrastructure/`
        *   **Feature Groups (Level 2):** `livechat/`, `banter_engine/`, `oauth_management/`, `token_manager/`, etc.
        *   **Modules (Level 3):** Individual module directories containing `src/`, `tests/`, etc.
        *   **Code Components (Level 4):** Functions, classes within module source files
    *   Examples of the new structure:
        *   `communication/livechat/livechat/` (Main chat interaction and management)
        *   `communication/livechat/live_chat_processor/` (Processes incoming chat messages)
        *   `communication/livechat/live_chat_poller/` (Polls for new chat messages)
        *   `ai_intelligence/banter_engine/banter_engine/` (Handles emoji-tone mapping and responses)
        *   `infrastructure/oauth_management/oauth_management/` (Manages OAuth credentials and authentication)
        *   `platform_integration/stream_resolver/stream_resolver/` (Resolves stream IDs and metadata)
        *   `infrastructure/token_manager/token_manager/` (Handles token authentication and refresh)
    *   **Module Structure:** Each module directory (`modules/<domain>/<feature_group>/<module_name>/`) should contain:
        *   `src/`: Main source code for the module.
        *   `tests/`: Unit and integration tests specific to the module.
        *   `__init__.py`: Makes the directory a Python package and exposes necessary components.
        *   `README.md`: Documentation specific to the module.
        *   `INTERFACE.md`: Defines the module's public interface (WSP 11).
        *   `requirements.txt`: Lists module-specific dependencies (WSP 12).
        *   *(Optionally)* `docs/`, `memory/`, `assets/`, etc., as needed by the module.
    *   **Lifecycle:** Modules progress through phases: POC (`0.0.x`) → Prototype (`0.1.x – 0.9.x`) → MVP/Production (`1.x.x+`).

3.  **Strict Change Logs (`MODLOG`):**
    *   All significant changes, especially those corresponding to WSPs, should be tracked in a `MODLOG` file (typically at the project root).
    *   Use tags like `[+WSP]`, `[+todo]`, or `[+UPDATES]` for clarity.

4.  **Clean Reference Baseline:**
    *   All changes and behaviors are validated against a pristine baseline branch (e.g., `Foundups-Agent-CleanX`). This prevents regression and unscoped changes.

5.  **Testing by Phase:**
    *   Each WSP must complete its cycle: code update → unit test → integration/live test → lock-in.
    *   Work does not proceed to the next WSP or phase until all tests pass and the scope is verified against the baseline.
    *   **Test Organization:** Each module's tests are contained in its own `tests/` directory with a `README.md` describing the available tests.

### Recent Refactoring

The codebase has undergone significant modular refactoring, following WSP 1 guidelines:

1. **Test Structure Reorganization:**
   * All tests have been moved from the root `tests/` directory (now `tests_archived/`) to their respective module directories (`modules/<module_name>/tests/`).
   * Each module's test directory includes a README.md documenting the available tests.

2. **Test File Refactoring:**
   * Large test files like `test_livechat.py` have been refactored into smaller, focused test files:
     * `test_livechat_lifecycle.py` - Tests for initialization and shutdown
     * `test_livechat_message_processing.py` - Tests for message handling
     * `test_livechat_emoji_triggers.py` - Tests for emoji detection and reactions
     * `test_livechat_rate_limiting.py` - Tests for rate limit handling
     * And several other focused test files
   * This improves maintainability and alleviates issues with test runtime and coverage reporting.

3. **FMAS Compliance:**
   * All modules now follow the structure required by the Foundups Modular Audit System (FMAS).
   * Standard module interfaces are defined in INTERFACE.md files.
   * Module dependencies are explicitly declared in requirements.txt files.

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

### `oauth_management`
**CANONICAL AUTHENTICATION SYSTEM** - Handles OAuth 2.0 authentication with Google/YouTube APIs.

**Key Features:**
- Multi-credential OAuth 2.0 authentication (4 credential sets)
- Intelligent credential rotation and fallback
- Quota management with cooldown tracking
- Automatic token refresh and storage
- Environment-based credential forcing
- Comprehensive error handling and logging

**Usage Example:**
```python
from modules.infrastructure.oauth_management.oauth_management import get_authenticated_service_with_fallback

# Get authenticated service with automatic fallback
result = get_authenticated_service_with_fallback()
if result:
    service, credentials, credential_set = result
    print(f"✅ Authenticated with {credential_set}")
```

**Migration Note:** This module replaces the legacy `utils/oauth_manager.py` and duplicate `youtube_auth` module. A compatibility shim exists for backward compatibility.

### `livechat`
Manages connection, listening, logging, and sending messages to a YouTube Live Chat.

**Key Features:**
- Live chat connection and polling
- Message processing and logging
- User-specific message tracking
- Rate-limit aware message sending
- Error handling with exponential backoff

**Usage Example:**
```python
from modules.communication.livechat.livechat import LiveChatListener

# Initialize and start the chat listener
listener = LiveChatListener(youtube_service, video_id)
listener.start_listening()
```

### `stream_resolver`
Handles YouTube stream identification and metadata management.

**Key Features:**
- Stream ID validation and resolution
- Metadata retrieval
- Stream status monitoring
- Error handling for invalid or ended streams

**Usage Example:**
```python
from modules.platform_integration.stream_resolver.stream_resolver import get_stream_info

# Get information about a livestream
stream_info = get_stream_info(youtube_service, video_id)
```

## Dependencies

Each module has its own `requirements.txt` file listing its specific dependencies. Common dependencies across modules include:
- `google-auth-oauthlib`
- `google-api-python-client`
- `python-dotenv`

## Configuration

Modules read configuration from environment variables defined in `.env`:
- `GOOGLE_CLIENT_SECRETS_FILE_1` through `GOOGLE_CLIENT_SECRETS_FILE_4`: OAuth client secrets (4 sets)
- `OAUTH_TOKEN_FILE_1` through `OAUTH_TOKEN_FILE_4`: OAuth token files (4 sets)
- `FORCE_CREDENTIAL_SET`: Force specific credential set (1-4)
- `YOUTUBE_VIDEO_ID`: Target livestream ID
- `LOG_LEVEL`: Logging verbosity
- `AGENT_GREETING_MESSAGE`: Custom greeting on connection

## Error Handling

All modules implement comprehensive error handling:
- API quota management with automatic rotation
- Network error recovery
- Token refresh handling
- Rate limiting compliance
- Cooldown management for quota exceeded scenarios

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
- The system supports 4 credential sets for quota distribution

## Future Enhancements

- AI message composition integration
- Blockchain reward integration
- Enhanced user tracking
- Command system implementation

See `ModLog.md` in the root directory for version history and changes.

