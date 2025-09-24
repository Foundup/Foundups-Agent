"""
Module Health Audit System for HoloIndex
WSP Compliance: WSP 87 (Code Navigation), WSP 49 (Module Structure)

Provides real-time health checks for code modules including:
- Size audits (line count thresholds)
- Structure audits (required scaffolding)
- Future: Refactor suggestions, violation history, churn metrics
"""

from .size_audit import SizeAuditor, FileSizeResult
from .structure_audit import StructureAuditor, StructureResult

__all__ = [
    'SizeAuditor',
    'FileSizeResult',
    'StructureAuditor',
    'StructureResult'
]
