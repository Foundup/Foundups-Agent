"""
Scheduling Engine - Advanced scheduling with platform-specific optimizations
WSP Compliance: WSP 3, WSP 49
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
import pytz


@dataclass
class ScheduledPost:
    """Represents a scheduled social media post"""
    id: str
    content: str
    platforms: List[str]
    schedule_time: datetime
    options: Dict[str, Any]
    status: str  # pending, posted, failed, cancelled
    created_at: datetime
    posted_at: Optional[datetime] = None
    error_message: Optional[str] = None


class SchedulingEngine:
    """
    Advanced scheduling engine with platform-specific optimizations
    
    Provides intelligent scheduling, retry logic, and optimal posting
    times based on platform best practices and user engagement patterns.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Scheduling Engine
        
        Args:
            config: Configuration including timezone, retry settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize scheduler
        self.scheduler = AsyncIOScheduler(timezone=pytz.UTC)
        self.active_schedules: Dict[str, ScheduledPost] = {}
        self.post_history: List[ScheduledPost] = []
        
        # Platform-specific optimal posting times (UTC)
        self.optimal_times = {
            'twitter': [
                # Peak engagement times for Twitter
                {'hour': 9, 'minute': 0},   # 9 AM
                {'hour': 12, 'minute': 0},  # 12 PM  
                {'hour': 15, 'minute': 0},  # 3 PM
                {'hour': 18, 'minute': 0},  # 6 PM
            ],
            'linkedin': [
                # Peak engagement times for LinkedIn (business hours)
                {'hour': 8, 'minute': 0},   # 8 AM
                {'hour': 11, 'minute': 0},  # 11 AM
                {'hour': 14, 'minute': 0},  # 2 PM
                {'hour': 17, 'minute': 0},  # 5 PM
            ]
        }
        
        # Retry configuration
        self.retry_config = {
            'max_retries': config.get('max_retries', 3),
            'retry_delay': config.get('retry_delay', 300),  # 5 minutes
            'exponential_backoff': config.get('exponential_backoff', True)
        }
        
        self.initialized = False
        
    async def initialize(self) -> bool:
        """
        Initialize the scheduling engine
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.scheduler.start()
            self.initialized = True
            self.logger.info("Scheduling engine initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize scheduling engine: {e}")
            return False
            
    async def shutdown(self):
        """Gracefully shutdown the scheduling engine"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            self.logger.info("Scheduling engine shutdown complete")
            
    async def schedule_post(self, content: str, platforms: List[str], 
                          schedule_time: datetime, options: Dict[str, Any],
                          orchestrator) -> str:
        """
        Schedule a post for specific time
        
        Args:
            content: Content to post
            platforms: Target platforms
            schedule_time: When to post
            options: Additional options
            orchestrator: Reference to the orchestrator for posting
            
        Returns:
            str: Schedule ID
        """
        schedule_id = str(uuid.uuid4())
        
        # Create scheduled post record
        scheduled_post = ScheduledPost(
            id=schedule_id,
            content=content,
            platforms=platforms,
            schedule_time=schedule_time,
            options=options,
            status='pending',
            created_at=datetime.now(pytz.UTC)
        )
        
        # Store in active schedules
        self.active_schedules[schedule_id] = scheduled_post
        
        # Schedule the job
        self.scheduler.add_job(
            func=self._execute_scheduled_post,
            trigger=DateTrigger(run_date=schedule_time),
            args=[schedule_id, orchestrator],
            id=schedule_id,
            name=f"Social Media Post: {content[:50]}..."
        )
        
        self.logger.info(f"Scheduled post {schedule_id} for {schedule_time}")
        return schedule_id
        
    async def _execute_scheduled_post(self, schedule_id: str, orchestrator):
        """Execute a scheduled post"""
        if schedule_id not in self.active_schedules:
            self.logger.error(f"Scheduled post {schedule_id} not found")
            return
            
        scheduled_post = self.active_schedules[schedule_id]
        
        try:
            self.logger.info(f"Executing scheduled post {schedule_id}")
            
            # Post content using orchestrator
            result = await orchestrator.post_content(
                content=scheduled_post.content,
                platforms=scheduled_post.platforms,
                options=scheduled_post.options
            )
            
            # Check if all platforms succeeded
            all_success = all(platform_result['success'] for platform_result in result.values())
            
            if all_success:
                scheduled_post.status = 'posted'
                scheduled_post.posted_at = datetime.now(pytz.UTC)
                self.logger.info(f"Successfully posted scheduled content {schedule_id}")
            else:
                # Some platforms failed
                failed_platforms = [
                    platform for platform, platform_result in result.items()
                    if not platform_result['success']
                ]
                scheduled_post.status = 'partial_failure'
                scheduled_post.error_message = f"Failed platforms: {failed_platforms}"
                self.logger.warning(f"Partially failed scheduled post {schedule_id}: {failed_platforms}")
                
                # Schedule retry for failed platforms
                await self._schedule_retry(scheduled_post, failed_platforms, orchestrator)
                
        except Exception as e:
            scheduled_post.status = 'failed'
            scheduled_post.error_message = str(e)
            self.logger.error(f"Failed to execute scheduled post {schedule_id}: {e}")
            
            # Schedule retry
            await self._schedule_retry(scheduled_post, scheduled_post.platforms, orchestrator)
            
        finally:
            # Move to history and remove from active
            self.post_history.append(scheduled_post)
            if schedule_id in self.active_schedules:
                del self.active_schedules[schedule_id]
                
    async def _schedule_retry(self, scheduled_post: ScheduledPost, failed_platforms: List[str], 
                            orchestrator, retry_count: int = 1):
        """Schedule a retry for failed posts"""
        if retry_count > self.retry_config['max_retries']:
            self.logger.error(f"Max retries exceeded for post {scheduled_post.id}")
            return
            
        # Calculate retry delay with exponential backoff
        delay = self.retry_config['retry_delay']
        if self.retry_config['exponential_backoff']:
            delay *= (2 ** (retry_count - 1))
            
        retry_time = datetime.now(pytz.UTC) + timedelta(seconds=delay)
        retry_id = f"{scheduled_post.id}_retry_{retry_count}"
        
        # Create retry job
        self.scheduler.add_job(
            func=self._execute_retry,
            trigger=DateTrigger(run_date=retry_time),
            args=[scheduled_post.id, failed_platforms, orchestrator, retry_count],
            id=retry_id,
            name=f"Retry {retry_count}: {scheduled_post.content[:30]}..."
        )
        
        self.logger.info(f"Scheduled retry {retry_count} for post {scheduled_post.id} at {retry_time}")
        
    async def _execute_retry(self, original_id: str, failed_platforms: List[str], 
                           orchestrator, retry_count: int):
        """Execute a retry attempt"""
        # Find the original post in history
        original_post = None
        for post in self.post_history:
            if post.id == original_id:
                original_post = post
                break
                
        if not original_post:
            self.logger.error(f"Original post {original_id} not found for retry")
            return
            
        try:
            self.logger.info(f"Executing retry {retry_count} for post {original_id}")
            
            # Retry posting to failed platforms only
            result = await orchestrator.post_content(
                content=original_post.content,
                platforms=failed_platforms,
                options=original_post.options
            )
            
            # Check results
            still_failed = [
                platform for platform, platform_result in result.items()
                if not platform_result['success']
            ]
            
            if not still_failed:
                original_post.status = 'posted'
                original_post.posted_at = datetime.now(pytz.UTC)
                self.logger.info(f"Retry successful for post {original_id}")
            else:
                # Some platforms still failed, schedule another retry
                await self._schedule_retry(original_post, still_failed, orchestrator, retry_count + 1)
                
        except Exception as e:
            self.logger.error(f"Retry {retry_count} failed for post {original_id}: {e}")
            await self._schedule_retry(original_post, failed_platforms, orchestrator, retry_count + 1)
            
    def cancel_scheduled_post(self, schedule_id: str) -> bool:
        """
        Cancel a scheduled post
        
        Args:
            schedule_id: ID of scheduled post to cancel
            
        Returns:
            bool: True if cancelled successfully
        """
        try:
            # Remove from scheduler
            self.scheduler.remove_job(schedule_id)
            
            # Update status and move to history
            if schedule_id in self.active_schedules:
                scheduled_post = self.active_schedules[schedule_id]
                scheduled_post.status = 'cancelled'
                self.post_history.append(scheduled_post)
                del self.active_schedules[schedule_id]
                
            self.logger.info(f"Cancelled scheduled post {schedule_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cancel scheduled post {schedule_id}: {e}")
            return False
            
    def get_active_schedules(self) -> List[Dict[str, Any]]:
        """
        Get list of active scheduled posts
        
        Returns:
            List[Dict[str, Any]]: List of active schedules
        """
        return [
            {
                'id': post.id,
                'content': post.content[:100] + '...' if len(post.content) > 100 else post.content,
                'platforms': post.platforms,
                'schedule_time': post.schedule_time.isoformat(),
                'status': post.status,
                'created_at': post.created_at.isoformat()
            }
            for post in self.active_schedules.values()
        ]
        
    def get_post_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent post history
        
        Args:
            limit: Maximum number of posts to return
            
        Returns:
            List[Dict[str, Any]]: List of historical posts
        """
        recent_posts = sorted(self.post_history, key=lambda x: x.created_at, reverse=True)[:limit]
        
        return [
            {
                'id': post.id,
                'content': post.content[:100] + '...' if len(post.content) > 100 else post.content,
                'platforms': post.platforms,
                'schedule_time': post.schedule_time.isoformat(),
                'status': post.status,
                'created_at': post.created_at.isoformat(),
                'posted_at': post.posted_at.isoformat() if post.posted_at else None,
                'error_message': post.error_message
            }
            for post in recent_posts
        ]
        
    def get_active_count(self) -> int:
        """Get number of active scheduled posts"""
        return len(self.active_schedules)
        
    def suggest_optimal_time(self, platform: str, target_time: Optional[datetime] = None) -> datetime:
        """
        Suggest optimal posting time for a platform
        
        Args:
            platform: Platform identifier
            target_time: Desired posting time (will find nearest optimal)
            
        Returns:
            datetime: Suggested optimal posting time
        """
        if platform not in self.optimal_times:
            return target_time or datetime.now(pytz.UTC) + timedelta(hours=1)
            
        optimal_hours = self.optimal_times[platform]
        
        if not target_time:
            # Suggest next optimal time today or tomorrow
            now = datetime.now(pytz.UTC)
            today_options = []
            
            for time_slot in optimal_hours:
                suggested_time = now.replace(
                    hour=time_slot['hour'],
                    minute=time_slot['minute'],
                    second=0,
                    microsecond=0
                )
                
                if suggested_time > now + timedelta(minutes=30):  # At least 30 min in future
                    today_options.append(suggested_time)
                    
            if today_options:
                return min(today_options)  # Earliest today
            else:
                # Use first option tomorrow
                tomorrow = now + timedelta(days=1)
                first_slot = optimal_hours[0]
                return tomorrow.replace(
                    hour=first_slot['hour'],
                    minute=first_slot['minute'],
                    second=0,
                    microsecond=0
                )
        else:
            # Find nearest optimal time to target
            target_date = target_time.date()
            best_option = None
            min_difference = None
            
            for time_slot in optimal_hours:
                option_time = datetime.combine(
                    target_date,
                    datetime.min.time().replace(
                        hour=time_slot['hour'],
                        minute=time_slot['minute']
                    )
                ).replace(tzinfo=pytz.UTC)
                
                difference = abs((option_time - target_time).total_seconds())
                
                if min_difference is None or difference < min_difference:
                    min_difference = difference
                    best_option = option_time
                    
            return best_option
            
    def get_scheduling_stats(self) -> Dict[str, Any]:
        """
        Get scheduling statistics
        
        Returns:
            Dict[str, Any]: Scheduling statistics
        """
        total_posts = len(self.post_history)
        successful_posts = len([p for p in self.post_history if p.status == 'posted'])
        failed_posts = len([p for p in self.post_history if p.status == 'failed'])
        
        return {
            'active_schedules': len(self.active_schedules),
            'total_scheduled': total_posts,
            'successful_posts': successful_posts,
            'failed_posts': failed_posts,
            'success_rate': (successful_posts / total_posts * 100) if total_posts > 0 else 0,
            'scheduler_running': self.scheduler.running if hasattr(self.scheduler, 'running') else False
        }