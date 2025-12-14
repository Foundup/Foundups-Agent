"""
Action Pattern Learner - Machine learning for browser automation success

Learns from action execution outcomes to improve future success rates.
Integrates with WRE Pattern Memory for persistent storage.

WSP Compliance:
    - WSP 48: Recursive pattern learning
    - WSP 77: AI Overseer integration
    - WSP 91: Observability

Sprint: V6 - Pattern Learning & Optimization
"""

import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ActionPattern:
    """Pattern learned from successful action execution."""
    pattern_id: str
    action: str
    platform: str
    driver: str  # selenium or vision
    params_hash: str  # Hash of common parameters
    success_count: int = 0
    failure_count: int = 0
    avg_duration_ms: float = 0.0
    last_used: str = None
    confidence: float = 0.0
    # 012 Human validation (WSP 77 Phase 3: Human Supervision)
    human_validation_count: int = 0
    human_success_count: int = 0
    last_012_comment: str = None

    @property
    def success_rate(self) -> float:
        """Calculate AI-reported success rate."""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return self.success_count / total

    @property
    def human_success_rate(self) -> float:
        """Calculate 012 validation success rate."""
        if self.human_validation_count == 0:
            return 0.0
        return self.human_success_count / self.human_validation_count

    @property
    def human_agreement_rate(self) -> float:
        """Calculate AI-Human agreement rate (learning signal)."""
        if self.human_validation_count == 0:
            return 0.0
        # Agreement = both succeeded or both failed
        # Simplified: assume validation happened on last N executions
        min_count = min(self.success_count + self.failure_count, self.human_validation_count)
        if min_count == 0:
            return 0.0
        # This is approximate - actual agreement requires per-execution tracking
        # For now, compare success rates as proxy
        ai_rate = self.success_rate
        human_rate = self.human_success_rate
        return 1.0 - abs(ai_rate - human_rate)  # Inverse of difference

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "action": self.action,
            "platform": self.platform,
            "driver": self.driver,
            "params_hash": self.params_hash,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "avg_duration_ms": self.avg_duration_ms,
            "last_used": self.last_used,
            "confidence": self.confidence,
            "human_validation_count": self.human_validation_count,
            "human_success_count": self.human_success_count,
            "last_012_comment": self.last_012_comment,
            "success_rate": self.success_rate,
            "human_success_rate": self.human_success_rate,
            "human_agreement_rate": self.human_agreement_rate,
        }


@dataclass
class RetryStrategy:
    """Adaptive retry strategy based on learned patterns."""
    max_retries: int
    backoff_ms: List[int]  # Delay between retries
    alternate_driver: bool  # Try alternate driver on retry
    success_probability: float


class ActionPatternLearner:
    """
    Learns patterns from browser action execution for optimization.

    Implements Sprint V6 objectives:
    - Pattern storage in Pattern Memory
    - Adaptive retry logic
    - A/B testing support
    - Performance metrics

    Usage:
        learner = ActionPatternLearner()

        # Record successful action
        learner.record_success(
            action="like_comment",
            platform="youtube",
            driver="vision",
            params={"video_id": "abc", "comment_id": "xyz"},
            duration_ms=450
        )

        # Get retry strategy for failed action
        strategy = learner.get_retry_strategy(
            action="like_comment",
            platform="youtube"
        )

        # Get best driver recommendation
        driver = learner.recommend_driver(
            action="like_comment",
            platform="youtube"
        )
    """

    def __init__(self, storage_path: Path = None):
        """
        Initialize pattern learner.

        Args:
            storage_path: Path to pattern storage JSON file
        """
        if storage_path is None:
            storage_path = Path("modules/infrastructure/foundups_vision/data/action_patterns.json")

        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        self._patterns: Dict[str, ActionPattern] = {}
        self._ab_tests: Dict[str, Dict[str, Any]] = {}

        # Load existing patterns
        self._load_patterns()

        logger.info(f"[LEARNER] Initialized with {len(self._patterns)} patterns")

    def record_success(
        self,
        action: str,
        platform: str,
        driver: str,
        params: Dict[str, Any],
        duration_ms: int,
    ) -> None:
        """
        Record a successful action execution.

        Args:
            action: Action name
            platform: Platform name
            driver: Driver used
            params: Action parameters
            duration_ms: Execution duration
        """
        pattern_id = self._get_pattern_id(action, platform, driver, params)

        if pattern_id in self._patterns:
            pattern = self._patterns[pattern_id]
            pattern.success_count += 1

            # Update average duration (running average)
            total = pattern.success_count + pattern.failure_count
            pattern.avg_duration_ms = (
                (pattern.avg_duration_ms * (total - 1) + duration_ms) / total
            )
        else:
            pattern = ActionPattern(
                pattern_id=pattern_id,
                action=action,
                platform=platform,
                driver=driver,
                params_hash=self._hash_params(params),
                success_count=1,
                avg_duration_ms=float(duration_ms),
            )
            self._patterns[pattern_id] = pattern

        pattern.last_used = datetime.utcnow().isoformat() + "Z"
        pattern.confidence = self._calculate_confidence(pattern)

        self._save_patterns()

        logger.debug(f"[LEARNER] Recorded success: {pattern_id} (success_rate={pattern.success_rate:.1%})")

    def record_failure(
        self,
        action: str,
        platform: str,
        driver: str,
        params: Dict[str, Any],
    ) -> None:
        """Record a failed action execution."""
        pattern_id = self._get_pattern_id(action, platform, driver, params)

        if pattern_id in self._patterns:
            pattern = self._patterns[pattern_id]
            pattern.failure_count += 1
        else:
            pattern = ActionPattern(
                pattern_id=pattern_id,
                action=action,
                platform=platform,
                driver=driver,
                params_hash=self._hash_params(params),
                failure_count=1,
            )
            self._patterns[pattern_id] = pattern

        pattern.last_used = datetime.utcnow().isoformat() + "Z"
        pattern.confidence = self._calculate_confidence(pattern)

        self._save_patterns()

        logger.debug(f"[LEARNER] Recorded failure: {pattern_id} (success_rate={pattern.success_rate:.1%})")

    def get_retry_strategy(
        self,
        action: str,
        platform: str,
        current_driver: str = None,
    ) -> RetryStrategy:
        """
        Get adaptive retry strategy based on learned patterns.

        Returns intelligent retry strategy using historical data.

        Args:
            action: Action name
            platform: Platform name
            current_driver: Driver that failed

        Returns:
            RetryStrategy with optimized parameters
        """
        # Find patterns for this action/platform
        matching_patterns = [
            p for p in self._patterns.values()
            if p.action == action and p.platform == platform
        ]

        if not matching_patterns:
            # No patterns - use conservative defaults
            return RetryStrategy(
                max_retries=3,
                backoff_ms=[1000, 2000, 4000],
                alternate_driver=True,
                success_probability=0.5,
            )

        # Calculate success probability
        total_attempts = sum(p.success_count + p.failure_count for p in matching_patterns)
        total_successes = sum(p.success_count for p in matching_patterns)
        success_prob = total_successes / total_attempts if total_attempts > 0 else 0.5

        # Adaptive retry count based on historical success
        if success_prob > 0.8:
            max_retries = 2  # High success - fewer retries needed
        elif success_prob > 0.5:
            max_retries = 3  # Medium success - normal retries
        else:
            max_retries = 4  # Low success - more retries

        # Check if alternate driver improves success rate
        if current_driver:
            other_driver = "vision" if current_driver == "selenium" else "selenium"
            other_patterns = [p for p in matching_patterns if p.driver == other_driver]

            if other_patterns:
                other_success_rate = sum(p.success_count for p in other_patterns) / sum(
                    p.success_count + p.failure_count for p in other_patterns
                )
                current_patterns = [p for p in matching_patterns if p.driver == current_driver]
                current_success_rate = sum(p.success_count for p in current_patterns) / sum(
                    p.success_count + p.failure_count for p in current_patterns
                ) if current_patterns else 0.0

                alternate_driver = other_success_rate > current_success_rate
            else:
                alternate_driver = True  # Try alternate if no data
        else:
            alternate_driver = True

        # Adaptive backoff based on avg duration
        avg_duration = sum(p.avg_duration_ms for p in matching_patterns) / len(matching_patterns)
        base_backoff = int(avg_duration * 0.5)  # 50% of avg duration
        backoff_ms = [base_backoff * (i + 1) for i in range(max_retries)]

        return RetryStrategy(
            max_retries=max_retries,
            backoff_ms=backoff_ms,
            alternate_driver=alternate_driver,
            success_probability=success_prob,
        )

    def recommend_driver(
        self,
        action: str,
        platform: str,
    ) -> str:
        """
        Recommend best driver based on learned patterns.

        Args:
            action: Action name
            platform: Platform name

        Returns:
            Recommended driver: "selenium" or "vision"
        """
        matching_patterns = [
            p for p in self._patterns.values()
            if p.action == action and p.platform == platform
        ]

        if not matching_patterns:
            # No data - default to vision (more flexible)
            return "vision"

        # Group by driver
        by_driver = defaultdict(list)
        for p in matching_patterns:
            by_driver[p.driver].append(p)

        # Calculate success rates by driver
        driver_scores = {}
        for driver, patterns in by_driver.items():
            total = sum(p.success_count + p.failure_count for p in patterns)
            successes = sum(p.success_count for p in patterns)
            driver_scores[driver] = successes / total if total > 0 else 0.0

        # Return driver with highest success rate
        best_driver = max(driver_scores.items(), key=lambda x: x[1])[0]

        logger.debug(f"[LEARNER] Recommending {best_driver} for {action}/{platform} (scores={driver_scores})")

        return best_driver

    def start_ab_test(
        self,
        test_id: str,
        action: str,
        platform: str,
        variant_a: str,  # Driver name
        variant_b: str,  # Driver name
        sample_size: int = 50,
    ) -> None:
        """
        Start A/B test between two drivers.

        Args:
            test_id: Unique test identifier
            action: Action to test
            platform: Platform to test on
            variant_a: First driver variant
            variant_b: Second driver variant
            sample_size: Number of executions per variant
        """
        self._ab_tests[test_id] = {
            "action": action,
            "platform": platform,
            "variant_a": variant_a,
            "variant_b": variant_b,
            "sample_size": sample_size,
            "a_count": 0,
            "b_count": 0,
            "started": datetime.utcnow().isoformat() + "Z",
            "status": "running",
        }

        logger.info(f"[LEARNER] Started A/B test {test_id}: {variant_a} vs {variant_b}")

    def get_ab_test_variant(self, test_id: str) -> Optional[str]:
        """Get next variant to test (round-robin)."""
        if test_id not in self._ab_tests:
            return None

        test = self._ab_tests[test_id]

        if test["status"] != "running":
            return None

        # Round-robin assignment
        if test["a_count"] <= test["b_count"]:
            test["a_count"] += 1
            return test["variant_a"]
        else:
            test["b_count"] += 1
            return test["variant_b"]

    def get_ab_test_results(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get A/B test results."""
        if test_id not in self._ab_tests:
            return None

        test = self._ab_tests[test_id]

        # Get patterns for each variant
        a_patterns = [
            p for p in self._patterns.values()
            if p.action == test["action"]
            and p.platform == test["platform"]
            and p.driver == test["variant_a"]
        ]
        b_patterns = [
            p for p in self._patterns.values()
            if p.action == test["action"]
            and p.platform == test["platform"]
            and p.driver == test["variant_b"]
        ]

        def calc_stats(patterns):
            if not patterns:
                return {"success_rate": 0.0, "avg_duration_ms": 0.0, "count": 0}
            total = sum(p.success_count + p.failure_count for p in patterns)
            successes = sum(p.success_count for p in patterns)
            return {
                "success_rate": successes / total if total > 0 else 0.0,
                "avg_duration_ms": sum(p.avg_duration_ms for p in patterns) / len(patterns),
                "count": total,
            }

        a_stats = calc_stats(a_patterns)
        b_stats = calc_stats(b_patterns)

        return {
            "test_id": test_id,
            "action": test["action"],
            "platform": test["platform"],
            "variant_a": test["variant_a"],
            "variant_b": test["variant_b"],
            "a_stats": a_stats,
            "b_stats": b_stats,
            "winner": test["variant_a"] if a_stats["success_rate"] > b_stats["success_rate"] else test["variant_b"],
            "status": test["status"],
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        if not self._patterns:
            return {"total_patterns": 0}

        total_attempts = sum(p.success_count + p.failure_count for p in self._patterns.values())
        total_successes = sum(p.success_count for p in self._patterns.values())

        # Metrics by platform
        by_platform = defaultdict(lambda: {"successes": 0, "attempts": 0})
        for p in self._patterns.values():
            by_platform[p.platform]["successes"] += p.success_count
            by_platform[p.platform]["attempts"] += p.success_count + p.failure_count

        platform_stats = {
            platform: {
                "success_rate": stats["successes"] / stats["attempts"] if stats["attempts"] > 0 else 0.0,
                "total_attempts": stats["attempts"],
            }
            for platform, stats in by_platform.items()
        }

        return {
            "total_patterns": len(self._patterns),
            "total_attempts": total_attempts,
            "total_successes": total_successes,
            "overall_success_rate": total_successes / total_attempts if total_attempts > 0 else 0.0,
            "platforms": platform_stats,
            "active_ab_tests": len([t for t in self._ab_tests.values() if t["status"] == "running"]),
        }

    def record_human_validation(
        self,
        action: str,
        platform: str,
        driver: str,
        params: Dict[str, Any],
        human_success: bool,
        comment_012: str = None,
    ) -> None:
        """
        Record 012 human validation for an action.

        Integrates with WSP 77 Phase 3: Human Supervision.
        Tracks AI-Human agreement for learning signal.

        Args:
            action: Action name
            platform: Platform name
            driver: Driver used
            params: Action parameters
            human_success: Whether 012 validated action as successful
            comment_012: Optional feedback comment from 012
        """
        pattern_id = self._get_pattern_id(action, platform, driver, params)

        if pattern_id in self._patterns:
            pattern = self._patterns[pattern_id]
        else:
            # Create pattern if it doesn't exist yet
            pattern = ActionPattern(
                pattern_id=pattern_id,
                action=action,
                platform=platform,
                driver=driver,
                params_hash=self._hash_params(params),
            )
            self._patterns[pattern_id] = pattern

        pattern.human_validation_count += 1
        if human_success:
            pattern.human_success_count += 1
        if comment_012:
            pattern.last_012_comment = comment_012

        pattern.last_used = datetime.utcnow().isoformat() + "Z"

        self._save_patterns()

        logger.debug(f"[LEARNER] Recorded 012 validation: {pattern_id} (human_success={human_success}, agreement={pattern.human_agreement_rate:.1%})")

    def get_012_recommendations(
        self,
        action: str,
        platform: str,
    ) -> List[Dict[str, Any]]:
        """
        Get 012's feedback recommendations for an action.

        Returns patterns with low AI-Human agreement (learning opportunities).

        Args:
            action: Action name
            platform: Platform name

        Returns:
            List of recommendations with 012 comments
        """
        matching_patterns = [
            p for p in self._patterns.values()
            if p.action == action and p.platform == platform and p.last_012_comment
        ]

        if not matching_patterns:
            return []

        # Sort by agreement rate (lowest first = biggest learning opportunities)
        matching_patterns.sort(key=lambda p: p.human_agreement_rate)

        recommendations = []
        for p in matching_patterns[:3]:  # Top 3 learning opportunities
            pattern_type = "unknown"
            if p.success_rate > p.human_success_rate:
                pattern_type = "AI overconfident"
            elif p.success_rate < p.human_success_rate:
                pattern_type = "AI underconfident"
            else:
                pattern_type = "AI-Human aligned"

            recommendations.append({
                "comment": p.last_012_comment,
                "pattern": pattern_type,
                "ai_success_rate": p.success_rate,
                "human_success_rate": p.human_success_rate,
                "agreement_rate": p.human_agreement_rate,
            })

        return recommendations

    def display_pre_learning(
        self,
        action: str,
        platform: str,
    ) -> None:
        """
        Display historical performance BEFORE executing action.

        Shows 012 with:
        - Past attempts
        - AI-Human agreement rate
        - 012's past feedback

        Args:
            action: Action about to be executed
            platform: Platform name
        """
        matching_patterns = [
            p for p in self._patterns.values()
            if p.action == action and p.platform == platform
        ]

        if not matching_patterns:
            return  # No history to show

        # Aggregate statistics
        total_attempts = sum(p.success_count + p.failure_count for p in matching_patterns)
        total_validations = sum(p.human_validation_count for p in matching_patterns)

        if total_validations > 0:
            avg_agreement = sum(p.human_agreement_rate * p.human_validation_count for p in matching_patterns) / total_validations
            confidence = "HIGH" if avg_agreement >= 0.9 else "MEDIUM" if avg_agreement >= 0.7 else "LOW"

            print(f"\n    [LEARNING] Historical Performance:")
            print(f"      Attempts: {total_attempts}")
            print(f"      012 Validations: {total_validations}")
            print(f"      AI-Human Agreement: {avg_agreement:.1%}")
            print(f"      Confidence: {confidence}")

            # Show 012's recommendations
            recommendations = self.get_012_recommendations(action, platform)
            if recommendations:
                print(f"\n    [012 INSIGHTS] Past feedback:")
                for rec in recommendations:
                    print(f"      - {rec['pattern']}: \"{rec['comment']}\"")
                    print(f"        (AI: {rec['ai_success_rate']:.1%}, Human: {rec['human_success_rate']:.1%}, Agreement: {rec['agreement_rate']:.1%})")

    def display_post_learning(
        self,
        action: str,
        platform: str,
        ai_success: bool,
        human_success: bool,
        comment_012: str = None,
    ) -> None:
        """
        Display learning analysis AFTER 012 validation.

        Shows:
        - Whether AI and 012 agreed
        - Specific learning insight
        - Updated confidence

        Args:
            action: Action that was executed
            platform: Platform name
            ai_success: AI-reported success
            human_success: 012 validation result
            comment_012: Optional 012 comment
        """
        match = ai_success == human_success

        if match:
            print(f"    [LEARN] [OK] AI and Human AGREE - Pattern validated!")
            print(f"             Confidence in '{action}' increasing")
        else:
            print(f"    [LEARN] [WARN] MISMATCH - AI said {ai_success}, Human said {human_success}")
            print(f"             Pattern needs calibration!")

            if not ai_success and human_success:
                print(f"             AI was too cautious - action actually succeeded")
            elif ai_success and not human_success:
                print(f"             AI was overconfident - action actually failed")

        if comment_012:
            print(f"    [012 NOTE] {comment_012}")
            print(f"             This feedback will guide future '{action}' attempts")

        # Show updated statistics
        matching_patterns = [
            p for p in self._patterns.values()
            if p.action == action and p.platform == platform
        ]

        if matching_patterns:
            total_validations = sum(p.human_validation_count for p in matching_patterns)
            if total_validations > 0:
                avg_agreement = sum(p.human_agreement_rate * p.human_validation_count for p in matching_patterns) / total_validations
                confidence = "HIGH" if avg_agreement >= 0.9 else "MEDIUM" if avg_agreement >= 0.7 else "LOW"
                print(f"    [STATS] New performance - Agreement: {avg_agreement:.1%} | Confidence: {confidence}")

    def _get_pattern_id(
        self,
        action: str,
        platform: str,
        driver: str,
        params: Dict[str, Any],
    ) -> str:
        """Generate unique pattern identifier."""
        params_hash = self._hash_params(params)
        return f"{platform}:{action}:{driver}:{params_hash}"

    def _hash_params(self, params: Dict[str, Any]) -> str:
        """Hash parameters for pattern matching."""
        # Simple hash of common parameter keys
        key_signature = ":".join(sorted(params.keys()))
        return key_signature[:32]  # Truncate for storage

    def _calculate_confidence(self, pattern: ActionPattern) -> float:
        """Calculate confidence score for pattern."""
        total = pattern.success_count + pattern.failure_count

        # Confidence increases with sample size and success rate
        if total < 5:
            return 0.3  # Low confidence with < 5 samples
        elif total < 20:
            return 0.6 * pattern.success_rate  # Medium confidence
        else:
            return 0.9 * pattern.success_rate  # High confidence with 20+ samples

    def _load_patterns(self) -> None:
        """Load patterns from storage."""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)

            for pattern_data in data.get("patterns", []):
                # Remove calculated properties before instantiation
                calculated_props = {'success_rate', 'human_success_rate', 'human_agreement_rate'}
                pattern_data_clean = {k: v for k, v in pattern_data.items() if k not in calculated_props}
                pattern = ActionPattern(**pattern_data_clean)
                self._patterns[pattern.pattern_id] = pattern

            self._ab_tests = data.get("ab_tests", {})

            logger.info(f"[LEARNER] Loaded {len(self._patterns)} patterns from storage")

        except Exception as e:
            logger.error(f"[LEARNER] Failed to load patterns: {e}")

    def _save_patterns(self) -> None:
        """Save patterns to storage."""
        try:
            data = {
                "patterns": [p.to_dict() for p in self._patterns.values()],
                "ab_tests": self._ab_tests,
                "last_updated": datetime.utcnow().isoformat() + "Z",
            }

            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"[LEARNER] Failed to save patterns: {e}")


# Singleton instance
_learner = None


def get_learner() -> ActionPatternLearner:
    """Get singleton learner instance."""
    global _learner
    if _learner is None:
        _learner = ActionPatternLearner()
    return _learner
