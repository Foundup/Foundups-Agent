"""
Learning Engine - Pattern Recognition and Behavioral Adaptation for 0102 Orchestrator

Provides intelligent learning and adaptation capabilities:
- User behavior pattern recognition
- Meeting preference learning
- Performance optimization
- Predictive scheduling suggestions
- Adaptive personality matching

Part of the 0102 unified AI companion layer.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, Counter
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LearningType(Enum):
    """Types of learning patterns"""
    PREFERENCE = "preference"           # User preferences
    BEHAVIOR = "behavior"              # Behavioral patterns
    TEMPORAL = "temporal"              # Time-based patterns
    PLATFORM = "platform"             # Platform usage patterns


class ConfidenceLevel(Enum):
    """Confidence levels for learned patterns"""
    LOW = "low"                        # < 3 data points
    MEDIUM = "medium"                  # 3-10 data points
    HIGH = "high"                      # 11+ data points


@dataclass
class LearningData:
    """Data point for learning"""
    user_id: str
    learning_type: LearningType
    context: Dict[str, Any]
    outcome: Dict[str, Any]
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Pattern:
    """Identified pattern from learning data"""
    pattern_id: str
    learning_type: LearningType
    description: str
    confidence: ConfidenceLevel
    pattern_data: Dict[str, Any]
    evidence_count: int
    last_updated: datetime


@dataclass
class UserProfile:
    """Learned user profile"""
    user_id: str
    preferences: Dict[str, Any]
    behavioral_patterns: List[Pattern]
    meeting_history: List[Dict[str, Any]]
    learning_score: float              # 0.0 to 1.0
    last_updated: datetime
    total_interactions: int


class LearningEngine:
    """
    Provides intelligent learning and adaptation for 0102 orchestrator.
    """
    
    def __init__(self):
        self.learning_data: List[LearningData] = []
        self.user_profiles: Dict[str, UserProfile] = {}
        self.identified_patterns: List[Pattern] = []
        
        logger.info("LearningEngine initialized - Ready to learn and adapt")
    
    async def record_interaction(
        self,
        user_id: str,
        interaction_type: str,
        context: Dict[str, Any],
        outcome: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Record a user interaction for learning."""
        
        learning_data = LearningData(
            user_id=user_id,
            learning_type=LearningType.BEHAVIOR,
            context=context,
            outcome=outcome,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        learning_data.metadata['interaction_type'] = interaction_type
        self.learning_data.append(learning_data)
        
        # Update user profile
        await self._update_user_profile(user_id, learning_data)
        
        logger.info(f"Recorded interaction for {user_id}: {interaction_type}")
        return f"learning_{len(self.learning_data)}"
    
    async def learn_preference(
        self,
        user_id: str,
        preference_type: str,
        value: Any,
        confidence: float = 1.0
    ) -> bool:
        """Learn and store user preference"""
        
        learning_data = LearningData(
            user_id=user_id,
            learning_type=LearningType.PREFERENCE,
            context={'preference_type': preference_type, 'confidence': confidence},
            outcome={'value': value},
            timestamp=datetime.now()
        )
        
        self.learning_data.append(learning_data)
        
        # Update user profile preferences
        if user_id not in self.user_profiles:
            await self._create_user_profile(user_id)
        
        profile = self.user_profiles[user_id]
        profile.preferences[preference_type] = {
            'value': value,
            'confidence': confidence,
            'learned_at': datetime.now()
        }
        
        profile.last_updated = datetime.now()
        profile.total_interactions += 1
        
        logger.info(f"Learned preference for {user_id}: {preference_type} = {value}")
        return True
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get learned preferences for user"""
        if user_id not in self.user_profiles:
            return {}
        
        profile = self.user_profiles[user_id]
        return {k: v['value'] for k, v in profile.preferences.items()}
    
    async def predict_user_behavior(
        self,
        user_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict user behavior based on learned patterns"""
        
        if user_id not in self.user_profiles:
            return {'confidence': 0.0, 'predictions': {}}
        
        profile = self.user_profiles[user_id]
        predictions = {}
        
        # Analyze platform patterns
        platform_prediction = self._predict_platform_preference(profile, context)
        if platform_prediction:
            predictions['preferred_platform'] = platform_prediction
        
        # Calculate overall confidence
        confidence = min(1.0, profile.learning_score)
        
        logger.info(f"Generated behavior prediction for {user_id} with {confidence:.2f} confidence")
        
        return {
            'confidence': confidence,
            'predictions': predictions,
            'based_on_interactions': profile.total_interactions
        }
    
    async def get_learning_statistics(self) -> Dict[str, Any]:
        """Get comprehensive learning statistics"""
        
        total_data_points = len(self.learning_data)
        unique_users = len(self.user_profiles)
        total_patterns = len(self.identified_patterns)
        
        # User engagement statistics
        user_interactions = {
            user_id: profile.total_interactions 
            for user_id, profile in self.user_profiles.items()
        }
        
        avg_interactions = statistics.mean(user_interactions.values()) if user_interactions else 0
        
        return {
            'total_data_points': total_data_points,
            'unique_users': unique_users,
            'total_patterns': total_patterns,
            'average_interactions_per_user': round(avg_interactions, 2),
            'most_active_user': max(user_interactions, key=user_interactions.get) if user_interactions else None
        }
    
    # Internal implementation methods
    
    async def _update_user_profile(self, user_id: str, learning_data: LearningData):
        """Update user profile with new learning data"""
        
        if user_id not in self.user_profiles:
            await self._create_user_profile(user_id)
        
        profile = self.user_profiles[user_id]
        profile.total_interactions += 1
        profile.last_updated = datetime.now()
        
        # Add to meeting history if it's a meeting-related interaction
        if learning_data.metadata.get('interaction_type') in ['meeting_created', 'meeting_completed']:
            profile.meeting_history.append({
                'timestamp': learning_data.timestamp,
                'context': learning_data.context,
                'outcome': learning_data.outcome
            })
        
        # Update learning score
        profile.learning_score = self._calculate_learning_score(profile)
    
    async def _create_user_profile(self, user_id: str) -> UserProfile:
        """Create new user profile"""
        
        profile = UserProfile(
            user_id=user_id,
            preferences={},
            behavioral_patterns=[],
            meeting_history=[],
            learning_score=0.0,
            last_updated=datetime.now(),
            total_interactions=0
        )
        
        self.user_profiles[user_id] = profile
        logger.info(f"Created user profile for {user_id}")
        return profile
    
    def _predict_platform_preference(self, profile: UserProfile, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Predict platform preferences based on patterns"""
        
        # Analyze meeting history for platform patterns
        platforms = []
        for meeting in profile.meeting_history:
            if 'platform' in meeting.get('context', {}):
                platforms.append(meeting['context']['platform'])
        
        if len(platforms) >= 3:
            platform_counts = Counter(platforms)
            most_common = platform_counts.most_common(1)[0]
            confidence = self._calculate_confidence_level(len(platforms))
            
            if confidence in [ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH]:
                return {
                    'preferred_platform': most_common[0],
                    'confidence': confidence.value,
                    'based_on_evidence': len(platforms)
                }
        
        return None
    
    def _calculate_learning_score(self, profile: UserProfile) -> float:
        """Calculate how well we know this user (0.0 to 1.0)"""
        
        # Base score from interaction count
        interaction_score = min(1.0, profile.total_interactions / 20.0)
        
        # Bonus for preference learning
        preference_score = min(0.3, len(profile.preferences) / 10.0)
        
        total_score = interaction_score + preference_score
        return min(1.0, total_score)
    
    def _calculate_confidence_level(self, evidence_count: int) -> ConfidenceLevel:
        """Calculate confidence level based on evidence count"""
        
        if evidence_count < 3:
            return ConfidenceLevel.LOW
        elif evidence_count < 11:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.HIGH


# Demo function
async def demo_learning_engine():
    """Demonstrate learning engine functionality"""
    engine = LearningEngine()
    
    print("=== 0102 Learning Engine Demo ===")
    
    # Simulate user interactions
    user_id = "alice"
    
    # Record interactions
    await engine.record_interaction(
        user_id, "meeting_created",
        {"platform": "discord", "duration": 30},
        {"success": True, "session_id": "session_123"}
    )
    
    # Learn preferences
    await engine.learn_preference(user_id, "notification_style", "friendly")
    
    # Get predictions
    predictions = await engine.predict_user_behavior(user_id, {"meeting_type": "sync"})
    print(f"🔮 Behavior predictions: {predictions}")
    
    # Get statistics
    stats = await engine.get_learning_statistics()
    print(f"📊 Learning statistics: {stats}")
    
    return engine


if __name__ == "__main__":
    asyncio.run(demo_learning_engine()) 