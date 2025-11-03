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

Size Audit Module - WSP 87 Compliance
Monitors file sizes and line counts against WSP thresholds.

Thresholds from WSP_87_Code_Navigation_Protocol.md:141-142:
- Guideline: 800-1000 lines for complex modules
- Hard limit: 1500 lines before mandatory split
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple
from enum import Enum


class RiskTier(Enum):
    """Risk levels for file size."""
    OK = "ok"        # Under 800 lines
    WARN = "warn"    # 800-1000 lines (guideline threshold)
    CRITICAL = "critical"  # Over 1000 lines (approaching hard limit)


@dataclass
class FileSizeResult:
    """Result of a file size audit."""
    path: Path
    line_count: int
    byte_size: int
    risk_tier: RiskTier
    wsp_reference: str = "WSP 87: Code Navigation Protocol"

    @property
    def needs_attention(self) -> bool:
        """Check if this file needs attention."""
        return self.risk_tier != RiskTier.OK

    @property
    def guidance(self) -> str:
        """Get guidance based on risk tier."""
        if self.risk_tier == RiskTier.OK:
            return f"File size acceptable ({self.line_count} lines)"
        elif self.risk_tier == RiskTier.WARN:
            return f"File approaching guideline limit ({self.line_count}/800-1000 lines). Consider refactoring."
        else:  # CRITICAL
            return f"File exceeds guideline ({self.line_count} lines, limit 1000). Mandatory split at 1500 lines."


class SizeAuditor:
    """
    Auditor for file size compliance per WSP 87.

    Thresholds (WSP_87_Code_Navigation_Protocol.md:141-142):
    - OK: < 800 lines
    - WARN: 800-1000 lines (guideline range)
    - CRITICAL: > 1000 lines (hard limit at 1500)
    """

    # Thresholds from WSP 87
    THRESHOLD_OK = 800        # Below this is fine
    THRESHOLD_WARN = 1000     # Guideline upper limit
    THRESHOLD_HARD = 1500     # Mandatory split required

    def __init__(self):
        """Initialize the size auditor."""
        pass

    def audit_file(self, file_path: Path) -> Optional[FileSizeResult]:
        """
        Audit a single file for size compliance.

        Args:
            file_path: Path to the file to audit

        Returns:
            FileSizeResult with metrics and risk tier, or None if file doesn't exist
        """
        if not file_path.exists():
            return None

        if not file_path.is_file():
            return None

        # Skip non-Python files for now (can be expanded)
        if file_path.suffix not in ['.py', '.js', '.ts', '.tsx', '.jsx']:
            return None

        try:
            # Count lines and bytes
            line_count = 0
            byte_size = file_path.stat().st_size

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for _ in f:
                    line_count += 1

            # Determine risk tier based on WSP 87 thresholds
            risk_tier = self._calculate_risk_tier(line_count)

            return FileSizeResult(
                path=file_path,
                line_count=line_count,
                byte_size=byte_size,
                risk_tier=risk_tier
            )

        except Exception as e:
            # If we can't read the file, return None
            return None

    def _calculate_risk_tier(self, line_count: int) -> RiskTier:
        """
        Calculate risk tier based on line count.

        Per WSP_87_Code_Navigation_Protocol.md:141-142:
        - OK: < 800 lines
        - WARN: 800-1000 lines (guideline)
        - CRITICAL: > 1000 lines (approaching hard limit of 1500)
        """
        if line_count < self.THRESHOLD_OK:
            return RiskTier.OK
        elif line_count <= self.THRESHOLD_WARN:
            return RiskTier.WARN
        else:
            return RiskTier.CRITICAL

    def audit_module(self, module_path: Path) -> list[FileSizeResult]:
        """
        Audit all files in a module.

        Args:
            module_path: Path to the module directory

        Returns:
            List of FileSizeResult for files needing attention
        """
        results = []

        if not module_path.is_dir():
            return results

        # Check all Python files in the module
        for py_file in module_path.rglob('*.py'):
            # Skip __pycache__ and test files
            if '__pycache__' in str(py_file):
                continue
            if 'test_' in py_file.name or '_test.py' in py_file.name:
                continue

            result = self.audit_file(py_file)
            if result and result.needs_attention:
                results.append(result)

        return results