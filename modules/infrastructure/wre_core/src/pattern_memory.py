#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pattern Memory - SQLite Outcome Storage for Recursive Learning

Per WSP 60 (Module Memory Architecture), WSP 48 (Recursive Self-Improvement)

Stores skill execution outcomes for recursive evolution:
- Skill executed with what parameters?
- What was the outcome (success/failure)?
- What was the pattern fidelity?
- What did we learn?

This enables skills to evolve via A/B testing and converge to >90% fidelity

WSP Compliance:
- WSP 60: Module Memory Architecture (pattern recall)
- WSP 48: Recursive Self-Improvement (learning loop)
- WSP 91: DAEMON Observability (breadcrumb tracking)
- WSP 96: WRE Skills Wardrobe (trainable weights)
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class SkillOutcome:
    """
    Record of skill execution outcome for learning

    Per WSP 96: Skills are trainable weights that evolve
    """
    execution_id: str
    skill_name: str
    agent: str  # qwen, gemma, grok, ui-tars
    timestamp: str  # ISO format
    input_context: str  # JSON string
    output_result: str  # JSON string
    success: bool
    pattern_fidelity: float  # 0.0-1.0 from Gemma validation
    outcome_quality: float  # 0.0-1.0 correctness score
    execution_time_ms: int
    step_count: int  # Number of steps in micro chain-of-thought
    failed_at_step: Optional[int] = None  # Which step failed (if any)
    notes: Optional[str] = None


class PatternMemory:
    """
    Pattern Memory - SQLite storage for skill outcomes and recursive learning

    Per WSP 60: Enable recall instead of computation
    Per WSP 48: Store outcomes for self-improvement

    Database Schema:
    - skill_outcomes: Execution records
    - skill_variations: A/B test variations
    - learning_events: Pattern improvement events

    This enables:
    1. Recall successful patterns (50-200 tokens)
    2. A/B test variations (Qwen generates, Gemma validates)
    3. Converge to >90% fidelity over 4 weeks
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize pattern memory database

        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            self.db_path = Path(__file__).parent.parent / "data" / "pattern_memory.db"
        else:
            self.db_path = Path(db_path)

        # Ensure data directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Access columns by name

        self._initialize_schema()

        logger.info(f"[PATTERN-MEMORY] Initialized - db={self.db_path}")

    def _initialize_schema(self) -> None:
        """
        Create database schema if not exists

        Per WSP 60: Structured memory for pattern recall
        """
        cursor = self.conn.cursor()

        # Skill outcomes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_outcomes (
                execution_id TEXT PRIMARY KEY,
                skill_name TEXT NOT NULL,
                agent TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                input_context TEXT NOT NULL,
                output_result TEXT NOT NULL,
                success INTEGER NOT NULL,
                pattern_fidelity REAL NOT NULL,
                outcome_quality REAL NOT NULL,
                execution_time_ms INTEGER NOT NULL,
                step_count INTEGER NOT NULL,
                failed_at_step INTEGER,
                notes TEXT
            )
        """)

        # Index for fast lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_skill_outcomes_skill_name
            ON skill_outcomes(skill_name)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_skill_outcomes_timestamp
            ON skill_outcomes(timestamp DESC)
        """)

        # Skill variations table (for A/B testing)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_variations (
                variation_id TEXT PRIMARY KEY,
                skill_name TEXT NOT NULL,
                parent_version TEXT,
                variation_content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                created_by TEXT NOT NULL,
                test_status TEXT DEFAULT 'testing',
                avg_fidelity REAL,
                execution_count INTEGER DEFAULT 0,
                promoted BOOLEAN DEFAULT 0
            )
        """)

        # Learning events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_events (
                event_id TEXT PRIMARY KEY,
                skill_name TEXT NOT NULL,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                description TEXT,
                before_fidelity REAL,
                after_fidelity REAL,
                variation_id TEXT
            )
        """)

        self.conn.commit()
        logger.debug("[PATTERN-MEMORY] Schema initialized")

    def store_outcome(self, outcome: SkillOutcome) -> None:
        """
        Store skill execution outcome

        Per WSP 48: Record outcomes for learning

        Args:
            outcome: Skill execution outcome
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO skill_outcomes (
                execution_id, skill_name, agent, timestamp,
                input_context, output_result, success,
                pattern_fidelity, outcome_quality, execution_time_ms,
                step_count, failed_at_step, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            outcome.execution_id,
            outcome.skill_name,
            outcome.agent,
            outcome.timestamp,
            outcome.input_context,
            outcome.output_result,
            1 if outcome.success else 0,
            outcome.pattern_fidelity,
            outcome.outcome_quality,
            outcome.execution_time_ms,
            outcome.step_count,
            outcome.failed_at_step,
            outcome.notes
        ))

        self.conn.commit()

        logger.info(f"[PATTERN-MEMORY] Stored outcome - skill={outcome.skill_name}, "
                   f"exec_id={outcome.execution_id}, fidelity={outcome.pattern_fidelity:.2f}")

    def recall_successful_patterns(
        self,
        skill_name: str,
        min_fidelity: float = 0.90,
        limit: int = 10
    ) -> List[Dict]:
        """
        Recall successful execution patterns for a skill

        Per WSP 60: Recall instead of compute (50-200 tokens vs 5000+)

        This enables Qwen to learn from past successful executions:
        - What input context led to high fidelity?
        - What output patterns worked well?
        - What step sequences succeeded?

        Args:
            skill_name: Skill to recall patterns for
            min_fidelity: Minimum pattern fidelity threshold
            limit: Max number of patterns to recall

        Returns:
            List of successful execution records
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT * FROM skill_outcomes
            WHERE skill_name = ?
              AND success = 1
              AND pattern_fidelity >= ?
            ORDER BY pattern_fidelity DESC, timestamp DESC
            LIMIT ?
        """, (skill_name, min_fidelity, limit))

        rows = cursor.fetchall()

        patterns = [dict(row) for row in rows]

        logger.info(f"[PATTERN-MEMORY] Recalled {len(patterns)} successful patterns - "
                   f"skill={skill_name}, min_fidelity={min_fidelity}")

        return patterns

    def recall_failure_patterns(
        self,
        skill_name: str,
        max_fidelity: float = 0.70,
        limit: int = 10
    ) -> List[Dict]:
        """
        Recall failed execution patterns for learning

        Per WSP 48: Learn from failures to improve

        This enables Qwen to generate better variations:
        - Which steps failed most often?
        - What input contexts cause failures?
        - What validation patterns need strengthening?

        Args:
            skill_name: Skill to recall failures for
            max_fidelity: Maximum pattern fidelity (failures)
            limit: Max number of patterns to recall

        Returns:
            List of failed execution records
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT * FROM skill_outcomes
            WHERE skill_name = ?
              AND pattern_fidelity <= ?
            ORDER BY pattern_fidelity ASC, timestamp DESC
            LIMIT ?
        """, (skill_name, max_fidelity, limit))

        rows = cursor.fetchall()

        patterns = [dict(row) for row in rows]

        logger.info(f"[PATTERN-MEMORY] Recalled {len(patterns)} failure patterns - "
                   f"skill={skill_name}, max_fidelity={max_fidelity}")

        return patterns

    def get_skill_metrics(self, skill_name: str, days: int = 7) -> Dict:
        """
        Get aggregated metrics for a skill over time period

        Per WSP 91: Observability for monitoring

        Returns:
            Dict with avg fidelity, success rate, execution count
        """
        cursor = self.conn.cursor()

        # Calculate metrics from last N days
        cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute("""
            SELECT
                COUNT(*) as execution_count,
                AVG(pattern_fidelity) as avg_fidelity,
                AVG(outcome_quality) as avg_quality,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as success_rate,
                AVG(execution_time_ms) as avg_time_ms,
                AVG(step_count) as avg_steps
            FROM skill_outcomes
            WHERE skill_name = ? AND timestamp >= ?
        """, (skill_name, cutoff_time))

        row = cursor.fetchone()

        if row["execution_count"] == 0:
            return {
                "skill_name": skill_name,
                "execution_count": 0,
                "avg_fidelity": 0.0,
                "avg_quality": 0.0,
                "success_rate": 0.0,
                "avg_time_ms": 0,
                "avg_steps": 0,
                "period_days": days
            }

        return {
            "skill_name": skill_name,
            "execution_count": row["execution_count"],
            "avg_fidelity": round(row["avg_fidelity"], 3),
            "avg_quality": round(row["avg_quality"], 3),
            "success_rate": round(row["success_rate"], 3),
            "avg_time_ms": int(row["avg_time_ms"]),
            "avg_steps": round(row["avg_steps"], 1),
            "period_days": days
        }

    def store_variation(
        self,
        variation_id: str,
        skill_name: str,
        variation_content: str,
        parent_version: Optional[str] = None,
        created_by: str = "qwen"
    ) -> None:
        """
        Store skill variation for A/B testing

        Per WSP 48: Recursive self-improvement through variation testing

        Args:
            variation_id: Unique variation identifier
            skill_name: Base skill name
            variation_content: Full SKILL.md content of variation
            parent_version: Version this was derived from
            created_by: Agent that created variation (qwen, 0102)
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO skill_variations (
                variation_id, skill_name, parent_version,
                variation_content, created_at, created_by
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            variation_id,
            skill_name,
            parent_version,
            variation_content,
            datetime.now().isoformat(),
            created_by
        ))

        self.conn.commit()

        logger.info(f"[PATTERN-MEMORY] Stored variation - skill={skill_name}, "
                   f"var_id={variation_id}, created_by={created_by}")

    def record_learning_event(
        self,
        event_id: str,
        skill_name: str,
        event_type: str,
        description: str,
        before_fidelity: Optional[float] = None,
        after_fidelity: Optional[float] = None,
        variation_id: Optional[str] = None
    ) -> None:
        """
        Record learning event for skill evolution tracking

        Per WSP 48: Track self-improvement progress

        Event types: variation_created, variation_promoted, threshold_tuned, rollback

        Args:
            event_id: Unique event identifier
            skill_name: Skill that evolved
            event_type: Type of learning event
            description: Human-readable description
            before_fidelity: Fidelity before change
            after_fidelity: Fidelity after change
            variation_id: Related variation (if applicable)
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO learning_events (
                event_id, skill_name, event_type, timestamp,
                description, before_fidelity, after_fidelity, variation_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            skill_name,
            event_type,
            datetime.now().isoformat(),
            description,
            before_fidelity,
            after_fidelity,
            variation_id
        ))

        self.conn.commit()

        logger.info(f"[PATTERN-MEMORY] Learning event - skill={skill_name}, "
                   f"type={event_type}, event_id={event_id}")

    def get_evolution_history(self, skill_name: str) -> List[Dict]:
        """
        Get evolution history for a skill

        Per WSP 48: Track recursive improvement over time

        Returns:
            List of learning events in chronological order
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT * FROM learning_events
            WHERE skill_name = ?
            ORDER BY timestamp ASC
        """, (skill_name,))

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def close(self) -> None:
        """Close database connection"""
        self.conn.close()
        logger.debug("[PATTERN-MEMORY] Connection closed")


# Example usage
if __name__ == "__main__":
    from datetime import timedelta
    import uuid

    logging.basicConfig(level=logging.INFO)

    # Initialize pattern memory
    memory = PatternMemory()

    print("[EXAMPLE 1] Store skill execution outcome:")
    outcome = SkillOutcome(
        execution_id=str(uuid.uuid4()),
        skill_name="qwen_gitpush",
        agent="qwen",
        timestamp=datetime.now().isoformat(),
        input_context=json.dumps({"files_changed": 14, "lines_added": 250}),
        output_result=json.dumps({"action": "push_now", "mps_score": 14}),
        success=True,
        pattern_fidelity=0.92,
        outcome_quality=0.95,
        execution_time_ms=1200,
        step_count=4,
        notes="Successful git push with P1 priority"
    )
    memory.store_outcome(outcome)
    print(f"  Stored: exec_id={outcome.execution_id[:8]}...")

    print("\n[EXAMPLE 2] Recall successful patterns:")
    patterns = memory.recall_successful_patterns("qwen_gitpush", min_fidelity=0.90, limit=5)
    print(f"  Recalled {len(patterns)} successful patterns")
    if patterns:
        print(f"  Best fidelity: {patterns[0]['pattern_fidelity']:.2f}")

    print("\n[EXAMPLE 3] Get skill metrics:")
    metrics = memory.get_skill_metrics("qwen_gitpush", days=7)
    print(f"  Executions: {metrics['execution_count']}")
    print(f"  Avg fidelity: {metrics['avg_fidelity']:.2f}")
    print(f"  Success rate: {metrics['success_rate']:.1%}")

    print("\n[EXAMPLE 4] Store variation for A/B testing:")
    memory.store_variation(
        variation_id="qwen_gitpush_v1.1_improved",
        skill_name="qwen_gitpush",
        variation_content="# Improved version with better MPS calculation",
        parent_version="v1.0_baseline",
        created_by="qwen"
    )
    print("  Variation stored for A/B testing")

    print("\n[EXAMPLE 5] Record learning event:")
    memory.record_learning_event(
        event_id=str(uuid.uuid4()),
        skill_name="qwen_gitpush",
        event_type="variation_promoted",
        description="Promoted v1.1 after 65% → 78% fidelity improvement",
        before_fidelity=0.65,
        after_fidelity=0.78,
        variation_id="qwen_gitpush_v1.1_improved"
    )
    print("  Learning event recorded")

    memory.close()

    print("\n[OK] Pattern Memory ready - recursive learning enabled")
