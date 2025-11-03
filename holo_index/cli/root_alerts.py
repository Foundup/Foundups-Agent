# -*- coding: utf-8 -*-
"""
HoloIndex CLI Root Alerts Module - WSP 64 Compliant Violation Prevention

Handles root directory violation monitoring and alerting.
Returns structured output for throttler integration.

WSP Compliance: WSP 64 (Violation Prevention), WSP 50 (Pre-action Verification)
"""

from typing import Optional


def get_root_alert_summary(verbose: bool = False) -> Optional[str]:
    """
    Check for root directory violations and return alert summary.

    Args:
        verbose: Whether to include detailed information

    Returns:
        Alert summary string for throttler, or None if no alerts
    """
    try:
        from holo_index.monitoring.root_violation_monitor import get_root_violation_alert
        import asyncio

        # Run violation check synchronously
        violation_alert = asyncio.run(get_root_violation_alert())
        if violation_alert:
            return violation_alert
    except Exception as e:
        if verbose:
            return f"[WARNING] Root violation monitoring failed: {e}"

    return None
