#!/usr/bin/env python3
"""
WRE Skills Registry
Query helpers and promotion readiness checks using SQLite metrics
WSP Compliance: WSP 77 (Agent Coordination), WSP 91 (DAEMON Observability)
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class WRESkillsRegistry:
    """
    Skills registry with query helpers for metrics and promotion gating

    Provides structured queries over SQLite metrics database for:
    - Promotion readiness checks
    - Aggregated metrics analysis
    - A/B version comparisons
    - Rollback trigger detection
    """

    def __init__(self, sqlite_path: Optional[Path] = None, registry_json: Optional[Path] = None):
        """
        Initialize skills registry

        Args:
            sqlite_path: Path to SQLite metrics database
            registry_json: Path to skills_registry.json
        """
        if sqlite_path is None:
            self.sqlite_path = Path(__file__).parent / "skills_metrics.db"
        else:
            self.sqlite_path = Path(sqlite_path)

        if registry_json is None:
            self.registry_json = Path(__file__).parent / "skills_registry.json"
        else:
            self.registry_json = Path(registry_json)

        self.conn = None
        if self.sqlite_path.exists():
            self.conn = sqlite3.connect(str(self.sqlite_path))
            self.conn.row_factory = sqlite3.Row

    def check_promotion_readiness(
        self,
        skill_name: str,
        from_state: str,
        to_state: str
    ) -> Dict[str, Any]:
        """
        Check if skill meets promotion criteria

        Args:
            skill_name: Name of skill
            from_state: Current promotion state
            to_state: Target promotion state

        Returns:
            Dict with readiness status and detailed checks
        """
        if from_state == "prototype" and to_state == "staged":
            return self._check_prototype_to_staged(skill_name)
        elif from_state == "staged" and to_state == "production":
            return self._check_staged_to_production(skill_name)
        else:
            return {"ready": False, "error": f"Invalid promotion path: {from_state} → {to_state}"}

    def _check_prototype_to_staged(self, skill_name: str) -> Dict[str, Any]:
        """Check prototype → staged promotion criteria"""
        # Prototype metrics are manual (0102 validation)
        # This just verifies structure exists
        return {
            "ready": True,  # Manual approval required regardless
            "checks": {
                "pattern_fidelity": "manual_validation_required",
                "outcome_quality": "manual_validation_required",
                "test_coverage": "manual_validation_required",
                "wsp_50_approval": "manual_validation_required"
            },
            "note": "Prototype → Staged requires manual 0102 sign-off. Use approval checklist."
        }

    def _check_staged_to_production(self, skill_name: str) -> Dict[str, Any]:
        """Check staged → production promotion criteria"""
        if not self.conn:
            return {"ready": False, "error": "Metrics database not available"}

        cursor = self.conn.cursor()

        # Check execution count
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM execution_metrics
            WHERE skill_id = ?
        """, (skill_name,))
        execution_count = cursor.fetchone()["count"]

        if execution_count < 100:
            return {
                "ready": False,
                "reason": f"Insufficient executions: {execution_count}/100 required",
                "execution_count": execution_count
            }

        # Check sustained pattern fidelity
        cursor.execute("""
            SELECT AVG(pattern_fidelity) as avg_fidelity,
                   MIN(pattern_fidelity) as min_fidelity,
                   COUNT(*) as sample_size
            FROM execution_metrics
            WHERE skill_id = ?
              AND pattern_fidelity IS NOT NULL
              AND timestamp > ?
        """, (skill_name, (datetime.now() - timedelta(days=7)).timestamp()))

        fidelity_row = cursor.fetchone()
        avg_fidelity = fidelity_row["avg_fidelity"] or 0
        min_fidelity = fidelity_row["min_fidelity"] or 0

        if avg_fidelity < 0.90:
            return {
                "ready": False,
                "reason": f"Pattern fidelity below threshold: {avg_fidelity:.2f} < 0.90",
                "avg_fidelity": avg_fidelity,
                "min_fidelity": min_fidelity
            }

        # Check outcome quality
        cursor.execute("""
            SELECT AVG(CAST(correct AS REAL)) as avg_correct,
                   COUNT(*) as sample_size
            FROM execution_metrics
            WHERE skill_id = ?
              AND correct IS NOT NULL
              AND timestamp > ?
        """, (skill_name, (datetime.now() - timedelta(days=7)).timestamp()))

        outcome_row = cursor.fetchone()
        avg_correct = outcome_row["avg_correct"] or 0

        if avg_correct < 0.85:
            return {
                "ready": False,
                "reason": f"Outcome quality below threshold: {avg_correct:.2f} < 0.85",
                "avg_correct": avg_correct
            }

        # Check for recent critical failures
        cursor.execute("""
            SELECT COUNT(*) as exception_count
            FROM execution_metrics
            WHERE skill_id = ?
              AND exception = 1
              AND timestamp > ?
        """, (skill_name, (datetime.now() - timedelta(days=7)).timestamp()))

        exception_count = cursor.fetchone()["exception_count"]

        if exception_count > 0:
            return {
                "ready": False,
                "reason": f"Critical failures detected: {exception_count} exceptions in last 7 days",
                "exception_count": exception_count
            }

        # All automated checks passed
        return {
            "ready": True,
            "checks": {
                "execution_count": execution_count,
                "avg_pattern_fidelity": round(avg_fidelity, 3),
                "min_pattern_fidelity": round(min_fidelity, 3),
                "avg_outcome_quality": round(avg_correct, 3),
                "exception_count": exception_count
            },
            "note": "Automated checks passed. Manual 0102 approval still required."
        }

    def get_skill_metrics(
        self,
        skill_name: str,
        timeframe: str = "last_7_days"
    ) -> Dict[str, Any]:
        """
        Get aggregated metrics for a skill

        Args:
            skill_name: Name of skill
            timeframe: Timeframe for metrics (last_7_days, last_30_days, all_time)

        Returns:
            Dict with aggregated metrics
        """
        if not self.conn:
            return {"error": "Metrics database not available"}

        # Parse timeframe
        if timeframe == "last_7_days":
            since_timestamp = (datetime.now() - timedelta(days=7)).timestamp()
        elif timeframe == "last_30_days":
            since_timestamp = (datetime.now() - timedelta(days=30)).timestamp()
        else:  # all_time
            since_timestamp = 0

        cursor = self.conn.cursor()

        # Pattern fidelity stats
        cursor.execute("""
            SELECT AVG(pattern_fidelity) as avg_fidelity,
                   MIN(pattern_fidelity) as min_fidelity,
                   MAX(pattern_fidelity) as max_fidelity,
                   COUNT(*) as sample_size
            FROM execution_metrics
            WHERE skill_id = ?
              AND pattern_fidelity IS NOT NULL
              AND timestamp > ?
        """, (skill_name, since_timestamp))
        fidelity_row = cursor.fetchone()

        # Outcome quality stats
        cursor.execute("""
            SELECT AVG(CAST(correct AS REAL)) as avg_correct,
                   COUNT(*) as sample_size
            FROM execution_metrics
            WHERE skill_id = ?
              AND correct IS NOT NULL
              AND timestamp > ?
        """, (skill_name, since_timestamp))
        outcome_row = cursor.fetchone()

        # Performance stats
        cursor.execute("""
            SELECT AVG(execution_time_ms) as avg_time,
                   MIN(execution_time_ms) as min_time,
                   MAX(execution_time_ms) as max_time
            FROM execution_metrics
            WHERE skill_id = ?
              AND execution_time_ms IS NOT NULL
              AND timestamp > ?
        """, (skill_name, since_timestamp))
        perf_row = cursor.fetchone()

        # Exception count
        cursor.execute("""
            SELECT COUNT(*) as exception_count
            FROM execution_metrics
            WHERE skill_id = ?
              AND exception = 1
              AND timestamp > ?
        """, (skill_name, since_timestamp))
        exception_count = cursor.fetchone()["exception_count"]

        return {
            "skill_name": skill_name,
            "timeframe": timeframe,
            "pattern_fidelity": {
                "avg": round(fidelity_row["avg_fidelity"] or 0, 3),
                "min": round(fidelity_row["min_fidelity"] or 0, 3),
                "max": round(fidelity_row["max_fidelity"] or 0, 3),
                "sample_size": fidelity_row["sample_size"]
            },
            "outcome_quality": {
                "avg_correct": round(outcome_row["avg_correct"] or 0, 3),
                "sample_size": outcome_row["sample_size"]
            },
            "performance": {
                "avg_time_ms": round(perf_row["avg_time"] or 0, 1),
                "min_time_ms": perf_row["min_time"],
                "max_time_ms": perf_row["max_time"]
            },
            "exceptions": exception_count
        }

    def compare_skill_versions(
        self,
        skill_name: str,
        version_a: str,
        version_b: str
    ) -> Dict[str, Any]:
        """
        Compare two skill versions (e.g., prototype vs staged)

        Args:
            skill_name: Name of skill
            version_a: First version state
            version_b: Second version state

        Returns:
            Dict with comparison results
        """
        # This is a simplified comparison
        # In practice, would need version tracking in metrics
        return {
            "skill_name": skill_name,
            "comparison": f"{version_a} vs {version_b}",
            "note": "Version comparison requires version tagging in metrics (future enhancement)"
        }

    def check_rollback_triggers(self, skill_name: str) -> Dict[str, Any]:
        """
        Check if skill should be rolled back

        Args:
            skill_name: Name of skill

        Returns:
            Dict with rollback recommendation
        """
        if not self.conn:
            return {"should_rollback": False, "error": "Metrics database not available"}

        cursor = self.conn.cursor()

        # Check recent pattern fidelity (last 10 executions)
        cursor.execute("""
            SELECT AVG(pattern_fidelity) as avg_fidelity,
                   COUNT(*) as sample_size
            FROM (
                SELECT pattern_fidelity
                FROM execution_metrics
                WHERE skill_id = ?
                  AND pattern_fidelity IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT 10
            )
        """, (skill_name,))
        recent_fidelity = cursor.fetchone()

        if recent_fidelity["sample_size"] >= 10 and recent_fidelity["avg_fidelity"] < 0.85:
            return {
                "should_rollback": True,
                "trigger": "pattern_fidelity_drop",
                "recent_fidelity": round(recent_fidelity["avg_fidelity"], 3),
                "threshold": 0.85
            }

        # Check recent exception rate
        cursor.execute("""
            SELECT AVG(CAST(exception AS REAL)) as exception_rate
            FROM (
                SELECT exception
                FROM execution_metrics
                WHERE skill_id = ?
                ORDER BY timestamp DESC
                LIMIT 20
            )
        """, (skill_name,))
        exception_rate = cursor.fetchone()["exception_rate"] or 0

        if exception_rate > 0.05:
            return {
                "should_rollback": True,
                "trigger": "high_exception_rate",
                "exception_rate": round(exception_rate, 3),
                "threshold": 0.05
            }

        return {
            "should_rollback": False,
            "recent_fidelity": round(recent_fidelity["avg_fidelity"] or 0, 3),
            "exception_rate": round(exception_rate, 3)
        }

    def load_registry_json(self) -> Dict[str, Any]:
        """Load skills_registry.json"""
        if not self.registry_json.exists():
            return {"version": "1.0", "skills": {}}

        with open(self.registry_json, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_registry_json(self, registry: Dict[str, Any]) -> None:
        """Save skills_registry.json"""
        with open(self.registry_json, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)

    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    registry = WRESkillsRegistry()

    # Example: Check promotion readiness
    readiness = registry.check_promotion_readiness(
        skill_name="youtube_spam_detection",
        from_state="staged",
        to_state="production"
    )
    print(f"[PROMOTION-CHECK] Ready: {readiness['ready']}")
    if readiness["ready"]:
        print(f"  Checks: {readiness['checks']}")
    else:
        print(f"  Reason: {readiness.get('reason', 'N/A')}")

    # Example: Get skill metrics
    metrics = registry.get_skill_metrics("youtube_spam_detection", timeframe="last_7_days")
    print(f"\n[METRICS] Skill: {metrics['skill_name']}")
    print(f"  Pattern Fidelity: avg={metrics['pattern_fidelity']['avg']} (n={metrics['pattern_fidelity']['sample_size']})")
    print(f"  Outcome Quality: avg={metrics['outcome_quality']['avg_correct']} (n={metrics['outcome_quality']['sample_size']})")
    print(f"  Performance: avg={metrics['performance']['avg_time_ms']}ms")
    print(f"  Exceptions: {metrics['exceptions']}")

    # Example: Check rollback triggers
    rollback = registry.check_rollback_triggers("youtube_spam_detection")
    print(f"\n[ROLLBACK-CHECK] Should rollback: {rollback['should_rollback']}")
    if rollback["should_rollback"]:
        print(f"  Trigger: {rollback['trigger']}")

    registry.close()
