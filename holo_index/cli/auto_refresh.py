# -*- coding: utf-8 -*-
"""
HoloIndex CLI Auto-Refresh Module - WSP 49 Compliant Modular Structure

Handles index freshness checking and optional DocDAE document organization.
Returns structured output for throttler integration.

WSP Compliance: WSP 49 (Module Structure), WSP 83 (Documentation Tree)
"""

import os
import time
import threading
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

# AutonomousHoloDAE integration for background auto-reindex
try:
    from holo_index.qwen_advisor.autonomous_holodae import AutonomousHoloDAE
    AUTONOMOUS_HOLODAE_AVAILABLE = True
except ImportError:
    AUTONOMOUS_HOLODAE_AVAILABLE = False

# Global daemon instance (singleton pattern)
_autonomous_daemon: Optional['AutonomousHoloDAE'] = None
_daemon_lock = threading.Lock()


def ensure_autonomous_daemon_running() -> Tuple[bool, str]:
    """
    Ensure AutonomousHoloDAE is running in background for continuous auto-reindex.

    Returns:
        Tuple of (success, message)
    """
    global _autonomous_daemon

    if not AUTONOMOUS_HOLODAE_AVAILABLE:
        return False, "[DAEMON] AutonomousHoloDAE not available"

    with _daemon_lock:
        if _autonomous_daemon is None:
            try:
                _autonomous_daemon = AutonomousHoloDAE()
                _autonomous_daemon.start_autonomous_monitoring()
                return True, "[DAEMON] AutonomousHoloDAE started - continuous auto-reindex enabled"
            except Exception as e:
                return False, f"[DAEMON] Failed to start AutonomousHoloDAE: {e}"
        elif not _autonomous_daemon.active:
            try:
                _autonomous_daemon.start_autonomous_monitoring()
                return True, "[DAEMON] AutonomousHoloDAE restarted - continuous auto-reindex enabled"
            except Exception as e:
                return False, f"[DAEMON] Failed to restart AutonomousHoloDAE: {e}"
        else:
            return True, "[DAEMON] AutonomousHoloDAE already running"


def maybe_refresh_indexes(holo, args, db=None) -> Tuple[List[str], Dict[str, bool]]:
    """
    Check index freshness and perform automatic refresh if needed.
    Auto-starts AutonomousHoloDAE for background monitoring (Gemma pattern detection).

    Args:
        holo: HoloIndex instance
        args: Parsed CLI arguments
        db: AgentDB instance (optional)

    Returns:
        Tuple of (summary_lines, action_flags)
        summary_lines: List of strings for throttler sections
        action_flags: Dict with keys like 'code_refreshed', 'wsp_refreshed', 'docdae_ran', 'daemon_started'
    """
    summary_lines = []
    action_flags = {
        'code_refreshed': False,
        'wsp_refreshed': False,
        'docdae_ran': False,
        'daemon_started': False
    }

    # Auto-start AutonomousHoloDAE for background auto-reindex + Gemma pattern detection
    daemon_success, daemon_msg = ensure_autonomous_daemon_running()
    if daemon_success:
        summary_lines.append(daemon_msg)
        action_flags['daemon_started'] = True

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
