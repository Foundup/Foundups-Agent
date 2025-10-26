# -*- coding: utf-8 -*-
"""
HoloIndex CLI Auto-Refresh Module - WSP 49 Compliant Modular Structure

Handles index freshness checking and optional DocDAE document organization.
Returns structured output for throttler integration.

WSP Compliance: WSP 49 (Module Structure), WSP 83 (Documentation Tree)
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple


def maybe_refresh_indexes(holo, args, db=None) -> Tuple[List[str], Dict[str, bool]]:
    """
    Check index freshness and perform automatic refresh if needed.

    Args:
        holo: HoloIndex instance
        args: Parsed CLI arguments
        db: AgentDB instance (optional)

    Returns:
        Tuple of (summary_lines, action_flags)
        summary_lines: List of strings for throttler sections
        action_flags: Dict with keys like 'code_refreshed', 'wsp_refreshed', 'docdae_ran'
    """
    summary_lines = []
    action_flags = {
        'code_refreshed': False,
        'wsp_refreshed': False,
        'docdae_ran': False
    }

    # Check if indexes need automatic refresh (only if not explicitly indexing)
    if db:
        try:
            needs_code_refresh = db.should_refresh_index("code", max_age_hours=1)
            needs_wsp_refresh = db.should_refresh_index("wsp", max_age_hours=1)

            if needs_code_refresh or needs_wsp_refresh:
                summary_lines.append(f"[AUTOMATIC] Index refresh needed (last refresh > 1 hour)")
                summary_lines.append(f"[AUTOMATIC] Code index: {'STALE' if needs_code_refresh else 'FRESH'}")
                summary_lines.append(f"[AUTOMATIC] WSP index: {'STALE' if needs_wsp_refresh else 'FRESH'}")

                if args.organize_docs:
                    summary_lines.append("[DOCDAE] Checking documentation organization...")
                    try:
                        from modules.infrastructure.doc_dae.src.doc_dae import DocDAE
                        dae = DocDAE()

                        analysis = dae.analyze_docs_folder()
                        misplaced_count = analysis['markdown_docs'] + analysis['json_data']

                        if misplaced_count > 0:
                            summary_lines.append(f"[DOCDAE] Found {misplaced_count} misplaced files - organizing...")
                            result = dae.run_autonomous_organization(dry_run=False)
                            summary_lines.append(f"[DOCDAE] Organized: {result['execution']['moves_completed']} moved, "
                                              f"{result['execution']['archives_completed']} archived")
                            action_flags['docdae_ran'] = True
                        else:
                            summary_lines.append("[DOCDAE] Documentation already organized")
                            action_flags['docdae_ran'] = True
                    except Exception as e:
                        summary_lines.append(f"[WARN] DocDAE failed: {e} - continuing with indexing")
                else:
                    summary_lines.append("[DOCDAE] Skipping automatic organization (use --organize-docs to enable)")

                # Automatically refresh stale indexes
                if needs_code_refresh:
                    summary_lines.append("[AUTO-REFRESH] Refreshing code index...")
                    start_time = time.time()
                    holo.index_code_entries()
                    duration = time.time() - start_time
                    db.record_index_refresh("code", duration, holo.get_code_entry_count())
                    summary_lines.append(f"[AUTO-REFRESH] Code index refreshed in {duration:.1f}s")
                    action_flags['code_refreshed'] = True
                if needs_wsp_refresh:
                    summary_lines.append("[AUTO-REFRESH] Refreshing WSP index...")
                    start_time = time.time()
                    holo.index_wsp_entries()
                    duration = time.time() - start_time
                    db.record_index_refresh("wsp", duration, holo.get_wsp_entry_count())
                    summary_lines.append(f"[AUTO-REFRESH] WSP index refreshed in {duration:.1f}s")
                    action_flags['wsp_refreshed'] = True
                summary_lines.append("[SUCCESS] Automatic index refresh completed")
            else:
                summary_lines.append("[FRESH] All indexes are up to date (< 1 hour old)")

        except Exception as e:
            summary_lines.append(f"[WARN] Could not check index freshness: {e}")

    return summary_lines, action_flags
