#!/usr/bin/env python3
"""
Issue MPS Evaluator - Adapts WSP 15 MPS System for HoloDAE Issue Evaluation
Uses the Module Prioritization Scoring dimensions to evaluate issues found by Qwen

WSP Compliance: WSP 15 (MPS System), WSP 50 (Pre-Action Verification)
"""

from typing import Dict, Tuple, List
from dataclasses import dataclass
from enum import Enum


class IssueSeverity(Enum):
    """Issue severity levels based on MPS priority classification"""
    P0_CRITICAL = "P0"     # 16-20 MPS score - Fix immediately
    P1_HIGH = "P1"         # 13-15 MPS score - Fix in batch
    P2_MEDIUM = "P2"       # 10-12 MPS score - Schedule for sprint
    P3_LOW = "P3"          # 7-9 MPS score - Can defer
    P4_BACKLOG = "P4"      # 4-6 MPS score - Reconsider later


@dataclass
class IssueEvaluation:
    """Result of MPS-based issue evaluation"""
    issue_type: str
    description: str
    complexity_score: int      # A: 1-5 (How difficult to fix?)
    importance_score: int      # B: 1-5 (How essential to system?)
    deferability_score: int    # C: 1-5 (How urgent? Higher = less deferrable)
    impact_score: int          # D: 1-5 (How much value from fixing?)
    total_mps: int            # Sum of A+B+C+D (4-20)
    priority: IssueSeverity
    action: str               # What 0102 should do
    reasoning: str            # Why this evaluation


class IssueMPSEvaluator:
    """
    Evaluates issues found by HoloDAE using WSP 15 MPS methodology.
    Allows 0102 to make autonomous decisions about what to fix based on complexity.
    """

    def __init__(self):
        self.issue_rules = self._define_issue_rules()

    def _define_issue_rules(self) -> Dict[str, Dict[str, int]]:
        """Define MPS scores for common issue types"""
        return {
            # WSP Violations - Usually simple but important
            "WSP_VIOLATION": {
                "complexity": 1,      # Trivial - usually path/structure fixes
                "importance": 4,      # Critical - WSP compliance essential
                "deferability": 4,    # Difficult to defer - violations accumulate
                "impact": 3          # Moderate - improves compliance
            },

            # Dead Code - Simple to remove, moderate importance
            "DEAD_CODE": {
                "complexity": 1,      # Trivial - just delete unused code
                "importance": 2,      # Helpful - cleaner codebase
                "deferability": 2,    # Deferrable - not urgent
                "impact": 2          # Minor - reduces bloat
            },

            # Vibecoding - Easy to fix, high importance
            "VIBECODE": {
                "complexity": 2,      # Low - usually search & enhance
                "importance": 4,      # Critical - prevents technical debt
                "deferability": 5,    # Cannot defer - compounds quickly
                "impact": 4          # Major - prevents future problems
            },

            # Duplicates - Medium complexity, important
            "DUPLICATE": {
                "complexity": 3,      # Moderate - requires consolidation
                "importance": 3,      # Important - architectural coherence
                "deferability": 3,    # Moderate - should fix soon
                "impact": 3          # Moderate - improves maintainability
            },

            # Architecture Issues - Complex, very important
            "ARCHITECTURE": {
                "complexity": 4,      # High - requires careful refactoring
                "importance": 5,      # Essential - system structure
                "deferability": 3,    # Moderate - plan carefully
                "impact": 5          # Transformative - major improvement
            },

            # Dependency Issues - Medium complexity, important
            "DEPENDENCY": {
                "complexity": 3,      # Moderate - requires analysis
                "importance": 4,      # Critical - can break system
                "deferability": 4,    # Difficult to defer - risks cascading
                "impact": 4          # Major - system stability
            },

            # File Size Violations - Complex refactoring needed
            "SIZE_VIOLATION": {
                "complexity": 4,      # High - requires splitting files
                "importance": 3,      # Important - maintainability
                "deferability": 2,    # Deferrable - can plan
                "impact": 3          # Moderate - better structure
            },

            # Missing Tests - Medium complexity, important
            "MISSING_TESTS": {
                "complexity": 3,      # Moderate - write test coverage
                "importance": 3,      # Important - quality assurance
                "deferability": 3,    # Moderate - should have tests
                "impact": 3          # Moderate - prevents bugs
            }
        }

    def evaluate_issue(self, issue_type: str, description: str,
                       confidence: float = 0.9) -> IssueEvaluation:
        """
        Evaluate an issue using MPS methodology.

        Args:
            issue_type: Type of issue (VIBECODE, DUPLICATE, etc.)
            description: Description of the specific issue
            confidence: Qwen's confidence in the issue (affects scores)

        Returns:
            IssueEvaluation with MPS scores and recommended action
        """
        # Get base scores for issue type
        if issue_type in self.issue_rules:
            scores = self.issue_rules[issue_type].copy()
        else:
            # Default scores for unknown issue types
            scores = {
                "complexity": 3,
                "importance": 3,
                "deferability": 3,
                "impact": 3
            }

        # Adjust scores based on confidence
        if confidence < 0.7:
            # Low confidence - reduce urgency
            scores["deferability"] = max(1, scores["deferability"] - 1)
            scores["importance"] = max(1, scores["importance"] - 1)
        elif confidence > 0.95:
            # Very high confidence - increase urgency
            scores["deferability"] = min(5, scores["deferability"] + 1)

        # Calculate total MPS score
        total_mps = sum(scores.values())

        # Determine priority based on MPS score
        if total_mps >= 16:
            priority = IssueSeverity.P0_CRITICAL
            action = "Fix immediately - critical issue"
        elif total_mps >= 13:
            priority = IssueSeverity.P1_HIGH
            action = "Add to current batch - fix within session"
        elif total_mps >= 10:
            priority = IssueSeverity.P2_MEDIUM
            action = "Schedule for next sprint"
        elif total_mps >= 7:
            priority = IssueSeverity.P3_LOW
            action = "Add to backlog - can defer"
        else:
            priority = IssueSeverity.P4_BACKLOG
            action = "Reconsider in future - very low priority"

        # Generate reasoning
        reasoning = self._generate_reasoning(issue_type, scores, total_mps)

        return IssueEvaluation(
            issue_type=issue_type,
            description=description,
            complexity_score=scores["complexity"],
            importance_score=scores["importance"],
            deferability_score=scores["deferability"],
            impact_score=scores["impact"],
            total_mps=total_mps,
            priority=priority,
            action=action,
            reasoning=reasoning
        )

    def _generate_reasoning(self, issue_type: str, scores: Dict[str, int],
                           total_mps: int) -> str:
        """Generate reasoning for the evaluation"""
        complexity_text = ["", "trivial", "low", "moderate", "high", "very high"]
        importance_text = ["", "optional", "helpful", "important", "critical", "essential"]

        reasoning = f"{issue_type} evaluated: "
        reasoning += f"Complexity={complexity_text[scores['complexity']]} ({scores['complexity']}), "
        reasoning += f"Importance={importance_text[scores['importance']]} ({scores['importance']}), "
        reasoning += f"Deferability={scores['deferability']}, "
        reasoning += f"Impact={scores['impact']}. "
        reasoning += f"Total MPS={total_mps}."

        return reasoning

    def batch_evaluate(self, issues: List[Tuple[str, str, float]]) -> List[IssueEvaluation]:
        """
        Evaluate multiple issues and return sorted by priority.

        Args:
            issues: List of (issue_type, description, confidence) tuples

        Returns:
            List of evaluations sorted by MPS score (highest first)
        """
        evaluations = []
        for issue_type, description, confidence in issues:
            evaluation = self.evaluate_issue(issue_type, description, confidence)
            evaluations.append(evaluation)

        # Sort by total MPS score (highest priority first)
        evaluations.sort(key=lambda e: e.total_mps, reverse=True)

        return evaluations

    def get_action_summary(self, evaluations: List[IssueEvaluation]) -> str:
        """Generate a summary of actions for 0102"""
        p0_count = sum(1 for e in evaluations if e.priority == IssueSeverity.P0_CRITICAL)
        p1_count = sum(1 for e in evaluations if e.priority == IssueSeverity.P1_HIGH)
        p2_count = sum(1 for e in evaluations if e.priority == IssueSeverity.P2_MEDIUM)

        summary = f"Issue Queue: {len(evaluations)} total\n"
        if p0_count > 0:
            summary += f"  • P0 (Fix Now): {p0_count} critical issues\n"
        if p1_count > 0:
            summary += f"  • P1 (Batch): {p1_count} high priority\n"
        if p2_count > 0:
            summary += f"  • P2 (Schedule): {p2_count} medium priority\n"

        return summary


# Example usage for testing
if __name__ == "__main__":
    evaluator = IssueMPSEvaluator()

    # Simulate issues found by Qwen
    test_issues = [
        ("VIBECODE", "Created new file without searching existing", 0.95),
        ("WSP_VIOLATION", "Test file in root directory (WSP 49)", 0.99),
        ("DUPLICATE", "Similar functionality in 3 other modules", 0.72),
        ("ARCHITECTURE", "Module exceeds 1500 lines, needs refactoring", 0.88),
        ("DEAD_CODE", "Orphaned module never imported", 0.91),
    ]

    evaluations = evaluator.batch_evaluate(test_issues)

    print("MPS-Based Issue Evaluation Results:")
    print("=" * 60)
    for eval in evaluations:
        print(f"\n{eval.priority.value} - {eval.issue_type}")
        print(f"  Description: {eval.description}")
        print(f"  MPS Score: {eval.total_mps} (C:{eval.complexity_score} I:{eval.importance_score} "
              f"D:{eval.deferability_score} Im:{eval.impact_score})")
        print(f"  Action: {eval.action}")
        print(f"  Reasoning: {eval.reasoning}")

    print("\n" + evaluator.get_action_summary(evaluations))