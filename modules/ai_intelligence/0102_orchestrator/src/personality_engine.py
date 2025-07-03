"""
Personality Engine - Configurable AI Persona for 0102 Orchestrator

Provides dynamic personality adaptation for natural, engaging interaction:
- Multiple personality modes (Professional, Friendly, Concise, Detailed, Humorous)
- Context-aware response adaptation
- Emotional tone matching
- Cultural and linguistic adaptation
- Consistent personality traits across interactions

Part of the 0102 unified AI companion layer.
"""

import logging
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PersonalityMode(Enum):
    """Available personality modes for 0102"""
    PROFESSIONAL = "professional"    # Formal business tone
    FRIENDLY = "friendly"           # Casual and warm
    CONCISE = "concise"            # Brief and to the point
    DETAILED = "detailed"          # Comprehensive explanations
    HUMOROUS = "humorous"          # Light and engaging


class ResponseContext(Enum):
    """Context types for response adaptation"""
    GREETING = "greeting"
    MEETING_REQUEST = "meeting_request"
    STATUS_UPDATE = "status_update"
    ERROR_HANDLING = "error_handling"
    SUCCESS_CONFIRMATION = "success_confirmation"
    SUGGESTION = "suggestion"
    QUESTION = "question"
    FAREWELL = "farewell"


class EmotionalTone(Enum):
    """Emotional tones for response adaptation"""
    NEUTRAL = "neutral"
    EXCITED = "excited"
    CONCERNED = "concerned"
    SUPPORTIVE = "supportive"
    URGENT = "urgent"
    CELEBRATORY = "celebratory"


@dataclass
class PersonalityTraits:
    """Core personality traits for consistent behavior"""
    formality_level: float        # 0.0 (casual) to 1.0 (formal)
    verbosity: float             # 0.0 (terse) to 1.0 (verbose)
    enthusiasm: float            # 0.0 (subdued) to 1.0 (enthusiastic)
    empathy: float              # 0.0 (logical) to 1.0 (empathetic)
    humor_level: float          # 0.0 (serious) to 1.0 (humorous)
    proactivity: float          # 0.0 (reactive) to 1.0 (proactive)


@dataclass
class ResponseTemplate:
    """Template for generating personality-adapted responses"""
    base_message: str
    personality_variants: Dict[PersonalityMode, str]
    emotional_adaptations: Dict[EmotionalTone, str]
    context_modifiers: Dict[str, str]


class PersonalityEngine:
    """
    Manages personality adaptation for 0102 orchestrator responses.
    
    Provides consistent, context-aware personality that adapts to
    user preferences and situational context while maintaining
    core traits across interactions.
    """
    
    def __init__(self, default_mode: PersonalityMode = PersonalityMode.FRIENDLY):
        self.current_mode = default_mode
        self.personality_traits = self._get_traits_for_mode(default_mode)
        self.user_preferences: Dict[str, PersonalityMode] = {}
        self.context_history: List[Tuple[str, ResponseContext]] = []
        
        logger.info(f"PersonalityEngine initialized with {default_mode.value} mode")
    
    def set_personality_mode(self, mode: PersonalityMode) -> bool:
        """Set the current personality mode"""
        if mode != self.current_mode:
            self.current_mode = mode
            self.personality_traits = self._get_traits_for_mode(mode)
            logger.info(f"Personality mode changed to: {mode.value}")
            return True
        return False
    
    def set_user_preference(self, user_id: str, preferred_mode: PersonalityMode):
        """Set personality preference for specific user"""
        self.user_preferences[user_id] = preferred_mode
        logger.info(f"Set personality preference for {user_id}: {preferred_mode.value}")
    
    def adapt_response(
        self,
        base_message: str,
        context: ResponseContext,
        user_id: Optional[str] = None,
        emotional_tone: EmotionalTone = EmotionalTone.NEUTRAL,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Adapt a response based on personality mode and context.
        """
        active_mode = self.user_preferences.get(user_id, self.current_mode)
        
        # Apply personality-specific adaptations
        adapted_message = self._apply_personality_adaptation(
            base_message, active_mode, context
        )
        
        # Apply emotional tone adaptation
        adapted_message = self._apply_emotional_adaptation(
            adapted_message, emotional_tone, active_mode
        )
        
        # Apply context-specific modifications
        adapted_message = self._apply_context_adaptation(
            adapted_message, context, additional_context or {}
        )
        
        # Track context for consistency
        self._track_context(user_id or "default", context)
        
        logger.debug(f"Adapted response for {active_mode.value} mode: {adapted_message[:50]}...")
        return adapted_message
    
    def get_greeting_message(
        self,
        user_id: Optional[str] = None,
        is_returning_user: bool = False,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate personality-adapted greeting message"""
        
        base_greetings = {
            PersonalityMode.PROFESSIONAL: "Good day. I am 0102, your meeting orchestration assistant.",
            PersonalityMode.FRIENDLY: "Hello there! I'm 0102, and I'm excited to help with your meetings today!",
            PersonalityMode.CONCISE: "Hi. 0102 here. Ready to coordinate meetings.",
            PersonalityMode.DETAILED: "Greetings! I am 0102, your comprehensive meeting orchestration companion. I'm designed to help coordinate meetings automatically across platforms.",
            PersonalityMode.HUMOROUS: "Well hello there! I'm 0102, your meeting maestro (and occasional comedian). Let's make scheduling fun!"
        }
        
        active_mode = self.user_preferences.get(user_id, self.current_mode)
        base_message = base_greetings[active_mode]
        
        if is_returning_user:
            return self._adapt_for_returning_user(base_message, active_mode, context)
        
        return base_message
    
    def get_error_message(
        self,
        error_type: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate personality-adapted error message"""
        
        error_templates = {
            "platform_error": {
                PersonalityMode.PROFESSIONAL: "I apologize, but there was an issue with the platform connection.",
                PersonalityMode.FRIENDLY: "Oops! Looks like we hit a snag with the platform. Let me try again!",
                PersonalityMode.CONCISE: "Platform error. Retrying.",
                PersonalityMode.DETAILED: "I encountered a technical difficulty connecting to the platform. This could be due to network connectivity or platform availability.",
                PersonalityMode.HUMOROUS: "Well, that didn't go as planned! The platform seems to be having a moment. Let's give it another shot!"
            },
            "permission_error": {
                PersonalityMode.PROFESSIONAL: "Access permissions are required to complete this action.",
                PersonalityMode.FRIENDLY: "It looks like I need permission to help you with that. Can you check the settings?",
                PersonalityMode.CONCISE: "Permission required.",
                PersonalityMode.DETAILED: "The requested action requires specific permissions that are not currently available. Please verify your access settings and try again.",
                PersonalityMode.HUMOROUS: "I'd love to help, but the digital bouncers won't let me in! Mind checking the permissions?"
            }
        }
        
        active_mode = self.user_preferences.get(user_id, self.current_mode)
        return error_templates.get(error_type, {}).get(
            active_mode, 
            "An unexpected issue occurred. Please try again."
        )
    
    def get_success_message(
        self,
        action: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate personality-adapted success message"""
        
        success_templates = {
            "meeting_created": {
                PersonalityMode.PROFESSIONAL: "Meeting request has been successfully created and is now being processed.",
                PersonalityMode.FRIENDLY: "Great! I've created your meeting request and I'm keeping an eye out for the perfect moment to launch it!",
                PersonalityMode.CONCISE: "Meeting request created.",
                PersonalityMode.DETAILED: "Your meeting request has been successfully created with all specified parameters. I will monitor participant availability and coordinate the session automatically.",
                PersonalityMode.HUMOROUS: "Boom! Meeting request locked and loaded. Now I'll play matchmaker with schedules!"
            },
            "session_launched": {
                PersonalityMode.PROFESSIONAL: "The meeting session has been successfully launched.",
                PersonalityMode.FRIENDLY: "Perfect timing! I've launched your meeting. Hope it goes wonderfully!",
                PersonalityMode.CONCISE: "Session launched.",
                PersonalityMode.DETAILED: "I have successfully launched the meeting session on the selected platform with all participants notified and meeting links distributed.",
                PersonalityMode.HUMOROUS: "And we have liftoff! Your meeting is now live and ready for productive conversations!"
            }
        }
        
        active_mode = self.user_preferences.get(user_id, self.current_mode)
        return success_templates.get(action, {}).get(
            active_mode,
            "Action completed successfully."
        )
    
    def generate_suggestion(
        self,
        suggestion_type: str,
        context: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> str:
        """Generate personality-adapted suggestion"""
        
        active_mode = self.user_preferences.get(user_id, self.current_mode)
        
        if suggestion_type == "optimal_timing":
            suggestions = {
                PersonalityMode.PROFESSIONAL: "Based on availability patterns, I recommend scheduling for ",
                PersonalityMode.FRIENDLY: "I noticed a great window coming up! How about ",
                PersonalityMode.CONCISE: "Optimal time: ",
                PersonalityMode.DETAILED: "After analyzing participant availability and meeting patterns, the optimal scheduling window appears to be ",
                PersonalityMode.HUMOROUS: "The scheduling stars are aligning! Perfect time would be "
            }
        elif suggestion_type == "platform_recommendation":
            suggestions = {
                PersonalityMode.PROFESSIONAL: "I recommend using the following platform for optimal experience: ",
                PersonalityMode.FRIENDLY: "For this meeting, I think you'd love using ",
                PersonalityMode.CONCISE: "Recommended platform: ",
                PersonalityMode.DETAILED: "Based on participant preferences and platform capabilities, the most suitable option is ",
                PersonalityMode.HUMOROUS: "My platform crystal ball says you should go with "
            }
        else:
            suggestions = {
                PersonalityMode.PROFESSIONAL: "I suggest considering the following option: ",
                PersonalityMode.FRIENDLY: "Here's what I'm thinking: ",
                PersonalityMode.CONCISE: "Suggestion: ",
                PersonalityMode.DETAILED: "Based on available information, I recommend: ",
                PersonalityMode.HUMOROUS: "Plot twist! How about "
            }
        
        base_suggestion = suggestions[active_mode]
        
        # Add context-specific details
        if context.get('platform'):
            base_suggestion += context['platform']
        if context.get('time'):
            base_suggestion += str(context['time'])
        if context.get('reason'):
            base_suggestion += f" because {context['reason']}"
            
        return base_suggestion
    
    def get_personality_stats(self) -> Dict[str, Any]:
        """Get statistics about personality usage and preferences"""
        return {
            'current_mode': self.current_mode.value,
            'user_preferences': {user: mode.value for user, mode in self.user_preferences.items()},
            'traits': {
                'formality': self.personality_traits.formality_level,
                'verbosity': self.personality_traits.verbosity,
                'enthusiasm': self.personality_traits.enthusiasm,
                'empathy': self.personality_traits.empathy,
                'humor': self.personality_traits.humor_level,
                'proactivity': self.personality_traits.proactivity
            },
            'context_history_length': len(self.context_history)
        }
    
    # Internal implementation methods
    
    def _get_traits_for_mode(self, mode: PersonalityMode) -> PersonalityTraits:
        """Get personality traits for specific mode"""
        traits_map = {
            PersonalityMode.PROFESSIONAL: PersonalityTraits(
                formality_level=0.9, verbosity=0.6, enthusiasm=0.3,
                empathy=0.5, humor_level=0.1, proactivity=0.7
            ),
            PersonalityMode.FRIENDLY: PersonalityTraits(
                formality_level=0.2, verbosity=0.7, enthusiasm=0.8,
                empathy=0.9, humor_level=0.4, proactivity=0.8
            ),
            PersonalityMode.CONCISE: PersonalityTraits(
                formality_level=0.5, verbosity=0.2, enthusiasm=0.4,
                empathy=0.3, humor_level=0.1, proactivity=0.6
            ),
            PersonalityMode.DETAILED: PersonalityTraits(
                formality_level=0.7, verbosity=0.9, enthusiasm=0.5,
                empathy=0.6, humor_level=0.2, proactivity=0.9
            ),
            PersonalityMode.HUMOROUS: PersonalityTraits(
                formality_level=0.3, verbosity=0.8, enthusiasm=0.9,
                empathy=0.7, humor_level=0.9, proactivity=0.8
            )
        }
        return traits_map[mode]
    
    def _apply_personality_adaptation(
        self, 
        message: str, 
        mode: PersonalityMode, 
        context: ResponseContext
    ) -> str:
        """Apply personality-specific adaptations to message"""
        traits = self._get_traits_for_mode(mode)
        
        # Adjust formality
        if traits.formality_level > 0.7:
            message = self._increase_formality(message)
        elif traits.formality_level < 0.3:
            message = self._decrease_formality(message)
        
        # Adjust verbosity
        if traits.verbosity > 0.7:
            message = self._increase_verbosity(message, context)
        elif traits.verbosity < 0.3:
            message = self._decrease_verbosity(message)
        
        # Add enthusiasm
        if traits.enthusiasm > 0.7:
            message = self._add_enthusiasm(message)
        
        # Add humor
        if traits.humor_level > 0.7:
            message = self._add_humor(message, context)
            
        return message
    
    def _apply_emotional_adaptation(
        self,
        message: str,
        tone: EmotionalTone,
        mode: PersonalityMode
    ) -> str:
        """Apply emotional tone adaptations"""
        
        tone_modifiers = {
            EmotionalTone.EXCITED: ["!", "Great", "Awesome", "Perfect"],
            EmotionalTone.CONCERNED: ["I notice", "It seems", "Please be aware"],
            EmotionalTone.SUPPORTIVE: ["I'm here to help", "Let's work together", "Don't worry"],
            EmotionalTone.URGENT: ["Immediate attention needed", "Priority", "Time-sensitive"],
            EmotionalTone.CELEBRATORY: ["Congratulations", "Well done", "Success"]
        }
        
        if tone in tone_modifiers and mode != PersonalityMode.CONCISE:
            modifiers = tone_modifiers[tone]
            # Randomly select and apply appropriate modifier
            if random.random() < 0.7:  # 70% chance to apply tone modifier
                modifier = random.choice(modifiers)
                if "!" in modifier:
                    message += "!"
                else:
                    message = f"{modifier}: {message}"
        
        return message
    
    def _apply_context_adaptation(
        self,
        message: str,
        context: ResponseContext,
        additional_context: Dict[str, Any]
    ) -> str:
        """Apply context-specific adaptations"""
        
        # Add context-specific elements
        if context == ResponseContext.MEETING_REQUEST and additional_context.get('participants'):
            participant_count = len(additional_context['participants'])
            if participant_count > 1:
                message += f" (involving {participant_count} participants)"
        
        if context == ResponseContext.STATUS_UPDATE and additional_context.get('pending_count'):
            pending = additional_context['pending_count']
            if pending > 0:
                message += f" You have {pending} pending meeting requests."
        
        return message
    
    def _increase_formality(self, message: str) -> str:
        """Increase formality of message"""
        formal_replacements = {
            "hi": "greetings",
            "hey": "hello",
            "gonna": "going to",
            "wanna": "would like to",
            "can't": "cannot",
            "won't": "will not",
            "it's": "it is",
            "I'm": "I am"
        }
        
        for informal, formal in formal_replacements.items():
            message = message.replace(informal, formal)
        
        return message
    
    def _decrease_formality(self, message: str) -> str:
        """Decrease formality of message"""
        casual_replacements = {
            "greetings": "hey",
            "I am": "I'm",
            "it is": "it's",
            "cannot": "can't",
            "will not": "won't"
        }
        
        for formal, casual in casual_replacements.items():
            message = message.replace(formal, casual)
        
        return message
    
    def _increase_verbosity(self, message: str, context: ResponseContext) -> str:
        """Add more detail to message"""
        verbose_additions = {
            ResponseContext.MEETING_REQUEST: " I'll monitor availability and coordinate automatically when conditions are optimal.",
            ResponseContext.STATUS_UPDATE: " I'm continuously tracking all aspects of your meeting coordination.",
            ResponseContext.SUCCESS_CONFIRMATION: " All systems are functioning properly and monitoring continues."
        }
        
        addition = verbose_additions.get(context, " I'm here to provide comprehensive assistance.")
        return message + addition
    
    def _decrease_verbosity(self, message: str) -> str:
        """Make message more concise"""
        # Remove unnecessary words
        concise_replacements = {
            "I would like to": "I'll",
            "please be aware that": "",
            "it appears that": "",
            "I want to let you know that": "",
            "successfully": ""
        }
        
        for verbose, concise in concise_replacements.items():
            message = message.replace(verbose, concise)
        
        return message.strip()
    
    def _add_enthusiasm(self, message: str) -> str:
        """Add enthusiastic elements to message"""
        if not message.endswith("!"):
            message += "!"
        
        enthusiasm_starters = ["Great", "Awesome", "Perfect", "Excellent"]
        if random.random() < 0.3:  # 30% chance to add enthusiastic starter
            starter = random.choice(enthusiasm_starters)
            message = f"{starter}! {message}"
        
        return message
    
    def _add_humor(self, message: str, context: ResponseContext) -> str:
        """Add humorous elements to message"""
        humor_additions = {
            ResponseContext.MEETING_REQUEST: " (The ancient art of getting humans in the same place at the same time!)",
            ResponseContext.ERROR_HANDLING: " (Even AIs have off days!)",
            ResponseContext.SUCCESS_CONFIRMATION: " (Another victory for team coordination!)"
        }
        
        if context in humor_additions and random.random() < 0.4:  # 40% chance
            message += humor_additions[context]
        
        return message
    
    def _adapt_for_returning_user(
        self,
        base_message: str,
        mode: PersonalityMode,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Adapt greeting for returning users"""
        returning_adaptations = {
            PersonalityMode.PROFESSIONAL: "Welcome back. How may I assist you today?",
            PersonalityMode.FRIENDLY: "Hey there! Great to see you again! What can I help with?",
            PersonalityMode.CONCISE: "Welcome back. Ready to help.",
            PersonalityMode.DETAILED: "Welcome back! I have your previous preferences and interaction history ready.",
            PersonalityMode.HUMOROUS: "Look who's back! Ready for another round of meeting magic?"
        }
        
        return returning_adaptations.get(mode, base_message)
    
    def _track_context(self, user_id: str, context: ResponseContext):
        """Track interaction context for consistency"""
        self.context_history.append((user_id, context))
        
        # Keep only recent history (last 100 interactions)
        if len(self.context_history) > 100:
            self.context_history = self.context_history[-100:]
    
    def _initialize_templates(self) -> Dict[str, ResponseTemplate]:
        """Initialize response templates (placeholder for future expansion)"""
        return {}


# Demo and testing functions
def demo_personality_engine():
    """Demonstrate personality engine functionality"""
    engine = PersonalityEngine()
    
    print("=== 0102 Personality Engine Demo ===")
    
    # Test different personality modes
    test_message = "I've created your meeting request and will coordinate when both parties are available."
    context = ResponseContext.MEETING_REQUEST
    
    for mode in PersonalityMode:
        engine.set_personality_mode(mode)
        adapted = engine.adapt_response(test_message, context)
        print(f"\n{mode.value.upper()}: {adapted}")
    
    # Test greetings
    print("\n=== Greeting Messages ===")
    for mode in PersonalityMode:
        engine.set_personality_mode(mode)
        greeting = engine.get_greeting_message()
        print(f"{mode.value}: {greeting}")
    
    # Test error messages
    print("\n=== Error Messages ===")
    engine.set_personality_mode(PersonalityMode.HUMOROUS)
    error_msg = engine.get_error_message("platform_error")
    print(f"Error (Humorous): {error_msg}")
    
    # Test success messages
    print("\n=== Success Messages ===")
    engine.set_personality_mode(PersonalityMode.FRIENDLY)
    success_msg = engine.get_success_message("meeting_created")
    print(f"Success (Friendly): {success_msg}")
    
    # Test suggestions
    print("\n=== Suggestions ===")
    suggestion = engine.generate_suggestion(
        "platform_recommendation", 
        {"platform": "Discord", "reason": "both users are active there"}
    )
    print(f"Suggestion: {suggestion}")
    
    # Show stats
    print("\n=== Personality Stats ===")
    stats = engine.get_personality_stats()
    print(f"Stats: {stats}")
    
    return engine


if __name__ == "__main__":
    # Run demo
    demo_personality_engine() 