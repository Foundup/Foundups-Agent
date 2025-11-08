#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mission planning helpers for AI Overseer.

Encapsulates Qwen strategic planning and WSP 15 scoring so the main
overseer module can stay focused on orchestration.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List

from .types import AgentRole, CoordinationPlan, MissionType

logger = logging.getLogger(__name__)


class MissionPlanningMixin:
    """Provides Qwen Phase 2 planning helpers."""

    daemon_logger = None

    def generate_coordination_plan(self, analysis: Dict[str, Any]) -> CoordinationPlan:
        """
        Phase 2: Qwen Partner strategic coordination planning.

        Qwen does simple stuff first, scales up over time.
        Uses WSP 15 scoring for prioritization.
        """
        planning_start = time.time()
        logger.info("[QWEN-PARTNER] Generating coordination plan...")

        mission_type = MissionType(analysis.get("mission_type", "custom"))
        complexity = analysis["classification"]["complexity"]

        phases = self._generate_mission_phases(mission_type, complexity, analysis)
        phases_with_mps = self._apply_wsp15_scoring(phases)

        plan = CoordinationPlan(
            mission_id=f"{mission_type.value}_{int(time.time())}",
            mission_type=mission_type,
            phases=phases_with_mps,
            estimated_complexity=complexity,
            recommended_approach=self._determine_approach(complexity),
            learning_patterns=analysis.get("patterns_detected", []),
        )

        if self.daemon_logger:
            planning_time = (time.time() - planning_start) * 1000
            self.daemon_logger.log_decision(
                decision_type="coordination_plan",
                chosen_path=plan.recommended_approach,
                confidence=0.85,
                reasoning=f"Qwen generated {len(phases)} phases for complexity {complexity}",
                mission_type=mission_type.value,
                phases=len(phases),
                planning_ms=planning_time,
            )

        logger.info(
            "[QWEN-PARTNER] Plan generated: %s phases, approach=%s",
            len(phases),
            plan.recommended_approach,
        )
        return plan

    def _generate_mission_phases(
        self,
        mission_type: MissionType,
        complexity: int,
        analysis: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Qwen generates strategic mission phases."""
        phases: List[Dict[str, Any]] = []
        phase_counter = 1

        def _append_phase(payload: Dict[str, Any]) -> None:
            nonlocal phase_counter
            payload["phase"] = phase_counter
            phases.append(payload)
            phase_counter += 1

        _append_phase(
            {
                "name": "Discovery",
                "agent": AgentRole.ASSOCIATE.value,
                "description": "Scan codebase for existing implementations",
                "complexity": 1,
                "estimated_time_ms": 100,
            }
        )

        _append_phase(
            {
                "name": "Analysis",
                "agent": AgentRole.PARTNER.value,
                "description": "Analyze requirements and dependencies",
                "complexity": 2,
                "estimated_time_ms": 500,
            }
        )

        pattern_report = analysis.get("pattern_coach", {})
        if pattern_report.get("message"):
            _append_phase(
                {
                    "name": "Pattern Coaching Review",
                    "agent": AgentRole.PARTNER.value,
                    "description": "Integrate pattern coach guidance before planning",
                    "complexity": 2,
                    "estimated_time_ms": 400,
                    "context": {
                        "coach_message": pattern_report["message"],
                        "stats": pattern_report.get("stats"),
                    },
                }
            )

        if complexity >= 3:
            _append_phase(
                {
                    "name": "Strategic Planning",
                    "agent": AgentRole.PARTNER.value,
                    "description": "Generate implementation strategy",
                    "complexity": complexity,
                    "estimated_time_ms": 2000,
                }
            )

        if complexity >= 4:
            _append_phase(
                {
                    "name": "Execution Oversight",
                    "agent": AgentRole.PRINCIPAL.value,
                    "description": "0102 supervises implementation for high-complexity work",
                    "complexity": complexity,
                    "estimated_time_ms": 10000,
                }
            )

        module_analysis = analysis.get("module_analysis", {})
        if module_analysis.get("size_findings") or module_analysis.get("structure_findings"):
            _append_phase(
                {
                    "name": "Module Health Remediation",
                    "agent": AgentRole.PRINCIPAL.value,
                    "description": "Address WSP 49/87 findings surfaced by module analysis",
                    "complexity": 3,
                    "estimated_time_ms": 2500,
                    "context": {
                        "size_findings": module_analysis.get("size_findings", [])[:3],
                        "structure_findings": module_analysis.get("structure_findings", [])[:3],
                    },
                }
            )

        wsp88 = analysis.get("wsp88", {})
        if wsp88.get("findings"):
            _append_phase(
                {
                    "name": "WSP 88 Connection Review",
                    "agent": AgentRole.PARTNER.value,
                    "description": "Review orphan analysis findings to create safe connections",
                    "complexity": 3,
                    "estimated_time_ms": 1800,
                    "context": {
                        "findings": wsp88["findings"][:3],
                        "report_excerpt": wsp88.get("report", "")[:500],
                    },
                }
            )

        health_check = analysis.get("health_check", {})
        if health_check.get("available"):
            _append_phase(
                {
                    "name": "System Health Verification",
                    "agent": AgentRole.PRINCIPAL.value,
                    "description": "Confirm architecture health signals from IntelligentSubroutineEngine",
                    "complexity": 2,
                    "estimated_time_ms": 1200,
                    "context": {
                        "summary": health_check.get("summary"),
                    },
                }
            )

        _append_phase(
            {
                "name": "Validation",
                "agent": AgentRole.ASSOCIATE.value,
                "description": "Validate implementation against requirements",
                "complexity": 2,
                "estimated_time_ms": 200,
            }
        )

        return phases

    def _apply_wsp15_scoring(self, phases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Qwen applies WSP 15 MPS scoring to prioritize phases."""
        for phase in phases:
            complexity = phase.get("complexity", 3)
            importance = 5 if phase["phase"] <= 2 else 3
            deferability = 5 - complexity
            impact = complexity

            mps_score = complexity + importance + deferability + impact

            if mps_score >= 16:
                priority = "P0"
            elif mps_score >= 13:
                priority = "P1"
            elif mps_score >= 10:
                priority = "P2"
            elif mps_score >= 7:
                priority = "P3"
            else:
                priority = "P4"

            phase["mps_score"] = mps_score
            phase["priority"] = priority

        return phases

    def _determine_approach(self, complexity: int) -> str:
        """Qwen determines recommended approach."""
        if complexity <= 2:
            return "autonomous_execution"
        if complexity <= 3:
            return "supervised_execution"
        return "collaborative_orchestration"
