#!/usr/bin/env python3
"""
QwenOrchestrator - Primary orchestrator for HoloDAE intelligence system

This is the Qwen LLM orchestration layer that coordinates all HoloIndex components.
Qwen acts as the "circulatory system" - continuously analyzing and orchestrating operations,
then presenting findings to 0102 for arbitration.

WSP Compliance: WSP 80 (Cube-Level DAE Orchestration)
"""

import logging
import os
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional


COMPONENT_META = {
    'health_analysis': ('💊✅', 'Health & WSP Compliance'),
    'vibecoding_analysis': ('🧠', 'Vibecoding Analysis'),
    'file_size_monitor': ('📏', 'File Size Monitor'),
    'module_analysis': ('📦', 'Module Analysis'),
    'pattern_coach': ('🧠', 'Pattern Coach'),
    'orphan_analysis': ('👻', 'Orphan Analysis'),
    'wsp_documentation_guardian': ('📚', 'WSP Documentation Guardian'),
}

# WSP Documentation Guardian Configuration
WSP_DOC_CONFIG = {
    'doc_only_modules': {
        'holo_index/docs',
        'WSP_framework/docs',
        'WSP_framework/historic_assets',
        'WSP_framework/reports/legacy',
    },
    'expected_update_intervals_days': {
        'README.md': 90,  # Quarterly updates
        'ModLog.md': 30,  # Monthly updates (tracking changes)
        'requirements.txt': 30,  # Monthly dependency updates
        'INTERFACE.md': 60,  # Bi-monthly API changes
        'ROADMAP.md': 30,  # Monthly planning updates
    },
    'auto_remediate_ascii': False,  # Default to read-only mode - remediation opt-in
    'remediation_log_path': 'WSP_framework/docs/WSP_ASCII_REMEDIATION_LOG.md',
    'backup_temp_dir': 'temp/wsp_backups',  # Store backups in temp directory
}

class QwenOrchestrator:
    """Primary orchestrator for HoloDAE - Qwen's decision-making and coordination layer"""

    def __init__(self) -> None:
        """Initialize the Qwen orchestrator"""
        self._ensure_utf8_console()
        self.logger = logging.getLogger('holodae_activity')
        self.chain_of_thought_log: List[Dict[str, Any]] = []
        self.performance_history: List[float] = []
        self._last_files: List[str] = []
        self._last_modules: List[str] = []
        self._last_executed_components: List[str] = []
        self.repo_root = Path(__file__).resolve().parents[3]

        # Initialize QWEN filtering attributes
        self._intent_filters = {}
        self._intent_keywords = {}
        self._max_suggestions = 10
        self._deduplicate_alerts = False

    def _format_component_display(self, component_name: str) -> str:
        emoji, label = COMPONENT_META.get(component_name, ('', component_name.replace('_', ' ').title()))
        return f"{emoji} {label}".strip()

    def _ensure_utf8_console(self) -> None:
        if os.name != 'nt':
            return
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            if kernel32.GetConsoleOutputCP() != 65001:
                kernel32.SetConsoleOutputCP(65001)
            if kernel32.GetConsoleCP() != 65001:
                kernel32.SetConsoleCP(65001)
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            if hasattr(sys.stderr, 'reconfigure'):
                sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

    def orchestrate_monitoring(self, work_context):
        """Handle monitoring orchestration for autonomous HoloDAE"""
        # Create a monitoring result object with expected attributes for self-improvement
        class MonitoringResult:
            def __init__(self, active_files=0, task_pattern='monitoring'):
                self.violations_found = []
                self.optimization_suggestions = []
                self.pattern_alerts = []
                self.active_files_count = active_files
                self.task_pattern = task_pattern
                self.timestamp = datetime.now().isoformat()
                self.status = 'monitoring_complete'

        active_files = len(work_context.active_files) if hasattr(work_context, 'active_files') else 0
        task_pattern = getattr(work_context, 'task_pattern', 'monitoring')

        return MonitoringResult(active_files, task_pattern)

    def orchestrate_holoindex_request(self, query: str, search_results: Dict[str, Any]) -> str:
        """Handle incoming HoloIndex request with chain-of-thought orchestration"""
        involved_files = self._extract_files_from_results(search_results)
        involved_modules = self._extract_modules_from_files(involved_files)

        # Persist context for coordinator integration
        self._last_files = involved_files.copy()
        self._last_modules = involved_modules.copy()

        # Log the orchestration initiation
        self._log_chain_of_thought("INIT", f"Processing HoloIndex query: '{query}'")
        self._log_chain_of_thought(
            "CONTEXT",
            f"Found {len(involved_files)} files across {len(involved_modules)} modules",
        )

        if not involved_files:
            self._log_chain_of_thought("DECISION", "No files to analyze - returning early")
            return "[HOLODAE-ANALYZE] No files found to analyze"

        context = self._build_orchestration_context(query, involved_files, involved_modules)

        # NEW: QWEN-CONTROLLED OUTPUT: Filter based on intent before any processing
        intent = context.get("query_intent", "standard")
        output_filter = self._get_output_filter_for_intent(intent)

        # Log detected intent (always shown for transparency)
        if intent == "fix_error":
            self._log_chain_of_thought("INTENT", "🔧 Error fixing mode - minimizing health checks")
        elif intent == "locate_code":
            self._log_chain_of_thought("INTENT", "📍 Code location mode - focused output")
        elif intent == "explore":
            self._log_chain_of_thought("INTENT", "🔍 Exploration mode - full analysis")

        # Get orchestration decisions and filter based on intent
        raw_decisions = self._get_orchestration_decisions(context)
        orchestration_decisions = self._filter_orchestration_decisions(raw_decisions, output_filter)

        # Execute analysis with filtered output
        analysis_report = self._execute_orchestrated_analysis_filtered(
            query, involved_files, involved_modules, orchestration_decisions, output_filter
        )

        # Calculate effectiveness (filtered logging)
        effectiveness = self._calculate_analysis_effectiveness(analysis_report)
        self.performance_history.append(effectiveness)
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]

        if output_filter["show_performance_logs"]:
            self._log_chain_of_thought("EFFECTIVENESS", f"Analysis effectiveness: {effectiveness:.2f}")

        # Return intent-aware formatted response
        return self._format_intent_aware_response(intent, analysis_report)

    def _get_output_filter_for_intent(self, intent: str) -> Dict[str, bool]:
        """
        NEW: QWEN-controlled output filtering based on query intent.

        Reduces noise by only showing relevant information for each intent type.
        """
        filters = {
            "fix_error": {
                "show_init_logs": False,        # Don't show processing details
                "show_decision_logs": False,   # Don't show orchestration decisions
                "show_performance_logs": False, # Don't show effectiveness metrics
                "show_health_checks": False,   # Don't show health analysis
                "show_module_metrics": False,  # Don't show module health
                "show_detailed_analysis": False, # Focus on error solution only
                "show_file_details": True,     # Show file locations for fixes
                "compact_format": True         # Use compact output format
            },
            "locate_code": {
                "show_init_logs": False,        # Minimal processing details
                "show_decision_logs": False,   # No orchestration noise
                "show_performance_logs": False, # No metrics
                "show_health_checks": False,   # No health analysis
                "show_module_metrics": False,  # No module details
                "show_detailed_analysis": False, # Just location info
                "show_file_details": True,     # Show exact file locations
                "compact_format": True         # Clean, focused output
            },
            "explore": {
                "show_init_logs": True,         # Show exploration context
                "show_decision_logs": True,    # Show analysis decisions
                "show_performance_logs": True, # Show effectiveness
                "show_health_checks": True,    # Show health analysis
                "show_module_metrics": True,   # Show module details
                "show_detailed_analysis": True, # Full analysis
                "show_file_details": True,     # Show file details
                "compact_format": False        # Full detailed format
            },
            "wsp_manage": {
                "show_init_logs": False,        # Surgical - no processing noise
                "show_decision_logs": False,   # Focus on WSP status only
                "show_performance_logs": False, # No performance metrics
                "show_health_checks": False,   # No general health - WSP specific
                "show_module_metrics": False,  # No module noise - WSP compliance only
                "show_detailed_analysis": True, # Show WSP compliance details
                "show_file_details": True,     # Show WSP file locations
                "compact_format": True         # Clean, focused WSP format
            },
            "standard": {
                "show_init_logs": False,        # Minimal init logs
                "show_decision_logs": True,    # Show key decisions
                "show_performance_logs": False, # No performance noise
                "show_health_checks": False,   # No health unless requested
                "show_module_metrics": False,  # No module noise
                "show_detailed_analysis": True, # Show analysis
                "show_file_details": True,     # Show files
                "compact_format": False        # Standard format
            }
        }

        return filters.get(intent, filters["standard"])

    def _format_intent_aware_response(self, intent: str, analysis_report: str) -> str:
        """
        NEW: Format response based on query intent for optimal 0102 consumption.

        Different intents get different output formats optimized for their use case.
        """
        if intent == "fix_error":
            # Ultra-compact format for error fixing - just the essentials
            lines = analysis_report.split('\n')
            essential_lines = []

            for line in lines:
                # Keep only critical information
                if any(keyword in line.lower() for keyword in [
                    'error', 'fix', 'solution', 'line', 'file:', 'function',
                    'traceback', 'exception', 'bug', 'issue'
                ]):
                    essential_lines.append(line)

            if essential_lines:
                return "🔧 ERROR SOLUTION:\n" + '\n'.join(essential_lines[:5])  # Limit to 5 lines
            else:
                return "🔧 ERROR FIXING MODE: Focus on error resolution"

        elif intent == "locate_code":
            # Location-focused format
            lines = analysis_report.split('\n')
            location_lines = []

            for line in lines:
                # Keep location and file information
                if any(keyword in line.lower() for keyword in [
                    'file:', 'line', 'function', 'class', 'def ', 'path:',
                    'location', 'module', 'in file'
                ]):
                    location_lines.append(line)

            if location_lines:
                return "📍 CODE LOCATION:\n" + '\n'.join(location_lines[:3])  # Limit to 3 lines
            else:
                return "📍 CODE LOCATION MODE: Focus on file and function locations"

        elif intent == "explore":
            # Full analysis for exploration
            return "🔍 EXPLORATION ANALYSIS:\n" + analysis_report

        elif intent == "wsp_manage":
            # Surgical WSP documentation management - focus on compliance
            lines = analysis_report.split('\n')
            wsp_lines = []

            for line in lines:
                # Keep only WSP-related compliance information
                if any(keyword in line.lower() for keyword in [
                    'wsp-guardian', 'compliance', 'documentation', 'readme', 'modlog',
                    'ascii', 'stale', 'outdated', 'violation', 'status'
                ]):
                    wsp_lines.append(line)

            if wsp_lines:
                return "📚 WSP DOCUMENTATION STATUS:\n" + '\n'.join(wsp_lines[:5])  # Limit to 5 lines
            else:
                return "📚 WSP MANAGEMENT MODE: Focus on documentation compliance and updates"

        else:
            # Standard format with some filtering
            lines = analysis_report.split('\n')

            # Remove excessive technical details
            filtered_lines = []
            skip_patterns = [
                'holodae-health', 'holodae-analyze', 'holodae-telemetry',
                'effectiveness:', 'processing', 'orchestration'
            ]

            for line in lines:
                if not any(pattern in line.lower() for pattern in skip_patterns):
                    filtered_lines.append(line)

            return '\n'.join(filtered_lines) if filtered_lines else analysis_report

    def _filter_orchestration_decisions(self, decisions: List[Dict[str, Any]], output_filter: Dict[str, bool]) -> List[Dict[str, Any]]:
        """
        NEW: Filter orchestration decisions based on QWEN output filter
        """
        if not output_filter:
            return decisions

        # Filter out components based on intent
        filtered_decisions = []
        for decision in decisions:
            component = decision.get('component', '')

            # Skip health checks for error/locator intents
            if not output_filter.get("show_health_checks", True):
                if 'health' in component.lower():
                    continue

            # Skip module analysis for simple queries
            if not output_filter.get("show_module_metrics", True):
                if 'module' in component.lower():
                    continue

            filtered_decisions.append(decision)

        return filtered_decisions

    def _execute_orchestrated_analysis_filtered(self, query: str, files: List[str], modules: List[str],
                                               orchestration_decisions: List[Dict[str, Any]],
                                               output_filter: Dict[str, bool] = None) -> str:
        """
        Enhanced with QWEN output filtering during execution
        """
        # Use existing method
        report = self._execute_orchestrated_analysis(query, files, modules, orchestration_decisions)

        if output_filter and output_filter.get("compact_format", False):
            # Apply compact formatting
            lines = report.split('\n')
            compact_lines = []

            # Keep headers and essential info, skip noise
            for line in lines:
                # Skip noisy technical details
                if any(noise in line.lower() for noise in [
                    'holodae-', 'orchestration', 'processing', 'telemetry',
                    'effectiveness', 'chain-of-thought'
                ]):
                    continue

                # Keep important information
                if line.strip() and len(line.strip()) > 10:  # Meaningful content
                    compact_lines.append(line)

            return '\n'.join(compact_lines[:10]) if compact_lines else report  # Limit output

        return report

    def get_recent_analysis_context(self) -> Dict[str, List[str]]:
        """Return the most recent file/module context analyzed by Qwen"""
        return {'files': self._last_files.copy(), 'modules': self._last_modules.copy()}

    def get_recent_execution_summary(self) -> Dict[str, Any]:
        """Return latest executed component list for downstream consumers"""
        return {'executed_components': self._last_executed_components.copy()}

    def _extract_files_from_results(self, search_results: Dict[str, Any]) -> List[str]:
        """Extract file paths from HoloIndex search results"""
        files: List[str] = []
        for category in ('code', 'wsps'):
            hits = search_results.get(category) or []
            for hit in hits:
                file_path: Optional[str] = None
                if category == 'code':
                    file_path = hit.get('location')
                else:
                    file_path = hit.get('path')
                if file_path and file_path not in files:
                    files.append(file_path)
        return files

    def _extract_modules_from_files(self, files: List[str]) -> List[str]:
        """Extract module names from file paths"""
        modules: set[str] = set()
        for file_path in files:
            module = self._extract_module_from_path(file_path)
            if module:
                modules.add(module)
        return list(modules)

    def _extract_module_from_path(self, file_path: str) -> Optional[str]:
        """Extract module name from file path"""
        path_parts = Path(file_path).parts
        if 'modules' in path_parts:
            try:
                idx = path_parts.index('modules')
                if idx + 2 < len(path_parts):
                    return f"modules/{path_parts[idx + 1]}/{path_parts[idx + 2]}"
            except ValueError:
                pass
        if 'holo_index' in path_parts:
            try:
                idx = path_parts.index('holo_index')
                if idx + 1 < len(path_parts):
                    return f"holo_index/{path_parts[idx + 1]}"
            except ValueError:
                pass
        return None

    def _detect_query_intent(self, query: str) -> str:
        """Detect the primary intent of the query for smarter output"""
        lower_query = query.lower()

        # Error fixing takes priority - no health checks needed
        error_keywords = ['error', 'exception', 'traceback', 'fix', 'bug', 'crash',
                         'nonetype', 'attribute', 'failed', 'broken']
        if any(kw in lower_query for kw in error_keywords):
            return "fix_error"

        # WSP documentation management takes precedence - surgical WSP compliance checking
        wsp_keywords = ['wsp', 'windsurf', 'protocol', 'compliance', 'documentation', 'readme', 'modlog']
        if any(kw in lower_query for kw in wsp_keywords):
            return "wsp_manage"

        # Code location request - minimal output
        locate_keywords = ['where', 'find', 'location', 'which file', 'line']
        if any(kw in lower_query for kw in locate_keywords):
            return "locate_code"

        # Regex patterns indicate code search - treat as locate_code for surgical output
        if '.*' in query or '|' in query or '\\' in query or '[' in query:
            return "locate_code"

        # Module exploration - show health
        explore_keywords = ['module', 'structure', 'architecture', 'health', 'status']
        if any(kw in lower_query for kw in explore_keywords):
            return "explore"

        # Default to standard
        return "standard"

    def _build_orchestration_context(
        self,
        query: str,
        files: List[str],
        modules: List[str],
    ) -> Dict[str, Any]:
        """Build context dictionary for orchestration decisions"""
        lower_query = query.lower()
        intent = self._detect_query_intent(query)

        # Only check health if intent is exploration or explicitly requested
        should_check_health = (intent == "explore" or
                              'health' in lower_query or
                              'audit' in lower_query)

        return {
            "query": query,
            "query_intent": intent,
            "files_count": len(files),
            "modules_count": len(modules),
            "query_keywords": lower_query.split(),
            "is_search_request": True,
            "has_files": bool(files),
            "has_modules": bool(modules),
            "query_contains_health": should_check_health,  # Smart detection based on intent
            "query_contains_vibecoding": any(kw in lower_query for kw in ['vibe', 'pattern', 'behavior', 'coach']),
            "query_contains_module": any(kw in lower_query for kw in ['module', 'create', 'refactor']),
            "query_contains_error": any(kw in lower_query for kw in ['error', 'fix', 'debug', 'issue']),
            "query_contains_wsp": any(kw in lower_query for kw in ['wsp', 'windsurf', 'protocol', 'compliance', 'documentation']),
        }

    def _get_orchestration_decisions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get orchestration decisions from performance orchestrator"""
        available_components = {
            "health_analysis": {
                "purpose": "Check system integrity and WSP compliance",
                "triggers": ["query_contains_health", "has_modules"],
                "cost": "medium",
                "value": "high",
                "skip_for_intents": ["fix_error", "locate_code"],  # Skip when locating code
            },
            "vibecoding_analysis": {
                "purpose": "Detect behavioral vibecoding patterns",
                "triggers": ["query_contains_vibecoding", "has_files"],
                "cost": "low",
                "value": "high",
                "skip_for_intents": ["fix_error", "locate_code"],  # Skip when locating code
            },
            "file_size_monitor": {
                "purpose": "Monitor for architectural bloat",
                "triggers": ["query_contains_module", "has_files"],
                "cost": "low",
                "value": "medium",
                "skip_for_intents": ["fix_error", "locate_code"],  # Skip when fixing errors or locating code
            },
            "module_analysis": {
                "purpose": "Validate module structure and dependencies",
                "triggers": ["has_modules", "query_contains_module"],
                "cost": "medium",
                "value": "high",
                "skip_for_intents": ["fix_error", "locate_code"],  # Skip when locating code
            },
            "pattern_coach": {
                "purpose": "Prevent behavioral vibecoding through coaching",
                "triggers": ["has_files", "query_contains_vibecoding"],
                "cost": "low",
                "value": "medium",
                "skip_for_intents": ["fix_error", "locate_code"],  # Skip when locating code
            },
            "orphan_analysis": {
                "purpose": "Find dead code and connection opportunities",
                "triggers": ["query_contains_health", "has_modules"],
                "cost": "high",
                "value": "medium",
                "skip_for_intents": ["fix_error", "locate_code"],  # Skip when locating code
            },
            "wsp_documentation_guardian": {
                "purpose": "Monitor WSP documentation compliance and freshness",
                "triggers": ["has_files", "query_contains_wsp"],
                "cost": "medium",
                "value": "high",
                "skip_for_intents": [],  # Always run for WSP-related queries
            },
        }

        decisions: List[Dict[str, Any]] = []
        for component_name, component_info in available_components.items():
            # Skip components based on intent
            if "skip_for_intents" in component_info:
                if context.get("query_intent") in component_info["skip_for_intents"]:
                    continue  # Skip this component entirely

            should_execute = False
            confidence = 0.5
            reasoning: List[str] = []
            for trigger in component_info["triggers"]:
                if context.get(trigger, False):
                    should_execute = True
                    confidence += 0.2
                    reasoning.append(f"triggered by {trigger}")
            # Skip expensive operations for error fixing
            if context.get("query_intent") == "fix_error" and component_info["cost"] == "high":
                confidence -= 0.3  # Strongly discourage expensive ops when fixing errors
            elif component_info["cost"] == "high" and not context.get("query_contains_health"):
                confidence -= 0.1
            display_name = self._format_component_display(component_name)
            if should_execute and confidence >= 0.6:
                decisions.append(
                    {
                        "component_name": component_name,
                        "decision_type": "execute",
                        "confidence_score": confidence,
                        "reasoning_chain": reasoning,
                        "purpose": component_info["purpose"],
                    }
                )
                self._log_chain_of_thought(
                    "DECISION",
                    f"EXECUTE {display_name} (confidence: {confidence:.2f}) - {', '.join(reasoning)}",
                )
            else:
                self._log_chain_of_thought(
                    "DECISION",
                    f"SKIP {display_name} (confidence: {confidence:.2f}) - insufficient trigger strength",
                )
        return decisions

    def _execute_orchestrated_analysis(
        self,
        query: str,
        files: List[str],
        modules: List[str],
        decisions: List[Dict[str, Any]],
    ) -> str:
        """Execute the orchestrated analysis components."""
        report_lines: List[str] = [f"[HOLODAE-INTELLIGENCE] Data-driven analysis for query: '{query}'"]
        unique_modules = sorted({module for module in modules if module})
        module_snapshots = {module: self._build_module_snapshot(module) for module in unique_modules}
        report_lines.append(
            f"[SEMANTIC] {len(files)} files across {len(unique_modules)} modules"
        )

        if not unique_modules:
            report_lines.append("[HOLODAE-CONTEXT] No module directories resolved from search results")

        executed_components: List[str] = []
        for decision in decisions:
            component_name = decision["component_name"]
            display_name = self._format_component_display(component_name)
            results = self._execute_component_stub(
                component_name, query, files, unique_modules, module_snapshots
            )
            if results:
                executed_components.append(display_name)
                report_lines.extend(results)
                self._log_chain_of_thought("PERFORMANCE", f"{display_name} executed with results")

        self._last_executed_components = executed_components
        if executed_components:
            report_lines.append(
                f"[HOLODAE-ORCHESTRATION] Executed components: {', '.join(executed_components)}"
            )
        else:
            report_lines.append(
                "[HOLODAE-ORCHESTRATION] No components produced actionable output"
            )
        return '\n'.join(report_lines)

    def _execute_component_stub(
        self,
        component_name: str,
        query: str,
        files: List[str],
        modules: List[str],
        module_snapshots: Dict[str, Dict[str, Any]],
    ) -> List[str]:
        """Execute a named analysis component using lightweight heuristics."""
        if component_name == "health_analysis":
            return self._run_health_analysis(module_snapshots)
        if component_name == "vibecoding_analysis":
            return self._run_vibecoding_analysis(module_snapshots)
        if component_name == "file_size_monitor":
            return self._run_file_size_monitor(files, module_snapshots)
        if component_name == "module_analysis":
            return self._run_module_analysis(module_snapshots)
        if component_name == "pattern_coach":
            return self._run_pattern_coach(module_snapshots)
        if component_name == "orphan_analysis":
            return self._run_orphan_analysis(module_snapshots)
        if component_name == "wsp_documentation_guardian":
            return self._run_wsp_documentation_guardian(query, files, modules, module_snapshots)
        return []

    def _run_health_analysis(self, module_snapshots: Dict[str, Dict[str, Any]]) -> List[str]:
        if not module_snapshots:
            return ["[HEALTH][OK] No modules to audit in current query"]
        lines: List[str] = []
        for module, snapshot in module_snapshots.items():
            if not snapshot['exists']:
                lines.append(f"[HEALTH][WARNING] FOUND missing module on disk: {module}")
                continue
            missing_docs = snapshot['missing_docs']
            if missing_docs:
                lines.append(
                    f"[HEALTH][VIOLATION] {module} missing {', '.join(missing_docs)} (WSP 22)"
                )
            else:
                lines.append(f"[HEALTH][OK] {module} documentation complete")
        return lines

    def _run_vibecoding_analysis(self, module_snapshots: Dict[str, Dict[str, Any]]) -> List[str]:
        lines: List[str] = []
        for module, snapshot in module_snapshots.items():
            if not snapshot['exists']:
                continue
            py_count = snapshot['py_file_count']
            tests = snapshot['test_count']
            if py_count == 0:
                continue
            coverage = tests / py_count
            if tests == 0 and py_count >= 3:
                lines.append(
                    f"[PATTERN] Found {py_count} implementation files with 0 tests in {module} (coverage 0%)"
                )
            elif coverage < 0.2 and py_count >= 5:
                lines.append(
                    f"[PATTERN] Low coverage {coverage:.0%} in {module} ({tests} tests across {py_count} files)"
                )
        if not lines:
            lines.append("[VIBECODING-PATTERN] No high-risk vibecoding patterns detected")
        return lines

    def _run_file_size_monitor(
        self,
        files: List[str],
        module_snapshots: Dict[str, Dict[str, Any]],
    ) -> List[str]:
        lines: List[str] = []
        flagged: set[str] = set()
        for snapshot in module_snapshots.values():
            if not snapshot['exists']:
                continue
            for py_file, line_count, size_kb in snapshot['large_python_files']:
                rel = self._relative_path(py_file)
                if rel in flagged:
                    continue
                lines.append(
                    f"[SIZE][WARNING] FOUND large file {rel} ({line_count} lines, {size_kb} KB)"
                )
                flagged.add(rel)
        for file_path in files:
            resolved = self._resolve_file_path(file_path)
            if not resolved or not resolved.exists():
                continue
            rel = self._relative_path(resolved)
            if rel in flagged:
                continue
            size_kb = max(1, resolved.stat().st_size // 1024)
            if resolved.suffix == '.py':
                line_count = self._count_file_lines(resolved)
                if line_count > 400 or size_kb > 120:
                    lines.append(
                        f"[SIZE][WARNING] FOUND large file {rel} ({line_count} lines, {size_kb} KB)"
                    )
                    flagged.add(rel)
            elif size_kb > 256:
                lines.append(
                    f"[SIZE][NOTICE] FOUND large artifact {rel} ({size_kb} KB)"
                )
                flagged.add(rel)
        if not lines:
            lines.append("[HOLODAE-SIZE][OK] No file size anomalies detected")
        return lines

    def _run_module_analysis(self, module_snapshots: Dict[str, Dict[str, Any]]) -> List[str]:
        lines: List[str] = []
        for module, snapshot in module_snapshots.items():
            if not snapshot['exists']:
                continue
            py_count = snapshot['py_file_count']
            tests = snapshot['test_count']
            lines.append(
                f"[MODULE][FOUND] {module} contains {py_count} python files with {tests} tests"
            )
            if snapshot['missing_docs']:
                lines.append(
                    f"[MODULE][WARNING] {module} missing {', '.join(snapshot['missing_docs'])}"
                )
            if snapshot['large_python_files']:
                rel = self._relative_path(snapshot['large_python_files'][0][0])
                lines.append(
                    f"[MODULE][WARNING] Large implementation file detected: {rel}"
                )
        if not lines:
            lines.append("[HOLODAE-MODULE][OK] Modules within healthy structural bounds")
        return lines

    def _run_pattern_coach(self, module_snapshots: Dict[str, Dict[str, Any]]) -> List[str]:
        lines: List[str] = []
        for module, snapshot in module_snapshots.items():
            if not snapshot['exists']:
                continue
            if snapshot['missing_docs']:
                lines.append(
                    f"[PATTERN] Found documentation gap in {module}: {', '.join(snapshot['missing_docs'])}"
                )
            if snapshot['script_orphans']:
                samples = ', '.join(
                    self._relative_path(path) for path in snapshot['script_orphans'][:2]
                )
                lines.append(
                    f"[PATTERN] Found {len(snapshot['script_orphans'])} scripts lacking tests in {module}: {samples}"
                )
        if not lines:
            lines.append("[PATTERN-COACH] Patterns stable - no interventions required")
        return lines

    def _run_orphan_analysis(self, module_snapshots: Dict[str, Dict[str, Any]]) -> List[str]:
        lines: List[str] = []
        for module, snapshot in module_snapshots.items():
            if not snapshot['exists']:
                continue
            orphans = snapshot['script_orphans']
            for orphan in orphans[:3]:
                rel = self._relative_path(orphan)
                lines.append(f"[ORPHAN-FOUND] {rel} lacks matching tests - investigate connection")
            if len(orphans) > 3:
                lines.append(
                    f"[ORPHAN-SUMMARY] {len(orphans)} potential orphan scripts detected in {module}"
                )
        if not lines:
            lines.append("[ORPHAN-ANALYSIS][OK] No orphaned scripts identified")
        return lines

    def _run_wsp_documentation_guardian(
        self,
        query: str,
        files: List[str],
        modules: List[str],
        module_snapshots: Dict[str, Dict[str, Any]],
        remediation_mode: bool = False
    ) -> List[str]:
        """
        WSP Documentation Guardian - Enhanced First Principles Implementation

        QWEN FIRST PRINCIPLES APPLIED:
        1. Understand Context - Detect WSP-related queries vs code queries
        2. Surgical Filtering - Show only relevant WSP compliance info
        3. Remove Corruption - Auto-sanitize ASCII violations (WSP 20)
        4. Focus on Essence - Show current compliance status and missing docs
        5. Continuous Learning - Log all WSP compliance checks and improvements

        ENHANCED FEATURES:
        - Doc-only exemption map integration
        - Config-driven update intervals
        - Automatic ASCII remediation
        - ModLog remediation tracking
        """
        lines: List[str] = []
        wsp_related_files = []
        wsp_framework_docs = []
        remediation_actions = []

        # Load WSP configuration
        config = WSP_DOC_CONFIG

        # Index WSP documentation from framework and modules
        for file_path in files:
            if 'wsp' in file_path.lower() or 'WSP' in file_path:
                wsp_related_files.append(file_path)

        # Check WSP framework documentation with smart exemptions
        wsp_framework_path = self.repo_root / "WSP_framework"
        if wsp_framework_path.exists():
            for md_file in wsp_framework_path.rglob("*.md"):
                file_path_str = str(md_file)
                wsp_framework_docs.append(file_path_str)

                # Skip doc-only modules for freshness checks
                rel_path = self._relative_path(md_file)
                is_doc_only = self._is_doc_only_path(rel_path, config['doc_only_modules'])

                if not is_doc_only:
                    # Check modification date with config-driven intervals
                    file_name = md_file.name
                    expected_interval = config['expected_update_intervals_days'].get(file_name, 90)  # Default quarterly

                    modlog_path = md_file.parent / "ModLog.md"
                    doc_mtime = md_file.stat().st_mtime
                    days_since_update = (datetime.now().timestamp() - doc_mtime) / 86400

                    if days_since_update > expected_interval:
                        lines.append(f"[WSP-GUARDIAN][STALE-WARNING] {rel_path} not updated in {days_since_update:.0f} days (expected: {expected_interval}d)")
                        # Note: Stale docs are warnings only - not added to remediation_actions
                        # Remediation_actions are reserved for actual file modifications
                    elif modlog_path.exists():
                        modlog_mtime = modlog_path.stat().st_mtime
                        if modlog_mtime < doc_mtime:
                            lines.append(f"[WSP-GUARDIAN][OUTDATED] {self._relative_path(modlog_path)} older than document")

        # Check module WSP compliance
        wsp_compliant_modules = 0
        total_modules = 0

        for module in modules:
            if module and module_snapshots.get(module, {}).get('exists'):
                total_modules += 1
                snapshot = module_snapshots[module]
                missing_docs = snapshot.get('missing_docs', [])

                # Check for required WSP documentation
                required_wsp_docs = ['README.md', 'ModLog.md']
                missing_wsp_docs = [doc for doc in missing_docs if doc in required_wsp_docs]

                if not missing_wsp_docs:
                    wsp_compliant_modules += 1
                else:
                    lines.append(f"[WSP-GUARDIAN][VIOLATION] {module} missing WSP docs: {', '.join(missing_wsp_docs)}")

        if total_modules > 0:
            compliance_rate = wsp_compliant_modules / total_modules
            lines.append(f"[WSP-GUARDIAN][STATUS] WSP compliance: {wsp_compliant_modules}/{total_modules} modules ({compliance_rate:.1%})")

        # ASCII compliance check with conditional remediation
        ascii_violations = []
        ascii_remediated = []

        for file_path in wsp_related_files + wsp_framework_docs:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                if any(ord(c) > 127 for c in content):
                    rel_path = self._relative_path(file_path)
                    ascii_violations.append(rel_path)

                    # Conditionally remediate based on mode
                    if remediation_mode:
                        sanitized_content = self._sanitize_ascii_content(content)
                        if sanitized_content != content:
                            # Create backup in temp directory
                            backup_dir = self.repo_root / config['backup_temp_dir']
                            backup_dir.mkdir(parents=True, exist_ok=True)
                            backup_filename = Path(file_path).name + '.backup'
                            backup_path = backup_dir / backup_filename

                            # Only backup if we haven't already
                            if not backup_path.exists():
                                with open(backup_path, 'w', encoding='utf-8') as f:
                                    f.write(content)

                            # Write sanitized version
                            with open(file_path, 'w', encoding='ascii', errors='replace') as f:
                                f.write(sanitized_content)

                            ascii_remediated.append(rel_path)
                            remediation_actions.append(f"Auto-sanitized ASCII violations in {rel_path}")
                            self.logger.info(f"[WSP-GUARDIAN] Auto-sanitized ASCII in {rel_path}")

            except Exception as e:
                self.logger.warning(f"[WSP-GUARDIAN] Error checking ASCII in {file_path}: {e}")
                continue

        # Report ASCII status (always show violations, only show fixes if in remediation mode)
        if ascii_violations:
            violation_count = len(ascii_violations)
            if remediation_mode:
                remediated_count = len(ascii_remediated)
                lines.append(f"[WSP-GUARDIAN][ASCII] {violation_count} files had violations, {remediated_count} auto-remediated")
            else:
                lines.append(f"[WSP-GUARDIAN][ASCII-WARNING] {violation_count} files have non-ASCII characters (use --fix-ascii to remediate)")
                lines.append(f"[WSP-GUARDIAN][ASCII-VIOLATION] Non-ASCII chars in: {', '.join(ascii_violations[:3])}")

        # Execute remediation pipeline only if we actually made changes
        if remediation_actions and remediation_mode:
            self._execute_wsp_remediation_pipeline(remediation_actions, config)

        # Log all WSP compliance checks for continuous learning
        self.logger.info(f"[WSP-GUARDIAN] Checked {len(wsp_related_files)} WSP files, {len(wsp_framework_docs)} framework docs")
        self.logger.info(f"[WSP-GUARDIAN] Compliance rate: {wsp_compliant_modules}/{total_modules}")
        if ascii_violations:
            self.logger.warning(f"[WSP-GUARDIAN] ASCII violations found: {len(ascii_violations)}, remediated: {len(ascii_remediated)}")

        return lines if lines else ["[WSP-GUARDIAN][OK] All WSP documentation compliant and up-to-date"]

    def _is_doc_only_path(self, rel_path: str, doc_only_modules: set) -> bool:
        """Check if path is in doc-only exemption map to prevent false stale alerts."""
        path_parts = Path(rel_path).parts

        # Check if any parent directory is doc-only
        for i in range(len(path_parts)):
            check_path = '/'.join(path_parts[:i+1])
            if check_path in doc_only_modules:
                return True

        return False

    def _sanitize_ascii_content(self, content: str) -> str:
        """
        Sanitize content to ASCII-only, replacing non-ASCII characters with safe alternatives.
        WSP 20 Compliance: Remove corruption while preserving readability.
        """
        sanitized = []
        for char in content:
            if ord(char) <= 127:
                sanitized.append(char)
            else:
                # Replace common Unicode chars with ASCII equivalents
                if char in ['—', '–', '―']:  # Various dashes
                    sanitized.append('-')
                elif char in ['"', '"', '"', '"']:  # Various quotes
                    sanitized.append('"')
                elif char in ["'", "'", '′', '″']:  # Various apostrophes
                    sanitized.append("'")
                elif char in ['…', '...']:  # Ellipsis
                    sanitized.append('...')
                elif char in ['•', '·', '⋅']:  # Various bullets
                    sanitized.append('*')
                elif char in ['→', '→', '➜']:  # Arrows
                    sanitized.append('->')
                elif char in ['✓', '✔', '☑']:  # Checkmarks
                    sanitized.append('[OK]')
                elif char in ['✗', '✘', '☒']:  # X marks
                    sanitized.append('[X]')
                elif char in ['⚠', '▲', '⚠️']:  # Warnings
                    sanitized.append('[WARNING]')
                elif char in ['🧠', '🤖', '💡']:  # Brains/AI
                    sanitized.append('[AI]')
                elif char in ['📚', '📖', '📄']:  # Books/docs
                    sanitized.append('[DOC]')
                elif char in ['🔧', '⚙', '🛠']:  # Tools
                    sanitized.append('[TOOL]')
                elif ord(char) > 127:
                    # Replace with [U+XXXX] notation for traceability
                    sanitized.append(f'[U+{ord(char):04X}]')
                else:
                    sanitized.append(char)  # Keep as-is if we can't map it

        return ''.join(sanitized)

    def _execute_wsp_remediation_pipeline(self, remediation_actions: List[str], config: Dict[str, Any]) -> None:
        """
        Execute WSP remediation pipeline with ModLog tracking.
        Creates remediation log and updates relevant ModLogs.
        """
        if not remediation_actions:
            return

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        remediation_log_path = self.repo_root / config['remediation_log_path']

        # Ensure log directory exists
        remediation_log_path.parent.mkdir(parents=True, exist_ok=True)

        # Read existing log or create new one
        existing_content = ""
        if remediation_log_path.exists():
            try:
                with open(remediation_log_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            except Exception:
                existing_content = ""

        # Create remediation entry
        remediation_entry = f"""## ASCII Remediation Session - {timestamp}

**Session Summary:**
- Total remediation actions: {len(remediation_actions)}
- Auto-remediation enabled: {config['auto_remediate_ascii']}

**Actions Taken:**
""" + '\n'.join(f"- {action}" for action in remediation_actions) + "\n\n---\n"

        # Write updated log
        new_content = remediation_entry + existing_content
        with open(remediation_log_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        # Update main ModLog if it exists (with deduplication)
        modlog_path = self.repo_root / "WSP_framework" / "ModLog.md"
        if modlog_path.exists():
            try:
                with open(modlog_path, 'r', encoding='utf-8') as f:
                    modlog_content = f.read()

                # Check for recent duplicate entries to prevent spam
                recent_entry_pattern = f"WSP Documentation Guardian performed ASCII remediation on \\d+ files"
                if re.search(recent_entry_pattern, modlog_content):
                    # Skip adding duplicate entry
                    self.logger.info(f"[WSP-GUARDIAN] Skipping duplicate ModLog entry (already logged recent remediation)")
                else:
                    # Add remediation entry to ModLog
                    remediation_note = f"""- **{timestamp}**: WSP Documentation Guardian performed ASCII remediation on {len(remediation_actions)} files
"""

                    # Insert after the most recent entry
                    if "## Recent Changes" in modlog_content:
                        modlog_content = modlog_content.replace("## Recent Changes", f"## Recent Changes\n{remediation_note}", 1)
                    else:
                        modlog_content = remediation_note + modlog_content

                    with open(modlog_path, 'w', encoding='utf-8') as f:
                        f.write(modlog_content)

            except Exception as e:
                self.logger.warning(f"[WSP-GUARDIAN] Failed to update ModLog: {e}")

        self.logger.info(f"[WSP-GUARDIAN] Remediation pipeline completed - {len(remediation_actions)} actions logged")

    def rollback_ascii_changes(self, filename: str) -> str:
        """
        Rollback ASCII changes for a specific file from backup.

        Returns status message.
        """
        config = WSP_DOC_CONFIG
        backup_dir = self.repo_root / config['backup_temp_dir']

        # Find backup file
        backup_filename = filename + '.backup'
        backup_path = backup_dir / backup_filename

        if not backup_path.exists():
            return f"[ERROR] No backup found for {filename} in {backup_dir}"

        # Find target file
        target_file = None
        for ext in ['.md', '.txt', '']:
            candidate = self.repo_root / filename
            if ext and not filename.endswith(ext):
                candidate = candidate.with_suffix(ext)
            if candidate.exists():
                target_file = candidate
                break

        if not target_file:
            return f"[ERROR] Target file {filename} not found"

        try:
            # Restore from backup
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()

            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(backup_content)

            # Log the rollback
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.logger.info(f"[WSP-GUARDIAN] Rolled back ASCII changes for {filename}")

            # Update remediation log
            self._log_rollback_to_remediation_log(filename, timestamp)

            return f"[SUCCESS] Rolled back ASCII changes for {filename}"

        except Exception as e:
            return f"[ERROR] Failed to rollback {filename}: {e}"

    def _log_rollback_to_remediation_log(self, filename: str, timestamp: str) -> None:
        """Log rollback action to remediation log."""
        config = WSP_DOC_CONFIG
        remediation_log_path = self.repo_root / config['remediation_log_path']

        try:
            existing_content = ""
            if remediation_log_path.exists():
                with open(remediation_log_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()

            rollback_entry = f"""## ASCII Rollback Session - {timestamp}

**Rollback Action:**
- Rolled back ASCII changes for: {filename}

---\n"""

            new_content = rollback_entry + existing_content
            with open(remediation_log_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

        except Exception as e:
            self.logger.warning(f"[WSP-GUARDIAN] Failed to log rollback: {e}")

    def _build_module_snapshot(self, module: str) -> Dict[str, Any]:
        path = self._resolve_module_path(module)
        snapshot: Dict[str, Any] = {
            'module': module,
            'path': path,
            'exists': bool(path and path.exists()),
            'missing_docs': [],
            'test_count': 0,
            'py_file_count': 0,
            'script_orphans': [],
            'large_python_files': [],
        }
        if not snapshot['exists']:
            return snapshot

        py_files = list(path.rglob('*.py'))
        snapshot['py_file_count'] = len(py_files)

        tests_dir = path / 'tests'
        test_files = list(tests_dir.rglob('test_*.py')) if tests_dir.exists() else []
        snapshot['test_count'] = len(test_files)

        docs = ('README.md', 'INTERFACE.md', 'ModLog.md', 'tests/TestModLog.md')
        snapshot['missing_docs'] = [doc for doc in docs if not (path / doc).exists()]

        large_files: List[tuple[Path, int, int]] = []
        for py_file in py_files:
            line_count = self._count_file_lines(py_file)
            size_kb = max(1, py_file.stat().st_size // 1024)
            if line_count > 400 or size_kb > 120:
                large_files.append((py_file, line_count, size_kb))
        snapshot['large_python_files'] = large_files

        scripts_dir = path / 'scripts'
        script_orphans: List[Path] = []
        if scripts_dir.exists():
            test_names = {test.name for test in test_files}
            for script in scripts_dir.glob('*.py'):
                if script.name.startswith('__init__'):
                    continue
                expected = f"test_{script.stem}.py"
                if expected not in test_names:
                    script_orphans.append(script)
        snapshot['script_orphans'] = script_orphans

        return snapshot

    def _resolve_module_path(self, module: str) -> Optional[Path]:
        if not module:
            return None
        candidate = (self.repo_root / module).resolve()
        if candidate.exists():
            return candidate
        return None

    def _resolve_file_path(self, file_path: str) -> Optional[Path]:
        if not file_path:
            return None
        candidate = Path(file_path)
        if candidate.is_absolute() and candidate.exists():
            return candidate
        candidate = (self.repo_root / file_path).resolve()
        return candidate if candidate.exists() else None

    def _relative_path(self, path: Path) -> str:
        try:
            return str(path.resolve().relative_to(self.repo_root))
        except Exception:
            return str(path)

    def _count_file_lines(self, path: Path) -> int:
        try:
            with path.open('r', encoding='utf-8', errors='ignore') as handle:
                return sum(1 for _ in handle)
        except OSError:
            return 0

    def _calculate_analysis_effectiveness(self, report: str) -> float:
        lines = report.split('\n')
        result_lines = [
            line
            for line in lines
            if any(keyword in line.upper() for keyword in ['FOUND', 'DETECTED', 'VIOLATION', 'PATTERN', 'OK', 'HEALTH'])
        ]
        return min(1.0, len(result_lines) / max(1, len(lines) * 0.3))

    def _log_chain_of_thought(self, step_type: str, message: str) -> None:
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] 🤖🧠 [QWEN-{step_type}] {message}"
        self.chain_of_thought_log.append({
            'timestamp': datetime.now(),
            'type': step_type,
            'message': message,
        })
        self.logger.info(log_entry)
        try:
            print(log_entry)
        except UnicodeEncodeError:
            sys.stdout.buffer.write((log_entry + '\n').encode('utf-8', errors='replace'))

    def get_analysis_context(self) -> Dict[str, Any]:
        return {
            'files': self._last_files.copy(),
            'modules': self._last_modules.copy(),
            'executed_components': self._last_executed_components.copy(),
        }

    def get_chain_of_thought_summary(self) -> Dict[str, Any]:
        return {
            'total_steps': len(self.chain_of_thought_log),
            'step_types': list({entry['type'] for entry in self.chain_of_thought_log[-20:]}),
            'recent_activity': [entry['message'] for entry in self.chain_of_thought_log[-5:]],
            'avg_effectiveness': sum(self.performance_history[-10:]) / max(1, len(self.performance_history[-10:])),
        }

