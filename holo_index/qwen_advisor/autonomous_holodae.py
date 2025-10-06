#!/usr/bin/env python3
"""
Autonomous HoloDAE - Self-Improving Code Intelligence Foundation

This is the truly autonomous HoloIndex daemon that automatically maintains
its knowledge base and provides real-time intelligence for WSP compliance.

Key Features:
- Automatic re-indexing when documentation changes are detected
- Self-improvement through continuous learning
- Foundation layer for WSP framework
- Autonomous operation following WSP 80 (Cube-Level DAE)

WSP Compliance: WSP 80 (Cube-Level DAE), WSP 87 (Code Navigation), WSP 84 (Memory Verification)
"""

import os
import time
import threading
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set

from .holodae_coordinator import HoloDAECoordinator
from ..core.holo_index import HoloIndex
from ..utils.helpers import get_wsp_paths
from .intelligent_monitor import IntelligentMonitor, MonitoringContext
from .models.work_context import WorkContext
from ..dae_cube_organizer.dae_cube_organizer import DAECubeCodeMap
from modules.infrastructure.database.src.agent_db import AgentDB


class AutonomousHoloDAE:
    """
    Autonomous HoloDAE - Foundation layer for WSP framework

    This daemon automatically maintains HoloIndex's knowledge base and
    provides self-improvement capabilities for the entire WSP ecosystem.
    """

    def __init__(self):
        """Initialize the autonomous HoloDAE"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("[HOLO-DAE] Initializing Autonomous HoloDAE...")

        # Core components
        self.holo_index = HoloIndex()
        self.holodae_coordinator = HoloDAECoordinator()
        self.intelligent_monitor = IntelligentMonitor()
        self.code_map = DAECubeCodeMap()  # NEW: Real-time 0102 work context mapping

        # State management
        self.active = False
        self.monitoring_thread = None
        self.stop_event = threading.Event()

        # Auto-reindex configuration
        self.reindex_check_interval = 300  # Check every 5 minutes
        self.max_index_age_hours = 6  # Same as CLI auto-refresh
        self.last_reindex_check = datetime.now()

        # Track file changes for re-indexing triggers
        self.documentation_paths = get_wsp_paths()
        self.last_known_file_count = self._count_documentation_files()

        self.logger.info("[HOLO-DAE] Autonomous HoloDAE initialized with auto-reindexing")

    def _count_documentation_files(self) -> int:
        """Count total documentation files that HoloIndex should track"""
        total_files = 0
        doc_extensions = {'.md', '.py', '.json', '.txt'}

        for path in self.documentation_paths:
            if path.exists():
                for file_path in path.rglob('*'):
                    if file_path.is_file() and file_path.suffix.lower() in doc_extensions:
                        total_files += 1

        return total_files

    def _detect_new_modules(self) -> list[str]:
        """
        Detect newly added modules that aren't yet indexed
        Enhanced module detection for daemon self-improvement

        Returns:
            list: Names of newly detected modules
        """
        new_modules = []
        try:
            # Check modules directory for new module folders
            modules_dir = Path("../modules") if Path.cwd().name == 'holo_index' else Path("modules")

            if modules_dir.exists():
                for module_dir in modules_dir.iterdir():
                    if module_dir.is_dir() and not module_dir.name.startswith('.'):
                        module_name = module_dir.name

                        # Check if module has required documentation files
                        readme_path = module_dir / "README.md"
                        if readme_path.exists():
                            # Check if this module is already known to the index
                            if not self._is_module_indexed(module_name):
                                new_modules.append(module_name)
                                self.logger.info(f"[MODULE-DETECT] New module discovered: {module_name}")

        except Exception as e:
            self.logger.debug(f"[MODULE-DETECT] Error during module detection: {e}")

        return new_modules

    def _is_module_indexed(self, module_name: str) -> bool:
        """
        Check if a module is already indexed by searching for its documentation

        Args:
            module_name: Name of the module to check

        Returns:
            bool: True if module documentation is found in index
        """
        try:
            # Search for the module name in WSP index
            results = self.holo_index.search(f"module {module_name}", doc_type_filter="module_readme", limit=1)
            return len(results) > 0
        except Exception:
            return False

    def _check_cli_monitor_triggers(self) -> bool:
        """
        Check if CLI IntelligentMonitor has triggered re-indexing recommendations
        Integrates daemon with CLI monitoring system for unified self-improvement

        Returns:
            bool: True if CLI monitor recommends re-indexing
        """
        try:
            # Create a monitoring context for the daemon's current state
            context = MonitoringContext(
                query="daemon_status_check",  # Special query for daemon monitoring
                user="0102_daemon",  # Identifies this as daemon-initiated
                timestamp=datetime.now(),
                session_id=f"daemon_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                metadata={
                    "daemon_active": self.active,
                    "last_reindex": self.last_reindex_check.isoformat(),
                    "wsp_entries": self.holo_index.get_wsp_entry_count(),
                    "code_entries": self.holo_index.get_code_entry_count(),
                    "documentation_files": self.last_known_file_count
                }
            )

            # Run intelligent monitoring
            legacy_data = {
                "health_warnings": [],
                "optimization_suggestions": [],
                "performance_metrics": {},
                "module_health": {}
            }

            # Check each trigger in the intelligent monitor
            for trigger_name, trigger_func in self.intelligent_monitor.triggers.items():
                try:
                    if trigger_func(context):
                        self.logger.debug(f"[CLI-INTEGRATION] Trigger '{trigger_name}' activated")
                        # Execute the trigger's action
                        trigger_action = getattr(self.intelligent_monitor, f"_trigger_{trigger_name.split('_')[0]}", None)
                        if trigger_action:
                            trigger_action(context, legacy_data)

                            # Check if this trigger recommends re-indexing
                            suggestions = legacy_data.get("optimization_suggestions", [])
                            for suggestion in suggestions:
                                if suggestion.get("action", "").lower().find("reindex") >= 0:
                                    self.logger.info(f"[CLI-INTEGRATION] Re-indexing recommended by trigger: {trigger_name}")
                                    return True
                except Exception as e:
                    self.logger.debug(f"[CLI-INTEGRATION] Error checking trigger {trigger_name}: {e}")

            return False

        except Exception as e:
            self.logger.debug(f"[CLI-INTEGRATION] Error during CLI monitor integration: {e}")
            return False

    def _should_reindex(self) -> tuple[bool, str]:
        """
        Determine if automatic re-indexing is needed
        Uses same logic as CLI auto-refresh with enhanced daemon-specific checks

        Returns:
            tuple: (should_reindex, reason)
        """
        try:
            # Check 1: Database freshness (same logic as CLI)
            db = AgentDB()
            needs_wsp_refresh = db.should_refresh_index("wsp", max_age_hours=self.max_index_age_hours)
            needs_code_refresh = db.should_refresh_index("code", max_age_hours=self.max_index_age_hours)

            if needs_wsp_refresh or needs_code_refresh:
                reason = f"Index stale (> {self.max_index_age_hours} hours): WSP={needs_wsp_refresh}, Code={needs_code_refresh}"
                return True, reason

            # Check 2: File count changes (new files added)
            current_file_count = self._count_documentation_files()
            if current_file_count != self.last_known_file_count:
                reason = f"Documentation files changed: {self.last_known_file_count} -> {current_file_count}"
                self.last_known_file_count = current_file_count
                return True, reason

            # Check 3: New module detection (enhanced for daemon)
            new_modules = self._detect_new_modules()
            if new_modules:
                reason = f"New modules detected: {', '.join(new_modules)}"
                return True, reason

            # Check 4: Time-based recheck (every 2 hours even if fresh)
            time_since_check = datetime.now() - self.last_reindex_check
            if time_since_check.total_seconds() > (2 * 3600):  # 2 hours
                self.last_reindex_check = datetime.now()
                # Do a quick verification by checking actual entry counts
                wsp_count = self.holo_index.get_wsp_entry_count()
                code_count = self.holo_index.get_code_entry_count()

                if wsp_count == 0 or code_count == 0:
                    reason = f"Index appears empty (WSP: {wsp_count}, Code: {code_count})"
                    return True, reason

                self.logger.info(f"[AUTO-CHECK] Indexes verified: WSP={wsp_count}, Code={code_count}")
                return False, "Indexes verified and current"

            return False, "All checks passed"

        except Exception as e:
            self.logger.warning(f"[AUTO-CHECK] Error during re-index check: {e}")
            return True, f"Error during check: {e}"

    def _perform_auto_reindex(self) -> bool:
        """
        Perform automatic re-indexing of stale or changed documentation

        Returns:
            bool: True if re-indexing completed successfully
        """
        try:
            self.logger.info("[AUTO-REINDEX] Starting automatic index refresh...")

            db = AgentDB()
            total_start = time.time()
            reindex_count = 0

            # Check and refresh WSP index
            if db.should_refresh_index("wsp", max_age_hours=self.max_index_age_hours):
                wsp_start = time.time()
                self.holo_index.index_wsp_entries()
                wsp_duration = time.time() - wsp_start
                wsp_count = self.holo_index.get_wsp_entry_count()
                db.record_index_refresh("wsp", wsp_duration, wsp_count)
                self.logger.info(f"[AUTO-REINDEX] WSP index refreshed: {wsp_count} entries in {wsp_duration:.1f}s")
                reindex_count += 1

            # Check and refresh code index
            if db.should_refresh_index("code", max_age_hours=self.max_index_age_hours):
                code_start = time.time()
                self.holo_index.index_code_entries()
                code_duration = time.time() - code_start
                code_count = self.holo_index.get_code_entry_count()
                db.record_index_refresh("code", code_duration, code_count)
                self.logger.info(f"[AUTO-REINDEX] Code index refreshed: {code_count} entries in {code_duration:.1f}s")
                reindex_count += 1

            total_duration = time.time() - total_start

            if reindex_count > 0:
                self.logger.info(f"[AUTO-REINDEX] ✅ Completed automatic refresh of {reindex_count} indexes in {total_duration:.1f}s")
                return True
            else:
                self.logger.info("[AUTO-REINDEX] No indexes needed refreshing")
                return True

        except Exception as e:
            self.logger.error(f"[AUTO-REINDEX] ❌ Failed automatic re-indexing: {e}")
            return False

    def _monitor_and_self_improve(self):
        """Main monitoring loop for autonomous operation"""
        self.logger.info("[HOLO-DAE] Starting autonomous monitoring and self-improvement...")

        while not self.stop_event.is_set():
            try:
                # Check if re-indexing is needed (daemon-specific checks)
                should_reindex, reason = self._should_reindex()
                if should_reindex:
                    self.logger.info(f"[HOLO-DAE] 🔄 Auto-reindex triggered: {reason}")
                    success = self._perform_auto_reindex()
                    if success:
                        self.logger.info("[HOLO-DAE] ✅ Self-improvement completed successfully")
                    else:
                        self.logger.warning("[HOLO-DAE] ⚠️ Self-improvement encountered issues")

                # Check CLI IntelligentMonitor triggers (integration with CLI system)
                cli_reindex_triggered = self._check_cli_monitor_triggers()
                if cli_reindex_triggered:
                    self.logger.info("[HOLO-DAE] 🔄 CLI-triggered re-index initiated")
                    success = self._perform_auto_reindex()
                    if success:
                        self.logger.info("[HOLO-DAE] ✅ CLI-integrated re-indexing completed")
                    else:
                        self.logger.warning("[HOLO-DAE] ⚠️ CLI-integrated re-indexing failed")

                # Run normal HoloDAE coordination
                if self.holodae_coordinator.monitoring_active:
                    # Update work context and run monitoring cycle
                    changed_files = list(self.holodae_coordinator.file_watcher.scan_for_changes())

                    # Create WorkContext for monitoring
                    current_context = WorkContext(
                        active_files=set(changed_files),
                        primary_module=None,
                        task_pattern="monitoring"
                    )

                    # Run QWEN-controlled monitoring with self-improvement feedback
                    monitoring_result = self.holodae_coordinator.qwen_orchestrator.orchestrate_monitoring(current_context)

                    # SELF-IMPROVEMENT: Analyze monitoring output to improve future filtering
                    self._analyze_monitoring_output_for_improvement(monitoring_result)
                    self.holodae_coordinator.last_monitoring_result = monitoring_result

                    # Log significant findings
                    if monitoring_result.optimization_suggestions:
                        self.logger.info(f"[HOLO-DAE] 🤖 Generated {len(monitoring_result.optimization_suggestions)} optimization suggestions")

                # Sleep until next check
                self.stop_event.wait(self.reindex_check_interval)

            except Exception as e:
                self.logger.error(f"[HOLO-DAE] Error in monitoring loop: {e}")
                self.stop_event.wait(60)  # Wait a minute before retrying

    def _analyze_monitoring_output_for_improvement(self, monitoring_result):
        """
        SELF-IMPROVEMENT: Analyze monitoring output to improve future QWEN filtering.

        Learns from:
        - Which components were skipped and why
        - Output patterns that were too noisy
        - Intent detection accuracy
        - User interaction patterns
        """
        if not monitoring_result:
            return

        # Extract patterns from monitoring result
        violations = getattr(monitoring_result, 'violations_found', [])
        suggestions = getattr(monitoring_result, 'optimization_suggestions', [])
        alerts = getattr(monitoring_result, 'pattern_alerts', [])

        improvement_insights = []

        # Analyze violation patterns
        if violations:
            violation_types = [v.violation_type for v in violations if hasattr(v, 'violation_type')]
            if 'structure_violation' in str(violation_types).lower():
                improvement_insights.append("INCREASE_WSP_FILTERING_STRENGTH")
            if len(violations) > 5:
                improvement_insights.append("ADD_OUTPUT_COMPRESSION_FOR_HIGH_VIOLATION_COUNTS")

        # Analyze suggestion patterns
        if suggestions:
            if any('documentation' in str(s).lower() for s in suggestions):
                improvement_insights.append("IMPROVE_DOCUMENTATION_INDEXING_AUTOMATION")
            if len(suggestions) > 10:
                improvement_insights.append("ADD_SUGGESTION_PRIORITIZATION_FILTER")

        # Analyze alert patterns
        if alerts:
            if len(alerts) > 3:
                improvement_insights.append("ADD_ALERT_DEDUPLICATION")

        # Apply self-improvements to QWEN orchestrator
        if improvement_insights:
            self._apply_qwen_improvements(improvement_insights)
            self.logger.info(f"[HOLO-DAE] 🔄 Self-improvement applied: {len(improvement_insights)} insights")

    def _apply_qwen_improvements(self, insights):
        """
        Apply learned improvements to QWEN filtering system.

        Modifies intent detection thresholds, output filters, and component selection
        based on observed patterns.
        """
        orchestrator = self.holodae_coordinator.qwen_orchestrator

        for insight in insights:
            if insight == "INCREASE_WSP_FILTERING_STRENGTH":
                # Make WSP violations trigger more easily
                if hasattr(orchestrator, '_component_info'):
                    for component, info in orchestrator._component_info.items():
                        if 'health' in component.lower():
                            info['triggers'].append('has_wsp_violations')

            elif insight == "ADD_OUTPUT_COMPRESSION_FOR_HIGH_VIOLATION_COUNTS":
                # Add compression when violations > 5
                orchestrator._intent_filters['standard']['compact_format'] = True

            elif insight == "IMPROVE_DOCUMENTATION_INDEXING_AUTOMATION":
                # Add more documentation keywords to intent detection
                orchestrator._intent_keywords['documentation'].extend([
                    'readme', 'docs', 'documentation', 'index', 'discover'
                ])

            elif insight == "ADD_SUGGESTION_PRIORITIZATION_FILTER":
                # Limit suggestions to top 5
                orchestrator._max_suggestions = 5

            elif insight == "ADD_ALERT_DEDUPLICATION":
                # Add deduplication for similar alerts
                orchestrator._deduplicate_alerts = True

    def start_autonomous_monitoring(self):
        """Start the autonomous HoloDAE monitoring"""
        if self.active:
            self.logger.warning("[HOLO-DAE] Already active")
            return

        self.logger.info("[HOLO-DAE] 🚀 Starting autonomous operation...")
        self.active = True

        # Initialize code map tracking for 0102 work context
        self._initialize_code_map_tracking()

        # Start HoloDAE coordinator
        self.holodae_coordinator.start_monitoring()

        # Start monitoring thread
        self.monitoring_thread = threading.Thread(
            target=self._monitor_and_self_improve,
            name="HoloDAEMonitor",
            daemon=True
        )
        self.monitoring_thread.start()

        self.logger.info("[HOLO-DAE] ✅ Autonomous HoloDAE now active - Foundation layer operational")

    def _initialize_code_map_tracking(self):
        """Initialize real-time 0102 work context mapping."""
        self.logger.info("[CODE-MAP] Initializing DAE Cube Code Map for 0102 work tracking")
        self.logger.info("[CODE-MAP] Components loaded: DAECubeCodeMap, Integration Gap Detection, Work Context Mapping")
        self.logger.info("[CODE-MAP] Ready to track 0102 agent work context in real-time")

    def get_current_work_context_map(self, agent_id: str = "0102") -> Dict[str, Any]:
        """
        Get the current work context map for an agent.

        This shows exactly what the agent is working on, down to the module and line.
        """
        self.logger.info(f"[CODE-MAP] Generating work context map for agent: {agent_id}")
        work_map = self.code_map.get_live_code_map(agent_id)
        self.logger.info(f"[CODE-MAP] Work context generated - Task: {work_map.get('current_task', {}).get('description', 'Unknown')}, Confidence: {work_map.get('confidence', 0.0):.2f}")
        return work_map

    def update_agent_cursor_position(self, agent_id: str, file_path: str, line: int, column: int = 0):
        """
        Update the cursor position for real-time work context tracking.

        This enables the code map to know exactly where the agent is working.
        """
        self.code_map.update_cursor_position(agent_id, file_path, line, column)
        self.logger.debug(f"[CODE-MAP] Updated cursor for {agent_id}: {file_path}:{line}")

    def stop_autonomous_monitoring(self):
        """Stop the autonomous HoloDAE monitoring"""
        if not self.active:
            self.logger.info("[HOLO-DAE] Not currently active")
            return

        self.logger.info("[HOLO-DAE] 🛑 Stopping autonomous operation...")
        self.active = False

        # Stop monitoring thread
        self.stop_event.set()
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=10)

        # Stop HoloDAE coordinator
        self.holodae_coordinator.stop_monitoring()

        self.logger.info("[HOLO-DAE] ✅ Autonomous HoloDAE stopped successfully")

    def get_status(self) -> Dict[str, Any]:
        """Get current status of the autonomous HoloDAE"""
        return {
            "active": self.active,
            "holodae_active": self.holodae_coordinator.monitoring_active if self.holodae_coordinator else False,
            "last_reindex_check": self.last_reindex_check.isoformat(),
            "documentation_files": self.last_known_file_count,
            "wsp_entries": self.holo_index.get_wsp_entry_count(),
            "code_entries": self.holo_index.get_code_entry_count(),
            "check_interval_seconds": self.reindex_check_interval
        }


# For backwards compatibility with main.py
def start_holodae_monitoring():
    """Legacy function for backwards compatibility"""
    dae = AutonomousHoloDAE()
    dae.start_autonomous_monitoring()
    return dae


def show_holodae_menu():
    """Legacy function for backwards compatibility - shows menu and returns user choice"""
    from .ui.menu_system import show_main_menu  # Import correct function that returns choice
    return show_main_menu()  # Returns user's menu choice
