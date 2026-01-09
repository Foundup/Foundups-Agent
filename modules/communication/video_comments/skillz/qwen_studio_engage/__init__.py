"""
Qwen Studio Engage Skill - Autonomous YouTube Studio Comment Engagement

This skill autonomously monitors YouTube Studio comments and engages
(like/reply/heart) based on Qwen sentiment analysis and Gemma validation.

Usage:
    from modules.communication.video_comments.skillz.qwen_studio_engage import execute_skill

    result = await execute_skill(
        channel_id="UC-LSSlOZwpGIRIYihaz8zCw",
        max_comments_to_check=5,
        engagement_policy={
            "like_threshold": 0.7,
            "reply_threshold": 0.8,
        }
    )
"""

from .executor import execute_skill

__all__ = ['execute_skill']
