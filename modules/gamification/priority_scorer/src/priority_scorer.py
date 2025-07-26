"""
WSP 15: Priority Scorer Implementation
======================================

Meeting priority assessment and scoring with 000-222 emoji scale gamification.
Extracted from auto_meeting_orchestrator PoC for strategic decomposition.

WSP Integration:
- WSP 3: Gamification domain for engagement mechanics and behavioral systems
- WSP 11: Clean interface definition for modular consumption
- WSP 15: Module prioritization scoring system integration
- WSP 49: Standard module structure compliance
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import math

# WRE Integration
try:
    from ...wre_core.src.utils.wre_logger import wre_log
except ImportError:
    def wre_log(msg: str, level: str = "INFO"):
        print(f"[{level}] {msg}")

logger = logging.getLogger(__name__)


class Priority(Enum):
    """Base priority levels with numeric scoring"""
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    URGENT = 3
    
    def get_base_score(self) -> int:
        """Get base numeric score"""
        return self.value


class MeetingType(Enum):
    """Meeting types with context weighting factors"""
    GENERAL = "general"
    BRAINSTORM = "brainstorm"
    DECISION = "decision"
    UPDATE = "update"
    REVIEW = "review"
    EMERGENCY = "emergency"
    
    def get_context_weight(self) -> float:
        """Get context weighting factor"""
        weights = {
            MeetingType.GENERAL: 1.0,
            MeetingType.BRAINSTORM: 1.1,
            MeetingType.UPDATE: 0.9,
            MeetingType.REVIEW: 1.0,
            MeetingType.DECISION: 1.3,
            MeetingType.EMERGENCY: 1.8
        }
        return weights[self]


@dataclass
class PriorityScore:
    """Comprehensive priority score with gamification elements"""
    base_priority: int  # 0-3 scale
    urgency_factor: float  # 1.0-2.0 multiplier
    context_weight: float  # Meeting type weighting
    time_pressure: float  # Deadline proximity factor
    final_score: float  # Calculated composite score
    emoji_representation: str  # 000-222 visual scale
    confidence: float = 1.0  # Scoring confidence
    
    def get_ranking_value(self) -> float:
        """Get final ranking value for comparison"""
        return self.final_score * self.confidence


@dataclass
class ScoringContext:
    """Context data for priority scoring calculations"""
    meeting_type: MeetingType
    duration_minutes: int
    participant_count: int
    deadline: Optional[datetime] = None
    importance_keywords: List[str] = None
    requester_urgency: float = 1.0
    
    def __post_init__(self):
        if self.importance_keywords is None:
            self.importance_keywords = []


class PriorityScorer:
    """
    Meeting priority assessment and scoring engine with gamification.
    
    Calculates multi-factor priority scores using 000-222 emoji scale,
    urgency factors, and contextual weighting for engagement mechanics.
    """
    
    def __init__(self):
        # Emoji scale mapping
        self.emoji_scale = {
            0: "🥱",  # Lowest priority
            1: "😐",  # Medium-low
            2: "🔥",  # High priority
            3: "⚡"   # Urgent/Critical
        }
        
        # Importance keyword weights
        self.importance_keywords = {
            "urgent": 1.5,
            "critical": 1.8,
            "emergency": 2.0,
            "asap": 1.6,
            "important": 1.2,
            "deadline": 1.4,
            "decision": 1.3,
            "approval": 1.2,
            "crisis": 2.0,
            "blocker": 1.7
        }
        
        wre_log("PriorityScorer initialized with 000-222 emoji scale")
    
    def score_intent(self, base_priority: Priority, context: ScoringContext) -> PriorityScore:
        """
        Calculate comprehensive priority score for a meeting intent.
        
        Args:
            base_priority: Base priority level
            context: Scoring context with meeting details
            
        Returns:
            PriorityScore with all scoring factors
        """
        # Base score from priority level
        base_score = base_priority.get_base_score()
        
        # Calculate component factors
        urgency_factor = self.calculate_urgency_factor(context)
        context_weight = context.meeting_type.get_context_weight()
        time_pressure = self._calculate_time_pressure(context)
        keyword_boost = self._calculate_keyword_boost(context)
        
        # Composite score calculation
        weighted_score = base_score * context_weight
        urgency_adjusted = weighted_score * urgency_factor
        time_adjusted = urgency_adjusted * time_pressure
        final_score = time_adjusted * keyword_boost
        
        # Generate emoji representation
        emoji_rep = self._generate_emoji_representation(final_score)
        
        # Calculate confidence based on available context
        confidence = self._calculate_confidence(context)
        
        score = PriorityScore(
            base_priority=base_score,
            urgency_factor=urgency_factor,
            context_weight=context_weight,
            time_pressure=time_pressure,
            final_score=final_score,
            emoji_representation=emoji_rep,
            confidence=confidence
        )
        
        wre_log(f"Priority scored: {emoji_rep} (score: {final_score:.2f})")
        return score
    
    def compare_priorities(self, scored_intents: List[Tuple[Any, PriorityScore]]) -> List[Tuple[Any, PriorityScore]]:
        """
        Sort intents by priority score for queue management.
        
        Args:
            scored_intents: List of (intent, priority_score) tuples
            
        Returns:
            Sorted list with highest priority first
        """
        sorted_intents = sorted(
            scored_intents,
            key=lambda x: x[1].get_ranking_value(),
            reverse=True
        )
        
        wre_log(f"Sorted {len(scored_intents)} intents by priority")
        return sorted_intents
    
    def calculate_urgency_factor(self, context: ScoringContext) -> float:
        """
        Calculate urgency multiplier based on context factors.
        
        Args:
            context: Meeting context for urgency assessment
            
        Returns:
            Urgency factor (1.0-2.0)
        """
        urgency = 1.0
        
        # Duration-based urgency (shorter = more focused = higher urgency)
        if context.duration_minutes <= 15:
            urgency *= 1.3
        elif context.duration_minutes <= 30:
            urgency *= 1.15
        elif context.duration_minutes >= 120:
            urgency *= 0.9  # Long meetings often less urgent
        
        # Participant count factor
        if context.participant_count >= 5:
            urgency *= 1.1  # Harder to reschedule large groups
        elif context.participant_count == 1:
            urgency *= 0.95  # 1:1 meetings easier to reschedule
        
        # Requester urgency factor
        urgency *= context.requester_urgency
        
        # Cap the urgency factor
        return min(urgency, 2.0)
    
    def get_emoji_scale(self, score: float) -> str:
        """
        Get emoji representation for a given score.
        
        Args:
            score: Numeric priority score
            
        Returns:
            Emoji string for visual representation
        """
        return self._generate_emoji_representation(score)
    
    def calculate_priority_decay(self, created_at: datetime, current_time: Optional[datetime] = None) -> float:
        """
        Calculate priority decay factor based on age.
        
        Args:
            created_at: When the intent was created
            current_time: Current time (defaults to now)
            
        Returns:
            Decay factor (0.5-1.0)
        """
        if current_time is None:
            current_time = datetime.now()
        
        age_hours = (current_time - created_at).total_seconds() / 3600
        
        # Exponential decay over 48 hours
        if age_hours <= 24:
            return 1.0  # No decay for first 24 hours
        elif age_hours <= 48:
            return 0.8  # Moderate decay 24-48 hours
        else:
            return 0.5  # Significant decay after 48 hours
    
    def get_priority_statistics(self, scores: List[PriorityScore]) -> Dict[str, Any]:
        """
        Generate priority distribution statistics.
        
        Args:
            scores: List of priority scores
            
        Returns:
            Statistics dictionary
        """
        if not scores:
            return {"total": 0, "distribution": {}, "average_score": 0.0}
        
        # Distribution by emoji scale
        distribution = {}
        for score in scores:
            emoji = score.emoji_representation
            distribution[emoji] = distribution.get(emoji, 0) + 1
        
        # Calculate statistics
        total_score = sum(s.final_score for s in scores)
        average_score = total_score / len(scores)
        
        return {
            "total": len(scores),
            "distribution": distribution,
            "average_score": round(average_score, 2),
            "highest_score": max(s.final_score for s in scores),
            "lowest_score": min(s.final_score for s in scores)
        }
    
    # Private Methods
    
    def _calculate_time_pressure(self, context: ScoringContext) -> float:
        """Calculate time pressure factor based on deadline proximity"""
        if not context.deadline:
            return 1.0  # No deadline pressure
        
        time_until_deadline = (context.deadline - datetime.now()).total_seconds()
        hours_until = time_until_deadline / 3600
        
        if hours_until <= 2:
            return 1.8  # Immediate deadline
        elif hours_until <= 24:
            return 1.4  # Same day deadline
        elif hours_until <= 72:
            return 1.2  # Within 3 days
        else:
            return 1.0  # No immediate pressure
    
    def _calculate_keyword_boost(self, context: ScoringContext) -> float:
        """Calculate boost factor based on importance keywords"""
        if not context.importance_keywords:
            return 1.0
        
        max_boost = 1.0
        for keyword in context.importance_keywords:
            keyword_lower = keyword.lower()
            for important_word, boost in self.importance_keywords.items():
                if important_word in keyword_lower:
                    max_boost = max(max_boost, boost)
        
        return max_boost
    
    def _generate_emoji_representation(self, score: float) -> str:
        """Generate 000-222 emoji representation for score"""
        if score <= 1.0:
            return "🥱 000"  # Low priority
        elif score <= 2.0:
            return "😐 111"  # Medium priority
        elif score <= 3.5:
            return "🔥 222"  # High priority
        else:
            return "⚡⚡⚡ URGENT"  # Critical/urgent
    
    def _calculate_confidence(self, context: ScoringContext) -> float:
        """Calculate scoring confidence based on available context"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence for complete context
        if context.meeting_type != MeetingType.GENERAL:
            confidence += 0.2
        
        if context.duration_minutes > 0:
            confidence += 0.1
            
        if context.participant_count > 0:
            confidence += 0.1
            
        if context.deadline:
            confidence += 0.1
            
        if context.importance_keywords:
            confidence += 0.1
        
        return min(confidence, 1.0)


# Utility Functions for AMO Integration

def score_meeting_intent(intent_data: Dict[str, Any]) -> PriorityScore:
    """
    Convenience function for scoring meeting intents.
    
    Args:
        intent_data: Dictionary with intent information
        
    Returns:
        PriorityScore for the intent
    """
    scorer = PriorityScorer()
    
    # Extract priority
    priority_str = intent_data.get('priority', 'medium').upper()
    priority = Priority[priority_str] if priority_str in Priority.__members__ else Priority.MEDIUM
    
    # Build scoring context
    context = ScoringContext(
        meeting_type=MeetingType(intent_data.get('meeting_type', 'general')),
        duration_minutes=intent_data.get('duration_minutes', 30),
        participant_count=intent_data.get('participant_count', 2),
        deadline=intent_data.get('deadline'),
        importance_keywords=intent_data.get('keywords', []),
        requester_urgency=intent_data.get('requester_urgency', 1.0)
    )
    
    return scorer.score_intent(priority, context)


def create_priority_queue(intents: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], PriorityScore]]:
    """
    Create a priority-sorted queue from a list of intents.
    
    Args:
        intents: List of intent dictionaries
        
    Returns:
        Priority-sorted list of (intent, score) tuples
    """
    scorer = PriorityScorer()
    scored_intents = []
    
    for intent in intents:
        score = score_meeting_intent(intent)
        scored_intents.append((intent, score))
    
    return scorer.compare_priorities(scored_intents) 