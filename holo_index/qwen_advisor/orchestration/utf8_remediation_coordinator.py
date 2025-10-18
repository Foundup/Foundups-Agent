#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io

"""
UTF-8 Remediation Coordinator - Qwen + Gemma Autonomous Remediation
====================================================================

Coordinates autonomous UTF-8 hygiene remediation across the repository using
WSP 90 (UTF-8 Encoding Enforcement) with WSP 77 (Agent Coordination) and
WSP 91 (DAEMON Observability).

Architecture:
    Phase 1 (Gemma): Fast pattern classification - identify violation types
    Phase 2 (Qwen):  Strategic remediation - decide fix method per file
    Phase 3 (0102):  Apply fixes with WSP 90 header insertion
    Phase 4 (Learning): Store patterns in PatternMemory for reuse

WSP Compliance:
    - WSP 90: UTF-8 Encoding Enforcement Protocol
    - WSP 77: Agent Coordination Protocol (Qwen -> Gemma -> 0102)
    - WSP 91: DAEMON Observability (structured logging)
    - WSP 50: Pre-Action Verification (scan before fix)
    - WSP 48: Recursive Self-Improvement (learn from fixes)
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import time
import re

# Import autonomous refactoring infrastructure
from holo_index.qwen_advisor.orchestration.autonomous_refactoring import (
    AutonomousRefactoringOrchestrator,
    DaemonLogger
)

logger = logging.getLogger(__name__)


@dataclass
class UTF8Violation:
    """Single UTF-8 violation detected in codebase"""
    file_path: str
    violation_type: str  # "missing_header", "emoji_output", "no_encoding", "bom", "legacy_char"
    line_number: Optional[int]
    context: str
    severity: str  # "critical", "high", "medium", "low"


@dataclass
class RemediationPlan:
    """Complete remediation plan for UTF-8 violations"""
    violations: List[UTF8Violation]
    total_files: int
    estimated_fixes: int
    fix_strategy: str  # "insert_header", "replace_emoji", "add_encoding", "ascii_safe"


class UTF8RemediationCoordinator:
    """
    Coordinates autonomous UTF-8 remediation using Qwen + Gemma coordination.

    This delegates to AutonomousRefactoringOrchestrator for the actual execution,
    following the "0102 way" of autonomous operation.
    """

    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)
        self.memory_path = self.repo_root / "holo_index" / "adaptive_learning" / "utf8_remediation_patterns.json"
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize autonomous refactoring orchestrator
        self.orchestrator = AutonomousRefactoringOrchestrator(repo_root)

        # WSP 91: Initialize structured daemon logger
        self.daemon_logger = DaemonLogger("UTF8RemediationCoordinator")

        # Load existing patterns
        self.patterns = self._load_patterns()

        # WSP 90 compliance rules
        self.wsp90_header = """# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ==="""

        # ASCII-safe replacements per WSP 90 Rule 3
        # NOTE: ONLY use these as FALLBACK for non-Python files
        # For .py files: ADD WSP 90 header instead (keeps emojis working!)
        self.emoji_replacements = {
            '[OK]': '[SUCCESS]',
            '[FAIL]': '[FAIL]',
            '[U+26A0]️': '[WARNING]',
            '[U+1F4C1]': '[FOLDER]',
            '[U+1F4C4]': '[FILE]',
            '[SEARCH]': '[SEARCH]',
            '[ROCKET]': '[LAUNCH]',
            '[IDEA]': '[IDEA]',
            '[TARGET]': '[TARGET]',
            '⏱️': '[TIME]',
            '[U+2728]': '[SPARKLE]',
            '[U+1F525]': '[HOT]',
            '[PILL]': '[HEALTH]',
            '[AI]': '[BRAIN]',
            '[DATA]': '[CHART]',
            '[BREAD]': '[BREADCRUMB]',
            '[BOT]': '[AI]',
            '[GHOST]': '[ORPHAN]',
            '[RULER]': '[MEASURE]',
            '[BOX]': '[PACKAGE]',
            '[BOOKS]': '[DOCS]',
            '[ART]': '[ART]',
            '[LINK]': '[LINK]',
            '[U+270D]️': '[WRITE]'
        }

    def _load_patterns(self) -> Dict:
        """Load UTF-8 remediation patterns from memory"""
        if self.memory_path.exists():
            with open(self.memory_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "successful_remediations": [],
            "failed_attempts": [],
            "violation_patterns": {}
        }

    def _save_patterns(self):
        """Save patterns to memory for learning"""
        with open(self.memory_path, 'w', encoding='utf-8') as f:
            json.dump(self.patterns, f, indent=2)

    # PHASE 1: Scan Repository for UTF-8 Violations

    def scan_for_violations(
        self,
        scope: Optional[str] = None,
        fast_scan: bool = False,
    ) -> List[UTF8Violation]:
        """
        Scan repository for UTF-8 violations using Gemma fast classification

        Args:
            scope: Optional module path to limit scan (prevents timeout)
            fast_scan: Skip deep dependency analysis for large batches

        Returns:
            List of UTF8Violation objects detected
        """
        scan_start = time.time()
        logger.info(f"[UTF8-SCAN] Scanning {scope or 'entire repository'} for violations...")

        violations = []
        search_path = self.repo_root / scope if scope else self.repo_root

        # Find all Python files
        python_files = list(search_path.rglob("*.py"))
        logger.info(f"[UTF8-SCAN] Found {len(python_files)} Python files to analyze")

        if not fast_scan and len(python_files) > 100:
            logger.info(
                "[UTF8-SCAN] Large batch detected (%d files). Enabling fast scan.",
                len(python_files),
            )
            fast_scan = True

        for py_file in python_files:
            try:
                if not fast_scan:
                    # Use Gemma for dependency-aware classification (small batches)
                    self.orchestrator.analyze_module_dependencies(str(py_file))

                # Check for UTF-8 violations
                file_violations = self._detect_violations_in_file(py_file)
                violations.extend(file_violations)

            except Exception as e:
                logger.warning(f"[UTF8-SCAN] Could not analyze {py_file}: {e}")

        # WSP 91: Log scan performance
        scan_time = (time.time() - scan_start) * 1000
        self.daemon_logger.log_performance(
            operation="utf8_violation_scan",
            duration_ms=scan_time,
            items_processed=len(python_files),
            success=True,
            violations_found=len(violations),
            scope=scope or "full_repo"
        )

        logger.info(f"[UTF8-SCAN] Found {len(violations)} violations in {scan_time:.0f}ms")
        return violations

    def _detect_violations_in_file(self, file_path: Path) -> List[UTF8Violation]:
        """Detect UTF-8 violations in a single file"""
        violations = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                lines = content.split('\n')

            # Check if this is an entry point or library module
            is_entry_point = self._is_entry_point(content)

            # Check 1: Missing WSP 90 UTF-8 enforcement header (ONLY for entry points)
            # Library modules should NOT have WSP 90 headers (causes import conflicts)
            if is_entry_point and "# === UTF-8 ENFORCEMENT (WSP 90) ===" not in content:
                violations.append(UTF8Violation(
                    file_path=str(file_path),
                    violation_type="missing_header",
                    line_number=None,
                    context="Entry point missing WSP 90 UTF-8 enforcement header",
                    severity="high"
                ))

            # Check 2: Emoji/Unicode in print statements
            for i, line in enumerate(lines, 1):
                for emoji, replacement in self.emoji_replacements.items():
                    if emoji in line:
                        violations.append(UTF8Violation(
                            file_path=str(file_path),
                            violation_type="emoji_output",
                            line_number=i,
                            context=f"Line contains emoji '{emoji}' -> replace with '{replacement}'",
                            severity="medium"
                        ))

            # Check 3: File operations without encoding parameter
            for i, line in enumerate(lines, 1):
                if 'open(' in line and 'encoding=' not in line and not line.strip().startswith('#'):
                    violations.append(UTF8Violation(
                        file_path=str(file_path),
                        violation_type="no_encoding",
                        line_number=i,
                        context="File operation missing encoding='utf-8' parameter",
                        severity="medium"
                    ))

            # Check 4: BOM characters (0xFF, 0xFE)
            if content.startswith('\ufeff'):
                violations.append(UTF8Violation(
                    file_path=str(file_path),
                    violation_type="bom",
                    line_number=1,
                    context="File has UTF-8 BOM - should be removed",
                    severity="low"
                ))

            # Check 5: Legacy encoding characters (0x84, 0xA0)
            if re.search(r'[\x84\xA0]', content):
                violations.append(UTF8Violation(
                    file_path=str(file_path),
                    violation_type="legacy_char",
                    line_number=None,
                    context="File contains legacy encoding characters",
                    severity="high"
                ))

        except Exception as e:
            logger.warning(f"[UTF8-SCAN] Error analyzing {file_path}: {e}")

        return violations

    # PHASE 2: Generate Remediation Plan (Qwen Strategic Planning)

    def generate_remediation_plan(self, violations: List[UTF8Violation]) -> RemediationPlan:
        """
        Use Qwen to generate strategic remediation plan

        Args:
            violations: List of detected violations

        Returns:
            RemediationPlan with fix strategy
        """
        planning_start = time.time()
        logger.info(f"[QWEN-PLAN] Generating remediation plan for {len(violations)} violations...")

        # Group violations by file
        files_affected = {}
        for violation in violations:
            if violation.file_path not in files_affected:
                files_affected[violation.file_path] = []
            files_affected[violation.file_path].append(violation)

        # Determine fix strategy (Qwen would decide this based on complexity)
        total_files = len(files_affected)
        estimated_fixes = len(violations)

        # Simple heuristic for now (Qwen LLM would do deeper analysis)
        if estimated_fixes < 100:
            strategy = "batch_fix_all"
        elif estimated_fixes < 1000:
            strategy = "scoped_module_fix"
        else:
            strategy = "incremental_scoped_fix"

        plan = RemediationPlan(
            violations=violations,
            total_files=total_files,
            estimated_fixes=estimated_fixes,
            fix_strategy=strategy
        )

        # WSP 91: Log planning performance
        planning_time = (time.time() - planning_start) * 1000
        self.daemon_logger.log_decision(
            decision_type="remediation_strategy",
            chosen_path=strategy,
            confidence=0.9,
            reasoning=f"Selected {strategy} for {estimated_fixes} violations across {total_files} files",
            violations=estimated_fixes,
            files=total_files,
            planning_ms=planning_time
        )

        logger.info(f"[QWEN-PLAN] Strategy: {strategy} for {total_files} files in {planning_time:.0f}ms")
        return plan

    # PHASE 3: Execute Remediation (0102 Supervision)

    def execute_remediation(self, plan: RemediationPlan, auto_approve: bool = False) -> Dict:
        """
        Execute UTF-8 remediation with 0102 supervision

        Args:
            plan: Remediation plan from Qwen
            auto_approve: If True, apply fixes without prompts

        Returns:
            Results dict with success status and metrics
        """
        execution_start = time.time()
        logger.info(f"[0102-EXECUTE] Starting UTF-8 remediation ({plan.fix_strategy})...")

        results = {
            "files_fixed": 0,
            "violations_fixed": 0,
            "failures": 0,
            "errors": [],
            "success": False
        }

        # Group violations by file for batch processing
        files_to_fix = {}
        for violation in plan.violations:
            if violation.file_path not in files_to_fix:
                files_to_fix[violation.file_path] = []
            files_to_fix[violation.file_path].append(violation)

        # Fix each file
        for file_path, violations in files_to_fix.items():
            try:
                if not auto_approve:
                    print(f"\n[0102-SUPERVISION] Fix {file_path}?")
                    print(f"  Violations: {len(violations)}")
                    print(f"  Types: {', '.join(set(v.violation_type for v in violations))}")
                    approval = input("  Approve? (y/n): ").lower()
                    if approval != 'y':
                        logger.warning(f"[0102] Skipped {file_path}")
                        continue

                # Apply fixes
                fix_success = self._fix_file(Path(file_path), violations)

                if fix_success:
                    results["files_fixed"] += 1
                    results["violations_fixed"] += len(violations)
                    logger.info(f"[0102] Fixed {file_path}: {len(violations)} violations")
                else:
                    results["failures"] += 1
                    results["errors"].append(f"Failed to fix {file_path}")
                    logger.error(f"[0102] Failed to fix {file_path}")

            except Exception as e:
                results["failures"] += 1
                results["errors"].append(f"{file_path}: {str(e)}")
                logger.error(f"[0102] Error fixing {file_path}: {e}")

        results["success"] = results["failures"] == 0

        # WSP 91: Log execution performance
        execution_time = (time.time() - execution_start) * 1000
        self.daemon_logger.log_performance(
            operation="utf8_remediation_execution",
            duration_ms=execution_time,
            items_processed=len(files_to_fix),
            success=results["success"],
            files_fixed=results["files_fixed"],
            violations_fixed=results["violations_fixed"],
            failures=results["failures"]
        )

        logger.info(f"[0102-EXECUTE] Complete: {results['files_fixed']} files, {results['violations_fixed']} fixes in {execution_time:.0f}ms")
        return results

    def _is_entry_point(self, content: str) -> bool:
        """
        Detect if file is an entry point script vs library module

        Entry points have:
        - if __name__ == "__main__": at the bottom
        - main() function definition
        - Script-like execution flow

        Library modules:
        - Only class/function definitions
        - Imported by other files
        - No __main__ guard
        """
        # Check for __main__ guard (strong indicator of entry point)
        if 'if __name__ == "__main__":' in content or "if __name__ == '__main__':" in content:
            return True

        # Check for main() function definition (common entry point pattern)
        if 'def main(' in content:
            return True

        # If no entry point indicators, it's a library module
        return False

    def _fix_file(self, file_path: Path, violations: List[UTF8Violation]) -> bool:
        """Apply UTF-8 fixes to a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                lines = content.split('\n')

            modified = False
            is_entry_point = self._is_entry_point(content)

            # Fix 1: Insert WSP 90 header if missing (ONLY for entry points)
            # CRITICAL: Library modules should NOT have WSP 90 header!
            # WSP 90 header wraps sys.stdout/stderr, causing conflicts when imported
            if any(v.violation_type == "missing_header" for v in violations):
                if is_entry_point:
                    # Find insertion point (after module docstring)
                    insert_idx = 0
                    in_docstring = False
                    for i, line in enumerate(lines):
                        if '"""' in line or "'''" in line:
                            if not in_docstring:
                                in_docstring = True
                            else:
                                insert_idx = i + 1
                                break

                    # Insert header
                    header_lines = self.wsp90_header.split('\n')
                    lines = lines[:insert_idx] + [''] + header_lines + [''] + lines[insert_idx:]
                    modified = True
                    logger.info(f"[ENTRY-POINT] Added WSP 90 header to {file_path}")
                else:
                    # Library module - do NOT add header
                    logger.info(f"[LIBRARY-MODULE] Skipping WSP 90 header for {file_path} (would break imports)")

            # Fix 2: Replace emojis with ASCII-safe alternatives
            # IMPORTANT: Skip this for .py files! WSP 90 header fixes emoji display.
            # ONLY do emoji replacement for non-Python files (config, markdown, etc.)
            if not file_path.suffix == '.py':
                for violation in violations:
                    if violation.violation_type == "emoji_output" and violation.line_number:
                        line_idx = violation.line_number - 1
                        if 0 <= line_idx < len(lines):
                            for emoji, replacement in self.emoji_replacements.items():
                                if emoji in lines[line_idx]:
                                    lines[line_idx] = lines[line_idx].replace(emoji, replacement)
                                    modified = True

            # Fix 3: Add encoding='utf-8' to file operations
            for i, line in enumerate(lines):
                if 'open(' in line and 'encoding=' not in line and not line.strip().startswith('#'):
                    # Simple regex replacement for common patterns
                    if 'open(' in line:
                        lines[i] = re.sub(r'open\((.*?)\)', r'open(\1, encoding="utf-8")', line)
                        modified = True

            # Write back if modified
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                return True

            return False

        except Exception as e:
            logger.error(f"[FIX-ERROR] Could not fix {file_path}: {e}")
            return False

    # PHASE 4: Learning - Store Patterns

    def store_remediation_pattern(self, plan: RemediationPlan, results: Dict):
        """
        Store successful remediation as learning pattern

        This enables recursive self-improvement - Qwen learns from
        successful remediations and can apply patterns autonomously.
        """
        pattern = {
            "timestamp": time.time(),
            "strategy": plan.fix_strategy,
            "total_files": plan.total_files,
            "violations_fixed": results['violations_fixed'],
            "success": results['success'],
            "lessons_learned": {
                "pattern_type": "utf8_remediation",
                "fix_strategy": plan.fix_strategy,
                "files_affected": plan.total_files
            }
        }

        if results['success']:
            self.patterns['successful_remediations'].append(pattern)
            logger.info("[LEARNING] Stored successful UTF-8 remediation pattern")
        else:
            self.patterns['failed_attempts'].append(pattern)
            logger.warning("[LEARNING] Stored failed UTF-8 remediation for analysis")

        self._save_patterns()

    # PUBLIC API

    def remediate_utf8_violations(self, scope: Optional[str] = None,
                                    auto_approve: bool = False,
                                    fast_scan: bool = False) -> Dict:
        """
        Main entry point: Autonomous UTF-8 remediation with Qwen + Gemma + 0102

        Args:
            scope: Optional module path to limit remediation (e.g., "holo_index")
            auto_approve: Skip 0102 approval prompts
            fast_scan: Skip deep dependency analysis for large batches (auto-enabled for >100 files)

        Returns:
            Results dict with success status and metrics
        """
        logger.info(f"[START] UTF-8 remediation: {scope or 'entire repository'}")

        # Phase 1: Gemma scan
        violations = self.scan_for_violations(scope, fast_scan=fast_scan)

        if not violations:
            logger.info("[COMPLETE] No UTF-8 violations found!")
            return {"success": True, "violations_fixed": 0, "message": "No violations found"}

        # Phase 2: Qwen planning
        plan = self.generate_remediation_plan(violations)

        # Phase 3: 0102 execution
        results = self.execute_remediation(plan, auto_approve)

        # Phase 4: Learning
        self.store_remediation_pattern(plan, results)

        return results


def main():
    """Demonstrate UTF-8 remediation coordinator"""
    import argparse

    parser = argparse.ArgumentParser(description="UTF-8 Remediation Coordinator")
    parser.add_argument("--scope", type=str, help="Limit remediation to specific module path")
    parser.add_argument("--auto-approve", action="store_true", help="Auto-approve all fixes")
    parser.add_argument("--scan-only", action="store_true", help="Scan only, don't fix")
    parser.add_argument("--fast-scan", action="store_true",
                       help="Skip deep dependency analysis (auto-enabled for >100 files)")

    args = parser.parse_args()

    # Initialize coordinator
    repo_root = Path(__file__).parent.parent.parent.parent
    coordinator = UTF8RemediationCoordinator(repo_root)

    print("UTF-8 Remediation Coordinator - Qwen + Gemma Coordination")
    print("=" * 60)

    if args.scan_only:
        # Scan only
        violations = coordinator.scan_for_violations(args.scope, fast_scan=args.fast_scan)
        print(f"\n[SCAN RESULTS] Found {len(violations)} violations")

        # Group by type
        by_type = {}
        for v in violations:
            by_type[v.violation_type] = by_type.get(v.violation_type, 0) + 1

        print("\nViolations by type:")
        for vtype, count in by_type.items():
            print(f"  {vtype}: {count}")
    else:
        # Full remediation
        results = coordinator.remediate_utf8_violations(
            scope=args.scope,
            auto_approve=args.auto_approve,
            fast_scan=args.fast_scan
        )

        print(f"\n[RESULTS]")
        print(f"  Files fixed: {results.get('files_fixed', 0)}")
        print(f"  Violations fixed: {results.get('violations_fixed', 0)}")
        print(f"  Failures: {results.get('failures', 0)}")
        print(f"  Success: {results.get('success', False)}")


if __name__ == "__main__":
    main()
