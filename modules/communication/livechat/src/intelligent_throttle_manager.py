"""
Intelligent Throttle Manager with QWEN Integration

Adaptive throttling system for YouTube API calls with QWEN intelligence.
Uses learning and AI to prevent quota exhaustion while maintaining responsiveness.
QWEN aggressively manages API drain by prioritizing valuable responses over banter.

NAVIGATION: Governs send/poll delays based on quota telemetry with AI oversight.
-> Called by: livechat_core.py::send_chat_message, ChatSender
-> Delegates to: QwenOrchestrator for response prioritization, throttle memory store, quota analytics
-> Related: NAVIGATION.py -> MODULE_GRAPH["core_flows"]["throttling_flow"]
-> Quick ref: NAVIGATION.py -> NEED_TO["adjust throttle window"]
"""

import time
import logging
import json
import random
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# QWEN Integration for aggressive throttling
try:
    from holo_index.qwen_advisor.orchestration.qwen_orchestrator import QwenOrchestrator
    QWEN_AVAILABLE = True
except ImportError:
    logger.warning("[QWEN-THROTTLE] QwenOrchestrator not available - using fallback logic")
    QWEN_AVAILABLE = False


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
    Now supports multiple concurrent streams with per-stream tracking.
    """

    def __init__(self,
                 min_delay: float = 1.0,
                 max_delay: float = 60.0,
                 throttle_window: int = 60,
                 memory_path: Optional[Path] = None):
        """
        Initialize intelligent throttle manager with QWEN integration.

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

        # QWEN Integration for aggressive API drain prevention
        self.qwen_orchestrator = None
        if QWEN_AVAILABLE:
            try:
                self.qwen_orchestrator = QwenOrchestrator()
                logger.info("[QWEN-THROTTLE] QwenOrchestrator integrated - aggressive API drain prevention enabled")
            except Exception as e:
                logger.error(f"[QWEN-THROTTLE] Failed to initialize QwenOrchestrator: {e}")
                self.qwen_orchestrator = None
        else:
            logger.warning("[QWEN-THROTTLE] QWEN not available - using enhanced fallback logic")

        # Aggressive quota thresholds for API drain prevention
        self.api_drain_threshold = 70  # Start restricting at 70% quota usage (more aggressive)
        self.critical_quota_threshold = 85  # Emergency mode at 85% (earlier intervention)
        self.banter_restriction_threshold = 50  # Restrict banter at 50% usage

        # Multi-stream tracking (channel_id -> timestamps)
        self.stream_message_timestamps = defaultdict(lambda: deque(maxlen=1000))
        self.stream_api_timestamps = defaultdict(lambda: deque(maxlen=1000))
        self.stream_last_response = {}  # channel_id -> last response time
        self.stream_priorities = {}  # channel_id -> priority (0-10)
        self.active_streams = set()  # Currently active stream channel IDs

        # Global tracking (backward compatibility)
        self.message_timestamps = deque(maxlen=1000)
        self.api_call_timestamps = deque(maxlen=1000)
        self.last_response_time = None
        
        # Response type cooldowns with learned adjustments and 0102 priority
        self.response_cooldowns = {
            'consciousness': {'last': None, 'multiplier': 1.0, 'success_rate': 1.0, 'priority': 8},
            'factcheck': {'last': None, 'multiplier': 1.5, 'success_rate': 1.0, 'priority': 6},
            'maga': {'last': None, 'multiplier': 0.5, 'success_rate': 1.0, 'priority': 9},
            'quiz': {'last': None, 'multiplier': 2.0, 'success_rate': 1.0, 'priority': 5},
            'whack': {'last': None, 'multiplier': 0.8, 'success_rate': 1.0, 'priority': 7},  # Increased from 0.3 for API safety
            '0102_emoji': {'last': None, 'multiplier': 1.2, 'success_rate': 1.0, 'priority': 4},
            'troll_response': {'last': None, 'multiplier': 3.0, 'success_rate': 1.0, 'priority': 2},
            'pqn_research': {'last': None, 'multiplier': 2.5, 'success_rate': 1.0, 'priority': 3},  # NEW: PQN throttling
            'command': {'last': None, 'multiplier': 0.8, 'success_rate': 1.0, 'priority': 7},  # NEW: Command throttling
            'video_progress': {'last': None, 'multiplier': 2.0, 'success_rate': 1.0, 'priority': 4},  # NEW: Shorts video progress messages
            'general': {'last': None, 'multiplier': 1.5, 'success_rate': 1.0, 'priority': 5}
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

        # 0102 Consciousness Monitoring
        self.consciousness_monitoring = True

        # Moderator Throttling System (WSP 84) - User-Centric with Database
        self.moderator_recent_commands = defaultdict(list)  # user_id -> list of (timestamp, command_text) in last 5 min
        self.moderator_command_limits = {
            'window_seconds': 300,  # 5 minutes
            'max_commands': 3,       # 3 commands per 5 minutes
            'cooldown_seconds': 60   # 1 minute between identical commands
        }

        # Qwen Message Diversity System - Prevent repetitive consciousness messages
        self.recent_messages = deque(maxlen=50)  # Track last 50 messages
        self.message_similarity_threshold = 0.7  # Similarity threshold for blocking
        self.diversity_cooldown = 180  # 3 minutes between similar messages
        self.message_themes = defaultdict(lambda: deque(maxlen=10))  # theme -> timestamps
        self.theme_cooldowns = {
            'consciousness': 300,  # 5 minutes between consciousness messages
            'maga_troll': 600,     # 10 minutes between MAGA trolling
            'greeting': 120,       # 2 minutes between greetings
            'engagement': 240      # 4 minutes between engagement messages
        }

        # QWEN-enhanced: More aggressive API drain prevention (70% threshold instead of 15%)
        self.emergency_mode = False
        self.priority_threshold = 6  # Only allow priority >= 6 in emergency

        logger.info("[0102] Intelligent Throttle Manager initialized with consciousness monitoring")
    
    def track_message(self, user_id: Optional[str] = None, username: Optional[str] = None,
                     channel_id: Optional[str] = None):
        """Track an incoming message for rate calculation.

        Args:
            user_id: User who sent the message
            username: Username of the sender
            channel_id: Channel/stream ID for multi-stream tracking
        """
        current_time = time.time()

        # Global tracking (for backward compatibility)
        self.message_timestamps.append(current_time)

        # Per-stream tracking if channel provided
        if channel_id:
            self.stream_message_timestamps[channel_id].append(current_time)
            self.active_streams.add(channel_id)

        # Check for troll behavior if user info provided
        if user_id and username:
            is_troll, response = self.troll_detector.track_trigger(user_id, username)
            if is_troll:
                return {'is_troll': True, 'response': response}

        return {'is_troll': False}

    def check_moderator_command_allowed(self, user_id: str, username: str, role: str, command_text: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a moderator's command is allowed (rate limits, repeats, etc.).

        Args:
            user_id: Moderator's user ID
            username: Moderator's username
            role: User's role (MOD, OWNER, etc.)
            command_text: The full command text

        Returns:
            (allowed, response_message) - allowed=True if command can proceed, response_message if blocked/trolled
        """
        # Only apply to moderators (not owners)
        if role not in ['MOD']:
            return True, None

        now = time.time()
        limits = self.moderator_command_limits

        # Get recent commands for this user
        recent_cmds = self.moderator_recent_commands[user_id]

        # Clean old commands (older than window)
        recent_cmds[:] = [(ts, cmd) for ts, cmd in recent_cmds if now - ts < limits['window_seconds']]

        # Check rate limit (3 commands per 5 minutes)
        if len(recent_cmds) >= limits['max_commands']:
            return False, f"@{username} [U+1F550] Rate limit: 3 commands per 5 minutes. Chill out! Next command allowed in {int(limits['window_seconds'] - (now - recent_cmds[0][0]))}s"

        # Check for repeated commands (same command within 60 seconds)
        normalized_cmd = command_text.lower().strip()
        for ts, prev_cmd in recent_cmds:
            if (now - ts < limits['cooldown_seconds'] and
                prev_cmd.lower().strip() == normalized_cmd):
                # Troll for repeated questions
                troll_responses = [
                    f"@{username} I'm not your bitch... chill out! Same question again? [BOT][U+1F485]",
                    f"@{username} Did I stutter? I already answered that. Take a breather! [U+1F624]",
                    f"@{username} Groundhog Day much? Same command twice in a minute? [U+1F644]",
                    f"@{username} Copy-paste error? I see you repeating yourself... [U+1F435]"
                ]
                import random
                return False, random.choice(troll_responses)

        return True, None

    def set_stream_priority(self, channel_id: str, priority: int) -> None:
        """Set priority for a specific stream (0-10, higher = more important).

        Args:
            channel_id: Channel/stream ID
            priority: Priority level (0-10)
        """
        self.stream_priorities[channel_id] = max(0, min(10, priority))
        logger.info(f"[PRIORITY] Stream {channel_id} set to priority {priority}")

    def get_stream_activity_level(self, channel_id: str) -> float:
        """Calculate messages per minute for a specific stream.

        Args:
            channel_id: Channel/stream ID

        Returns:
            Messages per minute for the stream
        """
        if channel_id not in self.stream_message_timestamps:
            return 0.0

        timestamps = self.stream_message_timestamps[channel_id]
        if not timestamps:
            return 0.0

        current_time = time.time()
        recent_messages = [t for t in timestamps if current_time - t <= self.throttle_window]

        if not recent_messages:
            return 0.0

        time_range = max(self.throttle_window, current_time - min(recent_messages))
        return (len(recent_messages) / time_range) * 60

    def calculate_multi_stream_delay(self, response_type: str = 'general',
                                   channel_id: Optional[str] = None) -> float:
        """Calculate delay considering multiple active streams.

        Args:
            response_type: Type of response being sent
            channel_id: Channel/stream ID for specific stream

        Returns:
            Calculated delay in seconds considering all active streams
        """
        # Get base delay from single-stream calculation
        base_delay = self.calculate_adaptive_delay(response_type)

        # Count active streams
        active_count = len(self.active_streams)

        if active_count <= 1:
            # Single stream, use normal delay
            return base_delay

        # Multi-stream adjustment
        if active_count == 2:
            # Two streams: increase delay by 50%
            multi_factor = 1.5
        elif active_count == 3:
            # Three streams: double the delay
            multi_factor = 2.0
        else:
            # More than 3: triple the delay and warn
            multi_factor = 3.0
            logger.warning(f"[THROTTLE] {active_count} concurrent streams - heavy throttling applied")

        # Priority adjustment if channel specified
        if channel_id and channel_id in self.stream_priorities:
            priority = self.stream_priorities[channel_id]
            # High priority streams get less delay
            priority_factor = 1.0 - (priority / 10 * 0.5)  # Up to 50% reduction for priority 10
            multi_factor *= priority_factor

        adjusted_delay = base_delay * multi_factor

        # Log multi-stream throttling
        if active_count > 1:
            logger.info(f"[MULTI-STREAM] {active_count} active streams, "
                       f"delay adjusted from {base_delay:.1f}s to {adjusted_delay:.1f}s")

        return min(adjusted_delay, self.max_response_delay)

    def cleanup_inactive_streams(self, timeout_seconds: int = 300) -> None:
        """Remove streams with no recent activity.

        Args:
            timeout_seconds: Consider stream inactive after this many seconds
        """
        current_time = time.time()
        inactive_streams = []

        for channel_id in list(self.active_streams):
            if channel_id in self.stream_message_timestamps:
                timestamps = self.stream_message_timestamps[channel_id]
                if timestamps:
                    last_message = max(timestamps)
                    if current_time - last_message > timeout_seconds:
                        inactive_streams.append(channel_id)
                else:
                    inactive_streams.append(channel_id)
            else:
                inactive_streams.append(channel_id)

        for channel_id in inactive_streams:
            self.active_streams.discard(channel_id)
            if channel_id in self.stream_message_timestamps:
                del self.stream_message_timestamps[channel_id]
            if channel_id in self.stream_api_timestamps:
                del self.stream_api_timestamps[channel_id]
            if channel_id in self.stream_last_response:
                del self.stream_last_response[channel_id]
            if channel_id in self.stream_priorities:
                del self.stream_priorities[channel_id]
            logger.info(f"[CLEANUP] Removed inactive stream {channel_id}")

    def record_moderator_command(self, user_id: str, username: str, role: str, command_text: str) -> None:
        """
        Record a moderator command for rate limiting and repeat detection.

        Args:
            user_id: Moderator's user ID
            username: Moderator's username
            role: User's role
            command_text: The full command text
        """
        # Only track moderators (not owners)
        if role not in ['MOD']:
            return

        now = time.time()

        # Add to recent commands (will be cleaned up by check method)
        self.moderator_recent_commands[user_id].append((now, command_text))

        # Keep only recent commands (automatic cleanup happens in check method)
        limits = self.moderator_command_limits
        self.moderator_recent_commands[user_id] = [
            (ts, cmd) for ts, cmd in self.moderator_recent_commands[user_id]
            if now - ts < limits['window_seconds']
        ]

        logger.debug(f"[MOD TRACK] Recorded command from {username}: {command_text[:50]}...")
    
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
            
            # WRE Monitor: Track pattern learning
            try:
                from modules.infrastructure.wre_core.wre_monitor import get_monitor
                monitor = get_monitor()
                if monitor:
                    monitor.track_pattern_learned('quota_usage', {
                        'messages_per_min': messages_per_minute,
                        'api_calls_per_min': api_calls_per_minute,
                        'optimal_delay': optimal_delay
                    })
            except:
                pass  # WRE monitor not available
    
    def handle_quota_error(self, credential_set: int = 0):
        """Handle a 403 quota exceeded error"""
        now = time.time()
        
        # WRE Monitor: Track quota error
        try:
            from modules.infrastructure.wre_core.wre_monitor import get_monitor
            monitor = get_monitor()
            if monitor:
                monitor.track_error('quota_exceeded', f'Credential set {credential_set}', 'Switching credential sets')
        except:
            pass
        
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
        # Get available credential sets dynamically (sets 1 and 10)
        from modules.platform_integration.youtube_auth.src.quota_monitor import get_available_credential_sets
        available_sets = get_available_credential_sets()

        # Find the set with most remaining quota
        best_set = None
        best_quota = 0

        for set_id in available_sets:
            if set_id not in self.quota_states:
                # New set not yet tracked - likely has quota
                best_set = set_id
                best_quota = 10000  # Assume full quota
                break

            state = self.quota_states[set_id]
            if not state.exhausted and state.remaining_quota > best_quota:
                best_quota = state.remaining_quota
                best_set = set_id

        # If no good options, try the next set in rotation
        if best_set is None or best_quota < 100:
            current_idx = available_sets.index(self.current_credential_set) if self.current_credential_set in available_sets else 0
            next_idx = (current_idx + 1) % len(available_sets)
            best_set = available_sets[next_idx] if available_sets else 0

        self.current_credential_set = best_set
        logger.info(f"[SWITCH] Switched to credential set {best_set} (quota: {best_quota})")

        # If all sets exhausted, log critical warning
        all_exhausted = all(
            self.quota_states.get(set_id, QuotaState(set_id)).exhausted
            for set_id in available_sets
        )
        if all_exhausted:
            logger.critical("[ALERT] ALL CREDENTIAL SETS EXHAUSTED - Will fall back to no-auth mode")

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
        0102 Consciousness decides if response should be sent.

        Args:
            response_type: Type of response
            user_id: User ID to check for troll status

        Returns:
            True if 0102 approves the response
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
        
        # 0102 Consciousness: Check quota and make intelligent decision
        state = self.quota_states.get(self.current_credential_set, QuotaState())

        # QWEN-enhanced: Check for emergency mode activation (when remaining quota is low)
        # api_drain_threshold is the percentage of remaining quota that triggers restrictions
        if state.quota_percentage < self.api_drain_threshold and not self.emergency_mode:
            self.emergency_mode = True
            logger.critical(f"[[AI] QWEN] EMERGENCY MODE: Remaining quota at {state.quota_percentage:.1f}% (used: {100-state.quota_percentage:.1f}%)")
            logger.warning("[[AI] QWEN] Restricting to high-priority responses only - API drain prevention active")
        elif state.quota_percentage > (100 - self.api_drain_threshold + 20) and self.emergency_mode:
            self.emergency_mode = False
            logger.info(f"[[AI] QWEN] Emergency mode deactivated - quota recovered to {state.quota_percentage:.1f}% remaining")

        # In emergency mode, only allow high priority responses
        if self.emergency_mode:
            priority = self.response_cooldowns.get(response_type, {}).get('priority', 5)
            if priority < self.priority_threshold:
                logger.warning(f"[[AI] 0102] Blocking {response_type} (priority {priority}) - emergency mode")
                return False

        # Critical quota check
        if state.quota_percentage < 5 and response_type not in ['whack', 'maga', 'consciousness']:
            logger.warning(f"[[AI] 0102] CRITICAL: Blocking {response_type} - quota at {state.quota_percentage:.1f}%")
            return False
        
        return True
    
    def record_response(self, response_type: str = 'general', success: bool = True, message_text: str = None):
        """
        Record that a response was sent.

        Args:
            response_type: Type of response sent
            success: Whether the response was successful
            message_text: The actual message text sent (for diversity tracking)
        """
        now = time.time()
        self.last_response_time = now

        # Track message for diversity analysis
        if message_text:
            self.recent_messages.append({
                'text': message_text,
                'timestamp': now,
                'type': response_type
            })

            # Extract and track message theme
            theme = self._extract_message_theme(message_text, response_type)
            if theme:
                self.message_themes[theme].append(now)

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
    
    def get_0102_consciousness_report(self) -> str:
        """Generate 0102 consciousness report on throttle state."""
        state = self.quota_states.get(self.current_credential_set, QuotaState())
        messages_per_minute = self._calculate_activity_rate()

        # Build consciousness assessment
        status_emoji = "[AI]" if state.quota_percentage > 50 else "[U+26A0]️" if state.quota_percentage > 15 else "🆘"

        report = f"{status_emoji} 0102 THROTTLE CONSCIOUSNESS:\n"
        report += f"Quota: {state.quota_percentage:.1f}% | "
        report += f"Activity: {messages_per_minute:.0f} msg/min | "
        report += f"Mode: {'EMERGENCY' if self.emergency_mode else 'Normal'} | "
        report += f"Trolls: {len(self.troll_detector.troll_list)} blocked"

        if self.emergency_mode:
            report += "\n[U+26A0]️ API DRAIN DETECTED - Restricting to critical responses only"

        # Add moderator throttling status
        tracked_mods = len([cmds for cmds in self.moderator_recent_commands.values() if cmds])
        if tracked_mods > 0:
            report += f"\n[U+1F46E] MOD TRACK: {tracked_mods} moderators being rate-limited"

        return report

    def get_status(self) -> Dict:
        """Get comprehensive throttle status with 0102 monitoring."""
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

    def check_message_diversity(self, message_text: str, response_type: str = 'general') -> Tuple[bool, str]:
        """
        Check if a message would be too similar to recent messages.
        Uses Qwen-inspired intelligence for content diversity.

        Args:
            message_text: The proposed message text
            response_type: Type of response

        Returns:
            (allowed, reason) - allowed=True if message can be sent
        """
        now = time.time()

        # Check theme-based cooldowns first
        theme = self._extract_message_theme(message_text, response_type)
        if theme and theme in self.theme_cooldowns:
            theme_timestamps = self.message_themes[theme]
            if theme_timestamps:
                last_theme_time = max(theme_timestamps)
                cooldown = self.theme_cooldowns[theme]
                if now - last_theme_time < cooldown:
                    remaining = cooldown - (now - last_theme_time)
                    return False, f"Theme '{theme}' cooldown active ({remaining:.0f}s remaining)"

        # Check for exact duplicate messages
        for recent_msg in self.recent_messages:
            if recent_msg['text'] == message_text:
                time_diff = now - recent_msg['timestamp']
                if time_diff < self.diversity_cooldown:
                    return False, f"Exact duplicate message ({time_diff:.0f}s ago)"

        # Check for highly similar consciousness messages
        if response_type in ['consciousness', 'maga_troll', 'engagement']:
            similarity_check = self._check_similarity_to_recent(message_text)
            if similarity_check['too_similar']:
                return False, f"Too similar to recent {similarity_check['similar_type']} message"

        return True, "Message diversity OK"

    def _extract_message_theme(self, message_text: str, response_type: str) -> Optional[str]:
        """
        Extract the thematic content of a message for diversity tracking.

        Args:
            message_text: Message to analyze
            response_type: Response type hint

        Returns:
            Theme string or None
        """
        text_lower = message_text.lower()

        # Direct type-based themes
        if response_type == 'consciousness':
            return 'consciousness'
        elif response_type == 'maga_troll':
            return 'maga_troll'
        elif response_type == 'greeting':
            return 'greeting'
        elif response_type in ['engagement', 'general']:
            return 'engagement'

        # Content-based theme detection
        if any(word in text_lower for word in ['[U+270A]', '[U+270B]', '[U+1F590]', 'consciousness', 'matrix', 'red pill', 'blue pill']):
            return 'consciousness'
        elif any(word in text_lower for word in ['maga', 'trump', 'biden', 'liberal', 'conservative']):
            return 'maga_troll'
        elif any(word in text_lower for word in ['hey', 'hi', 'hello', 'welcome', 'good morning']):
            return 'greeting'

        return None

    def _check_similarity_to_recent(self, message_text: str) -> Dict[str, Any]:
        """
        Check similarity to recent messages using simple keyword overlap.

        Args:
            message_text: Message to check

        Returns:
            Similarity analysis result
        """
        text_lower = message_text.lower()
        now = time.time()

        # Simple keyword extraction
        keywords = set()
        for word in text_lower.split():
            word = word.strip('.,!?()[]{}')
            if len(word) > 3:  # Skip short words
                keywords.add(word)

        # Check recent messages
        for recent in self.recent_messages:
            if now - recent['timestamp'] > 600:  # Only check last 10 minutes
                continue

            recent_text = recent['text'].lower()
            recent_keywords = set()
            for word in recent_text.split():
                word = word.strip('.,!?()[]{}')
                if len(word) > 3:
                    recent_keywords.add(word)

            # Calculate overlap
            if keywords and recent_keywords:
                overlap = len(keywords.intersection(recent_keywords))
                overlap_ratio = overlap / len(keywords)

                if overlap_ratio > self.message_similarity_threshold:
                    return {
                        'too_similar': True,
                        'similar_type': recent['type'],
                        'overlap_ratio': overlap_ratio,
                        'time_diff': now - recent['timestamp']
                    }

        return {'too_similar': False}

    def save_state(self):
        """Save current state and patterns"""
        self.learner.save_patterns()
        logger.info("[SAVE] Throttle manager state saved")