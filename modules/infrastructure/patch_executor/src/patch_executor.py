#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WRE Core - Patch Executor
==========================

Safe git patch application with allowlist enforcement for autonomous code fixes.

WSP Compliance: WSP 77 (Agent Coordination), WSP 90 (UTF-8 Enforcement)

Architecture:
    1. Validate patch against allowlist (file patterns, forbidden operations)
    2. Run `git apply --check` for dry-run validation
    3. Apply patch with `git apply` if checks pass
    4. Return structured results for MetricsAppender tracking

Safety Guarantees:
    - Only files matching allowlist patterns can be modified
    - Forbidden operations (deletions, binary, submodule changes) blocked
    - Dry-run validation before actual application
    - Full rollback capability via git
"""

import subprocess
import tempfile
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PatchAllowlist:
    """
    Allowlist configuration for patch execution

    Defines which files can be modified and what operations are permitted.
    """
    # File patterns that can be modified (glob-style)
    allowed_file_patterns: List[str]

    # Operations that are forbidden
    forbidden_operations: Set[str] = None

    # Maximum patch size (lines)
    max_patch_lines: int = 500

    def __post_init__(self):
        if self.forbidden_operations is None:
            self.forbidden_operations = {
                'delete_file',      # No file deletions
                'binary_change',    # No binary file modifications
                'submodule_change', # No submodule updates
                'rename_file'       # No file renames (could bypass allowlist)
            }


class PatchExecutor:
    """
    Safe git patch executor with allowlist enforcement

    Applies code patches autonomously while enforcing safety constraints.
    """

    def __init__(self, repo_root: Path, allowlist: Optional[PatchAllowlist] = None):
        """
        Initialize patch executor

        Args:
            repo_root: Root directory of git repository
            allowlist: Patch allowlist configuration (defaults to restrictive settings)
        """
        self.repo_root = Path(repo_root)

        if allowlist is None:
            # Default restrictive allowlist
            self.allowlist = PatchAllowlist(
                allowed_file_patterns=[
                    "modules/**/*.py",  # Python modules only by default
                ],
                max_patch_lines=100  # Small patches only
            )
        else:
            self.allowlist = allowlist

    def apply_patch(
        self,
        patch_content: str,
        patch_description: str = "Autonomous patch",
        dry_run: bool = False
    ) -> Dict:
        """
        Apply git patch with safety validation

        Args:
            patch_content: Unified diff patch content
            patch_description: Human-readable description of patch
            dry_run: If True, only validate without applying

        Returns:
            Dict with keys:
                - success: bool
                - validation_passed: bool
                - applied: bool
                - files_modified: List[str]
                - violations: List[str]
                - error: Optional[str]
        """
        logger.info(f"[PATCH-EXECUTOR] Processing patch: {patch_description}")

        result = {
            "success": False,
            "validation_passed": False,
            "applied": False,
            "files_modified": [],
            "violations": [],
            "error": None,
            "patch_description": patch_description
        }

        try:
            # Step 1: Validate patch against allowlist
            validation = self._validate_patch(patch_content)
            result["validation_passed"] = validation["valid"]
            result["violations"] = validation["violations"]
            result["files_modified"] = validation["files"]

            if not validation["valid"]:
                result["error"] = f"Patch validation failed: {', '.join(validation['violations'])}"
                logger.warning(f"[PATCH-EXECUTOR] Validation failed: {result['error']}")
                return result

            logger.info(f"[PATCH-EXECUTOR] Validation passed - {len(validation['files'])} files")

            if dry_run:
                result["success"] = True
                logger.info(f"[PATCH-EXECUTOR] Dry-run only - validation complete")
                return result

            # Step 2: Run git apply --check (dry-run)
            check_result = self._git_apply_check(patch_content)
            if not check_result["success"]:
                result["error"] = f"git apply --check failed: {check_result['error']}"
                logger.warning(f"[PATCH-EXECUTOR] {result['error']}")
                return result

            logger.info(f"[PATCH-EXECUTOR] git apply --check passed")

            # Step 3: Apply patch
            apply_result = self._git_apply(patch_content)
            if not apply_result["success"]:
                result["error"] = f"git apply failed: {apply_result['error']}"
                logger.error(f"[PATCH-EXECUTOR] {result['error']}")
                return result

            result["applied"] = True
            result["success"] = True
            logger.info(f"[PATCH-EXECUTOR] Patch applied successfully")

            return result

        except Exception as e:
            result["error"] = f"Unexpected error: {str(e)}"
            logger.error(f"[PATCH-EXECUTOR] {result['error']}", exc_info=True)
            return result

    def _validate_patch(self, patch_content: str) -> Dict:
        """
        Validate patch against allowlist

        Returns:
            Dict with keys: valid (bool), violations (List[str]), files (List[str])
        """
        violations = []
        files_modified = []

        # Check patch size
        patch_lines = patch_content.count('\n') + 1
        if patch_lines > self.allowlist.max_patch_lines:
            violations.append(
                f"Patch too large: {patch_lines} lines (max: {self.allowlist.max_patch_lines})"
            )

        # Parse patch to extract file operations
        current_file = None
        for line in patch_content.split('\n'):
            # Detect file operations
            if line.startswith('diff --git'):
                # Extract filename from: diff --git a/path/to/file b/path/to/file
                match = re.search(r'diff --git a/(.+?) b/(.+)', line)
                if match:
                    current_file = match.group(2)  # Use 'b' version (after change)
                    files_modified.append(current_file)

            elif line.startswith('deleted file'):
                if 'delete_file' in self.allowlist.forbidden_operations:
                    violations.append(f"Forbidden operation: delete_file ({current_file})")

            elif line.startswith('rename from'):
                if 'rename_file' in self.allowlist.forbidden_operations:
                    violations.append(f"Forbidden operation: rename_file ({current_file})")

            elif line.startswith('GIT binary patch'):
                if 'binary_change' in self.allowlist.forbidden_operations:
                    violations.append(f"Forbidden operation: binary_change ({current_file})")

            elif 'Subproject commit' in line:
                if 'submodule_change' in self.allowlist.forbidden_operations:
                    violations.append(f"Forbidden operation: submodule_change ({current_file})")

        # Check files against allowlist patterns
        for file_path in files_modified:
            if not self._file_matches_allowlist(file_path):
                violations.append(f"File not in allowlist: {file_path}")

        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "files": files_modified
        }

    def _file_matches_allowlist(self, file_path: str) -> bool:
        """Check if file matches any allowlist pattern"""
        from pathlib import PurePosixPath

        # Normalize to POSIX path for consistent glob matching
        path = PurePosixPath(file_path.replace('\\', '/'))

        for pattern in self.allowlist.allowed_file_patterns:
            # Use full_match approach: match the pattern against the full path
            # For patterns like "modules/**/*.py", we need to check if the path starts correctly

            # Simple implementation: if pattern contains **, expand it
            if '**' in pattern:
                # Convert modules/**/*.py to regex-like matching
                # Split on ** and match parts
                parts = pattern.split('**/')
                if len(parts) == 2:
                    prefix, suffix = parts
                    # Check if path starts with prefix and matches suffix pattern
                    if str(path).startswith(prefix.rstrip('/')):
                        # Extract the part after prefix and match against suffix
                        remaining = str(path)[len(prefix.rstrip('/')):]
                        if remaining.startswith('/'):
                            remaining = remaining[1:]
                        # Use Path.match for the suffix (which may contain single *)
                        if PurePosixPath(remaining).match(suffix):
                            return True
            else:
                # No **, use direct match
                if path.match(pattern):
                    return True

        return False

    def _git_apply_check(self, patch_content: str) -> Dict:
        """
        Run git apply --check (dry-run validation)

        Returns:
            Dict with keys: success (bool), error (Optional[str])
        """
        try:
            # Write patch to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False, encoding='utf-8') as f:
                f.write(patch_content)
                patch_file = f.name

            # Run git apply --check
            result = subprocess.run(
                ['git', 'apply', '--check', patch_file],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=10
            )

            # Clean up temp file
            Path(patch_file).unlink()

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr.strip() if result.stderr else "git apply --check failed"
                }

            return {"success": True, "error": None}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "git apply --check timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _git_apply(self, patch_content: str) -> Dict:
        """
        Apply patch with git apply

        Returns:
            Dict with keys: success (bool), error (Optional[str])
        """
        try:
            # Write patch to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False, encoding='utf-8') as f:
                f.write(patch_content)
                patch_file = f.name

            # Run git apply
            result = subprocess.run(
                ['git', 'apply', patch_file],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=10
            )

            # Clean up temp file
            Path(patch_file).unlink()

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr.strip() if result.stderr else "git apply failed"
                }

            return {"success": True, "error": None}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "git apply timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Example usage
if __name__ == "__main__":
    # Configure allowlist for UTF-8 header fixes
    allowlist = PatchAllowlist(
        allowed_file_patterns=[
            "modules/**/*.py",           # All Python modules
            "holo_index/**/*.py",         # HoloIndex Python files
            "*.py"                        # Root-level Python files
        ],
        forbidden_operations={
            'delete_file',
            'binary_change',
            'submodule_change',
            'rename_file'
        },
        max_patch_lines=200  # Allow slightly larger patches for multi-file fixes
    )

    # Initialize executor
    executor = PatchExecutor(
        repo_root=Path("."),
        allowlist=allowlist
    )

    # Example patch: Add UTF-8 header to a file
    example_patch = """diff --git a/modules/test/example.py b/modules/test/example.py
index 1234567..89abcdef 100644
--- a/modules/test/example.py
+++ b/modules/test/example.py
@@ -1,3 +1,4 @@
+# -*- coding: utf-8 -*-
 \"\"\"
 Example module
 \"\"\"
"""

    # Dry-run validation
    result = executor.apply_patch(
        patch_content=example_patch,
        patch_description="Add UTF-8 header to example.py",
        dry_run=True
    )

    print(f"[TEST] Validation result: {result}")
