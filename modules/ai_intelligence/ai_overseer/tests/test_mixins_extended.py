#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extended mixin coverage for AI Overseer."""

from __future__ import annotations

from pathlib import Path

from modules.ai_intelligence.ai_overseer.src.mission_analysis_mixin import MissionAnalysisMixin
from modules.ai_intelligence.ai_overseer.src.mission_execution_mixin import MissionExecutionMixin
from modules.ai_intelligence.ai_overseer.src.mission_planning_mixin import MissionPlanningMixin
from modules.ai_intelligence.ai_overseer.src.types import AgentRole, AgentTeam, CoordinationPlan, MissionType


class _AnalysisEnrichedStub(MissionAnalysisMixin):
    holo_available = True
    orchestrator = object()
    daemon_logger = None
    holo_adapter = None
    patterns = {"learned_strategies": {}}

    def _collect_mcp_status(self):
        return {"available": False, "source": "stub"}


def test_analysis_includes_mcp_status():
    stub = _AnalysisEnrichedStub()
    result = stub.analyze_mission_requirements("quick health check", MissionType.CUSTOM)
    assert result["mcp_status"]["source"] == "stub"


class _PlanningEnrichedStub(MissionPlanningMixin):
    daemon_logger = None


def test_planning_adds_pattern_phase_when_coach_message_present():
    stub = _PlanningEnrichedStub()
    analysis = {
        "mission_type": MissionType.CUSTOM.value,
        "classification": {"complexity": 3},
        "pattern_coach": {"message": "Provide documentation guidance", "stats": {}},
    }
    phases = stub._generate_mission_phases(MissionType.CUSTOM, 3, analysis)
    assert any(phase["name"] == "Pattern Coaching Review" for phase in phases)


class _ExecutionFailureStub(MissionExecutionMixin):
    repo_root = Path(".")
    holo_available = False
    holo_adapter = None
    daemon_logger = None
    patch_executor = None
    metrics = None
    fix_attempts = {}

    def _ensure_mcp_connected(self):
        return None

    def _execute_single_phase(self, phase, team):
        if phase["phase"] == 1:
            return {"success": False, "error": "boom", "agent": AgentRole.ASSOCIATE.value}
        return {"success": True, "agent": phase["agent"]}


def test_execute_mission_phases_flags_failure():
    stub = _ExecutionFailureStub()
    team = AgentTeam("mission-1", MissionType.CUSTOM)
    plan = CoordinationPlan(
        mission_id="mission-1",
        mission_type=MissionType.CUSTOM,
        phases=[
            {"phase": 1, "name": "Discovery", "agent": AgentRole.ASSOCIATE.value},
            {"phase": 2, "name": "Analysis", "agent": AgentRole.PARTNER.value},
        ],
        estimated_complexity=2,
        recommended_approach="autonomous_execution",
    )
    result = stub._execute_mission_phases(team, plan)
    assert not result["success"]
    assert result["phases_failed"] == 1
    assert any("boom" in err for err in result["errors"])
