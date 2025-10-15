from __future__ import annotations

import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

from ..qwen_advisor.qwen_health_monitor import CodeIndexCirculationEngine
from ..qwen_advisor.architect_mode import ArchitectDecisionEngine
from ..qwen_advisor.qwen_health_monitor.health_reporter import HealthReport


@dataclass
class CodeIndexReport:
    """Structured report payload for downstream storage/display."""

    title: str
    generated_at: datetime.datetime
    module_reports: List[HealthReport]
    markdown: str


class CodeIndexReporter:
    """Generates CodeIndex + architect summaries for a collection of modules."""

    def __init__(
        self,
        circulation_engine: CodeIndexCirculationEngine | None = None,
        architect_engine: ArchitectDecisionEngine | None = None,
    ) -> None:
        self.circulation_engine = circulation_engine or CodeIndexCirculationEngine()
        self.architect_engine = architect_engine or ArchitectDecisionEngine()

    def generate(self, module_paths: Iterable[Path], title: str) -> CodeIndexReport:
        module_path_list = list(module_paths)
        health_reports = self.circulation_engine.evaluate_modules(module_path_list)
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        markdown = self._to_markdown(title, timestamp, health_reports)
        return CodeIndexReport(
            title=title,
            generated_at=timestamp,
            module_reports=health_reports,
            markdown=markdown,
        )

    def _to_markdown(
        self,
        title: str,
        generated_at: datetime.datetime,
        health_reports: Sequence[HealthReport],
    ) -> str:
        lines: List[str] = [
            f"# {title}",
            "",
            f"- Generated: {generated_at.isoformat()}",
            f"- Modules analyzed: {len(health_reports)}",
            "",
        ]

        if not health_reports:
            lines.append("No modules available for CodeIndex analysis.")
            return "\n".join(lines)

        for report in health_reports:
            lines.append(f"## Module: {report.module_name}")
            lines.append("")
            lines.append(f"- Critical fixes: **{report.critical_fix_count()}**")
            if report.surgical_fixes:
                lines.append("")
                lines.append("### Surgical Fixes")
                for fix in report.surgical_fixes[:5]:
                    lines.append(
                        f"- `{fix.function}` ({fix.line_range}) — {fix.estimated_effort}min, complexity {fix.complexity}"
                    )
            lines.append("")
            architect_summary = self.architect_engine.summarize(report)
            lines.append("### Architect Options")
            lines.append("```text")
            lines.append(architect_summary)
            lines.append("```")

            if report.circulation_summary:
                lines.append("")
                lines.append("### Circulation Health")
                lines.append("```text")
                lines.append(report.circulation_summary)
                lines.append("```")

            if report.assumption_alerts:
                lines.append("")
                lines.append("### Assumption Alerts")
                lines.append("```text")
                lines.append(report.assumption_alerts)
                lines.append("```")

            lines.append("")

        return "\n".join(lines)


def resolve_module_paths(repo_root: Path, modules: Iterable[str]) -> List[Path]:
    """Resolve module directories relative to repository root."""
    paths: List[Path] = []
    for module in modules:
        candidate = (repo_root / module).resolve()
        if candidate.exists():
            paths.append(candidate)
    return paths
