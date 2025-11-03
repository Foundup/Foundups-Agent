#!/usr/bin/env python3
"""
WRE Skills Registry v2
FIXED: Integrity checks for separate metric tables + human approval tracking
WSP Compliance: WSP 77 (Agent Coordination), WSP 91 (DAEMON Observability), WSP 50 (Pre-Action)
"""

import sqlite3
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class WRESkillsRegistryV2:
    """
    Skills registry with query helpers for metrics and promotion gating (v2 - FIXED)

    CRITICAL FIXES:
    - Metric type coverage checks (all three tables must have ≥100 samples)
    - 0102 (AI supervisor) approval tracking (WSP 50 compliance)
    - Auto-update last_updated timestamp
    - Holo re-index automation + ModLog updates
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

        self.repo_root = Path(__file__).parent.parent.parent.parent

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
        """
        Check prototype → staged promotion criteria

        FIXED: Requires 0102 (AI supervisor) approval record in database
        """
        if not self.conn:
            return {"ready": False, "error": "Metrics database not available"}

        cursor = self.conn.cursor()

        # Check for 0102 approval record (WSP 50)
        cursor.execute("""
            SELECT * FROM ai_0102_approvals
            WHERE skill_id = ? AND promotion_path = 'prototype->staged'
            ORDER BY approval_timestamp DESC LIMIT 1
        """, (skill_name,))

        approval = cursor.fetchone()
        if not approval:
            return {
                "ready": False,
                "reason": "No 0102 (AI supervisor) approval record found - WSP 50 checklist required",
                "required_action": "Create approval record via promoter.py --create-approval"
            }

        # Verify all required checks passed
        failed_checks = []

        if not approval["wsp_50_no_duplication"]:
            failed_checks.append("WSP 50: Duplication check failed")

        if not approval["test_coverage_complete"]:
            failed_checks.append("Test coverage: Incomplete")

        if not approval["instruction_clarity_approved"]:
            failed_checks.append("Instruction clarity: Not approved")

        if not approval["dependencies_validated"]:
            failed_checks.append("Dependencies: Not validated")

        if not approval["security_reviewed"]:
            failed_checks.append("Security: Not reviewed")

        if failed_checks:
            return {
                "ready": False,
                "reason": "Human approval checks failed",
                "failed_checks": failed_checks,
                "approval_id": approval["approval_id"]
            }

        # All checks passed
        return {
            "ready": True,
            "approval_id": approval["approval_id"],
            "approver": approval["approver"],
            "approval_ticket": approval["approval_ticket"],
            "approval_timestamp": approval["approval_timestamp"],
            "note": "All WSP 50 checks passed. Safe to promote to staged."
        }

    def _check_staged_to_production(self, skill_name: str) -> Dict[str, Any]:
        """
        Check staged → production promotion criteria

        FIXED: Checks ALL THREE metric tables for coverage
        """
        if not self.conn:
            return {"ready": False, "error": "Metrics database not available"}

        cursor = self.conn.cursor()

        # CRITICAL FIX: Check metric type coverage (all three tables)
        cursor.execute("""
            SELECT
                (SELECT COUNT(*) FROM fidelity_metrics WHERE skill_id = ?) as fidelity_count,
                (SELECT COUNT(*) FROM outcome_metrics WHERE skill_id = ?) as outcome_count,
                (SELECT COUNT(*) FROM performance_metrics WHERE skill_id = ?) as perf_count
        """, (skill_name, skill_name, skill_name))

        counts = cursor.fetchone()

        # All three must have ≥100 samples
        if counts["fidelity_count"] < 100:
            return {
                "ready": False,
                "reason": f"Insufficient fidelity metrics: {counts['fidelity_count']}/100 required",
                "metric_coverage": {
                    "fidelity": counts["fidelity_count"],
                    "outcome": counts["outcome_count"],
                    "performance": counts["perf_count"]
                }
            }

        if counts["outcome_count"] < 100:
            return {
                "ready": False,
                "reason": f"Insufficient outcome metrics: {counts['outcome_count']}/100 required",
                "metric_coverage": {
                    "fidelity": counts["fidelity_count"],
                    "outcome": counts["outcome_count"],
                    "performance": counts["perf_count"]
                }
            }

        if counts["perf_count"] < 100:
            return {
                "ready": False,
                "reason": f"Insufficient performance metrics: {counts['perf_count']}/100 required",
                "metric_coverage": {
                    "fidelity": counts["fidelity_count"],
                    "outcome": counts["outcome_count"],
                    "performance": counts["perf_count"]
                }
            }

        # Check sustained pattern fidelity
        cursor.execute("""
            SELECT AVG(pattern_fidelity) as avg_fidelity,
                   MIN(pattern_fidelity) as min_fidelity,
                   COUNT(*) as sample_size
            FROM fidelity_metrics
            WHERE skill_id = ?
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
            FROM outcome_metrics
            WHERE skill_id = ?
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
            FROM performance_metrics
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

        # Check 0102 (AI supervisor) approval for staged->production
        cursor.execute("""
            SELECT * FROM ai_0102_approvals
            WHERE skill_id = ? AND promotion_path = 'staged->production'
            ORDER BY approval_timestamp DESC LIMIT 1
        """, (skill_name,))

        approval = cursor.fetchone()
        if not approval:
            return {
                "ready": False,
                "reason": "No 0102 (AI supervisor) approval record for staged->production",
                "required_action": "Create approval record with production-specific checks"
            }

        # Verify production-specific checks
        failed_checks = []
        if not approval.get("production_readiness"):
            failed_checks.append("Production readiness: Not confirmed")
        if not approval.get("integration_approved"):
            failed_checks.append("Integration: Not approved")
        if not approval.get("monitoring_configured"):
            failed_checks.append("Monitoring: Not configured")
        if not approval.get("rollback_tested"):
            failed_checks.append("Rollback plan: Not tested")
        if not approval.get("documentation_updated"):
            failed_checks.append("Documentation: Not updated")

        if failed_checks:
            return {
                "ready": False,
                "reason": "Production approval checks failed",
                "failed_checks": failed_checks
            }

        # All automated checks passed
        return {
            "ready": True,
            "checks": {
                "metric_coverage": {
                    "fidelity": counts["fidelity_count"],
                    "outcome": counts["outcome_count"],
                    "performance": counts["perf_count"]
                },
                "avg_pattern_fidelity": round(avg_fidelity, 3),
                "min_pattern_fidelity": round(min_fidelity, 3),
                "avg_outcome_quality": round(avg_correct, 3),
                "exception_count": exception_count
            },
            "approval_id": approval["approval_id"],
            "approver": approval["approver"],
            "note": "All checks passed. Safe to promote to production."
        }

    def get_skill_metrics(
        self,
        skill_name: str,
        timeframe: str = "last_7_days"
    ) -> Dict[str, Any]:
        """
        Get aggregated metrics for a skill

        FIXED: Queries separate tables for each metric type

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

        # Pattern fidelity stats (from fidelity_metrics table)
        cursor.execute("""
            SELECT AVG(pattern_fidelity) as avg_fidelity,
                   MIN(pattern_fidelity) as min_fidelity,
                   MAX(pattern_fidelity) as max_fidelity,
                   COUNT(*) as sample_size
            FROM fidelity_metrics
            WHERE skill_id = ?
              AND timestamp > ?
        """, (skill_name, since_timestamp))
        fidelity_row = cursor.fetchone()

        # Outcome quality stats (from outcome_metrics table)
        cursor.execute("""
            SELECT AVG(CAST(correct AS REAL)) as avg_correct,
                   COUNT(*) as sample_size
            FROM outcome_metrics
            WHERE skill_id = ?
              AND timestamp > ?
        """, (skill_name, since_timestamp))
        outcome_row = cursor.fetchone()

        # Performance stats (from performance_metrics table)
        cursor.execute("""
            SELECT AVG(execution_time_ms) as avg_time,
                   MIN(execution_time_ms) as min_time,
                   MAX(execution_time_ms) as max_time,
                   COUNT(*) as sample_size
            FROM performance_metrics
            WHERE skill_id = ?
              AND timestamp > ?
        """, (skill_name, since_timestamp))
        perf_row = cursor.fetchone()

        # Exception count (from performance_metrics table)
        cursor.execute("""
            SELECT COUNT(*) as exception_count
            FROM performance_metrics
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
                "max_time_ms": perf_row["max_time"],
                "sample_size": perf_row["sample_size"]
            },
            "exceptions": exception_count
        }

    def trigger_holo_reindex(self, reason: str, changed_skills: List[str]) -> None:
        """
        Trigger HoloIndex re-index and update ModLog (NEW - Automation)

        Args:
            reason: Why re-index needed (promotion/rollback)
            changed_skills: List of skills that changed state
        """
        # Run HoloIndex re-index
        try:
            result = subprocess.run(
                ["python", str(self.repo_root / "holo_index.py"), "--reindex-skills"],
                capture_output=True,
                text=True,
                cwd=str(self.repo_root),
                timeout=120
            )

            if result.returncode != 0:
                logger.error(f"[HOLO-REINDEX] Failed: {result.stderr}")
                raise RuntimeError(f"HoloIndex re-index failed: {result.stderr}")

            logger.info(f"[HOLO-REINDEX] Success: {result.stdout[:200]}...")

        except subprocess.TimeoutExpired:
            logger.error("[HOLO-REINDEX] Timeout after 120s")
            raise RuntimeError("HoloIndex re-index timed out")

        # Update ModLog (WSP 22)
        modlog_path = self.repo_root / "modules/infrastructure/wre_core/ModLog.md"
        modlog_entry = f"""
## {datetime.now().strftime("%Y-%m-%d %H:%M")} - Skills {reason}

**Skills Changed**: {', '.join(changed_skills)}
**Action**: HoloIndex re-indexed to reflect skill state changes
**Reason**: {reason}
**Automation**: `WRESkillsRegistryV2.trigger_holo_reindex()`

"""

        try:
            with open(modlog_path, 'a', encoding='utf-8') as f:
                f.write(modlog_entry)
            logger.info(f"[MODLOG] Updated: {modlog_path}")
        except Exception as e:
            logger.warning(f"[MODLOG] Failed to update: {e}")

        logger.info(f"[HOLO-REINDEX] Complete for {len(changed_skills)} skills")

    def check_rollback_triggers(self, skill_name: str) -> Dict[str, Any]:
        """
        Check if skill should be rolled back

        FIXED: Queries separate tables

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
                FROM fidelity_metrics
                WHERE skill_id = ?
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
                "threshold": 0.85,
                "sample_size": recent_fidelity["sample_size"]
            }

        # Check recent exception rate
        cursor.execute("""
            SELECT AVG(CAST(exception AS REAL)) as exception_rate
            FROM (
                SELECT exception
                FROM performance_metrics
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
        """
        Save skills_registry.json

        FIXED: Auto-updates last_updated timestamp
        """
        # Update timestamp automatically
        registry["last_updated"] = datetime.utcnow().isoformat() + "Z"

        with open(self.registry_json, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)

        logger.info(f"[REGISTRY] Updated: {registry['last_updated']}")

    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()
