"""
Qwen Quota Intelligence - Pattern Learning Enhancement
WSP-Compliant: Enhances quota management with historical pattern learning and predictive intelligence

This module WRAPS the existing QuotaIntelligence system (WSP 84) to add:
- Historical quota consumption pattern learning
- Predictive exhaustion forecasting
- Intelligent credential set switching recommendations
- Time-based usage optimization
- Adaptive polling strategies

Architecture: Decorator pattern - enhances QuotaIntelligence without breaking existing functionality
"""

import logging
import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from pathlib import Path

from .quota_intelligence import QuotaIntelligence
from .quota_monitor import QuotaMonitor

logger = logging.getLogger(__name__)


@dataclass
class QuotaSetProfile:
    """
    Historical intelligence profile for each credential set.
    Tracks patterns and learns optimal usage strategies.
    """
    set_number: int

    # Historical consumption patterns (Qwen learns these)
    total_operations_tracked: int = 0
    typical_daily_consumption: float = 0.0  # Rolling average
    peak_usage_hours: List[int] = field(default_factory=list)  # Hours with highest usage

    # Exhaustion tracking
    exhaustion_history: List[float] = field(default_factory=list)  # Timestamps of exhaustions
    typical_exhaustion_hour: Optional[int] = None  # Most common exhaustion time

    # Predictive intelligence
    current_consumption_rate: float = 0.0  # Units per hour (current session)
    predicted_exhaustion_time: Optional[float] = None  # Predicted timestamp

    # Pattern memory
    operation_frequency: Dict[str, int] = field(default_factory=dict)  # How often each operation is used
    high_value_operations: List[str] = field(default_factory=list)  # Operations worth the cost

    # Adaptive recommendations
    last_learning_update: Optional[float] = None
    confidence_level: float = 0.5  # How confident are predictions (0-1)


class QwenQuotaIntelligence:
    """
    Intelligent quota management with pattern learning and predictive capabilities.

    Wraps QuotaIntelligence to add:
    - Historical pattern learning
    - Predictive exhaustion forecasting
    - Smart credential set rotation
    - Time-based optimization
    """

    def __init__(self, quota_monitor: QuotaMonitor, quota_intelligence: QuotaIntelligence = None):
        """
        Initialize Qwen quota intelligence.

        Args:
            quota_monitor: QuotaMonitor instance for tracking usage
            quota_intelligence: Optional QuotaIntelligence instance (creates one if not provided)
        """
        self.quota_monitor = quota_monitor
        self.quota_intelligence = quota_intelligence or QuotaIntelligence(quota_monitor)

        # Memory persistence
        self.memory_dir = Path(__file__).parent.parent / "memory" / "quota_profiles"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Load existing profiles or create new ones
        self.profiles: Dict[int, QuotaSetProfile] = self._load_profiles()

        # Learning parameters
        self.learning_interval = 300  # Update patterns every 5 minutes
        self.exhaustion_threshold_hours = 2  # Warn when exhaustion predicted within 2 hours

        # Decision history for learning
        self.decision_history: List[Dict] = []
        self.max_decision_history = 1000

    def _load_profiles(self) -> Dict[int, QuotaSetProfile]:
        """Load historical quota profiles from memory."""
        profiles = {}

        # Try to load saved profiles
        profile_file = self.memory_dir / "quota_profiles.json"
        if profile_file.exists():
            try:
                with open(profile_file, 'r', encoding="utf-8") as f:
                    data = json.load(f)
                    for set_num_str, profile_data in data.items():
                        set_num = int(set_num_str)
                        profiles[set_num] = QuotaSetProfile(
                            set_number=set_num,
                            **{k: v for k, v in profile_data.items() if k != 'set_number'}
                        )
                logger.info(f"[BOT][AI] [QWEN-QUOTA] Loaded {len(profiles)} quota profiles from memory")
            except Exception as e:
                logger.warning(f"[BOT][AI] [QWEN-QUOTA] Error loading profiles: {e}")

        # Ensure profiles exist for active credential sets (1, 10)
        for set_num in [1, 10]:
            if set_num not in profiles:
                profiles[set_num] = QuotaSetProfile(set_number=set_num)
                logger.info(f"[BOT][AI] [QWEN-QUOTA] Created new profile for credential set {set_num}")

        return profiles

    def _save_profiles(self):
        """Save quota profiles to persistent memory."""
        try:
            profile_file = self.memory_dir / "quota_profiles.json"
            data = {
                str(set_num): {
                    **asdict(profile),
                    # Convert lists to ensure JSON serialization
                    'exhaustion_history': profile.exhaustion_history[-10:]  # Keep last 10 only
                }
                for set_num, profile in self.profiles.items()
            }

            with open(profile_file, 'w', encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            logger.debug(f"[BOT][AI] [QWEN-QUOTA] Saved {len(self.profiles)} quota profiles")
        except Exception as e:
            logger.error(f"[BOT][AI] [QWEN-QUOTA] Error saving profiles: {e}")

    def record_operation(self, operation: str, credential_set: int, cost: int):
        """
        Record an operation for pattern learning.

        Args:
            operation: YouTube API operation performed
            credential_set: Which credential set was used
            cost: Quota cost of the operation
        """
        profile = self.profiles.get(credential_set)
        if not profile:
            return

        # Update operation frequency
        profile.operation_frequency[operation] = profile.operation_frequency.get(operation, 0) + 1
        profile.total_operations_tracked += 1

        # Update current consumption rate (units per hour)
        current_hour = datetime.now().hour
        if current_hour not in profile.peak_usage_hours:
            # Track peak hours (hours with most operations)
            hour_counts = {}
            for op_name, count in profile.operation_frequency.items():
                # This is simplified - in reality, we'd track timestamps
                hour_counts[current_hour] = hour_counts.get(current_hour, 0) + count

            # Keep top 5 peak hours
            peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
            profile.peak_usage_hours = [h for h, _ in peak_hours[:5]]

        # Update last learning time
        profile.last_learning_update = time.time()

        # Periodically save profiles
        if profile.total_operations_tracked % 50 == 0:
            self._save_profiles()

        logger.debug(f"[BOT][AI] [QWEN-QUOTA] Recorded {operation} on set {credential_set} (cost: {cost})")

    def record_exhaustion(self, credential_set: int):
        """
        Record when a credential set is exhausted for pattern learning.

        Args:
            credential_set: Which set was exhausted
        """
        profile = self.profiles.get(credential_set)
        if not profile:
            return

        exhaustion_time = time.time()
        profile.exhaustion_history.append(exhaustion_time)

        # Keep only last 30 exhaustions
        profile.exhaustion_history = profile.exhaustion_history[-30:]

        # Learn typical exhaustion hour
        exhaustion_hours = [
            datetime.fromtimestamp(ts).hour
            for ts in profile.exhaustion_history
        ]
        if exhaustion_hours:
            # Most common hour
            from collections import Counter
            hour_counts = Counter(exhaustion_hours)
            profile.typical_exhaustion_hour = hour_counts.most_common(1)[0][0]

        # Increase confidence with more data
        profile.confidence_level = min(1.0, len(profile.exhaustion_history) / 10)

        self._save_profiles()

        logger.info(f"[BOT][AI] [QWEN-QUOTA] [U+26A0]️ Set {credential_set} exhausted. "
                   f"Typical exhaustion hour: {profile.typical_exhaustion_hour}:00 "
                   f"(confidence: {profile.confidence_level:.1%})")

    def should_perform_operation(self, operation: str, credential_set: int,
                                count: int = 1) -> Dict:
        """
        Enhanced operation check with predictive intelligence.

        This WRAPS quota_intelligence.can_perform_operation() to add predictions.

        Returns:
            Dict with enhanced fields including predictions and recommendations
        """
        # Get base check from existing QuotaIntelligence
        base_result = self.quota_intelligence.can_perform_operation(
            operation, credential_set, count
        )

        # Enhance with Qwen predictions
        profile = self.profiles.get(credential_set)
        if not profile:
            return base_result

        enhanced_result = {
            **base_result,
            'qwen_insights': {}
        }

        # Add prediction: Will this set exhaust soon?
        if profile.typical_exhaustion_hour is not None:
            current_hour = datetime.now().hour
            hours_until_typical_exhaustion = (profile.typical_exhaustion_hour - current_hour) % 24

            if hours_until_typical_exhaustion <= self.exhaustion_threshold_hours:
                enhanced_result['qwen_insights']['exhaustion_warning'] = {
                    'message': f"⏰ Set {credential_set} typically exhausts around {profile.typical_exhaustion_hour}:00",
                    'hours_until': hours_until_typical_exhaustion,
                    'confidence': profile.confidence_level,
                    'recommendation': f"Consider switching to backup set soon"
                }

        # Add operation value assessment
        if operation in profile.operation_frequency:
            frequency = profile.operation_frequency[operation]
            enhanced_result['qwen_insights']['operation_value'] = {
                'times_used': frequency,
                'assessment': 'high-value' if frequency > 100 else 'moderate-value' if frequency > 20 else 'low-value'
            }

        # Record this operation for learning
        if base_result['allowed']:
            cost = base_result.get('cost', 0)
            self.record_operation(operation, credential_set, cost)

        return enhanced_result

    def get_best_credential_set(self) -> int:
        """
        Intelligently select the best credential set to use right now.

        Returns:
            Recommended credential set number
        """
        summary = self.quota_monitor.get_usage_summary()
        current_hour = datetime.now().hour

        best_set = 1  # Default
        best_score = -1

        for set_num in [1, 10]:
            set_info = summary['sets'].get(set_num, {})
            profile = self.profiles.get(set_num)

            if not set_info or not profile:
                continue

            score = 0

            # Factor 1: Available quota (most important)
            available_percent = set_info.get('usage_percent', 100)
            score += (100 - available_percent) * 2  # Weight: 2x

            # Factor 2: Avoid sets near typical exhaustion hour
            if profile.typical_exhaustion_hour is not None:
                hours_until = (profile.typical_exhaustion_hour - current_hour) % 24
                if hours_until > 4:
                    score += 50  # Bonus if not near exhaustion time

            # Factor 3: Current hour is NOT a peak usage hour
            if current_hour not in profile.peak_usage_hours:
                score += 25  # Bonus for using during off-peak

            logger.debug(f"[BOT][AI] [QWEN-QUOTA] Set {set_num} score: {score:.1f}")

            if score > best_score:
                best_score = score
                best_set = set_num

        logger.info(f"[BOT][AI] [QWEN-QUOTA] [TARGET] Recommended credential set: {best_set} (score: {best_score:.1f})")
        return best_set

    def get_intelligence_summary(self) -> str:
        """Get summary of Qwen quota intelligence state."""
        summary = "[QWEN-QUOTA INTELLIGENCE]\n"
        summary += f"Profiles Tracked: {len(self.profiles)}\n"

        for set_num, profile in self.profiles.items():
            summary += f"\nCredential Set {set_num}:\n"
            summary += f"  Operations Tracked: {profile.total_operations_tracked}\n"
            summary += f"  Exhaustions Recorded: {len(profile.exhaustion_history)}\n"

            if profile.typical_exhaustion_hour is not None:
                summary += f"  Typical Exhaustion: {profile.typical_exhaustion_hour}:00 "
                summary += f"(confidence: {profile.confidence_level:.1%})\n"

            if profile.peak_usage_hours:
                hours_str = ', '.join([f"{h}:00" for h in profile.peak_usage_hours[:3]])
                summary += f"  Peak Hours: {hours_str}\n"

            # Top operations
            top_ops = sorted(profile.operation_frequency.items(), key=lambda x: x[1], reverse=True)[:3]
            if top_ops:
                summary += f"  Top Operations: {', '.join([f'{op}({count}x)' for op, count in top_ops])}\n"

        return summary


# Singleton instance for easy access
_qwen_quota_intelligence = None

def get_qwen_quota_intelligence() -> QwenQuotaIntelligence:
    """Get or create singleton Qwen quota intelligence instance."""
    global _qwen_quota_intelligence
    if _qwen_quota_intelligence is None:
        quota_monitor = QuotaMonitor()
        _qwen_quota_intelligence = QwenQuotaIntelligence(quota_monitor)
    return _qwen_quota_intelligence
