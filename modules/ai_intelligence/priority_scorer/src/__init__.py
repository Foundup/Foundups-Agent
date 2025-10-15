"""
Priority Scorer Module - AI-Powered Priority Intelligence

WSP Compliant: WSP 49 (Module Structure), WSP 54 (Agent Duties)
Provides AI-powered priority scoring for autonomous development operations.

REFACTORED ARCHITECTURE:
- priority_scorer.py: Main orchestration layer (refactored)
- data_structures.py: Data models and serialization
- scoring_config.py: Configuration constants and thresholds
- scoring_engine.py: Core scoring algorithms and business logic
- persistence.py: File I/O operations and data persistence
"""

from .priority_scorer import PriorityScorer, score_item, score_items
from .data_structures import PriorityScore, ScoringFactors, PriorityLevel
from .scoring_config import ScoringConfig
from .scoring_engine import ScoringEngine
from .persistence import ScorePersistence

__version__ = "1.0.0"
__all__ = [
    "PriorityScorer",
    "PriorityScore",
    "ScoringFactors",
    "PriorityLevel",
    "ScoringConfig",
    "ScoringEngine",
    "ScorePersistence",
    "score_item",
    "score_items"
] 