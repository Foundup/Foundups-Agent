"""
WSP 96 Skill Package: tars_like_heart_reply

This package is intentionally importable so WRE and tests can reference:
- modules.communication.video_comments.skillz.tars_like_heart_reply
"""

from .comment_engagement_dae import CommentEngagementDAE, execute_skill

__all__ = ["CommentEngagementDAE", "execute_skill"]

