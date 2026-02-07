#!/usr/bin/env python3
"""
WSP Documentation Guardian - Extracted from QwenOrchestrator

Handles WSP documentation compliance monitoring, ASCII remediation,
and automated documentation quality checks.

WSP 62 Refactoring: Extracted to comply with file size thresholds.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


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


class WSPDocumentationGuardian:
    """
    WSP Documentation Guardian for compliance monitoring and remediation.
    
    Extracted from QwenOrchestrator for WSP 62 compliance.
    """

    def __init__(self, repo_root: Path, logger, relative_path_func, count_lines_func):
        """
        Initialize WSP Documentation Guardian.
        
        Args:
            repo_root: Repository root path
            logger: Logging instance
            relative_path_func: Function to get relative paths
            count_lines_func: Function to count file lines
        """
        self.repo_root = repo_root
        self.logger = logger
        self._relative_path = relative_path_func
        self._count_file_lines = count_lines_func

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
                elif char in ['•', '·', '[U+22C5]']:  # Various bullets
                    sanitized.append('*')
                elif char in ['->', '->', '[U+279C]']:  # Arrows
                    sanitized.append('->')
                elif char in ['[OK]', '[U+2714]', '[U+2611]']:  # Checkmarks
                    sanitized.append('[OK]')
                elif char in ['[FAIL]', '[U+2718]', '[CHECKED]']:  # X marks
                    sanitized.append('[X]')
                elif char in ['[U+26A0]', '[U+25B2]', '[U+26A0]️']:  # Warnings
                    sanitized.append('[WARNING]')
                elif char in ['[AI]', '[BOT]', '[IDEA]']:  # Brains/AI
                    sanitized.append('[AI]')
                elif char in ['[BOOKS]', '[U+1F4D6]', '[U+1F4C4]']:  # Books/docs
                    sanitized.append('[DOC]')
                elif char in ['[TOOL]', '[U+2699]', '[U+1F6E0]']:  # Tools
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


    def _resolve_module_path(self, module: str):
        """Resolve module name to filesystem path (mirrors QwenOrchestrator pattern)."""
        if not module:
            return None
        candidate = (self.repo_root / module).resolve()
        return candidate if candidate.exists() else None

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

