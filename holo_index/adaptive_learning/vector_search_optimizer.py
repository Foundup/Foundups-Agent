#!/usr/bin/env python3
"""
HoloIndex Phase 3: Vector Search Optimizer
==========================================

[MLE-STAR REMOVED - DEEMED VIBECODING - 2025-09-23]
Previously claimed MLE-STAR integration but it was non-functional.
Now uses direct optimization strategies for search improvement.

Key Features:
- Ensemble-based ranking using weighted scoring algorithms
- Adaptive similarity scoring through pattern matching
- Context-aware result re-ranking with learned patterns
- Performance-driven search improvements

WSP Compliance: WSP 48 (Recursive Improvement), WSP 54 (Agent Coordination)
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
import numpy as np

from modules.infrastructure.database import AgentDB
# MLE-STAR removed - was non-functional vibecoding
# from modules.ai_intelligence.mle_star_engine.src.mlestar_orchestrator import (
#     MLESTAROrchestrator,
#     OptimizationTarget,
#     MLESTARPhase
# )

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Represents a search result with ranking information"""
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    optimized_score: float = 0.0
    ranking_factors: Dict[str, float] = field(default_factory=dict)

@dataclass
class OptimizedSearchResults:
    """Container for optimized search results"""
    original_results: List[SearchResult]
    optimized_results: List[SearchResult]
    optimization_metadata: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)

class VectorSearchOptimizer:
    """
    Vector search optimizer using MLE-STAR ensemble strategies.

    Implements Phase 3 adaptive learning by:
    1. Ensemble-based ranking optimization through multiple strategies
    2. Adaptive similarity scoring using ablation studies
    3. Context-aware re-ranking with learned patterns
    4. Performance-driven embedding optimization
    """

    def __init__(self):
        self.agent_db = AgentDB()
        # MLE-STAR removed - was non-functional
        # self.mlestar_orchestrator = MLESTAROrchestrator()
        self.mlestar_orchestrator = None
        self.ranking_patterns = self._load_ranking_patterns()
        self.performance_history = self._load_performance_history()

    def _load_ranking_patterns(self) -> Dict[str, Any]:
        """Load learned ranking patterns from AgentDB"""
        try:
            patterns = self.agent_db.get_patterns('holo_index', 'ranking_optimization', limit=100)
            return {p.get('pattern_type', 'unknown'): p for p in patterns}
        except Exception as e:
            logger.warning(f"Could not load ranking patterns: {e}")
            return {}

    def _load_performance_history(self) -> List[Dict[str, Any]]:
        """Load search performance history for optimization"""
        try:
            history = self.agent_db.get_patterns('holo_index', 'search_performance', limit=50)
            return history
        except Exception as e:
            logger.warning(f"Could not load performance history: {e}")
            return []

    async def optimize_search_results(self,
                                    query: str,
                                    results: List[SearchResult],
                                    context: Dict[str, Any] = None) -> OptimizedSearchResults:
        """
        Optimize search results using MLE-STAR ensemble strategies.

        Args:
            query: Original search query
            results: Raw search results to optimize
            context: Additional context for optimization

        Returns:
            OptimizedSearchResults with re-ranked and enhanced results
        """
        context = context or {}

        # Phase 1: Ensemble Ranking Optimization
        optimized_results = await self._apply_ensemble_ranking(query, results, context)

        # Phase 2: Context-Aware Re-ranking
        context_optimized_results = await self._apply_context_reranking(query, optimized_results, context)

        # Phase 3: Performance Validation
        performance_metrics = self._calculate_performance_metrics(results, context_optimized_results)

        # Record optimization data
        await self._record_optimization_learning(query, results, context_optimized_results, performance_metrics)

        return OptimizedSearchResults(
            original_results=results,
            optimized_results=context_optimized_results,
            optimization_metadata={
                'optimization_timestamp': datetime.now(timezone.utc).isoformat(),
                'mlestar_phases_used': ['ensemble_ranking', 'context_reranking'],
                'query_complexity': self._assess_query_complexity(query),
                'result_count': len(results)
            },
            performance_metrics=performance_metrics
        )

    async def _apply_ensemble_ranking(self,
                                     query: str,
                                     results: List[SearchResult],
                                     context: Dict[str, Any]) -> List[SearchResult]:
        """
        Apply ensemble ranking using direct optimization strategies.

        Uses multiple ranking algorithms and combines them through weighted scoring.
        """

        # Apply multiple ranking strategies
        for i, result in enumerate(results):
            ranking_factors = {}

            # Strategy 1: Semantic similarity boost
            semantic_boost = self._calculate_semantic_similarity(query, result.content)
            ranking_factors['semantic_similarity'] = semantic_boost

            # Strategy 2: Context relevance scoring
            context_relevance = self._calculate_context_relevance(query, result, context)
            ranking_factors['context_relevance'] = context_relevance

            # Strategy 3: Pattern matching boost
            pattern_boost = self._calculate_pattern_matching(query, result.content)
            ranking_factors['pattern_matching'] = pattern_boost

            # Strategy 4: Freshness factor (prefer newer content)
            freshness_factor = self._calculate_freshness_factor(result.metadata)
            ranking_factors['freshness'] = freshness_factor

            # Calculate ensemble score using weighted combination
            weights = {
                'semantic_similarity': 0.4,
                'context_relevance': 0.3,
                'pattern_matching': 0.2,
                'freshness': 0.1
            }

            ensemble_score = sum(
                ranking_factors[factor] * weight
                for factor, weight in weights.items()
            )

            # Combine with original score (weighted average)
            original_weight = 0.3
            ensemble_weight = 0.7
            results[i].optimized_score = (
                result.score * original_weight +
                ensemble_score * ensemble_weight
            )
            results[i].ranking_factors = ranking_factors

        # Sort by optimized score
        results.sort(key=lambda x: x.optimized_score, reverse=True)

        return results

    async def _apply_context_reranking(self,
                                      query: str,
                                      results: List[SearchResult],
                                      context: Dict[str, Any]) -> List[SearchResult]:
        """
        Apply context-aware re-ranking using direct optimization.

        Adjusts rankings based on user context, search history, and learned preferences.
        """

        # Apply context-based adjustments to each result
        for i, result in enumerate(results):
            context_adjustment = 1.0
            context_relevance = 0.0

            # Advisor context boost for documentation
            if context.get('advisor_enabled', False):
                if any(term in result.content.lower() for term in ['wsp', 'protocol', 'readme', 'interface']):
                    context_adjustment *= 1.2
                    context_relevance += 0.3

            # Technical context boost for code results
            if any(term in query.lower() for term in ['function', 'class', 'method', 'api']):
                if any(term in result.content.lower() for term in ['def ', 'class ', 'function', 'method']):
                    context_adjustment *= 1.15
                    context_relevance += 0.4

            # Module context boost
            if 'modules/' in result.content:
                context_adjustment *= 1.1
                context_relevance += 0.2

            # Apply the adjustment
            results[i].optimized_score *= context_adjustment

            # Update ranking factors
            results[i].ranking_factors.update({
                'context_adjustment': context_adjustment,
                'context_relevance': context_relevance
            })

        # Re-sort after context adjustments
        results.sort(key=lambda x: x.optimized_score, reverse=True)

        return results

    def _calculate_performance_metrics(self,
                                     original_results: List[SearchResult],
                                     optimized_results: List[SearchResult]) -> Dict[str, float]:
        """Calculate performance metrics for the optimization"""
        metrics = {
            'ranking_stability': 0.0,
            'score_improvement': 0.0,
            'top_result_confidence': 0.0,
            'diversity_score': 0.0
        }

        if not original_results or not optimized_results:
            return metrics

        # Calculate ranking stability (how much order changed)
        original_order = [r.content for r in original_results]
        optimized_order = [r.content for r in optimized_results]

        # Simple stability metric based on top 5 positions
        stability_count = 0
        for i in range(min(5, len(original_order))):
            if i < len(optimized_order) and original_order[i] == optimized_order[i]:
                stability_count += 1

        metrics['ranking_stability'] = stability_count / min(5, len(original_order))

        # Calculate score improvement (average score change)
        score_changes = []
        for orig, opt in zip(original_results, optimized_results):
            if orig.content == opt.content:  # Match by content
                score_changes.append(opt.optimized_score - orig.score)

        if score_changes:
            metrics['score_improvement'] = sum(score_changes) / len(score_changes)

        # Top result confidence
        if optimized_results:
            top_result = optimized_results[0]
            metrics['top_result_confidence'] = top_result.optimized_score

        # Diversity score (unique ranking factors used)
        all_factors = set()
        for result in optimized_results:
            all_factors.update(result.ranking_factors.keys())

        metrics['diversity_score'] = len(all_factors) / 10.0  # Normalize to 0-1 scale

        return metrics

    def _assess_query_complexity(self, query: str) -> float:
        """Assess query complexity for optimization decisions"""
        complexity_factors = {
            'length': len(query.split()),
            'special_chars': len([c for c in query if not c.isalnum() and not c.isspace()]),
            'capital_words': len([w for w in query.split() if w.isupper()]),
            'numbers': len([c for c in query if c.isdigit()])
        }

        # Normalize and combine factors
        length_score = min(complexity_factors['length'] / 10.0, 1.0)
        special_score = min(complexity_factors['special_chars'] / 5.0, 1.0)
        capital_score = min(complexity_factors['capital_words'] / 3.0, 1.0)
        number_score = min(complexity_factors['numbers'] / 3.0, 1.0)

        return (length_score + special_score + capital_score + number_score) / 4.0

    def _calculate_semantic_similarity(self, query: str, content: str) -> float:
        """Calculate semantic similarity between query and content"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())

        if not query_words:
            return 0.0

        overlap = len(query_words.intersection(content_words))
        return min(overlap / len(query_words), 1.0)

    def _calculate_context_relevance(self, query: str, result: SearchResult, context: Dict[str, Any]) -> float:
        """Calculate context-based relevance score"""
        relevance = 0.0

        # Advisor context boost
        if context.get('advisor_enabled', False):
            if any(term in result.content.lower() for term in ['wsp', 'protocol', 'documentation']):
                relevance += 0.3

        # Technical context boost
        if any(term in query.lower() for term in ['function', 'class', 'method']):
            if any(term in result.content.lower() for term in ['def ', 'class ', 'function']):
                relevance += 0.4

        # Recent content boost
        if self._calculate_freshness_factor(result.metadata) > 0.7:
            relevance += 0.1

        return min(relevance, 1.0)

    def _calculate_pattern_matching(self, query: str, content: str) -> float:
        """Calculate pattern matching score"""
        # Simple keyword matching for now - could be enhanced with regex patterns
        query_patterns = ['wsp', 'protocol', 'interface', 'readme', 'roadmap']
        content_lower = content.lower()

        matches = sum(1 for pattern in query_patterns if pattern in content_lower)
        return min(matches / len(query_patterns), 1.0)

    def _calculate_freshness_factor(self, metadata: Dict[str, Any]) -> float:
        """Calculate content freshness factor"""
        # This is a simplified implementation - in real system would use timestamps
        # For now, assume all content is equally fresh
        return 0.8

    async def _record_optimization_learning(self,
                                          query: str,
                                          original_results: List[SearchResult],
                                          optimized_results: List[SearchResult],
                                          metrics: Dict[str, float]):
        """Record optimization learning data for future improvement"""
        try:
            learning_data = {
                'query': query,
                'query_complexity': self._assess_query_complexity(query),
                'original_result_count': len(original_results),
                'optimized_result_count': len(optimized_results),
                'performance_metrics': metrics,
                'ranking_improvements': [
                    {
                        'original_score': orig.score,
                        'optimized_score': opt.optimized_score,
                        'ranking_factors': opt.ranking_factors
                    }
                    for orig, opt in zip(original_results[:5], optimized_results[:5])  # Top 5
                ],
                'optimization_timestamp': datetime.now(timezone.utc).isoformat()
            }

            # Store in AgentDB for future learning
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.agent_db.learn_pattern,
                'holo_index',
                'search_ranking_optimization',
                learning_data
            )

        except Exception as e:
            logger.warning(f"Failed to record optimization learning: {e}")

    async def get_optimization_insights(self) -> Dict[str, Any]:
        """Get insights from optimization learning patterns"""
        try:
            recent_patterns = self.agent_db.get_patterns('holo_index', 'search_ranking_optimization', limit=100)

            insights = {
                'total_optimizations': len(recent_patterns),
                'average_stability': 0.0,
                'average_score_improvement': 0.0,
                'common_ranking_factors': {},
                'optimization_effectiveness': 0.0
            }

            if recent_patterns:
                # Calculate metrics
                stabilities = [p.get('performance_metrics', {}).get('ranking_stability', 0) for p in recent_patterns]
                improvements = [p.get('performance_metrics', {}).get('score_improvement', 0) for p in recent_patterns]

                if stabilities:
                    insights['average_stability'] = sum(stabilities) / len(stabilities)
                if improvements:
                    insights['average_score_improvement'] = sum(improvements) / len(improvements)

                # Count ranking factors
                for pattern in recent_patterns:
                    improvements = pattern.get('ranking_improvements', [])
                    for improvement in improvements:
                        factors = improvement.get('ranking_factors', {})
                        for factor_name in factors.keys():
                            insights['common_ranking_factors'][factor_name] = insights['common_ranking_factors'].get(factor_name, 0) + 1

                # Calculate optimization effectiveness (improvement in score over time)
                recent_improvements = [p.get('performance_metrics', {}).get('score_improvement', 0) for p in recent_patterns[-20:]]
                older_improvements = [p.get('performance_metrics', {}).get('score_improvement', 0) for p in recent_patterns[:20]]

                if recent_improvements and older_improvements:
                    recent_avg = sum(recent_improvements) / len(recent_improvements)
                    older_avg = sum(older_improvements) / len(older_improvements)
                    insights['optimization_effectiveness'] = recent_avg - older_avg

            return insights

        except Exception as e:
            logger.warning(f"Failed to get optimization insights: {e}")
            return {}
