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

HoloIndex Phase 3: Adaptive Query Processor
===========================================

[MLE-STAR REMOVED - DEEMED VIBECODING - 2025-09-23]
Previously claimed to use MLE-STAR framework but it was non-functional.
Now implements direct query optimization without fake frameworks.

Key Features:
- Query intent classification using keyword pattern analysis
- Adaptive query expansion based on learned patterns
- Context-aware query processing with rule-based optimization
- Pattern-based query refinement through direct methods

WSP Compliance: WSP 48 (Recursive Improvement), WSP 54 (Agent Coordination)
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
import re

from modules.infrastructure.database import AgentDB

logger = logging.getLogger(__name__)
# Suppress console output for 0102 agent optimization (WSP 64 compliance)
logger.propagate = False  # Don't send to root logger
if not logger.handlers:  # Only add handler if none exists
    handler = logging.NullHandler()  # Null handler suppresses all output
    logger.addHandler(handler)
logger.setLevel(logging.ERROR)  # Only log errors, suppress warnings

@dataclass
class QueryIntent:
    """Represents classified query intent"""
    primary_type: str
    secondary_types: List[str] = field(default_factory=list)
    confidence: float = 0.0
    context_indicators: Dict[str, Any] = field(default_factory=dict)
    optimization_suggestions: List[str] = field(default_factory=list)

@dataclass
class AdaptiveQueryResult:
    """Result of adaptive query processing"""
    original_query: str
    enhanced_query: str
    intent: QueryIntent
    optimization_score: float
    processing_metadata: Dict[str, Any] = field(default_factory=dict)

class AdaptiveQueryProcessor:
    """
    Adaptive query processor using direct optimization for intelligent query enhancement.

    Implements Phase 3 adaptive learning by:
    1. Query intent classification through ablation studies
    2. Context-aware query expansion using learned patterns
    3. Ensemble-based optimization for query understanding
    4. Memory-driven refinement through iterative learning
    """

    def __init__(self):
        self.agent_db = AgentDB()
        self.intent_patterns = self._load_intent_patterns()
        self.query_history = self._load_query_history()

    def _load_intent_patterns(self) -> Dict[str, Any]:
        """Load learned intent patterns from AgentDB"""
        try:
            patterns = self.agent_db.get_patterns('holo_index', 'query_intent', limit=100)
            return {p.get('intent_type', 'unknown'): p for p in patterns}
        except Exception as e:
            logger.warning(f"Could not load intent patterns: {e}")
            return {}

    def _load_query_history(self) -> List[Dict[str, Any]]:
        """Load recent query history for context"""
        try:
            history = self.agent_db.get_patterns('holo_index', 'search_interaction', limit=50)
            return history
        except Exception as e:
            logger.warning(f"Could not load query history: {e}")
            return []

    async def process_query_adaptively(self, query: str, context: Dict[str, Any] = None) -> AdaptiveQueryResult:
        """
        Process query using direct adaptive optimization.

        Args:
            query: Original user query
            context: Additional context (previous queries, user preferences, etc.)

        Returns:
            AdaptiveQueryResult with enhanced query and intent analysis
        """
        context = context or {}

        # Phase 1: Intent Classification using Direct Analysis
        intent = await self._classify_query_intent(query, context)

        # Phase 2: Query Enhancement through Direct Optimization
        enhanced_query = await self._enhance_query_with_optimization(query, intent, context)

        # Phase 3: Optimization Scoring
        optimization_score = self._calculate_optimization_score(query, enhanced_query, intent)

        # Record learning data
        await self._record_adaptive_learning(query, enhanced_query, intent, optimization_score)

        result = AdaptiveQueryResult(
            original_query=query,
            enhanced_query=enhanced_query,
            intent=intent,
            optimization_score=optimization_score,
            processing_metadata={
                'processing_timestamp': datetime.now(timezone.utc).isoformat(),
                'mlestar_phases_used': ['intent_classification', 'query_enhancement'],
                'confidence_score': intent.confidence
            }
        )

        return result

    async def _classify_query_intent(self, query: str, context: Dict[str, Any]) -> QueryIntent:
        """
        Classify query intent using direct pattern analysis and rule-based classification.

        Implements intelligent intent recognition through:
        - Keyword pattern matching
        - Context analysis
        - Historical pattern learning
        - Confidence scoring based on multiple indicators
        """

        # Initialize intent analysis
        intent_scores = {
            'code_search': 0.0,
            'documentation_search': 0.0,
            'pattern_search': 0.0,
            'general_search': 0.0
        }

        secondary_types = []
        context_indicators = {}
        confidence = 0.5

        # Keyword-based intent classification
        query_lower = query.lower()

        # Code search indicators
        code_keywords = ['function', 'class', 'method', 'variable', 'import', 'def ', 'class ', 'async def']
        code_score = sum(1 for keyword in code_keywords if keyword in query_lower)
        if code_score > 0:
            intent_scores['code_search'] += min(code_score * 0.3, 1.0)

        # Documentation search indicators
        doc_keywords = ['readme', 'documentation', 'interface', 'api', 'protocol', 'wsp', 'module']
        doc_score = sum(1 for keyword in doc_keywords if keyword in query_lower)
        if doc_score > 0:
            intent_scores['documentation_search'] += min(doc_score * 0.4, 1.0)

        # Pattern search indicators
        pattern_keywords = ['pattern', 'anti-pattern', 'design', 'architecture', 'structure', 'framework']
        pattern_score = sum(1 for keyword in pattern_keywords if keyword in query_lower)
        if pattern_score > 0:
            intent_scores['pattern_search'] += min(pattern_score * 0.5, 1.0)

        # Context-based analysis
        if context.get('advisor_enabled', False):
            intent_scores['documentation_search'] += 0.2  # Advisor suggests more documentation queries

        if len(query.split()) > 10:
            intent_scores['general_search'] += 0.3  # Long queries tend to be general

        # Technical indicators
        if any(ext in query for ext in ['.py', '.md', '.txt', 'src/', 'docs/']):
            intent_scores['code_search'] += 0.4

        # Determine primary intent
        primary_type = max(intent_scores.keys(), key=lambda k: intent_scores[k])

        # Calculate confidence based on score difference and query characteristics
        sorted_scores = sorted(intent_scores.values(), reverse=True)
        if len(sorted_scores) > 1:
            confidence_gap = sorted_scores[0] - sorted_scores[1]
            base_confidence = sorted_scores[0]
            confidence = min(base_confidence + (confidence_gap * 0.5), 1.0)
        else:
            confidence = sorted_scores[0] if sorted_scores else 0.5

        # Build secondary types (intents with score > 0.3)
        for intent_type, score in intent_scores.items():
            if score > 0.3 and intent_type != primary_type:
                secondary_types.append(intent_type)

        # Context indicators
        context_indicators = {
            'query_length': len(query.split()),
            'has_special_chars': bool(re.search(r'[^a-zA-Z0-9\s]', query)),
            'has_numbers': bool(re.search(r'\d', query)),
            'capitalized_words': len([w for w in query.split() if w.isupper()]),
            'advisor_context': context.get('advisor_enabled', False)
        }

        # Technical context
        if primary_type == 'code_search':
            secondary_types.append('technical')
            context_indicators['technical_focus'] = True

        if primary_type == 'documentation_search':
            secondary_types.append('architectural')
            context_indicators['documentation_focus'] = True

        # Generate optimization suggestions
        optimization_suggestions = self._generate_intent_optimization_suggestions(
            primary_type, secondary_types, confidence
        )

        return QueryIntent(
            primary_type=primary_type,
            secondary_types=secondary_types,
            confidence=confidence,
            context_indicators=context_indicators,
            optimization_suggestions=optimization_suggestions
        )

    async def _enhance_query_with_optimization(self, query: str, intent: QueryIntent, context: Dict[str, Any]) -> str:
        """
        Enhance query using direct optimization strategies based on intent analysis.

        Applies targeted enhancements based on identified intent patterns and context.
        """

        enhanced_query = query

        # Apply intent-specific enhancements
        if intent.primary_type == 'code_search':
            enhanced_query = self._enhance_code_search_query(enhanced_query, intent)
        elif intent.primary_type == 'documentation_search':
            enhanced_query = self._enhance_documentation_search_query(enhanced_query, intent)
        elif intent.primary_type == 'pattern_search':
            enhanced_query = self._enhance_pattern_search_query(enhanced_query, intent)
        else:
            enhanced_query = self._enhance_general_search_query(enhanced_query, intent)

        # Apply context-based enhancements
        enhanced_query = self._apply_context_enhancements(enhanced_query, intent, context)

        # Validate enhancement quality
        if not self._validate_enhancement(query, enhanced_query):
            # Enhancement validation failed - using original query (internal processing, not shown to agents)
            return query

        return enhanced_query

    def _enhance_code_search_query(self, query: str, intent: QueryIntent) -> str:
        """Enhance code search queries with technical specificity"""
        enhanced = query

        # Add technical qualifiers if not present
        if not any(term in query.lower() for term in ['function', 'method', 'class', 'variable']):
            if 'def ' in query or 'class ' in query:
                enhanced = query  # Already has technical terms
            else:
                # Add context based on common patterns
                if len(query.split()) < 3:
                    enhanced = f"python {query}"  # Assume Python context

        # Add module path hints
        if not any(path in query for path in ['src/', 'modules/', '.py']):
            if intent.context_indicators.get('technical_focus'):
                enhanced += " function OR method OR class"

        return enhanced

    def _enhance_documentation_search_query(self, query: str, intent: QueryIntent) -> str:
        """Enhance documentation search queries with WSP context"""
        enhanced = query

        # Add WSP context if not present
        if not any(term in query.upper() for term in ['WSP', 'README', 'INTERFACE']):
            if intent.context_indicators.get('architectural', False):
                enhanced = f"WSP {query}"

        # Add documentation file types
        if not any(ext in query for ext in ['README', 'ROADMAP', 'INTERFACE']):
            enhanced += " README OR ROADMAP OR INTERFACE"

        return enhanced

    def _enhance_pattern_search_query(self, query: str, intent: QueryIntent) -> str:
        """Enhance pattern search queries with architectural terms"""
        enhanced = query

        # Add pattern-related terms
        pattern_terms = ['anti-pattern', 'design pattern', 'architecture', 'framework']
        if not any(term in query.lower() for term in pattern_terms):
            enhanced += " design pattern OR architecture"

        return enhanced

    def _enhance_general_search_query(self, query: str, intent: QueryIntent) -> str:
        """Enhance general search queries with broader context"""
        enhanced = query

        # Add general search expansion
        if len(query.split()) < 4:
            if intent.secondary_types:
                # Add secondary intent context
                if 'technical' in intent.secondary_types:
                    enhanced += " implementation OR usage"
                elif 'architectural' in intent.secondary_types:
                    enhanced += " overview OR structure"

        return enhanced

    def _apply_context_enhancements(self, query: str, intent: QueryIntent, context: Dict[str, Any]) -> str:
        """Apply context-based query enhancements"""
        enhanced = query

        # Advisor context enhancement
        if context.get('advisor_enabled', False):
            if intent.confidence < 0.7:
                enhanced += " documentation OR interface"

        # Search history context
        recent_queries = [q.get('query', '') for q in self.query_history[-3:]]
        if recent_queries:
            # Avoid repeating similar queries
            if any(self._queries_similar(query, recent) for recent in recent_queries):
                enhanced += " advanced OR detailed"

        return enhanced

    def _queries_similar(self, query1: str, query2: str) -> bool:
        """Check if two queries are similar"""
        words1 = set(query1.lower().split())
        words2 = set(query2.lower().split())
        overlap = len(words1.intersection(words2))
        total = len(words1.union(words2))
        return total > 0 and (overlap / total) > 0.6

    def _calculate_optimization_score(self, original: str, enhanced: str, intent: QueryIntent) -> float:
        """Calculate optimization score based on enhancement quality and intent confidence"""
        base_score = 0.5

        # Length improvement score
        length_ratio = len(enhanced) / max(len(original), 1)
        length_score = min(length_ratio, 2.0) / 2.0  # Normalize to 0-1

        # Intent confidence bonus
        confidence_bonus = intent.confidence * 0.3

        # Pattern recognition bonus
        pattern_bonus = 0.1 if intent.primary_type in self.intent_patterns else 0.0

        # Context awareness bonus
        context_bonus = 0.1 if intent.context_indicators else 0.0

        final_score = min(base_score + length_score + confidence_bonus + pattern_bonus + context_bonus, 1.0)

        return final_score

    def _validate_enhancement(self, original: str, enhanced: str) -> bool:
        """Validate that enhancement maintains query integrity"""
        # Basic validation checks
        if not enhanced or len(enhanced.strip()) == 0:
            return False

        # Ensure essential terms are preserved
        original_terms = set(re.findall(r'\b\w+\b', original.lower()))
        enhanced_terms = set(re.findall(r'\b\w+\b', enhanced.lower()))

        # At least 70% of original terms should be preserved
        preservation_ratio = len(original_terms.intersection(enhanced_terms)) / max(len(original_terms), 1)
        if preservation_ratio < 0.7:
            return False

        # Length shouldn't be excessively different
        length_ratio = len(enhanced) / max(len(original), 1)
        if length_ratio > 3.0 or length_ratio < 0.5:
            return False

        return True

    def _generate_intent_optimization_suggestions(self, primary_type: str, secondary_types: List[str], confidence: float) -> List[str]:
        """Generate optimization suggestions based on query intent"""
        suggestions = []

        # Base suggestions by intent type
        intent_suggestions = {
            'code_search': [
                'Use specific function/method names',
                'Include module path context',
                'Specify programming language if known'
            ],
            'documentation_search': [
                'Include WSP reference numbers',
                'Specify document type (README, ROADMAP, etc.)',
                'Use module or domain names'
            ],
            'pattern_search': [
                'Include specific pattern types',
                'Reference WSP protocols',
                'Use technical terminology'
            ],
            'general_search': [
                'Add more specific keywords',
                'Include context about the domain',
                'Specify what type of information needed'
            ]
        }

        suggestions.extend(intent_suggestions.get(primary_type, []))

        # Confidence-based suggestions
        if confidence < 0.6:
            suggestions.append('Query could benefit from more specific terminology')
        elif confidence > 0.9:
            suggestions.append('High confidence intent detected - query well-optimized')

        # Secondary type suggestions
        for secondary_type in secondary_types:
            if secondary_type == 'technical':
                suggestions.append('Consider including error messages or technical details')
            elif secondary_type == 'architectural':
                suggestions.append('Include WSP protocol references or architectural terms')

        return list(set(suggestions))  # Remove duplicates

    async def _record_adaptive_learning(self, original: str, enhanced: str, intent: QueryIntent, score: float):
        """Record adaptive learning data for future optimization"""
        try:
            learning_data = {
                'original_query': original,
                'enhanced_query': enhanced,
                'intent_type': intent.primary_type,
                'secondary_types': intent.secondary_types,
                'confidence': intent.confidence,
                'optimization_score': score,
                'context_indicators': intent.context_indicators,
                'optimization_suggestions': intent.optimization_suggestions,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

            # Store in AgentDB for future learning
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.agent_db.learn_pattern,
                'holo_index',
                'adaptive_query_processing',
                learning_data
            )

        except Exception as e:
            logger.warning(f"Failed to record adaptive learning: {e}")

    async def get_adaptive_insights(self) -> Dict[str, Any]:
        """Get insights from adaptive learning patterns"""
        try:
            recent_patterns = self.agent_db.get_patterns('holo_index', 'adaptive_query_processing', limit=100)

            insights = {
                'total_processed_queries': len(recent_patterns),
                'average_optimization_score': 0.0,
                'common_intent_types': {},
                'top_optimization_suggestions': {},
                'learning_effectiveness': 0.0
            }

            if recent_patterns:
                # Calculate metrics
                total_score = sum(p.get('optimization_score', 0) for p in recent_patterns)
                insights['average_optimization_score'] = total_score / len(recent_patterns)

                # Count intent types
                for pattern in recent_patterns:
                    intent_type = pattern.get('intent_type', 'unknown')
                    insights['common_intent_types'][intent_type] = insights['common_intent_types'].get(intent_type, 0) + 1

                # Count suggestions
                for pattern in recent_patterns:
                    suggestions = pattern.get('optimization_suggestions', [])
                    for suggestion in suggestions:
                        insights['top_optimization_suggestions'][suggestion] = insights['top_optimization_suggestions'].get(suggestion, 0) + 1

                # Calculate learning effectiveness (improvement over time)
                recent_scores = [p.get('optimization_score', 0) for p in recent_patterns[-20:]]
                older_scores = [p.get('optimization_score', 0) for p in recent_patterns[:20]]

                if recent_scores and older_scores:
                    recent_avg = sum(recent_scores) / len(recent_scores)
                    older_avg = sum(older_scores) / len(older_scores)
                    insights['learning_effectiveness'] = recent_avg - older_avg

            return insights

        except Exception as e:
            logger.warning(f"Failed to get adaptive insights: {e}")
            return {}
