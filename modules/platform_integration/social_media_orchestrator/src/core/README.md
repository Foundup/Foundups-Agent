# Social Media Orchestrator Core Components

## Overview

This `core` package contains modular, single-responsibility components extracted from the original `simple_posting_orchestrator.py` file (996 lines) to improve maintainability, testability, and clarity.

## Refactoring Rationale

The original `simple_posting_orchestrator.py` had grown to nearly 1000 lines and was handling multiple responsibilities:
- Duplicate post prevention
- History management (JSON and database)
- Live stream status verification
- Channel configuration management
- Platform-specific posting logic
- Browser management

This violated the Single Responsibility Principle and made the code difficult to maintain and debug.

## New Architecture

### Core Components

#### 1. **DuplicatePreventionManager** (`duplicate_prevention_manager.py`)
- **Purpose**: Manages duplicate post detection and history tracking
- **Responsibilities**:
  - Check if videos have been posted to platforms
  - Maintain in-memory cache of posted content
  - Persist posting history to SQLite database
  - Backup to JSON for resilience
  - Enhanced logging for duplicate prevention visibility
- **Key Methods**:
  - `check_if_already_posted()` - Main duplicate check with detailed logging
  - `mark_as_posted()` - Record successful posts
  - `get_posting_stats()` - Analytics on posting history

#### 2. **LiveStatusVerifier** (`live_status_verifier.py`)
- **Purpose**: Verify if YouTube streams are actually live
- **Responsibilities**:
  - Check stream status via YouTube API
  - Cache live status to reduce API calls
  - Fallback verification methods
  - Manual verification prompts
- **Key Methods**:
  - `verify_live_status()` - Main verification method
  - `verify_live_status_manually()` - User prompt fallback
  - `clear_cache()` - Cache management

#### 3. **ChannelConfigurationManager** (`channel_configuration_manager.py`)
- **Purpose**: Manage channel configurations and platform account mappings
- **Responsibilities**:
  - Load and save channel configurations
  - Map YouTube channels to LinkedIn pages
  - Map LinkedIn pages to X/Twitter accounts
  - Determine which X account to use for posts
- **Key Methods**:
  - `get_channel_config()` - Get configuration for a channel
  - `get_x_account_for_linkedin_page()` - Platform account mapping
  - `should_use_foundups_x()` - Account selection logic

## Usage Example

```python
from modules.platform_integration.social_media_orchestrator.src.core import (
    DuplicatePreventionManager,
    LiveStatusVerifier,
    ChannelConfigurationManager
)

# Initialize managers
duplicate_manager = DuplicatePreventionManager()
status_verifier = LiveStatusVerifier()
config_manager = ChannelConfigurationManager()

# Check if video was already posted
result = duplicate_manager.check_if_already_posted("VIDEO_ID_123")
if not result['already_posted']:
    # Verify stream is live
    if status_verifier.verify_live_status("VIDEO_ID_123"):
        # Get channel configuration
        config = config_manager.get_channel_config("@UnDaoDu")
        # Proceed with posting...
```

## Benefits of Refactoring

1. **Separation of Concerns**: Each module has a single, clear responsibility
2. **Testability**: Easier to write unit tests for focused components
3. **Maintainability**: Changes to one area don't affect others
4. **Reusability**: Components can be used independently
5. **Clarity**: Code is easier to understand and navigate
6. **Debugging**: Issues are easier to isolate and fix

## Migration Path

The original `simple_posting_orchestrator.py` can be gradually refactored to use these core components:

1. Import the core components
2. Replace internal methods with calls to managers
3. Remove duplicate code
4. Simplify the orchestrator to focus only on coordination

## Next Steps

1. Create `PlatformPostingService` for platform-specific posting logic
2. Refactor `SimplePostingOrchestrator` to use these components
3. Add comprehensive unit tests for each component
4. Consider further breaking down if components grow large

## File Size Comparison

- **Before**: `simple_posting_orchestrator.py` - 996 lines
- **After**:
  - `duplicate_prevention_manager.py` - 291 lines
  - `live_status_verifier.py` - 232 lines
  - `channel_configuration_manager.py` - 283 lines
  - **Total**: 806 lines (better organized and maintainable)

## Dependencies

- Standard library: `os`, `json`, `sqlite3`, `logging`, `datetime`, `enum`
- Internal: YouTube auth module, stream resolver (optional)