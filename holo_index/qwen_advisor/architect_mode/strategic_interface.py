from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ..qwen_health_monitor import HealthReport, SurgicalFix


@dataclass
class ArchitectDecision:
    """Simple representation of an A/B/C style decision."""

    label: str
    summary: str
    supporting_details: List[str]

    def to_dict(self) -> Dict[str, object]:
        return {
            "label": self.label,
            "summary": self.summary,
            "details": self.supporting_details,
        }


class ArchitectDecisionEngine:
    """
    Converts HealthReport artifacts into architect-ready decisions.

    The initial implementation keeps the logic deterministic and
    inexpensive so HoloDAE can adopt it incrementally.
    """

    def build_decisions(self, report: HealthReport) -> List[ArchitectDecision]:
        """Return three-option decision framing derived from the report."""
        if not report.surgical_fixes:
            return [
                ArchitectDecision(
                    label="A",
                    summary="Maintain current module state",
                    supporting_details=[
                        "No surgical fixes detected by CodeIndex.",
                        "Continue monitoring via circulation loop.",
                    ],
                ),
                ArchitectDecision(
                    label="B",
                    summary="Improve documentation and assumptions",
                    supporting_details=[
                        "Address assumption alerts to prevent regressions.",
                        "Use TODO reminders surfaced in the report.",
                    ],
                ),
                ArchitectDecision(
                    label="C",
                    summary="Schedule holistic module refactor",
                    supporting_details=[
                        "Plan future sprint to improve modularity.",
                        "Use HoloDAE module metrics to estimate effort.",
                    ],
                ),
            ]

        top_fix = report.surgical_fixes[0]
        secondary_fixes = report.surgical_fixes[1:3]

        gradual_details = [
            f"{fix.function} ({fix.line_range}) – {fix.estimated_effort}min"
            for fix in secondary_fixes
        ]
        if not gradual_details:
            gradual_details.append("Break remaining work into sub-functions.")

        return [
            ArchitectDecision(
                label="A",
                summary=f"Surgical: Refactor {top_fix.function} ({top_fix.line_range})",
                supporting_details=[
                    f"Estimated effort: {top_fix.estimated_effort} minutes",
                    f"Complexity score: {top_fix.complexity}",
                    "Reduces immediate complexity hot spot.",
                ],
            ),
            ArchitectDecision(
                label="B",
                summary="Gradual: chip away at remaining high complexity",
                supporting_details=gradual_details,
            ),
            ArchitectDecision(
                label="C",
                summary="Holistic redesign",
                supporting_details=[
                    "Plan comprehensive restructuring once resources free up.",
                    "Use circulation + assumptions text as preparatory research.",
                ],
            ),
        ]

    def summarize(self, report: HealthReport) -> str:
        """Produce a console-friendly summary block for quick display."""
        decisions = self.build_decisions(report)
        lines = [
            f"[ARCHITECT] Module: {report.module_name}",
            f"[ARCHITECT] Critical Fixes: {report.critical_fix_count()}",
        ]
        for decision in decisions:
            lines.append(f"  ({decision.label}) {decision.summary}")
            for detail in decision.supporting_details[:2]:
                lines.append(f"     → {detail}")
        return "\n".join(lines)
