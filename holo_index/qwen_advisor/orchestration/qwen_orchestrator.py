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

        # Log detected intent for visibility
        intent = context.get("query_intent", "standard")
        if intent == "fix_error":
            self._log_chain_of_thought("INTENT", "🔧 Error fixing mode - minimizing health checks")
        elif intent == "locate_code":
            self._log_chain_of_thought("INTENT", "📍 Code location mode - focused output")
        elif intent == "explore":
            self._log_chain_of_thought("INTENT", "🔍 Exploration mode - full analysis")

        orchestration_decisions = self._get_orchestration_decisions(context)

        analysis_report = self._execute_orchestrated_analysis(
            query, involved_files, involved_modules, orchestration_decisions
        )

        effectiveness = self._calculate_analysis_effectiveness(analysis_report)
        self.performance_history.append(effectiveness)
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]
        self._log_chain_of_thought("EFFECTIVENESS", f"Analysis effectiveness: {effectiveness:.2f}")

        return analysis_report

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

        # Code location request - minimal output
        locate_keywords = ['where', 'find', 'location', 'which file', 'line']
        if any(kw in lower_query for kw in locate_keywords):
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
        }

    def _get_orchestration_decisions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get orchestration decisions from performance orchestrator"""
        available_components = {
            "health_analysis": {
                "purpose": "Check system integrity and WSP compliance",
                "triggers": ["query_contains_health", "has_modules"],
                "cost": "medium",
                "value": "high",
            },
            "vibecoding_analysis": {
                "purpose": "Detect behavioral vibecoding patterns",
                "triggers": ["query_contains_vibecoding", "has_files"],
                "cost": "low",
                "value": "high",
            },
            "file_size_monitor": {
                "purpose": "Monitor for architectural bloat",
                "triggers": ["query_contains_module", "has_files"],
                "cost": "low",
                "value": "medium",
                "skip_for_intents": ["fix_error", "locate_code"],  # Skip when fixing errors
            },
            "module_analysis": {
                "purpose": "Validate module structure and dependencies",
                "triggers": ["has_modules", "query_contains_module"],
                "cost": "medium",
                "value": "high",
            },
            "pattern_coach": {
                "purpose": "Prevent behavioral vibecoding through coaching",
                "triggers": ["has_files", "query_contains_vibecoding"],
                "cost": "low",
                "value": "medium",
            },
            "orphan_analysis": {
                "purpose": "Find dead code and connection opportunities",
                "triggers": ["query_contains_health", "has_modules"],
                "cost": "high",
                "value": "medium",
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
            f"剥 [SEMANTIC-SEARCH] {len(files)} files across {len(unique_modules)} modules"
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
        return []

    def _run_health_analysis(self, module_snapshots: Dict[str, Dict[str, Any]]) -> List[str]:
        if not module_snapshots:
            return ["?? [HOLODAE-HEALTH][OK] No modules to audit in current query"]
        lines: List[str] = []
        for module, snapshot in module_snapshots.items():
            if not snapshot['exists']:
                lines.append(f"?? [HOLODAE-HEALTH][WARNING] FOUND missing module on disk: {module}")
                continue
            missing_docs = snapshot['missing_docs']
            if missing_docs:
                lines.append(
                    f"?? [HOLODAE-HEALTH][VIOLATION] {module} missing {', '.join(missing_docs)} (WSP 22)"
                )
            else:
                lines.append(f"?? [HOLODAE-HEALTH][OK] {module} documentation complete")
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
                    f"ｧ [VIBECODING-PATTERN] Found {py_count} implementation files with 0 tests in {module} (coverage 0%)"
                )
            elif coverage < 0.2 and py_count >= 5:
                lines.append(
                    f"ｧ [VIBECODING-PATTERN] Low coverage {coverage:.0%} in {module} ({tests} tests across {py_count} files)"
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
                    f"棟 [HOLODAE-SIZE][WARNING] FOUND large file {rel} ({line_count} lines, {size_kb} KB)"
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
                        f"棟 [HOLODAE-SIZE][WARNING] FOUND large file {rel} ({line_count} lines, {size_kb} KB)"
                    )
                    flagged.add(rel)
            elif size_kb > 256:
                lines.append(
                    f"棟 [HOLODAE-SIZE][NOTICE] FOUND large artifact {rel} ({size_kb} KB)"
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
                f"逃 [HOLODAE-MODULE][FOUND] {module} contains {py_count} python files with {tests} tests"
            )
            if snapshot['missing_docs']:
                lines.append(
                    f"逃 [HOLODAE-MODULE][WARNING] {module} missing {', '.join(snapshot['missing_docs'])}"
                )
            if snapshot['large_python_files']:
                rel = self._relative_path(snapshot['large_python_files'][0][0])
                lines.append(
                    f"逃 [HOLODAE-MODULE][WARNING] Large implementation file detected: {rel}"
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
                    f"ｧ [PATTERN-COACH] Found documentation gap in {module}: {', '.join(snapshot['missing_docs'])}"
                )
            if snapshot['script_orphans']:
                samples = ', '.join(
                    self._relative_path(path) for path in snapshot['script_orphans'][:2]
                )
                lines.append(
                    f"ｧ [PATTERN-COACH] Found {len(snapshot['script_orphans'])} scripts lacking tests in {module}: {samples}"
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
                lines.append(f"?? [ORPHAN-FOUND] {rel} lacks matching tests - investigate connection")
            if len(orphans) > 3:
                lines.append(
                    f"?? [ORPHAN-SUMMARY] {len(orphans)} potential orphan scripts detected in {module}"
                )
        if not lines:
            lines.append("?? [ORPHAN-ANALYSIS][OK] No orphaned scripts identified")
        return lines

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

