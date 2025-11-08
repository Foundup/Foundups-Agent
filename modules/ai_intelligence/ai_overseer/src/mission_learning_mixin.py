#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Learning helpers for AI Overseer.

Encapsulates pattern storage logic so the mission orchestrator remains
within WSP 87 size limits.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict

from .types import AgentTeam

logger = logging.getLogger(__name__)


class MissionLearningMixin:
    """Provides Phase 4 learning helpers."""

    patterns: Dict[str, Any]
    holo_adapter = None

    def store_mission_pattern(self, team: AgentTeam):
        """Phase 4: Store mission results as learning pattern (WSP 48)."""
        pattern = {
            "timestamp": time.time(),
            "mission_id": team.mission_id,
            "mission_type": team.mission_type.value,
            "status": team.status,
            "results": team.results,
            "lessons_learned": {
                "complexity_estimate_accuracy": "TBD",
                "phase_execution_efficiency": "TBD",
                "agent_coordination_quality": "TBD",
            },
        }

        if team.results.get("success", False):
            self.patterns["successful_missions"].append(pattern)
            logger.info("[LEARNING] Stored successful mission pattern: %s", team.mission_id)
        else:
            self.patterns["failed_missions"].append(pattern)
            logger.warning("[LEARNING] Stored failed mission for analysis: %s", team.mission_id)

        self._save_patterns()

        if self.holo_adapter:
            try:
                _ = self.holo_adapter.analyze_exec_log(team.mission_id, team.results)
            except Exception:
                pass

        try:
            from .overseer_db import OverseerDB

            db = OverseerDB()
            db.record_mission(
                mission_id=team.mission_id,
                mission_type=team.mission_type.value,
                status=team.status,
                results=team.results,
            )
        except Exception:
            pass
