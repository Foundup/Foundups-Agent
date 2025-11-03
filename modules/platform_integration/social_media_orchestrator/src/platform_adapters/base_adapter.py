"""
Base Platform Adapter
Abstract interface for all social media platform adapters
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass


@dataclass
class PlatformLimits:
    """Platform-specific limits and constraints"""
    max_content_length: int
    daily_post_limit: Optional[int] = None
    hourly_post_limit: Optional[int] = None
    rate_limit_window: int = 3600  # seconds
    supports_media: bool = True
    supports_scheduling: bool = True
    supported_media_types: List[str] = None

    def __post_init__(self):
        if self.supported_media_types is None:
            self.supported_media_types = ['image/jpeg', 'image/png']


@dataclass  
class PostResult:
    """Result of a platform post operation"""
    success: bool
    post_id: Optional[str] = None
    error: Optional[str] = None
    platform_response: Optional[Dict[str, Any]] = None
    posted_at: Optional[datetime] = None


class BasePlatformAdapter(ABC):
    """
    Abstract base class for all social media platform adapters
    
    Provides unified interface for cross-platform operations while allowing
    platform-specific implementations to handle their unique requirements.
    """

    def __init__(self, platform_name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize platform adapter
        
        Args:
            platform_name: Name of the platform (e.g., 'twitter', 'linkedin')
            config: Platform-specific configuration
        """
        self.platform_name = platform_name
        self.config = config or {}
        self.authenticated = False
        self.client = None
        self._limits = None

    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """
        Authenticate with the platform using provided credentials
        
        Args:
            credentials: Platform-specific authentication data
            
        Returns:
            bool: True if authentication successful
        """
        pass

    @abstractmethod
    async def post(self, content: str, options: Optional[Dict[str, Any]] = None) -> PostResult:
        """
        Post content to the platform
        
        Args:
            content: Text content to post
            options: Platform-specific posting options
            
        Returns:
            PostResult: Result of the posting operation
        """
        pass

    @abstractmethod
    def get_platform_limits(self) -> PlatformLimits:
        """
        Get platform-specific limits and constraints
        
        Returns:
            PlatformLimits: Platform limits and capabilities
        """
        pass

    @abstractmethod
    async def get_profile_info(self) -> Dict[str, Any]:
        """
        Get authenticated user's profile information
        
        Returns:
            Dict containing profile data
        """
        pass

    async def validate_content(self, content: str) -> Dict[str, Any]:
        """
        Validate content against platform limits
        
        Args:
            content: Content to validate
            
        Returns:
            Dict with validation results
        """
        limits = self.get_platform_limits()
        
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        if len(content) > limits.max_content_length:
            validation['valid'] = False
            validation['errors'].append(
                f"Content too long: {len(content)}/{limits.max_content_length} characters"
            )
        
        if len(content.strip()) == 0:
            validation['valid'] = False
            validation['errors'].append("Content cannot be empty")
        
        return validation

    async def test_connection(self) -> Dict[str, Any]:
        """
        Test platform connection and authentication
        
        Returns:
            Dict with connection test results
        """
        try:
            if not self.authenticated:
                return {
                    'success': False,
                    'error': 'Not authenticated',
                    'platform': self.platform_name
                }
            
            profile = await self.get_profile_info()
            return {
                'success': True,
                'platform': self.platform_name,
                'profile': profile,
                'limits': self.get_platform_limits().__dict__
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'platform': self.platform_name
            }

    def get_status(self) -> Dict[str, Any]:
        """
        Get current adapter status
        
        Returns:
            Dict with adapter status information
        """
        return {
            'platform': self.platform_name,
            'authenticated': self.authenticated,
            'config': {k: '***' if 'secret' in k.lower() or 'token' in k.lower() 
                      else v for k, v in self.config.items()},
            'limits': self.get_platform_limits().__dict__ if self._limits else None
        }

    async def hello_world_test(self, test_mode: bool = True) -> PostResult:
        """
        Perform hello world test for the platform
        
        Args:
            test_mode: If True, simulates posting without actually posting
            
        Returns:
            PostResult: Result of the hello world test
        """
        hello_content = f"[ROCKET] Hello World from FoundUps {self.platform_name.title()} integration! #FoundUps #HelloWorld"
        
        if test_mode:
            # Simulate the post without actually posting
            validation = await self.validate_content(hello_content)
            
            if not validation['valid']:
                return PostResult(
                    success=False,
                    error=f"Validation failed: {validation['errors']}"
                )
            
            return PostResult(
                success=True,
                post_id=f"test_{self.platform_name}_{datetime.now().timestamp()}",
                posted_at=datetime.now()
            )
        else:
            # Actually post the content
            return await self.post(hello_content, {'test_post': True})