#!/usr/bin/env python3
"""
HoloIndex Phase 3: Adaptive Learning Package
===========================================

[MLE-STAR REMOVED - DEEMED VIBECODING - 2025-09-23]
MLE-STAR was removed from the codebase as it was pure documentation without
functional implementation (0.0% validation score, no working code).

Now implements direct adaptive learning through:
- Intelligent query enhancement using pattern analysis
- Search optimization through ensemble ranking
- Response improvement via context-aware processing

WSP Compliance: WSP 48 (Recursive Improvement), WSP 54 (Agent Coordination)
"""

from .adaptive_query_processor import AdaptiveQueryProcessor, AdaptiveQueryResult
from .vector_search_optimizer import VectorSearchOptimizer, OptimizedSearchResults
from .llm_response_optimizer import LLMResponseOptimizer, OptimizedResponse
from .memory_architecture_evolution import MemoryArchitectureEvolution, MemoryOptimizationResult
from .adaptive_learning_orchestrator import AdaptiveLearningOrchestrator

__all__ = [
    'AdaptiveQueryProcessor',
    'AdaptiveQueryResult',
    'VectorSearchOptimizer',
    'OptimizedSearchResults',
    'LLMResponseOptimizer',
    'OptimizedResponse',
    'MemoryArchitectureEvolution',
    'MemoryOptimizationResult',
    'AdaptiveLearningOrchestrator'
]

__version__ = "3.0.0"
__status__ = "operational"
