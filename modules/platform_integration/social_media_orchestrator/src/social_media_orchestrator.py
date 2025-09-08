"""
Social Media Orchestrator - Unified social media management system
WSP Compliance: WSP 3, WSP 11, WSP 22, WSP 49, WSP 42
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Import activity control system
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))
try:
    from modules.infrastructure.activity_control.src.activity_control import is_enabled
except ImportError:
    # Fallback for testing - default to enabled
    def is_enabled(activity): return True

try:
    from .oauth.oauth_coordinator import OAuthCoordinator
    from .content.content_orchestrator import ContentOrchestrator  
    from .scheduling.scheduling_engine import SchedulingEngine
    from .platform_adapters.twitter_adapter import TwitterAdapter
    from .platform_adapters.linkedin_adapter import LinkedInAdapter
except ImportError:
    # Fallback for direct execution
    from oauth.oauth_coordinator import OAuthCoordinator
    from content.content_orchestrator import ContentOrchestrator  
    from scheduling.scheduling_engine import SchedulingEngine
    from platform_adapters.twitter_adapter import TwitterAdapter
    from platform_adapters.linkedin_adapter import LinkedInAdapter


class OrchestrationError(Exception):
    """Base exception for orchestrator-related failures"""
    pass


class AuthenticationError(OrchestrationError):
    """Raised when platform authentication fails"""
    pass


class ContentError(OrchestrationError):
    """Raised for content-related issues"""
    pass


class SchedulingError(OrchestrationError):
    """Raised for scheduling conflicts or failures"""
    pass


@dataclass
class PostResult:
    """Result of posting to a platform"""
    success: bool
    post_id: Optional[str]
    error: Optional[str]
    platform: str


class SocialMediaOrchestrator:
    """
    Main orchestration service for unified social media management
    
    Provides centralized management of multiple social media platforms
    with OAuth coordination, content formatting, and scheduling capabilities.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, logger: Optional[logging.Logger] = None):
        """
        Initialize the Social Media Orchestrator
        
        Args:
            config: Configuration including platform settings, logging level
            logger: Custom logger instance
        """
        self.config = config or {}
        self.logger = logger or self._setup_logger()
        
        # Initialize core components
        self.oauth_coordinator = OAuthCoordinator(config.get('oauth', {}))
        self.content_orchestrator = ContentOrchestrator(config.get('content', {}))
        self.scheduling_engine = SchedulingEngine(config.get('scheduling', {}))
        
        # Initialize platform adapters
        self.adapters = {
            'twitter': TwitterAdapter(logger=self.logger),
            'linkedin': LinkedInAdapter(logger=self.logger)
        }
        
        self.initialized = False
        self.total_posts = 0
        self.last_activity = None
        
    def _setup_logger(self) -> logging.Logger:
        """Setup default logger for the orchestrator"""
        logger = logging.getLogger(__name__)
        level = self.config.get('logging_level', 'INFO')
        logger.setLevel(getattr(logging, level.upper()))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Initialize the orchestrator and all components
        
        Args:
            config: Optional configuration override
            
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            self.logger.info("Initializing Social Media Orchestrator")
            
            if config:
                self.config.update(config)
                
            # Initialize scheduling engine if enabled
            if self.config.get('enable_scheduling', True):
                await self.scheduling_engine.initialize()
                
            self.initialized = True
            self.logger.info("Social Media Orchestrator initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize orchestrator: {e}")
            return False
            
    async def authenticate_platform(self, platform: str, credentials: Dict[str, Any]) -> bool:
        """
        Authenticate a specific platform
        
        Args:
            platform: Platform identifier ('twitter', 'linkedin')
            credentials: Platform-specific authentication data
            
        Returns:
            bool: True if authentication successful
            
        Raises:
            AuthenticationError: If authentication fails
        """
        if not self.initialized:
            raise OrchestrationError("Orchestrator not initialized")
            
        if platform not in self.adapters:
            raise AuthenticationError(f"Unsupported platform: {platform}")
            
        try:
            adapter = self.adapters[platform]
            success = await adapter.authenticate(credentials)
            
            if success:
                # Store credentials in OAuth coordinator
                self.oauth_coordinator.store_credentials(platform, credentials)
                self.logger.info(f"Successfully authenticated {platform}")
            else:
                self.logger.error(f"Failed to authenticate {platform}")
                
            return success
            
        except Exception as e:
            error_msg = f"Authentication failed for {platform}: {e}"
            self.logger.error(error_msg)
            raise AuthenticationError(error_msg)
            
    async def post_content(self, content: str, platforms: List[str], 
                         options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Post content to multiple platforms simultaneously
        
        Args:
            content: Content to post (required)
            platforms: Target platforms ['twitter', 'linkedin'] (required)  
            options: Platform-specific options (hashtags, mentions, media)
            
        Returns:
            Dict[str, Any]: Results per platform with post IDs and status
        """
        # Check if social media posting is enabled
        if not is_enabled("platform.api.social_media_posting"):
            self.logger.debug("Social media posting disabled by activity control")
            return {platform: PostResult(
                success=False,
                post_id=None,
                error="Social media posting disabled by activity control",
                platform=platform
            ).__dict__ for platform in platforms}
        
        if not self.initialized:
            raise OrchestrationError("Orchestrator not initialized")
            
        options = options or {}
        results = {}
        
        # Process content for each platform
        tasks = []
        for platform in platforms:
            if platform not in self.adapters:
                results[platform] = PostResult(
                    success=False,
                    post_id=None,
                    error=f"Unsupported platform: {platform}",
                    platform=platform
                ).__dict__
                continue
                
            # Format content for platform
            formatted_content = self.content_orchestrator.format_for_platform(
                content, platform, options.get(platform, {})
            )
            
            # Create post task
            adapter = self.adapters[platform]
            task = self._post_to_platform(adapter, formatted_content, platform, options.get(platform, {}))
            tasks.append((platform, task))
            
        # Execute all posts concurrently
        for platform, task in tasks:
            try:
                post_id = await task
                results[platform] = PostResult(
                    success=True,
                    post_id=post_id,
                    error=None,
                    platform=platform
                ).__dict__
                self.total_posts += 1
                
            except Exception as e:
                results[platform] = PostResult(
                    success=False, 
                    post_id=None,
                    error=str(e),
                    platform=platform
                ).__dict__
                
        self.last_activity = datetime.now().isoformat()
        return results
        
    async def _post_to_platform(self, adapter, content: str, platform: str, options: Dict) -> str:
        """Helper method to post to a single platform"""
        return await adapter.post(content, options)
        
    async def schedule_content(self, content: str, platforms: List[str], 
                             schedule_time: datetime, options: Optional[Dict] = None) -> str:
        """
        Schedule content for posting at a specific time
        
        Args:
            content: Content to schedule (required)
            platforms: Target platforms (required)
            schedule_time: When to post the content (required)
            options: Additional scheduling and content options
            
        Returns:
            str: Schedule ID for tracking the scheduled content
            
        Raises:
            SchedulingError: If scheduling fails
        """
        if not self.initialized:
            raise OrchestrationError("Orchestrator not initialized")
            
        try:
            schedule_id = await self.scheduling_engine.schedule_post(
                content=content,
                platforms=platforms,
                schedule_time=schedule_time,
                options=options or {},
                orchestrator=self
            )
            
            self.logger.info(f"Content scheduled with ID: {schedule_id}")
            return schedule_id
            
        except Exception as e:
            error_msg = f"Failed to schedule content: {e}"
            self.logger.error(error_msg)
            raise SchedulingError(error_msg)
            
    async def get_content_history(self, platform: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get content history for platforms
        
        Args:
            platform: Specific platform or None for all
            limit: Number of recent posts to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of recent posts with metadata
        """
        # This would typically query a database or cache
        # For now, return placeholder data
        return [{
            'platform': platform or 'all',
            'content': 'Sample post content',
            'post_id': f'sample_{i}',
            'timestamp': datetime.now().isoformat(),
            'success': True
        } for i in range(min(limit, 5))]
        
    async def sync_platforms(self) -> Dict[str, bool]:
        """
        Sync all platforms and verify connectivity
        
        Returns:
            Dict[str, bool]: Status of each platform
        """
        results = {}
        
        for platform_name, adapter in self.adapters.items():
            try:
                # Test platform connectivity
                status = await adapter.get_platform_status()
                results[platform_name] = status.get('connected', False)
                
            except Exception as e:
                self.logger.error(f"Failed to sync {platform_name}: {e}")
                results[platform_name] = False
                
        return results
        
    async def get_platform_status(self, platform: str) -> Dict[str, Any]:
        """
        Get detailed status for a specific platform
        
        Args:
            platform: Platform identifier
            
        Returns:
            Dict[str, Any]: Detailed platform status
        """
        if platform not in self.adapters:
            raise OrchestrationError(f"Unsupported platform: {platform}")
            
        adapter = self.adapters[platform]
        return await adapter.get_platform_status()
        
    def list_supported_platforms(self) -> List[str]:
        """
        List all supported platforms
        
        Returns:
            List[str]: List of platform identifiers
        """
        return list(self.adapters.keys())
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive orchestrator status
        
        Returns:
            Dict[str, Any]: Complete status information
        """
        platform_status = {}
        for platform, adapter in self.adapters.items():
            try:
                # Quick synchronous status check
                platform_status[platform] = 'authenticated' if hasattr(adapter, '_authenticated') and adapter._authenticated else 'not_authenticated'
            except:
                platform_status[platform] = 'error'
                
        return {
            'platforms': platform_status,
            'active_schedules': self.scheduling_engine.get_active_count() if self.initialized else 0,
            'total_posts': self.total_posts,
            'last_activity': self.last_activity,
            'initialized': self.initialized
        }
        
    async def test_platform_hello_world(self, platform: str, dry_run: bool = True) -> Dict[str, Any]:
        """
        Test platform with hello world message
        
        Args:
            platform: Platform to test
            dry_run: If True, simulate posting without actually posting
            
        Returns:
            Dict[str, Any]: Test results
        """
        if platform not in self.adapters:
            return {'success': False, 'error': f'Unsupported platform: {platform}'}
            
        test_content = f"🤖 Hello World from FoundUps Social Media Orchestrator! #TestMode #FoundUps"
        
        try:
            adapter = self.adapters[platform]
            
            if dry_run:
                # Simulate the post
                self.logger.info(f"DRY RUN: Would post to {platform}: {test_content}")
                return {
                    'success': True,
                    'platform': platform,
                    'content': test_content,
                    'dry_run': True,
                    'post_id': f'dry_run_{platform}_{int(datetime.now().timestamp())}'
                }
            else:
                # Actually post
                post_id = await adapter.post(test_content, {'test_mode': True})
                return {
                    'success': True,
                    'platform': platform,
                    'content': test_content,
                    'dry_run': False,
                    'post_id': post_id
                }
                
        except Exception as e:
            return {
                'success': False,
                'platform': platform,
                'error': str(e),
                'dry_run': dry_run
            }


def create_social_media_orchestrator(config: Optional[Dict[str, Any]] = None) -> SocialMediaOrchestrator:
    """
    Factory function to create a Social Media Orchestrator instance
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        SocialMediaOrchestrator: Configured orchestrator instance
    """
    return SocialMediaOrchestrator(config)