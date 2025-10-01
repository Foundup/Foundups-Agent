#!/usr/bin/env python3
"""
ContextAnalyzer - Analyze what 0102 is currently working on

WSP Compliance: WSP 80 (Cube-Level DAE Orchestration)
"""

from pathlib import Path
from typing import List, Optional, Dict, Set
from datetime import datetime

from ..models.work_context import WorkContext


class ContextAnalyzer:
    """Analyze what 0102 is working on based on file changes and actions"""

    def __init__(self):
        """Initialize the context analyzer with work pattern definitions"""
        self.work_patterns = {
            'database_migration': ['json', 'database', 'migration', 'db', 'schema'],
            'module_creation': ['module', 'create', 'new', 'scaffold', 'init'],
            'refactoring': ['refactor', 'large', 'size', 'split', 'monolithic'],
            'debugging': ['error', 'fix', 'debug', 'issue', 'bug', 'traceback'],
            'documentation': ['readme', 'doc', 'interface', 'modlog', 'comment'],
            'testing': ['test', 'coverage', 'audit', 'validation', 'pytest'],
            'configuration': ['config', 'settings', 'yaml', 'json', 'env'],
            'deployment': ['docker', 'deploy', 'build', 'ci', 'cd'],
            'monitoring': ['log', 'monitor', 'health', 'status', 'alert'],
            'security': ['auth', 'security', 'encrypt', 'token', 'permission']
        }

    def analyze_work_context(self, changed_files: List[str], session_actions: List[str]) -> WorkContext:
        """Analyze what type of work 0102 is doing based on changed files and actions

        Args:
            changed_files: List of file paths that have been modified
            session_actions: List of actions taken in this session

        Returns:
            WorkContext object describing the current work state
        """
        context = WorkContext()
        context.active_files = set(changed_files)
        context.last_activity = datetime.now()

        # Record session actions
        context.session_actions = session_actions.copy()

        # Determine primary module being worked on
        modules = set()
        for file_path in changed_files:
            module = self._extract_module(file_path)
            if module:
                modules.add(module)

        if modules:
            # Choose the module that appears most frequently in changed files
            context.primary_module = max(modules, key=lambda m: sum(1 for f in changed_files if m in f))

        # Identify task pattern based on file names, paths, and actions
        context.task_pattern = self._identify_task_pattern(changed_files, session_actions)

        return context

    def _identify_task_pattern(self, changed_files: List[str], session_actions: List[str]) -> str:
        """Identify the primary task pattern from files and actions"""
        # Combine all text for pattern matching
        all_text = ' '.join(changed_files + session_actions).lower()

        # Also analyze file extensions and directory names
        file_extensions = [Path(f).suffix.lower() for f in changed_files]
        dir_names = []
        for file_path in changed_files:
            parts = Path(file_path).parts
            dir_names.extend([p.lower() for p in parts if not p.startswith('.')])

        analysis_text = all_text + ' ' + ' '.join(file_extensions) + ' ' + ' '.join(dir_names)

        # Score each pattern
        pattern_scores = {}
        for pattern, keywords in self.work_patterns.items():
            score = sum(1 for keyword in keywords if keyword in analysis_text)
            if score > 0:
                pattern_scores[pattern] = score

        # Return highest scoring pattern, or 'unknown'
        return max(pattern_scores, key=pattern_scores.get) if pattern_scores else "unknown"

    def _extract_module(self, file_path: str) -> Optional[str]:
        """Extract module name from file path

        Supports both holo_index and modules directory structures.
        Returns module path like 'modules/ai_intelligence/social_media_dae' or 'holo_index/qwen_advisor'
        """
        path_parts = Path(file_path).parts

        # Handle modules directory structure
        if 'modules' in path_parts:
            try:
                module_idx = path_parts.index('modules')
                if module_idx + 2 < len(path_parts):
                    # Return full module path: modules/domain/module
                    return f"modules/{path_parts[module_idx + 1]}/{path_parts[module_idx + 2]}"
                elif module_idx + 1 < len(path_parts):
                    # Return domain level: modules/domain
                    return f"modules/{path_parts[module_idx + 1]}"
            except ValueError:
                pass

        # Handle holo_index directory structure
        if 'holo_index' in path_parts:
            try:
                holo_idx = path_parts.index('holo_index')
                if holo_idx + 2 < len(path_parts):
                    # Return component path: holo_index/component/subcomponent
                    return f"holo_index/{path_parts[holo_idx + 1]}/{path_parts[holo_idx + 2]}"
                elif holo_idx + 1 < len(path_parts):
                    # Return component level: holo_index/component
                    return f"holo_index/{path_parts[holo_idx + 1]}"
            except ValueError:
                pass

        # Handle WSP_framework
        if 'WSP_framework' in path_parts:
            return "WSP_framework"

        return None

    def get_related_modules(self, changed_files: List[str]) -> Set[str]:
        """Get all modules related to the changed files"""
        modules = set()
        for file_path in changed_files:
            module = self._extract_module(file_path)
            if module:
                modules.add(module)
        return modules

    def get_file_type_distribution(self, changed_files: List[str]) -> Dict[str, int]:
        """Get distribution of file types in changed files"""
        distribution = {}
        for file_path in changed_files:
            ext = Path(file_path).suffix.lower()
            distribution[ext] = distribution.get(ext, 0) + 1
        return distribution

    def detect_vibecoding_patterns(self, changed_files: List[str]) -> List[str]:
        """Detect potential vibecoding patterns in the changed files"""
        patterns = []

        # Check for large files (potential refactoring candidates)
        for file_path in changed_files:
            try:
                if file_path.endswith('.py'):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = sum(1 for _ in f)
                    if lines > 1000:
                        patterns.append(f"Large file: {Path(file_path).name} ({lines} lines)")
            except (IOError, OSError):
                continue

        # Check for duplicate file patterns
        file_names = [Path(f).stem.lower() for f in changed_files]
        duplicates = set()
        seen = set()
        for name in file_names:
            if name in seen:
                duplicates.add(name)
            else:
                seen.add(name)

        if duplicates:
            patterns.extend([f"Duplicate naming: {dup}" for dup in duplicates])

        return patterns
