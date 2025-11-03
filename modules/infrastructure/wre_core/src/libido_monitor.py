#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemma Libido Monitor - Pattern Frequency Sensor

IBM Typewriter Analogy: "Paper feed sensor" that monitors pattern activation frequency
Per WSP 96 (v1.3 - Micro Chain-of-Thought), WSP 77 (Agent Coordination)

Libido = "Pattern activation frequency" (not the Freudian sense!)
Monitors Qwen thought patterns like paper feed sensor monitors typing frequency

Gemma (270M params) = Fast binary decisions (<10ms)
Signals: CONTINUE (OK), THROTTLE (too much), ESCALATE (too little)

WSP Compliance:
- WSP 96: WRE Skills Wardrobe Protocol
- WSP 77: Agent Coordination (Gemma validation)
- WSP 60: Module Memory Architecture (pattern recall)
- WSP 91: DAEMON Observability (structured logging)
"""

from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class LibidoSignal(Enum):
    """
    Libido signals for pattern activation control
    Per WSP 96: Gemma acts as pattern frequency sensor
    """
    CONTINUE = "continue"      # Frequency OK, proceed with execution
    THROTTLE = "throttle"      # Hit max frequency, skip execution
    ESCALATE = "escalate"      # Below min frequency, force execution


@dataclass
class PatternExecution:
    """
    Record of skill pattern execution
    Per WSP 91: Structured logging for observability
    """
    skill_name: str
    agent: str                  # qwen, gemma, grok, ui-tars
    timestamp: datetime
    execution_id: str
    fidelity_score: Optional[float] = None  # Gemma's validation score


class GemmaLibidoMonitor:
    """
    Gemma Libido Monitor - Pattern Frequency Sensor

    IBM Typewriter Analogy:
    - Typewriter ball = Skills (interchangeable patterns)
    - Mechanical wiring = WRE Core (triggers correct skill)
    - Paper feed sensor = THIS CLASS (monitors pattern frequency)
    - Operator = HoloDAE + 0102 (when to type what)

    Gemma (270M) monitors Qwen's pattern activation frequency:
    - Too frequent → THROTTLE (prevent waste)
    - Too infrequent → ESCALATE (ensure coverage)
    - Just right → CONTINUE (optimal flow)

    Performance:
    - Binary classification: <10ms per check
    - Pattern matching: No complex reasoning
    - Memory efficient: deque(maxlen=100)

    Per WSP 96 v1.3: Micro Chain-of-Thought paradigm
    """

    def __init__(
        self,
        history_size: int = 100,
        default_min_frequency: int = 1,
        default_max_frequency: int = 5,
        default_cooldown_seconds: int = 600  # 10 minutes
    ):
        """
        Initialize Gemma Libido Monitor

        Args:
            history_size: Number of recent executions to track
            default_min_frequency: Default minimum executions per session
            default_max_frequency: Default maximum executions per session
            default_cooldown_seconds: Default cooldown between executions
        """
        self.pattern_history: deque = deque(maxlen=history_size)

        # Per-skill thresholds (skill_name -> (min, max, cooldown_seconds))
        self.frequency_thresholds: Dict[str, Tuple[int, int, int]] = {
            "qwen_gitpush": (1, 5, 600),  # Min 1, Max 5, 10min cooldown
            "youtube_spam_detection": (10, 100, 60),  # Fast classification OK
            "wsp_compliance_checker": (2, 10, 300),  # Strategic, less frequent
        }

        self.default_thresholds = (
            default_min_frequency,
            default_max_frequency,
            default_cooldown_seconds
        )

        logger.info(f"[LIBIDO] Initialized - history_size={history_size}, "
                   f"defaults=({default_min_frequency}, {default_max_frequency}, {default_cooldown_seconds}s)")

    def should_execute(
        self,
        skill_name: str,
        execution_id: str,
        force: bool = False
    ) -> LibidoSignal:
        """
        Check if skill should execute based on pattern frequency

        This is Gemma's binary classification task:
        1. Count recent activations for this skill
        2. Check against thresholds (min, max, cooldown)
        3. Return CONTINUE, THROTTLE, or ESCALATE

        Performance: <10ms (Gemma 270M pattern matching)

        Args:
            skill_name: Name of skill to check
            execution_id: Unique execution identifier
            force: Force execution regardless of libido (0102 override)

        Returns:
            LibidoSignal indicating whether to execute

        Per WSP 96: Gemma validates pattern frequency, not complex logic
        """
        if force:
            logger.info(f"[LIBIDO] FORCE execution - skill={skill_name}, exec_id={execution_id}")
            return LibidoSignal.CONTINUE

        # Get thresholds for this skill
        min_freq, max_freq, cooldown_secs = self.frequency_thresholds.get(
            skill_name,
            self.default_thresholds
        )

        # Count recent executions for this skill
        now = datetime.now()
        recent_executions = [
            p for p in self.pattern_history
            if p.skill_name == skill_name
        ]
        execution_count = len(recent_executions)

        # Check cooldown (time since last execution)
        if recent_executions:
            last_execution = recent_executions[-1]
            time_since_last = (now - last_execution.timestamp).total_seconds()

            if time_since_last < cooldown_secs:
                logger.debug(f"[LIBIDO] THROTTLE - cooldown active "
                           f"(last={time_since_last:.0f}s < {cooldown_secs}s) - "
                           f"skill={skill_name}")
                return LibidoSignal.THROTTLE

        # Check max frequency (prevent over-thinking)
        if execution_count >= max_freq:
            logger.info(f"[LIBIDO] THROTTLE - max frequency reached "
                       f"({execution_count} >= {max_freq}) - skill={skill_name}")
            return LibidoSignal.THROTTLE

        # Check min frequency (ensure coverage)
        if execution_count < min_freq:
            logger.info(f"[LIBIDO] ESCALATE - below min frequency "
                       f"({execution_count} < {min_freq}) - skill={skill_name}")
            return LibidoSignal.ESCALATE

        # Frequency is within acceptable range
        logger.debug(f"[LIBIDO] CONTINUE - frequency OK ({execution_count} in [{min_freq}, {max_freq}]) - "
                    f"skill={skill_name}")
        return LibidoSignal.CONTINUE

    def record_execution(
        self,
        skill_name: str,
        agent: str,
        execution_id: str,
        fidelity_score: Optional[float] = None
    ) -> None:
        """
        Record skill execution in pattern history

        Per WSP 91: Structured logging for breadcrumb tracking

        Args:
            skill_name: Name of executed skill
            agent: Agent that executed (qwen, gemma, grok, ui-tars)
            execution_id: Unique execution identifier
            fidelity_score: Gemma's pattern fidelity validation score (0.0-1.0)
        """
        execution = PatternExecution(
            skill_name=skill_name,
            agent=agent,
            timestamp=datetime.now(),
            execution_id=execution_id,
            fidelity_score=fidelity_score
        )

        self.pattern_history.append(execution)

        logger.info(f"[LIBIDO] Recorded execution - skill={skill_name}, agent={agent}, "
                   f"exec_id={execution_id}, fidelity={fidelity_score}")

    def validate_step_fidelity(
        self,
        step_output: Dict,
        expected_patterns: List[str]
    ) -> float:
        """
        Gemma validates if Qwen followed skill instructions for a single step

        Per WSP 96 v1.3: Micro Chain-of-Thought paradigm
        Each step in skill execution is validated before proceeding

        This is Gemma's pattern matching task:
        1. Check if expected patterns present in output
        2. Calculate fidelity score (patterns_present / total_patterns)
        3. Return score for WRE decision

        Performance: <10ms per step validation

        Args:
            step_output: Qwen's output for this step (dict with keys)
            expected_patterns: List of required output keys/patterns

        Returns:
            Fidelity score (0.0-1.0)

        Example:
            step_output = {"change_type": "feature", "summary": "Add X", "confidence": 0.85}
            expected_patterns = ["change_type", "summary", "confidence"]
            Returns: 1.0 (all patterns present)
        """
        patterns_present = sum(
            1 for pattern in expected_patterns
            if pattern in step_output and step_output[pattern] is not None
        )

        fidelity = patterns_present / len(expected_patterns) if expected_patterns else 0.0

        logger.debug(f"[LIBIDO] Step validation - {patterns_present}/{len(expected_patterns)} patterns present, "
                    f"fidelity={fidelity:.2f}")

        return fidelity

    def get_skill_statistics(self, skill_name: str) -> Dict:
        """
        Get execution statistics for a skill

        Returns:
            Dict with execution count, avg fidelity, recent executions
        """
        skill_executions = [
            p for p in self.pattern_history
            if p.skill_name == skill_name
        ]

        if not skill_executions:
            return {
                "skill_name": skill_name,
                "execution_count": 0,
                "avg_fidelity": 0.0,
                "recent_executions": []
            }

        # Calculate average fidelity (only for executions with scores)
        fidelity_scores = [p.fidelity_score for p in skill_executions if p.fidelity_score is not None]
        avg_fidelity = sum(fidelity_scores) / len(fidelity_scores) if fidelity_scores else 0.0

        return {
            "skill_name": skill_name,
            "execution_count": len(skill_executions),
            "avg_fidelity": avg_fidelity,
            "last_execution": skill_executions[-1].timestamp.isoformat(),
            "recent_count_5min": len([
                p for p in skill_executions
                if (datetime.now() - p.timestamp).total_seconds() < 300
            ])
        }

    def set_thresholds(
        self,
        skill_name: str,
        min_frequency: int,
        max_frequency: int,
        cooldown_seconds: int
    ) -> None:
        """
        Set custom thresholds for a skill

        Per WSP 96: Skills can have custom libido thresholds

        Args:
            skill_name: Skill to configure
            min_frequency: Minimum executions per session
            max_frequency: Maximum executions per session
            cooldown_seconds: Minimum seconds between executions
        """
        self.frequency_thresholds[skill_name] = (min_frequency, max_frequency, cooldown_seconds)
        logger.info(f"[LIBIDO] Thresholds updated - skill={skill_name}, "
                   f"min={min_frequency}, max={max_frequency}, cooldown={cooldown_seconds}s")

    def export_history(self, output_path: Path) -> None:
        """
        Export pattern history to JSON for analysis

        Per WSP 91: Observability through structured logging
        """
        history_data = [
            {
                "skill_name": p.skill_name,
                "agent": p.agent,
                "timestamp": p.timestamp.isoformat(),
                "execution_id": p.execution_id,
                "fidelity_score": p.fidelity_score
            }
            for p in self.pattern_history
        ]

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, indent=2)

        logger.info(f"[LIBIDO] Exported {len(history_data)} executions to {output_path}")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize monitor
    monitor = GemmaLibidoMonitor()

    print("[EXAMPLE 1] Check if qwen_gitpush should execute:")
    signal = monitor.should_execute("qwen_gitpush", "exec_001")
    print(f"  Signal: {signal.value} (first execution → ESCALATE)")

    # Record execution
    monitor.record_execution("qwen_gitpush", "qwen", "exec_001", fidelity_score=0.92)

    print("\n[EXAMPLE 2] Validate Qwen step output:")
    step_output = {
        "change_type": "feature",
        "summary": "Add libido monitor",
        "critical_files": ["libido_monitor.py"],
        "confidence": 0.85
    }
    expected_patterns = ["change_type", "summary", "critical_files", "confidence"]
    fidelity = monitor.validate_step_fidelity(step_output, expected_patterns)
    print(f"  Fidelity: {fidelity:.2f} (all patterns present → 1.00)")

    print("\n[EXAMPLE 3] Get skill statistics:")
    stats = monitor.get_skill_statistics("qwen_gitpush")
    print(f"  Executions: {stats['execution_count']}")
    print(f"  Avg fidelity: {stats['avg_fidelity']:.2f}")

    print("\n[OK] Gemma Libido Monitor ready - pattern frequency sensor operational")
