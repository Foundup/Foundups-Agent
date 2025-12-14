"""
Telemetry Dashboard - Unified metrics for browser automation

Aggregates telemetry from all platform actions for observability.

WSP Compliance:
    - WSP 91: Observability
    - WSP 77: AI Overseer telemetry
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


@dataclass
class PlatformMetrics:
    """Metrics for a single platform."""
    platform: str
    total_actions: int = 0
    successful_actions: int = 0
    failed_actions: int = 0
    total_duration_ms: int = 0
    actions_by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_actions == 0:
            return 0.0
        return self.successful_actions / self.total_actions

    @property
    def avg_duration_ms(self) -> float:
        """Calculate average action duration."""
        if self.total_actions == 0:
            return 0.0
        return self.total_duration_ms / self.total_actions


class TelemetryDashboard:
    """
    Unified telemetry dashboard for all browser automation.

    Tracks:
    - Action counts per platform
    - Success/failure rates
    - Action durations
    - Routing decisions (Selenium vs Vision)
    - AI Overseer mission outcomes

    Usage:
        dashboard = get_dashboard()

        # Record action
        dashboard.record_action(
            platform="youtube",
            action="like_comment",
            success=True,
            duration_ms=450
        )

        # Get metrics
        stats = dashboard.get_platform_stats("youtube")
        print(f"YouTube success rate: {stats.success_rate:.1%}")
    """

    def __init__(self):
        """Initialize dashboard."""
        self._platform_metrics: Dict[str, PlatformMetrics] = {}
        self._router_stats = {
            "selenium_calls": 0,
            "vision_calls": 0,
            "fallbacks": 0,
        }
        self._start_time = datetime.utcnow()

        logger.info("[DASHBOARD] Telemetry dashboard initialized")

    def record_action(
        self,
        platform: str,
        action: str,
        success: bool,
        duration_ms: int,
        driver: str = None,
    ) -> None:
        """
        Record an action execution.

        Args:
            platform: Platform name (youtube, linkedin, x, foundup)
            action: Action type
            success: Whether action succeeded
            duration_ms: Execution duration
            driver: Driver used (selenium, vision)
        """
        # Get or create platform metrics
        if platform not in self._platform_metrics:
            self._platform_metrics[platform] = PlatformMetrics(platform=platform)

        metrics = self._platform_metrics[platform]
        metrics.total_actions += 1

        if success:
            metrics.successful_actions += 1
        else:
            metrics.failed_actions += 1

        metrics.total_duration_ms += duration_ms
        metrics.actions_by_type[action] += 1

        # Track driver usage
        if driver == "selenium":
            self._router_stats["selenium_calls"] += 1
        elif driver == "vision":
            self._router_stats["vision_calls"] += 1

    def record_fallback(self, from_driver: str, to_driver: str) -> None:
        """Record a driver fallback."""
        self._router_stats["fallbacks"] += 1
        logger.debug(f"[DASHBOARD] Fallback: {from_driver} → {to_driver}")

    def get_platform_stats(self, platform: str) -> PlatformMetrics:
        """Get metrics for a specific platform."""
        return self._platform_metrics.get(platform, PlatformMetrics(platform=platform))

    def get_all_stats(self) -> Dict[str, Any]:
        """Get all telemetry statistics."""
        total_actions = sum(m.total_actions for m in self._platform_metrics.values())
        total_successful = sum(m.successful_actions for m in self._platform_metrics.values())

        return {
            "uptime_seconds": (datetime.utcnow() - self._start_time).total_seconds(),
            "total_actions": total_actions,
            "total_successful": total_successful,
            "total_failed": total_actions - total_successful,
            "overall_success_rate": total_successful / total_actions if total_actions > 0 else 0,
            "platforms": {
                platform: {
                    "total_actions": metrics.total_actions,
                    "success_rate": metrics.success_rate,
                    "avg_duration_ms": metrics.avg_duration_ms,
                    "actions_by_type": dict(metrics.actions_by_type),
                }
                for platform, metrics in self._platform_metrics.items()
            },
            "router_stats": self._router_stats.copy(),
        }

    def get_summary(self) -> str:
        """Get human-readable summary."""
        stats = self.get_all_stats()

        lines = [
            "=" * 60,
            "Browser Actions Telemetry Dashboard",
            "=" * 60,
            f"Uptime: {stats['uptime_seconds']:.0f}s",
            f"Total Actions: {stats['total_actions']}",
            f"Success Rate: {stats['overall_success_rate']:.1%}",
            "",
            "Platform Breakdown:",
        ]

        for platform, pstats in stats["platforms"].items():
            lines.append(f"  {platform.upper()}:")
            lines.append(f"    Actions: {pstats['total_actions']}")
            lines.append(f"    Success Rate: {pstats['success_rate']:.1%}")
            lines.append(f"    Avg Duration: {pstats['avg_duration_ms']:.0f}ms")

        lines.append("")
        lines.append("Router Stats:")
        lines.append(f"  Selenium Calls: {stats['router_stats']['selenium_calls']}")
        lines.append(f"  Vision Calls: {stats['router_stats']['vision_calls']}")
        lines.append(f"  Fallbacks: {stats['router_stats']['fallbacks']}")
        lines.append("=" * 60)

        return "\n".join(lines)

    def export_json(self) -> Dict[str, Any]:
        """Export metrics as JSON."""
        return self.get_all_stats()


# Singleton instance
_dashboard = None


def get_dashboard() -> TelemetryDashboard:
    """Get singleton dashboard instance."""
    global _dashboard
    if _dashboard is None:
        _dashboard = TelemetryDashboard()
    return _dashboard


# Helper function for quick access
def record_action(platform: str, action: str, success: bool, duration_ms: int, driver: str = None):
    """Quick helper to record an action."""
    get_dashboard().record_action(platform, action, success, duration_ms, driver)
