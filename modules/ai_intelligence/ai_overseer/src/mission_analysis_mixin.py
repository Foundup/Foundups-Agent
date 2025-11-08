#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mission analysis helpers for AI Overseer.

Contains Gemma-driven Phase 1 analysis utilities that were previously
embedded in `ai_overseer.py`. Factoring these into a mixin keeps the
main orchestrator lean while preserving behaviour.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List

from .types import MissionType

logger = logging.getLogger(__name__)


class MissionAnalysisMixin:
    """Provides Gemma Phase 1 analysis logic for AI Overseer."""

    holo_adapter = None  # hint for mypy/IDE – set in concrete class
    daemon_logger = None
    orchestrator = None
    holo_available: bool = False

    def analyze_mission_requirements(
        self,
        mission_description: str,
        mission_type: MissionType = MissionType.CUSTOM,
    ) -> Dict[str, Any]:
        """
        Phase 1: Gemma Associate fast pattern analysis.

        Args:
            mission_description: Human-readable mission description
            mission_type: Type of mission to coordinate

        Returns:
            Fast analysis results from Gemma (50-100ms)
        """
        analysis_start = time.time()
        logger.info(f"[GEMMA-ASSOCIATE] Analyzing mission: {mission_description}")

        if not self.holo_available or not self.orchestrator:
            logger.warning("[GEMMA-ASSOCIATE] Holo not available, using fallback analysis")
            return {
                "method": "fallback",
                "mission_type": mission_type.value,
                "complexity": 3,
                "requires_coordination": True,
            }

        analysis = {
            "method": "gemma_fast_classification",
            "mission_type": mission_type.value,
            "description": mission_description,
            "classification": self._classify_mission_complexity(mission_description),
            "patterns_detected": self._detect_known_patterns(mission_description),
            "recommended_team": self._recommend_team_composition(mission_type),
        }

        if self.daemon_logger:
            analysis_time = (time.time() - analysis_start) * 1000
            self.daemon_logger.log_performance(
                operation="gemma_mission_analysis",
                duration_ms=analysis_time,
                items_processed=1,
                success=True,
                mission_type=mission_type.value,
                complexity=analysis["classification"]["complexity"],
            )

        logger.info(
            "[GEMMA-ASSOCIATE] Analysis complete: complexity=%s",
            analysis["classification"]["complexity"],
        )

        if self.holo_adapter:
            holo_search = self.holo_adapter.search(mission_description, limit=5)
            analysis["holo_search"] = holo_search

            pattern_report = self.holo_adapter.run_pattern_coach(
                query=mission_description,
                search_results=holo_search.get("code", []),
                health_warnings=holo_search.get("warnings", []),
            )
            analysis["pattern_coach"] = pattern_report

            if mission_type in {
                MissionType.MODULE_INTEGRATION,
                MissionType.CODE_ANALYSIS,
                MissionType.WSP_COMPLIANCE,
            }:
                analysis["module_analysis"] = self.holo_adapter.run_module_analysis(limit=5)

            if mission_type in {
                MissionType.ARCHITECTURE_DESIGN,
                MissionType.TESTING_ORCHESTRATION,
                MissionType.WSP_COMPLIANCE,
            }:
                analysis["health_check"] = self.holo_adapter.run_health_check()

            analysis["wsp88"] = self.holo_adapter.run_wsp88_orphan_analysis(limit=5)

            engine = getattr(self, "_gemma_engine", None)
            if engine:
                try:
                    analysis["gemma_stats"] = engine.get_stats()
                except Exception as exc:
                    logger.debug("[GEMMA-ASSOCIATE] Unable to collect Gemma stats: %s", exc)

        analysis["mcp_status"] = self._collect_mcp_status()
        return analysis

    def _classify_mission_complexity(self, description: str) -> Dict[str, Any]:
        """Gemma fast complexity classification"""
        complexity = 1  # Default: simple

        if any(
            keyword in description.lower()
            for keyword in ["multi", "complex", "architecture", "system-wide"]
        ):
            complexity = 5
        elif any(
            keyword in description.lower() for keyword in ["integrate", "coordinate", "multiple"]
        ):
            complexity = 4
        elif any(
            keyword in description.lower()
            for keyword in ["refactor", "enhance", "optimize"]
        ):
            complexity = 3
        elif any(keyword in description.lower() for keyword in ["test", "validate", "check"]):
            complexity = 2

        return {
            "complexity": complexity,
            "estimated_phases": complexity,
            "requires_qwen_planning": complexity >= 3,
            "requires_0102_oversight": complexity >= 4,
        }

    def _detect_known_patterns(self, description: str) -> List[str]:
        """Detect known patterns from memory"""
        detected: List[str] = []

        for strategy_name, strategy_data in self.patterns.get("learned_strategies", {}).items():
            if any(
                keyword in description.lower()
                for keyword in strategy_data.get("keywords", [])
            ):
                detected.append(strategy_name)

        return detected

    def _recommend_team_composition(self, mission_type: MissionType) -> Dict[str, str]:
        """Recommend team composition based on mission type"""
        return {
            "partner": "qwen",  # Qwen: Simple tasks, scales up
            "principal": "0102",  # 0102: Plans and oversees
            "associate": "gemma",  # Gemma: Pattern recognition
        }
