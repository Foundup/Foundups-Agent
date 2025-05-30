# OAuth Management Module Interface

## Overview
The OAuth Management module provides comprehensive OAuth 2.0 authentication and quota management for the FoundUps Agent. It handles multiple credential sets with intelligent rotation, cooldown tracking, and fallback capabilities.

## Exports
This module exports:
- `get_authenticated_service`: Function to authenticate with a specific credential set
- `get_authenticated_service_with_fallback`: Function with automatic credential rotation
- `QuotaManager`: Class for quota tracking and cooldown management
- `quota_manager`: Pre-initialized QuotaManager instance

## Functions

### `get_authenticated_service(credential_set_index: int = 0) -> Optional[Tuple[Any, Credentials]]`
Authenticates with YouTube API using a specific credential set.

**Parameters:**
- `credential_set_index` (int): Index of the credential set to use (0-3, default: 0)

**Returns:**
- `Tuple[googleapiclient.discovery.Resource, google.oauth2.credentials.Credentials]`: YouTube API service object and credentials if successful
- `None`: If authentication fails

**Behavior:**
- Validates credential set index (0-3 for 4 credential sets)
- Loads existing credentials from token files if available
- Refreshes credentials if expired
- Initiates OAuth flow if no valid credentials found
- Saves new or refreshed credentials to token file

### `get_authenticated_service_with_fallback() -> Optional[Tuple[Any, Credentials, str]]`
Attempts authentication with multiple credential sets using intelligent rotation.

**Parameters:**
- None

**Returns:**
- `Tuple[googleapiclient.discovery.Resource, google.oauth2.credentials.Credentials, str]`: Service, credentials, and credential set name if successful
- `None`: If all credential sets fail

**Behavior:**
- Checks for forced credential set via `FORCE_CREDENTIAL_SET` environment variable
- Categorizes credential sets by availability (available vs. cooldown)
- Tries available sets first, then emergency fallback to cooldown sets
- Handles quota exceeded errors by placing sets in cooldown
- Provides comprehensive logging of rotation process

## Classes

### `QuotaManager`
Manages API quota tracking and credential set cooldowns.

#### Methods:
- `record_usage(credential_type: str, is_api_key: bool = False)`: Record API usage
- `get_usage_count(credential_type: str, is_api_key: bool = False) -> Tuple[int, int]`: Get current usage counts
- `is_quota_exceeded(credential_type: str, is_api_key: bool = False) -> bool`: Check if quota exceeded
- `start_cooldown(credential_set: str)`: Start cooldown period for a credential set
- `is_in_cooldown(credential_set: str) -> bool`: Check if credential set is in cooldown

## Environment Variables
The module requires the following environment variables:

### Credential Files (4 sets supported):
- `GOOGLE_CLIENT_SECRETS_FILE_1` through `GOOGLE_CLIENT_SECRETS_FILE_4`: Paths to client secrets files
- `OAUTH_TOKEN_FILE_1` through `OAUTH_TOKEN_FILE_4`: Paths to token files

### Optional Configuration:
- `FORCE_CREDENTIAL_SET`: Force specific credential set (1-4)
- `YOUTUBE_SCOPES`: Space-separated OAuth scopes (defaults to YouTube readonly and force-ssl)

## File Structure
The module expects the following credential files in the `credentials/` directory:
- `client_secret.json`, `client_secret2.json`, `client_secret3.json`, `client_secret4.json`
- `oauth_token.json`, `oauth_token2.json`, `oauth_token3.json`, `oauth_token4.json`

## Usage Examples

### Basic Authentication
```python
from modules.infrastructure.oauth_management.oauth_management import get_authenticated_service

# Authenticate with first credential set
result = get_authenticated_service(0)
if result:
    service, credentials = result
    # Use service for YouTube API calls
```

### Authentication with Fallback
```python
from modules.infrastructure.oauth_management.oauth_management import get_authenticated_service_with_fallback

# Try all credential sets with intelligent rotation
result = get_authenticated_service_with_fallback()
if result:
    service, credentials, credential_set = result
    print(f"Authenticated with {credential_set}")
```

### Quota Management
```python
from modules.infrastructure.oauth_management.oauth_management import quota_manager

# Check if credential set is in cooldown
if quota_manager.is_in_cooldown("set_1"):
    print("Credential set 1 is in cooldown")

# Manually start cooldown
quota_manager.start_cooldown("set_2")
```

## Error Handling
- **Invalid credential index**: Returns None with error log
- **Missing credential files**: Returns None with error log  
- **Quota exceeded**: Automatically rotates to next credential set
- **OAuth flow failure**: Continues to next credential set in fallback mode
- **Network errors**: Logged and handled gracefully

## Migration Notes
This module replaces the legacy `utils/oauth_manager.py`. A compatibility shim exists at the old location that imports from this module and issues deprecation warnings.

## Dependencies
- `google-auth`
- `google-auth-oauthlib` 
- `google-api-python-client`
- `python-dotenv` 