# -*- coding: utf-8 -*-
"""
Monitoring Loop - HoloDAE Background Monitoring System

Extracted from holodae_coordinator.py per WSP 62 remediation.
Sprint H5: Monitoring loop methods (fifth extraction, RISKIEST).

WSP Compliance:
- WSP 62: Modularity Enforcement (<500 lines)
- WSP 91: Structured logging for observability
- WSP 49: Module structure compliance

Usage:
    from holo_index.qwen_advisor.services.monitoring_loop import MonitoringLoop

    monitor = MonitoringLoop(
        file_watcher, context_analyzer, repo_root,
        codeindex_engine, architect_engine,
        current_work_context, telemetry_formatter, logger
    )
    monitor.start_monitoring()
    result = monitor.run_monitoring_cycle()
    monitor.stop_monitoring()
"""

import os
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from ..models.monitoring_types import MonitoringResult, FileChange, ChangeType
from .file_system_watcher import FileSystemWatcher
from .context_analyzer import ContextAnalyzer
from .telemetry_formatter import TelemetryFormatter
# Import SkillExecutor type for type hinting (avoid circular import if possible, or use Any)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...wre_integration.skill_executor import SkillExecutor


class MonitoringLoop:
    """
    Background monitoring system for HoloDAE file watching and analysis.

    Responsibilities:
    - Start/stop background monitoring threads
    - Run monitoring cycles to detect file changes
    - Emit monitoring summaries for 012 oversight
    - Build FileChange records from watched files
    - Trigger WRE skills based on monitoring events
    """

    def __init__(
        self,
        file_watcher: FileSystemWatcher,
        context_analyzer: ContextAnalyzer,
        repo_root: Path,
        codeindex_engine: Any,
        architect_engine: Any,
        current_work_context: Any,
        telemetry_formatter: TelemetryFormatter,
        logger: Any,
        monitoring_interval: float = 3.0,
        monitoring_heartbeat: float = 60.0,
        module_metrics_cache: Optional[Dict[str, Dict[str, Any]]] = None,
        holo_log_callback: Optional[callable] = None,
        detailed_log_callback: Optional[callable] = None,
        build_monitor_summary_callback: Optional[callable] = None,
        skill_executor: Optional[Any] = None  # WSP 96: Skill Executor
    ):
        """
        Initialize MonitoringLoop.

        Args:
            file_watcher: File system watcher for change detection
            context_analyzer: Context analyzer for work context tracking
            repo_root: Root path of the repository
            codeindex_engine: CodeIndex MCP engine for health evaluation
            architect_engine: Architect engine for optimization suggestions
            current_work_context: Current work context tracker
            telemetry_formatter: Telemetry formatter for report generation
            logger: Logger for detailed logging
            monitoring_interval: Seconds between monitoring cycles (default 3.0)
            monitoring_heartbeat: Seconds between heartbeat messages (default 60.0)
            module_metrics_cache: Cache for module metrics
            holo_log_callback: Callback for HoloDAE logging
            detailed_log_callback: Callback for detailed logging
            detailed_log_callback: Callback for detailed logging
            build_monitor_summary_callback: Callback for building monitor summaries
            skill_executor: WRE Skill Executor instance
        """
        self.file_watcher = file_watcher
        self.context_analyzer = context_analyzer
        self.repo_root = repo_root
        self.codeindex_engine = codeindex_engine
        self.architect_engine = architect_engine
        self.current_work_context = current_work_context
        self.telemetry_formatter = telemetry_formatter
        self.logger = logger

        self.monitoring_interval = monitoring_interval
        self.monitoring_heartbeat = monitoring_heartbeat
        self._module_metrics_cache = module_metrics_cache if module_metrics_cache is not None else {}
        self.skill_executor = skill_executor

        self.monitoring_enabled = False
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_stop_event = threading.Event()
        self.last_monitoring_result: Optional[MonitoringResult] = None

        # Callbacks for coordinator integration
        self._holo_log = holo_log_callback if holo_log_callback else lambda msg, console=True: None
        self._detailed_log = detailed_log_callback if detailed_log_callback else lambda msg: self.logger.info(msg)
        self._build_monitor_summary_block = build_monitor_summary_callback if build_monitor_summary_callback else lambda r, m, p: []

    def start_monitoring(self) -> bool:
        """Start the quiet monitoring system"""
        if not self.monitoring_enabled:
            self._detailed_log("[HOLODAE-COORDINATOR] Monitoring disabled for this session (enable_monitoring() to override)")
            return False

        if self.monitoring_active:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [HOLODAE] Monitoring already active")
            return False

        self.monitoring_active = True
        self.monitoring_stop_event.clear()
        self._detailed_log("[HOLODAE-COORDINATOR] Starting quiet monitoring mode")

        result = self._run_monitoring_cycle()
        if result.has_actionable_events():
            summary = result.get_summary()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [HOLODAE] [LAUNCH] Quiet monitoring activated - {summary}")
            self._emit_monitoring_summary(result, prefix='[HOLO-MONITOR][INITIAL]')
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [HOLODAE] [LAUNCH] Quiet monitoring activated")

        if self.monitoring_thread is None or not self.monitoring_thread.is_alive():
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, name='HoloMonitor', daemon=True)
            self.monitoring_thread.start()
            self._detailed_log("[HOLODAE-COORDINATOR] Monitoring loop thread started")
        return True

    def run_monitoring_cycle(self) -> MonitoringResult:
        """Trigger a monitoring cycle manually"""
        return self._run_monitoring_cycle()

    def stop_monitoring(self) -> bool:
        """Stop the monitoring system"""
        if not self.monitoring_active:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [HOLODAE] Monitoring not active")
            return False

        self.monitoring_active = False
        self.monitoring_stop_event.set()
        self._detailed_log("[HOLODAE-COORDINATOR] Monitoring deactivated")

        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5.0)
            self._detailed_log("[HOLODAE-COORDINATOR] Monitoring loop thread joined")
        self.monitoring_thread = None
        self.monitoring_stop_event.clear()

        print(f"[{datetime.now().strftime('%H:%M:%S')}] [HOLODAE] Monitoring deactivated")
        return True

    def enable_monitoring(self) -> None:
        """Allow background monitoring loops (used by autonomous daemon mode)."""
        self.monitoring_enabled = True

    def _run_monitoring_cycle(self) -> MonitoringResult:
        """Run a monitoring cycle and update internal state"""
        cycle_start = time.perf_counter()
        changes = self.file_watcher.scan_for_changes()
        file_changes = [self._build_file_change(path) for path in changes]

        result = MonitoringResult(
            changes_detected=file_changes,
            scan_duration=time.perf_counter() - cycle_start,
            watched_paths=self.file_watcher.get_watched_paths()
        )

        modules_to_scan: Set[str] = set()

        if file_changes:
            touched_modules = self.context_analyzer.get_related_modules([change.file_path for change in file_changes])
            for module in touched_modules:
                self._module_metrics_cache.pop(module, None)
            modules_to_scan.update(touched_modules)

            analyzed_context = self.context_analyzer.analyze_work_context(
                [change.file_path for change in file_changes],
                self.current_work_context.session_actions
            )
            self.current_work_context = analyzed_context
        elif self.current_work_context.primary_module:
            modules_to_scan.add(self.current_work_context.primary_module)

        if modules_to_scan:
            module_paths = []
            for module in list(modules_to_scan)[:3]:
                module_path = (self.repo_root / module).resolve()
                if module_path.exists():
                    module_paths.append(module_path)
            if module_paths:
                health_reports = self.codeindex_engine.evaluate_modules(module_paths)
                if health_reports:
                    result.codeindex_reports = [report.to_summary() for report in health_reports]
                    architect_summaries = [
                        self.architect_engine.summarize(report) for report in health_reports
                    ]
                    if architect_summaries:
                        result.optimization_suggestions.extend(architect_summaries[:1])
                        result.metadata['architect_decisions'] = architect_summaries

        self.last_monitoring_result = result
        return result

    def _monitoring_loop(self) -> None:
        """Background monitoring loop that throttles noise for 012 oversight"""
        self._detailed_log('[HOLODAE-COORDINATOR] Monitoring loop active')
        last_heartbeat = time.perf_counter()

        while not self.monitoring_stop_event.is_set():
            cycle_start = time.perf_counter()
            result = self._run_monitoring_cycle()

            if result.has_actionable_events():
                self._emit_monitoring_summary(result, prefix='[HOLO-MONITOR]')
                last_heartbeat = time.perf_counter()

                # Phase 3: WRE Skills Integration (WSP 96 v1.3)
                if self.skill_executor:
                    wre_triggers = self.skill_executor.check_wre_triggers(result)
                    if wre_triggers:
                        self.skill_executor.execute_wre_skills(wre_triggers)

            elif time.perf_counter() - last_heartbeat >= self.monitoring_heartbeat:
                self._emit_monitoring_summary(result, prefix='[HOLO-MONITOR][HEARTBEAT]')
                last_heartbeat = time.perf_counter()

            elapsed = time.perf_counter() - cycle_start
            sleep_for = max(0.2, self.monitoring_interval - elapsed)
            if self.monitoring_stop_event.wait(sleep_for):
                break

        self._detailed_log('[HOLODAE-COORDINATOR] Monitoring loop stopped')

    def _emit_monitoring_summary(self, result: MonitoringResult, prefix: str = '[HOLO-MONITOR]') -> None:
        """Emit a compact summary of monitoring outcomes with module context"""
        change_modules = sorted({change.module_path for change in result.changes_detected if change.module_path})
        module_preview = ', '.join(change_modules[:3]) if change_modules else 'no module activity'
        summary_parts = [
            f"changes={len(result.changes_detected)}",
            f"violations={len(result.violations_found)}",
            f"patterns={len(result.pattern_alerts)}",
            f"modules={module_preview}"
        ]

        if result.pattern_alerts:
            high_conf = next((alert for alert in result.pattern_alerts if alert.is_high_confidence()), None)
            if high_conf:
                summary_parts.append(f"hi-pattern={high_conf.get_summary()}")
        if result.violations_found:
            summary_parts.append(f"first-violation={result.violations_found[0].get_summary()}")
        if result.codeindex_reports:
            critical_total = sum(report.get('critical_fixes', 0) for report in result.codeindex_reports)
            summary_parts.append(f"codeindex-critical={critical_total}")
            if critical_total > 0:
                summary_parts.append("architect=A/B/C ready")

        message = f"{prefix} [DATA] {' | '.join(summary_parts)}"
        self._holo_log(message, console=True)

        if result.has_actionable_events() or '[HEARTBEAT]' in prefix:
            summary_block = self._build_monitor_summary_block(result, message, prefix)
            # TODO: Append to 012 summary if needed
            # self._append_012_summary(summary_block)

    def _build_file_change(self, file_path: str) -> FileChange:
        """Construct a FileChange record from a watched file"""
        file_size = None
        module_path = None
        try:
            file_size = os.path.getsize(file_path)
        except (OSError, IOError):
            pass

        related_modules = self.context_analyzer.get_related_modules([file_path])
        module_path = next(iter(related_modules)) if related_modules else None

        return FileChange(
            file_path=file_path,
            change_type=ChangeType.MODIFIED,
            file_size=file_size,
            is_module_file=module_path is not None,
            module_path=module_path
        )
