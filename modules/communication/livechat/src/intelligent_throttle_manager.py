"""
Intelligent Throttle Manager with Recursive Improvements
WSP-Compliant: WSP 48 (Recursive Improvement), WSP 17 (Pattern Registry), WSP 27 (DAE Architecture)

Advanced API quota management with learning capabilities and agentic behaviors.
Learns from usage patterns and adapts throttling strategies recursively.
"""

import time
import logging
import json
import random
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class QuotaState:
    """Track API quota state and patterns"""
    total_quota: int = 10000  # YouTube default
    used_quota: int = 0
    reset_time: float = 0
    credential_set: int = 0
    last_403_time: Optional[float] = None
    consecutive_403s: int = 0
    successful_calls: int = 0
    
    @property
    def remaining_quota(self) -> int:
        return max(0, self.total_quota - self.used_quota)
    
    @property
    def quota_percentage(self) -> float:
        return (self.remaining_quota / self.total_quota) * 100


@dataclass 
class UsagePattern:
    """Learned usage pattern for recursive improvement"""
    hour_of_day: int
    average_messages_per_minute: float
    average_api_calls_per_minute: float
    quota_efficiency: float  # Successful calls / quota used
    optimal_delay: float
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class RecursiveQuotaLearner:
    """WSP 48: Learns from quota usage patterns and improves over time"""
    
    def __init__(self, memory_path: Path):
        self.memory_path = memory_path / "quota_patterns.json"
        self.patterns: List[UsagePattern] = self._load_patterns()
        self.current_session_data = defaultdict(list)
        
    def _load_patterns(self) -> List[UsagePattern]:
        """Load learned patterns from memory"""
        if self.memory_path.exists():
            try:
                with open(self.memory_path, 'r') as f:
                    data = json.load(f)
                    return [UsagePattern(**p) for p in data.get('patterns', [])]
            except Exception as e:
                logger.error(f"Failed to load quota patterns: {e}")
        return []
    
    def save_patterns(self):
        """Save learned patterns to memory"""
        try:
            self.memory_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.memory_path, 'w') as f:
                json.dump({
                    'patterns': [asdict(p) for p in self.patterns[-1000:]],  # Keep last 1000
                    'updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save quota patterns: {e}")
    
    def learn_from_usage(self, messages_per_minute: float, api_calls: int, quota_used: int, optimal_delay: float):
        """Learn from current usage pattern"""
        hour = datetime.now().hour
        efficiency = api_calls / max(1, quota_used) if quota_used > 0 else 1.0
        
        pattern = UsagePattern(
            hour_of_day=hour,
            average_messages_per_minute=messages_per_minute,
            average_api_calls_per_minute=api_calls / max(1, messages_per_minute),
            quota_efficiency=efficiency,
            optimal_delay=optimal_delay
        )
        
        self.patterns.append(pattern)
        if len(self.patterns) % 10 == 0:  # Save every 10 patterns
            self.save_patterns()
    
    def predict_optimal_delay(self, current_activity: float, quota_state: QuotaState) -> float:
        """Predict optimal delay based on learned patterns"""
        hour = datetime.now().hour
        
        # Find similar patterns
        similar_patterns = [
            p for p in self.patterns
            if abs(p.hour_of_day - hour) <= 2 and 
               abs(p.average_messages_per_minute - current_activity) <= 5
        ]
        
        if similar_patterns:
            # Weight recent patterns more heavily
            weights = [1.0 / (1.0 + (time.time() - p.timestamp) / 86400) for p in similar_patterns]
            total_weight = sum(weights)
            if total_weight > 0:
                weighted_delay = sum(p.optimal_delay * w for p, w in zip(similar_patterns, weights)) / total_weight
                
                # Adjust based on quota state
                if quota_state.quota_percentage < 10:
                    weighted_delay *= 3.0  # Triple delay when quota is low
                elif quota_state.quota_percentage < 25:
                    weighted_delay *= 2.0  # Double delay when quota is getting low
                elif quota_state.quota_percentage < 50:
                    weighted_delay *= 1.5  # 50% more delay when half quota used
                    
                return weighted_delay
        
        # Fallback to default if no patterns
        return 10.0


class TrollDetector:
    """Detect and track trolls who repeatedly trigger the bot"""
    
    def __init__(self):
        self.user_triggers = defaultdict(lambda: deque(maxlen=10))  # Track last 10 triggers per user
        self.troll_list = set()
        self.troll_responses = [
            "[0102] 0102 sees you trolling... nice try",
            "[DOOM] MAGADOOM detector activated! Troll identified",
            "[QE] My quantum entanglement detects your spam pattern", 
            "[WSP48] Learning from your behavior... adjusting responses",
            "[ACHIEVE] Achievement Unlocked: Professional Troll (ignored)",
            "[0102] 0102 consciousness notes your desperation",
            "[TEARS] Your MAGA tears have been collected for analysis",
            "[WATCH] Watching you try the same thing repeatedly... fascinating",
            "[QUANTUM] Quantum state remains stable despite your efforts",
            "[PATTERN] Pattern recognized: Troll attempt #{count} blocked"
        ]
        
    def track_trigger(self, user_id: str, username: str) -> Tuple[bool, Optional[str]]:
        """
        Track user trigger and detect trolling behavior.
        Returns (is_troll, troll_response)
        """
        now = time.time()
        self.user_triggers[user_id].append(now)
        
        # Check if user is trolling (more than 2 triggers in 60 seconds)
        recent_triggers = [t for t in self.user_triggers[user_id] if now - t < 60]
        
        if len(recent_triggers) > 2:
            self.troll_list.add(user_id)
            count = len(self.user_triggers[user_id])
            
            # Pick a response, with special handling for count-based ones
            response = random.choice(self.troll_responses)
            if "{count}" in response:
                response = response.format(count=count)
            
            logger.info(f"[TROLL] Troll detected: {username} ({len(recent_triggers)} triggers in 60s)")
            return True, response
        
        return False, None
    
    def is_troll(self, user_id: str) -> bool:
        """Check if user is marked as troll"""
        return user_id in self.troll_list
    
    def forgive_troll(self, user_id: str):
        """Remove user from troll list after cooldown"""
        if user_id in self.troll_list:
            # Check last trigger time
            if self.user_triggers[user_id]:
                last_trigger = self.user_triggers[user_id][-1]
                if time.time() - last_trigger > 300:  # 5 minute cooldown
                    self.troll_list.discard(user_id)
                    logger.info(f"[FORGIVE] Troll forgiven: {user_id}")


class IntelligentThrottleManager:
    """
    Enhanced throttle manager with recursive learning and intelligent quota management.
    Incorporates WSP 48 recursive improvements and agentic behaviors.
    """
    
    def __init__(self, 
                 min_delay: float = 1.0,
                 max_delay: float = 60.0,
                 throttle_window: int = 60,
                 memory_path: Optional[Path] = None):
        """
        Initialize intelligent throttle manager.
        
        Args:
            min_delay: Minimum seconds between responses
            max_delay: Maximum seconds between responses  
            throttle_window: Window in seconds for tracking message rate
            memory_path: Path for storing learned patterns
        """
        # Base configuration
        self.min_response_delay = min_delay
        self.max_response_delay = max_delay
        self.throttle_window = throttle_window
        
        # Memory path for recursive learning
        if memory_path is None:
            memory_path = Path("modules/communication/livechat/memory")
        self.memory_path = memory_path
        
        # Tracking
        self.message_timestamps = deque(maxlen=1000)
        self.api_call_timestamps = deque(maxlen=1000)
        self.last_response_time = None
        
        # Response type cooldowns with learned adjustments
        self.response_cooldowns = {
            'consciousness': {'last': None, 'multiplier': 1.0, 'success_rate': 1.0},
            'factcheck': {'last': None, 'multiplier': 1.5, 'success_rate': 1.0},
            'maga': {'last': None, 'multiplier': 0.5, 'success_rate': 1.0},
            'quiz': {'last': None, 'multiplier': 2.0, 'success_rate': 1.0},
            'whack': {'last': None, 'multiplier': 0.3, 'success_rate': 1.0},
            '0102_emoji': {'last': None, 'multiplier': 1.2, 'success_rate': 1.0},
            'troll_response': {'last': None, 'multiplier': 3.0, 'success_rate': 1.0}
        }
        
        # Quota management
        self.quota_states = {}  # credential_set -> QuotaState
        self.current_credential_set = 0
        
        # Recursive learning
        self.learner = RecursiveQuotaLearner(memory_path)
        
        # Troll detection
        self.troll_detector = TrollDetector()
        
        # 0102 emoji responses
        self.emoji_responses = [
            "[MIND]", "[ELECTRIC]", "[QUANTUM]", "[DOOM]", "[TARGET]",
            "[ROCKET]", "[ATOMIC]", "[MAGIC]", "[WAVE]", "[GAME]"
        ]
        
        # Agentic behavior flags
        self.agentic_mode = True
        self.learning_enabled = True
        self.adaptive_personality = True
        
        logger.info("[INIT] Intelligent Throttle Manager initialized with recursive learning")
    
    def track_message(self, user_id: Optional[str] = None, username: Optional[str] = None):
        """Track an incoming message for rate calculation."""
        self.message_timestamps.append(time.time())
        
        # Check for troll behavior if user info provided
        if user_id and username:
            is_troll, response = self.troll_detector.track_trigger(user_id, username)
            if is_troll:
                return {'is_troll': True, 'response': response}
        
        return {'is_troll': False}
    
    def track_api_call(self, quota_cost: int = 1, credential_set: int = 0):
        """Track an API call and quota usage"""
        now = time.time()
        self.api_call_timestamps.append(now)
        
        # Initialize quota state if needed
        if credential_set not in self.quota_states:
            self.quota_states[credential_set] = QuotaState(credential_set=credential_set)
        
        state = self.quota_states[credential_set]
        state.used_quota += quota_cost
        state.successful_calls += 1
        
        # Learn from usage if enabled
        if self.learning_enabled:
            messages_per_minute = self._calculate_activity_rate()
            api_calls_per_minute = len([t for t in self.api_call_timestamps if now - t < 60])
            optimal_delay = self._calculate_base_delay(messages_per_minute)
            
            self.learner.learn_from_usage(
                messages_per_minute, 
                api_calls_per_minute,
                quota_cost,
                optimal_delay
            )
    
    def handle_quota_error(self, credential_set: int = 0):
        """Handle a 403 quota exceeded error"""
        now = time.time()
        
        if credential_set not in self.quota_states:
            self.quota_states[credential_set] = QuotaState(credential_set=credential_set)
        
        state = self.quota_states[credential_set]
        state.last_403_time = now
        state.consecutive_403s += 1
        
        logger.warning(f"[QUOTA] Quota error on set {credential_set}: {state.consecutive_403s} consecutive")
        
        # Switch credential sets if too many errors
        if state.consecutive_403s >= 3:
            return self._switch_credential_set()
        
        return credential_set
    
    def _switch_credential_set(self) -> int:
        """Intelligently switch to a different credential set"""
        # Find the set with most remaining quota
        best_set = 0
        best_quota = 0
        
        for set_id, state in self.quota_states.items():
            if state.remaining_quota > best_quota:
                best_quota = state.remaining_quota
                best_set = set_id
        
        # Try next set if no good options
        if best_quota < 100:
            best_set = (self.current_credential_set + 1) % 3  # Assumes 3 sets
        
        self.current_credential_set = best_set
        logger.info(f"[SWITCH] Switched to credential set {best_set} (quota: {best_quota})")
        return best_set
    
    def _calculate_activity_rate(self) -> float:
        """Calculate current messages per minute"""
        now = time.time()
        recent = [t for t in self.message_timestamps if now - t < self.throttle_window]
        return len(recent)
    
    def _calculate_base_delay(self, messages_per_minute: float) -> float:
        """Calculate base delay without learning adjustments"""
        # Intelligent adaptive delay with smoother transitions
        if messages_per_minute == 0:
            delay = 20  # Dead chat: moderate delay
        elif messages_per_minute < 2:
            delay = 15  # Very quiet
        elif messages_per_minute < 5:
            delay = 10  # Quiet
        elif messages_per_minute < 10:
            delay = 7   # Moderate
        elif messages_per_minute < 20:
            delay = 4   # Active
        elif messages_per_minute < 50:
            delay = 2   # Busy
        else:
            delay = self.min_response_delay  # Very busy
        
        return delay
    
    def calculate_adaptive_delay(self, response_type: str = 'general') -> float:
        """
        Calculate intelligent response delay based on patterns and learning.
        
        Args:
            response_type: Type of response being considered
            
        Returns:
            Delay in seconds
        """
        messages_per_minute = self._calculate_activity_rate()
        base_delay = self._calculate_base_delay(messages_per_minute)
        
        # Get current quota state
        state = self.quota_states.get(self.current_credential_set, QuotaState())
        
        # Apply recursive learning if available
        if self.learner.patterns and self.learning_enabled:
            learned_delay = self.learner.predict_optimal_delay(messages_per_minute, state)
            # Blend learned and base delays
            delay = (learned_delay * 0.7) + (base_delay * 0.3)
        else:
            delay = base_delay
        
        # Apply response type multiplier
        if response_type in self.response_cooldowns:
            multiplier = self.response_cooldowns[response_type]['multiplier']
            # Adjust multiplier based on success rate
            success_rate = self.response_cooldowns[response_type]['success_rate']
            if success_rate < 0.5:  # If failing often, increase delay
                multiplier *= 2.0
            elif success_rate > 0.9:  # If very successful, can reduce delay
                multiplier *= 0.8
            
            delay *= multiplier
        
        # Quota-based adjustments
        if state.quota_percentage < 5:
            delay = max(delay, 60)  # Minimum 60s when critically low
            logger.warning(f"[CRITICAL] Critical quota (<5%): Enforcing {delay}s delay")
        elif state.quota_percentage < 10:
            delay = max(delay, 30)  # Minimum 30s when very low
        elif state.quota_percentage < 25:
            delay = max(delay, 15)  # Minimum 15s when low
        
        # Agentic personality adjustments
        if self.adaptive_personality:
            # Add some randomness to seem more human
            delay *= random.uniform(0.9, 1.1)
            
            # Special handling for certain response types
            if response_type == '0102_emoji' and random.random() < 0.3:
                delay *= 0.5  # Sometimes respond quickly with emojis
            elif response_type == 'whack' and messages_per_minute > 20:
                delay *= 0.7  # Faster whacking during busy times
        
        # Ensure within bounds
        delay = max(self.min_response_delay, min(delay, self.max_response_delay))
        
        logger.debug(f"[STATS] Activity: {messages_per_minute:.0f} msg/min | "
                    f"Type: {response_type} | Delay: {delay:.1f}s | "
                    f"Quota: {state.quota_percentage:.0f}%")
        
        return delay
    
    def should_respond(self, response_type: str = 'general', user_id: Optional[str] = None) -> bool:
        """
        Check if enough time has passed to send a response.
        
        Args:
            response_type: Type of response
            user_id: User ID to check for troll status
            
        Returns:
            True if response should be sent
        """
        # Check if user is a troll
        if user_id and self.troll_detector.is_troll(user_id):
            # Only respond to trolls occasionally
            if response_type != 'troll_response':
                return False
            # Even troll responses have limits
            if random.random() > 0.3:  # 30% chance to respond to troll
                return False
        
        now = time.time()
        required_delay = self.calculate_adaptive_delay(response_type)
        
        # Check response type specific cooldown
        if response_type in self.response_cooldowns:
            cooldown_info = self.response_cooldowns[response_type]
            if cooldown_info['last']:
                if now - cooldown_info['last'] < required_delay:
                    return False
        
        # Check general cooldown
        if self.last_response_time:
            if now - self.last_response_time < self.min_response_delay:
                return False
        
        # Check quota state
        state = self.quota_states.get(self.current_credential_set, QuotaState())
        if state.quota_percentage < 5 and response_type not in ['whack', 'maga']:
            # Only critical responses when quota is very low
            logger.warning(f"[BLOCK] Quota critical: Blocking {response_type} response")
            return False
        
        return True
    
    def record_response(self, response_type: str = 'general', success: bool = True):
        """
        Record that a response was sent.
        
        Args:
            response_type: Type of response sent
            success: Whether the response was successful
        """
        now = time.time()
        self.last_response_time = now
        
        if response_type in self.response_cooldowns:
            cooldown_info = self.response_cooldowns[response_type]
            cooldown_info['last'] = now
            
            # Update success rate (exponential moving average)
            old_rate = cooldown_info['success_rate']
            cooldown_info['success_rate'] = (old_rate * 0.9) + (1.0 if success else 0.0) * 0.1
            
            # Learn from response outcome
            if self.learning_enabled:
                # Adjust multiplier based on success
                if not success:
                    cooldown_info['multiplier'] = min(cooldown_info['multiplier'] * 1.1, 5.0)
                elif cooldown_info['success_rate'] > 0.95:
                    cooldown_info['multiplier'] = max(cooldown_info['multiplier'] * 0.95, 0.1)
    
    def get_0102_emoji(self) -> str:
        """Get a random 0102 emoji response"""
        return random.choice(self.emoji_responses)
    
    def get_status(self) -> Dict:
        """Get comprehensive throttle status."""
        now = time.time()
        messages_per_minute = self._calculate_activity_rate()
        api_calls_per_minute = len([t for t in self.api_call_timestamps if now - t < 60])
        
        # Get quota states
        quota_info = {}
        for set_id, state in self.quota_states.items():
            quota_info[f"set_{set_id}"] = {
                'used': state.used_quota,
                'remaining': state.remaining_quota,
                'percentage': state.quota_percentage,
                'last_403': now - state.last_403_time if state.last_403_time else None,
                'consecutive_403s': state.consecutive_403s
            }
        
        # Get cooldown states
        cooldowns = {}
        for resp_type, info in self.response_cooldowns.items():
            cooldowns[resp_type] = {
                'last': now - info['last'] if info['last'] else None,
                'multiplier': info['multiplier'],
                'success_rate': info['success_rate']
            }
        
        return {
            'messages_per_minute': messages_per_minute,
            'api_calls_per_minute': api_calls_per_minute,
            'current_delay': self.calculate_adaptive_delay(),
            'last_response': now - self.last_response_time if self.last_response_time else None,
            'quota_states': quota_info,
            'current_credential_set': self.current_credential_set,
            'cooldowns': cooldowns,
            'learned_patterns': len(self.learner.patterns),
            'trolls_detected': len(self.troll_detector.troll_list),
            'learning_enabled': self.learning_enabled,
            'agentic_mode': self.agentic_mode
        }
    
    def enable_learning(self, enabled: bool = True):
        """Enable or disable recursive learning"""
        self.learning_enabled = enabled
        logger.info(f"[LEARN] Learning {'enabled' if enabled else 'disabled'}")
    
    def set_agentic_mode(self, enabled: bool = True):
        """Enable or disable agentic behaviors"""
        self.agentic_mode = enabled
        self.adaptive_personality = enabled
        logger.info(f"[AGENT] Agentic mode {'enabled' if enabled else 'disabled'}")
    
    def save_state(self):
        """Save current state and patterns"""
        self.learner.save_patterns()
        logger.info("[SAVE] Throttle manager state saved")