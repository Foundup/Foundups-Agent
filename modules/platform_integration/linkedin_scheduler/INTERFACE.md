# INTERFACE (WSP 11)

## Module: LinkedIn Scheduler
**Domain**: platform_integration  
**Classification**: Social Media Scheduling Service  
**WSP Compliance**: WSP 42 (Platform Integration)

## Public API

### Core Classes
- `LinkedInScheduler`: Main scheduling service with LinkedIn API v2 integration
- `LinkedInAPIError`: Custom exception for API-related errors

### Primary Methods

#### OAuth Authentication
```python
def get_oauth_url(redirect_uri: str, state: Optional[str] = None) -> str
def exchange_code_for_token(code: str, redirect_uri: str) -> Dict[str, Any]
```

#### Content Posting
```python
def create_ugc_post(profile_id: str, content: str, visibility: str = "PUBLIC") -> Dict[str, Any]
def create_text_post(profile_id: str, text: str, visibility: str = "PUBLIC") -> Dict[str, Any]
```

#### Profile Management
```python
def get_profile_info(profile_id: str) -> Dict[str, Any]
def set_access_token(profile_id: str, access_token: str) -> None
```

## Parameters

### LinkedInScheduler.__init__()
- `client_id: Optional[str]` - LinkedIn application client ID (or from LINKEDIN_CLIENT_ID env var)
- `client_secret: Optional[str]` - LinkedIn application client secret (or from LINKEDIN_CLIENT_SECRET env var)

### get_oauth_url()
- `redirect_uri: str` - Callback URL after authorization (required)
- `state: Optional[str]` - Optional state parameter for security

### create_ugc_post()
- `profile_id: str` - LinkedIn profile/page ID (required)
- `content: str` - Post content text (required)
- `visibility: str` - Post visibility ("PUBLIC", "CONNECTIONS", default: "PUBLIC")

## Returns

### get_oauth_url()
- `str` - Authorization URL for user to visit for OAuth flow

### exchange_code_for_token()
- `Dict[str, Any]` - Token response with access_token, expires_in, scope

### create_ugc_post()
- `Dict[str, Any]` - LinkedIn API response with post ID and creation details

### get_profile_info()
- `Dict[str, Any]` - Profile information including name, title, company

## Errors

### LinkedInAPIError
- Raised for all LinkedIn API-related failures
- Includes API error codes and messages
- Provides detailed error context

### Common Error Scenarios
- Missing or invalid credentials
- API rate limit exceeded (150/day per member, 100k/day per app)
- Invalid profile ID or access token
- Network connectivity issues
- Malformed post content

## Examples

### OAuth Flow Setup
```python
from modules.platform_integration.linkedin_scheduler.src.linkedin_scheduler import LinkedInScheduler

# Initialize scheduler
scheduler = LinkedInScheduler(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Generate OAuth URL
auth_url = scheduler.get_oauth_url(
    redirect_uri="http://localhost:8080/callback",
    state="random_state_string"
)
print(f"Visit: {auth_url}")
```

### Token Exchange
```python
# Exchange authorization code for access token
token_data = scheduler.exchange_code_for_token(
    code="authorization_code_from_callback",
    redirect_uri="http://localhost:8080/callback"
)

# Store access token
scheduler.set_access_token("profile_id", token_data["access_token"])
```

### Content Posting
```python
# Create a LinkedIn post
response = scheduler.create_text_post(
    profile_id="your_profile_id",
    text="[ROCKET] Exciting update from our development team! #LinkedIn #API",
    visibility="PUBLIC"
)

print(f"Post created: {response['id']}")
```

### Error Handling
```python
try:
    post = scheduler.create_ugc_post(
        profile_id="invalid_id",
        content="Test post"
    )
except LinkedInAPIError as e:
    print(f"LinkedIn API error: {e}")
```
