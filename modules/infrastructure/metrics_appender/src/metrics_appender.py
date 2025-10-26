#!/usr/bin/env python3
"""
WRE Skills Metrics Appender
Append-only JSON metrics collection for real-time skill execution tracking
WSP Compliance: WSP 77 (Agent Coordination), WSP 91 (DAEMON Observability)
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MetricsAppender:
    """
    Append-only metrics writer for skill execution tracking

    Provides fast, real-time metrics collection without database overhead.
    JSON files are append-only for easy diffing and rollback.
    """

    def __init__(self, metrics_dir: Optional[Path] = None):
        """
        Initialize metrics appender

        Args:
            metrics_dir: Directory for metrics files (defaults to recursive_improvement/metrics/)
        """
        if metrics_dir is None:
            self.metrics_dir = Path(__file__).parent.parent / "recursive_improvement" / "metrics"
        else:
            self.metrics_dir = Path(metrics_dir)

        self.metrics_dir.mkdir(parents=True, exist_ok=True)

    def append_fidelity_metric(
        self,
        skill_name: str,
        execution_id: str,
        pattern_fidelity: float,
        patterns_followed: int,
        patterns_missed: int,
        patterns_detail: Dict[str, bool],
        agent: str,
        timestamp: Optional[float] = None
    ) -> None:
        """
        Append pattern fidelity metric for skill execution

        Args:
            skill_name: Name of skill
            execution_id: Unique execution identifier
            pattern_fidelity: Overall fidelity score (0.0-1.0)
            patterns_followed: Count of patterns agent followed
            patterns_missed: Count of patterns agent missed
            patterns_detail: Dict mapping pattern name to followed (bool)
            agent: Agent that executed (gemma, qwen, grok, ui-tars)
            timestamp: Unix timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = time.time()

        metric = {
            "execution_id": execution_id,
            "timestamp": timestamp,
            "timestamp_iso": datetime.fromtimestamp(timestamp).isoformat(),
            "skill_name": skill_name,
            "agent": agent,
            "pattern_fidelity": pattern_fidelity,
            "patterns_followed": patterns_followed,
            "patterns_missed": patterns_missed,
            "patterns_detail": patterns_detail,
            "metric_type": "fidelity"
        }

        self._append_to_file(f"{skill_name}_fidelity.json", metric)
        logger.debug(f"[METRICS] Fidelity metric appended: {skill_name} | fidelity={pattern_fidelity:.2f}")

    def append_outcome_metric(
        self,
        skill_name: str,
        execution_id: str,
        decision: str,
        expected_decision: Optional[str],
        correct: bool,
        confidence: float,
        reasoning: str,
        agent: str,
        timestamp: Optional[float] = None
    ) -> None:
        """
        Append outcome quality metric for skill execution

        Args:
            skill_name: Name of skill
            execution_id: Unique execution identifier
            decision: Decision made by agent
            expected_decision: Expected/correct decision (if known)
            correct: Whether decision was correct
            confidence: Agent's confidence score (0.0-1.0)
            reasoning: Agent's reasoning for decision
            agent: Agent that executed
            timestamp: Unix timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = time.time()

        metric = {
            "execution_id": execution_id,
            "timestamp": timestamp,
            "timestamp_iso": datetime.fromtimestamp(timestamp).isoformat(),
            "skill_name": skill_name,
            "agent": agent,
            "decision": decision,
            "expected_decision": expected_decision,
            "correct": correct,
            "confidence": confidence,
            "reasoning": reasoning,
            "metric_type": "outcome"
        }

        self._append_to_file(f"{skill_name}_outcomes.json", metric)
        logger.debug(f"[METRICS] Outcome metric appended: {skill_name} | correct={correct} | confidence={confidence:.2f}")

    def append_performance_metric(
        self,
        skill_name: str,
        execution_id: str,
        execution_time_ms: int,
        agent: str,
        exception_occurred: bool = False,
        exception_type: Optional[str] = None,
        memory_usage_mb: Optional[float] = None,
        timestamp: Optional[float] = None
    ) -> None:
        """
        Append performance metric for skill execution

        Args:
            skill_name: Name of skill
            execution_id: Unique execution identifier
            execution_time_ms: Execution time in milliseconds
            agent: Agent that executed
            exception_occurred: Whether an exception was raised
            exception_type: Type of exception (if any)
            memory_usage_mb: Memory usage in MB (optional)
            timestamp: Unix timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = time.time()

        metric = {
            "execution_id": execution_id,
            "timestamp": timestamp,
            "timestamp_iso": datetime.fromtimestamp(timestamp).isoformat(),
            "skill_name": skill_name,
            "agent": agent,
            "execution_time_ms": execution_time_ms,
            "exception_occurred": exception_occurred,
            "exception_type": exception_type,
            "memory_usage_mb": memory_usage_mb,
            "metric_type": "performance"
        }

        self._append_to_file(f"{skill_name}_performance.json", metric)
        logger.debug(f"[METRICS] Performance metric appended: {skill_name} | time={execution_time_ms}ms | exception={exception_occurred}")

    def append_promotion_event(
        self,
        skill_name: str,
        from_state: str,
        to_state: str,
        approver: str,
        approval_ticket: str,
        reason: str,
        automated_checks: Dict[str, Any],
        timestamp: Optional[float] = None
    ) -> None:
        """
        Append promotion event for skill state change

        Args:
            skill_name: Name of skill
            from_state: Previous promotion state
            to_state: New promotion state
            approver: Who approved the promotion (usually 0102)
            approval_ticket: Approval ticket ID
            reason: Reason for promotion
            automated_checks: Results of automated promotion checks
            timestamp: Unix timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = time.time()

        event = {
            "event_id": f"promo_{skill_name}_{int(timestamp)}",
            "timestamp": timestamp,
            "timestamp_iso": datetime.fromtimestamp(timestamp).isoformat(),
            "skill_name": skill_name,
            "from_state": from_state,
            "to_state": to_state,
            "approver": approver,
            "approval_ticket": approval_ticket,
            "reason": reason,
            "automated_checks": automated_checks,
            "event_type": "promotion"
        }

        self._append_to_file(f"{skill_name}_promotion_log.json", event)
        logger.info(f"[PROMOTION] {skill_name}: {from_state} → {to_state} | approver={approver} | ticket={approval_ticket}")

    def append_rollback_event(
        self,
        skill_name: str,
        from_state: str,
        to_state: str,
        trigger_reason: str,
        trigger_metric: str,
        automated: bool = True,
        timestamp: Optional[float] = None
    ) -> None:
        """
        Append rollback event for skill demotion

        Args:
            skill_name: Name of skill
            from_state: Previous promotion state
            to_state: New promotion state (demoted)
            trigger_reason: Why rollback was triggered
            trigger_metric: Metric that triggered rollback
            automated: Whether rollback was automatic or manual
            timestamp: Unix timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = time.time()

        event = {
            "event_id": f"rollback_{skill_name}_{int(timestamp)}",
            "timestamp": timestamp,
            "timestamp_iso": datetime.fromtimestamp(timestamp).isoformat(),
            "skill_name": skill_name,
            "from_state": from_state,
            "to_state": to_state,
            "trigger_reason": trigger_reason,
            "trigger_metric": trigger_metric,
            "automated": automated,
            "event_type": "rollback"
        }

        self._append_to_file(f"{skill_name}_promotion_log.json", event)
        logger.warning(f"[ROLLBACK] {skill_name}: {from_state} → {to_state} | reason={trigger_reason} | automated={automated}")

    def _append_to_file(self, filename: str, metric: Dict[str, Any]) -> None:
        """
        Append metric to JSON file (newline-delimited JSON format)

        Args:
            filename: Name of metrics file
            metric: Metric data to append
        """
        filepath = self.metrics_dir / filename

        try:
            with open(filepath, 'a', encoding='utf-8') as f:
                json.dump(metric, f, ensure_ascii=False)
                f.write('\n')
        except Exception as e:
            logger.error(f"[METRICS-ERROR] Failed to append to {filename}: {e}")
            raise

    def read_metrics(self, filename: str, limit: Optional[int] = None) -> list:
        """
        Read metrics from file (for debugging/inspection)

        Args:
            filename: Name of metrics file
            limit: Max number of recent metrics to read (default: all)

        Returns:
            List of metric dictionaries
        """
        filepath = self.metrics_dir / filename

        if not filepath.exists():
            return []

        metrics = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        metrics.append(json.loads(line))
        except Exception as e:
            logger.error(f"[METRICS-ERROR] Failed to read {filename}: {e}")
            return []

        if limit:
            return metrics[-limit:]
        return metrics


# Example usage
if __name__ == "__main__":
    # Initialize appender
    appender = MetricsAppender()

    # Example: Append fidelity metric
    appender.append_fidelity_metric(
        skill_name="youtube_spam_detection",
        execution_id="exec_20251020_001",
        pattern_fidelity=0.95,
        patterns_followed=19,
        patterns_missed=1,
        patterns_detail={
            "caps_check_executed": True,
            "repetition_check_executed": True,
            "rate_limit_applied": True,
            "toxicity_check_executed": True,
            "allowed_and_routed": False  # missed this one
        },
        agent="gemma"
    )

    # Example: Append outcome metric
    appender.append_outcome_metric(
        skill_name="youtube_spam_detection",
        execution_id="exec_20251020_001",
        decision="block",
        expected_decision="block",
        correct=True,
        confidence=0.98,
        reasoning="CAPS spam detected, length=38, uppercase=100%",
        agent="gemma"
    )

    # Example: Append performance metric
    appender.append_performance_metric(
        skill_name="youtube_spam_detection",
        execution_id="exec_20251020_001",
        execution_time_ms=45,
        agent="gemma",
        exception_occurred=False
    )

    print("[OK] Metrics appended successfully")

    # Read back metrics
    fidelity_metrics = appender.read_metrics("youtube_spam_detection_fidelity.json", limit=5)
    print(f"[DEBUG] Last 5 fidelity metrics: {len(fidelity_metrics)} entries")
