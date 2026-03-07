#!/usr/bin/env python3
"""
Regression tests for Connect WRE CLI status command.
"""

import sys
import types


def test_run_connect_wre_reports_ready_with_insufficient_data(monkeypatch):
    """Connect WRE should return truthy state when preflight passes and data is warming."""
    fake_preflight = types.SimpleNamespace(
        run_dae_preflight=lambda dae_name, quiet=False: True,
    )

    class _FakeMonitor:
        def is_in_watch_period(self):
            return True

    fake_alerts = types.SimpleNamespace(
        DashboardAlertMonitor=_FakeMonitor,
        check_dashboard_health=lambda: {
            "healthy": True,
            "alerts": [],
            "insufficient_data": True,
            "total_executions": 0,
            "min_samples": 25,
        },
    )

    monkeypatch.setitem(
        sys.modules,
        "modules.infrastructure.wre_core.src.dae_preflight",
        fake_preflight,
    )
    monkeypatch.setitem(
        sys.modules,
        "modules.infrastructure.wre_core.src.dashboard_alerts",
        fake_alerts,
    )

    from modules.infrastructure.cli.src.main_menu import _run_connect_wre

    assert _run_connect_wre(verbose=False) is True

