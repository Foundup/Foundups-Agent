#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

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

Code Health Scoring System for HoloIndex Pattern Learning

FIRST PRINCIPLES: Health = Usage Patterns + Structural Properties

Code health is multi-dimensional:
1. Structural Health - Architecture integrity
2. Maintenance Health - Change resistance
3. Knowledge Health - Understanding accessibility
4. Dependency Health - System criticality
5. Pattern Health - Quality indicators

HoloIndex learns health through USAGE PATTERNS over time.

WSP Compliance: WSP 48 (Recursive Learning), WSP 60 (Memory Architecture)
"""


import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class ModuleHealth:
    """Multi-dimensional health metrics for a module."""
    module_path: str

    # Structural Health (0-1)
    size_score: float = 0.5          # File count, LOC (smaller = healthier up to point)
    cohesion_score: float = 0.5      # Single responsibility indicator
    coupling_score: float = 0.5      # Dependency strength (lower = healthier)

    # Maintenance Health (0-1)
    stability_score: float = 0.5     # Change frequency (stable = healthier)
    recency_score: float = 0.5       # Time since last change (recent = active/healthy)
    bug_density: float = 0.5         # Issues per KLOC (lower = healthier)

    # Knowledge Health (0-1)
    documentation_score: float = 0.5  # Doc coverage (higher = healthier)
    test_coverage: float = 0.5        # Test coverage (higher = healthier)
    usage_frequency: float = 0.5      # How often searched/referenced

    # Dependency Health (0-1)
    centrality_score: float = 0.5    # Import graph position (foundational = high)
    criticality_score: float = 0.5   # Failure blast radius

    # Pattern Health (0-1)
    search_satisfaction: float = 0.5  # Average user rating when found
    wsp_compliance: float = 0.5       # Violation count (lower = healthier)

    # Aggregate metrics
    overall_health: float = 0.5       # Weighted average
    foundational_score: float = 0.5   # How foundational is this module

    # Evolution tracking
    health_history: List[Tuple[str, float]] = field(default_factory=list)  # (timestamp, health)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CodebaseHealthMap:
    """System-wide health mapping."""
    modules: Dict[str, ModuleHealth] = field(default_factory=dict)

    # System-wide metrics
    avg_health: float = 0.5
    foundational_modules: List[str] = field(default_factory=list)  # Top 20% by criticality
    unhealthy_modules: List[str] = field(default_factory=list)     # Bottom 20% by health

    # Evolution
    health_trajectory: List[Tuple[str, float]] = field(default_factory=list)  # System health over time
    last_scan: str = field(default_factory=lambda: datetime.now().isoformat())


class CodeHealthScorer:
    """
    Learns code health through usage patterns and structural analysis.

    Implements: "Running holo IS remembering holo" for health tracking
    - Every search reveals what's foundational (frequently needed)
    - Every modification reveals stability (change frequency)
    - Every user rating reveals quality (satisfaction)
    - Every WSP violation reveals compliance issues
    """

    def __init__(self, memory_path: str = "E:/HoloIndex/pattern_memory"):
        self.memory_path = Path(memory_path)
        self.memory_path.mkdir(parents=True, exist_ok=True)

        self.health_map_file = self.memory_path / "codebase_health_map.json"
        self.health_map: CodebaseHealthMap = self._load_health_map()

    def update_from_search_pattern(self, module_path: str, search_success: bool,
                                   user_rating: Optional[float] = None):
        """
        Update module health from search pattern data.

        This is called by SearchPatternLearner after each search.
        """
        if module_path not in self.health_map.modules:
            self.health_map.modules[module_path] = ModuleHealth(module_path=module_path)

        health = self.health_map.modules[module_path]

        # Update usage frequency (exponential moving average)
        alpha = 0.1  # Learning rate
        health.usage_frequency = (1 - alpha) * health.usage_frequency + alpha * 1.0

        # Update search satisfaction if rating provided
        if user_rating is not None:
            health.search_satisfaction = (
                (1 - alpha) * health.search_satisfaction + alpha * user_rating
            )

        # Successful searches indicate quality
        if search_success:
            health.pattern_health = min(
                (health.pattern_health * 0.9 + 0.1), 1.0
            )

        # Recalculate overall health
        self._recalculate_health(health)

        # Track evolution
        health.health_history.append((datetime.now().isoformat(), health.overall_health))
        if len(health.health_history) > 100:
            health.health_history = health.health_history[-100:]  # Keep last 100

        health.last_updated = datetime.now().isoformat()
        self._save_health_map()

    def update_from_structure_scan(self, module_path: str, structure_metrics: Dict):
        """
        Update module health from structural analysis.

        structure_metrics should include:
        - file_count, total_loc
        - has_readme, has_interface, has_tests
        - test_coverage_pct
        - import_count (dependencies)
        - violation_count
        """
        if module_path not in self.health_map.modules:
            self.health_map.modules[module_path] = ModuleHealth(module_path=module_path)

        health = self.health_map.modules[module_path]

        # Size score (smaller is better up to a point)
        loc = structure_metrics.get('total_loc', 1000)
        # Optimal range: 200-2000 LOC per module
        if loc < 200:
            health.size_score = 0.7  # Too small, possibly incomplete
        elif loc <= 2000:
            health.size_score = 1.0  # Ideal size
        elif loc <= 5000:
            health.size_score = 0.8  # Getting large
        else:
            health.size_score = max(0.3, 1.0 - (loc - 5000) / 10000)  # Too large

        # Documentation score
        has_readme = structure_metrics.get('has_readme', False)
        has_interface = structure_metrics.get('has_interface', False)
        has_tests = structure_metrics.get('has_tests', False)
        health.documentation_score = (
            (0.4 if has_readme else 0) +
            (0.3 if has_interface else 0) +
            (0.3 if has_tests else 0)
        )

        # Test coverage
        health.test_coverage = structure_metrics.get('test_coverage_pct', 0) / 100.0

        # Coupling score (fewer dependencies = healthier)
        import_count = structure_metrics.get('import_count', 0)
        health.coupling_score = max(0.2, 1.0 - (import_count / 50.0))  # Normalize

        # WSP compliance (fewer violations = healthier)
        violation_count = structure_metrics.get('violation_count', 0)
        health.wsp_compliance = max(0.0, 1.0 - (violation_count / 10.0))

        # Recalculate overall health
        self._recalculate_health(health)

        health.last_updated = datetime.now().isoformat()
        self._save_health_map()

    def update_from_modification(self, module_path: str, change_type: str):
        """
        Update module health from code modifications.

        change_type: 'bug_fix', 'feature', 'refactor', 'test'
        """
        if module_path not in self.health_map.modules:
            self.health_map.modules[module_path] = ModuleHealth(module_path=module_path)

        health = self.health_map.modules[module_path]

        # Track change frequency for stability score
        if not hasattr(health, '_change_timestamps'):
            health._change_timestamps = []

        health._change_timestamps.append(datetime.now().isoformat())

        # Calculate stability (fewer recent changes = more stable)
        recent_changes = [
            ts for ts in health._change_timestamps
            if datetime.fromisoformat(ts) > datetime.now() - timedelta(days=30)
        ]

        # Stability: 0 changes = 1.0, 10+ changes/month = 0.3
        health.stability_score = max(0.3, 1.0 - (len(recent_changes) / 10.0))

        # Recency score (recent activity = healthy development)
        health.recency_score = 1.0  # Just modified

        # Bug fixes reduce bug density
        if change_type == 'bug_fix':
            health.bug_density = max(0.0, health.bug_density - 0.05)

        # Recalculate overall health
        self._recalculate_health(health)

        health.last_updated = datetime.now().isoformat()
        self._save_health_map()

    def calculate_dependency_graph(self, import_graph: Dict[str, List[str]]):
        """
        Calculate dependency health metrics from import graph.

        import_graph: {module_path: [imported_modules]}
        """
        # Build reverse graph (who imports this module)
        reverse_graph = defaultdict(list)
        for module, imports in import_graph.items():
            for imported in imports:
                reverse_graph[imported].append(module)

        # Calculate centrality (how many modules import this)
        for module_path in import_graph.keys():
            if module_path not in self.health_map.modules:
                self.health_map.modules[module_path] = ModuleHealth(module_path=module_path)

            health = self.health_map.modules[module_path]

            # Centrality: normalized by max imports
            import_count = len(reverse_graph.get(module_path, []))
            max_imports = max(len(v) for v in reverse_graph.values()) if reverse_graph else 1
            health.centrality_score = import_count / max_imports if max_imports > 0 else 0

            # Criticality: how many modules depend on this
            health.criticality_score = min(1.0, import_count / 10.0)  # 10+ = critical

            # Foundational score = centrality + criticality
            health.foundational_score = (health.centrality_score + health.criticality_score) / 2

            # Recalculate overall health
            self._recalculate_health(health)

            health.last_updated = datetime.now().isoformat()

        # Update system-wide foundational modules (top 20%)
        sorted_modules = sorted(
            self.health_map.modules.items(),
            key=lambda x: x[1].foundational_score,
            reverse=True
        )

        top_20_pct = max(1, len(sorted_modules) // 5)
        self.health_map.foundational_modules = [m[0] for m in sorted_modules[:top_20_pct]]

        self._save_health_map()

    def _recalculate_health(self, health: ModuleHealth):
        """Recalculate overall health score with weighted components."""
        weights = {
            'structural': 0.15,    # Size, cohesion, coupling
            'maintenance': 0.20,   # Stability, recency, bugs
            'knowledge': 0.25,     # Docs, tests, usage
            'dependency': 0.20,    # Centrality, criticality
            'pattern': 0.20        # Satisfaction, compliance
        }

        structural = (health.size_score + health.cohesion_score + health.coupling_score) / 3
        maintenance = (health.stability_score + health.recency_score + (1.0 - health.bug_density)) / 3
        knowledge = (health.documentation_score + health.test_coverage + health.usage_frequency) / 3
        dependency = (health.centrality_score + health.criticality_score) / 2
        pattern = (health.search_satisfaction + health.wsp_compliance) / 2

        health.overall_health = (
            weights['structural'] * structural +
            weights['maintenance'] * maintenance +
            weights['knowledge'] * knowledge +
            weights['dependency'] * dependency +
            weights['pattern'] * pattern
        )

    def get_module_health(self, module_path: str) -> Optional[ModuleHealth]:
        """Get health metrics for a specific module."""
        return self.health_map.modules.get(module_path)

    def get_unhealthy_modules(self, threshold: float = 0.4) -> List[Tuple[str, float]]:
        """Get modules below health threshold."""
        unhealthy = [
            (path, health.overall_health)
            for path, health in self.health_map.modules.items()
            if health.overall_health < threshold
        ]
        return sorted(unhealthy, key=lambda x: x[1])

    def get_foundational_modules(self) -> List[Tuple[str, float]]:
        """Get foundational modules sorted by foundational score."""
        foundational = [
            (path, health.foundational_score)
            for path, health in self.health_map.modules.items()
        ]
        return sorted(foundational, key=lambda x: x[1], reverse=True)

    def get_health_report(self) -> Dict:
        """Generate comprehensive health report."""
        if not self.health_map.modules:
            return {
                'total_modules': 0,
                'avg_health': 0.0,
                'message': 'No health data available yet - run searches to build health map'
            }

        healths = [h.overall_health for h in self.health_map.modules.values()]
        foundational = self.get_foundational_modules()
        unhealthy = self.get_unhealthy_modules()

        return {
            'total_modules': len(self.health_map.modules),
            'avg_health': sum(healths) / len(healths) if healths else 0,
            'health_distribution': {
                'excellent': len([h for h in healths if h >= 0.8]),
                'good': len([h for h in healths if 0.6 <= h < 0.8]),
                'fair': len([h for h in healths if 0.4 <= h < 0.6]),
                'poor': len([h for h in healths if h < 0.4])
            },
            'foundational_modules': foundational[:10],
            'unhealthy_modules': unhealthy[:10],
            'health_trend': self._calculate_health_trend()
        }

    def _calculate_health_trend(self) -> str:
        """Calculate if codebase health is improving or declining."""
        if len(self.health_map.health_trajectory) < 2:
            return 'insufficient_data'

        recent = self.health_map.health_trajectory[-5:]
        if len(recent) < 2:
            return 'insufficient_data'

        first_avg = sum(h[1] for h in recent[:len(recent)//2]) / (len(recent)//2)
        second_avg = sum(h[1] for h in recent[len(recent)//2:]) / (len(recent) - len(recent)//2)

        diff = second_avg - first_avg

        if diff > 0.05:
            return 'improving'
        elif diff < -0.05:
            return 'declining'
        else:
            return 'stable'

    def _load_health_map(self) -> CodebaseHealthMap:
        """Load health map from storage."""
        if not self.health_map_file.exists():
            return CodebaseHealthMap()

        try:
            with open(self.health_map_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # Reconstruct ModuleHealth objects
                modules = {}
                for path, health_data in data.get('modules', {}).items():
                    modules[path] = ModuleHealth(**health_data)

                health_map = CodebaseHealthMap(
                    modules=modules,
                    avg_health=data.get('avg_health', 0.5),
                    foundational_modules=data.get('foundational_modules', []),
                    unhealthy_modules=data.get('unhealthy_modules', []),
                    health_trajectory=data.get('health_trajectory', []),
                    last_scan=data.get('last_scan', datetime.now().isoformat())
                )

                return health_map
        except Exception as e:
            logger.warning(f"Error loading health map: {e}")
            return CodebaseHealthMap()

    def _save_health_map(self):
        """Save health map to storage."""
        try:
            # Update system-wide metrics before saving
            if self.health_map.modules:
                healths = [h.overall_health for h in self.health_map.modules.values()]
                self.health_map.avg_health = sum(healths) / len(healths)

                # Track system health evolution
                self.health_map.health_trajectory.append(
                    (datetime.now().isoformat(), self.health_map.avg_health)
                )
                if len(self.health_map.health_trajectory) > 100:
                    self.health_map.health_trajectory = self.health_map.health_trajectory[-100:]

                # Update unhealthy modules
                unhealthy = self.get_unhealthy_modules()
                self.health_map.unhealthy_modules = [m[0] for m in unhealthy[:20]]

            self.health_map.last_scan = datetime.now().isoformat()

            # Serialize
            data = {
                'modules': {path: asdict(health) for path, health in self.health_map.modules.items()},
                'avg_health': self.health_map.avg_health,
                'foundational_modules': self.health_map.foundational_modules,
                'unhealthy_modules': self.health_map.unhealthy_modules,
                'health_trajectory': self.health_map.health_trajectory,
                'last_scan': self.health_map.last_scan
            }

            with open(self.health_map_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving health map: {e}")
