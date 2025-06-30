# YouTube Authentication Module Interface

## Overview
The YouTube Authentication module handles OAuth 2.0 authentication with the YouTube API, managing credential loading, refreshing, and the initial authorization flow. It implements multi-client OAuth fallback for quota management.

## Exports
This module exports:
- `get_authenticated_service`: Function to authenticate and obtain a YouTube API service object

## Functions

### `get_authenticated_service() -> googleapiclient.discovery.Resource`
Authenticates the user with YouTube API using OAuth 2.0 and returns a YouTube API service object.

**Parameters:**
- None

**Returns:**
- `googleapiclient.discovery.Resource`: A YouTube API service object that can be used to make API calls

**Behavior:**
- Sequentially tries up to 4 credential sets defined in environment variables
- Loads existing credentials from token files if available
- Refreshes credentials if expired
- Initiates a new OAuth flow if no valid credentials are found
- Saves new or refreshed credentials to the appropriate token file
- Falls back to the next credential set if authentication fails or quota is exceeded
- Raises an exception if all credential sets fail

## Environment Variables
The module requires the following environment variables to be set:

- `YOUTUBE_SCOPES`: Space-separated list of OAuth scopes required
- `GOOGLE_CLIENT_SECRETS_FILE_1` through `GOOGLE_CLIENT_SECRETS_FILE_4`: Paths to client secrets files
- `OAUTH_TOKEN_FILE_1` through `OAUTH_TOKEN_FILE_4`: Paths to token files for credential storage

## Usage Example
```python
from modules.youtube_auth import get_authenticated_service

try:
    # Get authenticated YouTube API service
    youtube = get_authenticated_service()
    
    # Use the service to make API calls
    response = youtube.channels().list(
        part='snippet',
        mine=True
    ).execute()
    
    channel_title = response['items'][0]['snippet']['title']
    print(f"Authenticated as channel: {channel_title}")
    
except Exception as e:
    print(f"Authentication failed: {e}")
```

## Dependencies
- google.oauth2.credentials
- google_auth_oauthlib.flow
- googleapiclient.discovery
- google.auth.transport.requests
- dotenv

## Error Handling
- `ValueError`: Raised if required environment variables are missing
- `Exception`: Raised if all credential sets fail to authenticate
- HTTP errors from the YouTube API are logged but handled internally during authentication

## Internal Functions
The module contains internal helper functions not part of the public interface:
- `get_credentials_for_index(index)`: Helper function to retrieve credential paths for a specific index 