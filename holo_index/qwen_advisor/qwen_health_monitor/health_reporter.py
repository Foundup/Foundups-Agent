from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class SurgicalFix:
    """Precise CodeIndex fix location surfaced by QwenAdvisor."""

    module: str
    function: str
    line_range: str
    estimated_effort: int
    complexity: int

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to primitive types for telemetry."""
        return {
            "module": self.module,
            "function": self.function,
            "line_range": self.line_range,
            "estimated_effort": self.estimated_effort,
            "complexity": self.complexity,
        }


@dataclass
class HealthReport:
    """Aggregated health insight for a module scan."""

    module_name: str
    timestamp: float = field(default_factory=lambda: time.time())
    surgical_fixes: List[SurgicalFix] = field(default_factory=list)
    circulation_summary: str = ""
    architect_options: str = ""
    assumption_alerts: str = ""

    def critical_fix_count(self) -> int:
        """Return number of high-effort fixes surfaced (>= 60 minutes)."""
        return sum(1 for fix in self.surgical_fixes if fix.estimated_effort >= 60)

    def to_summary(self) -> Dict[str, Any]:
        """Compact summary for console dashboards and telemetry."""
        return {
            "module": self.module_name,
            "timestamp": self.timestamp,
            "critical_fixes": self.critical_fix_count(),
            "fixes": [fix.to_dict() for fix in self.surgical_fixes[:5]],
            "circulation": self.circulation_summary[:400],
            "architect_options": self.architect_options[:400],
            "assumptions": self.assumption_alerts[:400],
        }
