from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, List, Optional

from ..advisor import AdvisorContext, QwenAdvisor
from .health_reporter import HealthReport, SurgicalFix

logger = logging.getLogger(__name__)


class CodeIndexCirculationEngine:
    """
    Lightweight engine that runs CodeIndex surgical analysis on a set of modules.

    Designed as the first building block for WSP 93's continuous 5 minute loop.
    It intentionally keeps the API small so HoloDAE coordinators can integrate
    gradually without a sweeping refactor.
    """

    def __init__(self, advisor: Optional[QwenAdvisor] = None) -> None:
        self.advisor = advisor or QwenAdvisor()

    def _build_context(self, module_path: Path) -> Optional[AdvisorContext]:
        """Construct AdvisorContext seeded with the module's primary file."""
        if not module_path.exists():
            logger.debug("[CODEINDEX-MONITOR] Module path missing: %s", module_path)
            return None

        python_files = sorted(module_path.rglob("*.py"))
        if not python_files:
            logger.debug("[CODEINDEX-MONITOR] No python files in module: %s", module_path)
            return None

        primary_file = python_files[0]
        code_hits = [{"file_path": str(primary_file)}]
        return AdvisorContext(
            query=f"CodeIndex health scan for {module_path.name}",
            code_hits=code_hits,
            wsp_hits=[],
        )

    def evaluate_module(self, module_path: Path) -> Optional[HealthReport]:
        """
        Run CodeIndex surgical analysis for the given module directory.

        Returns HealthReport with surgical fixes + circulation insights.
        """
        context = self._build_context(module_path)
        if not context:
            return None

        logger.info("[CODEINDEX-MONITOR] Evaluating module: %s", module_path)
        surgical_results = self.advisor.surgical_code_index(context)

        circulation_summary = self.advisor.continuous_circulation(context)
        architect_options = self.advisor.present_choice(context)
        assumption_alerts = self.advisor.challenge_assumptions(context)

        fixes = [
            SurgicalFix(
                module=fix["module"],
                function=fix["function"],
                line_range=fix["line_range"],
                estimated_effort=fix["estimated_effort"],
                complexity=fix["complexity"],
            )
            for fix in surgical_results.get("exact_fixes", [])
        ]

        report = HealthReport(
            module_name=module_path.name,
            surgical_fixes=fixes,
            circulation_summary=circulation_summary,
            architect_options=architect_options,
            assumption_alerts=assumption_alerts,
        )
        logger.debug(
            "[CODEINDEX-MONITOR] Completed scan %s | critical fixes=%s",
            module_path.name,
            report.critical_fix_count(),
        )
        return report

    def evaluate_modules(self, module_paths: Iterable[Path]) -> List[HealthReport]:
        """Convenience helper to scan multiple modules sequentially."""
        reports: List[HealthReport] = []
        for module_path in module_paths:
            report = self.evaluate_module(module_path)
            if report:
                reports.append(report)
        return reports
