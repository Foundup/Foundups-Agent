#!/usr/bin/env python3
"""
Structure Audit Module - WSP 49 Compliance
Ensures modules have required scaffolding files.

Required structure per WSP 49:
- README.md (module overview)
- INTERFACE.md (public API)
- ModLog.md (change history)
- tests/ directory
- tests/TestModLog.md (test evolution log)
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class StructureResult:
    """Result of a module structure audit."""
    module_path: Path
    missing_artifacts: List[str] = field(default_factory=list)
    wsp_reference: str = "WSP 49: Module Directory Structure"

    @property
    def is_compliant(self) -> bool:
        """Check if module structure is compliant."""
        return len(self.missing_artifacts) == 0

    @property
    def todos(self) -> List[str]:
        """Generate TODO items for missing artifacts."""
        todos = []
        for artifact in self.missing_artifacts:
            if artifact == "README.md":
                todos.append(f"Create {self.module_path}/README.md with module overview and purpose")
            elif artifact == "INTERFACE.md":
                todos.append(f"Create {self.module_path}/INTERFACE.md documenting public API (WSP 11)")
            elif artifact == "ModLog.md":
                todos.append(f"Create {self.module_path}/ModLog.md for change tracking (WSP 22)")
            elif artifact == "tests/":
                todos.append(f"Create {self.module_path}/tests/ directory for test files")
            elif artifact == "tests/TestModLog.md":
                todos.append(f"Create {self.module_path}/tests/TestModLog.md for test evolution tracking")
            elif artifact == "src/":
                todos.append(f"Create {self.module_path}/src/ directory for source code")
            else:
                todos.append(f"Create {self.module_path}/{artifact}")
        return todos

    @property
    def guidance(self) -> str:
        """Get guidance message."""
        if self.is_compliant:
            return "Module structure is WSP 49 compliant"
        else:
            count = len(self.missing_artifacts)
            artifacts = ", ".join(self.missing_artifacts)
            return f"Module missing {count} required artifacts: {artifacts}"


class StructureAuditor:
    """
    Auditor for module structure compliance per WSP 49.

    Required artifacts:
    - README.md: Module overview and purpose
    - INTERFACE.md: Public API documentation (WSP 11)
    - ModLog.md: Change history (WSP 22)
    - src/: Source code directory
    - tests/: Test directory
    - tests/TestModLog.md: Test evolution log
    """

    # Required files per WSP 49
    REQUIRED_FILES = [
        "README.md",
        "INTERFACE.md",
        "ModLog.md"
    ]

    # Required directories
    REQUIRED_DIRS = [
        "src",
        "tests"
    ]

    # Required test artifacts
    REQUIRED_TEST_FILES = [
        "tests/TestModLog.md"
    ]

    def __init__(self):
        """Initialize the structure auditor."""
        pass

    def audit_module(self, module_path: Path) -> StructureResult:
        """
        Audit a module's structure for WSP 49 compliance.

        Args:
            module_path: Path to the module root directory

        Returns:
            StructureResult with missing artifacts
        """
        if not module_path.exists():
            # If module doesn't exist, all artifacts are missing
            return StructureResult(
                module_path=module_path,
                missing_artifacts=self.REQUIRED_FILES + [d + "/" for d in self.REQUIRED_DIRS] + self.REQUIRED_TEST_FILES
            )

        if not module_path.is_dir():
            # Not a directory
            return StructureResult(
                module_path=module_path,
                missing_artifacts=["Not a directory"]
            )

        missing = []

        # Check required files
        for required_file in self.REQUIRED_FILES:
            file_path = module_path / required_file
            if not file_path.exists():
                missing.append(required_file)

        # Check required directories
        for required_dir in self.REQUIRED_DIRS:
            dir_path = module_path / required_dir
            if not dir_path.exists() or not dir_path.is_dir():
                missing.append(f"{required_dir}/")

        # Check test-specific files (only if tests dir exists)
        tests_dir = module_path / "tests"
        if tests_dir.exists():
            test_modlog = tests_dir / "TestModLog.md"
            if not test_modlog.exists():
                missing.append("tests/TestModLog.md")
        elif "tests/" not in missing:
            # If tests dir is missing, TestModLog is implicitly missing
            missing.append("tests/TestModLog.md")

        return StructureResult(
            module_path=module_path,
            missing_artifacts=missing
        )

    def find_module_root(self, file_path: Path) -> Optional[Path]:
        """
        Find the module root directory for a given file.

        Looks for patterns like:
        - modules/{domain}/{module}/
        - holo_index/{package}/

        Args:
            file_path: Path to a file within a module

        Returns:
            Path to module root, or None if not found
        """
        path = file_path if file_path.is_dir() else file_path.parent

        # Walk up looking for module indicators
        while path != path.parent:
            # Check if this looks like a module root
            if self._is_module_root(path):
                return path

            # Check if we're in a modules/{domain}/{module} structure
            if path.parent.name == "modules" and path.parent.parent == path.parent.parent.parent:
                # We're at {module} level
                return path
            elif path.parent.parent.name == "modules":
                # We're below {module} level, go up
                if (path.parent / "README.md").exists() or (path.parent / "src").exists():
                    return path.parent

            # Go up one level
            path = path.parent

        return None

    def _is_module_root(self, path: Path) -> bool:
        """
        Check if a path looks like a module root.

        A module root typically has at least one of:
        - README.md
        - INTERFACE.md
        - ModLog.md
        - src/ directory
        - tests/ directory
        """
        indicators = [
            "README.md",
            "INTERFACE.md",
            "ModLog.md",
            "src",
            "tests"
        ]

        for indicator in indicators:
            if (path / indicator).exists():
                return True

        return False