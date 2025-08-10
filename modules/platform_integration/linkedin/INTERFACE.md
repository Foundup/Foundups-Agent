# INTERFACE (WSP 11)

## Module: LinkedIn Unified Platform Integration
**Domain**: platform_integration  
**Classification**: Professional Social Media Platform Integration  
**WSP Compliance**: WSP 3, WSP 11, WSP 22, WSP 49, WSP 42

## Public API

### Core Classes
- `LinkedInManager`: Main unified LinkedIn management service
- `LinkedInAuth`: Centralized OAuth and authentication management
- `LinkedInContentManager`: Content creation and formatting for LinkedIn
- `LinkedInScheduler`: Advanced scheduling with LinkedIn optimization
- `LinkedInProxy`: Direct API proxy for LinkedIn operations
- `LinkedInEngagement`: Professional networking and engagement automation

### Primary Methods

#### Authentication & Setup
```python
async def authenticate(credentials: Dict[str, Any]) -> bool
def get_oauth_url(redirect_uri: str, scope: str = "w_member_social") -> str
async def exchange_code_for_token(code: str, redirect_uri: str) -> Dict[str, Any]
```

#### Content Management
```python
async def create_post(content: str, options: Dict[str, Any] = None) -> str
async def create_company_post(company_id: str, content: str, options: Dict[str, Any] = None) -> str
async def schedule_post(content: str, schedule_time: datetime, options: Dict[str, Any] = None) -> str
def format_content_for_linkedin(content: str, options: Dict[str, Any] = None) -> str
```

#### Professional Networking
```python
async def get_profile_info() -> Dict[str, Any]
async def get_connections(limit: int = 50) -> List[Dict[str, Any]]
async def send_connection_request(profile_id: str, message: str = None) -> bool
```

#### Analytics & Insights
```python
async def get_post_analytics(post_id: str) -> Dict[str, Any]
async def get_engagement_metrics(time_period: str = "30d") -> Dict[str, Any]
```

### Unified Service Interface

#### LinkedInManager.__init__()
- `config: Optional[Dict[str, Any]]` - Configuration for all LinkedIn services
- `auth_credentials: Optional[Dict[str, Any]]` - Authentication credentials
- `logger: Optional[logging.Logger]` - Custom logger instance

#### authenticate()
- `credentials: Dict[str, Any]` - LinkedIn OAuth credentials
  - `client_id: str` - LinkedIn application client ID
  - `client_secret: str` - LinkedIn application client secret
  - `access_token: str` - LinkedIn access token (optional, for existing auth)
  - `refresh_token: str` - LinkedIn refresh token (optional)

#### create_post()
- `content: str` - Post content text (required)
- `options: Dict[str, Any]` - Posting options
  - `visibility: str` - Post visibility ("PUBLIC", "CONNECTIONS", default: "PUBLIC")
  - `hashtags: List[str]` - Hashtags to include
  - `mentions: List[str]` - User mentions to include
  - `media: List[str]` - Media URLs or file paths
  - `call_to_action: str` - Call-to-action text

## Returns

### authenticate()
- `bool` - True if authentication successful, False otherwise

### create_post()
- `str` - LinkedIn post ID if successful

### schedule_post()
- `str` - Schedule ID for tracking the scheduled post

### get_profile_info()
- `Dict[str, Any]` - Complete profile information
```python
{
    'id': 'profile_id',
    'firstName': {'localized': {'en_US': 'First'}},
    'lastName': {'localized': {'en_US': 'Last'}},
    'headline': {'localized': {'en_US': 'Professional Title'}},
    'industry': 'Technology',
    'location': {'name': 'Location'},
    'connections': 500,
    'profilePicture': 'url_to_picture'
}
```

### get_post_analytics()
- `Dict[str, Any]` - Post engagement analytics
```python
{
    'views': 1250,
    'likes': 45,
    'comments': 12,
    'shares': 8,
    'clicks': 67,
    'engagement_rate': 0.084,
    'reach': 980
}
```

## Errors

### LinkedInAuthError
- Raised for authentication-related failures
- Includes OAuth error details and remediation steps

### LinkedInAPIError
- Raised for LinkedIn API-related failures
- Includes API error codes and rate limit information

### LinkedInContentError
- Raised for content validation and formatting errors
- Provides content optimization suggestions

### Common Error Scenarios
- Invalid or expired credentials
- Rate limit exceeded (varies by endpoint)
- Content policy violations
- Network connectivity issues
- Invalid profile or company IDs

## Examples

### Basic Setup and Authentication
```python
from modules.platform_integration.linkedin import LinkedInManager

# Initialize LinkedIn manager
linkedin = LinkedInManager({
    'logging_level': 'INFO',
    'enable_scheduling': True,
    'content_optimization': True
})

# OAuth flow
auth_url = linkedin.get_oauth_url(
    redirect_uri="http://localhost:8080/callback",
    scope="w_member_social r_liteprofile r_emailaddress"
)
print(f"Visit: {auth_url}")

# After user authorization, exchange code for token
token_data = await linkedin.exchange_code_for_token(
    code="authorization_code_from_callback",
    redirect_uri="http://localhost:8080/callback"
)

# Authenticate with token
await linkedin.authenticate(token_data)
```

### Professional Content Posting
```python
# Create a professional LinkedIn post
post_id = await linkedin.create_post(
    content="""Excited to share our latest development milestone! 🚀

Our team has successfully implemented autonomous social media orchestration, 
enabling seamless cross-platform content management with intelligent 
scheduling and engagement optimization.

Key achievements:
• Unified API integration across platforms
• Advanced content formatting and optimization
• Professional networking automation
• WSP compliance and quality assurance

Looking forward to connecting with fellow innovators in the space!""",
    options={
        'visibility': 'PUBLIC',
        'hashtags': ['#Innovation', '#SocialMedia', '#Automation', '#LinkedIn', '#Development'],
        'call_to_action': 'Connect with us to learn more about our platform!'
    }
)

print(f"Posted successfully: {post_id}")
```

### Scheduled Professional Updates
```python
from datetime import datetime, timedelta

# Schedule a post for optimal LinkedIn engagement time
schedule_time = datetime.now() + timedelta(days=1)
schedule_time = schedule_time.replace(hour=11, minute=0)  # 11 AM next day

schedule_id = await linkedin.schedule_post(
    content="Weekly professional update: Key insights from our development journey",
    schedule_time=schedule_time,
    options={
        'hashtags': ['#WeeklyUpdate', '#Development', '#Insights'],
        'visibility': 'PUBLIC'
    }
)

print(f"Scheduled for {schedule_time}: {schedule_id}")
```

### Professional Networking
```python
# Get profile information
profile = await linkedin.get_profile_info()
print(f"Profile: {profile['firstName']['localized']['en_US']} {profile['lastName']['localized']['en_US']}")
print(f"Title: {profile['headline']['localized']['en_US']}")

# Get connections
connections = await linkedin.get_connections(limit=20)
print(f"Recent connections: {len(connections)}")

# Send targeted connection request
await linkedin.send_connection_request(
    profile_id="target_profile_id",
    message="Hi! I'd like to connect and share insights about social media automation. Best regards!"
)
```

### Analytics and Insights
```python
# Get post performance
analytics = await linkedin.get_post_analytics("recent_post_id")
print(f"Post performance: {analytics['views']} views, {analytics['engagement_rate']:.1%} engagement")

# Get overall engagement metrics
metrics = await linkedin.get_engagement_metrics("30d")
print(f"30-day metrics: {metrics['total_impressions']} impressions, {metrics['avg_engagement_rate']:.1%} avg engagement")
```

### Company Page Management
```python
# Post as company page
company_post_id = await linkedin.create_company_post(
    company_id="your_company_id",
    content="Company update: We're excited to announce our latest innovation in autonomous development!",
    options={
        'visibility': 'PUBLIC',
        'hashtags': ['#CompanyNews', '#Innovation'],
        'media': ['company_announcement_image.jpg']
    }
)
```

## WSP Compliance Notes

- **WSP 49**: Unified module structure consolidating linkedin_agent, linkedin_scheduler, linkedin_proxy
- **WSP 11**: Complete interface specification with all methods and parameters
- **WSP 22**: Comprehensive ModLog documentation for all components
- **WSP 3**: Proper domain organization within platform_integration
- **WSP 42**: Universal platform protocol implementation for LinkedIn