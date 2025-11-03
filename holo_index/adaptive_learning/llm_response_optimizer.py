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
# Suppress console output for 0102 agent optimization (WSP 64 compliance)
logger.propagate = False  # Don't send to root logger
if not logger.handlers:  # Only add handler if none exists
    handler = logging.NullHandler()  # Null handler suppresses all output
    logger.addHandler(handler)
logger.setLevel(logging.ERROR)  # Only log errors, suppress warnings

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
    LLM Response Optimizer with Qwen-Orchestrated Enhancement Strategies.

    Integrates with Qwen's orchestration pattern for intelligent, context-aware
    response optimization. Instead of blindly applying all enhancement strategies,
    Qwen analyzes response quality and makes targeted decisions about which
    specific optimizations are needed.

    Implements Phase 3 adaptive learning by:
    1. Response quality analysis with multi-dimensional assessment
    2. Qwen-orchestrated enhancement strategy selection
    3. Confidence-based execution of targeted improvements
    4. Context-aware optimization with learned patterns

    Enhancement Strategies (Qwen-Decided):
    - clarity_enhancement: Improve readability and understanding
    - relevance_enhancement: Strengthen query-response alignment
    - structure_enhancement: Add organization and headings
    - actionability_enhancement: Add steps, examples, clear instructions
    - conciseness_enhancement: Remove redundancy and verbosity
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
        Optimize LLM response using direct enhancement strategies.

        Uses ensemble methods with clarity, relevance, and actionability
        enhancements without external framework dependencies.

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
                'optimization_phases_used': ['candidate_generation', 'quality_selection', 'final_refinement'],
                'candidate_count': len(candidates),
                'query_complexity': self._assess_query_complexity(query)
            },
            quality_metrics=quality_metrics
        )

    async def _get_qwen_enhancement_decisions(self,
                                             query: str,
                                             original_response: str,
                                             context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get Qwen's orchestration decisions for which enhancement strategies to apply.

        Analyzes response quality and determines which specific optimizations are needed,
        following Qwen's intelligent decision-making pattern.
        """
        decisions = []

        # Analyze response characteristics
        response_analysis = self._analyze_response_quality(original_response, query, context)

        # Define available enhancement strategies with Qwen's decision logic
        available_strategies = {
            "clarity_enhancement": {
                "purpose": "Improve response clarity and readability",
                "triggers": ["low_clarity_score", "complex_language", "ambiguous_terms"],
                "cost": "low",
                "value": "high"
            },
            "relevance_enhancement": {
                "purpose": "Strengthen response relevance to query",
                "triggers": ["low_relevance_score", "off_topic_content", "missing_key_points"],
                "cost": "medium",
                "value": "high"
            },
            "structure_enhancement": {
                "purpose": "Improve response organization and structure",
                "triggers": ["poor_structure", "long_paragraphs", "missing_headings"],
                "cost": "medium",
                "value": "high"
            },
            "actionability_enhancement": {
                "purpose": "Make response more actionable with clear steps",
                "triggers": ["low_actionability", "vague_instructions", "missing_examples"],
                "cost": "medium",
                "value": "medium"
            },
            "conciseness_enhancement": {
                "purpose": "Remove redundancy and improve conciseness",
                "triggers": ["high_redundancy", "verbose_content", "unnecessary_details"],
                "cost": "low",
                "value": "medium"
            }
        }

        # Qwen's decision-making logic for each strategy
        for strategy_name, strategy_config in available_strategies.items():
            confidence, reasoning = self._calculate_enhancement_confidence(
                strategy_name, strategy_config, response_analysis, query, context
            )

            decisions.append({
                'strategy': strategy_name,
                'confidence': confidence,
                'reasoning': reasoning,
                'cost': strategy_config['cost'],
                'value': strategy_config['value']
            })

        # Sort by confidence (highest first) and return top decisions
        decisions.sort(key=lambda x: x['confidence'], reverse=True)
        return decisions

    def _analyze_response_quality(self, response: str, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze response quality to inform enhancement decisions."""
        analysis = {
            'clarity_score': self._assess_clarity(response),
            'relevance_score': self._assess_relevance(response, query),
            'structure_score': self._assess_structure(response),
            'actionability_score': self._assess_actionability(response),
            'conciseness_score': self._assess_conciseness(response),
            'length': len(response.split()),
            'has_headings': '###' in response or '##' in response,
            'has_lists': '- ' in response or '* ' in response or '1.' in response,
            'has_examples': 'example' in response.lower() or '`' in response,
            'complexity': self._assess_query_complexity(query)
        }

        # Add trigger flags based on analysis
        analysis.update({
            'low_clarity_score': analysis['clarity_score'] < 0.6,
            'low_relevance_score': analysis['relevance_score'] < 0.6,
            'poor_structure': analysis['structure_score'] < 0.6,
            'low_actionability': analysis['actionability_score'] < 0.6,
            'high_redundancy': analysis['conciseness_score'] < 0.6,
            'complex_language': analysis['complexity'] > 0.7,
            'long_paragraphs': any(len(p.split()) > 100 for p in response.split('\n\n')),
            'missing_headings': not analysis['has_headings'] and analysis['length'] > 200,
            'missing_examples': not analysis['has_examples'] and 'how' in query.lower(),
            'verbose_content': analysis['length'] > 300
        })

        return analysis

    def _calculate_enhancement_confidence(self, strategy_name: str, strategy_config: Dict,
                                        analysis: Dict, query: str, context: Dict) -> tuple[float, str]:
        """Calculate confidence score and reasoning for applying an enhancement strategy."""
        confidence = 0.0
        reasoning_parts = []

        # Check triggers and adjust confidence
        for trigger in strategy_config['triggers']:
            if analysis.get(trigger, False):
                confidence += 0.3
                reasoning_parts.append(f"triggered by {trigger}")

        # Strategy-specific logic
        if strategy_name == 'clarity_enhancement':
            if analysis['complexity'] > 0.7:
                confidence += 0.2
                reasoning_parts.append("high query complexity requires clarity")
            if analysis['clarity_score'] < 0.5:
                confidence += 0.3
                reasoning_parts.append("very low clarity score")

        elif strategy_name == 'relevance_enhancement':
            if 'search' in query.lower() or 'find' in query.lower():
                confidence += 0.2
                reasoning_parts.append("search-oriented query needs relevance")
            if analysis['relevance_score'] < 0.5:
                confidence += 0.3
                reasoning_parts.append("very low relevance score")

        elif strategy_name == 'structure_enhancement':
            if analysis['length'] > 200 and not analysis['has_headings']:
                confidence += 0.4
                reasoning_parts.append("long response without headings needs structure")
            if analysis['structure_score'] < 0.5:
                confidence += 0.3
                reasoning_parts.append("very poor structure")

        elif strategy_name == 'actionability_enhancement':
            if any(word in query.lower() for word in ['how', 'steps', 'implement', 'create']):
                confidence += 0.4
                reasoning_parts.append("how-to query requires actionability")
            if not analysis['has_lists'] and analysis['length'] > 100:
                confidence += 0.2
                reasoning_parts.append("response could benefit from structured steps")

        elif strategy_name == 'conciseness_enhancement':
            if analysis['length'] > 400:
                confidence += 0.3
                reasoning_parts.append("very long response needs conciseness")
            if analysis['conciseness_score'] < 0.4:
                confidence += 0.4
                reasoning_parts.append("extremely verbose content")

        # Cost-value adjustment
        if strategy_config['cost'] == 'low' and strategy_config['value'] == 'high':
            confidence += 0.1  # Bonus for high-value, low-cost strategies
        elif strategy_config['cost'] == 'high':
            confidence -= 0.1  # Penalty for high-cost strategies

        confidence = max(0.0, min(1.0, confidence))  # Clamp to 0-1 range

        reasoning = " | ".join(reasoning_parts) if reasoning_parts else "no clear triggers"

        return confidence, reasoning

    async def _generate_response_candidates(self,
                                          query: str,
                                          original_response: str,
                                          context: Dict[str, Any]) -> List[ResponseCandidate]:
        """
        Generate response candidates using Qwen-orchestrated enhancement strategies.

        Analyzes response quality and applies only needed enhancements based on
        Qwen's intelligent decision-making, not blind application of all strategies.
        """

        candidates = []

        # Get Qwen's orchestration decisions for enhancement strategies
        enhancement_decisions = await self._get_qwen_enhancement_decisions(query, original_response, context)

        # Execute only the enhancements Qwen determined are necessary
        for decision in enhancement_decisions:
            strategy_name = decision['strategy']
            confidence = decision['confidence']
            reasoning = decision.get('reasoning', '')

            if confidence >= 0.5:  # Only execute high-confidence enhancements
                logger.debug(f"[QWEN-DECISION] EXECUTE {strategy_name} (confidence: {confidence:.2f}) - {reasoning}")

                if strategy_name == 'clarity_enhancement':
                    candidate = self._enhance_response_clarity(original_response, query, context)
                elif strategy_name == 'relevance_enhancement':
                    candidate = self._enhance_response_relevance(original_response, query, context)
                elif strategy_name == 'structure_enhancement':
                    candidate = self._enhance_response_structure(original_response, query, context)
                elif strategy_name == 'actionability_enhancement':
                    candidate = self._enhance_response_actionability(original_response, query, context)
                elif strategy_name == 'conciseness_enhancement':
                    candidate = self._enhance_response_conciseness(original_response, query, context)
                else:
                    continue

                # Add Qwen's decision metadata
                candidate.metadata.update({
                    'qwen_decision': decision,
                    'strategy_applied': strategy_name,
                    'confidence_score': confidence
                })
                candidates.append(candidate)

            else:
                logger.debug(f"[QWEN-DECISION] SKIP {strategy_name} (confidence: {confidence:.2f}) - {reasoning}")

        # If no enhancements were applied, use original as fallback
        if not candidates:
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
            # Refinement validation failed - using selected response (internal processing, not shown to agents)
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

    def _enhance_response_actionability(self, response: str, query: str, context: Dict[str, Any]) -> ResponseCandidate:
        """
        Enhance response actionability by adding clear steps and examples.

        Makes responses more actionable by adding numbered lists, examples, and clear instructions.
        """
        enhanced = response

        # Add step-by-step structure if missing
        if not any(char in enhanced for char in ['1.', '2.', '3.', '-', '*']):
            # Convert paragraphs to numbered steps for how-to queries
            if any(word in query.lower() for word in ['how', 'steps', 'implement', 'create']):
                paragraphs = [p.strip() for p in enhanced.split('\n\n') if p.strip()]
                if len(paragraphs) > 1:
                    enhanced = '\n\n'.join(f'{i+1}. {p}' for i, p in enumerate(paragraphs))

        # Add examples if missing and query suggests need
        if 'example' not in enhanced.lower() and any(word in query.lower() for word in ['how', 'implement', 'create']):
            enhanced += '\n\nExample:\n```python\n# Example implementation\nprint("Hello, World!")\n```'

        # Add actionable language
        enhanced = enhanced.replace('should', 'must').replace('could', 'can').replace('might', 'will')

        return ResponseCandidate(
            content=enhanced,
            quality_score=self._assess_actionability(enhanced),
            relevance_score=self._assess_relevance(enhanced, query),
            clarity_score=self._assess_clarity(enhanced)
        )

    def _enhance_response_conciseness(self, response: str, query: str, context: Dict[str, Any]) -> ResponseCandidate:
        """
        Enhance response conciseness by removing redundancy and verbosity.

        Reduces word count while maintaining key information and clarity.
        """
        enhanced = response

        # Remove redundant phrases
        redundant_phrases = [
            'it is important to note that',
            'please be aware that',
            'it should be noted that',
            'as previously mentioned',
            'in other words',
            'basically',
            'essentially'
        ]

        for phrase in redundant_phrases:
            enhanced = enhanced.replace(phrase, '')

        # Shorten long sentences (split sentences over 30 words)
        sentences = enhanced.split('. ')
        shortened_sentences = []
        for sentence in sentences:
            words = sentence.split()
            if len(words) > 30:
                # Split long sentences at natural break points
                midpoint = len(words) // 2
                # Find good break point (conjunction or preposition)
                break_words = ['and', 'but', 'or', 'so', 'because', 'although', 'however']
                break_point = midpoint
                for i, word in enumerate(words[midpoint-5:midpoint+5]):
                    if word.lower() in break_words:
                        break_point = midpoint - 5 + i
                        break
                part1 = ' '.join(words[:break_point])
                part2 = ' '.join(words[break_point:])
                shortened_sentences.append(f'{part1}. {part2}')
            else:
                shortened_sentences.append(sentence)

        enhanced = '. '.join(shortened_sentences)

        # Remove excessive whitespace
        enhanced = '\n\n'.join(line.strip() for line in enhanced.split('\n\n') if line.strip())

        return ResponseCandidate(
            content=enhanced,
            quality_score=self._assess_conciseness(enhanced),
            relevance_score=self._assess_relevance(enhanced, query),
            clarity_score=self._assess_clarity(enhanced)
        )
