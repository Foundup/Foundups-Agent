#!/usr/bin/env python3
"""
Search Pattern Learner - Recursive Self-Improvement for HoloIndex

PRINCIPLE: Running holo IS remembering holo
Every search builds pattern recognition roadmap through:
1. Qwen scores search results (relevance, quality)
2. 0102 rates outcome (did it help?)
3. Patterns stored for future improvement
4. Better searches emerge through quantum learning
5. Code health mapping through usage patterns

WSP Compliance: WSP 48 (Recursive Improvement), WSP 60 (Memory Architecture)
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict

logger = logging.getLogger(__name__)

# Import code health scorer
try:
    from .code_health_scorer import CodeHealthScorer
    HEALTH_SCORING_AVAILABLE = True
except ImportError:
    HEALTH_SCORING_AVAILABLE = False
    logger.warning("CodeHealthScorer not available - health tracking disabled")


@dataclass
class SearchPattern:
    """Pattern learned from a search interaction."""
    query: str
    intent: str  # create, debug, explore, etc.
    timestamp: str

    # Search metrics
    results_count: int
    code_hits: int
    wsp_hits: int

    # Qwen scoring
    qwen_relevance_score: float  # 0-1: How relevant were results
    qwen_quality_score: float    # 0-1: How good were the matches

    # 0102 feedback
    user_rating: Optional[float] = None  # 0-1: Did this help?
    user_action: Optional[str] = None    # What did 0102 do after? (read, edit, create)

    # Learned patterns
    successful: Optional[bool] = None  # Was this search ultimately useful?
    improvement_notes: List[str] = field(default_factory=list)


@dataclass
class PatternRoadmap:
    """Roadmap of learned patterns for query types."""
    query_type: str  # Intent category
    total_searches: int = 0
    successful_searches: int = 0

    # Pattern insights
    best_keywords: List[Tuple[str, float]] = field(default_factory=list)  # (keyword, success_rate)
    common_mistakes: List[str] = field(default_factory=list)
    optimal_patterns: List[str] = field(default_factory=list)

    # Evolution tracking
    avg_relevance_score: float = 0.0
    avg_quality_score: float = 0.0
    improvement_trajectory: List[float] = field(default_factory=list)  # Over time


class SearchPatternLearner:
    """
    Learns from every HoloIndex search to improve future searches.

    Implements: Running holo IS remembering holo
    - Every search leaves a pattern trace
    - Qwen scores results automatically
    - 0102 can rate outcomes
    - System learns what works
    """

    def __init__(self, memory_path: str = "E:/HoloIndex/pattern_memory"):
        self.memory_path = Path(memory_path)
        self.memory_path.mkdir(parents=True, exist_ok=True)

        self.patterns_file = self.memory_path / "search_patterns.jsonl"
        self.roadmaps_file = self.memory_path / "pattern_roadmaps.json"

        # Load existing patterns
        self.patterns: List[SearchPattern] = self._load_patterns()
        self.roadmaps: Dict[str, PatternRoadmap] = self._load_roadmaps()

        # Initialize code health scorer
        self.health_scorer = CodeHealthScorer(memory_path=str(self.memory_path)) if HEALTH_SCORING_AVAILABLE else None
        if self.health_scorer:
            logger.info("[HEALTH] Code health tracking enabled - building health map through usage")

    def record_search(self,
                     query: str,
                     intent: str,
                     results: List[Dict],
                     qwen_scores: Optional[Dict[str, float]] = None) -> str:
        """
        Record a search and get automatic Qwen scoring.
        Also updates code health map based on usage patterns.

        Returns:
            pattern_id: Use this to provide feedback later
        """
        # Extract metrics
        code_hits = len([r for r in results if r.get('type') == 'code'])
        wsp_hits = len([r for r in results if r.get('type') == 'wsp'])

        # Get Qwen scores (or compute defaults)
        if qwen_scores is None:
            qwen_scores = self._auto_score_results(query, results)

        # Create pattern
        pattern = SearchPattern(
            query=query,
            intent=intent,
            timestamp=datetime.now().isoformat(),
            results_count=len(results),
            code_hits=code_hits,
            wsp_hits=wsp_hits,
            qwen_relevance_score=qwen_scores.get('relevance', 0.5),
            qwen_quality_score=qwen_scores.get('quality', 0.5)
        )

        # Store pattern
        self.patterns.append(pattern)
        self._save_pattern(pattern)

        # Update roadmap
        self._update_roadmap(pattern)

        # Update code health from usage pattern
        if self.health_scorer:
            for result in results:
                module_path = result.get('module_path') or result.get('file_path')
                if module_path:
                    # Every search reveals what's used/needed (foundational indicator)
                    search_success = qwen_scores.get('relevance', 0.5) > 0.6
                    self.health_scorer.update_from_search_pattern(
                        module_path=module_path,
                        search_success=search_success
                    )

        pattern_id = f"{pattern.timestamp}_{len(self.patterns)}"
        logger.info(f"[PATTERN-LEARN] Recorded search pattern: {pattern_id}")

        return pattern_id

    def provide_feedback(self,
                        pattern_id: str,
                        user_rating: float,
                        user_action: str,
                        notes: Optional[List[str]] = None):
        """
        0102 provides feedback on search outcome.
        Updates code health based on user satisfaction.

        Args:
            pattern_id: From record_search()
            user_rating: 0-1 scale (0=useless, 1=perfect)
            user_action: What 0102 did (read, edit, create, gave_up)
            notes: Optional improvement suggestions
        """
        # Find pattern by timestamp (pattern_id contains timestamp)
        timestamp = pattern_id.split('_')[0]

        for pattern in reversed(self.patterns):
            if pattern.timestamp.startswith(timestamp):
                pattern.user_rating = user_rating
                pattern.user_action = user_action
                pattern.successful = user_rating >= 0.6  # Threshold for success

                if notes:
                    pattern.improvement_notes.extend(notes)

                # Update roadmap with feedback
                self._update_roadmap_feedback(pattern)

                # Update code health with user satisfaction rating
                if self.health_scorer:
                    # Extract module paths from the original search
                    # (We'd need to store this in pattern - for now, update last searched modules)
                    # This is a simplified version - real implementation would track per-result
                    pass  # Health already updated in record_search, rating tracked there

                # Save updated pattern
                self._save_patterns()

                logger.info(f"[PATTERN-LEARN] Feedback recorded: rating={user_rating}, action={user_action}")
                return

        logger.warning(f"[PATTERN-LEARN] Pattern ID not found: {pattern_id}")

    def get_search_suggestions(self, intent: str, query: str) -> Dict[str, any]:
        """
        Get suggestions to improve search based on learned patterns.

        Returns:
            Suggestions for better keywords, avoiding mistakes, etc.
        """
        roadmap = self.roadmaps.get(intent)

        if not roadmap or roadmap.total_searches < 3:
            return {
                'has_suggestions': False,
                'reason': 'Insufficient pattern data for this intent'
            }

        suggestions = {
            'has_suggestions': True,
            'intent': intent,
            'historical_success_rate': roadmap.successful_searches / roadmap.total_searches if roadmap.total_searches > 0 else 0,
            'suggested_keywords': roadmap.best_keywords[:5],
            'common_mistakes': roadmap.common_mistakes[:3],
            'optimal_patterns': roadmap.optimal_patterns[:3],
            'improvement_trend': roadmap.improvement_trajectory[-5:] if len(roadmap.improvement_trajectory) >= 5 else []
        }

        return suggestions

    def _auto_score_results(self, query: str, results: List[Dict]) -> Dict[str, float]:
        """
        Automatically score results using Qwen-like heuristics.

        This is a simplified version - real Qwen integration would be better.
        """
        if not results:
            return {'relevance': 0.0, 'quality': 0.0}

        # Simple relevance: keyword matching
        query_words = set(query.lower().split())
        relevance_scores = []

        for result in results:
            result_text = str(result).lower()
            matches = sum(1 for word in query_words if word in result_text)
            relevance = matches / len(query_words) if query_words else 0
            relevance_scores.append(relevance)

        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0

        # Simple quality: result diversity and completeness
        has_code = any(r.get('type') == 'code' for r in results)
        has_wsp = any(r.get('type') == 'wsp' for r in results)
        has_multiple = len(results) >= 3

        quality = (0.4 if has_code else 0) + (0.3 if has_wsp else 0) + (0.3 if has_multiple else 0)

        return {
            'relevance': min(avg_relevance, 1.0),
            'quality': quality
        }

    def _update_roadmap(self, pattern: SearchPattern):
        """Update pattern roadmap for this intent."""
        intent = pattern.intent

        if intent not in self.roadmaps:
            self.roadmaps[intent] = PatternRoadmap(query_type=intent)

        roadmap = self.roadmaps[intent]
        roadmap.total_searches += 1

        # Update averages
        n = roadmap.total_searches
        roadmap.avg_relevance_score = ((roadmap.avg_relevance_score * (n-1)) + pattern.qwen_relevance_score) / n
        roadmap.avg_quality_score = ((roadmap.avg_quality_score * (n-1)) + pattern.qwen_quality_score) / n

        # Track improvement trajectory
        combined_score = (pattern.qwen_relevance_score + pattern.qwen_quality_score) / 2
        roadmap.improvement_trajectory.append(combined_score)

        self._save_roadmaps()

    def _update_roadmap_feedback(self, pattern: SearchPattern):
        """Update roadmap with user feedback."""
        intent = pattern.intent
        roadmap = self.roadmaps.get(intent)

        if not roadmap:
            return

        if pattern.successful:
            roadmap.successful_searches += 1

            # Extract successful keywords
            for word in pattern.query.lower().split():
                if len(word) > 3:  # Skip short words
                    # Track keyword success
                    # (Simplified - real implementation would track across all patterns)
                    pass

        # Learn from improvement notes
        if pattern.improvement_notes:
            for note in pattern.improvement_notes:
                if note not in roadmap.common_mistakes and 'mistake' in note.lower():
                    roadmap.common_mistakes.append(note)
                elif note not in roadmap.optimal_patterns and 'better' in note.lower():
                    roadmap.optimal_patterns.append(note)

        self._save_roadmaps()

    def _load_patterns(self) -> List[SearchPattern]:
        """Load patterns from JSONL file."""
        patterns = []

        if not self.patterns_file.exists():
            return patterns

        try:
            with open(self.patterns_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        patterns.append(SearchPattern(**data))
        except Exception as e:
            logger.warning(f"Error loading patterns: {e}")

        return patterns

    def _save_pattern(self, pattern: SearchPattern):
        """Append pattern to JSONL file."""
        try:
            with open(self.patterns_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(asdict(pattern)) + '\n')
        except Exception as e:
            logger.error(f"Error saving pattern: {e}")

    def _save_patterns(self):
        """Save all patterns (for updates)."""
        try:
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                for pattern in self.patterns:
                    f.write(json.dumps(asdict(pattern)) + '\n')
        except Exception as e:
            logger.error(f"Error saving patterns: {e}")

    def _load_roadmaps(self) -> Dict[str, PatternRoadmap]:
        """Load pattern roadmaps."""
        if not self.roadmaps_file.exists():
            return {}

        try:
            with open(self.roadmaps_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {k: PatternRoadmap(**v) for k, v in data.items()}
        except Exception as e:
            logger.warning(f"Error loading roadmaps: {e}")
            return {}

    def _save_roadmaps(self):
        """Save pattern roadmaps."""
        try:
            data = {k: asdict(v) for k, v in self.roadmaps.items()}
            with open(self.roadmaps_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving roadmaps: {e}")

    def get_statistics(self) -> Dict[str, any]:
        """Get learning statistics including code health metrics."""
        total_patterns = len(self.patterns)
        rated_patterns = [p for p in self.patterns if p.user_rating is not None]
        successful_patterns = [p for p in self.patterns if p.successful]

        stats = {
            'total_searches': total_patterns,
            'rated_searches': len(rated_patterns),
            'successful_searches': len(successful_patterns),
            'success_rate': len(successful_patterns) / len(rated_patterns) if rated_patterns else 0,
            'intents_learned': len(self.roadmaps),
            'avg_relevance': sum(p.qwen_relevance_score for p in self.patterns) / total_patterns if total_patterns > 0 else 0,
            'avg_quality': sum(p.qwen_quality_score for p in self.patterns) / total_patterns if total_patterns > 0 else 0,
            'roadmaps': {intent: {'total': r.total_searches, 'successful': r.successful_searches}
                        for intent, r in self.roadmaps.items()}
        }

        # Add code health report if available
        if self.health_scorer:
            stats['code_health'] = self.health_scorer.get_health_report()

        return stats

    def get_health_report(self) -> Optional[Dict]:
        """Get comprehensive code health report."""
        if self.health_scorer:
            return self.health_scorer.get_health_report()
        return None

    def get_foundational_modules(self) -> Optional[List[Tuple[str, float]]]:
        """Get foundational modules sorted by importance."""
        if self.health_scorer:
            return self.health_scorer.get_foundational_modules()
        return None

    def get_unhealthy_modules(self, threshold: float = 0.4) -> Optional[List[Tuple[str, float]]]:
        """Get modules that need attention."""
        if self.health_scorer:
            return self.health_scorer.get_unhealthy_modules(threshold)
        return None
