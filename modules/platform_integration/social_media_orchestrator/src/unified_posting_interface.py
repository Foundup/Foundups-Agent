#!/usr/bin/env python3
"""
Unified Social Media Posting Interface for DAE Cubes
WSP Compliance: WSP 3, WSP 11, WSP 27, WSP 49, WSP 54, WSP 80

This interface allows ANY DAE cube to post to social media platforms
using a unified protocol that abstracts platform differences.

WSP 27: Universal DAE pattern - all DAEs can use this interface
WSP 80: Cube-level DAE implementation for social posting
"""

import os
import sys
import json
import asyncio
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

# Add parent path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))


class Platform(Enum):
    """Supported social media platforms"""
    LINKEDIN = "linkedin"
    X_TWITTER = "x_twitter"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"


class PostType(Enum):
    """Types of posts"""
    IMMEDIATE = "immediate"  # Post now
    SCHEDULED = "scheduled"  # Schedule for later
    DRAFT = "draft"         # Save as draft


@dataclass
class PostRequest:
    """
    Universal post request structure for any DAE cube
    
    This dataclass represents a platform-agnostic posting request
    that can be used by any DAE cube to post to any platform.
    """
    content: str                    # The actual content to post
    platforms: List[Platform]       # Target platforms
    post_type: PostType = PostType.IMMEDIATE
    schedule_time: Optional[datetime] = None
    media_urls: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'content': self.content,
            'platforms': [p.value for p in self.platforms],
            'post_type': self.post_type.value,
            'schedule_time': self.schedule_time.isoformat() if self.schedule_time else None,
            'media_urls': self.media_urls,
            'hashtags': self.hashtags,
            'mentions': self.mentions,
            'metadata': self.metadata
        }


@dataclass
class PostResponse:
    """
    Universal post response structure
    
    Contains results from posting to multiple platforms
    """
    request_id: str
    results: Dict[str, Dict[str, Any]]  # Platform -> result details
    timestamp: datetime
    success_count: int
    failure_count: int
    
    def all_successful(self) -> bool:
        """Check if all platforms posted successfully"""
        return self.failure_count == 0
    
    def get_platform_result(self, platform: Platform) -> Optional[Dict[str, Any]]:
        """Get result for specific platform"""
        return self.results.get(platform.value)


class PlatformAdapter(ABC):
    """
    Abstract base class for platform-specific adapters
    
    Each platform implements this interface to handle platform-specific
    posting logic while maintaining a consistent interface.
    """
    
    @abstractmethod
    async def post(self, request: PostRequest) -> Dict[str, Any]:
        """Post content to the platform"""
        pass
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the platform"""
        pass
    
    @abstractmethod
    def format_content(self, request: PostRequest) -> str:
        """Format content for platform-specific requirements"""
        pass
    
    @abstractmethod
    def validate_content(self, content: str) -> bool:
        """Validate content meets platform requirements"""
        pass


class LinkedInAdapter(PlatformAdapter):
    """
    LinkedIn-specific adapter using anti-detection posting
    """
    
    def __init__(self):
        self.poster = None
        self._initialize_poster()
    
    def _initialize_poster(self):
        """Initialize the anti-detection LinkedIn poster"""
        try:
            from modules.platform_integration.linkedin_agent.src.anti_detection_poster import LinkedInAntiDetectionPoster
            self.poster = LinkedInAntiDetectionPoster()
        except ImportError:
            print("[WARN] LinkedIn anti-detection poster not available")
    
    async def authenticate(self) -> bool:
        """Check if LinkedIn credentials are configured"""
        email = os.getenv('LINKEDIN_EMAIL')
        password = os.getenv('LINKEDIN_PASSWORD')
        return bool(email and password)
    
    def format_content(self, request: PostRequest) -> str:
        """Format content for LinkedIn"""
        content = request.content
        
        # Add hashtags if provided
        if request.hashtags:
            hashtags_str = ' '.join(f'#{tag}' for tag in request.hashtags)
            content = f"{content}\n\n{hashtags_str}"
        
        return content
    
    def validate_content(self, content: str) -> bool:
        """Validate LinkedIn content"""
        # LinkedIn has a 3000 character limit
        return len(content) <= 3000
    
    async def post(self, request: PostRequest) -> Dict[str, Any]:
        """Post to LinkedIn using anti-detection method"""
        if not self.poster:
            return {'success': False, 'error': 'LinkedIn poster not initialized'}
        
        content = self.format_content(request)
        
        if not self.validate_content(content):
            return {'success': False, 'error': 'Content exceeds LinkedIn limit'}
        
        try:
            # Use the anti-detection poster
            success = await self.poster.post_content(content)
            return {
                'success': success,
                'platform': 'linkedin',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class XTwitterAdapter(PlatformAdapter):
    """
    X/Twitter-specific adapter using anti-detection posting
    """
    
    def __init__(self):
        self.poster = None
        self._initialize_poster()
    
    def _initialize_poster(self):
        """Initialize the anti-detection X/Twitter poster"""
        try:
            from modules.platform_integration.x_twitter.src.simple_x_poster import SimpleXPoster
            self.poster = SimpleXPoster()
        except ImportError:
            print("[WARN] X/Twitter poster not available")
    
    async def authenticate(self) -> bool:
        """Check if X/Twitter credentials are configured"""
        username = os.getenv('X_Acc2') or os.getenv('X_Acc1')
        password = os.getenv('x_Acc_pass')
        return bool(username and password)
    
    def format_content(self, request: PostRequest) -> str:
        """Format content for X/Twitter"""
        content = request.content
        
        # Remove emojis for X/Twitter (encoding issues)
        content = ''.join(char for char in content if ord(char) <= 127)
        
        # Add hashtags if provided
        if request.hashtags:
            hashtags_str = ' '.join(f'#{tag}' for tag in request.hashtags)
            # Ensure we don't exceed 280 chars
            available_space = 280 - len(content) - 2  # 2 for newlines
            if len(hashtags_str) <= available_space:
                content = f"{content}\n\n{hashtags_str}"
        
        # Truncate if too long
        if len(content) > 280:
            content = content[:277] + "..."
        
        return content
    
    def validate_content(self, content: str) -> bool:
        """Validate X/Twitter content"""
        # X/Twitter has a 280 character limit
        return len(content) <= 280
    
    async def post(self, request: PostRequest) -> Dict[str, Any]:
        """Post to X/Twitter using the last button method"""
        if not self.poster:
            return {'success': False, 'error': 'X/Twitter poster not initialized'}
        
        content = self.format_content(request)
        
        if not self.validate_content(content):
            return {'success': False, 'error': 'Content exceeds X/Twitter limit'}
        
        try:
            # Use the simple poster that finds POST as last button
            success = self.poster.post_to_x(content)
            return {
                'success': success,
                'platform': 'x_twitter',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class UnifiedSocialPoster:
    """
    Unified social media posting interface for all DAE cubes
    
    This is the main interface that any DAE cube can use to post
    to multiple social media platforms with a single call.
    
    WSP 80: This implements the cube-level DAE pattern for social posting
    WSP 27: Follows the universal DAE architecture
    """
    
    def __init__(self):
        self.adapters = {}
        self._initialize_adapters()
        self.post_history = []
    
    def _initialize_adapters(self):
        """Initialize all platform adapters"""
        self.adapters[Platform.LINKEDIN] = LinkedInAdapter()
        self.adapters[Platform.X_TWITTER] = XTwitterAdapter()
        # Add more adapters as needed
    
    async def post(self, request: PostRequest) -> PostResponse:
        """
        Post to multiple platforms with a single request
        
        This is the main method that DAE cubes call to post content.
        It handles posting to all requested platforms and returns
        a unified response.
        """
        request_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        results = {}
        success_count = 0
        failure_count = 0
        
        # Post to each requested platform
        for platform in request.platforms:
            if platform not in self.adapters:
                results[platform.value] = {
                    'success': False,
                    'error': f'Platform {platform.value} not supported'
                }
                failure_count += 1
                continue
            
            adapter = self.adapters[platform]
            
            # Check authentication
            if not await adapter.authenticate():
                results[platform.value] = {
                    'success': False,
                    'error': f'Platform {platform.value} not authenticated'
                }
                failure_count += 1
                continue
            
            # Handle different post types
            if request.post_type == PostType.SCHEDULED:
                # For scheduled posts, we'd integrate with scheduling system
                # For now, just post immediately
                pass
            
            # Post to platform
            try:
                result = await adapter.post(request)
                results[platform.value] = result
                
                if result.get('success'):
                    success_count += 1
                else:
                    failure_count += 1
                    
            except Exception as e:
                results[platform.value] = {
                    'success': False,
                    'error': str(e)
                }
                failure_count += 1
        
        # Create response
        response = PostResponse(
            request_id=request_id,
            results=results,
            timestamp=datetime.now(),
            success_count=success_count,
            failure_count=failure_count
        )
        
        # Store in history
        self.post_history.append({
            'request': request.to_dict(),
            'response': response.__dict__
        })
        
        return response
    
    async def post_stream_notification(self, 
                                      stream_title: str,
                                      stream_url: str,
                                      platforms: Optional[List[Platform]] = None) -> PostResponse:
        """
        Convenience method for posting stream notifications
        
        This method is specifically designed for the automatic stream monitor
        to easily post stream notifications to social media.
        """
        if platforms is None:
            platforms = [Platform.LINKEDIN, Platform.X_TWITTER]
        
        # Create LinkedIn content
        linkedin_content = f"""[LIVE] We're LIVE NOW!

{stream_title}

Join our AI development session.

Link: {stream_url}

#ArtificialIntelligence #SoftwareDevelopment #Innovation #QuantumComputing #FoundUps"""
        
        # Create X/Twitter content (no emojis)
        x_content = f"""[LIVE] NOW: {stream_title[:100]}

Watch: {stream_url}

#AI #LiveCoding #FoundUps #QuantumComputing"""
        
        # Create requests for each platform
        if Platform.LINKEDIN in platforms and Platform.X_TWITTER in platforms:
            # Post different content to each platform
            linkedin_request = PostRequest(
                content=linkedin_content,
                platforms=[Platform.LINKEDIN],
                post_type=PostType.IMMEDIATE
            )
            
            x_request = PostRequest(
                content=x_content,
                platforms=[Platform.X_TWITTER],
                post_type=PostType.IMMEDIATE
            )
            
            # Post to both
            linkedin_response = await self.post(linkedin_request)
            x_response = await self.post(x_request)
            
            # Combine responses
            combined_results = {}
            combined_results.update(linkedin_response.results)
            combined_results.update(x_response.results)
            
            return PostResponse(
                request_id=f"stream_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                results=combined_results,
                timestamp=datetime.now(),
                success_count=linkedin_response.success_count + x_response.success_count,
                failure_count=linkedin_response.failure_count + x_response.failure_count
            )
        else:
            # Post to selected platforms
            content = linkedin_content if Platform.LINKEDIN in platforms else x_content
            request = PostRequest(
                content=content,
                platforms=platforms,
                post_type=PostType.IMMEDIATE
            )
            return await self.post(request)
    
    def get_supported_platforms(self) -> List[Platform]:
        """Get list of supported platforms"""
        return list(self.adapters.keys())
    
    def get_post_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent post history"""
        return self.post_history[-limit:]


# DAE Cube Interface
class DAESocialInterface:
    """
    Interface specifically designed for DAE cubes to use
    
    This provides a simplified interface that any DAE cube can use
    to post to social media without worrying about platform specifics.
    
    WSP 80: Cube-level DAE implementation
    WSP 54: Agent coordination pattern
    """
    
    def __init__(self):
        self.poster = UnifiedSocialPoster()
    
    async def announce_stream(self, title: str, url: str) -> bool:
        """
        Announce a live stream on all configured platforms
        
        Simple method for DAE cubes to announce streams.
        """
        response = await self.poster.post_stream_notification(title, url)
        return response.all_successful()
    
    async def post_update(self, message: str, platforms: Optional[List[str]] = None) -> bool:
        """
        Post a general update to social media
        
        Simple method for DAE cubes to post updates.
        """
        if platforms:
            platform_enums = [Platform(p) for p in platforms]
        else:
            platform_enums = [Platform.LINKEDIN, Platform.X_TWITTER]
        
        request = PostRequest(
            content=message,
            platforms=platform_enums,
            post_type=PostType.IMMEDIATE
        )
        
        response = await self.poster.post(request)
        return response.all_successful()
    
    async def schedule_post(self, message: str, schedule_time: datetime, platforms: Optional[List[str]] = None) -> str:
        """
        Schedule a post for later
        
        Allows DAE cubes to schedule posts for optimal times.
        """
        if platforms:
            platform_enums = [Platform(p) for p in platforms]
        else:
            platform_enums = [Platform.LINKEDIN, Platform.X_TWITTER]
        
        request = PostRequest(
            content=message,
            platforms=platform_enums,
            post_type=PostType.SCHEDULED,
            schedule_time=schedule_time
        )
        
        response = await self.poster.post(request)
        return response.request_id


# Example usage for testing
async def test_unified_interface():
    """Test the unified interface"""
    print("Testing Unified Social Media Interface")
    print("="*60)
    
    # Create DAE interface
    dae_interface = DAESocialInterface()
    
    # Test stream announcement
    print("\n[TEST] Stream Announcement")
    success = await dae_interface.announce_stream(
        title="Where is #Trump? #MAGA #ICEraids Move2Japan Show LIVE!",
        url="https://youtube.com/watch?v=PD-NYPQtEZ8"
    )
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")
    
    # Test general update
    print("\n[TEST] General Update")
    success = await dae_interface.post_update(
        "Testing the unified social media interface for DAE cubes!"
    )
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")
    
    print("\n" + "="*60)
    print("Test Complete")


if __name__ == "__main__":
    asyncio.run(test_unified_interface())