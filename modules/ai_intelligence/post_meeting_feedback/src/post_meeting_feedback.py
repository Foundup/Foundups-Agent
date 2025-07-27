# modules/ai_intelligence/post_meeting_feedback/src/post_meeting_feedback.py

"""
Post-Meeting Feedback System Module
WSP Protocol: WSP 25/44 (Semantic Rating System), WSP 54 (Agent Coordination)

Intelligent post-meeting feedback collection using WSP 000-222 rating system
with agentic follow-up scheduling and priority adjustment based on meeting outcomes.

Part of Meeting Orchestration Block enhancement - can be integrated with any block.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import math

logger = logging.getLogger(__name__)

class RatingValue(Enum):
    """WSP 25/44 compatible rating values (000-222 system)"""
    BAD = 0      # 000 - Negative experience, avoid future meetings
    OKAY = 1     # 111 - Neutral experience, conditional follow-up
    GOOD = 2     # 222 - Positive experience, encourage future meetings

class FollowUpPriority(Enum):
    """Priority levels for follow-up meetings based on feedback"""
    NO_FOLLOWUP = "no_followup"       # 0 rating - no future meetings
    LOW_PRIORITY = "low_priority"     # 0 rating but wants to meet again
    MEDIUM_PRIORITY = "medium_priority" # 1 rating - conditional follow-up
    HIGH_PRIORITY = "high_priority"   # 2 rating - encourage follow-up
    URGENT_FOLLOWUP = "urgent_followup" # 2 rating with immediate action needed

class FollowUpTimeframe(Enum):
    """Relative timeframes for follow-up scheduling"""
    NEXT_WEEK = 7       # 7 days baseline
    NEXT_MONTH = 30     # 30 days baseline  
    NEXT_QUARTER = 90   # 90 days baseline
    WHEN_NEEDED = 0     # No specific timeline
    NEVER = -1          # No follow-up desired

@dataclass
class FeedbackQuestion:
    """Individual feedback question structure"""
    question_id: str
    question_text: str
    question_type: str  # "rating", "choice", "text"
    options: List[str] = field(default_factory=list)
    required: bool = True
    follow_up_logic: Optional[Dict] = None

@dataclass
class FeedbackResponse:
    """User's response to feedback questions"""
    question_id: str
    response_value: Any
    response_text: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class MeetingFeedback:
    """Complete feedback record for a meeting session"""
    feedback_id: str
    session_id: str
    intent_id: str
    respondent_id: str
    meeting_host_id: str
    meeting_participants: List[str]
    overall_rating: RatingValue
    responses: List[FeedbackResponse]
    calculated_score: float  # WSP compatible 0.0-10.0 score
    semantic_triplet: str    # WSP 25/44 triplet like "201"
    follow_up_priority: FollowUpPriority
    follow_up_timeframe: Optional[FollowUpTimeframe]
    follow_up_notes: Optional[str]
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)

@dataclass
class FollowUpSchedule:
    """Agentic follow-up scheduling with dynamic priority"""
    schedule_id: str
    original_feedback_id: str
    requester_id: str
    target_id: str
    follow_up_intent: str
    base_timeframe_days: int
    current_priority_value: float  # Increases as time approaches
    max_priority_value: float = 10.0
    rejection_count: int = 0
    max_rejections: int = 3
    auto_downgrade: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    target_activation_date: Optional[datetime] = None
    status: str = "scheduled"  # scheduled, active, rejected, completed, cancelled
    metadata: Dict = field(default_factory=dict)

class PostMeetingFeedbackSystem:
    """
    Intelligent post-meeting feedback collection and follow-up management system
    
    Responsibilities:
    - Collect structured feedback using WSP 25/44 rating system
    - Process 3-question cascading flow (rating → detail → action)
    - Calculate WSP-compatible scores and semantic triplets
    - Manage agentic follow-up scheduling with increasing priority values
    - Track meeting rejection patterns and auto-adjust priorities
    - Integration with AMO modules via event callbacks
    """
    
    def __init__(self):
        self.active_feedback_sessions: Dict[str, Dict] = {}
        self.feedback_history: List[MeetingFeedback] = []
        self.follow_up_schedules: Dict[str, FollowUpSchedule] = {}
        self.feedback_callbacks: Dict[str, List[Callable]] = {
            'feedback_collected': [],
            'follow_up_scheduled': [],
            'follow_up_activated': [],
            'rejection_threshold_reached': [],
            'priority_auto_adjusted': []
        }
        
        # Configuration
        self.config = {
            'feedback_timeout_hours': 24,
            'priority_increase_rate': 0.1,  # Daily priority increase
            'max_rejection_count': 3,
            'auto_downgrade_enabled': True,
            'notification_host_on_rejection': True,
            'semantic_calculation_weights': {
                'overall_rating': 0.5,
                'follow_up_priority': 0.3,
                'engagement_level': 0.2
            }
        }
        
        # WSP 25/44 Semantic Mapping
        self.semantic_mapping = self._initialize_semantic_mapping()
        
        # Question Flow Templates
        self.question_flows = self._initialize_question_flows()
        
        logger.info("📝 Post-Meeting Feedback System initialized")

    async def initiate_feedback_collection(
        self,
        session_id: str,
        intent_id: str,
        participants: List[str],
        host_id: str,
        session_metadata: Optional[Dict] = None
    ) -> List[str]:
        """
        Initiate feedback collection for all meeting participants
        
        Args:
            session_id: Completed session identifier
            intent_id: Original meeting intent ID
            participants: All meeting participants
            host_id: Meeting host identifier
            session_metadata: Additional session context
            
        Returns:
            List[str]: Feedback session IDs for tracking
        """
        feedback_session_ids = []
        
        logger.info(f"📝 Initiating feedback collection for session: {session_id}")
        logger.info(f"   Participants: {participants}")
        
        for participant_id in participants:
            feedback_session_id = str(uuid.uuid4())
            
            # Create feedback session
            feedback_session = {
                'feedback_session_id': feedback_session_id,
                'session_id': session_id,
                'intent_id': intent_id,
                'participant_id': participant_id,
                'host_id': host_id,
                'all_participants': participants,
                'current_question': 0,
                'responses': [],
                'status': 'initiated',
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(hours=self.config['feedback_timeout_hours']),
                'metadata': session_metadata or {}
            }
            
            self.active_feedback_sessions[feedback_session_id] = feedback_session
            feedback_session_ids.append(feedback_session_id)
            
            # Send first question
            await self._send_feedback_question(feedback_session_id, 0)
        
        logger.info(f"✅ Feedback collection initiated: {len(feedback_session_ids)} sessions")
        return feedback_session_ids

    async def process_feedback_response(
        self,
        feedback_session_id: str,
        response_value: Any,
        response_text: Optional[str] = None
    ) -> bool:
        """
        Process a user's response to a feedback question
        
        Args:
            feedback_session_id: Active feedback session
            response_value: User's response value
            response_text: Optional additional text
            
        Returns:
            bool: True if response processed successfully
        """
        session = self.active_feedback_sessions.get(feedback_session_id)
        if not session:
            logger.warning(f"❌ Unknown feedback session: {feedback_session_id}")
            return False
        
        current_q_index = session['current_question']
        questions = self.question_flows['standard']
        
        if current_q_index >= len(questions):
            logger.warning(f"❌ Invalid question index: {current_q_index}")
            return False
        
        current_question = questions[current_q_index]
        
        # Create response record
        response = FeedbackResponse(
            question_id=current_question.question_id,
            response_value=response_value,
            response_text=response_text
        )
        
        session['responses'].append(response)
        
        logger.info(f"📝 Feedback response: {feedback_session_id}")
        logger.info(f"   Question: {current_question.question_text}")
        logger.info(f"   Response: {response_value}")
        
        # Determine next question based on current response and logic
        next_question_index = await self._determine_next_question(
            session, current_q_index, response_value
        )
        
        if next_question_index is not None:
            # Send next question
            session['current_question'] = next_question_index
            await self._send_feedback_question(feedback_session_id, next_question_index)
        else:
            # Feedback collection complete
            await self._complete_feedback_collection(feedback_session_id)
        
        return True

    async def get_feedback_summary(self, session_id: str) -> Dict:
        """Get comprehensive feedback summary for a session"""
        session_feedback = [
            feedback for feedback in self.feedback_history
            if feedback.session_id == session_id
        ]
        
        if not session_feedback:
            return {'session_id': session_id, 'feedback_count': 0}
        
        # Calculate aggregate metrics
        ratings = [f.overall_rating.value for f in session_feedback]
        scores = [f.calculated_score for f in session_feedback]
        follow_up_priorities = [f.follow_up_priority.value for f in session_feedback]
        
        summary = {
            'session_id': session_id,
            'feedback_count': len(session_feedback),
            'average_rating': sum(ratings) / len(ratings) if ratings else 0,
            'average_score': sum(scores) / len(scores) if scores else 0,
            'rating_distribution': {
                'bad': ratings.count(0),
                'okay': ratings.count(1), 
                'good': ratings.count(2)
            },
            'follow_up_distribution': {},
            'semantic_analysis': self._calculate_session_semantic_state(session_feedback),
            'recommendations': self._generate_session_recommendations(session_feedback)
        }
        
        # Follow-up distribution
        for priority in FollowUpPriority:
            summary['follow_up_distribution'][priority.value] = follow_up_priorities.count(priority.value)
        
        return summary

    async def check_follow_up_schedules(self) -> List[str]:
        """
        Check follow-up schedules and activate those whose priority has reached threshold
        
        Returns:
            List[str]: Activated follow-up schedule IDs
        """
        activated_schedules = []
        current_time = datetime.now()
        
        for schedule_id, schedule in list(self.follow_up_schedules.items()):
            if schedule.status != 'scheduled':
                continue
            
            # Calculate time-based priority increase
            if schedule.target_activation_date and current_time >= schedule.target_activation_date:
                # Priority increases as we approach and pass target date
                days_since_target = (current_time - schedule.target_activation_date).days
                priority_increase = max(0, days_since_target * self.config['priority_increase_rate'])
                schedule.current_priority_value = min(
                    schedule.max_priority_value,
                    schedule.current_priority_value + priority_increase
                )
                
                # Activate if priority is high enough (≥7.0 for activation)
                if schedule.current_priority_value >= 7.0:
                    await self._activate_follow_up_schedule(schedule_id)
                    activated_schedules.append(schedule_id)
        
        if activated_schedules:
            logger.info(f"⚡ Activated {len(activated_schedules)} follow-up schedules")
        
        return activated_schedules

    async def process_follow_up_rejection(
        self,
        schedule_id: str,
        rejection_reason: Optional[str] = None
    ) -> Dict:
        """
        Process rejection of a follow-up meeting request
        
        Args:
            schedule_id: Follow-up schedule being rejected
            rejection_reason: Optional reason for rejection
            
        Returns:
            Dict: Processing result with next actions
        """
        schedule = self.follow_up_schedules.get(schedule_id)
        if not schedule:
            return {'success': False, 'error': 'Schedule not found'}
        
        schedule.rejection_count += 1
        schedule.metadata['last_rejection'] = datetime.now().isoformat()
        if rejection_reason:
            schedule.metadata[f'rejection_reason_{schedule.rejection_count}'] = rejection_reason
        
        logger.info(f"🚫 Follow-up rejected: {schedule_id}")
        logger.info(f"   Rejection count: {schedule.rejection_count}/{schedule.max_rejections}")
        
        result = {
            'success': True,
            'schedule_id': schedule_id,
            'rejection_count': schedule.rejection_count,
            'max_rejections': schedule.max_rejections,
            'action_taken': None
        }
        
        # Check if rejection threshold reached
        if schedule.rejection_count >= schedule.max_rejections:
            logger.warning(f"🚨 Rejection threshold reached: {schedule_id}")
            
            # Notify original requester
            if self.config['notification_host_on_rejection']:
                await self._notify_requester_of_rejections(schedule)
                result['action_taken'] = 'requester_notified'
            
            # Auto-downgrade priority if enabled
            if schedule.auto_downgrade:
                await self._auto_downgrade_follow_up(schedule_id)
                result['action_taken'] = 'auto_downgraded'
            
            # Trigger callback
            await self._trigger_callbacks('rejection_threshold_reached', schedule, {
                'rejection_count': schedule.rejection_count,
                'auto_downgrade': schedule.auto_downgrade
            })
        
        return result

    async def get_feedback_statistics(self) -> Dict:
        """Get comprehensive feedback and follow-up statistics"""
        total_feedback = len(self.feedback_history)
        total_follow_ups = len(self.follow_up_schedules)
        
        if total_feedback == 0:
            return {'total_feedback': 0, 'total_follow_ups': 0}
        
        # Rating distribution
        ratings = [f.overall_rating.value for f in self.feedback_history]
        scores = [f.calculated_score for f in self.feedback_history]
        
        # Follow-up analysis
        follow_up_statuses = [s.status for s in self.follow_up_schedules.values()]
        rejection_counts = [s.rejection_count for s in self.follow_up_schedules.values()]
        
        stats = {
            'total_feedback': total_feedback,
            'total_follow_ups': total_follow_ups,
            'average_rating': sum(ratings) / len(ratings),
            'average_score': sum(scores) / len(scores),
            'rating_distribution': {
                'bad': ratings.count(0),
                'okay': ratings.count(1),
                'good': ratings.count(2)
            },
            'follow_up_status_distribution': {},
            'average_rejections': sum(rejection_counts) / len(rejection_counts) if rejection_counts else 0,
            'high_rejection_schedules': len([r for r in rejection_counts if r >= 2])
        }
        
        # Follow-up status breakdown
        for status in ['scheduled', 'active', 'rejected', 'completed', 'cancelled']:
            stats['follow_up_status_distribution'][status] = follow_up_statuses.count(status)
        
        return stats

    async def subscribe_to_feedback_events(self, event_type: str, callback: Callable):
        """Subscribe to feedback events for integration with other modules"""
        if event_type in self.feedback_callbacks:
            self.feedback_callbacks[event_type].append(callback)
            logger.info(f"📡 Subscribed to {event_type} events")
        else:
            logger.warning(f"❌ Unknown feedback event type: {event_type}")

    # Private methods
    
    def _initialize_question_flows(self) -> Dict:
        """Initialize the 3-question cascading flow system"""
        return {
            'standard': [
                # Question 1: Overall Rating (WSP 000-222)
                FeedbackQuestion(
                    question_id="overall_rating",
                    question_text="How was the meeting overall?",
                    question_type="rating",
                    options=["0 - Not helpful/Poor experience", "1 - Okay/Neutral", "2 - Good/Valuable"],
                    follow_up_logic={
                        0: "negative_detail",  # Go to negative detail question
                        1: "neutral_detail",   # Go to neutral detail question
                        2: "positive_detail"   # Go to positive detail question
                    }
                ),
                
                # Question 2a: Negative Detail (Rating = 0)
                FeedbackQuestion(
                    question_id="negative_detail",
                    question_text="Since the meeting wasn't helpful, would you like to:",
                    question_type="choice",
                    options=[
                        "meet_again_low",     # Meet again but lowest priority
                        "no_followup",        # No follow-up meetings
                        "different_approach"  # Try different meeting approach
                    ],
                    follow_up_logic={
                        "meet_again_low": "action_question",
                        "no_followup": "action_question", 
                        "different_approach": "action_question"
                    }
                ),
                
                # Question 2b: Neutral Detail (Rating = 1)
                FeedbackQuestion(
                    question_id="neutral_detail",
                    question_text="The meeting was okay. What would make future meetings more valuable?",
                    question_type="choice",
                    options=[
                        "better_preparation",  # Need better preparation
                        "clearer_agenda",      # Need clearer agenda
                        "right_timing",        # Timing was good, continue as-is
                        "different_format"     # Try different meeting format
                    ],
                    follow_up_logic={
                        "better_preparation": "action_question",
                        "clearer_agenda": "action_question",
                        "right_timing": "action_question",
                        "different_format": "action_question"
                    }
                ),
                
                # Question 2c: Positive Detail (Rating = 2)
                FeedbackQuestion(
                    question_id="positive_detail",
                    question_text="Great! What made this meeting particularly valuable?",
                    question_type="choice", 
                    options=[
                        "productive_discussion",  # Good discussion/outcomes
                        "clear_next_steps",      # Clear action items
                        "good_collaboration",    # Great collaboration
                        "solved_problems"        # Solved specific problems
                    ],
                    follow_up_logic={
                        "productive_discussion": "action_question",
                        "clear_next_steps": "action_question",
                        "good_collaboration": "action_question",
                        "solved_problems": "action_question"
                    }
                ),
                
                # Question 3: Action/Follow-up
                FeedbackQuestion(
                    question_id="action_question", 
                    question_text="When should we have a follow-up meeting?",
                    question_type="choice",
                    options=[
                        "next_week",      # ~7 days
                        "next_month",     # ~30 days
                        "next_quarter",   # ~90 days
                        "when_needed",    # As needed basis
                        "no_followup"     # No follow-up needed
                    ],
                    follow_up_logic=None  # End of flow
                )
            ]
        }

    def _initialize_semantic_mapping(self) -> Dict:
        """Initialize WSP 25/44 semantic triplet mapping"""
        return {
            # Format: "XYZ" where X=overall, Y=engagement, Z=follow_up_intent
            "000": {"description": "Poor meeting, low engagement, no follow-up", "score": 0.0},
            "001": {"description": "Poor meeting, low engagement, minimal follow-up", "score": 1.0},
            "010": {"description": "Poor meeting, medium engagement, no follow-up", "score": 2.0},
            "011": {"description": "Poor meeting, medium engagement, minimal follow-up", "score": 3.0},
            "100": {"description": "Neutral meeting, low engagement, no follow-up", "score": 4.0},
            "101": {"description": "Neutral meeting, low engagement, minimal follow-up", "score": 5.0},
            "110": {"description": "Neutral meeting, medium engagement, no follow-up", "score": 5.5},
            "111": {"description": "Neutral meeting, medium engagement, standard follow-up", "score": 6.0},
            "112": {"description": "Neutral meeting, medium engagement, high follow-up", "score": 6.5},
            "200": {"description": "Good meeting, low engagement, no follow-up", "score": 7.0},
            "201": {"description": "Good meeting, low engagement, minimal follow-up", "score": 7.5},
            "210": {"description": "Good meeting, medium engagement, no follow-up", "score": 8.0},
            "211": {"description": "Good meeting, medium engagement, standard follow-up", "score": 8.5},
            "212": {"description": "Good meeting, medium engagement, high follow-up", "score": 9.0},
            "220": {"description": "Good meeting, high engagement, no follow-up", "score": 9.0},
            "221": {"description": "Good meeting, high engagement, standard follow-up", "score": 9.5},
            "222": {"description": "Good meeting, high engagement, urgent follow-up", "score": 10.0}
        }

    async def _send_feedback_question(self, feedback_session_id: str, question_index: int):
        """Send feedback question to participant"""
        session = self.active_feedback_sessions[feedback_session_id]
        questions = self.question_flows['standard']
        
        if question_index >= len(questions):
            logger.error(f"❌ Invalid question index: {question_index}")
            return
        
        question = questions[question_index]
        
        # For PoC, simulate sending question
        logger.info(f"📨 [SIMULATED] Sending feedback question to {session['participant_id']}")
        logger.info(f"   Question: {question.question_text}")
        logger.info(f"   Options: {question.options}")
        
        session['status'] = 'question_sent'
        session['last_question_sent'] = datetime.now()

    async def _determine_next_question(
        self,
        session: Dict,
        current_q_index: int,
        response_value: Any
    ) -> Optional[int]:
        """Determine next question based on response and flow logic"""
        questions = self.question_flows['standard']
        current_question = questions[current_q_index]
        
        if not current_question.follow_up_logic:
            return None  # End of flow
        
        # Get next question ID based on response
        next_question_id = current_question.follow_up_logic.get(response_value)
        if not next_question_id:
            return None
        
        # Find question index by ID
        for i, q in enumerate(questions):
            if q.question_id == next_question_id:
                return i
        
        return None

    async def _complete_feedback_collection(self, feedback_session_id: str):
        """Complete feedback collection and process results"""
        session = self.active_feedback_sessions.pop(feedback_session_id)
        
        logger.info(f"✅ Completing feedback collection: {feedback_session_id}")
        
        # Process responses and calculate feedback
        feedback = await self._process_feedback_responses(session)
        
        # Store in history
        self.feedback_history.append(feedback)
        
        # Create follow-up schedule if needed
        if feedback.follow_up_priority != FollowUpPriority.NO_FOLLOWUP:
            await self._create_follow_up_schedule(feedback)
        
        # Trigger callbacks
        await self._trigger_callbacks('feedback_collected', feedback, {
            'session_id': session['session_id'],
            'overall_rating': feedback.overall_rating.value,
            'calculated_score': feedback.calculated_score
        })

    async def _process_feedback_responses(self, session: Dict) -> MeetingFeedback:
        """Process collected responses into structured feedback"""
        responses = session['responses']
        
        # Extract key responses
        overall_rating = None
        detail_response = None
        action_response = None
        
        for response in responses:
            if response.question_id == "overall_rating":
                overall_rating = RatingValue(response.response_value)
            elif response.question_id in ["negative_detail", "neutral_detail", "positive_detail"]:
                detail_response = response.response_value
            elif response.question_id == "action_question":
                action_response = response.response_value
        
        # Calculate semantic triplet and score
        semantic_triplet, calculated_score = self._calculate_semantic_score(
            overall_rating, detail_response, action_response
        )
        
        # Determine follow-up priority and timeframe
        follow_up_priority, follow_up_timeframe = self._determine_follow_up_parameters(
            overall_rating, detail_response, action_response
        )
        
        feedback = MeetingFeedback(
            feedback_id=str(uuid.uuid4()),
            session_id=session['session_id'],
            intent_id=session['intent_id'],
            respondent_id=session['participant_id'],
            meeting_host_id=session['host_id'],
            meeting_participants=session['all_participants'],
            overall_rating=overall_rating,
            responses=responses,
            calculated_score=calculated_score,
            semantic_triplet=semantic_triplet,
            follow_up_priority=follow_up_priority,
            follow_up_timeframe=follow_up_timeframe,
            follow_up_notes=f"Detail: {detail_response}, Action: {action_response}"
        )
        
        logger.info(f"📊 Feedback processed: {feedback.feedback_id}")
        logger.info(f"   Rating: {overall_rating.value} → Score: {calculated_score}")
        logger.info(f"   Semantic: {semantic_triplet}")
        logger.info(f"   Follow-up: {follow_up_priority.value}")
        
        return feedback

    def _calculate_semantic_score(
        self,
        overall_rating: RatingValue,
        detail_response: str,
        action_response: str
    ) -> Tuple[str, float]:
        """Calculate WSP 25/44 semantic triplet and numerical score"""
        
        # X = Overall rating (0, 1, 2)
        x = str(overall_rating.value)
        
        # Y = Engagement level based on detail response
        engagement_mapping = {
            # Negative details
            "meet_again_low": "0",
            "no_followup": "0", 
            "different_approach": "1",
            # Neutral details
            "better_preparation": "1",
            "clearer_agenda": "1",
            "right_timing": "1",
            "different_format": "1",
            # Positive details
            "productive_discussion": "2",
            "clear_next_steps": "1",
            "good_collaboration": "2",
            "solved_problems": "2"
        }
        y = engagement_mapping.get(detail_response, "1")
        
        # Z = Follow-up intent based on action response
        followup_mapping = {
            "no_followup": "0",
            "when_needed": "1",
            "next_quarter": "1", 
            "next_month": "2",
            "next_week": "2"
        }
        z = followup_mapping.get(action_response, "1")
        
        semantic_triplet = f"{x}{y}{z}"
        
        # Get score from mapping
        score_data = self.semantic_mapping.get(semantic_triplet, {"score": 5.0})
        calculated_score = score_data["score"]
        
        return semantic_triplet, calculated_score

    def _determine_follow_up_parameters(
        self,
        overall_rating: RatingValue,
        detail_response: str,
        action_response: str
    ) -> Tuple[FollowUpPriority, Optional[FollowUpTimeframe]]:
        """Determine follow-up priority and timeframe from responses"""
        
        if action_response == "no_followup":
            return FollowUpPriority.NO_FOLLOWUP, None
        
        # Priority based on overall rating and detail
        if overall_rating == RatingValue.BAD:
            if detail_response == "meet_again_low":
                priority = FollowUpPriority.LOW_PRIORITY
            else:
                priority = FollowUpPriority.NO_FOLLOWUP
        elif overall_rating == RatingValue.OKAY:
            priority = FollowUpPriority.MEDIUM_PRIORITY
        else:  # GOOD
            if action_response == "next_week":
                priority = FollowUpPriority.URGENT_FOLLOWUP
            else:
                priority = FollowUpPriority.HIGH_PRIORITY
        
        # Timeframe mapping
        timeframe_mapping = {
            "next_week": FollowUpTimeframe.NEXT_WEEK,
            "next_month": FollowUpTimeframe.NEXT_MONTH,
            "next_quarter": FollowUpTimeframe.NEXT_QUARTER,
            "when_needed": FollowUpTimeframe.WHEN_NEEDED
        }
        timeframe = timeframe_mapping.get(action_response, FollowUpTimeframe.WHEN_NEEDED)
        
        return priority, timeframe

    async def _create_follow_up_schedule(self, feedback: MeetingFeedback):
        """Create agentic follow-up schedule based on feedback"""
        if feedback.follow_up_timeframe is None:
            return
        
        schedule_id = str(uuid.uuid4())
        
        # Calculate initial priority and target date
        initial_priority = {
            FollowUpPriority.LOW_PRIORITY: 3.0,
            FollowUpPriority.MEDIUM_PRIORITY: 5.0,
            FollowUpPriority.HIGH_PRIORITY: 7.0,
            FollowUpPriority.URGENT_FOLLOWUP: 9.0
        }.get(feedback.follow_up_priority, 5.0)
        
        target_date = None
        if feedback.follow_up_timeframe.value > 0:
            target_date = datetime.now() + timedelta(days=feedback.follow_up_timeframe.value)
        
        schedule = FollowUpSchedule(
            schedule_id=schedule_id,
            original_feedback_id=feedback.feedback_id,
            requester_id=feedback.meeting_host_id,  # Original host wants follow-up
            target_id=feedback.respondent_id,       # Person who gave feedback
            follow_up_intent=f"Follow-up based on {feedback.overall_rating.value}/2 rating",
            base_timeframe_days=feedback.follow_up_timeframe.value,
            current_priority_value=initial_priority,
            target_activation_date=target_date,
            metadata={
                'original_session_id': feedback.session_id,
                'semantic_triplet': feedback.semantic_triplet,
                'calculated_score': feedback.calculated_score
            }
        )
        
        self.follow_up_schedules[schedule_id] = schedule
        
        logger.info(f"📅 Follow-up scheduled: {schedule_id}")
        logger.info(f"   Priority: {feedback.follow_up_priority.value}")
        logger.info(f"   Timeframe: {feedback.follow_up_timeframe.value} days")
        logger.info(f"   Target date: {target_date}")
        
        # Trigger callback
        await self._trigger_callbacks('follow_up_scheduled', schedule, {
            'feedback_id': feedback.feedback_id,
            'priority': feedback.follow_up_priority.value,
            'timeframe_days': feedback.follow_up_timeframe.value
        })

    async def _activate_follow_up_schedule(self, schedule_id: str):
        """Activate a follow-up schedule by creating new meeting intent"""
        schedule = self.follow_up_schedules[schedule_id]
        schedule.status = 'active'
        
        logger.info(f"⚡ Activating follow-up schedule: {schedule_id}")
        
        # This would integrate with Intent Manager to create new meeting intent
        # For now, simulate the activation
        logger.info(f"📝 [SIMULATED] Creating follow-up meeting intent")
        logger.info(f"   From: {schedule.requester_id} → To: {schedule.target_id}")
        logger.info(f"   Priority: {schedule.current_priority_value}/10.0")
        
        await self._trigger_callbacks('follow_up_activated', schedule, {
            'activation_priority': schedule.current_priority_value,
            'days_since_target': (datetime.now() - schedule.target_activation_date).days if schedule.target_activation_date else 0
        })

    async def _notify_requester_of_rejections(self, schedule: FollowUpSchedule):
        """Notify original requester about rejection threshold"""
        logger.info(f"🚨 Notifying requester of rejections: {schedule.requester_id}")
        logger.info(f"   Target: {schedule.target_id}")
        logger.info(f"   Rejection count: {schedule.rejection_count}")
        
        # Simulate notification
        logger.info(f"📧 [SIMULATED] Notification sent to {schedule.requester_id}")
        logger.info(f"   Message: {schedule.target_id} has declined {schedule.rejection_count} follow-up requests")

    async def _auto_downgrade_follow_up(self, schedule_id: str):
        """Automatically downgrade follow-up priority due to rejections"""
        schedule = self.follow_up_schedules[schedule_id]
        
        # Reduce priority significantly
        schedule.current_priority_value = max(1.0, schedule.current_priority_value * 0.3)
        schedule.max_priority_value = schedule.current_priority_value * 2
        schedule.status = 'downgraded'
        
        logger.info(f"📉 Auto-downgraded follow-up: {schedule_id}")
        logger.info(f"   New priority: {schedule.current_priority_value}")
        
        await self._trigger_callbacks('priority_auto_adjusted', schedule, {
            'reason': 'rejection_threshold',
            'new_priority': schedule.current_priority_value
        })

    def _calculate_session_semantic_state(self, session_feedback: List[MeetingFeedback]) -> Dict:
        """Calculate overall semantic state for a session from all feedback"""
        if not session_feedback:
            return {'overall_triplet': '000', 'confidence': 0.0}
        
        # Average the individual semantic scores
        total_score = sum(f.calculated_score for f in session_feedback)
        avg_score = total_score / len(session_feedback)
        
        # Find closest semantic triplet
        closest_triplet = "111"
        closest_distance = float('inf')
        
        for triplet, data in self.semantic_mapping.items():
            distance = abs(data['score'] - avg_score)
            if distance < closest_distance:
                closest_distance = distance
                closest_triplet = triplet
        
        return {
            'overall_triplet': closest_triplet,
            'average_score': avg_score,
            'confidence': 1.0 - (closest_distance / 10.0),
            'feedback_count': len(session_feedback)
        }

    def _generate_session_recommendations(self, session_feedback: List[MeetingFeedback]) -> List[str]:
        """Generate recommendations based on session feedback patterns"""
        if not session_feedback:
            return []
        
        recommendations = []
        
        # Analyze rating distribution
        ratings = [f.overall_rating.value for f in session_feedback]
        avg_rating = sum(ratings) / len(ratings)
        
        if avg_rating < 0.5:
            recommendations.append("Consider restructuring meeting format or agenda")
            recommendations.append("Review meeting preparation and participant selection")
        elif avg_rating < 1.5:
            recommendations.append("Focus on clearer agenda and better preparation")
            recommendations.append("Consider shorter, more focused meetings")
        else:
            recommendations.append("Great meeting format - continue similar approach")
            recommendations.append("Consider scheduling regular follow-ups")
        
        # Analyze follow-up patterns
        follow_up_priorities = [f.follow_up_priority for f in session_feedback]
        high_priority_count = len([p for p in follow_up_priorities if p in [FollowUpPriority.HIGH_PRIORITY, FollowUpPriority.URGENT_FOLLOWUP]])
        
        if high_priority_count > len(session_feedback) * 0.7:
            recommendations.append("High follow-up interest - schedule next meeting soon")
        
        return recommendations

    async def _trigger_callbacks(self, event_type: str, data: Any, metadata: Dict):
        """Trigger registered callbacks for feedback events"""
        callbacks = self.feedback_callbacks.get(event_type, [])
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data, metadata)
                else:
                    callback(data, metadata)
            except Exception as e:
                logger.error(f"❌ Feedback callback error for {event_type}: {e}")

# Factory function for easy integration
def create_post_meeting_feedback_system() -> PostMeetingFeedbackSystem:
    """Factory function to create Post-Meeting Feedback System instance"""
    return PostMeetingFeedbackSystem()

# Example usage and testing
async def demo_post_meeting_feedback():
    """Demonstrate Post-Meeting Feedback System functionality"""
    print("=== Post-Meeting Feedback System Demo ===")
    
    feedback_system = create_post_meeting_feedback_system()
    
    # Simulate post-meeting feedback collection
    session_ids = await feedback_system.initiate_feedback_collection(
        session_id="session_123",
        intent_id="intent_456", 
        participants=["alice", "bob", "charlie"],
        host_id="alice"
    )
    
    print(f"✅ Initiated feedback collection: {len(session_ids)} sessions")
    
    # Simulate feedback responses
    for session_id in session_ids[:1]:  # Just simulate one for demo
        # Question 1: Overall rating = 2 (Good)
        await feedback_system.process_feedback_response(session_id, 2)
        
        # Question 2: Positive detail = productive discussion
        await feedback_system.process_feedback_response(session_id, "productive_discussion")
        
        # Question 3: Action = next week
        await feedback_system.process_feedback_response(session_id, "next_week")
    
    # Get feedback summary
    summary = await feedback_system.get_feedback_summary("session_123")
    print(f"📊 Feedback summary: {summary}")
    
    # Check follow-up schedules
    await asyncio.sleep(1)  # Simulate time passing
    activated = await feedback_system.check_follow_up_schedules()
    print(f"⚡ Activated follow-ups: {activated}")
    
    # Get statistics
    stats = await feedback_system.get_feedback_statistics()
    print(f"📈 Statistics: {stats}")
    
    return feedback_system

if __name__ == "__main__":
    asyncio.run(demo_post_meeting_feedback()) 