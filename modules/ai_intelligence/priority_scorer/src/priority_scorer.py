"""
Priority Scorer - Intelligent Meeting Priority Assessment

Analyzes multiple factors to score meeting priority from 1-10.
Supports business logic customization and learning from outcomes.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MeetingPriority(Enum):
    """Meeting priority levels"""
    CRITICAL = "critical"      # 9-10: Urgent & Important
    HIGH = "high"             # 7-8: High impact
    MEDIUM = "medium"         # 5-6: Standard priority
    LOW = "low"              # 3-4: Nice to have
    MINIMAL = "minimal"       # 1-2: Optional


class ScoringFactor(Enum):
    """Factors that influence priority scoring"""
    URGENCY = "urgency"           # Time sensitivity
    IMPORTANCE = "importance"     # Business impact
    PARTICIPANTS = "participants" # Who's involved
    PURPOSE = "purpose"          # Meeting type/purpose
    CONTEXT = "context"          # External factors
    HISTORY = "history"          # Past behavior patterns


@dataclass
class PriorityAnalysis:
    """Complete priority analysis for a meeting intent"""
    overall_score: float
    priority_level: MeetingPriority
    factor_scores: Dict[ScoringFactor, float]
    reasoning: List[str]
    confidence: float
    analyzed_at: datetime


class PriorityScorer:
    """
    Intelligent priority scoring system for meeting orchestration.
    
    Uses configurable factors and weights to determine meeting priority.
    """
    
    def __init__(self):
        # Default factor weights (customizable)
        self.factor_weights = {
            ScoringFactor.URGENCY: 0.25,
            ScoringFactor.IMPORTANCE: 0.25,
            ScoringFactor.PARTICIPANTS: 0.20,
            ScoringFactor.PURPOSE: 0.15,
            ScoringFactor.CONTEXT: 0.10,
            ScoringFactor.HISTORY: 0.05
        }
        
        self.priority_thresholds = {
            MeetingPriority.CRITICAL: 9.0,
            MeetingPriority.HIGH: 7.0,
            MeetingPriority.MEDIUM: 5.0,
            MeetingPriority.LOW: 3.0,
            MeetingPriority.MINIMAL: 0.0
        }
        
        self.scoring_history = []
        self.user_preferences = {}
    
    async def score_meeting_priority(self, meeting_data: Dict[str, Any]) -> PriorityAnalysis:
        """
        Score meeting priority based on multiple factors.
        
        Args:
            meeting_data: Meeting information including participants, purpose, timing, etc.
            
        Returns:
            Complete priority analysis with score and reasoning
        """
        try:
            # Calculate individual factor scores
            factor_scores = {}
            reasoning = []
            
            # Urgency scoring
            urgency_score = await self._score_urgency(meeting_data)
            factor_scores[ScoringFactor.URGENCY] = urgency_score
            reasoning.append(f"Urgency: {urgency_score:.1f}/10 - {await self._get_urgency_reason(meeting_data)}")
            
            # Importance scoring
            importance_score = await self._score_importance(meeting_data)
            factor_scores[ScoringFactor.IMPORTANCE] = importance_score
            reasoning.append(f"Importance: {importance_score:.1f}/10 - {await self._get_importance_reason(meeting_data)}")
            
            # Participant scoring
            participant_score = await self._score_participants(meeting_data)
            factor_scores[ScoringFactor.PARTICIPANTS] = participant_score
            reasoning.append(f"Participants: {participant_score:.1f}/10 - {await self._get_participant_reason(meeting_data)}")
            
            # Purpose scoring
            purpose_score = await self._score_purpose(meeting_data)
            factor_scores[ScoringFactor.PURPOSE] = purpose_score
            reasoning.append(f"Purpose: {purpose_score:.1f}/10 - {await self._get_purpose_reason(meeting_data)}")
            
            # Context scoring
            context_score = await self._score_context(meeting_data)
            factor_scores[ScoringFactor.CONTEXT] = context_score
            
            # History scoring
            history_score = await self._score_history(meeting_data)
            factor_scores[ScoringFactor.HISTORY] = history_score
            
            # Calculate weighted overall score
            overall_score = sum(
                score * self.factor_weights[factor] 
                for factor, score in factor_scores.items()
            )
            
            # Determine priority level
            priority_level = await self._determine_priority_level(overall_score)
            
            # Calculate confidence
            confidence = await self._calculate_confidence(factor_scores, meeting_data)
            
            analysis = PriorityAnalysis(
                overall_score=round(overall_score, 2),
                priority_level=priority_level,
                factor_scores=factor_scores,
                reasoning=reasoning,
                confidence=confidence,
                analyzed_at=datetime.now()
            )
            
            # Store for learning
            self.scoring_history.append(analysis)
            
            logger.info(f"Priority scored: {overall_score:.2f} ({priority_level.value})")
            return analysis
            
        except Exception as e:
            logger.error(f"Error scoring priority: {e}")
            # Return default medium priority
            return PriorityAnalysis(
                overall_score=5.0,
                priority_level=MeetingPriority.MEDIUM,
                factor_scores={},
                reasoning=["Error in scoring - defaulted to medium priority"],
                confidence=0.1,
                analyzed_at=datetime.now()
            )
    
    async def update_factor_weights(self, new_weights: Dict[ScoringFactor, float]) -> bool:
        """Update scoring factor weights"""
        try:
            # Validate weights sum to 1.0
            total_weight = sum(new_weights.values())
            if abs(total_weight - 1.0) > 0.01:
                logger.error(f"Weights must sum to 1.0, got {total_weight}")
                return False
            
            self.factor_weights.update(new_weights)
            logger.info("Factor weights updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating weights: {e}")
            return False
    
    async def get_priority_suggestions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get priority suggestions based on user history"""
        user_history = [s for s in self.scoring_history if s.get('user_id') == user_id]
        
        suggestions = []
        
        # Analyze patterns
        if len(user_history) >= 5:
            avg_urgency = sum(h.factor_scores.get(ScoringFactor.URGENCY, 5) for h in user_history[-5:]) / 5
            
            if avg_urgency > 7:
                suggestions.append({
                    "type": "urgency_pattern",
                    "message": "You tend to have urgent meetings - consider scheduling buffer time",
                    "confidence": 0.8
                })
        
        return suggestions
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get priority scoring statistics"""
        if not self.scoring_history:
            return {"total_scored": 0}
        
        priority_distribution = {}
        for priority in MeetingPriority:
            count = len([s for s in self.scoring_history if s.priority_level == priority])
            priority_distribution[priority.value] = count
        
        avg_score = sum(s.overall_score for s in self.scoring_history) / len(self.scoring_history)
        avg_confidence = sum(s.confidence for s in self.scoring_history) / len(self.scoring_history)
        
        return {
            "total_scored": len(self.scoring_history),
            "average_score": round(avg_score, 2),
            "average_confidence": round(avg_confidence, 2),
            "priority_distribution": priority_distribution,
            "factor_weights": {f.value: w for f, w in self.factor_weights.items()}
        }
    
    # Private scoring methods
    
    async def _score_urgency(self, meeting_data: Dict[str, Any]) -> float:
        """Score based on time sensitivity"""
        proposed_time = meeting_data.get('proposed_time')
        if not proposed_time:
            return 5.0  # Default medium urgency
        
        # Calculate time until meeting
        if isinstance(proposed_time, str):
            # Simple parsing - would use proper NLP in production
            if "asap" in proposed_time.lower() or "urgent" in proposed_time.lower():
                return 9.0
            elif "today" in proposed_time.lower():
                return 8.0
            elif "tomorrow" in proposed_time.lower():
                return 6.0
            else:
                return 4.0
        
        return 5.0
    
    async def _score_importance(self, meeting_data: Dict[str, Any]) -> float:
        """Score based on business importance"""
        purpose = meeting_data.get('purpose', '').lower()
        
        # High importance keywords
        critical_keywords = ['crisis', 'emergency', 'urgent', 'critical', 'deadline']
        high_keywords = ['decision', 'strategy', 'budget', 'launch', 'review']
        medium_keywords = ['sync', 'update', 'planning', 'discussion']
        
        if any(keyword in purpose for keyword in critical_keywords):
            return 9.0
        elif any(keyword in purpose for keyword in high_keywords):
            return 7.0
        elif any(keyword in purpose for keyword in medium_keywords):
            return 5.0
        else:
            return 4.0
    
    async def _score_participants(self, meeting_data: Dict[str, Any]) -> float:
        """Score based on participant seniority/importance"""
        participants = meeting_data.get('participants', [])
        
        if not participants:
            return 3.0
        
        # Simple participant scoring (would integrate with org chart in production)
        score = 3.0
        
        # More participants = slightly higher priority
        score += min(len(participants) * 0.5, 2.0)
        
        # Check for senior roles (basic keyword detection)
        participant_text = ' '.join(participants).lower()
        senior_keywords = ['ceo', 'director', 'manager', 'lead', 'head']
        
        if any(keyword in participant_text for keyword in senior_keywords):
            score += 2.0
        
        return min(score, 10.0)
    
    async def _score_purpose(self, meeting_data: Dict[str, Any]) -> float:
        """Score based on meeting purpose/type"""
        purpose = meeting_data.get('purpose', '').lower()
        
        # Meeting type scoring
        if any(word in purpose for word in ['demo', 'presentation', 'interview']):
            return 7.0
        elif any(word in purpose for word in ['standup', 'sync', 'update']):
            return 5.0
        elif any(word in purpose for word in ['brainstorm', 'planning']):
            return 6.0
        elif any(word in purpose for word in ['social', 'coffee', 'casual']):
            return 3.0
        else:
            return 5.0
    
    async def _score_context(self, meeting_data: Dict[str, Any]) -> float:
        """Score based on external context factors"""
        # Simple context scoring - would integrate with calendar, workload, etc.
        context_score = 5.0
        
        # Check for conflict indicators
        if meeting_data.get('has_conflicts'):
            context_score += 2.0
        
        # Check for deadline proximity
        if meeting_data.get('near_deadline'):
            context_score += 1.5
        
        return min(context_score, 10.0)
    
    async def _score_history(self, meeting_data: Dict[str, Any]) -> float:
        """Score based on historical patterns"""
        user_id = meeting_data.get('user_id')
        if not user_id or not self.scoring_history:
            return 5.0
        
        # Analyze user's historical patterns
        user_scores = [s.overall_score for s in self.scoring_history if s.get('user_id') == user_id]
        
        if user_scores:
            avg_user_score = sum(user_scores) / len(user_scores)
            return min(avg_user_score + 1.0, 10.0)  # Slight bias toward historical average
        
        return 5.0
    
    async def _determine_priority_level(self, score: float) -> MeetingPriority:
        """Convert numeric score to priority level"""
        for priority, threshold in self.priority_thresholds.items():
            if score >= threshold:
                return priority
        return MeetingPriority.MINIMAL
    
    async def _calculate_confidence(self, factor_scores: Dict[ScoringFactor, float], meeting_data: Dict[str, Any]) -> float:
        """Calculate confidence in the priority score"""
        # Base confidence on data completeness
        confidence = 0.5
        
        # More complete data = higher confidence
        if meeting_data.get('participants'):
            confidence += 0.1
        if meeting_data.get('purpose'):
            confidence += 0.1
        if meeting_data.get('proposed_time'):
            confidence += 0.1
        
        # Score consistency across factors
        scores = list(factor_scores.values())
        if len(scores) > 1:
            score_variance = sum((s - sum(scores)/len(scores))**2 for s in scores) / len(scores)
            # Lower variance = higher confidence
            confidence += max(0, 0.2 - score_variance/10)
        
        return min(confidence, 1.0)
    
    async def _get_urgency_reason(self, meeting_data: Dict[str, Any]) -> str:
        """Get reasoning for urgency score"""
        proposed_time = meeting_data.get('proposed_time', '')
        if "asap" in str(proposed_time).lower():
            return "ASAP timeline requested"
        elif "today" in str(proposed_time).lower():
            return "Same-day meeting"
        elif "tomorrow" in str(proposed_time).lower():
            return "Next-day meeting"
        else:
            return "Standard timeline"
    
    async def _get_importance_reason(self, meeting_data: Dict[str, Any]) -> str:
        """Get reasoning for importance score"""
        purpose = meeting_data.get('purpose', '').lower()
        if any(word in purpose for word in ['crisis', 'emergency', 'critical']):
            return "Critical business issue"
        elif any(word in purpose for word in ['decision', 'strategy', 'launch']):
            return "Strategic importance"
        else:
            return "Standard business meeting"
    
    async def _get_participant_reason(self, meeting_data: Dict[str, Any]) -> str:
        """Get reasoning for participant score"""
        participants = meeting_data.get('participants', [])
        count = len(participants)
        if count == 0:
            return "No specific participants"
        elif count == 1:
            return "One-on-one meeting"
        elif count <= 3:
            return f"Small group ({count} people)"
        else:
            return f"Large group ({count} people)"
    
    async def _get_purpose_reason(self, meeting_data: Dict[str, Any]) -> str:
        """Get reasoning for purpose score"""
        purpose = meeting_data.get('purpose', '').lower()
        if 'demo' in purpose or 'presentation' in purpose:
            return "Formal presentation"
        elif 'standup' in purpose or 'sync' in purpose:
            return "Regular sync meeting"
        else:
            return "General discussion"


# Demo functionality
if __name__ == "__main__":
    async def demo():
        print("📊 Priority Scorer Demo")
        print("=" * 50)
        
        scorer = PriorityScorer()
        
        # Demo meeting scenarios
        scenarios = [
            {
                "purpose": "Emergency system outage discussion",
                "participants": ["alice", "bob", "cto"],
                "proposed_time": "ASAP",
                "user_id": "alice"
            },
            {
                "purpose": "Weekly team standup",
                "participants": ["team"],
                "proposed_time": "tomorrow",
                "user_id": "bob"
            },
            {
                "purpose": "Coffee chat with new hire",
                "participants": ["newbie"],
                "proposed_time": "next week",
                "user_id": "alice"
            },
            {
                "purpose": "Product launch strategy meeting",
                "participants": ["ceo", "cto", "marketing_lead"],
                "proposed_time": "today",
                "user_id": "ceo"
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n🎯 Scenario {i}: {scenario['purpose'][:30]}...")
            analysis = await scorer.score_meeting_priority(scenario)
            
            print(f"   Priority: {analysis.priority_level.value.upper()} ({analysis.overall_score}/10)")
            print(f"   Confidence: {analysis.confidence:.2f}")
            print(f"   Reasoning:")
            for reason in analysis.reasoning[:2]:  # Show first 2 reasons
                print(f"     • {reason}")
        
        # Show statistics
        stats = await scorer.get_statistics()
        print(f"\n📈 Statistics:")
        print(f"   Total scored: {stats['total_scored']}")
        print(f"   Average score: {stats['average_score']}")
        print(f"   Distribution: {stats['priority_distribution']}")
        
        print("\n✨ Demo completed!")
    
    asyncio.run(demo()) 