"""
Priority Scorer Module - Meeting Priority Assessment with Gamification

Public API for 000-222 emoji scale priority scoring with urgency factors.
Extracted from auto_meeting_orchestrator strategic decomposition.
"""

from .src.priority_scorer import (
    PriorityScorer,
    PriorityScore,
    ScoringContext,
    Priority,
    MeetingType,
    score_meeting_intent,
    create_priority_queue
)

__all__ = [
    'PriorityScorer',
    'PriorityScore',
    'ScoringContext',
    'Priority',
    'MeetingType',
    'score_meeting_intent',
    'create_priority_queue'
]

# Module metadata
__version__ = "0.1.0"
__domain__ = "gamification"
__purpose__ = "Meeting priority assessment and scoring with 000-222 emoji scale gamification" 