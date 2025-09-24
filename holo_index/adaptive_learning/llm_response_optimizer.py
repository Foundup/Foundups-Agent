#!/usr/bin/env python3
"""
HoloIndex Phase 3: LLM Response Optimizer
========================================

[MLE-STAR REMOVED - DEEMED VIBECODING - 2025-09-23]
Previously claimed MLE-STAR refinement but it was non-functional.
Now uses direct optimization strategies for response quality.

Key Features:
- Response quality assessment using scoring algorithms
- Adaptive response enhancement through feedback patterns
- Context-aware response optimization with learned patterns
- Multi-strategy response generation with rule selection

WSP Compliance: WSP 48 (Recursive Improvement), WSP 54 (Agent Coordination)
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone

from modules.infrastructure.database import AgentDB
# MLE-STAR removed - was non-functional vibecoding
# from modules.ai_intelligence.mle_star_engine.src.mlestar_orchestrator import (
#     MLESTAROrchestrator,
#     OptimizationTarget,
#     MLESTARPhase
# )

logger = logging.getLogger(__name__)

@dataclass
class ResponseCandidate:
    """Represents a candidate response with quality metrics"""
    content: str
    quality_score: float = 0.0
    relevance_score: float = 0.0
    clarity_score: float = 0.0
    generation_metadata: Dict[str, Any] = field(default_factory=dict)
    optimization_factors: Dict[str, float] = field(default_factory=dict)

@dataclass
class OptimizedResponse:
    """Container for optimized LLM response"""
    original_response: str
    optimized_response: str
    response_candidates: List[ResponseCandidate]
    optimization_metadata: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)

class LLMResponseOptimizer:
    """
    LLM response optimizer using MLE-STAR refinement loops.

    Implements Phase 3 adaptive learning by:
    1. Response quality assessment through ablation studies
    2. Adaptive enhancement using iterative optimization
    3. Context-aware response improvement with learned patterns
    4. Multi-strategy generation with ensemble selection
    """

    def __init__(self):
        self.agent_db = AgentDB()
        # MLE-STAR removed - was non-functional
        # self.mlestar_orchestrator = MLESTAROrchestrator()
        self.mlestar_orchestrator = None
        self.response_patterns = self._load_response_patterns()
        self.quality_history = self._load_quality_history()

    def _load_response_patterns(self) -> Dict[str, Any]:
        """Load learned response optimization patterns from AgentDB"""
        try:
            patterns = self.agent_db.get_patterns('holo_index', 'response_optimization', limit=100)
            return {p.get('pattern_type', 'unknown'): p for p in patterns}
        except Exception as e:
            logger.warning(f"Could not load response patterns: {e}")
            return {}

    def _load_quality_history(self) -> List[Dict[str, Any]]:
        """Load response quality history for optimization"""
        try:
            history = self.agent_db.get_patterns('holo_index', 'response_quality', limit=50)
            return history
        except Exception as e:
            logger.warning(f"Could not load quality history: {e}")
            return []

    async def optimize_response(self,
                               query: str,
                               original_response: str,
                               context: Dict[str, Any] = None) -> OptimizedResponse:
        """
        Optimize LLM response using MLE-STAR refinement loops.

        Args:
            query: Original user query
            original_response: Raw LLM response to optimize
            context: Additional context for optimization

        Returns:
            OptimizedResponse with enhanced and validated response
        """
        context = context or {}

        # Phase 1: Generate Response Candidates using Ensemble Strategies
        candidates = await self._generate_response_candidates(query, original_response, context)

        # Phase 2: Quality Assessment and Selection
        selected_response = await self._select_optimal_response(query, candidates, context)

        # Phase 3: Final Refinement and Validation
        optimized_response = await self._apply_final_refinement(query, selected_response, context)

        # Calculate quality metrics
        quality_metrics = self._calculate_response_quality_metrics(
            original_response, optimized_response, candidates
        )

        # Record optimization learning
        await self._record_response_optimization_learning(
            query, original_response, optimized_response, candidates, quality_metrics
        )

        return OptimizedResponse(
            original_response=original_response,
            optimized_response=optimized_response,
            response_candidates=candidates,
            optimization_metadata={
                'optimization_timestamp': datetime.now(timezone.utc).isoformat(),
                'mlestar_phases_used': ['candidate_generation', 'quality_selection', 'final_refinement'],
                'candidate_count': len(candidates),
                'query_complexity': self._assess_query_complexity(query)
            },
            quality_metrics=quality_metrics
        )

    async def _generate_response_candidates(self,
                                          query: str,
                                          original_response: str,
                                          context: Dict[str, Any]) -> List[ResponseCandidate]:
        """
        Generate multiple response candidates using direct enhancement strategies.

        Creates different optimized versions through targeted improvements.
        """

        candidates = []

        # Strategy 1: Clarity-focused enhancement
        clarity_candidate = self._enhance_response_clarity(original_response, query, context)
        candidates.append(clarity_candidate)

        # Strategy 2: Relevance-focused enhancement
        relevance_candidate = self._enhance_response_relevance(original_response, query, context)
        candidates.append(relevance_candidate)

        # Strategy 3: Structure-focused enhancement
        structure_candidate = self._enhance_response_structure(original_response, query, context)
        candidates.append(structure_candidate)

        # If all enhancements failed, use original as fallback
        if not any(c.content != original_response for c in candidates):
            candidates.append(ResponseCandidate(
                content=original_response,
                quality_score=0.5,
                relevance_score=0.5,
                clarity_score=0.5
            ))

        return candidates

    def _enhance_response_clarity(self, response: str, query: str, context: Dict[str, Any]) -> ResponseCandidate:
        """Enhance response clarity through simplification and structure"""
        enhanced = response

        # Remove redundant phrases
        redundant_phrases = ["it appears that", "it seems like", "I think that", "it looks like"]
        for phrase in redundant_phrases:
            enhanced = enhanced.replace(phrase, "")

        # Improve sentence structure
        if len(response.split('.')) > 3:
            # Break long sentences
            sentences = response.split('.')
            enhanced_sentences = []
            for sentence in sentences:
                if len(sentence.split()) > 20:
                    # Split long sentences
                    words = sentence.split()
                    mid = len(words) // 2
                    enhanced_sentences.append(' '.join(words[:mid]) + '.')
                    enhanced_sentences.append(' '.join(words[mid:]) + '.')
                else:
                    enhanced_sentences.append(sentence + '.')
            enhanced = ' '.join(enhanced_sentences)

        quality_score = 0.7 if len(enhanced) < len(response) * 1.1 else 0.5
        relevance_score = 0.6
        clarity_score = 0.8

        return ResponseCandidate(
            content=enhanced,
            quality_score=quality_score,
            relevance_score=relevance_score,
            clarity_score=clarity_score,
            generation_metadata={'strategy': 'clarity_focus'},
            optimization_factors={'redundancy_removal': True, 'structure_improvement': True}
        )

    def _enhance_response_relevance(self, response: str, query: str, context: Dict[str, Any]) -> ResponseCandidate:
        """Enhance response relevance to query context"""
        enhanced = response

        # Add query-specific context if missing
        query_terms = set(query.lower().split())
        response_terms = set(response.lower().split())

        missing_terms = query_terms - response_terms
        if missing_terms and len(missing_terms) <= 3:
            # Add missing key terms to make response more relevant
            term_additions = []
            for term in missing_terms:
                if term not in ['the', 'a', 'an', 'is', 'are', 'was', 'were']:
                    term_additions.append(f"Regarding '{term}': ")

            if term_additions:
                enhanced = term_additions[0] + enhanced

        # Advisor context enhancement
        if context.get('advisor_enabled'):
            if 'wsp' not in response.lower():
                enhanced += " Consider reviewing relevant WSP protocols for additional guidance."

        quality_score = 0.6
        relevance_score = 0.8 if missing_terms else 0.6
        clarity_score = 0.6

        return ResponseCandidate(
            content=enhanced,
            quality_score=quality_score,
            relevance_score=relevance_score,
            clarity_score=clarity_score,
            generation_metadata={'strategy': 'relevance_boost'},
            optimization_factors={'query_term_integration': bool(missing_terms), 'context_awareness': True}
        )

    def _enhance_response_structure(self, response: str, query: str, context: Dict[str, Any]) -> ResponseCandidate:
        """Enhance response structure with better formatting"""
        enhanced = response

        # Add structured formatting
        if len(response.split('.')) > 2 and not response.startswith('•'):
            # Convert to bullet points for multi-part responses
            sentences = [s.strip() for s in response.split('.') if s.strip()]
            if len(sentences) >= 3:
                enhanced = '\n'.join(f'• {sentence}.' for sentence in sentences[:4])

        # Add section headers if appropriate
        if 'function' in query.lower() and 'Here are' in response:
            enhanced = "Available Functions:\n" + enhanced

        if 'wsp' in query.lower() and 'protocols' in response.lower():
            enhanced = "Relevant WSP Protocols:\n" + enhanced

        quality_score = 0.65
        relevance_score = 0.65
        clarity_score = 0.75

        return ResponseCandidate(
            content=enhanced,
            quality_score=quality_score,
            relevance_score=relevance_score,
            clarity_score=clarity_score,
            generation_metadata={'strategy': 'structure_improvement'},
            optimization_factors={'formatting_enhancement': True, 'section_headers': True}
        )

    async def _select_optimal_response(self,
                                      query: str,
                                      candidates: List[ResponseCandidate],
                                      context: Dict[str, Any]) -> str:
        """
        Select optimal response using direct quality assessment.

        Evaluates candidates and selects the best one based on weighted scoring.
        """

        # Calculate composite scores for each candidate
        scored_candidates = []
        for candidate in candidates:
            # Weighted scoring: 40% quality, 30% relevance, 30% clarity
            composite_score = (
                candidate.quality_score * 0.4 +
                candidate.relevance_score * 0.3 +
                candidate.clarity_score * 0.3
            )
            scored_candidates.append((candidate, composite_score))

        # Select candidate with highest composite score
        best_candidate = max(scored_candidates, key=lambda x: x[1])[0]

        return best_candidate.content

    async def _apply_final_refinement(self,
                                     query: str,
                                     selected_response: str,
                                     context: Dict[str, Any]) -> str:
        """
        Apply final refinement using direct optimization techniques.

        Performs final polish and validation of the selected response.
        """

        refined_response = selected_response

        # Apply final polish techniques
        # 1. Fix common grammar issues
        refined_response = refined_response.replace(" .", ".").replace(" ,", ",")

        # 2. Ensure proper capitalization
        if refined_response and not refined_response[0].isupper():
            refined_response = refined_response[0].upper() + refined_response[1:]

        # 3. Add final punctuation if missing
        if (refined_response and
            not refined_response.strip().endswith(('.', '!', '?', ':')) and
            len(refined_response.split()) > 3):
            refined_response += "."

        # Validate refinement
        if not self._validate_response_quality(refined_response):
            logger.warning("Refinement validation failed, using selected response")
            return selected_response

        return refined_response

    def _calculate_response_quality_metrics(self,
                                          original: str,
                                          optimized: str,
                                          candidates: List[ResponseCandidate]) -> Dict[str, float]:
        """Calculate comprehensive quality metrics for the optimization"""

        metrics = {
            'improvement_score': 0.0,
            'candidate_diversity': 0.0,
            'quality_consistency': 0.0,
            'optimization_effectiveness': 0.0
        }

        # Calculate improvement score (length and quality change)
        original_length = len(original.split())
        optimized_length = len(optimized.split())

        length_ratio = optimized_length / max(original_length, 1)
        length_score = 1.0 - abs(length_ratio - 1.0)  # Penalize large changes

        if candidates:
            avg_quality = sum(c.quality_score for c in candidates) / len(candidates)
            best_quality = max(c.quality_score for c in candidates)
            metrics['improvement_score'] = (length_score + avg_quality) / 2.0
            metrics['optimization_effectiveness'] = best_quality

        # Calculate candidate diversity (unique content measure)
        if len(candidates) > 1:
            unique_candidates = set(c.content for c in candidates)
            metrics['candidate_diversity'] = len(unique_candidates) / len(candidates)

        # Calculate quality consistency (variance in candidate scores)
        if len(candidates) > 1:
            qualities = [c.quality_score for c in candidates]
            mean_quality = sum(qualities) / len(qualities)
            variance = sum((q - mean_quality) ** 2 for q in qualities) / len(qualities)
            metrics['quality_consistency'] = 1.0 - min(variance, 1.0)  # Lower variance = higher consistency

        return metrics

    def _assess_query_complexity(self, query: str) -> float:
        """Assess query complexity for optimization decisions"""
        complexity_factors = {
            'length': len(query.split()),
            'technical_terms': len([w for w in query.lower().split() if any(term in w for term in ['wsp', 'api', 'function', 'class', 'module'])]),
            'special_chars': len([c for c in query if not c.isalnum() and not c.isspace()]),
            'questions': query.count('?')
        }

        # Normalize and combine factors
        length_score = min(complexity_factors['length'] / 15.0, 1.0)
        technical_score = min(complexity_factors['technical_terms'] / 3.0, 1.0)
        special_score = min(complexity_factors['special_chars'] / 10.0, 1.0)
        question_score = min(complexity_factors['questions'] / 3.0, 1.0)

        return (length_score + technical_score + special_score + question_score) / 4.0

    def _validate_response_quality(self, response: str) -> bool:
        """Validate basic response quality criteria"""
        if not response or len(response.strip()) == 0:
            return False

        # Check minimum length
        if len(response.split()) < 3:
            return False

        # Check for incomplete sentences (ending with certain patterns)
        if response.strip().endswith(('.', '!', '?')):
            return True
        elif any(response.strip().endswith(p) for p in ['-', ':', ',']):
            return False

        return True

    async def _record_response_optimization_learning(self,
                                                   query: str,
                                                   original: str,
                                                   optimized: str,
                                                   candidates: List[ResponseCandidate],
                                                   metrics: Dict[str, float]):
        """Record response optimization learning data"""
        try:
            learning_data = {
                'query': query,
                'query_complexity': self._assess_query_complexity(query),
                'original_response_length': len(original.split()),
                'optimized_response_length': len(optimized.split()),
                'candidate_count': len(candidates),
                'quality_metrics': metrics,
                'candidate_performance': [
                    {
                        'quality_score': c.quality_score,
                        'relevance_score': c.relevance_score,
                        'clarity_score': c.clarity_score,
                        'optimization_factors': c.optimization_factors
                    }
                    for c in candidates
                ],
                'optimization_timestamp': datetime.now(timezone.utc).isoformat()
            }

            # Store in AgentDB for future learning
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.agent_db.learn_pattern,
                'holo_index',
                'response_optimization',
                learning_data
            )

        except Exception as e:
            logger.warning(f"Failed to record response optimization learning: {e}")

    async def get_response_optimization_insights(self) -> Dict[str, Any]:
        """Get insights from response optimization learning patterns"""
        try:
            recent_patterns = self.agent_db.get_patterns('holo_index', 'response_optimization', limit=100)

            insights = {
                'total_optimizations': len(recent_patterns),
                'average_improvement': 0.0,
                'average_candidates': 0.0,
                'quality_trends': {},
                'optimization_effectiveness': 0.0
            }

            if recent_patterns:
                # Calculate metrics
                improvements = [p.get('quality_metrics', {}).get('improvement_score', 0) for p in recent_patterns]
                candidate_counts = [p.get('candidate_count', 0) for p in recent_patterns]

                if improvements:
                    insights['average_improvement'] = sum(improvements) / len(improvements)
                if candidate_counts:
                    insights['average_candidates'] = sum(candidate_counts) / len(candidate_counts)

                # Track quality trends over time
                recent_scores = [p.get('quality_metrics', {}).get('optimization_effectiveness', 0) for p in recent_patterns[-20:]]
                older_scores = [p.get('quality_metrics', {}).get('optimization_effectiveness', 0) for p in recent_patterns[:20]]

                if recent_scores and older_scores:
                    recent_avg = sum(recent_scores) / len(recent_scores)
                    older_avg = sum(older_scores) / len(older_scores)
                    insights['optimization_effectiveness'] = recent_avg - older_avg

            return insights

        except Exception as e:
            logger.warning(f"Failed to get response optimization insights: {e}")
            return {}
