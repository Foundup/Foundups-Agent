# -*- coding: utf-8 -*-
"""
Pattern Memory System (WSP 60 Enhanced)

Provides cross-platform pattern storage, sharing, and learning.
Enables agents to learn from patterns across all domains and platforms.

WSP 60: Module Memory Architecture Protocol
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import asyncio
from dataclasses import dataclass, asdict
import sys
import io

# WSP 90 UTF-8 Enforcement for Windows compatibility
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logger = logging.getLogger(__name__)


@dataclass
class Pattern:
    """Cross-platform pattern data structure"""
    name: str
    data: Dict[str, Any]
    source_module: str
    created_at: datetime
    last_updated: datetime
    usage_count: int = 0
    effectiveness_score: float = 0.0
    cross_platform: bool = False
    shared_domains: List[str] = None
    learned_patterns: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.shared_domains is None:
            self.shared_domains = []
        if self.learned_patterns is None:
            self.learned_patterns = []


class PatternMemory:
    """
    Pattern Memory System

    WSP 60 Enhanced: Cross-platform pattern storage and learning
    Enables agents to share intelligence across all domains

    Features:
    - Pattern storage and retrieval
    - Cross-platform pattern sharing
    - Effectiveness tracking and optimization
    - Pattern evolution through learning
    """

    def __init__(self, storage_path: Path):
        """
        Initialize pattern memory

        Args:
            storage_path: Directory for pattern storage
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # In-memory pattern cache
        self.patterns: Dict[str, Pattern] = {}

        # Pattern effectiveness tracking
        self.effectiveness_history: Dict[str, List[float]] = {}

        logger.info(f"[PATTERN-MEMORY] Initialized at {self.storage_path}")

    async def initialize(self):
        """Initialize pattern memory system"""
        await self._load_patterns()
        logger.info(f"[PATTERN-MEMORY] Loaded {len(self.patterns)} existing patterns")

    async def _load_patterns(self):
        """Load patterns from storage"""
        pattern_file = self.storage_path / "patterns.json"

        if pattern_file.exists():
            try:
                with open(pattern_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for pattern_name, pattern_data in data.items():
                    # Convert datetime strings back to datetime objects
                    created_at = datetime.fromisoformat(pattern_data['created_at'])
                    last_updated = datetime.fromisoformat(pattern_data['last_updated'])

                    pattern = Pattern(
                        name=pattern_name,
                        data=pattern_data['data'],
                        source_module=pattern_data['source_module'],
                        created_at=created_at,
                        last_updated=last_updated,
                        usage_count=pattern_data.get('usage_count', 0),
                        effectiveness_score=pattern_data.get('effectiveness_score', 0.0),
                        cross_platform=pattern_data.get('cross_platform', False),
                        shared_domains=pattern_data.get('shared_domains', []),
                        learned_patterns=pattern_data.get('learned_patterns', [])
                    )

                    self.patterns[pattern_name] = pattern

            except Exception as e:
                logger.error(f"[PATTERN-MEMORY] Failed to load patterns: {e}")

    async def save_all(self):
        """Save all patterns to storage"""
        try:
            data = {}
            for pattern_name, pattern in self.patterns.items():
                data[pattern_name] = {
                    'data': pattern.data,
                    'source_module': pattern.source_module,
                    'created_at': pattern.created_at.isoformat(),
                    'last_updated': pattern.last_updated.isoformat(),
                    'usage_count': pattern.usage_count,
                    'effectiveness_score': pattern.effectiveness_score,
                    'cross_platform': pattern.cross_platform,
                    'shared_domains': pattern.shared_domains,
                    'learned_patterns': pattern.learned_patterns
                }

            pattern_file = self.storage_path / "patterns.json"
            with open(pattern_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"[PATTERN-MEMORY] Saved {len(self.patterns)} patterns")

        except Exception as e:
            logger.error(f"[PATTERN-MEMORY] Failed to save patterns: {e}")

    async def store_pattern(self, name: str, data: Dict[str, Any],
                           source_module: str, cross_platform: bool = False,
                           shared_domains: List[str] = None) -> bool:
        """
        Store a pattern in memory

        Args:
            name: Pattern name
            data: Pattern data
            source_module: Source module identifier
            cross_platform: Whether pattern has cross-platform value
            shared_domains: Domains this pattern should be shared with

        Returns:
            bool: True if stored successfully
        """
        try:
            now = datetime.now()

            if name in self.patterns:
                # Update existing pattern
                pattern = self.patterns[name]
                pattern.data = data
                pattern.last_updated = now
                pattern.usage_count += 1
                pattern.cross_platform = cross_platform
                if shared_domains:
                    pattern.shared_domains.extend(shared_domains)
                    pattern.shared_domains = list(set(pattern.shared_domains))  # Remove duplicates
            else:
                # Create new pattern
                pattern = Pattern(
                    name=name,
                    data=data,
                    source_module=source_module,
                    created_at=now,
                    last_updated=now,
                    cross_platform=cross_platform,
                    shared_domains=shared_domains or []
                )
                self.patterns[name] = pattern

            # Auto-save for cross-platform patterns
            if cross_platform:
                await self.save_all()

            logger.info(f"[PATTERN-MEMORY] Stored pattern: {name} (cross_platform: {cross_platform})")
            return True

        except Exception as e:
            logger.error(f"[PATTERN-MEMORY] Failed to store pattern {name}: {e}")
            return False

    async def retrieve_pattern(self, name: str, track_usage: bool = True) -> Optional[Pattern]:
        """
        Retrieve a pattern from memory

        Args:
            name: Pattern name
            track_usage: Whether to track usage for effectiveness scoring

        Returns:
            Pattern object or None if not found
        """
        pattern = self.patterns.get(name)
        if pattern and track_usage:
            pattern.usage_count += 1
            pattern.last_updated = datetime.now()

        if pattern:
            logger.debug(f"[PATTERN-MEMORY] Retrieved pattern: {name}")
        else:
            logger.debug(f"[PATTERN-MEMORY] Pattern not found: {name}")

        return pattern

    async def query_patterns(self, query: str, domains: List[str] = None,
                           min_effectiveness: float = 0.0) -> Dict[str, Any]:
        """
        Query patterns by content and metadata

        Args:
            query: Search query (searches in pattern data)
            domains: Filter by domains
            min_effectiveness: Minimum effectiveness score

        Returns:
            Query results
        """
        results = []
        query_lower = query.lower()

        for pattern_name, pattern in self.patterns.items():
            # Check effectiveness threshold
            if pattern.effectiveness_score < min_effectiveness:
                continue

            # Check domain filter
            if domains and pattern.source_module.split('.')[0] not in domains:
                continue

            # Check content match
            pattern_json = json.dumps(pattern.data, default=str).lower()
            if query_lower in pattern_name.lower() or query_lower in pattern_json:
                results.append({
                    'name': pattern_name,
                    'pattern': asdict(pattern),
                    'relevance_score': self._calculate_relevance(query_lower, pattern_name, pattern.data)
                })

        # Sort by relevance and effectiveness
        results.sort(key=lambda x: (
            x['relevance_score'],
            x['pattern']['effectiveness_score'],
            x['pattern']['usage_count']
        ), reverse=True)

        logger.info(f"[PATTERN-MEMORY] Query '{query}' returned {len(results)} results")

        return {
            'query': query,
            'total_results': len(results),
            'patterns': results[:10],  # Limit to top 10
            'domains_filtered': domains,
            'min_effectiveness': min_effectiveness
        }

    def _calculate_relevance(self, query: str, name: str, data: Dict[str, Any]) -> float:
        """Calculate relevance score for a pattern"""
        score = 0.0

        # Name match bonus
        if query in name.lower():
            score += 0.5

        # Content match
        content_str = json.dumps(data, default=str).lower()
        if query in content_str:
            score += 0.3

        # Cross-platform bonus
        if data.get('cross_platform', False):
            score += 0.2

        return min(score, 1.0)  # Cap at 1.0

    async def update_effectiveness(self, pattern_name: str, outcome_score: float):
        """
        Update pattern effectiveness based on usage outcome

        Args:
            pattern_name: Name of pattern to update
            outcome_score: Outcome score (0.0 to 1.0)
        """
        if pattern_name in self.patterns:
            pattern = self.patterns[pattern_name]

            # Update effectiveness history
            if pattern_name not in self.effectiveness_history:
                self.effectiveness_history[pattern_name] = []

            self.effectiveness_history[pattern_name].append(outcome_score)

            # Calculate new effectiveness score (weighted average)
            history = self.effectiveness_history[pattern_name]
            weights = [0.5 ** (len(history) - i - 1) for i in range(len(history))]  # Exponential decay
            pattern.effectiveness_score = sum(s * w for s, w in zip(history, weights)) / sum(weights)

            pattern.last_updated = datetime.now()

            logger.debug(f"[PATTERN-MEMORY] Updated effectiveness for {pattern_name}: {pattern.effectiveness_score:.3f}")

    async def analyze_effectiveness(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze pattern effectiveness across all patterns

        Returns:
            Effectiveness analysis
        """
        analysis = {}

        for pattern_name, pattern in self.patterns.items():
            history = self.effectiveness_history.get(pattern_name, [])

            analysis[pattern_name] = {
                'current_score': pattern.effectiveness_score,
                'usage_count': pattern.usage_count,
                'history_length': len(history),
                'average_outcome': sum(history) / len(history) if history else 0.0,
                'cross_platform': pattern.cross_platform,
                'source_module': pattern.source_module,
                'last_updated': pattern.last_updated.isoformat()
            }

        # Sort by effectiveness
        sorted_analysis = dict(sorted(analysis.items(),
                                    key=lambda x: x[1]['current_score'],
                                    reverse=True))

        logger.info(f"[PATTERN-MEMORY] Analyzed effectiveness for {len(analysis)} patterns")

        return sorted_analysis

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get pattern memory statistics

        Returns:
            Memory statistics
        """
        total_patterns = len(self.patterns)
        cross_platform_patterns = sum(1 for p in self.patterns.values() if p.cross_platform)
        total_usage = sum(p.usage_count for p in self.patterns.values())
        avg_effectiveness = sum(p.effectiveness_score for p in self.patterns.values()) / total_patterns if total_patterns > 0 else 0.0

        # Domain distribution
        domain_counts = {}
        for pattern in self.patterns.values():
            domain = pattern.source_module.split('.')[0]
            domain_counts[domain] = domain_counts.get(domain, 0) + 1

        return {
            'total_patterns': total_patterns,
            'cross_platform_patterns': cross_platform_patterns,
            'total_usage': total_usage,
            'average_effectiveness': avg_effectiveness,
            'domain_distribution': domain_counts,
            'storage_path': str(self.storage_path)
        }

    async def cleanup_old_patterns(self, max_age_days: int = 90):
        """
        Clean up old, unused patterns

        Args:
            max_age_days: Maximum age in days for unused patterns
        """
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        to_remove = []

        for pattern_name, pattern in self.patterns.items():
            # Keep if recently used or highly effective
            if (pattern.last_updated > cutoff_date or
                pattern.effectiveness_score > 0.8 or
                pattern.cross_platform):
                continue

            # Mark for removal if old and ineffective
            if pattern.usage_count < 5 and pattern.last_updated < cutoff_date:
                to_remove.append(pattern_name)

        # Remove old patterns
        for pattern_name in to_remove:
            del self.patterns[pattern_name]

        if to_remove:
            await self.save_all()
            logger.info(f"[PATTERN-MEMORY] Cleaned up {len(to_remove)} old patterns")

        return len(to_remove)




