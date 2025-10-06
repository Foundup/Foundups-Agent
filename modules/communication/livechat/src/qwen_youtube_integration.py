#!/usr/bin/env python3
"""
QWEN-YouTube DAE Integration Bridge
Provides intelligence layer for YouTube DAE without breaking existing code
WSP Compliance: WSP 3, WSP 49, WSP 50, WSP 84, WSP 87
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ChannelIntelligence:
    """Intelligence profile for each YouTube channel"""
    channel_id: str
    channel_name: str
    last_429_time: Optional[float] = None
    consecutive_429_count: int = 0
    typical_stream_hours: List[int] = field(default_factory=list)
    typical_stream_days: List[int] = field(default_factory=list)
    avg_stream_duration_minutes: float = 120.0
    last_successful_check: Optional[float] = None
    heat_level: int = 0  # 0=cold, 1=warm, 2=hot, 3=overheated
    video_count: int = 0
    last_stream_time: Optional[float] = None  # When was the last stream detected
    total_streams_detected: int = 0  # How many streams have we found
    recent_activity_boost: float = 1.0  # Boost factor for recent activity

    def should_check_now(self) -> Tuple[bool, str]:
        """Intelligent decision on whether to check this channel"""
        if self.heat_level >= 3:
            return False, f"Channel overheated (heat={self.heat_level})"

        if self.last_429_time:
            time_since_429 = time.time() - self.last_429_time
            if time_since_429 < 300:  # 5 minutes
                return False, f"Recent 429 error ({int(time_since_429)}s ago)"

        # Check if it's a typical streaming hour
        current_hour = datetime.now().hour
        if self.typical_stream_hours and current_hour not in self.typical_stream_hours:
            confidence = 0.3  # Low confidence outside typical hours
        else:
            confidence = 0.9  # High confidence during typical hours

        return True, f"Check recommended (confidence={confidence:.1%})"

    def should_investigate_stream(self, stream_info: Dict[str, Any]) -> bool:
        """
        QWEN intelligence: Decide if a stream is worth detailed investigation/logging

        Args:
            stream_info: Dict with video_id, broadcast_content, actual_end, actual_start, age_hours

        Returns:
            True if stream should be investigated, False to skip
        """
        video_id = stream_info.get('video_id', '')
        broadcast_content = stream_info.get('broadcast_content', 'none')
        age_hours = stream_info.get('age_hours')

        # Always investigate live streams
        if broadcast_content == 'live':
            return True

        # Never investigate streams that have ended
        if broadcast_content == 'completed' or stream_info.get('actual_end'):
            # Only investigate very recent ended streams (within 2 hours)
            # These might still be relevant for posting about recent activity
            if age_hours is not None and age_hours <= 2:
                logger.debug(f"🤖🧠 [QWEN-INVESTIGATE] Recent ended stream ({age_hours:.1f}h) - investigating")
                return True
            else:
                logger.debug(f"🤖🧠 [QWEN-INVESTIGATE] Old ended stream ({age_hours:.1f}h) - skipping")
                return False

        # For upcoming streams, always investigate (they're future events)
        if broadcast_content == 'upcoming':
            return True

        # Default: investigate unknown status
        logger.debug(f"🤖🧠 [QWEN-INVESTIGATE] Unknown status '{broadcast_content}' - investigating")
        return True

    def validate_video_selection(self, videos_to_check: List[str], channel_name: str, has_time_data: bool) -> Dict[str, Any]:
        """
        QWEN intelligence: Validate and potentially optimize video selection for checking

        Args:
            videos_to_check: List of video IDs selected for checking
            channel_name: Name of the channel
            has_time_data: Whether time metadata was available for filtering

        Returns:
            Dict with validation results and potential alternative selection
        """
        result = {
            'selection_valid': True,
            'alternative_selection': None,
            'reasoning': []
        }

        # Basic validation
        if not videos_to_check:
            result['selection_valid'] = False
            result['reasoning'].append("No videos selected for checking")
            return result

        if len(videos_to_check) > 5:
            result['reasoning'].append(f"Large selection ({len(videos_to_check)}) - consider reducing")
            # Suggest keeping only the most recent/relevant ones
            result['alternative_selection'] = videos_to_check[:3]
            result['reasoning'].append("Reduced to top 3 most relevant videos")

        # Intelligence based on channel patterns
        channel_profile = self.get_channel_profile('', channel_name)  # Get by name
        if channel_profile and channel_profile.heat_level > 2:
            result['reasoning'].append(f"Channel {channel_name} is hot - prioritize checking")
        elif channel_profile and channel_profile.heat_level == 0:
            result['reasoning'].append(f"Channel {channel_name} is cold - reduce checking frequency")

        # Time data validation
        if not has_time_data:
            result['reasoning'].append("No time metadata available - selection may include old videos")

        logger.debug(f"🤖🧠 [QWEN-VALIDATE] Video selection validated: {len(videos_to_check)} videos, {'with' if has_time_data else 'without'} time data")
        return result

    def record_429_error(self):
        """Record a 429 error and update heat level"""
        self.last_429_time = time.time()
        self.consecutive_429_count += 1
        self.heat_level = min(3, self.heat_level + 1)
        logger.info(f"🤖🧠 [QWEN-429] 🔥 Channel {self.channel_name} received 429 error")
        logger.info(f"🤖🧠 [QWEN-HEAT] 🌡️ {self.channel_name} heat level increased: {self.heat_level-1} → {self.heat_level}")
        logger.info(f"🤖🧠 [QWEN-429] 📊 Consecutive 429 count: {self.consecutive_429_count}")

    def record_success(self):
        """Record successful check and cool down"""
        self.last_successful_check = time.time()
        old_heat = self.heat_level
        self.consecutive_429_count = 0
        self.heat_level = max(0, self.heat_level - 1)
        if old_heat != self.heat_level:
            logger.info(f"🤖🧠 [QWEN-COOL] ❄️ {self.channel_name} cooling down: {old_heat} → {self.heat_level}")


class QwenYouTubeIntegration:
    """
    QWEN Intelligence Bridge for YouTube DAE
    Provides smart decision-making without breaking existing code
    """

    def __init__(self):
        self.channel_profiles: Dict[str, ChannelIntelligence] = {}
        self.global_heat_level = 0
        self.decision_history = []

        # Try to import QWEN components if available
        try:
            from holo_index.qwen_advisor.intelligent_monitor import IntelligentMonitor
            from holo_index.qwen_advisor.rules_engine import ComplianceRulesEngine
            from holo_index.qwen_advisor.pattern_coach import PatternCoach

            self.intelligent_monitor = IntelligentMonitor()
            self.rules_engine = ComplianceRulesEngine()
            self.pattern_coach = PatternCoach()
            self.qwen_available = True
            logger.info("🤖🧠 [QWEN-BRIDGE] Full QWEN intelligence connected - YouTube DAE brain activated")
            logger.info("🤖🧠 [QWEN-BRIDGE] 📊 Components: IntelligentMonitor ✓ RulesEngine ✓ PatternCoach ✓")
        except ImportError as e:
            logger.debug(f"[QWEN-BRIDGE] Operating without full QWEN: {e}")
            self.intelligent_monitor = None
            self.rules_engine = None
            self.pattern_coach = None
            self.qwen_available = False

    def get_channel_profile(self, channel_id: str, channel_name: str = "Unknown") -> ChannelIntelligence:
        """Get or create intelligence profile for a channel"""
        if channel_id not in self.channel_profiles:
            self.channel_profiles[channel_id] = ChannelIntelligence(
                channel_id=channel_id,
                channel_name=channel_name
            )
        return self.channel_profiles[channel_id]

    def prioritize_channels(self, channels: List[Tuple[str, str]]) -> List[Tuple[str, str, float]]:
        """
        Intelligently prioritize channel checking order
        Returns list of (channel_id, channel_name, priority_score)
        """
        prioritized = []

        for channel_id, channel_name in channels:
            profile = self.get_channel_profile(channel_id, channel_name)

            # Calculate priority score (base = 1.0)
            score = 1.0

            # PENALTY: Reduce priority if overheated or recently rate-limited
            if profile.heat_level >= 3:
                score -= 0.9
            elif profile.heat_level == 2:
                score -= 0.6
            elif profile.heat_level == 1:
                score -= 0.3

            if profile.last_429_time and time.time() - profile.last_429_time < 300:
                score -= 0.5

            # PENALTY: Reduce by heat level multiplier
            score *= (1.0 - (profile.heat_level * 0.3))

            # BOOST 1: Recent stream activity (last 24 hours)
            if profile.last_stream_time:
                hours_since_last_stream = (time.time() - profile.last_stream_time) / 3600
                if hours_since_last_stream < 24:
                    # Strong boost if stream was recent
                    activity_boost = 2.0 - (hours_since_last_stream / 24)  # 2.0x -> 1.0x over 24h
                    score *= activity_boost
                    logger.debug(f"🤖🧠 [QWEN-BOOST] 🎯 {channel_name}: Recent stream {hours_since_last_stream:.1f}h ago (+{activity_boost:.1f}x)")
                elif hours_since_last_stream < 168:  # Last week
                    # Moderate boost for streams in the last week
                    score *= 1.3
                    logger.debug(f"🤖🧠 [QWEN-BOOST] 📊 {channel_name}: Stream {hours_since_last_stream:.1f}h ago (+1.3x)")

            # BOOST 2: Typical streaming time pattern matching
            current_hour = datetime.now().hour
            current_day = datetime.now().weekday()

            if profile.typical_stream_hours and current_hour in profile.typical_stream_hours:
                score *= 1.5
                logger.debug(f"🤖🧠 [QWEN-BOOST] ⏰ {channel_name}: Typical streaming hour {current_hour}:00 (+1.5x)")

            if profile.typical_stream_days and current_day in profile.typical_stream_days:
                score *= 1.2
                logger.debug(f"🤖🧠 [QWEN-BOOST] 📅 {channel_name}: Typical streaming day ({datetime.now().strftime('%A')}) (+1.2x)")

            # BOOST 3: Channel has history of streams
            if profile.total_streams_detected > 0:
                # Channels with proven activity get priority
                history_boost = 1.0 + min(0.5, profile.total_streams_detected * 0.1)  # Up to 1.5x
                score *= history_boost
                logger.debug(f"🤖🧠 [QWEN-BOOST] 📈 {channel_name}: {profile.total_streams_detected} streams found (+{history_boost:.1f}x)")

            # PENALTY: Recently checked (avoid spam)
            if profile.last_successful_check:
                minutes_since = (time.time() - profile.last_successful_check) / 60
                if minutes_since < 5:
                    score *= 0.3
                    logger.debug(f"🤖🧠 [QWEN-PENALTY] ⏳ {channel_name}: Checked {minutes_since:.1f}m ago (-70%)")

            prioritized.append((channel_id, channel_name, score))

        # Sort by priority score (highest first)
        prioritized.sort(key=lambda x: x[2], reverse=True)

        # Log detailed decision process
        logger.info("🤖🧠 [QWEN-PRIORITIZE] 🎯 Channel prioritization analysis:")
        for _, name, score in prioritized:
            heat_emoji = "🔥" if self.get_channel_profile(_, name).heat_level >= 2 else "❄️"
            logger.info(f"🤖🧠 [QWEN-SCORE] {heat_emoji} {name}: {score:.2f}")

        decision = f"Channel priorities: {[(name, f'{score:.2f}') for _, name, score in prioritized]}"
        self.decision_history.append(decision)
        logger.info(f"🤖🧠 [QWEN-DECISION] Final order selected based on heat levels and patterns")

        return prioritized

    def calculate_retry_delay(self, channel_id: str, retry_count: int) -> float:
        """
        Calculate intelligent retry delay based on channel profile
        """
        profile = self.get_channel_profile(channel_id)

        # Base delay depends on heat level
        if profile.heat_level >= 3:
            base_delay = 300  # 5 minutes for overheated
        elif profile.heat_level == 2:
            base_delay = 120  # 2 minutes for hot
        elif profile.heat_level == 1:
            base_delay = 60   # 1 minute for warm
        else:
            base_delay = 30   # 30 seconds for cold

        # Apply exponential backoff
        delay = base_delay * (2 ** retry_count)

        # Cap at 10 minutes
        delay = min(delay, 600)

        # Enhanced delay logging with reasoning
        heat_emoji = {0: "❄️", 1: "🌤️", 2: "🔥", 3: "🌋"}.get(profile.heat_level, "🌡️")
        logger.info(f"🤖🧠 [QWEN-DELAY] {heat_emoji} {profile.channel_name}: {delay}s delay")
        logger.info(f"🤖🧠 [QWEN-REASON] 📊 Heat={profile.heat_level}, Retries={retry_count}, Base={base_delay}s")

        return delay

    def record_stream_found(self, channel_id: str, channel_name: str, video_id: str):
        """Record successful stream detection for pattern learning"""
        # Update profile to ensure channel name is set
        profile = self.get_channel_profile(channel_id, channel_name)
        # Call the internal method that handles everything
        self.record_stream_detection(channel_id, {'video_id': video_id, 'channel_name': channel_name})

    def record_stream_detection(self, channel_id: str, stream_info: Dict):
        """Record successful stream detection for pattern learning (internal)"""
        profile = self.get_channel_profile(channel_id)
        profile.record_success()

        # Track stream detection history
        profile.last_stream_time = time.time()
        profile.total_streams_detected += 1

        # Learn streaming patterns
        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()

        if current_hour not in profile.typical_stream_hours:
            profile.typical_stream_hours.append(current_hour)
            logger.info(f"🤖🧠 [QWEN-LEARN] 🕐 New typical hour learned: {current_hour}:00 for {profile.channel_name}")

        if current_day not in profile.typical_stream_days:
            profile.typical_stream_days.append(current_day)
            logger.info(f"🤖🧠 [QWEN-LEARN] 📅 New typical day learned: {datetime.now().strftime('%A')} for {profile.channel_name}")

        # Record to pattern coach if available (skip if method not available)
        if self.pattern_coach:
            try:
                # Try to record pattern if PatternCoach supports it
                if hasattr(self.pattern_coach, 'record_pattern'):
                    self.pattern_coach.record_pattern({
                        'type': 'stream_detected',
                        'channel': channel_id,
                        'hour': current_hour,
                        'day': current_day,
                        'timestamp': time.time()
                    })
                # Otherwise just log that we learned
                logger.debug(f"🤖🧠 [QWEN-PATTERN] Pattern coach notified of stream detection")
            except Exception as e:
                logger.debug(f"🤖🧠 [QWEN-PATTERN] Could not record to pattern coach: {e}")

        logger.info(f"🤖🧠 [QWEN-LEARN] 📚 Recorded stream pattern for {profile.channel_name}")
        logger.info(f"🤖🧠 [QWEN-PATTERN] 🕐 Hour: {current_hour}, Day: {datetime.now().strftime('%A')}")
        logger.info(f"🤖🧠 [QWEN-MEMORY] Typical hours: {profile.typical_stream_hours[-3:]}")

    def get_intelligence_summary(self) -> str:
        """Get summary of current intelligence state"""
        summary = "[QWEN-INTELLIGENCE SUMMARY]\n"
        summary += f"Global Heat: {self.global_heat_level}\n"
        summary += f"Channels Tracked: {len(self.channel_profiles)}\n"

        for channel_id, profile in self.channel_profiles.items():
            summary += f"\n{profile.channel_name}:\n"
            summary += f"  Heat Level: {profile.heat_level}\n"
            summary += f"  429 Count: {profile.consecutive_429_count}\n"
            summary += f"  Streams Found: {profile.total_streams_detected}\n"

            if profile.last_stream_time:
                hours_ago = (time.time() - profile.last_stream_time) / 3600
                summary += f"  Last Stream: {hours_ago:.1f}h ago\n"

            summary += f"  Typical Hours: {profile.typical_stream_hours}\n"
            summary += f"  Typical Days: {[datetime.fromtimestamp(0).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=d) for d in profile.typical_stream_days] if profile.typical_stream_days else []}\n"

        summary += f"\nRecent Decisions: {self.decision_history[-5:]}\n"

        return summary

    def should_check_now(self) -> Tuple[bool, str]:
        """Global decision on whether to check any channels"""
        logger.info("🤖🧠 [QWEN-GLOBAL] 🌍 Evaluating global system state...")

        # Global overheating protection
        if self.global_heat_level >= 5:
            logger.warning(f"🤖🧠 [QWEN-GLOBAL] 🌋 System overheated (level {self.global_heat_level}) - cooling down")
            return False, "System overheated - cooling down"

        # Time-based intelligence
        current_hour = datetime.now().hour
        time_emoji = "🌙" if 22 <= current_hour or current_hour <= 6 else "☀️"

        if 2 <= current_hour <= 6:  # Late night
            logger.info(f"🤖🧠 [QWEN-TIME] {time_emoji} Low-activity period ({current_hour}:00) - safe to check")
            return True, "Low-activity period - safe to check (reduced frequency)"

        logger.info(f"🤖🧠 [QWEN-TIME] {time_emoji} Normal hours ({current_hour}:00) - standard checking")
        return True, "Normal checking enabled"


# Singleton instance for shared intelligence
_qwen_youtube = None

def get_qwen_youtube() -> QwenYouTubeIntegration:
    """Get singleton QWEN YouTube intelligence instance"""
    global _qwen_youtube
    if _qwen_youtube is None:
        _qwen_youtube = QwenYouTubeIntegration()
    return _qwen_youtube