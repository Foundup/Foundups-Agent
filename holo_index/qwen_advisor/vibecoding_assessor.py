#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io

"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

HoloIndex Vibecoding Assessment Module
======================================

Periodically prompts 0102 agents to perform vibecoding assessments.
Tracks patterns of code creation vs. code reuse to identify vibecoding trends.

WSP Compliance: WSP 50 (Pre-Action Verification), WSP 84 (Code Memory)
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict

@dataclass
class VibecodeMetrics:
    """Metrics for tracking vibecoding behavior"""
    new_files_created: int = 0
    existing_files_enhanced: int = 0
    duplicate_functions_created: int = 0
    holoindex_searches_performed: int = 0
    wsp_violations_detected: int = 0
    code_reuse_ratio: float = 0.0
    last_assessment: Optional[str] = None
    assessment_count: int = 0

    def calculate_vibecode_score(self) -> float:
        """
        Calculate vibecode score (0-100, lower is better)
        0 = Perfect WSP compliance
        100 = Maximum vibecoding
        """
        if self.holoindex_searches_performed == 0:
            return 100.0  # No searches = max vibecoding

        # Calculate negative factors
        new_file_penalty = min(self.new_files_created * 10, 30)
        duplicate_penalty = min(self.duplicate_functions_created * 15, 30)
        violation_penalty = min(self.wsp_violations_detected * 20, 40)

        # Calculate positive factors
        search_bonus = min(self.holoindex_searches_performed * 5, 25)
        enhance_bonus = min(self.existing_files_enhanced * 5, 25)

        score = new_file_penalty + duplicate_penalty + violation_penalty
        score -= (search_bonus + enhance_bonus)

        return max(0, min(100, score))

@dataclass
class AssessmentResult:
    """Result of a vibecoding assessment"""
    timestamp: str
    vibecode_score: float
    metrics: VibecodeMetrics
    recommendations: List[str] = field(default_factory=list)
    warning_level: str = "low"  # low, medium, high, critical

    def to_dict(self) -> Dict:
        return asdict(self)

class VibecodingAssessor:
    """
    Monitors and assesses vibecoding patterns in development
    """

    def __init__(self, assessment_interval_minutes: int = 30):
        """
        Initialize the assessor

        Args:
            assessment_interval_minutes: How often to trigger assessment (default 30 mins)
        """
        self.assessment_interval = timedelta(minutes=assessment_interval_minutes)
        self.last_assessment_time = None
        self.metrics = VibecodeMetrics()
        self.assessment_history: List[AssessmentResult] = []

        # Persistence
        self.data_dir = Path("E:/HoloIndex/vibecoding_assessment")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.data_dir / "metrics.json"
        self.history_file = self.data_dir / "assessment_history.json"

        self._load_state()

    def _load_state(self):
        """Load persisted state"""
        if self.metrics_file.exists():
            try:
                data = json.loads(self.metrics_file.read_text())
                self.metrics = VibecodeMetrics(**data)
                if self.metrics.last_assessment:
                    self.last_assessment_time = datetime.fromisoformat(
                        self.metrics.last_assessment
                    )
            except Exception as e:
                print(f"[WARN] Could not load metrics: {e}")

        if self.history_file.exists():
            try:
                history_data = json.loads(self.history_file.read_text())
                self.assessment_history = [
                    AssessmentResult(**item) for item in history_data
                ]
            except Exception as e:
                print(f"[WARN] Could not load history: {e}")

    def _save_state(self):
        """Persist current state"""
        self.metrics_file.write_text(
            json.dumps(asdict(self.metrics), indent=2)
        )

        history_data = [r.to_dict() for r in self.assessment_history[-100:]]
        self.history_file.write_text(
            json.dumps(history_data, indent=2)
        )

    def track_search(self):
        """Track a HoloIndex search performed"""
        self.metrics.holoindex_searches_performed += 1
        self._save_state()

    def track_file_creation(self, is_new: bool = True):
        """
        Track file creation/modification

        Args:
            is_new: True if new file, False if enhancing existing
        """
        if is_new:
            self.metrics.new_files_created += 1
        else:
            self.metrics.existing_files_enhanced += 1

        # Update code reuse ratio
        total = self.metrics.new_files_created + self.metrics.existing_files_enhanced
        if total > 0:
            self.metrics.code_reuse_ratio = (
                self.metrics.existing_files_enhanced / total
            )

        self._save_state()

    def track_duplicate(self):
        """Track creation of duplicate functionality"""
        self.metrics.duplicate_functions_created += 1
        self._save_state()

    def track_violation(self):
        """Track WSP violation"""
        self.metrics.wsp_violations_detected += 1
        self._save_state()

    def should_assess(self) -> bool:
        """
        Check if it's time for an assessment

        Returns:
            True if assessment should be triggered
        """
        if self.last_assessment_time is None:
            return True

        time_since_last = datetime.now() - self.last_assessment_time
        return time_since_last >= self.assessment_interval

    def perform_assessment(self) -> AssessmentResult:
        """
        Perform a vibecoding assessment

        Returns:
            Assessment result with score and recommendations
        """
        score = self.metrics.calculate_vibecode_score()

        # Determine warning level
        if score >= 80:
            warning_level = "critical"
        elif score >= 60:
            warning_level = "high"
        elif score >= 40:
            warning_level = "medium"
        else:
            warning_level = "low"

        # Generate recommendations
        recommendations = self._generate_recommendations(score)

        # Create result
        result = AssessmentResult(
            timestamp=datetime.now().isoformat(),
            vibecode_score=score,
            metrics=self.metrics,
            recommendations=recommendations,
            warning_level=warning_level
        )

        # Update state
        self.last_assessment_time = datetime.now()
        self.metrics.last_assessment = self.last_assessment_time.isoformat()
        self.metrics.assessment_count += 1
        self.assessment_history.append(result)
        self._save_state()

        return result

    def _generate_recommendations(self, score: float) -> List[str]:
        """Generate recommendations based on metrics"""
        recommendations = []

        if self.metrics.holoindex_searches_performed < 5:
            recommendations.append(
                "[ALERT] [VIOLATION] You have NOT been using HoloIndex! RUN IT NOW!"
            )
            recommendations.append(
                "   -> python holo_index.py --search 'your current task'"
            )

        if self.metrics.new_files_created > self.metrics.existing_files_enhanced:
            recommendations.append(
                "[FAIL] [STOP] STOP CREATING NEW FILES! Enhance existing modules!"
            )
            recommendations.append(
                "   -> Use --check-module BEFORE creating ANYTHING"
            )

        if self.metrics.duplicate_functions_created > 0:
            recommendations.append(
                "[U+1F534] [DUPLICATE] You created DUPLICATE functions! This is VIBECODING!"
            )
            recommendations.append(
                "   -> ALWAYS search first: python holo_index.py --search"
            )

        if self.metrics.wsp_violations_detected > 0:
            recommendations.append(
                f"[U+26A0]️ [WSP VIOLATION x{self.metrics.wsp_violations_detected}] You violated WSP {self.metrics.wsp_violations_detected} times!"
            )
            recommendations.append(
                "   -> READ WSP_MASTER_INDEX.md NOW"
            )

        if score < 30:
            recommendations.append("[OK] [GOOD] Acceptable WSP compliance - maintain this")
        elif score >= 60:
            recommendations.append(
                "[ALERT][ALERT] [CRITICAL VIBECODING] You are NOT following WSP!"
            )
            recommendations.append(
                "   -> STOP ALL CODING until you run HoloIndex"
            )

        if self.metrics.code_reuse_ratio < 0.5:
            recommendations.append(
                f"[DATA] [LOW REUSE] Only {self.metrics.code_reuse_ratio:.0%} code reuse - TARGET: >70%"
            )
            recommendations.append(
                "   -> Search for existing code BEFORE writing new"
            )

        # Add the constant reminder
        recommendations.append("")
        recommendations.append("[TARGET] GOLDEN RULE: 'follow WSP' = USE HOLOINDEX FIRST!")

        return recommendations

    def get_assessment_prompt(self) -> str:
        """
        Generate a prompt for the 0102 agent

        Returns:
            Prompt text to display to agent
        """
        if not self.should_assess():
            return ""

        result = self.perform_assessment()

        # MUCH MORE ASSERTIVE LANGUAGE
        prompt = f"""
==============================================================
[ALERT] MANDATORY WSP COMPLIANCE CHECK - STOP AND READ [ALERT]
==============================================================

Vibecode Score: {result.vibecode_score:.1f}/100 (lower is better)
Warning Level: {result.warning_level.upper()}

Current Session Metrics:
- HoloIndex Searches: {self.metrics.holoindex_searches_performed}
- New Files Created: {self.metrics.new_files_created}
- Existing Files Enhanced: {self.metrics.existing_files_enhanced}
- Duplicate Functions: {self.metrics.duplicate_functions_created}
- WSP Violations: {self.metrics.wsp_violations_detected}
- Code Reuse Ratio: {self.metrics.code_reuse_ratio:.1%}

Recommendations:
"""
        for rec in result.recommendations:
            prompt += f"  {rec}\n"

        # MORE DIRECTIVE LANGUAGE
        if result.vibecode_score > 50:
            prompt += """
[U+26A0]️ HIGH VIBECODING DETECTED - IMMEDIATE ACTION REQUIRED:
===========================================================
STOP! You are writing code WITHOUT using HoloIndex!

MANDATORY BEFORE ANY MORE CODE:
1. RUN THIS NOW: python holo_index.py --search "what you're building"
2. RUN THIS NOW: python holo_index.py --check-module "module_name"
3. READ the results COMPLETELY
4. DO NOT CREATE NEW FILES - enhance existing ones

YOU ARE VIBECODING IF YOU:
- Started coding without searching
- Created files without checking if they exist
- Ignored HoloIndex results
- Didn't read module documentation

THIS IS YOUR {:.0f}th REMINDER - USE HOLOINDEX!
""".format(self.metrics.assessment_count + 1)
        else:
            prompt += """
[OK] GOOD WSP COMPLIANCE - MAINTAIN THIS BEHAVIOR:
================================================
Continue to:
1. ALWAYS run HoloIndex BEFORE coding
2. ALWAYS check modules BEFORE creating
3. ALWAYS enhance existing code
4. NEVER create duplicates
"""

        prompt += """
==============================================================
[TARGET] REMEMBER THE GOLDEN RULE:
"follow WSP" = USE HOLOINDEX FIRST, ALWAYS!
==============================================================

Next assessment in {:.0f} minutes.
""".format(self.assessment_interval.total_seconds() / 60)

        return prompt

    def reset_metrics(self):
        """Reset metrics for a new session"""
        self.metrics = VibecodeMetrics()
        self._save_state()

    def get_trend_analysis(self, last_n: int = 10) -> str:
        """
        Get trend analysis of recent assessments

        Args:
            last_n: Number of recent assessments to analyze

        Returns:
            Trend analysis text
        """
        if len(self.assessment_history) < 2:
            return "Not enough data for trend analysis"

        recent = self.assessment_history[-last_n:]
        scores = [r.vibecode_score for r in recent]

        avg_score = sum(scores) / len(scores)
        trend = "improving" if scores[-1] < scores[0] else "worsening"

        analysis = f"""
Vibecoding Trend Analysis (Last {len(recent)} assessments):
- Average Score: {avg_score:.1f}/100
- Current Trend: {trend}
- Best Score: {min(scores):.1f}
- Worst Score: {max(scores):.1f}
"""
        return analysis


# Integration with HoloIndex CLI
def integrate_with_cli(assessor: VibecodingAssessor, search_performed: bool = False):
    """
    Integrate assessor with HoloIndex CLI

    Args:
        assessor: The vibecoding assessor instance
        search_performed: Whether a search was just performed
    """
    if search_performed:
        assessor.track_search()

    # Check if assessment needed
    if assessor.should_assess():
        prompt = assessor.get_assessment_prompt()
        if prompt:
            print("\n" + prompt)
            return True

    return False


if __name__ == "__main__":
    # Test the assessor
    assessor = VibecodingAssessor(assessment_interval_minutes=1)  # 1 min for testing

    # Simulate some activity
    assessor.track_search()
    assessor.track_file_creation(is_new=False)
    assessor.track_search()
    assessor.track_file_creation(is_new=True)
    assessor.track_duplicate()

    # Get assessment
    print(assessor.get_assessment_prompt())

    # Show trend
    print(assessor.get_trend_analysis())