#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WRE Dashboard Regression Alerts

Post-release monitoring for 7-day watch period.
Alerts on metric regression vs production baselines.

Usage:
    python -m modules.infrastructure.wre_core.src.dashboard_alerts

Or programmatically:
    from modules.infrastructure.wre_core.src.dashboard_alerts import DashboardAlertMonitor
    monitor = DashboardAlertMonitor()
    alerts = monitor.check_all()
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AlertThreshold:
    """Alert threshold configuration."""
    metric: str
    operator: str  # 'lt' (less than) or 'gt' (greater than)
    threshold: float
    severity: str  # 'warning' or 'critical'
    description: str


@dataclass
class Alert:
    """Triggered alert."""
    metric: str
    current_value: float
    threshold: float
    severity: str
    message: str
    timestamp: str


# Production baselines from gate evidence
PRODUCTION_BASELINES = {
    "tot_confidence_rate": 0.70,
    "codeact_success_rate": 0.90,
    "retrieval_coverage": 0.80,
    "variation_win_rate": 0.50,
    "fidelity_delta_baseline": 0.20,  # +20% from outcome gate
    "repeat_failure_rate_baseline": 0.30,  # Baseline for comparison
}

# Alert thresholds
ALERT_THRESHOLDS = [
    AlertThreshold(
        metric="tot_confidence_rate",
        operator="lt",
        threshold=0.50,
        severity="critical",
        description="ToT selection confidence below 50%"
    ),
    AlertThreshold(
        metric="tot_confidence_rate",
        operator="lt",
        threshold=0.60,
        severity="warning",
        description="ToT selection confidence below 60%"
    ),
    AlertThreshold(
        metric="codeact_success_rate",
        operator="lt",
        threshold=0.80,
        severity="critical",
        description="CodeAct success rate below 80%"
    ),
    AlertThreshold(
        metric="codeact_success_rate",
        operator="lt",
        threshold=0.85,
        severity="warning",
        description="CodeAct success rate below 85%"
    ),
    AlertThreshold(
        metric="retrieval_coverage",
        operator="lt",
        threshold=0.60,
        severity="critical",
        description="RAG retrieval coverage below 60%"
    ),
    AlertThreshold(
        metric="retrieval_coverage",
        operator="lt",
        threshold=0.70,
        severity="warning",
        description="RAG retrieval coverage below 70%"
    ),
    AlertThreshold(
        metric="variation_win_rate",
        operator="lt",
        threshold=0.30,
        severity="critical",
        description="TT-SI variation win rate below 30%"
    ),
    AlertThreshold(
        metric="variation_win_rate",
        operator="lt",
        threshold=0.40,
        severity="warning",
        description="TT-SI variation win rate below 40%"
    ),
    AlertThreshold(
        metric="codeact_gate_trigger_rate",
        operator="gt",
        threshold=0.10,
        severity="warning",
        description="CodeAct safety gate triggers above 10%"
    ),
    AlertThreshold(
        metric="codeact_gate_trigger_rate",
        operator="gt",
        threshold=0.20,
        severity="critical",
        description="CodeAct safety gate triggers above 20%"
    ),
]


class DashboardAlertMonitor:
    """
    Monitor WRE dashboard for metric regressions.

    Checks against production baselines and triggers alerts
    when thresholds are breached.
    """

    def __init__(self, pattern_memory=None):
        """
        Initialize monitor.

        Args:
            pattern_memory: Optional PatternMemory instance.
                           If None, will create one.
        """
        self.pattern_memory = pattern_memory
        self.thresholds = ALERT_THRESHOLDS
        self.baselines = PRODUCTION_BASELINES
        self.watch_period_start = datetime(2026, 2, 24)
        self.watch_period_end = self.watch_period_start + timedelta(days=7)

    def _get_memory(self):
        """Lazy-load pattern memory."""
        if self.pattern_memory is None:
            from modules.infrastructure.wre_core.src.pattern_memory import PatternMemory
            self.pattern_memory = PatternMemory()
        return self.pattern_memory

    def get_dashboard(self) -> Dict:
        """Get current dashboard metrics."""
        memory = self._get_memory()
        return memory.get_telemetry_dashboard()

    def check_threshold(self, metric: str, value: float, threshold: AlertThreshold) -> Optional[Alert]:
        """Check if metric breaches threshold."""
        breached = False

        if threshold.operator == "lt" and value < threshold.threshold:
            breached = True
        elif threshold.operator == "gt" and value > threshold.threshold:
            breached = True

        if breached:
            return Alert(
                metric=metric,
                current_value=value,
                threshold=threshold.threshold,
                severity=threshold.severity,
                message=threshold.description,
                timestamp=datetime.now().isoformat()
            )
        return None

    def check_all(self) -> List[Alert]:
        """
        Check all metrics against thresholds.

        Returns:
            List of triggered alerts (empty if healthy)
        """
        alerts = []
        dashboard = self.get_dashboard()

        # Add computed metrics
        codeact_total = dashboard.get("codeact_executions", 0)
        codeact_triggers = dashboard.get("codeact_gate_triggers", 0)
        if codeact_total > 0:
            dashboard["codeact_gate_trigger_rate"] = codeact_triggers / codeact_total
        else:
            dashboard["codeact_gate_trigger_rate"] = 0.0

        # Check each threshold
        for threshold in self.thresholds:
            if threshold.metric in dashboard:
                value = dashboard[threshold.metric]
                alert = self.check_threshold(threshold.metric, value, threshold)
                if alert:
                    alerts.append(alert)

        # Deduplicate: keep only highest severity per metric
        deduped = {}
        for alert in alerts:
            key = alert.metric
            if key not in deduped:
                deduped[key] = alert
            elif alert.severity == "critical" and deduped[key].severity == "warning":
                deduped[key] = alert

        return list(deduped.values())

    def is_in_watch_period(self) -> bool:
        """Check if currently in 7-day watch period."""
        now = datetime.now()
        return self.watch_period_start <= now <= self.watch_period_end

    def format_alerts(self, alerts: List[Alert]) -> str:
        """Format alerts for display."""
        if not alerts:
            return "[OK] All metrics healthy"

        lines = []
        critical = [a for a in alerts if a.severity == "critical"]
        warnings = [a for a in alerts if a.severity == "warning"]

        if critical:
            lines.append(f"[CRITICAL] {len(critical)} critical alert(s):")
            for a in critical:
                lines.append(f"  - {a.metric}: {a.current_value:.3f} (threshold: {a.threshold:.3f})")
                lines.append(f"    {a.message}")

        if warnings:
            lines.append(f"[WARNING] {len(warnings)} warning(s):")
            for a in warnings:
                lines.append(f"  - {a.metric}: {a.current_value:.3f} (threshold: {a.threshold:.3f})")
                lines.append(f"    {a.message}")

        return "\n".join(lines)

    def run_check(self, verbose: bool = True) -> bool:
        """
        Run full alert check.

        Args:
            verbose: Print results to stdout

        Returns:
            True if all healthy, False if any alerts
        """
        alerts = self.check_all()

        if verbose:
            print("=" * 60)
            print("WRE Dashboard Alert Check")
            print(f"Timestamp: {datetime.now().isoformat()}")
            print(f"Watch period: {self.watch_period_start.date()} to {self.watch_period_end.date()}")
            print(f"In watch period: {self.is_in_watch_period()}")
            print("=" * 60)
            print(self.format_alerts(alerts))
            print("=" * 60)

        return len(alerts) == 0


def check_dashboard_health() -> Dict:
    """
    Quick health check function.

    Returns:
        {"healthy": bool, "alerts": [...], "dashboard": {...}}
    """
    monitor = DashboardAlertMonitor()
    alerts = monitor.check_all()
    dashboard = monitor.get_dashboard()

    return {
        "healthy": len(alerts) == 0,
        "alerts": [
            {
                "metric": a.metric,
                "value": a.current_value,
                "threshold": a.threshold,
                "severity": a.severity,
                "message": a.message
            }
            for a in alerts
        ],
        "dashboard": dashboard,
        "timestamp": datetime.now().isoformat()
    }


# CLI entry point
if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    monitor = DashboardAlertMonitor()
    healthy = monitor.run_check(verbose=True)

    sys.exit(0 if healthy else 1)
