# -*- coding: utf-8 -*-
"""
Helper utilities that make PatternCoach guidance available without having
to import the `holo_index.cli` package as a module (avoids naming clashes
with the `cli.py` entry point).
"""

from typing import Optional, Sequence, Dict, Any


def get_pattern_coach_guidance(
    pattern_coach,
    query: str,
    search_results: Dict[str, Any],
    health_warnings: Optional[Sequence[str]] = None,
) -> Optional[str]:
    """
    Delegate to PatternCoach.analyze_and_coach() while normalising inputs.
    """
    if not pattern_coach:
        return None

    health_context = list(health_warnings or [])
    if 'health_notices' in search_results:
        notices = search_results['health_notices']
        if isinstance(notices, (list, tuple)):
            health_context.extend(notices)
        elif notices:
            health_context.append(notices)

    search_hits = search_results.get('code', []) + search_results.get('wsps', [])

    return pattern_coach.analyze_and_coach(
        query=query,
        search_results=search_hits,
        health_warnings=health_context,
    )
