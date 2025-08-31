#!/usr/bin/env python3
"""
Multi-Account Manager for Social Media Orchestrator
WSP-Compliant implementation for enterprise-scale social media management
Handles routing, account selection, and credential management
"""

import os
import sys
import yaml
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

# Add parent path for imports
sys.path.insert(0, 'O:/Foundups-Agent')

# Import existing anti-detection posters
from modules.platform_integration.linkedin_agent.src.anti_detection_poster import AntiDetectionLinkedIn
from modules.platform_integration.x_twitter.src.x_anti_detection_poster import AntiDetectionX

logger = logging.getLogger(__name__)


@dataclass
class AccountInfo:
    """Information about a social media account"""
    platform: str
    account_key: str
    config: Dict
    credentials: Dict
    poster: Optional[Any] = None  # Will hold platform-specific poster
    last_post_time: Optional[datetime] = None
    post_count: int = 0


class AccountCredentialManager:
    """
    Secure credential management for multiple accounts.
    WSP 64 compliant - never stores passwords in code.
    """
    
    def __init__(self):
        self.credentials = {}
        self._load_from_env()
    
    def _load_from_env(self):
        """Load credentials from environment variables"""
        # LinkedIn accounts
        self.credentials['LINKEDIN_FOUNDUPS'] = {
            'email': os.getenv('LINKEDIN_EMAIL', 'mtrout@foundups.com'),
            'password': os.getenv('LINKEDIN_PASSWORD'),
            'company_id': '104834798'
        }
        
        self.credentials['LINKEDIN_DEV'] = {
            'email': os.getenv('LINKEDIN_DEV_EMAIL', os.getenv('LINKEDIN_EMAIL', 'mtrout@foundups.com')),
            'password': os.getenv('LINKEDIN_DEV_PASS', os.getenv('LINKEDIN_PASSWORD')),
            'company_id': '1263645'
        }
        
        # X/Twitter accounts
        self.credentials['X_FOUNDUPS'] = {
            'username': os.getenv('X_Acc2', 'foundups'),  # Use X_Acc2 for FoundUps
            'password': os.getenv('x_Acc_pass')
        }
        
        self.credentials['X_GEOZEAI'] = {
            'username': os.getenv('X_Acc1', 'GeozeAi'),
            'password': os.getenv('x_Acc_pass')
        }
    
    def get_credentials(self, key: str) -> Dict:
        """Get credentials for a specific account"""
        return self.credentials.get(key, {})


class MultiAccountManager:
    """
    Manages multiple social media accounts across platforms.
    Core component for enterprise scaling.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize multi-account manager.
        
        Args:
            config_path: Path to social_accounts.yaml configuration
        """
        self.config_path = config_path or "modules/platform_integration/social_media_orchestrator/config/social_accounts.yaml"
        self.config = self._load_config()
        self.credential_manager = AccountCredentialManager()
        self.accounts = {}  # platform -> account_key -> AccountInfo
        self._initialize_accounts()
        
    def _load_config(self) -> Dict:
        """Load configuration from YAML file"""
        config_file = Path(self.config_path)
        if not config_file.exists():
            # Use default configuration if file doesn't exist
            return self._get_default_config()
        
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def _get_default_config(self) -> Dict:
        """Get default configuration for quick start"""
        return {
            'accounts': {
                'linkedin': {
                    'foundups_company': {
                        'id': '104834798',
                        'type': 'company',
                        'name': 'FoundUps',
                        'credentials_key': 'LINKEDIN_FOUNDUPS'
                    }
                },
                'x_twitter': {
                    'geozeai': {
                        'username': 'GeozeAi',
                        'credentials_key': 'X_GEOZEAI'
                    }
                }
            },
            'event_routing': {
                'youtube_live': {
                    'linkedin': ['foundups_company'],
                    'x_twitter': ['geozeai']
                }
            }
        }
    
    def _initialize_accounts(self):
        """Initialize all configured accounts"""
        for platform, platform_accounts in self.config.get('accounts', {}).items():
            self.accounts[platform] = {}
            
            for account_key, account_config in platform_accounts.items():
                credentials = self.credential_manager.get_credentials(
                    account_config.get('credentials_key', '')
                )
                
                self.accounts[platform][account_key] = AccountInfo(
                    platform=platform,
                    account_key=account_key,
                    config=account_config,
                    credentials=credentials
                )
                
                logger.info(f"Initialized account: {platform}/{account_key}")
    
    def get_accounts_for_event(self, event_type: str) -> Dict[str, List[str]]:
        """
        Get which accounts should post for a given event type.
        
        Args:
            event_type: Type of event (youtube_live, git_push, etc.)
            
        Returns:
            Dict mapping platform to list of account keys
        """
        routing = self.config.get('event_routing', {})
        return routing.get(event_type, {})
    
    def get_account(self, platform: str, account_key: str) -> Optional[AccountInfo]:
        """Get specific account information"""
        if platform in self.accounts and account_key in self.accounts[platform]:
            return self.accounts[platform][account_key]
        return None
    
    async def post_to_account(self, platform: str, account_key: str, content: str) -> Dict:
        """
        Post content to a specific account.
        
        Args:
            platform: Platform name (linkedin, x_twitter)
            account_key: Account identifier
            content: Content to post
            
        Returns:
            Dict with success status and details
        """
        account = self.get_account(platform, account_key)
        if not account:
            return {
                'success': False,
                'error': f'Account not found: {platform}/{account_key}'
            }
        
        try:
            # Initialize poster if needed (lazy loading)
            if not account.poster:
                account.poster = self._create_poster(platform, account)
            
            # Adapt content for this account
            adapted_content = self._adapt_content(content, platform, account_key)
            
            # Post using the appropriate method
            if platform == 'linkedin':
                success = await self._post_to_linkedin(account, adapted_content)
            elif platform == 'x_twitter':
                success = await self._post_to_x(account, adapted_content)
            else:
                return {'success': False, 'error': f'Unsupported platform: {platform}'}
            
            # Update account stats
            if success:
                account.last_post_time = datetime.now()
                account.post_count += 1
            
            return {
                'success': success,
                'platform': platform,
                'account': account_key,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error posting to {platform}/{account_key}: {e}")
            return {
                'success': False,
                'error': str(e),
                'platform': platform,
                'account': account_key
            }
    
    def _create_poster(self, platform: str, account: AccountInfo) -> Any:
        """Create platform-specific poster instance"""
        if platform == 'linkedin':
            poster = AntiDetectionLinkedIn()
            # Set company ID if it's a company account
            if account.config.get('type') == 'company':
                poster.company_id = account.config.get('id')
            return poster
            
        elif platform == 'x_twitter':
            poster = AntiDetectionX()
            poster.username = account.credentials.get('username')
            poster.password = account.credentials.get('password')
            return poster
        
        return None
    
    def _adapt_content(self, content: str, platform: str, account_key: str) -> str:
        """
        Adapt content for specific platform and account.
        
        Applies platform-specific formatting and account personality.
        """
        adaptation_rules = self.config.get('content_adaptation', {}).get(platform, {}).get(account_key, {})
        
        adapted = content
        
        # Add hashtags if configured
        hashtags = adaptation_rules.get('add_hashtags', [])
        if hashtags:
            adapted += '\n\n' + ' '.join(hashtags)
        
        # Truncate for X if needed
        if platform == 'x_twitter':
            max_length = adaptation_rules.get('max_length', 280)
            if len(adapted) > max_length:
                adapted = adapted[:max_length-3] + '...'
        
        return adapted
    
    async def _post_to_linkedin(self, account: AccountInfo, content: str) -> bool:
        """Post to LinkedIn account"""
        try:
            # Use synchronous method wrapped in async
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                account.poster.post_to_company_page,
                content
            )
            return result
        except Exception as e:
            logger.error(f"LinkedIn posting error: {e}")
            return False
    
    async def _post_to_x(self, account: AccountInfo, content: str) -> bool:
        """Post to X/Twitter account"""
        try:
            # Use synchronous method wrapped in async
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                account.poster.post_to_x,
                content
            )
            return result
        except Exception as e:
            logger.error(f"X posting error: {e}")
            return False


class SocialMediaEventRouter:
    """
    Routes events to appropriate social media accounts.
    Central decision point for multi-account posting.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize event router.
        
        Args:
            config_path: Path to configuration file
        """
        self.manager = MultiAccountManager(config_path)
        self.logger = logging.getLogger(__name__)
    
    async def handle_event(self, event_type: str, event_data: Dict) -> Dict[str, Any]:
        """
        Route event to appropriate accounts based on configuration.
        
        Args:
            event_type: Type of event ('youtube_live', 'git_push', etc.)
            event_data: Event payload with content and metadata
            
        Returns:
            Dict with results for each platform/account
        """
        self.logger.info(f"Handling event: {event_type}")
        
        # Get routing rules for this event
        accounts_to_post = self.manager.get_accounts_for_event(event_type)
        
        if not accounts_to_post:
            self.logger.info(f"No accounts configured for event type: {event_type}")
            return {'message': 'No accounts configured for this event'}
        
        # Prepare content based on event type
        content = self._prepare_content(event_type, event_data)
        
        # Post to each configured account
        tasks = []
        for platform, account_keys in accounts_to_post.items():
            for account_key in account_keys:
                task = self.manager.post_to_account(platform, account_key, content)
                tasks.append(task)
        
        # Execute all posts in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Format results
        formatted_results = {}
        for i, (platform, account_keys) in enumerate(accounts_to_post.items()):
            for j, account_key in enumerate(account_keys):
                key = f"{platform}/{account_key}"
                result = results[i * len(account_keys) + j]
                if isinstance(result, Exception):
                    formatted_results[key] = {'success': False, 'error': str(result)}
                else:
                    formatted_results[key] = result
        
        return formatted_results
    
    def _prepare_content(self, event_type: str, event_data: Dict) -> str:
        """Prepare content string based on event type"""
        if event_type == 'youtube_live':
            mention = event_data.get('mention', '@UnDaoDu')
            title = event_data.get('stream_title', 'Live Stream')
            url = event_data.get('stream_url', '')
            
            return f"{mention} going live!\n\n{title}\n\n{url}"
        
        elif event_type == 'git_push':
            commits = event_data.get('commits', [])
            if not commits:
                return "Development update: New changes pushed"
            
            # Format commit messages
            content = "🚀 Development Update\n\n"
            for commit in commits[:3]:  # Show first 3 commits
                content += f"• {commit.get('subject', 'Update')}\n"
            
            if len(commits) > 3:
                content += f"...and {len(commits) - 3} more commits\n"
            
            return content
        
        # Default: use raw content if provided
        return event_data.get('content', str(event_data))


def test_multi_account():
    """Test multi-account functionality"""
    import asyncio
    
    print("Multi-Account Manager Test")
    print("=" * 60)
    
    # Initialize router
    router = SocialMediaEventRouter()
    
    # Test YouTube live event
    event = {
        'event_type': 'youtube_live',
        'event_data': {
            'stream_title': 'Test Stream - Multi-Account',
            'stream_url': 'https://youtube.com/watch?v=test',
            'mention': '@UnDaoDu'
        }
    }
    
    print(f"\nEvent: {event['event_type']}")
    print(f"Configured accounts:")
    accounts = router.manager.get_accounts_for_event(event['event_type'])
    for platform, account_keys in accounts.items():
        for account_key in account_keys:
            print(f"  - {platform}/{account_key}")
    
    # Run the event handling
    results = asyncio.run(router.handle_event(**event))
    
    print("\nResults:")
    for account, result in results.items():
        status = "✓" if result.get('success') else "✗"
        print(f"  {status} {account}: {result}")
    
    return results


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    test_multi_account()