# -*- coding: utf-8 -*-
"""
Module Metrics - HoloDAE Module Health and Size Analysis

Extracted from holodae_coordinator.py per WSP 62 remediation.
Sprint H4: Module metrics methods (fourth extraction).

WSP Compliance:
- WSP 62: Modularity Enforcement (<500 lines)
- WSP 91: Structured logging for observability
- WSP 49: Module structure compliance

Usage:
    from holo_index.qwen_advisor.services.module_metrics import ModuleMetrics

    metrics_collector = ModuleMetrics(repo_root, doc_only_modules)
    metrics = metrics_collector.collect_module_metrics(module_path)
    alerts = metrics_collector.get_system_alerts(modules)
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from collections import Counter
from holo_index.core.intelligent_subroutine_engine import IntelligentSubroutineEngine


class ModuleMetrics:
    """
    Collect and analyze module health, size, and compliance metrics.

    Responsibilities:
    - Collect module metrics (health, size, recommendations)
    - Resolve module paths from various formats
    - Track module documentation completeness
    - Analyze module code files for WSP 62/87 compliance
    - Build module maps for orphan analysis
    - Check for test coverage and imports
    """

    def __init__(
        self,
        repo_root: Path,
        doc_only_modules: Set[str],
        module_map: Optional[Dict[str, Dict[str, Any]]] = None,
        orphan_candidates: Optional[List[str]] = None
    ):
        """
        Initialize ModuleMetrics collector.

        Args:
            repo_root: Root path of the repository
            doc_only_modules: Set of documentation-only module paths
            module_map: Existing module map for orphan analysis
            orphan_candidates: List of potential orphan files
        """
        self.repo_root = repo_root
        self.doc_only_modules = doc_only_modules
        self.module_map = module_map if module_map is not None else {}
        self.orphan_candidates = orphan_candidates if orphan_candidates is not None else []
        self._module_metrics_cache: Dict[str, Dict[str, Any]] = {}

    def collect_module_metrics(self, module_path: str) -> Dict[str, Any]:
        """Collect health and size metrics for a single module"""
        cached = self._module_metrics_cache.get(module_path)
        if cached is not None:
            return cached

        display_name = module_path or 'unknown-module'
        resolved_path = self._resolve_component_path(module_path)

        recommendations: List[str] = ["WSP 49 (Module Structure)", "WSP 22 (Documentation)"]
        module_alerts: List[str] = []
        health_label = '[UNKNOWN]'
        size_label = 'N/A'

        if not resolved_path or not resolved_path.exists():
            health_label = 'Module not found'
            module_alerts.append('Module not found on disk')
        else:
            doc_only = self._is_doc_only_module(module_path, resolved_path)
            if doc_only:
                required_files = ("README.md", "INTERFACE.md", "ModLog.md")
            else:
                required_files = ("README.md", "INTERFACE.md", "requirements.txt")
            missing_files = [req for req in required_files if not (resolved_path / req).exists()]
            if missing_files:
                if doc_only:
                    health_label = f"[DOCS-INCOMPLETE] Missing: {', '.join(missing_files)}"
                else:
                    health_label = f"Missing: {', '.join(missing_files)}"
                module_alerts.append(f"Missing documentation: {', '.join(missing_files)}")
                if not doc_only:
                    recommendations.append("WSP 11 (Interface Documentation)")
            else:
                health_label = "[DOCS-COMPLETE]" if doc_only else '[COMPLETE]'

            if doc_only:
                size_label = 'Docs bundle (no code files)'
            else:
                # Use IntelligentSubroutineEngine for language-specific threshold detection
                engine = IntelligentSubroutineEngine()
                total_lines = 0
                total_files = 0
                has_tests = False
                large_file_found = False
                violations_by_type = {}

                # Scan ALL code files (not just .py) with language-specific thresholds
                for code_file in resolved_path.rglob('*'):
                    if not code_file.is_file():
                        continue

                    # Only check files with known thresholds (WSP 62 Section 2.1)
                    if code_file.suffix.lower() not in engine.FILE_THRESHOLDS:
                        continue

                    try:
                        with open(code_file, 'r', encoding='utf-8', errors='ignore') as handle:
                            line_count = sum(1 for _ in handle)
                        total_lines += line_count
                        total_files += 1

                        # Check for tests
                        if code_file.name.startswith('test_'):
                            has_tests = True

                        # Agentic threshold detection per WSP 62/87
                        threshold, file_type = engine.get_file_threshold(code_file)
                        if line_count > threshold:
                            large_file_found = True
                            severity = engine._classify_severity(line_count, code_file.suffix)

                            # Track violations by file type
                            if file_type not in violations_by_type:
                                violations_by_type[file_type] = []
                            violations_by_type[file_type].append({
                                'file': code_file.name,
                                'lines': line_count,
                                'threshold': threshold,
                                'severity': severity
                            })

                    except (OSError, IOError):
                        continue

                if not has_tests:
                    recommendations.append("WSP 5 (Testing Standards)")

                if total_files == 0:
                    size_label = 'No code files'
                else:
                    avg_lines = max(1, total_lines // total_files)
                    if total_lines > 1600:
                        status = '[CRITICAL]'
                        module_alerts.append('Exceeds size thresholds (>1600 lines)')
                    elif total_lines > 1000:
                        status = '[WARN]'
                    else:
                        status = '[GOOD]'
                    size_label = f"{status} {total_lines} lines in {total_files} files (avg: {avg_lines})"

                if large_file_found:
                    recommendations.append("WSP 62 (Modularity Enforcement)")
                    if total_lines <= 1600:
                        # Build detailed alert with file types
                        for file_type, violations in violations_by_type.items():
                            count = len(violations)
                            module_alerts.append(f'{count} {file_type} file(s) exceed WSP 62/87 thresholds')

        deduped_recommendations = []
        for rec in recommendations:
            if rec not in deduped_recommendations:
                deduped_recommendations.append(rec)

        metrics = {
            'display_name': display_name,
            'health_label': health_label,
            'size_label': size_label,
            'recommendations': tuple(deduped_recommendations[:3]),
            'module_alerts': module_alerts,
        }

        self._module_metrics_cache[module_path] = metrics
        return metrics

    def collect_module_metrics_for_request(self, involved_modules: List[str]) -> Dict[str, Dict[str, Any]]:
        """Collect metrics for all modules involved in a request"""
        metrics: Dict[str, Dict[str, Any]] = {}
        if not involved_modules:
            return metrics

        for module in involved_modules:
            if module and module not in metrics:
                metrics[module] = self.collect_module_metrics(module)

        return metrics

    def _resolve_component_path(self, module_path: str) -> Optional[Path]:
        """Resolve module path to absolute Path object"""
        if not module_path:
            return None

        candidate = Path(module_path)
        if candidate.is_absolute() and candidate.exists():
            return candidate

        search_targets = []
        relative = candidate if not candidate.is_absolute() else Path(candidate.name)
        search_targets.append(self.repo_root / relative)

        if not module_path.startswith('modules/'):
            search_targets.append(self.repo_root / 'modules' / module_path)
        if not module_path.startswith('holo_index/'):
            search_targets.append(self.repo_root / 'holo_index' / module_path)

        for target in search_targets:
            if target.exists():
                return target

        return None

    def _is_doc_only_module(self, module_path: str, resolved_path: Optional[Path]) -> bool:
        """Check if module is a documentation-only bundle"""
        if not resolved_path:
            return False

        normalized = module_path.replace('\\', '/').strip()
        if normalized in self.doc_only_modules:
            return True

        absolute = str(resolved_path).replace('\\', '/')
        if absolute in self.doc_only_modules:
            return True

        return False

    def get_module_health_info(self, module_path: str) -> str:
        """Get health information for a module"""
        return self.collect_module_metrics(module_path)['health_label']

    def get_module_size_info(self, module_path: str) -> str:
        """Get size information for a module"""
        return self.collect_module_metrics(module_path)['size_label']

    def get_recommended_wsps(self, module_path: str) -> str:
        """Get recommended WSP protocols for a module"""
        recommendations = self.collect_module_metrics(module_path)['recommendations']
        return ' | '.join(recommendations) if recommendations else 'WSP guidance unavailable'

    def get_system_alerts(self, modules: List[str]) -> List[str]:
        """Get system-wide alerts for the matched modules"""
        alerts: List[str] = []
        if not modules:
            return alerts

        unique_modules: List[str] = []
        for module in modules:
            if module and module not in unique_modules:
                unique_modules.append(module)

        for module in unique_modules:
            metrics = self.collect_module_metrics(module)
            for module_alert in metrics['module_alerts']:
                alerts.append(f"{metrics['display_name']}: {module_alert}")

        name_counts = Counter(m.split('/')[-1] for m in unique_modules if m)
        for name, count in name_counts.items():
            if count > 1:
                alerts.append(f"Multiple modules share the name '{name}' ({count} matches)")

        return alerts
    def build_module_map(self, module_metrics: Dict[str, Dict[str, Any]]) -> None:
        """Build module map for orphan analysis and save to JSON"""
        for module_path, metrics in module_metrics.items():
            resolved_path = Path(module_path)
            if not resolved_path.exists():
                continue

            module_info = {
                'path': module_path,
                'files': {},
                'orphans': [],
                'duplicates': [],
                'docs': {
                    'README.md': (resolved_path / 'README.md').exists(),
                    'INTERFACE.md': (resolved_path / 'INTERFACE.md').exists(),
                    'ModLog.md': (resolved_path / 'ModLog.md').exists(),
                    'tests/TestModLog.md': (resolved_path / 'tests' / 'TestModLog.md').exists()
                }
            }

            # Scan Python files
            for py_file in resolved_path.glob('**/*.py'):
                if '_archive' in str(py_file) or '__pycache__' in str(py_file):
                    continue

                rel_path = py_file.relative_to(resolved_path)
                line_count = sum(1 for _ in open(py_file, 'r', encoding='utf-8', errors='ignore'))

                module_info['files'][str(rel_path)] = {
                    'lines': line_count,
                    'last_modified': datetime.fromtimestamp(py_file.stat().st_mtime).isoformat(),
                    'has_tests': self._check_has_tests(module_path, py_file.stem),
                    'is_imported': self._check_is_imported(module_path, py_file.stem)
                }

                # Check for orphans
                if not module_info['files'][str(rel_path)]['is_imported']:
                    if not module_info['files'][str(rel_path)]['has_tests']:
                        module_info['orphans'].append(str(rel_path))
                        self.orphan_candidates.append(f"{module_path}/{rel_path}")

            self.module_map[module_path] = module_info

            # Save module map to JSON
            map_dir = Path('holo_index/logs/module_map')
            map_dir.mkdir(parents=True, exist_ok=True)

            module_name = module_path.replace('/', '_').replace('\\', '_')
            map_file = map_dir / f"{module_name}.json"

            with open(map_file, 'w', encoding='utf-8') as f:
                json.dump(module_info, f, indent=2)

    def _check_has_tests(self, module_path: str, file_stem: str) -> bool:
        """Check if a file has associated tests"""
        test_patterns = [
            f"test_{file_stem}.py",
            f"test_{file_stem}_*.py",
            f"*_test_{file_stem}.py"
        ]

        test_dir = Path(module_path) / 'tests'
        if not test_dir.exists():
            return False

        for pattern in test_patterns:
            if list(test_dir.glob(pattern)):
                return True

        return False

    def _check_is_imported(self, module_path: str, file_stem: str) -> bool:
        """Check if a file is imported anywhere"""
        # Simple heuristic - check if imported in __init__.py or other files
        module_root = Path(module_path)

        # Check __init__.py
        init_file = module_root / '__init__.py'
        if init_file.exists():
            content = init_file.read_text(encoding='utf-8', errors='ignore')
            if file_stem in content:
                return True

        # Check other Python files
        for py_file in module_root.glob('**/*.py'):
            if py_file.stem == file_stem:
                continue
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            if f"from .{file_stem}" in content or f"import {file_stem}" in content:
                return True

        return False

