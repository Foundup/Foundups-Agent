#!/usr/bin/env python3
"""
Human (012) Scheduling Interface for Social Media
WSP Compliant: Allows 012 humans to schedule posts while 0102 handles execution

This module provides scheduling capabilities for humans to queue posts
that will be executed by the autonomous system at specified times.
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

# Use existing orchestrator for actual posting
from .simple_posting_orchestrator import SimplePostingOrchestrator, Platform, PostResponse

logger = logging.getLogger(__name__)

class ScheduleType(Enum):
    """Types of scheduling"""
    ONCE = "once"  # Post once at specific time
    DAILY = "daily"  # Post every day at same time
    WEEKLY = "weekly"  # Post weekly on specific days
    STREAM_DETECT = "stream_detect"  # Post when stream detected

@dataclass
class ScheduledPost:
    """Scheduled post information"""
    id: str
    content: str
    platforms: List[str]
    scheduled_time: datetime
    schedule_type: ScheduleType
    created_by: str  # "012" or "0102"
    status: str = "pending"  # pending, posted, failed, cancelled
    metadata: Optional[Dict] = None
    created_at: datetime = None
    posted_at: Optional[datetime] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class HumanSchedulingInterface:
    """
    Interface for 012 humans to schedule social media posts.
    Works alongside 0102 autonomous posting.

    Features:
    - Schedule posts for specific times
    - Recurring posts (daily, weekly)
    - Stream-triggered posts
    - Vision-enhanced verification (future)
    - Manual override capabilities
    """

    def __init__(self):
        self.orchestrator = SimplePostingOrchestrator()
        self.schedule_file = "memory/012_scheduled_posts.json"
        self.scheduled_posts: Dict[str, ScheduledPost] = {}
        self.load_schedule()

        # Create memory directory if needed
        os.makedirs("memory", exist_ok=True)

        logger.info("[012 SCHEDULER] Human scheduling interface initialized")

    def load_schedule(self):
        """Load scheduled posts from file"""
        if os.path.exists(self.schedule_file):
            try:
                with open(self.schedule_file, 'r') as f:
                    data = json.load(f)
                    for post_id, post_data in data.items():
                        # Convert string times back to datetime
                        if 'scheduled_time' in post_data:
                            post_data['scheduled_time'] = datetime.fromisoformat(post_data['scheduled_time'])
                        if 'created_at' in post_data:
                            post_data['created_at'] = datetime.fromisoformat(post_data['created_at'])
                        if 'posted_at' in post_data and post_data['posted_at']:
                            post_data['posted_at'] = datetime.fromisoformat(post_data['posted_at'])

                        # Convert schedule_type string to enum
                        post_data['schedule_type'] = ScheduleType(post_data['schedule_type'])

                        self.scheduled_posts[post_id] = ScheduledPost(**post_data)

                logger.info(f"[012 SCHEDULER] Loaded {len(self.scheduled_posts)} scheduled posts")
            except Exception as e:
                logger.error(f"[012 SCHEDULER] Error loading schedule: {e}")

    def save_schedule(self):
        """Save scheduled posts to file"""
        try:
            # Convert to JSON-serializable format
            data = {}
            for post_id, post in self.scheduled_posts.items():
                post_dict = asdict(post)
                # Convert datetime objects to strings
                post_dict['scheduled_time'] = post.scheduled_time.isoformat()
                if post_dict['created_at']:
                    post_dict['created_at'] = post.created_at.isoformat()
                if post_dict['posted_at']:
                    post_dict['posted_at'] = post.posted_at.isoformat()
                # Convert enum to string
                post_dict['schedule_type'] = post.schedule_type.value
                data[post_id] = post_dict

            with open(self.schedule_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"[012 SCHEDULER] Saved {len(self.scheduled_posts)} scheduled posts")
        except Exception as e:
            logger.error(f"[012 SCHEDULER] Error saving schedule: {e}")

    def schedule_post(
        self,
        content: str,
        platforms: List[Platform],
        scheduled_time: datetime,
        schedule_type: ScheduleType = ScheduleType.ONCE,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Schedule a post for future publication.

        Args:
            content: Post content
            platforms: List of platforms to post to
            scheduled_time: When to post
            schedule_type: Type of schedule (once, daily, etc.)
            metadata: Additional metadata (stream info, etc.)

        Returns:
            Post ID for tracking
        """
        import uuid
        post_id = str(uuid.uuid4())[:8]

        scheduled_post = ScheduledPost(
            id=post_id,
            content=content,
            platforms=[p.value for p in platforms],
            scheduled_time=scheduled_time,
            schedule_type=schedule_type,
            created_by="012",
            metadata=metadata or {}
        )

        self.scheduled_posts[post_id] = scheduled_post
        self.save_schedule()

        logger.info(f"[012 SCHEDULER] Scheduled post {post_id} for {scheduled_time}")
        logger.info(f"[012 SCHEDULER] Platforms: {[p.value for p in platforms]}")
        logger.info(f"[012 SCHEDULER] Type: {schedule_type.value}")

        return post_id

    async def execute_scheduled_posts(self) -> List[Tuple[str, PostResponse]]:
        """
        Execute any posts that are due.
        Called by 0102 system periodically.

        Returns:
            List of (post_id, response) tuples
        """
        results = []
        now = datetime.now()

        for post_id, post in list(self.scheduled_posts.items()):
            if post.status == "pending" and post.scheduled_time <= now:
                logger.info(f"[012 SCHEDULER] Executing scheduled post {post_id}")

                # Convert platform strings back to Platform enums
                platforms = [Platform(p) for p in post.platforms]

                # Use orchestrator to post
                try:
                    # For stream posts, extract URL from metadata
                    if "stream_url" in post.metadata:
                        response = await self.orchestrator.post_stream_notification(
                            stream_title=post.metadata.get("stream_title", "Live Stream"),
                            stream_url=post.metadata["stream_url"],
                            platforms=platforms
                        )
                    else:
                        # For regular posts, need to implement in orchestrator
                        # For now, create a fake stream post
                        response = await self.orchestrator.post_stream_notification(
                            stream_title="Scheduled Post",
                            stream_url="https://youtube.com/watch?v=scheduled",
                            platforms=platforms
                        )

                    # Update post status
                    if response.failure_count == 0:
                        post.status = "posted"
                        post.posted_at = datetime.now()
                        logger.info(f"[012 SCHEDULER] Successfully posted {post_id}")
                    else:
                        post.status = "failed"
                        post.error_message = f"Failed on {response.failure_count} platforms"
                        logger.error(f"[012 SCHEDULER] Failed to post {post_id}")

                    results.append((post_id, response))

                    # Handle recurring posts
                    if post.status == "posted" and post.schedule_type != ScheduleType.ONCE:
                        self._reschedule_recurring_post(post)

                except Exception as e:
                    post.status = "failed"
                    post.error_message = str(e)
                    logger.error(f"[012 SCHEDULER] Error posting {post_id}: {e}")

        if results:
            self.save_schedule()

        return results

    def _reschedule_recurring_post(self, post: ScheduledPost):
        """Reschedule a recurring post"""
        import uuid

        if post.schedule_type == ScheduleType.DAILY:
            new_time = post.scheduled_time + timedelta(days=1)
        elif post.schedule_type == ScheduleType.WEEKLY:
            new_time = post.scheduled_time + timedelta(weeks=1)
        else:
            return  # Not a recurring post

        # Create new scheduled post
        new_id = str(uuid.uuid4())[:8]
        new_post = ScheduledPost(
            id=new_id,
            content=post.content,
            platforms=post.platforms,
            scheduled_time=new_time,
            schedule_type=post.schedule_type,
            created_by=post.created_by,
            metadata=post.metadata
        )

        self.scheduled_posts[new_id] = new_post
        logger.info(f"[012 SCHEDULER] Rescheduled recurring post as {new_id} for {new_time}")

    def get_scheduled_posts(self, status: Optional[str] = None) -> List[ScheduledPost]:
        """Get all scheduled posts, optionally filtered by status"""
        posts = list(self.scheduled_posts.values())
        if status:
            posts = [p for p in posts if p.status == status]
        return sorted(posts, key=lambda p: p.scheduled_time)

    def cancel_post(self, post_id: str) -> bool:
        """Cancel a scheduled post"""
        if post_id in self.scheduled_posts:
            self.scheduled_posts[post_id].status = "cancelled"
            self.save_schedule()
            logger.info(f"[012 SCHEDULER] Cancelled post {post_id}")
            return True
        return False

    def update_post(self, post_id: str, **kwargs) -> bool:
        """Update a scheduled post"""
        if post_id in self.scheduled_posts:
            post = self.scheduled_posts[post_id]
            for key, value in kwargs.items():
                if hasattr(post, key):
                    setattr(post, key, value)
            self.save_schedule()
            logger.info(f"[012 SCHEDULER] Updated post {post_id}")
            return True
        return False

# CLI Interface for 012 humans
def main():
    """Command line interface for 012 scheduling"""
    import argparse

    parser = argparse.ArgumentParser(description="012 Human Social Media Scheduler")
    parser.add_argument("action", choices=["schedule", "list", "cancel", "execute"])
    parser.add_argument("--content", help="Post content")
    parser.add_argument("--platforms", nargs="+", default=["linkedin", "x_twitter"])
    parser.add_argument("--time", help="Schedule time (ISO format or 'now+X' where X is minutes)")
    parser.add_argument("--type", default="once", choices=["once", "daily", "weekly"])
    parser.add_argument("--id", help="Post ID for cancel/update")
    parser.add_argument("--status", help="Filter by status for list")

    args = parser.parse_args()
    scheduler = HumanSchedulingInterface()

    if args.action == "schedule":
        # Parse time
        if args.time and args.time.startswith("now+"):
            minutes = int(args.time[4:])
            scheduled_time = datetime.now() + timedelta(minutes=minutes)
        elif args.time:
            scheduled_time = datetime.fromisoformat(args.time)
        else:
            scheduled_time = datetime.now() + timedelta(minutes=5)

        # Convert platforms
        platforms = [Platform(p) for p in args.platforms]

        post_id = scheduler.schedule_post(
            content=args.content or "Test scheduled post from 012",
            platforms=platforms,
            scheduled_time=scheduled_time,
            schedule_type=ScheduleType(args.type)
        )

        print(f"✅ Scheduled post {post_id} for {scheduled_time}")
        print(f"   Platforms: {args.platforms}")
        print(f"   Type: {args.type}")

    elif args.action == "list":
        posts = scheduler.get_scheduled_posts(status=args.status)
        print(f"\n📅 Scheduled Posts ({len(posts)} total):")
        print("-" * 60)
        for post in posts:
            print(f"ID: {post.id}")
            print(f"   Time: {post.scheduled_time}")
            print(f"   Platforms: {post.platforms}")
            print(f"   Status: {post.status}")
            print(f"   Type: {post.schedule_type.value}")
            print(f"   Content: {post.content[:50]}...")
            print("-" * 60)

    elif args.action == "cancel":
        if scheduler.cancel_post(args.id):
            print(f"✅ Cancelled post {args.id}")
        else:
            print(f"❌ Post {args.id} not found")

    elif args.action == "execute":
        # Execute pending posts (usually called by 0102 system)
        print("🚀 Executing pending posts...")
        results = asyncio.run(scheduler.execute_scheduled_posts())
        for post_id, response in results:
            print(f"   {post_id}: {'✅' if response.failure_count == 0 else '❌'}")

if __name__ == "__main__":
    main()