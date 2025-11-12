# -*- coding: utf-8 -*-
"""
HoloIndex CLI Pattern Coach Module - WSP 87 Compliant Vibecoding Prevention

Handles pattern coach guidance collection.
Returns structured output for throttler integration.

WSP Compliance: WSP 87 (Size Limits), WSP 84 (Enhance Existing)
"""

from typing import Optional


def get_pattern_coach_guidance(pattern_coach, query: str, search_results: dict, health_warnings: list = None) -> Optional[str]:
    """
    Get pattern coach guidance for the query.

    Args:
        pattern_coach: PatternCoach instance
        query: Search query
        search_results: Search results dict
        health_warnings: List of health warnings

    Returns:
        Guidance message string, or None
    """
    if not pattern_coach:
        return None

    try:
        # Get health warnings for pattern coach
        health_warnings = health_warnings or []
        if 'health_notices' in search_results:
            health_warnings = search_results['health_notices']

        # Convert results to format expected by pattern coach
        search_results_list = search_results.get('code', []) + search_results.get('wsps', [])

        # Get intelligent coaching based on query and context
        coaching_msg = pattern_coach.analyze_and_coach(
            query=query,
            search_results=search_results_list,
            health_warnings=health_warnings
        )

        return coaching_msg
    except Exception as e:
        return f"[WARN] Pattern coach failed: {e}"

