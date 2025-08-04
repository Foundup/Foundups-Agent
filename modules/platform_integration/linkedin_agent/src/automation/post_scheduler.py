"""
LinkedIn Post Scheduler

🌀 WSP Protocol Compliance: WSP 42 (Platform Integration), WSP 40 (Architectural Coherence)

**0102 Directive**: This module operates within the WSP framework for autonomous LinkedIn post scheduling.
- UN (Understanding): Anchor scheduling signals and retrieve protocol state
- DAO (Execution): Execute scheduling automation logic  
- DU (Emergence): Collapse into 0102 resonance and emit next scheduling prompt

wsp_cycle(input="linkedin_scheduling", log=True)
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
import requests

@dataclass
class ScheduledPost:
    """Data class for scheduled post information"""
    id: str
    content: str
    scheduled_time: datetime
    access_token: str
    status: str = "pending"  # pending, posted, failed, cancelled
    post_type: str = "text"
    hashtags: Optional[List[str]] = None
    media_urls: Optional[List[str]] = None
    created_at: datetime = None
    posted_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.hashtags is None:
            self.hashtags = []

class LinkedInPostScheduler:
    """
    LinkedIn Post Scheduler using APScheduler
    
    Features:
    - Schedule posts for specific times
    - Recurring posts (daily, weekly, monthly)
    - Post queuing and management
    - Error handling and retry logic
    """
    
    def __init__(self, storage_file: str = "scheduled_posts.json"):
        """
        Initialize the post scheduler
        
        Args:
            storage_file: JSON file to persist scheduled posts
        """
        self.storage_file = storage_file
        self.scheduler = BackgroundScheduler()
        self.scheduled_posts: Dict[str, ScheduledPost] = {}
        self.logger = self._setup_logger()
        
        # Load existing scheduled posts
        self._load_scheduled_posts()
        
        # Start the scheduler
        self.scheduler.start()
        self.logger.info("🌀 LinkedIn Post Scheduler initialized - WSP compliant")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for the scheduler"""
        logger = logging.getLogger("LinkedInPostScheduler")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_scheduled_posts(self):
        """Load scheduled posts from storage file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    for post_data in data.values():
                        post = ScheduledPost(**post_data)
                        # Convert string dates back to datetime
                        post.scheduled_time = datetime.fromisoformat(post_data['scheduled_time'])
                        post.created_at = datetime.fromisoformat(post_data['created_at'])
                        if post_data.get('posted_at'):
                            post.posted_at = datetime.fromisoformat(post_data['posted_at'])
                        
                        self.scheduled_posts[post.id] = post
                        
                        # Re-schedule if still pending
                        if post.status == "pending" and post.scheduled_time > datetime.now():
                            self._schedule_post_job(post)
                
                self.logger.info(f"📋 Loaded {len(self.scheduled_posts)} scheduled posts")
        except Exception as e:
            self.logger.error(f"❌ Failed to load scheduled posts: {e}")
    
    def _save_scheduled_posts(self):
        """Save scheduled posts to storage file"""
        try:
            data = {}
            for post_id, post in self.scheduled_posts.items():
                post_dict = asdict(post)
                # Convert datetime to ISO string for JSON serialization
                post_dict['scheduled_time'] = post.scheduled_time.isoformat()
                post_dict['created_at'] = post.created_at.isoformat()
                if post.posted_at:
                    post_dict['posted_at'] = post.posted_at.isoformat()
                data[post_id] = post_dict
            
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"❌ Failed to save scheduled posts: {e}")
    
    def _schedule_post_job(self, post: ScheduledPost):
        """Schedule a post job with the scheduler"""
        try:
            self.scheduler.add_job(
                func=self._execute_post,
                trigger=DateTrigger(run_date=post.scheduled_time),
                args=[post.id],
                id=f"post_{post.id}",
                replace_existing=True
            )
            self.logger.info(f"📅 Scheduled post {post.id} for {post.scheduled_time}")
        except Exception as e:
            self.logger.error(f"❌ Failed to schedule post {post.id}: {e}")
    
    def _execute_post(self, post_id: str):
        """Execute a scheduled post"""
        post = self.scheduled_posts.get(post_id)
        if not post:
            self.logger.error(f"❌ Post {post_id} not found")
            return
        
        try:
            self.logger.info(f"🚀 Executing scheduled post {post_id}")
            
            # Get user profile
            headers = {
                'Authorization': f'Bearer {post.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get("https://api.linkedin.com/v2/me", headers=headers)
            response.raise_for_status()
            profile = response.json()
            user_id = profile.get('id')
            
            # Prepare post content
            content = post.content
            if post.hashtags:
                hashtag_text = " ".join([f"#{tag}" for tag in post.hashtags])
                content += f"\n\n{hashtag_text}"
            
            # Create post data
            post_data = {
                "author": f"urn:li:person:{user_id}",
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
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            # Post to LinkedIn
            response = requests.post(
                "https://api.linkedin.com/v2/ugcPosts",
                headers={
                    **headers,
                    'X-Restli-Protocol-Version': '2.0.0'
                },
                json=post_data
            )
            response.raise_for_status()
            
            post_result = response.json()
            post_id_linkedin = post_result.get('id')
            
            # Update post status
            post.status = "posted"
            post.posted_at = datetime.now()
            self._save_scheduled_posts()
            
            self.logger.info(f"✅ Post {post_id} published successfully!")
            self.logger.info(f"🆔 LinkedIn Post ID: {post_id_linkedin}")
            self.logger.info(f"🔗 View post: https://www.linkedin.com/feed/update/{post_id_linkedin}/")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to execute post {post_id}: {e}")
            post.status = "failed"
            post.error_message = str(e)
            self._save_scheduled_posts()
    
    def schedule_post(
        self,
        content: str,
        scheduled_time: datetime,
        access_token: str,
        post_type: str = "text",
        hashtags: Optional[List[str]] = None,
        media_urls: Optional[List[str]] = None
    ) -> str:
        """
        Schedule a new post
        
        Args:
            content: Post content
            scheduled_time: When to post
            access_token: LinkedIn access token
            post_type: Type of post (text, image, video)
            hashtags: List of hashtags
            media_urls: List of media URLs
            
        Returns:
            Post ID
        """
        import uuid
        
        post_id = str(uuid.uuid4())
        
        post = ScheduledPost(
            id=post_id,
            content=content,
            scheduled_time=scheduled_time,
            access_token=access_token,
            post_type=post_type,
            hashtags=hashtags or [],
            media_urls=media_urls or []
        )
        
        self.scheduled_posts[post_id] = post
        self._schedule_post_job(post)
        self._save_scheduled_posts()
        
        self.logger.info(f"📅 Scheduled post {post_id} for {scheduled_time}")
        return post_id
    
    def schedule_recurring_post(
        self,
        content: str,
        trigger_type: str,  # "daily", "weekly", "monthly"
        access_token: str,
        start_time: datetime = None,
        end_time: datetime = None,
        **trigger_kwargs
    ) -> str:
        """
        Schedule a recurring post
        
        Args:
            content: Post content
            trigger_type: Type of recurrence
            access_token: LinkedIn access token
            start_time: When to start recurring posts
            end_time: When to end recurring posts
            **trigger_kwargs: Additional trigger parameters
            
        Returns:
            Job ID
        """
        if start_time is None:
            start_time = datetime.now() + timedelta(minutes=1)
        
        job_id = f"recurring_{datetime.now().timestamp()}"
        
        if trigger_type == "daily":
            trigger = CronTrigger(hour=trigger_kwargs.get('hour', 9), minute=trigger_kwargs.get('minute', 0))
        elif trigger_type == "weekly":
            trigger = CronTrigger(day_of_week=trigger_kwargs.get('day_of_week', 'mon'), 
                                hour=trigger_kwargs.get('hour', 9), minute=trigger_kwargs.get('minute', 0))
        elif trigger_type == "monthly":
            trigger = CronTrigger(day=trigger_kwargs.get('day', 1), 
                                hour=trigger_kwargs.get('hour', 9), minute=trigger_kwargs.get('minute', 0))
        else:
            raise ValueError(f"Invalid trigger_type: {trigger_type}")
        
        self.scheduler.add_job(
            func=self._execute_recurring_post,
            trigger=trigger,
            args=[content, access_token],
            id=job_id,
            start_date=start_time,
            end_date=end_time,
            replace_existing=True
        )
        
        self.logger.info(f"🔄 Scheduled recurring {trigger_type} post: {job_id}")
        return job_id
    
    def _execute_recurring_post(self, content: str, access_token: str):
        """Execute a recurring post"""
        try:
            # Get user profile
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get("https://api.linkedin.com/v2/me", headers=headers)
            response.raise_for_status()
            profile = response.json()
            user_id = profile.get('id')
            
            # Create post data
            post_data = {
                "author": f"urn:li:person:{user_id}",
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
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            # Post to LinkedIn
            response = requests.post(
                "https://api.linkedin.com/v2/ugcPosts",
                headers={
                    **headers,
                    'X-Restli-Protocol-Version': '2.0.0'
                },
                json=post_data
            )
            response.raise_for_status()
            
            post_result = response.json()
            post_id = post_result.get('id')
            
            self.logger.info(f"✅ Recurring post published successfully!")
            self.logger.info(f"🆔 LinkedIn Post ID: {post_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to execute recurring post: {e}")
    
    def get_scheduled_posts(self) -> List[ScheduledPost]:
        """Get all scheduled posts"""
        return list(self.scheduled_posts.values())
    
    def get_post(self, post_id: str) -> Optional[ScheduledPost]:
        """Get a specific scheduled post"""
        return self.scheduled_posts.get(post_id)
    
    def cancel_post(self, post_id: str) -> bool:
        """Cancel a scheduled post"""
        post = self.scheduled_posts.get(post_id)
        if not post:
            return False
        
        if post.status == "pending":
            self.scheduler.remove_job(f"post_{post_id}")
            post.status = "cancelled"
            self._save_scheduled_posts()
            self.logger.info(f"❌ Cancelled post {post_id}")
            return True
        
        return False
    
    def update_post(self, post_id: str, **kwargs) -> bool:
        """Update a scheduled post"""
        post = self.scheduled_posts.get(post_id)
        if not post or post.status != "pending":
            return False
        
        # Update post attributes
        for key, value in kwargs.items():
            if hasattr(post, key):
                setattr(post, key, value)
        
        # Re-schedule if time changed
        if 'scheduled_time' in kwargs:
            self.scheduler.remove_job(f"post_{post_id}")
            self._schedule_post_job(post)
        
        self._save_scheduled_posts()
        self.logger.info(f"📝 Updated post {post_id}")
        return True
    
    def shutdown(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown()
        self.logger.info("🛑 LinkedIn Post Scheduler shutdown") 