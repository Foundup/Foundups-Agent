"""
Recursive Improvement Module
WSP 48 Level 1 Protocol Implementation

Automatic learning from errors, pattern extraction, and self-improvement.
"""

from .src.recursive_engine import (
    RecursiveLearningEngine,
    ErrorPattern,
    Solution,
    Improvement,
    PatternType,
    get_engine,
    process_error,
    install_global_handler
)

__version__ = "1.0.0"
__all__ = [
    "RecursiveLearningEngine",
    "ErrorPattern",
    "Solution",
    "Improvement",
    "PatternType",
    "get_engine",
    "process_error",
    "install_global_handler"
]

# Initialize global engine on import
_engine = get_engine()