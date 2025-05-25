# Token Manager Module Interface

## Overview
The Token Manager handles OAuth token rotation and health checking for YouTube API authentication. It integrates with existing OAuth manager and quota tracking systems.

## Exports
This module exports:
- `token_manager`: A singleton instance of the TokenManager class
- `TokenManager`: The class itself for advanced use cases

## Classes

### `TokenManager`
Manages OAuth token rotation and health checking for YouTube API interactions.

#### Properties
- `current_token_index`: The index of the currently active token set
- `health_check_interval`: Time in seconds before a token's health status is rechecked (default: 300)
- `max_retries`: Maximum number of retry attempts for token rotation (default: 3)
- `retry_delay`: Time in seconds between retry attempts (default: 5)
- `cooldown_period`: Time in seconds a failed token remains in cooldown (default: 1800)
- `parallel_check_timeout`: Maximum time in seconds for parallel token health checks (default: 10)

#### Methods

##### `check_token_health(token_index: Optional[int] = None) -> bool`
Validates the health of the specified token or current token.

**Parameters:**
- `token_index`: Optional index of token to check. If None, uses current token.

**Returns:**
- `bool`: True if token is healthy, False otherwise

**Behavior:**
- Checks if token is in cooldown period
- Uses cached health status if available and recent
- Performs actual API call to validate token health if needed
- Updates health cache with results

##### `async rotate_tokens() -> Optional[int]`
Rotates to the next available healthy token using parallel checking.

**Parameters:**
- None

**Returns:**
- `Optional[int]`: Index of the new token if successful, None if rotation failed

**Behavior:**
- Tries all tokens in parallel first for efficiency
- Falls back to sequential checking if parallel check fails
- Returns the index of the first healthy token found
- Returns None if all tokens are unhealthy or checks fail

## Usage Examples

### Basic Usage
```python
from modules.token_manager import token_manager

# Check health of current token
is_healthy = token_manager.check_token_health()

# Rotate to next healthy token
import asyncio
new_token_index = asyncio.run(token_manager.rotate_tokens())
if new_token_index is not None:
    print(f"Rotated to token set {new_token_index + 1}")
else:
    print("All tokens failed health check")
```

### Advanced Usage
```python
from modules.token_manager import TokenManager

# Create a custom token manager instance
custom_tm = TokenManager()
custom_tm.health_check_interval = 600  # 10 minutes
custom_tm.cooldown_period = 3600  # 1 hour
```

## Dependencies
- modules.youtube_auth
- utils.oauth_manager
- google.oauth2.credentials
- google.auth.transport.requests
- asyncio

## Error Handling
The module handles errors during token health checks and rotation, logging issues through the standard logging system. 