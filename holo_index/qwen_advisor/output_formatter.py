#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io

"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

Output Formatter - Clean, actionable console output for 0102

Based on 012's observations: The output 0102 sees is the choke point.
This module provides structured, actionable summaries replacing noisy logs.

WSP Compliance: WSP 62 (Modularity), WSP 22 (Documentation)
"""

from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import json
from pathlib import Path


class HoloOutputFormatter:
    """Formats HoloDAE analysis into clean, actionable output for 0102"""

    def __init__(self, verbose: bool = False):
        """Initialize the output formatter

        Args:
            verbose: If True, include DETAILS section in output
        """
        self.verbose = verbose
        self.todos = []
        self.summary_lines = []
        self.detail_lines = []

    def format_analysis(self,
                       query: str,
                       search_results: Dict[str, Any],
                       module_metrics: Dict[str, Dict[str, Any]],
                       alerts: List[str]) -> str:
        """Format complete analysis into structured console output

        Returns clean, actionable output with:
        - SUMMARY: What happened (search hits, modules flagged)
        - TODO: Numbered action items with specific files/docs
        - DETAILS: (verbose only) Evidence and metrics
        """
        self._build_summary(query, search_results, module_metrics)
        self._build_todos(module_metrics, alerts)
        self._build_details(module_metrics)

        return self._render_output()

    def _build_summary(self, query: str, search_results: Dict[str, Any],
                      module_metrics: Dict[str, Dict[str, Any]]) -> None:
        """Build the SUMMARY section"""
        self.summary_lines = []

        # Search summary
        code_hits = len(search_results.get('code', []))
        wsp_hits = len(search_results.get('wsps', []))
        self.summary_lines.append(
            f"  - Search: \"{query}\" -> {code_hits} code hits, {wsp_hits} WSP docs"
        )

        # Modules flagged
        flagged_modules = []
        for module_path, metrics in module_metrics.items():
            if metrics.get('module_alerts'):
                wsp_violations = self._extract_wsp_violations(metrics)
                flagged_modules.append(f"{module_path} ({', '.join(wsp_violations)})")

        if flagged_modules:
            self.summary_lines.append(
                f"  - Modules flagged: {', '.join(flagged_modules[:3])}"
            )
            if len(flagged_modules) > 3:
                self.summary_lines.append(f"  - ... and {len(flagged_modules) - 3} more")

    def _build_todos(self, module_metrics: Dict[str, Dict[str, Any]],
                    alerts: List[str]) -> None:
        """Build the TODO section with actionable items"""
        self.todos = []
        todo_counter = 1

        # Module-specific TODOs
        for module_path, metrics in module_metrics.items():
            if not metrics.get('module_alerts'):
                continue

            todo_items = []

            # Size violations
            if 'lines' in metrics.get('size_label', ''):
                lines_match = self._extract_line_count(metrics['size_label'])
                if lines_match and lines_match > 800:
                    todo_items.append(f"Refactor large files ({lines_match} lines)")

            # Missing docs
            missing_docs = self._extract_missing_docs(metrics)
            if missing_docs:
                todo_items.append(f"Create: {', '.join(missing_docs)}")

            # Always add doc reading requirement
            todo_items.append("Read INTERFACE.md, update ModLog")

            if todo_items:
                self.todos.append(
                    f"  {todo_counter}. {module_path} – {'. '.join(todo_items)}."
                )
                todo_counter += 1

        # System-level alerts as TODOs
        for alert in alerts[:3]:  # Limit to top 3 alerts
            if 'duplicate' in alert.lower():
                self.todos.append(f"  {todo_counter}. Review duplicates: {alert}")
                todo_counter += 1

    def _build_details(self, module_metrics: Dict[str, Dict[str, Any]]) -> None:
        """Build the DETAILS section (verbose mode only)"""
        if not self.verbose:
            return

        self.detail_lines = []

        for module_path, metrics in module_metrics.items():
            if not metrics.get('module_alerts'):
                continue

            self.detail_lines.append(f"  - {module_path}:")

            # File-level details
            if 'size_label' in metrics:
                self.detail_lines.append(f"      * Size: {metrics['size_label']}")

            # Doc status
            if 'health_label' in metrics:
                self.detail_lines.append(f"      * Health: {metrics['health_label']}")

            # Duplicates if any
            if 'duplicates' in metrics:
                for dup in metrics['duplicates'][:2]:
                    self.detail_lines.append(f"      * Duplicate: {dup}")

    def _render_output(self) -> str:
        """Render the final structured output"""
        lines = []

        # SUMMARY section
        if self.summary_lines:
            lines.append("[SUMMARY]")
            lines.extend(self.summary_lines)
            lines.append("")  # Blank line

        # TODO section
        if self.todos:
            lines.append("[TODO]")
            lines.extend(self.todos)
            lines.append("")  # Blank line

        # DETAILS section (verbose only)
        if self.verbose and self.detail_lines:
            lines.append("[DETAILS]")
            lines.extend(self.detail_lines)
            lines.append("")  # Blank line

        return "\n".join(lines)

    def _extract_wsp_violations(self, metrics: Dict[str, Any]) -> List[str]:
        """Extract WSP violation numbers from metrics"""
        violations = []
        recommendations = metrics.get('recommendations', [])

        for rec in recommendations:
            if 'WSP' in rec:
                # Extract "WSP 62" from "WSP 62 (Modularity)"
                wsp_part = rec.split('(')[0].strip()
                violations.append(wsp_part)

        return violations[:2]  # Limit to 2 for brevity

    def _extract_line_count(self, size_label: str) -> Optional[int]:
        """Extract line count from size label"""
        import re
        match = re.search(r'(\d+)\s+lines', size_label)
        if match:
            return int(match.group(1))
        return None

    def _extract_missing_docs(self, metrics: Dict[str, Any]) -> List[str]:
        """Extract missing documentation files"""
        health_label = metrics.get('health_label', '')
        if 'Missing:' in health_label:
            # Extract from "Missing: README.md, INTERFACE.md"
            missing_part = health_label.split('Missing:')[1].strip()
            return [doc.strip() for doc in missing_part.split(',')]
        return []


class TelemetryLogger:
    """Logs structured JSON telemetry for recursive improvement"""

    def __init__(self, session_id: str = None):
        """Initialize telemetry logger

        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id or f"holo-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.log_dir = Path("holo_index/logs/telemetry")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / f"{self.session_id}.jsonl"

    def log_event(self, event_type: str, **kwargs) -> None:
        """Log a telemetry event to JSONL file

        Args:
            event_type: Type of event (e.g., 'module_status', 'doc_hint')
            **kwargs: Event-specific data
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "session": self.session_id,
            "event": event_type,
            **kwargs
        }

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event) + '\n')

    def log_module_status(self, module: str, wsp_clause: str,
                         severity: str, evidence: Dict[str, Any],
                         next_action: str = None, acknowledged: bool = False) -> None:
        """Log module health status event"""
        self.log_event(
            "module_status",
            module=module,
            wsp_clause=wsp_clause,
            severity=severity,
            evidence=evidence,
            next_action=next_action,
            acknowledged=acknowledged
        )

    def log_doc_hint(self, module: str, doc_path: str, reason: str) -> None:
        """Log documentation hint event"""
        self.log_event(
            "doc_hint",
            module=module,
            doc_path=doc_path,
            reason=reason
        )

    def log_doc_read(self, doc_path: str, duration_seconds: float = None) -> None:
        """Log documentation read event"""
        self.log_event(
            "doc_read",
            doc_path=doc_path,
            duration_seconds=duration_seconds
        )

    def log_search_request(self, query: str, code_hits: int, wsp_hits: int) -> None:
        """Log search request event"""
        self.log_event(
            "search_request",
            query=query,
            code_hits=code_hits,
            wsp_hits=wsp_hits
        )