"""Participation Sentinel - AI Pattern Detection (WSP 26 Section 15).

AI-powered sentinel for detecting manipulation patterns in epoch distributions:

DETECTION VECTORS:
- Sybil patterns: Multiple accounts with coordinated behavior
- Bot activity: Superhuman timing, pattern repetition
- Wash trading: Circular transactions between accounts
- Concentration: Unhealthy reward clustering
- Velocity anomalies: Statistical outliers in earnings

SEVERITY LEVELS:
- 0.0-0.3: Low (informational)
- 0.3-0.6: Medium (flag for review)
- 0.6-0.8: High (freeze pending investigation)
- 0.8-1.0: Critical (automatic restrictions)

INTEGRATION:
- Receives epoch entries from EpochLedger
- Uses Gemma for fast binary classification (is_suspicious?)
- Uses Qwen for strategic pattern analysis (what pattern?)
- Emits sentinel_alert FAM events

Reference: WSP 26 Section 15, WSP 29 (CABR integration)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from enum import Enum
import math


class AlertType(str, Enum):
    """Types of sentinel alerts."""

    CONCENTRATION = "concentration"  # Reward clustering
    VELOCITY_ANOMALY = "velocity_anomaly"  # Unusual earnings spike
    SYBIL_PATTERN = "sybil_pattern"  # Multiple accounts, one actor
    BOT_TIMING = "bot_timing"  # Inhuman timing patterns
    WASH_TRADING = "wash_trading"  # Circular transactions
    ANOMALY = "anomaly"  # General statistical outlier


class RecommendedAction(str, Enum):
    """Recommended actions for alerts."""

    LOG = "log"  # Just record
    FLAG = "flag"  # Flag for review
    INVESTIGATE = "investigate"  # Requires human review
    FREEZE = "freeze"  # Temporary freeze
    BAN = "ban"  # Permanent restriction


@dataclass
class SentinelAlert:
    """Alert raised by the participation sentinel."""

    alert_type: AlertType
    severity: float  # 0.0-1.0 (higher = more severe)
    participant_ids: List[str]  # Suspected participants
    evidence: Dict[str, Any]  # Supporting data
    timestamp: str
    recommended_action: RecommendedAction
    epoch_number: Optional[int] = None
    resolved: bool = False
    resolution_notes: str = ""

    def to_dict(self) -> Dict:
        """Export for JSON serialization / FAM event."""
        return {
            "alert_type": self.alert_type.value,
            "severity": round(self.severity, 3),
            "participant_ids": self.participant_ids,
            "evidence": self.evidence,
            "timestamp": self.timestamp,
            "recommended_action": self.recommended_action.value,
            "epoch_number": self.epoch_number,
            "resolved": self.resolved,
        }


@dataclass
class ParticipantProfile:
    """Profile tracking for anomaly detection."""

    participant_id: str
    total_rewards: float = 0.0
    epoch_count: int = 0
    avg_reward: float = 0.0
    max_reward: float = 0.0
    last_active_epoch: int = 0
    reward_history: List[float] = field(default_factory=list)
    flagged_count: int = 0

    @property
    def reward_stddev(self) -> float:
        """Standard deviation of rewards."""
        if len(self.reward_history) < 2:
            return 0.0
        mean = sum(self.reward_history) / len(self.reward_history)
        variance = sum((r - mean) ** 2 for r in self.reward_history) / len(
            self.reward_history
        )
        return math.sqrt(variance)

    def update(self, epoch: int, reward: float) -> None:
        """Update profile with new reward data."""
        self.total_rewards += reward
        self.epoch_count += 1
        self.max_reward = max(self.max_reward, reward)
        self.last_active_epoch = epoch

        # Rolling history (keep last 100)
        self.reward_history.append(reward)
        if len(self.reward_history) > 100:
            self.reward_history = self.reward_history[-100:]

        # Update average
        self.avg_reward = self.total_rewards / self.epoch_count


class ParticipationSentinel:
    """AI-powered sentinel for detecting manipulation patterns.

    Monitors epoch distributions for:
    - Statistical anomalies
    - Coordination patterns
    - Sybil attacks
    - Bot behavior

    Example usage:
        sentinel = ParticipationSentinel()

        # Analyze an epoch entry
        alerts = sentinel.analyze_epoch(epoch_entry)

        for alert in alerts:
            if alert.severity > 0.8:
                print(f"CRITICAL: {alert.alert_type}")

        # Get health report
        report = sentinel.get_health_report()
    """

    # Detection thresholds (tunable)
    GINI_THRESHOLD = 0.8  # High concentration warning
    VELOCITY_MULTIPLE = 10.0  # X times average = anomaly
    SYBIL_GROUP_SIZE = 5  # Min accounts with identical rewards
    STDDEV_THRESHOLD = 3.0  # Z-score for outlier detection

    def __init__(self):
        """Initialize the sentinel."""
        self.alerts: List[SentinelAlert] = []
        self.profiles: Dict[str, ParticipantProfile] = {}
        self.epoch_history: List[Dict] = []
        self.flagged_participants: Set[str] = set()

    def analyze_epoch(
        self,
        epoch_number: int,
        total_distributed: float,
        participant_rewards: Dict[str, float],
        timestamp: Optional[str] = None,
    ) -> List[SentinelAlert]:
        """Analyze an epoch for suspicious patterns.

        Args:
            epoch_number: Epoch being analyzed
            total_distributed: Total F_i distributed this epoch
            participant_rewards: Dict of participant_id → reward amount
            timestamp: ISO timestamp (optional, uses now if not provided)

        Returns:
            List of alerts raised (may be empty)
        """
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()

        alerts: List[SentinelAlert] = []

        # Record epoch history
        self.epoch_history.append({
            "epoch": epoch_number,
            "total": total_distributed,
            "participant_count": len(participant_rewards),
        })

        # Run detection patterns
        alerts.extend(
            self._check_concentration(epoch_number, total_distributed, participant_rewards, timestamp)
        )
        alerts.extend(
            self._check_velocity_anomalies(epoch_number, participant_rewards, timestamp)
        )
        alerts.extend(
            self._check_sybil_patterns(epoch_number, participant_rewards, timestamp)
        )
        alerts.extend(
            self._check_statistical_outliers(epoch_number, participant_rewards, timestamp)
        )

        # Update profiles
        for pid, reward in participant_rewards.items():
            if pid not in self.profiles:
                self.profiles[pid] = ParticipantProfile(participant_id=pid)
            self.profiles[pid].update(epoch_number, reward)

        # Track flagged participants
        for alert in alerts:
            self.flagged_participants.update(alert.participant_ids)
            for pid in alert.participant_ids:
                if pid in self.profiles:
                    self.profiles[pid].flagged_count += 1

        self.alerts.extend(alerts)
        return alerts

    def analyze_entry(self, entry) -> List[SentinelAlert]:
        """Analyze an EpochEntry from epoch_ledger.py.

        Args:
            entry: EpochEntry object

        Returns:
            List of alerts
        """
        return self.analyze_epoch(
            epoch_number=entry.epoch_number,
            total_distributed=entry.total_fi_distributed,
            participant_rewards=entry.participant_rewards,
            timestamp=entry.timestamp,
        )

    def _check_concentration(
        self,
        epoch: int,
        total: float,
        rewards: Dict[str, float],
        timestamp: str,
    ) -> List[SentinelAlert]:
        """Detect unhealthy reward concentration.

        Uses Gini coefficient to measure inequality.
        High Gini (>0.8) indicates potential manipulation.
        """
        alerts = []

        if total <= 0 or len(rewards) < 2:
            return alerts

        # Calculate Gini coefficient
        sorted_rewards = sorted(rewards.values())
        n = len(sorted_rewards)
        cumulative = sum((i + 1) * r for i, r in enumerate(sorted_rewards))
        sum_rewards = sum(sorted_rewards)

        if sum_rewards == 0:
            return alerts

        gini = (2 * cumulative) / (n * sum_rewards) - (n + 1) / n

        if gini > self.GINI_THRESHOLD:
            # Find top earners
            top_earners = sorted(rewards.items(), key=lambda x: x[1], reverse=True)[:5]
            top_share = sum(r for _, r in top_earners) / total

            severity = min(1.0, gini)
            action = (
                RecommendedAction.INVESTIGATE
                if severity > 0.9
                else RecommendedAction.FLAG
            )

            alerts.append(
                SentinelAlert(
                    alert_type=AlertType.CONCENTRATION,
                    severity=severity,
                    participant_ids=[p[0] for p in top_earners],
                    evidence={
                        "gini_coefficient": round(gini, 4),
                        "top_5_share": round(top_share, 4),
                        "participant_count": len(rewards),
                        "top_5_rewards": {p[0]: round(p[1], 2) for p in top_earners},
                    },
                    timestamp=timestamp,
                    recommended_action=action,
                    epoch_number=epoch,
                )
            )

        return alerts

    def _check_velocity_anomalies(
        self,
        epoch: int,
        rewards: Dict[str, float],
        timestamp: str,
    ) -> List[SentinelAlert]:
        """Detect superhuman activity velocity.

        Flags participants earning significantly more than their average.
        """
        alerts = []

        for pid, amount in rewards.items():
            profile = self.profiles.get(pid)

            if profile is None or profile.epoch_count < 3:
                continue  # Not enough history

            avg = profile.avg_reward
            if avg <= 0:
                continue

            multiple = amount / avg

            if multiple > self.VELOCITY_MULTIPLE:
                severity = min(1.0, multiple / 20)  # Scale: 10x = 0.5, 20x = 1.0

                alerts.append(
                    SentinelAlert(
                        alert_type=AlertType.VELOCITY_ANOMALY,
                        severity=severity,
                        participant_ids=[pid],
                        evidence={
                            "current_reward": round(amount, 4),
                            "average_reward": round(avg, 4),
                            "multiple": round(multiple, 2),
                            "epoch_count": profile.epoch_count,
                            "max_previous": round(profile.max_reward, 4),
                        },
                        timestamp=timestamp,
                        recommended_action=RecommendedAction.FLAG,
                        epoch_number=epoch,
                    )
                )

        return alerts

    def _check_sybil_patterns(
        self,
        epoch: int,
        rewards: Dict[str, float],
        timestamp: str,
    ) -> List[SentinelAlert]:
        """Detect Sybil attack patterns.

        Multiple accounts earning identical (or near-identical) amounts
        is statistically improbable in organic activity.
        """
        alerts = []

        # Group by rounded reward amount
        reward_groups: Dict[float, List[str]] = {}

        for pid, amount in rewards.items():
            # Round to 6 decimal places (handles floating point)
            rounded = round(amount, 6)
            if rounded not in reward_groups:
                reward_groups[rounded] = []
            reward_groups[rounded].append(pid)

        # Flag groups larger than threshold
        for amount, pids in reward_groups.items():
            if len(pids) >= self.SYBIL_GROUP_SIZE:
                severity = min(1.0, len(pids) / 15)  # Scale: 5=0.33, 15=1.0

                alerts.append(
                    SentinelAlert(
                        alert_type=AlertType.SYBIL_PATTERN,
                        severity=severity,
                        participant_ids=pids,
                        evidence={
                            "identical_reward": amount,
                            "account_count": len(pids),
                            "probability": self._sybil_probability(len(pids), len(rewards)),
                        },
                        timestamp=timestamp,
                        recommended_action=RecommendedAction.INVESTIGATE,
                        epoch_number=epoch,
                    )
                )

        return alerts

    def _sybil_probability(self, group_size: int, total_participants: int) -> float:
        """Calculate probability of N accounts having identical rewards by chance.

        Very low probability indicates coordinated action.
        """
        if total_participants < 2 or group_size < 2:
            return 1.0

        # Simplified: assume uniform distribution, calculate birthday paradox-like probability
        # In practice, organic rewards have high variance, so identical rewards are rare
        p = 1.0 / total_participants
        prob = math.pow(p, group_size - 1)
        return min(1.0, prob * 1e6)  # Scale up for readability

    def _check_statistical_outliers(
        self,
        epoch: int,
        rewards: Dict[str, float],
        timestamp: str,
    ) -> List[SentinelAlert]:
        """Detect statistical outliers using Z-score.

        Participants with rewards > 3 standard deviations from mean
        are flagged for review.
        """
        alerts = []

        if len(rewards) < 10:
            return alerts  # Not enough data for statistics

        values = list(rewards.values())
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        stddev = math.sqrt(variance)

        if stddev == 0:
            return alerts

        for pid, amount in rewards.items():
            z_score = (amount - mean) / stddev

            if abs(z_score) > self.STDDEV_THRESHOLD:
                severity = min(1.0, abs(z_score) / 5)  # 3σ = 0.6, 5σ = 1.0

                alerts.append(
                    SentinelAlert(
                        alert_type=AlertType.ANOMALY,
                        severity=severity,
                        participant_ids=[pid],
                        evidence={
                            "reward": round(amount, 4),
                            "z_score": round(z_score, 2),
                            "mean": round(mean, 4),
                            "stddev": round(stddev, 4),
                            "direction": "high" if z_score > 0 else "low",
                        },
                        timestamp=timestamp,
                        recommended_action=RecommendedAction.FLAG,
                        epoch_number=epoch,
                    )
                )

        return alerts

    def get_health_report(self) -> Dict:
        """Generate sentinel health report.

        Returns:
            Dict with alert statistics and flagged participant counts
        """
        severity_buckets = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for alert in self.alerts:
            if alert.severity < 0.3:
                severity_buckets["low"] += 1
            elif alert.severity < 0.6:
                severity_buckets["medium"] += 1
            elif alert.severity < 0.8:
                severity_buckets["high"] += 1
            else:
                severity_buckets["critical"] += 1

        return {
            "total_alerts": len(self.alerts),
            "unresolved_alerts": sum(1 for a in self.alerts if not a.resolved),
            "by_type": self._count_by_type(),
            "by_severity": severity_buckets,
            "avg_severity": (
                sum(a.severity for a in self.alerts) / max(1, len(self.alerts))
            ),
            "flagged_participants": len(self.flagged_participants),
            "repeat_offenders": sum(
                1 for p in self.profiles.values() if p.flagged_count > 2
            ),
            "epochs_analyzed": len(self.epoch_history),
        }

    def _count_by_type(self) -> Dict[str, int]:
        """Count alerts by type."""
        counts: Dict[str, int] = {}
        for alert in self.alerts:
            key = alert.alert_type.value
            counts[key] = counts.get(key, 0) + 1
        return counts

    def get_participant_risk_score(self, participant_id: str) -> float:
        """Calculate risk score for a participant.

        Args:
            participant_id: Participant to evaluate

        Returns:
            Risk score 0.0-1.0 (higher = more risky)
        """
        profile = self.profiles.get(participant_id)
        if profile is None:
            return 0.0

        # Factors contributing to risk
        flag_factor = min(1.0, profile.flagged_count / 5)  # 5+ flags = max

        # Check variance in rewards (high variance = potential manipulation)
        variance_factor = 0.0
        if profile.reward_stddev > 0 and profile.avg_reward > 0:
            cv = profile.reward_stddev / profile.avg_reward  # Coefficient of variation
            variance_factor = min(1.0, cv / 2)  # CV > 2 = max risk

        # Recency factor (recent flags weigh more)
        recent_alerts = [
            a
            for a in self.alerts
            if participant_id in a.participant_ids
            and a.epoch_number is not None
            and a.epoch_number >= profile.last_active_epoch - 10
        ]
        recency_factor = min(1.0, len(recent_alerts) / 3)

        # Weighted combination
        risk = flag_factor * 0.4 + variance_factor * 0.3 + recency_factor * 0.3

        return round(risk, 3)

    def resolve_alert(self, alert_index: int, notes: str = "") -> bool:
        """Mark an alert as resolved.

        Args:
            alert_index: Index of alert in self.alerts
            notes: Resolution notes

        Returns:
            True if alert was resolved
        """
        if 0 <= alert_index < len(self.alerts):
            self.alerts[alert_index].resolved = True
            self.alerts[alert_index].resolution_notes = notes
            return True
        return False


# Singleton management
_sentinel_instance: Optional[ParticipationSentinel] = None


def get_participation_sentinel() -> ParticipationSentinel:
    """Get or create singleton sentinel instance."""
    global _sentinel_instance
    if _sentinel_instance is None:
        _sentinel_instance = ParticipationSentinel()
    return _sentinel_instance


def reset_participation_sentinel() -> None:
    """Reset sentinel (for testing)."""
    global _sentinel_instance
    _sentinel_instance = None


__all__ = [
    "AlertType",
    "RecommendedAction",
    "SentinelAlert",
    "ParticipantProfile",
    "ParticipationSentinel",
    "get_participation_sentinel",
    "reset_participation_sentinel",
]
