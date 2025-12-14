# -*- coding: utf-8 -*-
"""
Telemetry Formatter - HoloDAE Telemetry Logging and Report Formatting

Extracted from holodae_coordinator.py per WSP 62 remediation.
Sprint H3: Telemetry formatting methods (third extraction).

WSP Compliance:
- WSP 62: Modularity Enforcement (<500 lines)
- WSP 91: Structured logging for observability
- WSP 49: Module structure compliance

Usage:
    from holo_index.qwen_advisor.services.telemetry_formatter import TelemetryFormatter

    formatter = TelemetryFormatter(telemetry_logger)
    formatter.log_request_telemetry(query, search_summary, module_metrics, alerts)
    report = formatter.format_final_report(qwen_report, decisions, results)
"""

from typing import Dict, List, Any, Set, Optional
from datetime import datetime
from ..arbitration.mps_arbitrator import ArbitrationDecision
from ..models.monitoring_types import MonitoringResult


# Emoji-to-label mapping for summary normalization
SUMMARY_EMOJI_ALIASES = {
    '[PILL][OK]': 'HEALTH',
    '[AI]': 'PATTERN',
    '[SEARCH]': 'SEMANTIC',
    '[BOX]': 'MODULE',
    '[RULER]': 'SIZE',
    '[GHOST]': 'ORPHAN'
}


class TelemetryFormatter:
    """
    Format telemetry logs and reports for HoloDAE operations.

    Responsibilities:
    - Log structured telemetry for search requests and module status
    - Format module metrics summaries for final reports
    - Build search and monitor summary blocks for 012 oversight
    - Normalize and sanitize summary text for consistent display
    - Extract key findings and high-priority actions from monitoring data
    """

    def __init__(
        self,
        telemetry_logger: Any,
        current_work_context: Optional[Any] = None,
        last_monitoring_result: Optional[MonitoringResult] = None,
        logger: Optional[Any] = None
    ):
        """
        Initialize TelemetryFormatter.

        Args:
            telemetry_logger: Logger for structured telemetry events
            current_work_context: Current work context for reporting
            last_monitoring_result: Last monitoring cycle result
            logger: General logger for debug/error messages
        """
        self.telemetry_logger = telemetry_logger
        self.current_work_context = current_work_context
        self.last_monitoring_result = last_monitoring_result
        self.logger = logger

    def log_request_telemetry(
        self,
        query: str,
        search_summary: Dict[str, List[Any]],
        module_metrics: Dict[str, Dict[str, Any]],
        alerts: List[str]
    ) -> None:
        """Record structured telemetry for the current request"""
        try:
            code_hits = len(search_summary.get('code', []))
            wsp_hits = len(search_summary.get('wsps', []))
            self.telemetry_logger.log_search_request(query=query, code_hits=code_hits, wsp_hits=wsp_hits)

            for module, metrics in module_metrics.items():
                alerts_for_module = metrics.get('module_alerts') or []
                if alerts_for_module:
                    wsp_clause = 'WSP 49'
                    for rec in metrics.get('recommendations', []):
                        if 'WSP' in rec:
                            wsp_clause = rec.split('(')[0].strip()
                            break

                    severity = 'critical' if '[CRITICAL]' in metrics.get('size_label', '') else 'warning'
                    evidence = {
                        'health': metrics.get('health_label'),
                        'size': metrics.get('size_label'),
                        'alerts': alerts_for_module,
                    }
                    self.telemetry_logger.log_module_status(
                        module=module,
                        wsp_clause=wsp_clause,
                        severity=severity,
                        evidence=evidence,
                        next_action='refactor' if severity == 'critical' else 'review',
                        acknowledged=False,
                    )

                    health = metrics.get('health_label', '')
                    if 'Missing:' in health:
                        missing_part = health.split('Missing:')[1].strip()
                        for doc in [d.strip() for d in missing_part.split(',') if d.strip()]:
                            doc_path = f"{module}/{doc}"
                            self.telemetry_logger.log_doc_hint(module=module, doc_path=doc_path, reason='Missing required documentation')

            if alerts:
                self.telemetry_logger.log_event('system_alerts', alerts=alerts[:5])
        except Exception as exc:
            if self.logger:
                self.logger.error(f"[HOLODAE-TELEMETRY] Failed to log telemetry: {exc}")

    def format_module_metrics_summary(self, module_metrics: Dict[str, Dict[str, Any]], alerts: List[str]) -> str:
        """Create a concise summary of module metrics for final report"""
        if not module_metrics and not alerts:
            return ''

        lines: List[str] = []
        for module, metrics in module_metrics.items():
            issues: List[str] = []
            health_label = metrics.get('health_label')
            if health_label and health_label != '[COMPLETE]':
                issues.append(health_label)
            module_alerts = metrics.get('module_alerts') or []
            issues.extend(module_alerts)
            if issues:
                lines.append(f"[MODULE-ALERT] {module}: {'; '.join(issues)}")

        if alerts:
            lines.append(f"[SYSTEM-ALERT] {' | '.join(alerts[:3])}")

        if not lines:
            return ''

        lines.insert(0, '[MODULE-METRICS] Module health recap')
        return '\n'.join(lines)

    def format_final_report(
        self,
        qwen_report: str,
        arbitration_decisions: List[ArbitrationDecision],
        execution_results: Dict[str, Any]
    ) -> str:
        """Format the final report for 012 monitoring"""
        lines = []

        # Qwen's orchestrated analysis
        lines.append(qwen_report)

        # 0102's arbitration decisions
        if arbitration_decisions:
            lines.append("\n[0102-ARBITRATION] Arbitration Decisions:")
            for decision in arbitration_decisions:
                lines.append(f"  {decision.recommended_action.value.upper()}: {decision.description}")
                lines.append(f"    MPS: {decision.mps_analysis.total_score} | {decision.reasoning}")

        # Execution results
        if execution_results:
            executed = len(execution_results.get('executed_immediately', []))
            batched = len(execution_results.get('batched_for_session', []))
            lines.append(f"\n[EXECUTION] Immediate: {executed} | Batched: {batched}")

        if self.current_work_context:
            context_summary = self.current_work_context.get_summary()
            if context_summary:
                lines.append(f"\n[WORK-CONTEXT] {context_summary}")

        if self.last_monitoring_result:
            lines.append(f"[MONITORING] {self.last_monitoring_result.get_summary()}")

        return "\n".join(lines)

    def normalize_summary_line(self, text: str) -> str:
        """Normalize summary text by replacing emojis with labels"""
        normalized = text.strip()
        for emoji, label in SUMMARY_EMOJI_ALIASES.items():
            if emoji in normalized:
                normalized = normalized.replace(emoji, f"{label} ({emoji})")
        fallback_map = {
            '?? [HOLODAE-HEALTH': 'HEALTH ([PILL][OK]) [HOLODAE-HEALTH',
            '?? HOLODAE-HEALTH': 'HEALTH ([PILL][OK]) HOLODAE-HEALTH',
            '抽笨・': 'HEALTH ([PILL][OK])',
            '剥': 'SEMANTIC ([SEARCH])',
            '逃': 'MODULE ([BOX])',
            'ｧ': 'PATTERN ([AI])',
            '棟': 'SIZE ([RULER])',
            '遜': 'ORPHAN ([GHOST])'
        }
        for fallback, replacement in fallback_map.items():
            normalized = normalized.replace(fallback, replacement)
        # Strip out any remaining non-ASCII glyphs introduced by noisy logs
        normalized = ''.join(ch if 32 <= ord(ch) < 127 else ' ' for ch in normalized)
        normalized = ' '.join(normalized.split())
        return normalized

    def format_modules_for_summary(self, modules: List[str]) -> str:
        """Format module list for summary display"""
        module_list = []
        for module in modules:
            if module and module not in module_list:
                module_list.append(module)
        if not module_list:
            return 'none'
        preview = module_list[:4]
        formatted = ', '.join(preview)
        if len(module_list) > len(preview):
            formatted += ' ...'
        return formatted

    def extract_key_findings(self, alerts: List[str], module_metrics: Dict[str, Dict[str, Any]]) -> List[str]:
        """Extract key findings from alerts and module metrics"""
        findings: List[str] = []
        seen: Set[str] = set()

        def add_entry(entry: str) -> None:
            if entry and entry not in seen:
                seen.add(entry)
                findings.append(entry)

        for alert in alerts:
            normalized = self.normalize_summary_line(alert)
            add_entry(normalized)
            if len(findings) >= 5:
                return findings

        for module, metrics in module_metrics.items():
            health_label = metrics.get('health_label')
            if health_label and health_label not in {'[COMPLETE]', '[UNKNOWN]'}:
                add_entry(self.normalize_summary_line(f"{module}: {health_label}"))
            for module_alert in (metrics.get('module_alerts') or [])[:2]:
                add_entry(self.normalize_summary_line(f"{module}: {module_alert}"))
            if len(findings) >= 5:
                break

        return findings[:5]

    def extract_high_priority_actions(self, decisions: List[ArbitrationDecision]) -> List[str]:
        """Extract high-priority actions from arbitration decisions"""
        actions: List[str] = []
        seen: Set[str] = set()

        for decision in decisions:
            summary = self.normalize_summary_line(decision.description)
            if not summary or not self._is_meaningful_action(summary):
                continue

            if summary in seen:
                continue
            seen.add(summary)

            action_label = decision.recommended_action.value.replace('_', ' ').title()
            score = None
            if getattr(decision, 'mps_analysis', None):
                score = decision.mps_analysis.total_score
            if score is not None:
                actions.append(f"{action_label} (MPS {score}): {summary}")
            else:
                actions.append(f"{action_label}: {summary}")

            if len(actions) >= 5:
                break

        return actions

    def _is_meaningful_action(self, summary: str) -> bool:
        """Check if action summary is meaningful (not noise)"""
        noise_phrases = (
            'no high-risk vibecoding patterns detected',
            'executed components',
            'no monitoring alerts',
            'no actionable violations detected',
            'monitoring loop active',
            'monitoring loop stopped',
            'no module activity',
            'analysis complete',
            'request processing complete'
        )
        lowered = summary.lower()
        return not any(phrase in lowered for phrase in noise_phrases)

    def build_search_summary_block(self, query: str, modules: List[str], findings: List[str], actions: List[str]) -> List[str]:
        """Build a search summary block for display"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        lines = [f"=== {timestamp} SEARCH ==="]
        lines.append(f"Query: {self.normalize_summary_line(query)}")
        lines.append(f"Modules: {self.format_modules_for_summary(modules)}")
        if findings:
            lines.append('Key Findings:')
            lines.extend(f"  - {entry}" for entry in findings)
        else:
            lines.append('Key Findings: none')
        if actions:
            lines.append('High Priority Actions:')
            lines.extend(f"  - {entry}" for entry in actions)
        else:
            lines.append('High Priority Actions: none')
        return lines

    def build_monitor_summary_block(self, result: MonitoringResult, summary_message: str, prefix: str) -> List[str]:
        """Build a monitoring summary block for display"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        label = 'MONITOR-HEARTBEAT' if '[HEARTBEAT]' in prefix else 'MONITOR'
        lines = [f"=== {timestamp} {label} ==="]
        lines.append(f"Summary: {self.normalize_summary_line(summary_message)}")
        modules = sorted({change.module_path for change in result.changes_detected if change.module_path})
        lines.append(f"Modules: {self.format_modules_for_summary(modules)}")
        if result.changes_detected:
            lines.append('Recent Changes:')
            for change in result.changes_detected[:3]:
                path_display = change.file_path
                lines.append(f"  - {self.normalize_summary_line(path_display)}")
        if result.violations_found:
            lines.append('Violations:')
            for violation in result.violations_found[:3]:
                lines.append(f"  - {self.normalize_summary_line(violation.get_summary())}")
        if result.pattern_alerts:
            lines.append('Patterns:')
            for alert in result.pattern_alerts[:2]:
                lines.append(f"  - {self.normalize_summary_line(alert.get_summary())}")
        return lines

    def sanitize_summary_block(self, block: str) -> str:
        """Sanitize summary block by normalizing all lines"""
        sanitized_lines: List[str] = []
        for line in block.splitlines():
            if not line.strip():
                sanitized_lines.append('')
                continue
            if line.startswith('=== '):
                sanitized_lines.append(' '.join(line.strip().split()))
                continue
            prefix_len = len(line) - len(line.lstrip())
            prefix = line[:prefix_len]
            normalized = self.normalize_summary_line(line.strip())
            sanitized_lines.append(f"{prefix}{normalized}")
        return '\n'.join(sanitized_lines)
