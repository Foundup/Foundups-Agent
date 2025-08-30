"""
Recursive Improvement Module
WSP 48 Level 1 Protocol Implementation

Automatic learning from errors, pattern extraction, and self-improvement.
"""

from modules.infrastructure.wre_core.recursive_improvement.src.core import PatternType, ErrorPattern, Solution, Improvement
from modules.infrastructure.wre_core.recursive_improvement.src.persistence import QuantumState, QuantumStatePersistence
from modules.infrastructure.wre_core.recursive_improvement.src.learning import RecursiveLearningEngine, process_error, install_global_handler, get_engine

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