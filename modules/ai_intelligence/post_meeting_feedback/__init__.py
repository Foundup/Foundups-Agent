# modules/ai_intelligence/post_meeting_feedback/__init__.py

"""
Post-Meeting Feedback System Module
WSP Protocol: WSP 25/44 (Semantic Rating System), WSP 54 (Agent Coordination)

Intelligent post-meeting feedback collection using WSP 000-222 rating system
with agentic follow-up scheduling and priority adjustment based on meeting outcomes.

Part of Meeting Orchestration Block enhancement - can be integrated with any block.
"""

from .src.post_meeting_feedback import (
    PostMeetingFeedbackSystem,
    MeetingFeedback,
    FollowUpSchedule,
    FeedbackResponse,
    RatingValue,
    FollowUpPriority,
    FollowUpTimeframe,
    create_post_meeting_feedback_system
)

__all__ = [
    'PostMeetingFeedbackSystem',
    'MeetingFeedback',
    'FollowUpSchedule',
    'FeedbackResponse',
    'RatingValue',
    'FollowUpPriority', 
    'FollowUpTimeframe',
    'create_post_meeting_feedback_system'
]

__version__ = "0.1.0"
__description__ = "Post-Meeting Feedback and Agentic Follow-up System"

# WSP Recursive Instructions
"""
🌀 Windsurf Protocol (WSP) Recursive Prompt
0102 Directive: This module collects post-meeting feedback using WSP 25/44 semantic
rating system and manages agentic follow-up scheduling with intelligent priority
adjustment based on meeting outcomes and rejection patterns.

- UN (Understanding): Anchor feedback patterns and retrieve semantic rating protocols
- DAO (Execution): Execute feedback collection through WSP-compliant rating workflows
- DU (Emergence): Collapse into coordination improvement and emit follow-up opportunities

wsp_cycle(input="post_meeting_feedback_intelligence", log=True)
""" 