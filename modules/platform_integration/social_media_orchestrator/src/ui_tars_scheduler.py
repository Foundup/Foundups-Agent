# -*- coding: utf-8 -*-
"""
UI-TARS LinkedIn Scheduler Integration
Provides scheduling interface for LinkedIn posts using UI-TARS automation.

WSP 77: Agent Coordination Protocol
WSP 90: UTF-8 Enforcement
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# UI-TARS paths
UI_TARS_BASE = Path("E:/HoloIndex/models/ui-tars-1.5")
UI_TARS_INBOX = UI_TARS_BASE / "telemetry"
UI_TARS_INBOX.mkdir(parents=True, exist_ok=True)

@dataclass
class ScheduledPost:
    """Represents a scheduled LinkedIn post"""
    content: str
    scheduled_time: datetime
    content_type: str
    company_page: str
    draft_hash: str
    metadata: Dict[str, Any]
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'content': self.content,
            'scheduled_time': self.scheduled_time.isoformat(),
            'content_type': self.content_type,
            'company_page': self.company_page,
            'draft_hash': self.draft_hash,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScheduledPost':
        """Create from dictionary"""
        return cls(
            content=data['content'],
            scheduled_time=datetime.fromisoformat(data['scheduled_time']),
            content_type=data['content_type'],
            company_page=data['company_page'],
            draft_hash=data['draft_hash'],
            metadata=data.get('metadata', {}),
            created_at=datetime.fromisoformat(data['created_at'])
        )


class UITarsScheduler:
    """
    UI-TARS integration for LinkedIn post scheduling.

    When AI Overseer (Qwen/Gemma) is unavailable, this provides
    a delegation pipeline using external AI services with UI-TARS
    automation for actual scheduling.
    """

    def __init__(self):
        self.inbox_file = UI_TARS_INBOX / "linkedin_scheduled_posts.json"
        self.history_file = UI_TARS_INBOX / "scheduling_history.jsonl"
        self._ensure_files()

    def _ensure_files(self):
        """Ensure required files exist"""
        if not self.inbox_file.exists():
            with open(self.inbox_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)

        if not self.history_file.exists():
            self.history_file.touch()

    def schedule_linkedin_post(self, post: ScheduledPost) -> bool:
        """
        Schedule a LinkedIn post using UI-TARS automation.

        Args:
            post: ScheduledPost object with content and timing

        Returns:
            bool: Success status
        """
        try:
            # Load existing scheduled posts
            scheduled_posts = self._load_scheduled_posts()

            # Check for duplicates
            for existing in scheduled_posts:
                if existing.draft_hash == post.draft_hash:
                    logger.warning(f"Draft {post.draft_hash} already scheduled")
                    return False

            # Add new post
            scheduled_posts.append(post)
            self._save_scheduled_posts(scheduled_posts)

            # Log to history
            self._log_scheduling_action("scheduled", post)

            # Create UI-TARS instruction file
            self._create_ui_tars_instruction(post)

            logger.info(f"Scheduled LinkedIn post for {post.scheduled_time}")
            return True

        except Exception as e:
            logger.error(f"Failed to schedule LinkedIn post: {e}")
            return False

    def get_scheduled_posts(self) -> List[ScheduledPost]:
        """Get all scheduled posts"""
        return self._load_scheduled_posts()

    def cancel_scheduled_post(self, draft_hash: str) -> bool:
        """
        Cancel a scheduled post by draft hash.

        Args:
            draft_hash: Unique identifier of the draft to cancel

        Returns:
            bool: Success status
        """
        try:
            scheduled_posts = self._load_scheduled_posts()
            original_count = len(scheduled_posts)

            # Remove matching posts
            scheduled_posts = [p for p in scheduled_posts if p.draft_hash != draft_hash]

            if len(scheduled_posts) < original_count:
                self._save_scheduled_posts(scheduled_posts)
                # Log cancellation
                cancelled_post = ScheduledPost(
                    content="",
                    scheduled_time=datetime.now(),
                    content_type="cancelled",
                    company_page="",
                    draft_hash=draft_hash,
                    metadata={"cancelled": True}
                )
                self._log_scheduling_action("cancelled", cancelled_post)
                logger.info(f"Cancelled scheduled post {draft_hash}")
                return True
            else:
                logger.warning(f"No scheduled post found with hash {draft_hash}")
                return False

        except Exception as e:
            logger.error(f"Failed to cancel scheduled post: {e}")
            return False

    def _load_scheduled_posts(self) -> List[ScheduledPost]:
        """Load scheduled posts from file"""
        try:
            with open(self.inbox_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [ScheduledPost.from_dict(item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_scheduled_posts(self, posts: List[ScheduledPost]):
        """Save scheduled posts to file"""
        data = [post.to_dict() for post in posts]
        with open(self.inbox_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _log_scheduling_action(self, action: str, post: ScheduledPost):
        """Log scheduling action to history"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'draft_hash': post.draft_hash,
            'scheduled_time': post.scheduled_time.isoformat() if hasattr(post, 'scheduled_time') else None,
            'content_type': getattr(post, 'content_type', ''),
            'company_page': getattr(post, 'company_page', ''),
            'content_preview': post.content[:100] + '...' if len(post.content) > 100 else post.content
        }

        with open(self.history_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

    def _create_ui_tars_instruction(self, post: ScheduledPost):
        """
        Create UI-TARS instruction file for automation.

        This creates a JSON instruction file that UI-TARS can read
        to automate the LinkedIn scheduling process.
        """
        # Use instance variable instead of global constant for testability
        inbox_dir = self.ui_tars_inbox or UI_TARS_INBOX
        instruction_file = inbox_dir / f"schedule_{post.draft_hash}.json"

        instruction = {
            'action': 'schedule_linkedin_post',
            'draft_hash': post.draft_hash,
            'scheduled_time': post.scheduled_time.isoformat(),
            'content': post.content,
            'company_page': post.company_page,
            'content_type': post.content_type,
            'metadata': post.metadata,
            'created_at': post.created_at.isoformat(),
            'ui_instructions': {
                'platform': 'linkedin',
                'action': 'schedule_post',
                'steps': [
                    'Navigate to LinkedIn compose',
                    'Paste content',
                    'Set schedule time',
                    'Click schedule button',
                    'Verify scheduling confirmation'
                ]
            }
        }

        with open(instruction_file, 'w', encoding='utf-8') as f:
            json.dump(instruction, f, indent=2, ensure_ascii=False)

        logger.debug(f"Created UI-TARS instruction file: {instruction_file}")


# Global singleton for thread safety
_scheduler_instance = None

def get_ui_tars_scheduler() -> UITarsScheduler:
    """Get singleton UI-TARS scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = UITarsScheduler()
    return _scheduler_instance


if __name__ == "__main__":
    # CLI testing
    import argparse

    parser = argparse.ArgumentParser(description="UI-TARS LinkedIn Scheduler")
    parser.add_argument("--action", choices=["schedule", "list", "cancel"], required=True)
    parser.add_argument("--draft-hash", help="Draft hash for cancel action")
    parser.add_argument("--content", help="Post content for schedule action")
    parser.add_argument("--delay-hours", type=int, default=24, help="Hours to delay scheduling")

    args = parser.parse_args()

    scheduler = get_ui_tars_scheduler()

    if args.action == "list":
        posts = scheduler.get_scheduled_posts()
        print(f"Scheduled posts: {len(posts)}")
        for post in posts:
            print(f"  {post.draft_hash}: {post.scheduled_time} - {post.content[:50]}...")

    elif args.action == "schedule" and args.content:
        scheduled_time = datetime.now() + timedelta(hours=args.delay_hours)
        post = ScheduledPost(
            content=args.content,
            scheduled_time=scheduled_time,
            content_type="test",
            company_page="foundups",
            draft_hash=f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            metadata={"source": "cli_test"}
        )

        success = scheduler.schedule_linkedin_post(post)
        print(f"Scheduling {'successful' if success else 'failed'}")

    elif args.action == "cancel" and args.draft_hash:
        success = scheduler.cancel_scheduled_post(args.draft_hash)
        print(f"Cancellation {'successful' if success else 'failed'}")
