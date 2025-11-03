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

Module Health Audit System for HoloIndex
WSP Compliance: WSP 87 (Code Navigation), WSP 49 (Module Structure)

Provides real-time health checks for code modules including:
- Size audits (line count thresholds)
- Structure audits (required scaffolding)
- Dependency audits (import tracing and orphan detection)
- Future: Refactor suggestions, violation history, churn metrics
"""

from .size_audit import SizeAuditor, FileSizeResult
from .structure_audit import StructureAuditor, StructureResult
from .dependency_audit import DependencyAuditor

__all__ = [
    'SizeAuditor',
    'FileSizeResult',
    'StructureAuditor',
    'StructureResult',
    'DependencyAuditor'
]
