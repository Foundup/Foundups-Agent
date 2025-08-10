# LinkedIn Unified Platform Integration

**WSP Compliance**: WSP 3, WSP 11, WSP 22, WSP 49, WSP 42

Unified LinkedIn platform integration module consolidating functionality from:
- `linkedin_agent` - Professional networking and engagement
- `linkedin_scheduler` - Content scheduling and automation  
- `linkedin_proxy` - Direct API proxy operations

## Features

### Professional Content Management
- Intelligent content formatting for LinkedIn
- Professional hashtag optimization
- Company page posting capabilities
- Media attachment support

### Advanced Scheduling
- Optimal posting time suggestions
- LinkedIn-specific engagement optimization
- Bulk content scheduling
- Automated professional updates

### Professional Networking
- Connection management and outreach
- Profile analytics and insights
- Professional engagement automation
- Industry-specific targeting

### OAuth Integration
- Complete OAuth 2.0 flow implementation
- Secure credential management
- Token refresh automation
- Multi-account support

## Quick Start

```python
from modules.platform_integration.linkedin import LinkedInManager

# Initialize LinkedIn manager
linkedin = LinkedInManager({
    'logging_level': 'INFO',
    'enable_scheduling': True
})

# Authenticate
await linkedin.authenticate({
    'client_id': 'your_client_id',
    'client_secret': 'your_client_secret',
    'access_token': 'your_access_token'  # Optional
})

# Create professional post
post_id = await linkedin.create_post(
    "Exciting professional update! 🚀",
    options={
        'hashtags': ['#Innovation', '#LinkedIn'],
        'visibility': 'PUBLIC'
    }
)
```

## OAuth Setup

1. Create LinkedIn application at https://developer.linkedin.com/
2. Configure OAuth redirect URI
3. Obtain client credentials
4. Use OAuth flow for user authentication

```python
# Get OAuth URL
auth_url = linkedin.get_oauth_url(
    redirect_uri="http://localhost:8080/callback",
    scope="w_member_social r_liteprofile"
)

# Exchange code for token
token_data = await linkedin.exchange_code_for_token(
    code="auth_code_from_callback",
    redirect_uri="http://localhost:8080/callback"
)
```

## Professional Features

### Content Optimization
- Character limit compliance (3000 chars)
- Professional tone suggestions
- Hashtag recommendations
- Engagement optimization

### Networking Automation
- Connection request management
- Professional messaging
- Industry targeting
- Engagement tracking

### Analytics Integration
- Post performance metrics
- Engagement analytics
- Professional network insights
- Growth tracking

## WSP Compliance

- **WSP 49**: Unified module structure with proper directory organization
- **WSP 11**: Complete interface specification with all public methods
- **WSP 22**: Comprehensive documentation and ModLog integration
- **WSP 3**: Proper domain organization within platform_integration
- **WSP 42**: Universal platform protocol implementation

## Migration from Legacy Modules

### From linkedin_agent
```python
# Old way
from modules.platform_integration.linkedin_agent import LinkedInAgent
agent = LinkedInAgent()

# New unified way  
from modules.platform_integration.linkedin import LinkedInManager
linkedin = LinkedInManager()
```

### From linkedin_scheduler
```python
# Old way
from modules.platform_integration.linkedin_scheduler import LinkedInScheduler
scheduler = LinkedInScheduler()

# New unified way - scheduling is built-in
linkedin = LinkedInManager()
await linkedin.schedule_post(content, schedule_time)
```

### From linkedin_proxy
```python
# Old way
from modules.platform_integration.linkedin_proxy import LinkedInProxy
proxy = LinkedInProxy()

# New unified way - proxy functionality is integrated
linkedin = LinkedInManager()
await linkedin.create_post(content)  # Uses proxy internally
```

## Development

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_auth.py -v
python -m pytest tests/test_content.py -v
python -m pytest tests/test_scheduling.py -v
```

### Validation
```bash
# Validate module structure and functionality
python scripts/validate.py
```

## API Reference

See `INTERFACE.md` for complete API documentation including:
- Method signatures and parameters
- Return types and error handling
- Usage examples and best practices
- Professional networking guidelines