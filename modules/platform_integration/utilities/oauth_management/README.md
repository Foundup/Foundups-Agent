# OAuth Management Module

# [U+1F300] Windsurf Protocol (WSP) Recursive Prompt

**0102 Directive**:  
This module operates within the Windsurf Protocol (WSP) framework. Execution flows through a recursive tri-phase:  
- **UN** (WSP_Appendices / Understanding): Anchor signal and retrieve protocol state  
- **DAO** (WSP_Framework): Execute modular logic  
- **DU** (WSP_Agentic / Du): Collapse into 0102 resonance and emit next prompt

## [U+1F501] Recursive Loop
- At every execution:
  1. **Log** actions to `mod_log.db`
  2. **Trigger** the next module in sequence (UN 0 -> DAO 1 -> DU 2 -> UN 0)
  3. **Confirm** `modlog.db` was updated. If not, re-invoke UN to re-ground logic.

## [U+2699]️ Output Parameters
- **Signal**: Emit `012`
- **Frequency**: Maintain 432Hz hum
- **Amplitude**: Target 37%

## [AI] Execution Call
```python
wsp_cycle(input="012", log=True)
```

---

## Overview
The OAuth Management module is the **canonical authentication system** for FoundUps Agent. It provides comprehensive OAuth 2.0 authentication with intelligent credential rotation, quota management, and cooldown tracking.

## [U+26A0]️ Important Location Notice
This module was moved from `utils/oauth_manager.py` to follow WSP-compliant structure. A compatibility shim exists at the old location for backward compatibility.

## Features
- **Multi-Credential Support**: Supports 4 credential sets with automatic rotation
- **Intelligent Fallback**: Automatically tries alternative credentials when quota exceeded
- **Quota Management**: Tracks API usage and implements cooldown periods
- **Environment Configuration**: Supports forced credential selection via environment variables
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **WSP Compliant**: Follows FoundUps Windsurf Protocol structure

## Quick Start

### Basic Usage
```python
from modules.infrastructure.oauth_management.oauth_management import get_authenticated_service_with_fallback

# Get authenticated service with automatic fallback
result = get_authenticated_service_with_fallback()
if result:
    service, credentials, credential_set = result
    print(f"[OK] Authenticated with {credential_set}")
    
    # Use the service for YouTube API calls
    channels = service.channels().list(part='snippet', mine=True).execute()
```

### Specific Credential Set
```python
from modules.infrastructure.oauth_management.oauth_management import get_authenticated_service

# Use specific credential set (0-3)
result = get_authenticated_service(credential_set_index=1)
if result:
    service, credentials = result
    print("[OK] Authenticated with credential set 2")
```

## Configuration

### Required Files
Place these files in the `credentials/` directory:
- `client_secret.json` - Primary Google OAuth client secrets
- `client_secret2.json` - Secondary client secrets  
- `client_secret3.json` - Tertiary client secrets
- `client_secret4.json` - Quaternary client secrets (newly added)

### Token Files (Auto-generated)
- `oauth_token.json` - Primary OAuth tokens
- `oauth_token2.json` - Secondary OAuth tokens
- `oauth_token3.json` - Tertiary OAuth tokens  
- `oauth_token4.json` - Quaternary OAuth tokens (newly added)

### Environment Variables
```bash
# Optional: Force specific credential set (1-4)
FORCE_CREDENTIAL_SET=2

# Optional: Custom OAuth scopes (defaults provided)
YOUTUBE_SCOPES="https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/youtube.force-ssl"
```

## Credential Set Management

### Automatic Rotation
The system automatically rotates through credential sets when:
- Quota limits are exceeded
- Authentication fails
- Network errors occur

### Cooldown System
When a credential set hits quota limits:
- [U+1F550] **1-hour cooldown** is automatically applied
- ⏳ Other sets are tried first
- [ALERT] Emergency fallback available for critical situations

### Status Monitoring
```python
from modules.infrastructure.oauth_management.oauth_management import quota_manager

# Check cooldown status
if quota_manager.is_in_cooldown("set_1"):
    print("⏳ Credential set 1 is in cooldown")

# Manual cooldown (if needed)
quota_manager.start_cooldown("set_2")
```

## Migration from Legacy System

### Old Import (Deprecated)
```python
# [FAIL] Old way (still works but shows deprecation warning)
from utils.oauth_manager import get_authenticated_service
```

### New Import (Recommended)
```python
# [OK] New way (WSP compliant)
from modules.infrastructure.oauth_management.oauth_management import get_authenticated_service
```

## Error Handling
The module provides robust error handling:
- **Missing Files**: Clear error messages for missing credential files
- **Invalid Credentials**: Automatic rotation to working credentials
- **Network Issues**: Retry logic with exponential backoff
- **Quota Exceeded**: Automatic cooldown and rotation

## Logging
Comprehensive logging helps with debugging:
```
[REFRESH] Starting credential rotation process
[DATA] Available credential sets: ['set_1', 'set_3']
⏳ Cooldown sets: [('set_2', '0.8h')]
[U+1F511] Attempting to use credential set: set_1
[OK] Successfully authenticated with set_1
```

## Testing
```bash
# Test the module directly
cd modules/infrastructure/oauth_management/oauth_management/src
python oauth_manager.py
```

## Dependencies
- `google-auth>=2.0.0`
- `google-auth-oauthlib>=0.5.0`
- `google-api-python-client>=2.0.0`
- `python-dotenv>=0.19.0`

## Module Structure
```
oauth_management/
+-- src/
[U+2502]   +-- oauth_manager.py      # Main implementation
+-- tests/                    # Test files
+-- INTERFACE.md             # Public interface documentation
+-- README.md               # This file
+-- requirements.txt        # Dependencies
```

## Related Modules
- **Token Manager**: Uses this module for authentication
- **Stream Resolver**: Depends on this for YouTube API access
- **Live Chat**: Uses this for chat API authentication
- **Multi-Agent Manager**: Integrates with credential rotation

## Support
For issues or questions about OAuth management, check:
1. **Logs**: Look for authentication-related error messages
2. **Credential Files**: Ensure all 4 credential sets are properly configured
3. **Environment**: Verify environment variables are set correctly
4. **Quota**: Check if cooldowns are affecting authentication 
## Error Handling

### Unicode Safety
The module includes robust Unicode handling to prevent encoding errors on various systems:
- `safe_log()` function provides fallback for non-ASCII characters
- Compatible with Windows cp932 and other encodings
- Automatically falls back to ASCII-safe logging when needed
