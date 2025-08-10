"""
LinkedIn Scheduler - Core Implementation
Enhanced with LinkedIn API v2 Integration
"""

import logging
import requests
import json
import os
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime, timedelta
from urllib.parse import urlencode
import time

logger = logging.getLogger(__name__)


class LinkedInAPIError(Exception):
    """Custom exception for LinkedIn API errors"""
    pass


class LinkedInScheduler:
    """
    LinkedIn post scheduling system with LinkedIn API v2 integration
    
    Supports OAuth 2.0 authentication and UGC Posts API for automated posting.
    Designed for 012 observer → 0102 executor delegation workflow.
    """
    
    # LinkedIn API Configuration
    API_BASE_URL = "https://api.linkedin.com/v2"
    UGC_POSTS_ENDPOINT = f"{API_BASE_URL}/ugcPosts"
    ASSETS_ENDPOINT = f"{API_BASE_URL}/assets"
    
    # Rate limits per LinkedIn documentation
    RATE_LIMITS = {
        'member_daily': 150,      # Per member per day (UTC)
        'app_daily': 100000,      # Per application per day (UTC)
        'posts_per_hour': 10,     # Conservative estimate for scheduling
    }
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """
        Initialize LinkedIn Scheduler
        
        Args:
            client_id: LinkedIn application client ID (or from LINKEDIN_CLIENT_ID env var)
            client_secret: LinkedIn application client secret (or from LINKEDIN_CLIENT_SECRET env var)
        """
        # Use provided credentials or fall back to environment variables
        self.client_id = client_id or os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('LINKEDIN_CLIENT_SECRET')
        
        # Validate credentials
        if not self.client_id or not self.client_secret:
            logger.warning("LinkedIn API credentials not found. Set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET environment variables.")
        
        self.access_tokens = {}  # Profile ID -> access token mapping
        self.authenticated_profiles = set()
        
        # Request session with common headers
        self.session = requests.Session()
        self.session.headers.update({
            'X-Restli-Protocol-Version': '2.0.0',
            'Content-Type': 'application/json'
        })
        
        logger.info(f"LinkedInScheduler initialized with API integration")
        if self.client_id:
            logger.info(f"Using LinkedIn Client ID: {self.client_id[:8]}..." if len(self.client_id) > 8 else self.client_id)
    
    def get_oauth_url(self, redirect_uri: str, state: Optional[str] = None) -> str:
        """
        Generate OAuth 2.0 authorization URL for LinkedIn
        
        Args:
            redirect_uri: Callback URL after authorization
            state: Optional state parameter for security
            
        Returns:
            str: Authorization URL for user to visit
        """
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'scope': 'w_member_social',  # Required scope for posting
        }
        
        if state:
            params['state'] = state
            
        auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"
        logger.info(f"Generated OAuth URL for LinkedIn authorization")
        return auth_url
    
    def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from LinkedIn callback
            redirect_uri: Same redirect URI used in authorization
            
        Returns:
            Dict containing access token and metadata
        """
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            logger.info("Successfully exchanged authorization code for access token")
            return token_data
            
        except requests.RequestException as e:
            logger.error(f"Failed to exchange code for token: {e}")
            raise LinkedInAPIError(f"Token exchange failed: {e}")
    
    def authenticate_profile(self, profile_id: str, access_token: str) -> bool:
        """
        Authenticate a LinkedIn profile with access token
        
        Args:
            profile_id: LinkedIn profile identifier (Person URN)
            access_token: OAuth 2.0 access token
            
        Returns:
            bool: Authentication success status
        """
        try:
            # Store access token for this profile
            self.access_tokens[profile_id] = access_token
            
            # Validate token by making a test request
            headers = {'Authorization': f'Bearer {access_token}'}
            test_url = f"{self.API_BASE_URL}/people/~"
            
            response = self.session.get(test_url, headers=headers)
            response.raise_for_status()
            
            self.authenticated_profiles.add(profile_id)
            logger.info(f"Successfully authenticated profile {profile_id}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Authentication failed for profile {profile_id}: {e}")
            return False
    
    def create_text_post(self, profile_id: str, content: str, 
                        visibility: Literal["PUBLIC", "CONNECTIONS"] = "PUBLIC") -> Dict[str, Any]:
        """
        Create a text-only LinkedIn post
        
        Args:
            profile_id: LinkedIn profile identifier (Person URN)
            content: Post content text
            visibility: Post visibility (PUBLIC or CONNECTIONS)
            
        Returns:
            Dict containing post creation result
        """
        if profile_id not in self.authenticated_profiles:
            raise LinkedInAPIError(f"Profile {profile_id} not authenticated")
        
        # Validate content length (LinkedIn limit)
        if len(content) > 3000:
            raise LinkedInAPIError("Content exceeds LinkedIn 3000 character limit")
        
        post_data = {
            "author": profile_id,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }
        
        try:
            headers = {'Authorization': f'Bearer {self.access_tokens[profile_id]}'}
            response = self.session.post(
                self.UGC_POSTS_ENDPOINT, 
                json=post_data, 
                headers=headers
            )
            response.raise_for_status()
            
            # Extract post ID from response header
            post_id = response.headers.get('X-RestLi-Id')
            
            result = {
                'success': True,
                'post_id': post_id,
                'profile_id': profile_id,
                'content_preview': content[:100] + '...' if len(content) > 100 else content,
                'visibility': visibility,
                'created_at': datetime.now().isoformat()
            }
            
            logger.info(f"Successfully created text post for profile {profile_id}")
            return result
            
        except requests.RequestException as e:
            logger.error(f"Failed to create post for profile {profile_id}: {e}")
            raise LinkedInAPIError(f"Post creation failed: {e}")
    
    def create_article_post(self, profile_id: str, content: str, article_url: str,
                           title: Optional[str] = None, description: Optional[str] = None,
                           visibility: Literal["PUBLIC", "CONNECTIONS"] = "PUBLIC") -> Dict[str, Any]:
        """
        Create a LinkedIn post with article/URL attachment
        
        Args:
            profile_id: LinkedIn profile identifier (Person URN)
            content: Post commentary text
            article_url: URL to attach to the post
            title: Optional title for the article
            description: Optional description for the article
            visibility: Post visibility (PUBLIC or CONNECTIONS)
            
        Returns:
            Dict containing post creation result
        """
        if profile_id not in self.authenticated_profiles:
            raise LinkedInAPIError(f"Profile {profile_id} not authenticated")
        
        media_data = {
            "status": "READY",
            "originalUrl": article_url
        }
        
        if title:
            media_data["title"] = {"text": title}
        if description:
            media_data["description"] = {"text": description}
        
        post_data = {
            "author": profile_id,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "ARTICLE",
                    "media": [media_data]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }
        
        try:
            headers = {'Authorization': f'Bearer {self.access_tokens[profile_id]}'}
            response = self.session.post(
                self.UGC_POSTS_ENDPOINT, 
                json=post_data, 
                headers=headers
            )
            response.raise_for_status()
            
            post_id = response.headers.get('X-RestLi-Id')
            
            result = {
                'success': True,
                'post_id': post_id,
                'profile_id': profile_id,
                'content_preview': content[:100] + '...' if len(content) > 100 else content,
                'article_url': article_url,
                'visibility': visibility,
                'created_at': datetime.now().isoformat()
            }
            
            logger.info(f"Successfully created article post for profile {profile_id}")
            return result
            
        except requests.RequestException as e:
            logger.error(f"Failed to create article post for profile {profile_id}: {e}")
            raise LinkedInAPIError(f"Article post creation failed: {e}")
    
    def check_rate_limits(self, profile_id: str) -> Dict[str, Any]:
        """
        Check current rate limit status for a profile
        
        Args:
            profile_id: LinkedIn profile identifier
            
        Returns:
            Dict containing rate limit information
        """
        # Note: LinkedIn doesn't provide a rate limit checking endpoint
        # This is a placeholder for internal rate limiting logic
        
        return {
            'member_daily_limit': self.RATE_LIMITS['member_daily'],
            'app_daily_limit': self.RATE_LIMITS['app_daily'],
            'estimated_remaining': 'Unknown',  # Would need internal tracking
            'reset_time': 'Next UTC midnight'
        }
    
    def validate_connection(self) -> bool:
        """
        Validate LinkedIn API connection and authentication
        
        Returns:
            bool: Connection status
        """
        try:
            # Test basic API connectivity
            response = self.session.get(f"{self.API_BASE_URL}/people/~:(id)")
            
            # 401 is expected without auth - means API is reachable
            if response.status_code in [200, 401]:
                logger.info("LinkedIn API connection validated")
                return True
            else:
                logger.error(f"LinkedIn API connection failed: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"LinkedIn API connection test failed: {e}")
            return False


class PostQueue:
    """
    Enhanced post queue management with LinkedIn API integration
    
    Manages scheduled LinkedIn posts with rate limiting and retry logic
    """
    
    def __init__(self, scheduler: LinkedInScheduler):
        """
        Initialize post queue with scheduler instance
        
        Args:
            scheduler: LinkedInScheduler instance for API operations
        """
        self.scheduler = scheduler
        self.queue = []
        self.processed = []
        self.failed = []
        
    def add_post(self, profile_id: str, content: str, schedule_time: datetime,
                 post_type: Literal["text", "article"] = "text",
                 article_url: Optional[str] = None,
                 title: Optional[str] = None,
                 description: Optional[str] = None,
                 visibility: Literal["PUBLIC", "CONNECTIONS"] = "PUBLIC") -> str:
        """
        Add post to scheduling queue
        
        Args:
            profile_id: LinkedIn profile identifier
            content: Post content
            schedule_time: When to publish
            post_type: Type of post (text or article)
            article_url: URL for article posts
            title: Title for article posts
            description: Description for article posts
            visibility: Post visibility
            
        Returns:
            str: Unique post ID for tracking
        """
        post_id = f"post_{len(self.queue)}_{int(datetime.now().timestamp())}"
        
        post_entry = {
            'id': post_id,
            'profile_id': profile_id,
            'content': content,
            'schedule_time': schedule_time,
            'post_type': post_type,
            'article_url': article_url,
            'title': title,
            'description': description,
            'visibility': visibility,
            'status': 'queued',
            'created_at': datetime.now(),
            'retry_count': 0,
            'max_retries': 3
        }
        
        self.queue.append(post_entry)
        logger.info(f"Added {post_type} post {post_id} to queue for profile {profile_id}")
        
        return post_id
    
    def process_pending_posts(self) -> List[Dict[str, Any]]:
        """
        Process all posts ready for publishing
        
        Returns:
            List of processing results
        """
        now = datetime.now()
        pending = [
            post for post in self.queue 
            if post['schedule_time'] <= now and post['status'] == 'queued'
        ]
        
        results = []
        for post in pending:
            try:
                if post['post_type'] == 'text':
                    result = self.scheduler.create_text_post(
                        post['profile_id'],
                        post['content'],
                        post['visibility']
                    )
                elif post['post_type'] == 'article':
                    result = self.scheduler.create_article_post(
                        post['profile_id'],
                        post['content'],
                        post['article_url'],
                        post['title'],
                        post['description'],
                        post['visibility']
                    )
                else:
                    raise ValueError(f"Unknown post type: {post['post_type']}")
                
                # Mark as successful
                post['status'] = 'processed'
                post['processed_at'] = datetime.now()
                post['api_result'] = result
                self.processed.append(post)
                
                results.append({
                    'post_id': post['id'],
                    'success': True,
                    'api_result': result
                })
                
                logger.info(f"Successfully processed post {post['id']}")
                
            except Exception as e:
                # Handle failures with retry logic
                post['retry_count'] += 1
                
                if post['retry_count'] >= post['max_retries']:
                    post['status'] = 'failed'
                    post['error'] = str(e)
                    self.failed.append(post)
                    logger.error(f"Post {post['id']} failed permanently: {e}")
                else:
                    # Retry later (exponential backoff)
                    retry_delay = 2 ** post['retry_count']  # 2, 4, 8 seconds
                    post['schedule_time'] = datetime.now() + timedelta(seconds=retry_delay)
                    logger.warning(f"Post {post['id']} failed, retry {post['retry_count']}/{post['max_retries']}: {e}")
                
                results.append({
                    'post_id': post['id'],
                    'success': False,
                    'error': str(e),
                    'retry_count': post['retry_count']
                })
        
        return results
    
    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get current queue status and statistics
        
        Returns:
            Dict containing queue statistics
        """
        return {
            'queued': len([p for p in self.queue if p['status'] == 'queued']),
            'processed': len(self.processed),
            'failed': len(self.failed),
            'total': len(self.queue),
            'next_scheduled': min(
                [p['schedule_time'] for p in self.queue if p['status'] == 'queued'],
                default=None
            )
        }
