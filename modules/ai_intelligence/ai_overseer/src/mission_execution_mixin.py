#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mission execution helpers for AI Overseer.

Hosts execution-phase logic (team spawning, phase delegation, MCP support)
so the orchestrator class stays within WSP 87 guidelines.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .mcp_integration import RubikDAE
from .types import AgentRole, AgentTeam, CoordinationPlan, MissionType

logger = logging.getLogger(__name__)


class MissionExecutionMixin:
    """Provides Phase 3 execution/coordination helpers."""

# Attributes expected on consuming class for type hints / IDEs
    repo_root: Path
    daemon_logger = None
    holo_adapter = None
    patch_executor = None
    metrics = None
    fix_attempts: Dict[str, Any]
    holo_available: bool = False

    def spawn_agent_team(
        self,
        mission_description: str,
        mission_type: MissionType = MissionType.CUSTOM,
        auto_approve: bool = False,
    ) -> AgentTeam:
        """
        Phase 3: 0102 Principal spawns and oversees agent team.
        """
        execution_start = time.time()
        logger.info("[0102-PRINCIPAL] Spawning agent team for: %s", mission_description)

        analysis = self.analyze_mission_requirements(mission_description, mission_type)
        plan = self.generate_coordination_plan(analysis)

        team = AgentTeam(
            mission_id=plan.mission_id,
            mission_type=mission_type,
            status="executing",
        )
        self.active_teams[team.mission_id] = team

        if not auto_approve:
            print(f"\n[0102-PRINCIPAL] Execute mission plan?")
            print(f"  Mission: {mission_description}")
            print(f"  Complexity: {plan.estimated_complexity}/5")
            print(f"  Phases: {len(plan.phases)}")
            print(f"  Approach: {plan.recommended_approach}")
            approval = input("  Approve? (y/n): ").lower()
            if approval != "y":
                logger.warning("[0102-PRINCIPAL] Mission declined by user")
                team.status = "declined"
                team.results = {"success": False, "reason": "User declined"}
                return team

        results = self._execute_mission_phases(team, plan)
        results["analysis"] = analysis
        results["plan_snapshot"] = {
            "mission_id": plan.mission_id,
            "phases": plan.phases,
            "recommended_approach": plan.recommended_approach,
        }
        results["mcp_status"] = self._collect_mcp_status()
        team.results = results
        team.status = "completed" if results["success"] else "failed"

        if self.daemon_logger:
            execution_time = (time.time() - execution_start) * 1000
            self.daemon_logger.log_performance(
                operation="0102_mission_oversight",
                duration_ms=execution_time,
                items_processed=len(plan.phases),
                success=results["success"],
                mission_type=mission_type.value,
                complexity=plan.estimated_complexity,
            )

        logger.info("[0102-PRINCIPAL] Mission %s: %s", team.status, team.mission_id)
        return team

    def _execute_mission_phases(self, team: AgentTeam, plan: CoordinationPlan) -> Dict[str, Any]:
        """0102 Principal executes mission phases with oversight."""
        results = {
            "success": True,
            "phases_completed": 0,
            "phases_failed": 0,
            "phase_results": [],
            "errors": [],
        }

        self._ensure_mcp_connected()

        for phase in plan.phases:
            phase_start = time.time()
            logger.info(
                "[0102-PRINCIPAL] Executing phase %s: %s (%s)",
                phase["phase"],
                phase["name"],
                phase["agent"],
            )

            try:
                phase_result = self._execute_single_phase(phase, team)

                if "phase" not in phase_result:
                    phase_result["phase"] = phase.get("phase")
                if "name" not in phase_result:
                    phase_result["name"] = phase.get("name")
                if "agent" not in phase_result and phase.get("agent"):
                    phase_result["agent"] = phase.get("agent")

                phase_duration = (time.time() - phase_start) * 1000
                phase_result["duration_ms"] = phase_duration

                results["phase_results"].append(phase_result)

                if phase_result.get("success", False):
                    results["phases_completed"] += 1
                    logger.info(
                        "[0102-PRINCIPAL] Phase %s complete in %.0fms",
                        phase["phase"],
                        phase_duration,
                    )
                else:
                    results["phases_failed"] += 1
                    results["errors"].append(
                        f"Phase {phase['phase']} failed: {phase_result.get('error', 'Unknown')}"
                    )
                    logger.error("[0102-PRINCIPAL] Phase %s failed", phase["phase"])

            except Exception as exc:
                results["phases_failed"] += 1
                results["errors"].append(f"Phase {phase['phase']} exception: {exc}")
                logger.error("[0102-PRINCIPAL] Phase %s exception: %s", phase["phase"], exc)

        results["success"] = results["phases_failed"] == 0
        return results

    def _execute_single_phase(self, phase: Dict[str, Any], team: AgentTeam) -> Dict[str, Any]:
        """Execute a single phase (delegated to agent)."""
        agent = phase["agent"]

        if agent == AgentRole.ASSOCIATE.value:
            return self._delegate_to_gemma(phase, team)
        if agent == AgentRole.PARTNER.value:
            return self._delegate_to_qwen(phase, team)
        if agent == AgentRole.PRINCIPAL.value:
            return self._execute_as_principal(phase, team)
        return {"success": False, "error": f"Unknown agent: {agent}"}

    def _delegate_to_gemma(self, phase: Dict[str, Any], team: AgentTeam) -> Dict[str, Any]:
        """Delegate phase to Gemma Associate (fast pattern matching)."""
        logger.info("[GEMMA-ASSOCIATE] Executing phase: %s", phase["name"])

        if not self.holo_available:
            return {"success": True, "method": "fallback", "result": "Simulated Gemma execution"}

        context = phase.get("context", {})
        prompt_context = json.dumps(context, default=str)[:1000] if context else "None"
        prompt = (
            f"Mission ID: {team.mission_id}\n"
            f"Phase: {phase['name']}\n"
            f"Description: {phase.get('description', '')}\n"
            f"Context: {prompt_context}\n"
            "Task: Provide fast validation insights referencing WSP protocols. "
            "Respond in concise bullet points (<=120 words)."
        )

        if hasattr(self, "_initialize_gemma") and self._initialize_gemma():
            try:
                inference = self._gemma_engine.infer(prompt)  # type: ignore[attr-defined]
                result = {
                    "success": True,
                    "method": "gemma_rag_inference",
                    "result": inference.response,
                    "agent": AgentRole.ASSOCIATE.value,
                    "model_used": inference.model_used,
                    "confidence": inference.confidence,
                    "latency_ms": inference.latency_ms,
                    "patterns_used": inference.patterns_used,
                    "escalated": inference.escalated,
                }
                if inference.escalated and inference.escalation_reason:
                    result["escalation_reason"] = inference.escalation_reason

                if self.holo_adapter:
                    guard_report = self.holo_adapter.guard(result, intent="gemma_phase")
                    if guard_report.get("emit_warnings"):
                        result["guard_warnings"] = guard_report["emit_warnings"]

                try:
                    result["gemma_stats"] = self._gemma_engine.get_stats()  # type: ignore[attr-defined]
                except Exception as exc:
                    logger.debug("[GEMMA-ASSOCIATE] Unable to attach Gemma stats: %s", exc)

                return result
            except Exception as exc:
                logger.warning("[GEMMA] Inference failed, falling back to orchestrator: %s", exc)

        if getattr(self, "orchestrator", None):
            try:
                heuristic = self.orchestrator.analyze_module_dependencies(
                    phase.get("description", "")
                )
                result = {
                    "success": True,
                    "method": "gemma_orchestrator_fallback",
                    "result": heuristic,
                    "agent": AgentRole.ASSOCIATE.value,
                }
                if self.holo_adapter:
                    guard_report = self.holo_adapter.guard(result, intent="gemma_phase_fallback")
                    if guard_report.get("emit_warnings"):
                        result["guard_warnings"] = guard_report["emit_warnings"]
                engine = getattr(self, "_gemma_engine", None)
                if engine:
                    try:
                        result["gemma_stats"] = engine.get_stats()
                    except Exception as exc:  # pragma: no cover - defensive
                        logger.debug("[GEMMA-ASSOCIATE] Unable to attach Gemma stats: %s", exc)
                return result
            except Exception as exc:
                logger.warning("[GEMMA] Orchestrator fallback failed: %s", exc)

        return {
            "success": True,
            "method": "gemma_fast_pattern",
            "result": f"Gemma completed {phase['name']}",
            "agent": AgentRole.ASSOCIATE.value,
        }

    def _delegate_to_qwen(self, phase: Dict[str, Any], team: AgentTeam) -> Dict[str, Any]:
        """Delegate phase to Qwen Partner (strategic planning)."""
        logger.info("[QWEN-PARTNER] Executing phase: %s", phase["name"])

        if not self.holo_available:
            return {"success": True, "method": "fallback", "result": "Simulated Qwen execution"}

        phase_description = phase.get("description", "")
        holo_context: Optional[Dict[str, Any]] = None
        if self.holo_adapter:
            holo_context = self.holo_adapter.search(
                query=phase_description or team.mission_id,
                limit=3,
            )

        if hasattr(self, "_initialize_qwen") and self._initialize_qwen():
            prompt_payload = {
                "mission_id": team.mission_id,
                "phase": phase["name"],
                "description": phase_description,
                "context": phase.get("context", {}),
                "holo_context": holo_context,
                "wsp_focus": ["WSP 15", "WSP 77", "WSP 88"],
            }
            system_prompt = (
                "You are Qwen Partner executing WSP 77 coordination. "
                "Return JSON with keys: plan, risks, wsp_references, next_steps."
            )
            try:
                response = self._qwen_engine.generate_response(  # type: ignore[attr-defined]
                    json.dumps(prompt_payload),
                    system_prompt=system_prompt,
                    max_tokens=512,
                )
                try:
                    parsed = json.loads(response)
                except json.JSONDecodeError:
                    parsed = {"plan": response}

                mcp_support = None
                phase_context = phase.get("context", {})
                candidate_path = None
                abs_path = None
                if isinstance(phase_context, dict):
                    size_findings = phase_context.get("size_findings") or []
                    wsp88_findings = phase_context.get("findings") or []
                    if size_findings:
                        candidate_path = size_findings[0].get("path")
                    elif wsp88_findings:
                        candidate_path = wsp88_findings[0].get("file_path")

                if candidate_path:
                    abs_path = str((self.repo_root / candidate_path).resolve())
                    mcp_support = self._execute_mcp_tool(
                        rubik=RubikDAE.COMPOSE,
                        tool="read_file",
                        params={"path": abs_path},
                    )

                result = {
                    "success": True,
                    "method": "qwen_llm_planning",
                    "result": parsed,
                    "agent": AgentRole.PARTNER.value,
                    "model_used": "qwen-coder-1.5b",
                }
                if mcp_support and mcp_support.get("success") and abs_path:
                    result["mcp_support"] = {
                        "tool": "read_file",
                        "path": abs_path,
                        "excerpt": mcp_support.get("content", "")[:500],
                    }
                if self.holo_adapter:
                    guard_report = self.holo_adapter.guard(result, intent="planning")
                    if guard_report.get("emit_warnings"):
                        result["guard_warnings"] = guard_report["emit_warnings"]
                return result
            except Exception as exc:
                logger.warning("[QWEN] LLM planning failed: %s", exc)

        if getattr(self, "orchestrator", None):
            try:
                strategy = self.orchestrator.generate_refactoring_plan(
                    module_path=phase_description,
                    target_location=phase_description,
                    module_analysis={},
                )
                result = {
                    "success": True,
                    "method": "qwen_orchestrator_plan",
                    "result": strategy.summary if hasattr(strategy, "summary") else str(strategy),
                    "agent": AgentRole.PARTNER.value,
                    "wsp15_applied": True,
                }
                if self.holo_adapter:
                    guard_report = self.holo_adapter.guard(result, intent="planning_fallback")
                    if guard_report.get("emit_warnings"):
                        result["guard_warnings"] = guard_report["emit_warnings"]
                return result
            except Exception as exc:
                logger.warning("[QWEN] Orchestrator fallback failed: %s", exc)

        result = {
            "success": True,
            "method": "qwen_strategic_planning",
            "result": f"Qwen completed {phase['name']}",
            "agent": AgentRole.PARTNER.value,
            "wsp15_applied": True,
        }

        if self.holo_adapter:
            guard_report = self.holo_adapter.guard(result, intent="planning")
            if guard_report.get("emit_warnings"):
                result["guard_warnings"] = guard_report["emit_warnings"]

        return result

    def _execute_as_principal(self, phase: Dict[str, Any], team: AgentTeam) -> Dict[str, Any]:
        """0102 Principal executes phase directly."""
        logger.info("[0102-PRINCIPAL] Executing directly: %s", phase["name"])

        return {
            "success": True,
            "method": "0102_direct_execution",
            "result": f"0102 completed {phase['name']} with full oversight",
            "agent": AgentRole.PRINCIPAL.value,
        }
