# -*- coding: utf-8 -*-
"""
MCP Integration - HoloDAE MCP Connector Health and Activity Tracking

Extracted from holodae_coordinator.py per WSP 62 remediation.
Sprint H2: MCP integration methods (second extraction).

WSP Compliance:
- WSP 62: Modularity Enforcement (<500 lines)
- WSP 91: Structured logging for observability
- WSP 49: Module structure compliance

Usage:
    from holo_index.qwen_advisor.services.mcp_integration import MCPIntegration

    mcp = MCPIntegration(mcp_watchlist, mcp_action_log)
    mcp.show_mcp_hook_status()
    mcp.show_mcp_action_log(limit=10)
"""

from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
import logging

logger = logging.getLogger(__name__)


class MCPIntegration:
    """
    Manage MCP (Model Context Protocol) connector health and activity tracking.

    Responsibilities:
    - Track MCP-related activity for telemetry and breadcrumbs
    - Monitor MCP connector health across modules
    - Display MCP hook status and action logs for 012 oversight
    - Record MCP events for audits
    """

    def __init__(
        self,
        mcp_watchlist: List[Dict[str, Any]],
        mcp_action_log: Optional[deque] = None,
        breadcrumb_tracer: Optional[Any] = None,
        telemetry_logger: Optional[Any] = None
    ):
        """
        Initialize MCP Integration service.

        Args:
            mcp_watchlist: List of known MCP connectors to watch
            mcp_action_log: Deque for storing MCP action history (created if None)
            breadcrumb_tracer: Optional breadcrumb tracer for event tracking
            telemetry_logger: Optional telemetry logger for event logging
        """
        self.mcp_watchlist = mcp_watchlist
        self.mcp_action_log = mcp_action_log if mcp_action_log is not None else deque(maxlen=100)
        self.breadcrumb_tracer = breadcrumb_tracer
        self.telemetry_logger = telemetry_logger
        self._module_metrics_cache: Dict[str, Dict[str, Any]] = {}
        self._detailed_log = logger.debug  # Override point for coordinator's logging

    def set_module_metrics_cache(self, cache: Dict[str, Dict[str, Any]]) -> None:
        """Set reference to coordinator's module metrics cache."""
        self._module_metrics_cache = cache

    def set_metrics_collector(self, collector_fn) -> None:
        """Set function to collect module metrics (from coordinator)."""
        self._collect_module_metrics = collector_fn

    def show_mcp_hook_status(self) -> None:
        """Display MCP connector health for 012 oversight."""
        status_rows = self._collect_mcp_watch_status()
        print('\n🛰️ MCP Hook Map — Research & Platform Connectors')
        if not status_rows:
            print("No MCP-aware modules detected. Trigger ricDAE ingestion to register connectors.")
            return
        for row in status_rows:
            print(f"{row['icon']} {row['name']} ({row['priority']})")
            print(f"   Path: {row['module']}")
            print(f"   Health: {row['health']} | Size: {row['size']}")
            if row['notes']:
                for note in row['notes'][:3]:
                    print(f"   - {note}")
            print(f"   About: {row['description']}")
            print()

    def show_mcp_action_log(self, limit: int = 10) -> None:
        """Render the recent MCP activity log for 012 observers."""
        entries = list(self.mcp_action_log)[:limit]
        print('\n📡 MCP Action Log — Recent Tool Activity')
        if not entries:
            print("No MCP activity recorded. Run HoloIndex against MCP-enabled modules to generate telemetry.")
            return
        for entry in entries:
            timestamp = entry.get('timestamp', '??:??:??')
            line = f"[{timestamp}] {entry.get('event_type', 'event').upper()}"
            module = entry.get('module')
            if module:
                line += f" · {module}"
            health = entry.get('health')
            if health:
                line += f" · {health}"
            print(line)
            notes = entry.get('notes') or []
            for note in notes[:3]:
                print(f"   - {note}")
            query = entry.get('query')
            if query:
                print(f"   Query: {query}")
            print()

    def track_mcp_activity(
        self,
        query: str,
        module_metrics: Dict[str, Dict[str, Any]],
        qwen_report: str
    ) -> None:
        """
        Capture MCP-related activity for telemetry and breadcrumbs.

        Args:
            query: Search query that triggered the activity
            module_metrics: Metrics for modules affected
            qwen_report: Qwen advisor report text
        """
        events: list[tuple[str, dict]] = []

        # Collect module-level MCP events
        for module_path, metrics in module_metrics.items():
            if self._module_has_mcp_signature(module_path):
                alerts = list(metrics.get('module_alerts') or [])
                recommendations = metrics.get('recommendations') or ()
                notes = alerts + [f"Recommendation: {rec}" for rec in recommendations if rec]
                events.append((
                    'module',
                    {
                        'query': query,
                        'module': module_path,
                        'health': metrics.get('health_label'),
                        'size': metrics.get('size_label'),
                        'notes': notes,
                    },
                ))

        # Collect telemetry-level MCP events from Qwen report
        for line in qwen_report.splitlines():
            upper_line = line.upper()
            if 'MCP' in upper_line or 'RICDAE' in upper_line:
                clean_line = line.strip()
                if clean_line:
                    events.append((
                        'telemetry',
                        {
                            'query': query,
                            'notes': [clean_line],
                        },
                    ))

        # Record all collected events
        for event_type, payload in events:
            self._record_mcp_event(event_type, payload)

    def _record_mcp_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Store MCP events for telemetry, breadcrumbs, and audits."""
        timestamp = datetime.now()
        notes = payload.get('notes') or []
        if isinstance(notes, str):
            notes = [notes]

        entry = {
            'timestamp': timestamp.strftime('%H:%M:%S'),
            'timestamp_iso': timestamp.isoformat(),
            'event_type': event_type,
            'query': payload.get('query'),
            'module': payload.get('module'),
            'health': payload.get('health'),
            'size': payload.get('size'),
            'notes': notes,
        }
        self.mcp_action_log.appendleft(entry)

        # Add breadcrumb if tracer available
        preview = '; '.join(notes[:2]) if notes else ''
        breadcrumb_target = payload.get('module') or 'mcp'
        if self.breadcrumb_tracer:
            try:
                self.breadcrumb_tracer.add_action(
                    'mcp_activity',
                    breadcrumb_target,
                    preview or 'MCP event captured',
                    payload.get('query', 'n/a')
                )
            except Exception:
                pass

        # Log to telemetry if logger available
        if self.telemetry_logger:
            try:
                self.telemetry_logger.log_event(
                    'mcp_action',
                    timestamp=entry['timestamp_iso'],
                    event_type=event_type,
                    module=entry.get('module'),
                    health=entry.get('health'),
                    size=entry.get('size'),
                    notes=notes,
                    query=entry.get('query'),
                )
            except Exception as exc:
                self._detailed_log(f"[HOLODAE-MCP] Telemetry logging failed: {exc}")

    def _collect_mcp_watch_status(self) -> List[Dict[str, Any]]:
        """Collect status data for known and detected MCP connectors."""
        status_rows: List[Dict[str, Any]] = []
        seen_modules: set[str] = set()

        # Collect status for known watchlist items
        for item in self.mcp_watchlist:
            metrics = self._collect_module_metrics(item['module'])
            status_rows.append(self._build_mcp_status_row(item, metrics))
            seen_modules.add(item['module'])

        # Detect and collect status for dynamically discovered MCP modules
        for module_path in list(self._module_metrics_cache.keys()):
            if module_path in seen_modules:
                continue
            if self._module_has_mcp_signature(module_path):
                metrics = self._collect_module_metrics(module_path)
                dynamic_item = {
                    'name': module_path,
                    'module': module_path,
                    'description': 'Detected MCP signature',
                    'priority': 'P?'
                }
                status_rows.append(self._build_mcp_status_row(dynamic_item, metrics))
                seen_modules.add(module_path)

        status_rows.sort(key=lambda row: row['name'])
        return status_rows

    def _build_mcp_status_row(self, item: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Build a status row for MCP connector display."""
        health = metrics.get('health_label', '[UNKNOWN]')
        size = metrics.get('size_label', '[UNKNOWN]')
        notes = list(metrics.get('module_alerts') or [])
        recommendations = metrics.get('recommendations') or ()
        notes.extend(recommendations)

        return {
            'name': item.get('name', item.get('module', 'MCP Connector')),
            'module': item.get('module', ''),
            'description': item.get('description', 'Detected MCP signature'),
            'priority': item.get('priority', 'P?'),
            'health': health,
            'size': size,
            'notes': notes,
            'icon': self._derive_health_icon(health),
        }

    def _derive_health_icon(self, health_label: str) -> str:
        """Derive an icon based on health status label."""
        label = (health_label or '').upper()
        if 'MISSING' in label or 'CRITICAL' in label:
            return '🔴'
        if 'WARN' in label:
            return '🟡'
        if 'COMPLETE' in label or 'OK' in label:
            return '🟢'
        return '🔹'

    def _module_has_mcp_signature(self, module_path: str) -> bool:
        """Check if a module has MCP-related signature."""
        if not module_path:
            return False

        lowered = module_path.lower()
        if 'mcp' in lowered or 'ric_dae' in lowered:
            return True

        # Check against watchlist
        for item in self.mcp_watchlist:
            if lowered.startswith(item['module'].lower()):
                return True

        return False

    def _collect_module_metrics(self, module_path: str) -> Dict[str, Any]:
        """
        Placeholder for module metrics collection.
        Should be overridden by coordinator via set_metrics_collector().
        """
        return self._module_metrics_cache.get(module_path, {})
