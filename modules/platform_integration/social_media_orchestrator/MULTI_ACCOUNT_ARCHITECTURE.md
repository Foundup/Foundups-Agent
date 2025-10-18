# Multi-Account Social Media Architecture (WSP-Compliant)

## Executive Summary

Enterprise-scalable, WSP-compliant architecture for managing multiple social media accounts across platforms. This design follows WSP 27 (Universal DAE), WSP 46 (WRE Orchestration), WSP 54 (Agent Duties), and WSP 80 (DAE Cube Architecture).

## Core Architecture Pattern

```
Event Source (YouTube LiveChat DAE)
    v
Event Router (determines which accounts to post to)
    v
Social Media Orchestrator DAE (Coordinator)
    v
Account-Aware Platform DAEs (Executors)
    +-- LinkedIn DAE
    [U+2502]   +-- FoundUps Company (104834798)
    [U+2502]   +-- Development Updates (1263645)
    [U+2502]   +-- Personal Profiles (future)
    +-- X/Twitter DAE
    [U+2502]   +-- FoundUps Account (@FoundUps)
    [U+2502]   +-- GeozeAi Account (@GeozeAi)
    [U+2502]   +-- UnDaoDu Account (@UnDaoDu)
    +-- [Future Platform DAEs...]
```

## Account Configuration System

### Configuration Structure (WSP 3 - Module Organization)

```yaml
# config/social_accounts.yaml
accounts:
  linkedin:
    foundups_company:
      id: "104834798"
      type: "company"
      name: "FoundUps Main"
      credentials_key: "LINKEDIN_FOUNDUPS"
      posting_rules:
        - event_type: "youtube_live"
        - event_type: "product_launch"
      
    development_updates:
      id: "1263645"
      type: "company"
      name: "Development Updates"
      credentials_key: "LINKEDIN_DEV"
      posting_rules:
        - event_type: "git_push"
        - event_type: "wsp_update"
        - event_type: "dae_deployment"
    
    personal_michael:
      id: "michael-trout"
      type: "personal"
      name: "Michael J Trout"
      credentials_key: "LINKEDIN_PERSONAL"
      posting_rules:
        - event_type: "thought_leadership"
      
  x_twitter:
    foundups:
      username: "FoundUps"
      credentials_key: "X_FOUNDUPS"
      posting_rules:
        - event_type: "youtube_live"
        - event_type: "announcement"
    
    geozeai:
      username: "GeozeAi"
      credentials_key: "X_GEOZEAI"  
      posting_rules:
        - event_type: "youtube_live"
        - event_type: "ai_updates"
    
    undaodu:
      username: "UnDaoDu"
      credentials_key: "X_UNDAODU"
      posting_rules:
        - event_type: "consciousness_updates"

# Event routing rules
event_routing:
  youtube_live:
    linkedin: ["foundups_company"]
    x_twitter: ["foundups", "geozeai"]
    
  git_push:
    linkedin: ["development_updates"]
    
  wsp_update:
    linkedin: ["development_updates"]
    x_twitter: ["foundups"]
```

### Credential Management (WSP 64 - Violation Prevention)

```python
class AccountCredentialManager:
    """
    Secure credential management for multiple accounts.
    Never stores passwords in code, uses environment variables.
    """
    
    def __init__(self):
        self.credentials = {}
        self._load_from_env()
    
    def _load_from_env(self):
        """Load credentials from environment variables"""
        # LinkedIn accounts
        self.credentials['LINKEDIN_FOUNDUPS'] = {
            'email': os.getenv('LINKEDIN_FOUNDUPS_EMAIL'),
            'password': os.getenv('LINKEDIN_FOUNDUPS_PASS'),
            'company_id': '104834798'
        }
        
        self.credentials['LINKEDIN_DEV'] = {
            'email': os.getenv('LINKEDIN_DEV_EMAIL', os.getenv('LINKEDIN_FOUNDUPS_EMAIL')),
            'password': os.getenv('LINKEDIN_DEV_PASS', os.getenv('LINKEDIN_FOUNDUPS_PASS')),
            'company_id': '1263645'
        }
        
        # X/Twitter accounts
        self.credentials['X_FOUNDUPS'] = {
            'username': os.getenv('X_FOUNDUPS_USER', 'FoundUps'),
            'password': os.getenv('X_FOUNDUPS_PASS')
        }
        
        self.credentials['X_GEOZEAI'] = {
            'username': os.getenv('X_GEOZEAI_USER', 'GeozeAi'),
            'password': os.getenv('X_GEOZEAI_PASS', os.getenv('x_Acc_pass'))
        }
    
    def get_credentials(self, key: str) -> Dict:
        """Get credentials for a specific account"""
        return self.credentials.get(key, {})
```

## Platform DAE Enhancement (WSP 27 - Universal DAE)

### Enhanced LinkedIn DAE

```python
class LinkedInDAE:
    """
    LinkedIn DAE with multi-account support.
    Each account maintains its own session and anti-detection profile.
    """
    
    def __init__(self):
        self.accounts = {}
        self.sessions = {}  # Separate browser sessions per account
        self._load_accounts()
    
    def _load_accounts(self):
        """Load all LinkedIn accounts from configuration"""
        config = load_config('social_accounts.yaml')
        cred_manager = AccountCredentialManager()
        
        for account_key, account_config in config['accounts']['linkedin'].items():
            self.accounts[account_key] = {
                'config': account_config,
                'credentials': cred_manager.get_credentials(
                    account_config['credentials_key']
                ),
                'poster': None  # Will be initialized on first use
            }
    
    async def post_to_account(self, account_key: str, content: str, options: Dict = None):
        """
        Post to a specific LinkedIn account.
        
        Args:
            account_key: Which account to post to ('foundups_company', 'development_updates')
            content: Content to post
            options: Additional options (schedule, media, etc.)
        """
        if account_key not in self.accounts:
            raise ValueError(f"Unknown LinkedIn account: {account_key}")
        
        account = self.accounts[account_key]
        
        # Initialize poster if needed (lazy loading)
        if not account['poster']:
            account['poster'] = AntiDetectionLinkedIn()
            account['poster'].company_id = account['config']['id']
            
            # Use separate Chrome profile for each account
            profile_dir = f"data/chrome_profiles/linkedin_{account_key}"
            account['poster'].profile_dir = profile_dir
        
        # Adapt content for this specific account
        adapted_content = self.adapt_content_for_account(content, account_key)
        
        # Post using anti-detection
        if account['config']['type'] == 'company':
            return await account['poster'].post_to_company_page(adapted_content)
        else:
            return await account['poster'].post_to_personal(adapted_content)
    
    def adapt_content_for_account(self, content: str, account_key: str) -> str:
        """Adapt content based on account type and audience"""
        account = self.accounts[account_key]
        
        if account_key == 'development_updates':
            # Technical audience - add technical details
            return f"[ROCKET] Development Update\n\n{content}\n\n#WSPCompliant #RecursiveImprovement #OpenSource"
        
        elif account_key == 'foundups_company':
            # Business audience - professional tone
            return f"{content}\n\n#Innovation #TechStartup #LiveStreaming"
        
        return content
```

### Enhanced X/Twitter DAE

```python
class XTwitterDAE:
    """
    X/Twitter DAE with multi-account support.
    Handles account switching and session management.
    """
    
    def __init__(self):
        self.accounts = {}
        self._load_accounts()
    
    def _load_accounts(self):
        """Load all X accounts from configuration"""
        config = load_config('social_accounts.yaml')
        cred_manager = AccountCredentialManager()
        
        for account_key, account_config in config['accounts']['x_twitter'].items():
            self.accounts[account_key] = {
                'config': account_config,
                'credentials': cred_manager.get_credentials(
                    account_config['credentials_key']
                ),
                'poster': None
            }
    
    async def post_to_account(self, account_key: str, content: str, options: Dict = None):
        """Post to specific X account"""
        if account_key not in self.accounts:
            raise ValueError(f"Unknown X account: {account_key}")
        
        account = self.accounts[account_key]
        
        # Initialize poster with account-specific profile
        if not account['poster']:
            account['poster'] = AntiDetectionX()
            account['poster'].username = account['credentials']['username']
            account['poster'].password = account['credentials']['password']
            
            # Separate Chrome profile per account
            profile_dir = f"data/chrome_profiles/x_{account_key}"
            account['poster'].profile_dir = profile_dir
        
        # Adapt content for account personality
        adapted_content = self.adapt_content_for_account(content, account_key)
        
        return await account['poster'].post_to_x(adapted_content)
```

## Event-Driven Orchestration (WSP 46 - WRE Orchestration)

### Event Router

```python
class SocialMediaEventRouter:
    """
    Routes events to appropriate social media accounts.
    Central decision point for which accounts post what.
    """
    
    def __init__(self):
        self.routing_config = self._load_routing_config()
        self.orchestrator = SocialMediaOrchestratorDAE()
    
    async def handle_event(self, event_type: str, event_data: Dict):
        """
        Route event to appropriate accounts based on configuration.
        
        Args:
            event_type: Type of event ('youtube_live', 'git_push', etc.)
            event_data: Event payload with content and metadata
        """
        # Get routing rules for this event type
        routes = self.routing_config.get(event_type, {})
        
        if not routes:
            logger.info(f"No routing rules for event type: {event_type}")
            return
        
        # Prepare base content
        base_content = self._prepare_base_content(event_type, event_data)
        
        # Post to each configured account
        tasks = []
        
        for platform, account_keys in routes.items():
            for account_key in account_keys:
                task = self.orchestrator.post_to_platform_account(
                    platform=platform,
                    account_key=account_key,
                    content=base_content,
                    event_type=event_type
                )
                tasks.append(task)
        
        # Execute all posts in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log results
        self._log_posting_results(event_type, results)
    
    def _prepare_base_content(self, event_type: str, event_data: Dict) -> Dict:
        """Prepare base content structure based on event type"""
        if event_type == 'youtube_live':
            return {
                'mention': '@UnDaoDu',
                'action': 'going live!',
                'title': event_data.get('stream_title', ''),
                'url': event_data.get('stream_url', '')
            }
        
        elif event_type == 'git_push':
            return {
                'type': 'development_update',
                'commits': event_data.get('commits', []),
                'repository': event_data.get('repository', ''),
                'wsp_refs': event_data.get('wsp_refs', [])
            }
        
        return event_data
```

### Enhanced Orchestrator DAE

```python
class SocialMediaOrchestratorDAE:
    """
    Enhanced orchestrator with multi-account support.
    Coordinates posting across multiple accounts on multiple platforms.
    """
    
    def __init__(self):
        self.platform_daes = {
            'linkedin': LinkedInDAE(),
            'x_twitter': XTwitterDAE(),
            # Future: TikTokDAE(), InstagramDAE(), etc.
        }
        self.metrics = PostingMetrics()
    
    async def post_to_platform_account(self, platform: str, account_key: str, 
                                      content: Dict, event_type: str):
        """
        Post to a specific account on a specific platform.
        
        This is the main entry point for multi-account posting.
        """
        if platform not in self.platform_daes:
            raise ValueError(f"Unsupported platform: {platform}")
        
        dae = self.platform_daes[platform]
        
        try:
            # Let the platform DAE handle account-specific posting
            result = await dae.post_to_account(account_key, content)
            
            # Track metrics
            self.metrics.record_post(platform, account_key, event_type, success=True)
            
            return {
                'platform': platform,
                'account': account_key,
                'success': True,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Failed to post to {platform}/{account_key}: {e}")
            self.metrics.record_post(platform, account_key, event_type, success=False)
            
            return {
                'platform': platform,
                'account': account_key,
                'success': False,
                'error': str(e)
            }
```

## Integration Points

### YouTube LiveChat Integration

```python
# In livechat_core.py
async def _handle_stream_live(self, stream_data):
    """When stream goes live, trigger social media posting"""
    
    # Create event
    event = {
        'event_type': 'youtube_live',
        'event_data': {
            'stream_title': stream_data['title'],
            'stream_url': stream_data['url'],
            'channel': stream_data['channel'],
            'timestamp': datetime.now().isoformat()
        }
    }
    
    # Send to event router
    router = SocialMediaEventRouter()
    await router.handle_event(**event)
```

### Git Monitor Integration

```python
# In git_monitor_dae.py
def post_development_updates(self):
    """Post Git updates to appropriate accounts"""
    
    event = {
        'event_type': 'git_push',
        'event_data': {
            'commits': self.get_recent_commits(),
            'repository': 'Foundups-Agent',
            'wsp_refs': self.extract_wsp_references()
        }
    }
    
    # Route to development accounts
    router = SocialMediaEventRouter()
    asyncio.run(router.handle_event(**event))
```

## Enterprise Scaling Features

### 1. Account Pools
```python
class AccountPool:
    """
    Manage pools of accounts for load balancing and failover.
    """
    
    def get_next_available_account(self, platform: str, account_type: str):
        """Get next available account from pool"""
        # Round-robin or least-recently-used selection
        # Handle rate limits per account
        # Automatic failover if account fails
```

### 2. Rate Limit Management
```python
class RateLimitManager:
    """
    Track rate limits per account, per platform.
    """
    
    def can_post(self, platform: str, account_key: str) -> bool:
        """Check if account can post without hitting rate limit"""
        # Platform-specific rate limit tracking
        # Exponential backoff on rate limit hits
```

### 3. Content Queuing
```python
class ContentQueue:
    """
    Queue content when accounts are rate limited.
    """
    
    async def enqueue(self, platform: str, account_key: str, content: Dict):
        """Add content to queue for later posting"""
        # Priority queue based on content importance
        # Retry failed posts automatically
```

### 4. Metrics and Monitoring
```python
class PostingMetrics:
    """
    Track posting success rates, engagement, and patterns.
    """
    
    def record_post(self, platform: str, account_key: str, event_type: str, success: bool):
        """Record posting attempt"""
        # Success rate per account
        # Optimal posting times
        # Engagement tracking
```

## Migration Path

### Phase 1: Current State [OK]
- Single LinkedIn company account (104834798)
- Single X account (GeozeAi)
- Hardcoded in livechat_core

### Phase 2: Configuration System (Next)
1. Create `config/social_accounts.yaml`
2. Implement `AccountCredentialManager`
3. Update `.env` with account-specific credentials

### Phase 3: Multi-Account DAEs
1. Enhance `LinkedInDAE` with multi-account support
2. Enhance `XTwitterDAE` with multi-account support
3. Implement account-specific Chrome profiles

### Phase 4: Event Router
1. Implement `SocialMediaEventRouter`
2. Create routing configuration
3. Update YouTube and Git monitors to use router

### Phase 5: Enterprise Features
1. Add account pools for scaling
2. Implement rate limit management
3. Add content queuing system
4. Deploy metrics dashboard

## Environment Variables

```bash
# LinkedIn Accounts
LINKEDIN_FOUNDUPS_EMAIL=mtrout@foundups.com
LINKEDIN_FOUNDUPS_PASS=xxx
LINKEDIN_DEV_EMAIL=mtrout@foundups.com  # Can be same
LINKEDIN_DEV_PASS=xxx

# X/Twitter Accounts
X_FOUNDUPS_USER=FoundUps
X_FOUNDUPS_PASS=xxx
X_GEOZEAI_USER=GeozeAi
X_GEOZEAI_PASS=xxx
X_UNDAODU_USER=UnDaoDu
X_UNDAODU_PASS=xxx
```

## WSP Compliance Summary

- **WSP 3**: Module organization - Each platform has its own DAE module
- **WSP 27**: Universal DAE architecture - Platform DAEs follow 4-phase pattern
- **WSP 46**: WRE orchestration - Event-driven coordination
- **WSP 54**: Agent duties - Clear separation of orchestrator/platform/account responsibilities
- **WSP 64**: Violation prevention - No hardcoded credentials, configuration-driven
- **WSP 80**: DAE cube architecture - Each platform DAE is an autonomous cube
- **WSP 84**: Code reuse - Leverages existing anti-detection posters

## Conclusion

This architecture provides:
- **Multi-account support** without code changes
- **Enterprise scalability** through account pools and rate limiting
- **Configuration-driven** routing and account management
- **WSP compliance** throughout the design
- **Future-proof** extension points for new platforms and features

The system can grow from 2 accounts to 200 accounts without any architectural changes.