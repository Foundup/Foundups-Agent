#!/usr/bin/env python3
"""
MPS Arbitrator - 0102's decision-making layer for reviewing Qwen's orchestration

This module implements WSP 15 (MPS - Module Prioritization Scoring) algorithm
to review Qwen's findings and decide what actions to take.

0102 acts as the "brain" - reviewing Qwen's orchestration decisions and making
final arbitration calls based on MPS scoring.

WSP Compliance: WSP 15 (Module Prioritization Scoring), WSP 80 (Cube-Level DAE Orchestration)
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import os
import sys




def _ensure_utf8_console():
    if os.name != 'nt':
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        if kernel32.GetConsoleOutputCP() != 65001:
            kernel32.SetConsoleOutputCP(65001)
        if kernel32.GetConsoleCP() != 65001:
            kernel32.SetConsoleCP(65001)
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def _safe_print(message: str) -> None:
    _ensure_utf8_console()
    try:
        print(message)
    except UnicodeEncodeError:
        sys.stdout.buffer.write((message + '\n').encode('utf-8', errors='replace'))

class PriorityLevel(Enum):
    """MPS Priority levels based on WSP 15"""
    P0_CRITICAL = "P0"  # Fix immediately - critical blockers
    P1_HIGH = "P1"      # Batch fixes - high priority this session
    P2_MEDIUM = "P2"    # Schedule - medium priority for sprint
    P3_LOW = "P3"       # Backlog - can defer
    P4_IGNORE = "P4"    # Reconsider - very low priority


class ActionType(Enum):
    """Types of actions 0102 can take"""
    EXECUTE_IMMEDIATELY = "execute_immediately"
    BATCH_FOR_SESSION = "batch_for_session"
    SCHEDULE_FOR_SPRINT = "schedule_for_sprint"
    ADD_TO_BACKLOG = "add_to_backlog"
    IGNORE = "ignore"


@dataclass
class MPSAnalysis:
    """MPS scoring analysis for a finding"""
    complexity: int  # 1-5 scale
    importance: int  # 1-5 scale
    deferability: int  # 1-5 scale (1 = cannot defer, 5 = can defer indefinitely)
    impact: int  # 1-5 scale

    @property
    def total_score(self) -> int:
        """Calculate total MPS score"""
        return self.complexity + self.importance + self.deferability + self.impact

    @property
    def priority_level(self) -> PriorityLevel:
        """Determine priority level based on MPS score"""
        score = self.total_score
        if score >= 16:
            return PriorityLevel.P0_CRITICAL
        elif score >= 13:
            return PriorityLevel.P1_HIGH
        elif score >= 10:
            return PriorityLevel.P2_MEDIUM
        elif score >= 7:
            return PriorityLevel.P3_LOW
        else:
            return PriorityLevel.P4_IGNORE


@dataclass
class ArbitrationDecision:
    """0102's arbitration decision on a Qwen finding"""
    finding_id: str
    finding_type: str  # e.g., "wsp_violation", "vibecoding_pattern", "health_issue"
    description: str
    mps_analysis: MPSAnalysis
    recommended_action: ActionType
    reasoning: str
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class MPSArbitrator:
    """0102's arbitration layer - reviews Qwen's findings and makes MPS-based decisions"""

    def __init__(self):
        """Initialize the MPS arbitrator"""
        self.decision_history = []
        self.mps_calculations = []

    def arbitrate_qwen_findings(self, qwen_report: str) -> List[ArbitrationDecision]:
        """Review Qwen's orchestrated analysis and make arbitration decisions

        Args:
            qwen_report: The formatted analysis report from Qwen orchestrator

        Returns:
            List of arbitration decisions with MPS scoring and recommended actions
        """
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [0102-ARBITRATION] Reviewing Qwen findings with MPS scoring...")

        decisions = []

        # Parse Qwen's report for individual findings
        findings = self._parse_qwen_report(qwen_report)

        print(f"[{datetime.now().strftime('%H:%M:%S')}] [0102-ARBITRATION] Found {len(findings)} findings to evaluate")

        for finding in findings:
            # Perform MPS analysis on each finding
            mps_analysis = self._analyze_finding_with_mps(finding)

            # Log MPS scoring at debug level to reduce noise
            # Only show critical scores (P0/P1) at info level
            if mps_analysis.total_score >= 13:  # P0 or P1 priority
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [0102-MPS-CRITICAL] {finding['type']} = {mps_analysis.total_score} (P{mps_analysis.priority_level.value[-1]})")
            # All other scores go to debug/detailed log (not shown by default)

            # Determine recommended action based on MPS
            recommended_action = self._get_action_from_mps(mps_analysis)

            # Create arbitration decision
            decision = ArbitrationDecision(
                finding_id=f"{finding['type']}_{hash(finding['description']) % 10000}",
                finding_type=finding['type'],
                description=finding['description'],
                mps_analysis=mps_analysis,
                recommended_action=recommended_action,
                reasoning=self._generate_reasoning(mps_analysis, recommended_action)
            )

            decisions.append(decision)
            self.decision_history.append(decision)

        return decisions

    def _parse_qwen_report(self, report: str) -> List[Dict[str, str]]:
        """Parse Qwen's analysis report to extract individual findings"""
        findings = []
        lines = report.split('\n')

        current_finding = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for finding indicators
            if any(keyword in line.upper() for keyword in ['VIOLATION', 'PATTERN', 'FOUND', 'DETECTED', 'WARNING', 'ERROR']):
                # Extract finding information
                finding_type = self._classify_finding(line)
                description = self._extract_description(line)

                findings.append({
                    'type': finding_type,
                    'description': description,
                    'raw_line': line
                })

        return findings

    def _classify_finding(self, line: str) -> str:
        """Classify the type of finding from the line"""
        line_upper = line.upper()

        if 'WSP' in line_upper and ('VIOLATION' in line_upper or 'MISSING' in line_upper):
            return 'wsp_violation'
        elif 'PATTERN' in line_upper and ('VIBECODING' in line_upper or 'DUPLICATE' in line_upper):
            return 'vibecoding_pattern'
        elif 'HEALTH' in line_upper or 'SIZE' in line_upper:
            return 'health_issue'
        elif 'ORPHAN' in line_upper or 'DEAD' in line_upper:
            return 'orphan_analysis'
        elif 'MODULE' in line_upper and 'ANALYSIS' in line_upper:
            return 'module_issue'
        else:
            return 'general_finding'

    def _extract_description(self, line: str) -> str:
        """Extract human-readable description from finding line"""
        # Remove common prefixes
        prefixes_to_remove = ['[', ']', '⚠', 'ERROR', 'WARNING', 'FOUND', 'DETECTED']
        description = line

        for prefix in prefixes_to_remove:
            description = description.replace(prefix, '')

        # Clean up extra spaces and colons
        description = description.strip()
        if description.startswith(':'):
            description = description[1:].strip()

        return description or line  # Fallback to original line

    def _analyze_finding_with_mps(self, finding: Dict[str, str]) -> MPSAnalysis:
        """Analyze a finding using WSP 15 MPS methodology"""
        finding_type = finding['type']
        description = finding['description']

        # Base MPS scores
        complexity = 2  # Default medium complexity
        importance = 3  # Default medium importance
        deferability = 3  # Default medium deferability
        impact = 2  # Default medium impact

        # Adjust scores based on finding type
        if finding_type == 'wsp_violation':
            # WSP violations are high importance, low deferability
            importance = 5
            deferability = 1  # Cannot defer WSP compliance
            impact = 4

            # Check if it's size-related (higher complexity)
            if 'LINES' in description.upper() or 'SIZE' in description.upper():
                complexity = 4

        elif finding_type == 'vibecoding_pattern':
            # Vibecoding patterns are critical to prevent
            importance = 5
            deferability = 2
            impact = 5
            complexity = 2  # Usually quick to analyze

        elif finding_type == 'health_issue':
            # Health issues vary - analyze description
            if 'CRITICAL' in description.upper():
                importance = 5
                deferability = 1
                impact = 5
            else:
                importance = 3
                deferability = 3
                impact = 3

        elif finding_type == 'orphan_analysis':
            # Orphan analysis is lower priority
            importance = 2
            deferability = 4
            impact = 2
            complexity = 3  # Can be complex to analyze

        elif finding_type == 'module_issue':
            # Module issues are important but often deferable
            importance = 4
            deferability = 3
            impact = 4
            complexity = 3

        return MPSAnalysis(
            complexity=min(5, complexity),
            importance=min(5, importance),
            deferability=min(5, deferability),
            impact=min(5, impact)
        )

    def _get_action_from_mps(self, mps: MPSAnalysis) -> ActionType:
        """Determine recommended action based on MPS priority level"""
        priority = mps.priority_level

        if priority == PriorityLevel.P0_CRITICAL:
            return ActionType.EXECUTE_IMMEDIATELY
        elif priority == PriorityLevel.P1_HIGH:
            return ActionType.BATCH_FOR_SESSION
        elif priority == PriorityLevel.P2_MEDIUM:
            return ActionType.SCHEDULE_FOR_SPRINT
        elif priority == PriorityLevel.P3_LOW:
            return ActionType.ADD_TO_BACKLOG
        else:  # P4_IGNORE
            return ActionType.IGNORE

    def _generate_reasoning(self, mps: MPSAnalysis, action: ActionType) -> str:
        """Generate reasoning for the arbitration decision"""
        score_breakdown = f"MPS Score: {mps.total_score} (C:{mps.complexity}, I:{mps.importance}, D:{mps.deferability}, P:{mps.impact})"

        action_reasoning = {
            ActionType.EXECUTE_IMMEDIATELY: "P0 critical issue requiring immediate attention",
            ActionType.BATCH_FOR_SESSION: "P1 high priority, suitable for batch processing this session",
            ActionType.SCHEDULE_FOR_SPRINT: "P2 medium priority, schedule for upcoming sprint",
            ActionType.ADD_TO_BACKLOG: "P3 low priority, add to backlog for future consideration",
            ActionType.IGNORE: "P4 very low priority, reconsider if situation changes"
        }

        return f"{score_breakdown}. {action_reasoning[action]}."

    def execute_arbitration_decisions(self, decisions: List[ArbitrationDecision]) -> Dict[str, Any]:
        """Execute the arbitration decisions (this would integrate with actual fix systems)"""
        execution_results = {
            'executed_immediately': [],
            'batched_for_session': [],
            'scheduled_for_sprint': [],
            'added_to_backlog': [],
            'ignored': [],
            'total_decisions': len(decisions)
        }

        # Track counts to reduce noise
        action_counts = {
            ActionType.EXECUTE_IMMEDIATELY: 0,
            ActionType.BATCH_FOR_SESSION: 0,
            ActionType.SCHEDULE_FOR_SPRINT: 0,
            ActionType.ADD_TO_BACKLOG: 0,
            ActionType.IGNORE: 0
        }

        # Only show first few examples of each type to reduce noise
        shown_examples = {
            ActionType.EXECUTE_IMMEDIATELY: 0,
            ActionType.BATCH_FOR_SESSION: 0,
            ActionType.SCHEDULE_FOR_SPRINT: 0,
            ActionType.ADD_TO_BACKLOG: 0,
            ActionType.IGNORE: 0
        }
        max_examples_per_type = 3  # Only show first 3 of each type

        for decision in decisions:
            action = decision.recommended_action
            action_counts[action] += 1

            if action == ActionType.EXECUTE_IMMEDIATELY:
                execution_results['executed_immediately'].append(decision.finding_id)
                # Only show first few examples
                if shown_examples[action] < max_examples_per_type:
                    _safe_print(f"[{datetime.now().strftime('%H:%M:%S')}] [0102-ARBITRATION] EXECUTING: {decision.description}")
                    shown_examples[action] += 1

            elif action == ActionType.BATCH_FOR_SESSION:
                execution_results['batched_for_session'].append(decision.finding_id)
                if shown_examples[action] < max_examples_per_type:
                    _safe_print(f"[{datetime.now().strftime('%H:%M:%S')}] [0102-ARBITRATION] BATCHING: {decision.description}")
                    shown_examples[action] += 1

            elif action == ActionType.SCHEDULE_FOR_SPRINT:
                execution_results['scheduled_for_sprint'].append(decision.finding_id)
                if shown_examples[action] < max_examples_per_type:
                    _safe_print(f"[{datetime.now().strftime('%H:%M:%S')}] [0102-ARBITRATION] SCHEDULING: {decision.description}")
                    shown_examples[action] += 1

            elif action == ActionType.ADD_TO_BACKLOG:
                execution_results['added_to_backlog'].append(decision.finding_id)
                if shown_examples[action] < max_examples_per_type:
                    _safe_print(f"[{datetime.now().strftime('%H:%M:%S')}] [0102-ARBITRATION] BACKLOGGING: {decision.description}")
                    shown_examples[action] += 1

            else:  # IGNORE
                execution_results['ignored'].append(decision.finding_id)
                # Don't show ignored items at all to reduce noise

        return execution_results

    def get_arbitration_summary(self) -> Dict[str, Any]:
        """Get summary of recent arbitration activity"""
        recent_decisions = self.decision_history[-20:]  # Last 20 decisions

        priority_counts = {}
        for decision in recent_decisions:
            priority = decision.mps_analysis.priority_level.value
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        return {
            'total_decisions': len(self.decision_history),
            'recent_decisions': len(recent_decisions),
            'priority_distribution': priority_counts,
            'avg_mps_score': sum(d.mps_analysis.total_score for d in recent_decisions) / max(1, len(recent_decisions))
        }
