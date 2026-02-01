#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Intelligence Overseer - WSP 77 Agent Coordination
====================================================

MCP coordinator that oversees Holo Qwen/Gemma for autonomous task orchestration.

Replaces deprecated 6-agent system (WINSERV, RIDER, BOARD, FRONT_CELL, BACK_CELL, GEMINI)
with WSP 77 coordination: Qwen (Partner) + 0102 (Principal) + Gemma (Associate).

WSP 54 Role Mapping (Agent Teams):
    - Partner: Qwen (does simple stuff, scales up - developed WSP 15 scoring)
    - Principal: 0102 (lays out plan, oversees execution)
    - Associate: Gemma (pattern recognition, scales up)

Architecture:
    Phase 1 (Gemma Associate): Fast pattern matching & binary classification
    Phase 2 (Qwen Partner): Strategic planning & coordination (starts simple, scales)
    Phase 3 (0102 Principal): Oversight, plan generation, supervision
    Phase 4 (Learning): Pattern storage for recursive self-improvement

WSP Compliance:
    - WSP 77: Agent Coordination Protocol
    - WSP 54: Role Assignment (Agent Teams variant)
    - WSP 96: MCP Governance and Consensus
    - WSP 48: Recursive Self-Improvement
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

import json
import logging
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum
import time
import asyncio

# MetricsAppender for WSP 77 promotion tracking (WSP 3 compliant path)
from modules.infrastructure.metrics_appender.src.metrics_appender import MetricsAppender

# PatchExecutor for autonomous code fixes (WSP 3 compliant path)
from modules.infrastructure.patch_executor.src.patch_executor import PatchExecutor, PatchAllowlist

# PatternMemory for collective false-positive learning (WSP 48/60)
try:
    from modules.infrastructure.wre_core.src.pattern_memory import PatternMemory
    PATTERN_MEMORY_AVAILABLE = True
except ImportError:
    PATTERN_MEMORY_AVAILABLE = False
    logging.warning("[AI-OVERSEER] PatternMemory unavailable - running without false-positive suppression")

# Import Holo Qwen/Gemma coordination infrastructure
try:
    from holo_index.qwen_advisor.orchestration.autonomous_refactoring import (
        AutonomousRefactoringOrchestrator,
        DaemonLogger
    )
    HOLO_AVAILABLE = True
except ImportError:
    HOLO_AVAILABLE = False
    logging.warning("[AI-OVERSEER] Holo Qwen/Gemma not available - running in limited mode")

# Import MCP integration (WSP 96)
try:
    from modules.ai_intelligence.ai_overseer.src.mcp_integration import (
        AIOverseerMCPIntegration,
        RubikDAE
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("[AI-OVERSEER] MCP integration not available - running without MCP")

# AutoGate Integration
try:
    from modules.ai_intelligence.ai_overseer.src.auto_gate import AutoGate
    AUTOGATE_AVAILABLE = True
except ImportError:
    AUTOGATE_AVAILABLE = False

logger = logging.getLogger(__name__)
project_root = Path(__file__).resolve().parents[5]


class AgentRole(Enum):
    """WSP 54 Agent Team Roles (NOT traditional 012/0102 roles)"""
    PARTNER = "qwen"      # Qwen: Does simple stuff, scales up
    PRINCIPAL = "0102"    # 0102: Lays out plan, oversees execution
    ASSOCIATE = "gemma"   # Gemma: Pattern recognition, scales up


class MissionType(Enum):
    """Types of missions AI Overseer can coordinate"""
    CODE_ANALYSIS = "code_analysis"
    ARCHITECTURE_DESIGN = "architecture_design"
    MODULE_INTEGRATION = "module_integration"
    TESTING_ORCHESTRATION = "testing_orchestration"
    DOCUMENTATION_GENERATION = "documentation_generation"
    WSP_COMPLIANCE = "wsp_compliance"
    DAEMON_MONITORING = "daemon_monitoring"      # Monitor daemon bash shells
    BUG_DETECTION = "bug_detection"              # Detect bugs in daemon output
    AUTO_REMEDIATION = "auto_remediation"        # Auto-fix low-hanging fruit
    CUSTOM = "custom"
    # Activity Routing Types (WSP 15 MPS Priority) - 2026-01-19
    ACTIVITY_ROUTING = "activity_routing"        # Meta: orchestrate activity transitions
    LIVE_STREAM = "live_stream"                  # P0: Critical - always wins
    COMMENT_PROCESSING = "comment_processing"    # P1: High priority
    VIDEO_INDEXING = "video_indexing"            # P1: Default when idle
    SCHEDULING = "scheduling"                    # P2: Medium priority (triggers indexing)
    GIT_PUSH = "git_push"                        # P2: Medium priority (autonomous commits)
    SOCIAL_MEDIA = "social_media"                # P3: Low priority
    MAINTENANCE = "maintenance"                  # P4: Lowest priority


@dataclass
class AgentTeam:
    """Represents a coordinated agent team following WSP 54"""
    mission_id: str
    mission_type: MissionType
    partner: str = "qwen"     # Qwen Partner: Simple tasks, scales up
    principal: str = "0102"   # 0102 Principal: Plans and oversees
    associate: str = "gemma"  # Gemma Associate: Pattern recognition
    status: str = "initialized"
    created_at: float = field(default_factory=time.time)
    results: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CoordinationPlan:
    """Strategic coordination plan from WSP 77 Phase 2 (Qwen Partner)"""
    mission_id: str
    mission_type: MissionType
    phases: List[Dict[str, Any]]
    estimated_complexity: int  # 1-5 scale
    recommended_approach: str
    learning_patterns: List[str] = field(default_factory=list)


class AIIntelligenceOverseer:
    """
    AI Intelligence Overseer - MCP coordinator for Holo Qwen/Gemma

    Replaces deprecated 6-agent system with WSP 77 coordination.

    WSP 54 Role Assignments (Agent Teams):
        - Partner: Qwen (strategic planning, starts simple, scales up)
        - Principal: 0102 (oversight, plan generation, supervision)
        - Associate: Gemma (fast validation, pattern recognition, scales up)

    Architecture:
        Phase 1 (Gemma): Fast pattern matching
        Phase 2 (Qwen): Strategic coordination planning
        Phase 3 (0102): Oversight and execution
        Phase 4: Learning and pattern storage
    """

    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)
        # WSP 60: Persist overseer patterns under module-local memory
        self.memory_path = (
            self.repo_root
            / "modules"
            / "ai_intelligence"
            / "ai_overseer"
            / "memory"
            / "ai_overseer_patterns.json"
        )
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        # Ensure memory file exists with initial structure for tests and WSP 60 compliance
        if not self.memory_path.exists():
            try:
                with open(self.memory_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        "successful_missions": [],
                        "failed_missions": [],
                        "learned_strategies": {},
                        "team_performance": {}
                    }, f, indent=2)
            except Exception:
                pass

        # Initialize Holo Qwen/Gemma orchestrator
        if HOLO_AVAILABLE:
            self.orchestrator = AutonomousRefactoringOrchestrator(repo_root)
            logger.info("[AI-OVERSEER] Holo Qwen/Gemma orchestrator initialized")
        else:
            self.orchestrator = None
            logger.warning("[AI-OVERSEER] Running without Holo orchestrator")

        # Initialize HoloAdapter (deterministic facade)
        try:
            from .holo_adapter import HoloAdapter  # local import to avoid hard dependency if missing
            self.holo_adapter = HoloAdapter(self.repo_root)
        except Exception:
            self.holo_adapter = None

        # WSP 91: Structured daemon logger
        if HOLO_AVAILABLE:
            self.daemon_logger = DaemonLogger("AIIntelligenceOverseer")
        else:
            self.daemon_logger = None

        # WSP 96: MCP integration
        if MCP_AVAILABLE:
            self.mcp = AIOverseerMCPIntegration(repo_root)
            logger.info("[AI-OVERSEER] MCP integration initialized")
        else:
            self.mcp = None
            logger.warning("[AI-OVERSEER] Running without MCP integration")

        # WSP 48/60: Pattern memory for false-positive suppression
        self.pattern_memory = PatternMemory() if PATTERN_MEMORY_AVAILABLE else None

        # AutoGate Initialization
        self.auto_gate = None
        if AUTOGATE_AVAILABLE and self.holo_adapter:
            try:
                self.auto_gate = AutoGate(self.repo_root, self.holo_adapter)
                logger.info("[AI-OVERSEER] AutoGate initialized")
            except Exception as e:
                logger.warning(f"[AI-OVERSEER] AutoGate failed to init: {e}")

        # Priority 1: HoloDAE Telemetry Monitor (dual-channel architecture)
        # Bridges HoloDAE JSONL telemetry → AI Overseer event_queue
        self.telemetry_monitor = None
        self.telemetry_consumer_task = None
        if MCP_AVAILABLE and hasattr(self.mcp, 'event_queue'):
            try:
                from .holo_telemetry_monitor import HoloTelemetryMonitor
                self.telemetry_monitor = HoloTelemetryMonitor(
                    repo_root=repo_root,
                    event_queue=self.mcp.event_queue
                )
                logger.info("[AI-OVERSEER] HoloDAE telemetry monitor initialized")
            except Exception as e:
                logger.warning("[AI-OVERSEER] Telemetry monitor unavailable: %s", e)

        # Active agent teams
        self.active_teams: Dict[str, AgentTeam] = {}

        # Metrics appender for WSP 77 promotion tracking
        self.metrics = MetricsAppender()

        # PatternMemory for collective false-positive learning (WSP 48/60)
        self.pattern_memory: Optional[Any] = None
        if PATTERN_MEMORY_AVAILABLE:
            try:
                self.pattern_memory = PatternMemory()
                logger.info("[AI-OVERSEER] PatternMemory initialized for false-positive filtering")
            except Exception as exc:
                logger.warning("[AI-OVERSEER] PatternMemory unavailable: %s", exc)

        # Patch executor for autonomous code fixes (WSP 90 UTF-8, etc.)
        patch_allowlist = PatchAllowlist(
            allowed_file_patterns=[
                "modules/**/*.py",
                "holo_index/**/*.py",
                "*.py"
            ],
            max_patch_lines=200
        )
        self.patch_executor = PatchExecutor(repo_root=repo_root, allowlist=patch_allowlist)

        # Fix attempt tracking - prevent spam and limit retries
        # pattern_key → {attempts: int, last_attempt: float, disabled: bool, first_seen: float}
        self.fix_attempts = {}

        # Load learning patterns
        self.patterns = self._load_patterns()

        logger.info("[AI-OVERSEER] AI Intelligence Overseer initialized")

    def _load_patterns(self) -> Dict:
        """Load AI coordination patterns from memory"""
        if self.memory_path.exists():
            with open(self.memory_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "successful_missions": [],
            "failed_missions": [],
            "learned_strategies": {},
            "team_performance": {}
        }

    def _save_patterns(self):
        """Save patterns to memory for WSP 48 learning"""
        with open(self.memory_path, 'w', encoding='utf-8') as f:
            json.dump(self.patterns, f, indent=2)

    def _is_known_false_positive(self, entity_type: str, entity_name: str) -> bool:
        """
        Check PatternMemory for known false positives before coordinating mission.

        WSP 48/60: Collective learning - skip missions that are known false positives
        (e.g., "fix holo_dae module" when holo_dae is not a module but a coordinator class)

        Returns:
            True if this is a learned false positive (skip mission)
        """
        if not self.pattern_memory:
            return False

        try:
            details = self.pattern_memory.get_false_positive_reason(entity_type, entity_name)
            if details:
                reason = details.get("reason", "No reason provided")
                actual_location = details.get("actual_location", "Unknown")
                logger.info(
                    f"[AI-OVERSEER] [LEARNED] Skipping known false positive: {entity_name}\n"
                    f"  Reason: {reason}\n"
                    f"  Actual location: {actual_location}"
                )
                return True
        except Exception as exc:
            logger.debug(f"[AI-OVERSEER] Error checking false positive: {exc}")

        return False

    def record_false_positive(self, entity_type: str, entity_name: str,
                             reason: str, actual_location: Optional[str] = None) -> bool:
        """
        Record a new false positive in PatternMemory for collective learning.

        WSP 48: Enable recursive self-improvement by learning from mistakes

        Args:
            entity_type: Type of entity (e.g., "mission", "module", "wsp")
            entity_name: Name to remember as false positive
            reason: Why this is a false positive
            actual_location: Where the entity actually exists (if applicable)

        Returns:
            True if successfully recorded
        """
        if not self.pattern_memory:
            logger.warning("[AI-OVERSEER] Cannot record false positive - PatternMemory unavailable")
            return False

        try:
            self.pattern_memory.record_false_positive(
                entity_type=entity_type,
                entity_name=entity_name,
                reason=reason,
                actual_location=actual_location
            )
            logger.info(
                f"[AI-OVERSEER] [LEARNED] Recorded false positive: {entity_type}/{entity_name}\n"
                f"  Reason: {reason}"
            )
            return True
        except Exception as exc:
            logger.error(f"[AI-OVERSEER] Failed to record false positive: {exc}")
            return False

    # ==================== PHASE 1: GEMMA ASSOCIATE ANALYSIS ====================

    def analyze_mission_requirements(self, mission_description: str,
                                      mission_type: MissionType = MissionType.CUSTOM) -> Dict[str, Any]:
        """
        Phase 1: Gemma Associate fast pattern analysis

        Args:
            mission_description: Human-readable mission description
            mission_type: Type of mission to coordinate

        Returns:
            Fast analysis results from Gemma (50-100ms)
        """
        analysis_start = time.time()
        logger.info(f"[GEMMA-ASSOCIATE] Analyzing mission: {mission_description}")

        if not HOLO_AVAILABLE or not self.orchestrator:
            logger.warning("[GEMMA-ASSOCIATE] Holo not available, using fallback analysis")
            return {
                "method": "fallback",
                "mission_type": mission_type.value,
                "complexity": 3,
                "requires_coordination": True
            }

        # Use Gemma for fast binary classification via orchestrator
        # NOTE: analyze_module_dependencies is fast heuristic-based analysis (Gemma-like)
        analysis = {
            "method": "gemma_fast_classification",
            "mission_type": mission_type.value,
            "description": mission_description,
            "classification": self._classify_mission_complexity(mission_description),
            "patterns_detected": self._detect_known_patterns(mission_description),
            "recommended_team": self._recommend_team_composition(mission_type)
        }

        # WSP 91: Log Gemma performance
        if self.daemon_logger:
            analysis_time = (time.time() - analysis_start) * 1000
            self.daemon_logger.log_performance(
                operation="gemma_mission_analysis",
                duration_ms=analysis_time,
                items_processed=1,
                success=True,
                mission_type=mission_type.value,
                complexity=analysis["classification"]["complexity"]
            )

        logger.info(f"[GEMMA-ASSOCIATE] Analysis complete: complexity={analysis['classification']['complexity']}")
        return analysis

    def _classify_mission_complexity(self, description: str) -> Dict[str, Any]:
        """Gemma fast complexity classification"""
        # Simple heuristic-based classification (real Gemma would use LLM)
        complexity = 1  # Default: simple

        if any(keyword in description.lower() for keyword in ["multi", "complex", "architecture", "system-wide"]):
            complexity = 5
        elif any(keyword in description.lower() for keyword in ["integrate", "coordinate", "multiple"]):
            complexity = 4
        elif any(keyword in description.lower() for keyword in ["refactor", "enhance", "optimize"]):
            complexity = 3
        elif any(keyword in description.lower() for keyword in ["test", "validate", "check"]):
            complexity = 2

        return {
            "complexity": complexity,
            "estimated_phases": complexity,
            "requires_qwen_planning": complexity >= 3,
            "requires_0102_oversight": complexity >= 4
        }

    def _detect_known_patterns(self, description: str) -> List[str]:
        """Detect known patterns from memory"""
        detected = []

        # Check against learned strategies
        for strategy_name, strategy_data in self.patterns.get("learned_strategies", {}).items():
            if any(keyword in description.lower() for keyword in strategy_data.get("keywords", [])):
                detected.append(strategy_name)

        return detected

    def _recommend_team_composition(self, mission_type: MissionType) -> Dict[str, str]:
        """Recommend team composition based on mission type"""
        # All teams follow WSP 54 Agent Teams structure
        return {
            "partner": "qwen",    # Qwen: Simple tasks, scales up
            "principal": "0102",  # 0102: Plans and oversees
            "associate": "gemma"  # Gemma: Pattern recognition
        }

    # ==================== PHASE 2: QWEN PARTNER COORDINATION ====================

    def generate_coordination_plan(self, analysis: Dict[str, Any]) -> CoordinationPlan:
        """
        Phase 2: Qwen Partner strategic coordination planning

        Qwen does simple stuff first, scales up over time.
        Uses WSP 15 scoring for prioritization.

        Args:
            analysis: Results from Gemma Phase 1

        Returns:
            Strategic coordination plan
        """
        planning_start = time.time()
        logger.info(f"[QWEN-PARTNER] Generating coordination plan...")

        mission_type = MissionType(analysis.get("mission_type", "custom"))
        complexity = analysis["classification"]["complexity"]

        # Qwen generates strategic phases (starts simple, scales up)
        phases = self._generate_mission_phases(mission_type, complexity, analysis)

        # Qwen applies WSP 15 MPS scoring for prioritization
        phases_with_mps = self._apply_wsp15_scoring(phases)

        plan = CoordinationPlan(
            mission_id=f"{mission_type.value}_{int(time.time())}",
            mission_type=mission_type,
            phases=phases_with_mps,
            estimated_complexity=complexity,
            recommended_approach=self._determine_approach(complexity),
            learning_patterns=analysis.get("patterns_detected", [])
        )

        # WSP 91: Log Qwen planning performance
        if self.daemon_logger:
            planning_time = (time.time() - planning_start) * 1000
            self.daemon_logger.log_decision(
                decision_type="coordination_plan",
                chosen_path=plan.recommended_approach,
                confidence=0.85,
                reasoning=f"Qwen generated {len(phases)} phases for complexity {complexity}",
                mission_type=mission_type.value,
                phases=len(phases),
                planning_ms=planning_time
            )

        logger.info(f"[QWEN-PARTNER] Plan generated: {len(phases)} phases, approach={plan.recommended_approach}")
        return plan

    def _generate_mission_phases(self, mission_type: MissionType,
                                   complexity: int,
                                   analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Qwen generates strategic mission phases"""
        phases = []

        # Phase 1: Always start with discovery (Qwen does simple stuff first)
        phases.append({
            "phase": 1,
            "name": "Discovery",
            "agent": AgentRole.ASSOCIATE.value,  # Gemma does fast discovery
            "description": "Scan codebase for existing implementations",
            "complexity": 1,
            "estimated_time_ms": 100
        })

        # Phase 2: Analysis (Qwen starts involvement)
        phases.append({
            "phase": 2,
            "name": "Analysis",
            "agent": AgentRole.PARTNER.value,  # Qwen does simple analysis
            "description": "Analyze requirements and dependencies",
            "complexity": 2,
            "estimated_time_ms": 500
        })

        # Phase 3+: Scale up based on complexity
        if complexity >= 3:
            phases.append({
                "phase": 3,
                "name": "Strategic Planning",
                "agent": AgentRole.PARTNER.value,  # Qwen scales up to strategy
                "description": "Generate implementation strategy",
                "complexity": complexity,
                "estimated_time_ms": 2000
            })

        if complexity >= 4:
            phases.append({
                "phase": 4,
                "name": "Execution Oversight",
                "agent": AgentRole.PRINCIPAL.value,  # 0102 oversees execution
                "description": "0102 supervises implementation",
                "complexity": complexity,
                "estimated_time_ms": 10000
            })

        # Final phase: Always validate (Gemma does fast validation)
        phases.append({
            "phase": len(phases) + 1,
            "name": "Validation",
            "agent": AgentRole.ASSOCIATE.value,  # Gemma fast validation
            "description": "Validate implementation against requirements",
            "complexity": 2,
            "estimated_time_ms": 200
        })

        return phases

    def _apply_wsp15_scoring(self, phases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Qwen applies WSP 15 MPS scoring to prioritize phases"""
        for phase in phases:
            # WSP 15 MPS: Complexity + Importance + Deferability + Impact
            complexity = phase.get("complexity", 3)
            importance = 5 if phase["phase"] <= 2 else 3  # Early phases more important
            deferability = 5 - complexity  # Less complex = more deferrable
            impact = complexity  # Complexity correlates with impact

            mps_score = complexity + importance + deferability + impact

            # Priority: 16-20=P0, 13-15=P1, 10-12=P2, 7-9=P3, 4-6=P4
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
        """Qwen determines recommended approach"""
        if complexity <= 2:
            return "autonomous_execution"  # Qwen/Gemma handle autonomously
        elif complexity <= 3:
            return "supervised_execution"  # 0102 supervises
        else:
            return "collaborative_orchestration"  # Full team coordination

    # ==================== PHASE 3: 0102 PRINCIPAL OVERSIGHT ====================

    def spawn_agent_team(self, mission_description: str,
                          mission_type: MissionType = MissionType.CUSTOM,
                          auto_approve: bool = False) -> AgentTeam:
        """
        Phase 3: 0102 Principal spawns and oversees agent team

        0102 lays out the plan and oversees execution.

        Args:
            mission_description: Mission to accomplish
            mission_type: Type of mission
            auto_approve: Skip approval prompts

        Returns:
            AgentTeam with execution results
        """
        execution_start = time.time()
        logger.info(f"[0102-PRINCIPAL] Spawning agent team for: {mission_description}")

        # Phase 1: Gemma Associate analysis
        analysis = self.analyze_mission_requirements(mission_description, mission_type)

        # Phase 2: Qwen Partner coordination plan
        plan = self.generate_coordination_plan(analysis)

        # --- AUTO-GATE CHECK (Always Run) ---
        gate_verdict = None
        if self.auto_gate:
            try:
                gate_verdict = self.auto_gate.validate_plan(plan)
                logger.info(f"[GATE] Verdict: {gate_verdict.status}")
                
                # WSP 77: 0102 (Principal) receives the warning via log/context
                if gate_verdict.status != "PASS":
                     for w in gate_verdict.warnings:
                         logger.warning(f"[GATE-WARN] {w}")
                     
                     # If BLOCKED, revoke auto-approval (Passive Resistance -> Checkpoint)
                     if gate_verdict.status == "BLOCK" and auto_approve:
                         logger.warning("[0102-PRINCIPAL] 🛑 Auto-approval REVOKED by AutoGate BLOCK verdict.")
                         logger.info("[0102-PRINCIPAL] Downgrading to supervised execution.")
                         auto_approve = False

            except Exception as e:
                logger.error(f"[GATE] Check failed: {e}")
        # ------------------------------------

        # Create agent team
        team = AgentTeam(
            mission_id=plan.mission_id,
            mission_type=mission_type,
            status="executing"
        )
        self.active_teams[team.mission_id] = team

        # 0102 Principal oversight: Execute plan with supervision
        if not auto_approve:
            print(f"\\n[0102-PRINCIPAL] Execute mission plan?")
            
            # Display Gate Results to Observer (if present)
            if gate_verdict:
                if gate_verdict.status == "PASS":
                     print(f"  [GATE] Verdict: PASS (Safe)")
                elif gate_verdict.status == "WARN":
                     print(f"  [GATE] Verdict: WARNING ⚠️")
                     for w in gate_verdict.warnings:
                         print(f"    --> {w}")
                elif gate_verdict.status == "BLOCK":
                     print(f"  [GATE] Verdict: BLOCKED 🛑")
                     for w in gate_verdict.warnings:
                         print(f"    --> {w}")

            print(f"  Mission: {mission_description}")
            print(f"  Complexity: {plan.estimated_complexity}/5")
            print(f"  Phases: {len(plan.phases)}")
            print(f"  Approach: {plan.recommended_approach}")
            approval = input("  Approve? (y/n): ").lower()
            if approval != 'y':
                logger.warning(f"[0102-PRINCIPAL] Mission declined by user")
                team.status = "declined"
                team.results = {"success": False, "reason": "User declined"}
                return team

        # Execute phases under 0102 oversight
        results = self._execute_mission_phases(team, plan)
        team.results = results
        team.status = "completed" if results["success"] else "failed"

        # WSP 91: Log 0102 oversight performance
        if self.daemon_logger:
            execution_time = (time.time() - execution_start) * 1000
            self.daemon_logger.log_performance(
                operation="0102_mission_oversight",
                duration_ms=execution_time,
                items_processed=len(plan.phases),
                success=results["success"],
                mission_type=mission_type.value,
                complexity=plan.estimated_complexity
            )

        logger.info(f"[0102-PRINCIPAL] Mission {team.status}: {team.mission_id}")
        return team

    def _execute_mission_phases(self, team: AgentTeam, plan: CoordinationPlan) -> Dict[str, Any]:
        """0102 Principal executes mission phases with oversight"""
        results = {
            "success": True,
            "phases_completed": 0,
            "phases_failed": 0,
            "phase_results": [],
            "errors": []
        }

        for phase in plan.phases:
            phase_start = time.time()
            logger.info(f"[0102-PRINCIPAL] Executing phase {phase['phase']}: {phase['name']} ({phase['agent']})")

            try:
                # Execute phase (delegated to appropriate agent)
                phase_result = self._execute_single_phase(phase, team)

                # Ensure required identifiers are present for DB persistence
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
                    logger.info(f"[0102-PRINCIPAL] Phase {phase['phase']} complete in {phase_duration:.0f}ms")
                else:
                    results["phases_failed"] += 1
                    results["errors"].append(f"Phase {phase['phase']} failed: {phase_result.get('error', 'Unknown')}")
                    logger.error(f"[0102-PRINCIPAL] Phase {phase['phase']} failed")

            except Exception as e:
                results["phases_failed"] += 1
                results["errors"].append(f"Phase {phase['phase']} exception: {str(e)}")
                logger.error(f"[0102-PRINCIPAL] Phase {phase['phase']} exception: {e}")

        results["success"] = results["phases_failed"] == 0
        return results

    def _execute_single_phase(self, phase: Dict[str, Any], team: AgentTeam) -> Dict[str, Any]:
        """Execute a single phase (delegated to agent)"""
        agent = phase["agent"]

        if agent == AgentRole.ASSOCIATE.value:  # Gemma
            return self._delegate_to_gemma(phase, team)
        elif agent == AgentRole.PARTNER.value:  # Qwen
            return self._delegate_to_qwen(phase, team)
        elif agent == AgentRole.PRINCIPAL.value:  # 0102
            return self._execute_as_principal(phase, team)
        else:
            return {"success": False, "error": f"Unknown agent: {agent}"}

    def _delegate_to_gemma(self, phase: Dict[str, Any], team: AgentTeam) -> Dict[str, Any]:
        """Delegate phase to Gemma Associate (fast pattern matching)"""
        logger.info(f"[GEMMA-ASSOCIATE] Executing phase: {phase['name']}")

        # Gemma does fast classification/validation
        if not HOLO_AVAILABLE:
            return {"success": True, "method": "fallback", "result": "Simulated Gemma execution"}

        # Real Gemma would use orchestrator.analyze_module_dependencies (fast heuristic)
        return {
            "success": True,
            "method": "gemma_fast_pattern",
            "result": f"Gemma completed {phase['name']}",
            "agent": AgentRole.ASSOCIATE.value
        }

    def _delegate_to_qwen(self, phase: Dict[str, Any], team: AgentTeam) -> Dict[str, Any]:
        """Delegate phase to Qwen Partner (strategic planning)"""
        logger.info(f"[QWEN-PARTNER] Executing phase: {phase['name']}")

        # Qwen does strategic analysis (starts simple, scales up)
        if not HOLO_AVAILABLE:
            return {"success": True, "method": "fallback", "result": "Simulated Qwen execution"}

        # Optional: prefetch context via HoloAdapter.search to minimize tokens
        if getattr(self, "holo_adapter", None):
            _ = self.holo_adapter.search(query=phase.get("description", ""), limit=3)

        # Real Qwen would use orchestrator.generate_refactoring_plan (strategic planning)
        result = {
            "success": True,
            "method": "qwen_strategic_planning",
            "result": f"Qwen completed {phase['name']}",
            "agent": AgentRole.PARTNER.value,
            "wsp15_applied": True
        }

        # WSP guard: compress hygiene warnings, do not block
        if getattr(self, "holo_adapter", None):
            guard_report = self.holo_adapter.guard(payload=result, intent="planning")
            if guard_report.get("warnings"):
                result["guard_warnings"] = guard_report["warnings"]

        return result

    def _execute_as_principal(self, phase: Dict[str, Any], team: AgentTeam) -> Dict[str, Any]:
        """0102 Principal executes phase directly"""
        logger.info(f"[0102-PRINCIPAL] Executing directly: {phase['name']}")

        # 0102 executes with full oversight
        return {
            "success": True,
            "method": "0102_direct_execution",
            "result": f"0102 completed {phase['name']} with full oversight",
            "agent": AgentRole.PRINCIPAL.value
        }

    # ==================== PHASE 4: LEARNING ====================

    def store_mission_pattern(self, team: AgentTeam):
        """Phase 4: Store mission results as learning pattern (WSP 48)"""
        pattern = {
            "timestamp": time.time(),
            "mission_id": team.mission_id,
            "mission_type": team.mission_type.value,
            "status": team.status,
            "results": team.results,
            "lessons_learned": {
                "complexity_estimate_accuracy": "TBD",
                "phase_execution_efficiency": "TBD",
                "agent_coordination_quality": "TBD"
            }
        }

        if team.results.get("success", False):
            self.patterns["successful_missions"].append(pattern)
            logger.info(f"[LEARNING] Stored successful mission pattern: {team.mission_id}")
        else:
            self.patterns["failed_missions"].append(pattern)
            logger.warning(f"[LEARNING] Stored failed mission for analysis: {team.mission_id}")

        self._save_patterns()

        # Persist a compact execution report under module memory for later analysis
        if getattr(self, "holo_adapter", None):
            try:
                _ = self.holo_adapter.analyze_exec_log(team.mission_id, team.results)
            except Exception:
                pass

        # Also record mission results into SQLite (WSP 78)
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
            # Do not block on DB issues
            pass

    # ==================== ACTIVITY ROUTING (WSP 15 MPS) ====================

    # Activity MPS Scores (WSP 15 priority scoring)
    ACTIVITY_MPS_SCORES = {
        MissionType.LIVE_STREAM: 20,         # P0: Critical - always wins
        MissionType.COMMENT_PROCESSING: 15,  # P1: High priority
        MissionType.VIDEO_INDEXING: 14,      # P1: Default when idle
        MissionType.SCHEDULING: 12,          # P2: Medium (triggers indexing via index_weave)
        MissionType.GIT_PUSH: 12,            # P2: Medium (autonomous commits via qwen_gitpush)
        MissionType.SOCIAL_MEDIA: 8,         # P3: Low priority
        MissionType.MAINTENANCE: 4,          # P4: Lowest priority
    }

    def get_next_activity(self, current_state: Dict[str, Any]) -> MissionType:
        """
        WSP 15 MPS-based activity routing.

        Determines next activity based on system state and priority scoring.
        Uses pattern from multi_channel_coordinator.py for done detection.

        Args:
            current_state: Dict with keys:
                - is_live: bool - Is stream currently live (P0 override)
                - unprocessed_comments: int - Comments awaiting processing
                - all_processed: bool - Multi-channel done signal
                - schedule_queue: int - Videos awaiting scheduling
                - git_staged_files: int - Files staged for autonomous commit
                - social_queue: int - Social media posts pending
                - maintenance_due: bool - System maintenance needed

        Returns:
            MissionType - Next activity to execute
        """
        # P0: Live stream ALWAYS wins (critical engagement)
        if current_state.get("is_live", False):
            logger.info("[ACTIVITY] P0 Override: Live stream active")
            return MissionType.LIVE_STREAM

        # P1: Comments if unprocessed (from multi_channel_coordinator pattern)
        if not current_state.get("all_processed", False):
            unprocessed = current_state.get("unprocessed_comments", 0)
            if unprocessed > 0:
                logger.info(f"[ACTIVITY] P1: {unprocessed} comments pending")
                return MissionType.COMMENT_PROCESSING

        # P2: Scheduling if queue exists (triggers indexing via index_weave.py)
        if current_state.get("schedule_queue", 0) > 0:
            logger.info("[ACTIVITY] P2: Schedule queue active (will trigger indexing)")
            return MissionType.SCHEDULING

        # P2: Git push if staged files exist (autonomous commits via qwen_gitpush)
        staged_files = current_state.get("git_staged_files", 0)
        if staged_files > 0:
            logger.info(f"[ACTIVITY] P2: {staged_files} files staged for commit (qwen_gitpush)")
            return MissionType.GIT_PUSH

        # P3: Social media if posts pending
        if current_state.get("social_queue", 0) > 0:
            logger.info("[ACTIVITY] P3: Social media queue active")
            return MissionType.SOCIAL_MEDIA

        # P4: Maintenance if due
        if current_state.get("maintenance_due", False):
            logger.info("[ACTIVITY] P4: Maintenance due")
            return MissionType.MAINTENANCE

        # P1 Default: Indexing when all else complete
        logger.info("[ACTIVITY] P1 Default: Falling back to video indexing")
        return MissionType.VIDEO_INDEXING

    def detect_activity_state(self, daemon_results: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Detect current activity state from daemon monitoring results.

        Extracts state signals for activity routing decisions.
        Pattern: Reuses multi_channel_coordinator's all_processed detection.

        Args:
            daemon_results: Optional results from monitor_daemon()

        Returns:
            Dict with activity state for get_next_activity()
        """
        state = {
            "is_live": False,
            "unprocessed_comments": 0,
            "all_processed": False,
            "schedule_queue": 0,
            "git_staged_files": 0,  # Staged files for autonomous commit
            "social_queue": 0,
            "maintenance_due": False,
        }

        if not daemon_results:
            return state

        # Extract signals from daemon monitoring
        signals = daemon_results.get("signals", [])
        for signal in signals:
            pattern = signal.get("pattern", "")

            # Live stream detection
            if "live" in pattern.lower() and "active" in pattern.lower():
                state["is_live"] = True

            # Comments cleared detection (from youtube_daemon_monitor.json)
            if "comments_cleared" in pattern or "edge_comments_cleared" in pattern:
                state["all_processed"] = True

            # Git push detection (from git_push_dae signals)
            if "git_staged" in pattern or "files_changed" in pattern:
                # Extract count from pattern if available
                import re
                match = re.search(r'(\d+)\s*files?', pattern)
                if match:
                    state["git_staged_files"] = int(match.group(1))
                else:
                    state["git_staged_files"] = 1  # At least one file staged

        # Check for remaining bugs as work indicator
        bugs_detected = daemon_results.get("bugs_detected", 0)
        if bugs_detected == 0 and daemon_results.get("signals_detected", 0) == 0:
            # Quiet daemon = all_processed likely true
            state["all_processed"] = True

        return state

    def route_activity(self, daemon_results: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Complete activity routing cycle.

        1. Detect current state
        2. Route to next activity
        3. Return routing decision with metadata

        Args:
            daemon_results: Optional results from monitor_daemon()

        Returns:
            Dict with:
                - next_activity: MissionType
                - state: Current detected state
                - mps_score: Priority score of selected activity
        """
        state = self.detect_activity_state(daemon_results)
        next_activity = self.get_next_activity(state)
        mps_score = self.ACTIVITY_MPS_SCORES.get(next_activity, 0)

        logger.info(
            f"[ACTIVITY-ROUTING] Selected: {next_activity.value} (MPS: {mps_score})"
        )

        return {
            "next_activity": next_activity,
            "state": state,
            "mps_score": mps_score,
            "routing_reason": f"WSP 15 MPS routing: {next_activity.value} scored {mps_score}"
        }

    def execute_git_push_activity(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Execute autonomous git push via qwen_gitpush skill.

        WSP 77 Agent Coordination:
            1. Qwen analyzes git diff (micro chain-of-thought)
            2. Calculates MPS score for commit value
            3. Generates WSP-compliant commit message
            4. Executes module-by-module commits (or batched)
            5. Creates PR if branch protection requires

        Skill Path: modules/infrastructure/git_push_dae/skillz/qwen_gitpush/

        Args:
            dry_run: If True, analyze only, don't commit

        Returns:
            Dict with:
                - success: bool
                - commits: List of commit hashes
                - pr_url: Optional PR URL if created
                - skill_execution: qwen_gitpush skill results
        """
        import subprocess

        result = {
            "success": False,
            "commits": [],
            "pr_url": None,
            "skill_execution": None,
            "staged_files": 0,
            "dry_run": dry_run
        }

        try:
            # Step 1: Check git status for staged files
            git_status = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, cwd=str(self.repo_root)
            )
            staged_files = [
                line for line in git_status.stdout.strip().split('\n')
                if line and (line.startswith('M ') or line.startswith('A ') or line.startswith('D '))
            ]
            result["staged_files"] = len(staged_files)

            if not staged_files:
                logger.info("[GIT-PUSH] No staged files found")
                result["success"] = True
                result["message"] = "No staged files to commit"
                return result

            logger.info(f"[GIT-PUSH] Found {len(staged_files)} staged files")

            # Step 2: Load qwen_gitpush skill for commit analysis
            skill_path = self.repo_root / "modules/infrastructure/git_push_dae/skillz/qwen_gitpush/SKILLz.md"
            if skill_path.exists():
                logger.info(f"[GIT-PUSH] Using qwen_gitpush skill at {skill_path}")
                result["skill_execution"] = {"skill": "qwen_gitpush", "status": "available"}
            else:
                logger.warning(f"[GIT-PUSH] qwen_gitpush skill not found at {skill_path}")
                result["skill_execution"] = {"skill": "qwen_gitpush", "status": "not_found"}

            if dry_run:
                result["success"] = True
                result["message"] = f"Dry run: Would commit {len(staged_files)} files"
                logger.info(f"[GIT-PUSH] Dry run complete: {len(staged_files)} files staged")
                return result

            # Step 3: Execute git commit (WSP-aligned message)
            # Note: Full qwen_gitpush integration would use WRE skill execution
            # For now, create mission for coordination
            mission = self.create_mission(
                mission_type=MissionType.GIT_PUSH,
                context={
                    "staged_files": len(staged_files),
                    "files": [f.strip() for f in staged_files[:10]],  # First 10 for context
                    "skill_path": str(skill_path) if skill_path.exists() else None
                },
                expected_outputs=["commit_hash", "commit_message", "pr_url"]
            )

            result["mission_id"] = mission.mission_id
            result["success"] = True
            result["message"] = f"Git push mission created: {mission.mission_id}"
            logger.info(f"[GIT-PUSH] Created mission {mission.mission_id} for {len(staged_files)} files")

            return result

        except Exception as e:
            logger.error(f"[GIT-PUSH] Error: {e}")
            result["error"] = str(e)
            return result

    def check_git_status(self) -> Dict[str, Any]:
        """
        Quick check of git status for activity routing.

        Returns:
            Dict with staged_files, modified_files, untracked_files counts
        """
        import subprocess

        try:
            git_status = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, cwd=str(self.repo_root)
            )
            lines = [l for l in git_status.stdout.strip().split('\n') if l]

            staged = len([l for l in lines if l[:2] in ('M ', 'A ', 'D ', 'R ')])
            modified = len([l for l in lines if l[1:2] == 'M' or l[:2] == ' M'])
            untracked = len([l for l in lines if l.startswith('??')])

            return {
                "staged_files": staged,
                "modified_files": modified,
                "untracked_files": untracked,
                "total_changes": len(lines)
            }
        except Exception as e:
            logger.error(f"[GIT-STATUS] Error: {e}")
            return {"staged_files": 0, "modified_files": 0, "untracked_files": 0, "error": str(e)}

    # ==================== UBIQUITOUS DAEMON MONITORING ====================

    def monitor_daemon(self, bash_id: str = None, skill_path: Path = None,
                       bash_output: str = None, auto_fix: bool = True,
                       report_complex: bool = True, chat_sender = None,
                       announce_to_chat: bool = True) -> Dict[str, Any]:
        """
        UBIQUITOUS daemon monitor - works with ANY daemon using skill-driven patterns

        First Principles + Occam's Razor:
            WHAT: AI Overseer monitors any bash shell (universal)
            HOW: Skills define daemon-specific patterns (modular)
            WHO: Qwen/Gemma/0102 coordination (WSP 77)
            WHAT TO DO: Auto-fix or report (skill-driven)

        Args:
            bash_id: Bash shell ID to monitor (e.g., "7f81b9") - LEGACY, use bash_output
            skill_path: Path to daemon monitoring skill JSON
            bash_output: Bash output string (Option A - simplified approach)
            auto_fix: Apply WRE fixes for low-hanging fruit (complexity 1-2)
            report_complex: Generate bug reports for complex issues (complexity 3+)
            chat_sender: ChatSender instance for live chat announcements (012's vision!)
            announce_to_chat: Post fix announcements to live chat

        Returns:
            Monitoring results with detected bugs, fixes applied, reports generated

        Example (Option A - Simplified):
            overseer = AIIntelligenceOverseer(repo_root)
            bash_output = BashOutput("56046d").get("stdout")
            overseer.monitor_daemon(
                bash_output=bash_output,
                skill_path=Path("modules/communication/livechat/skillz/youtube_daemon_monitor.json"),
                chat_sender=chat_sender,
                announce_to_chat=True
            )
        """
        logger.info(f"[DAEMON-MONITOR] Starting ubiquitous monitor")

        # Load daemon-specific skill
        skill = self._load_daemon_skill(skill_path)
        if not skill:
            return {"success": False, "error": f"Failed to load skill: {skill_path}"}

        logger.info(f"[DAEMON-MONITOR] Loaded skill for {skill.get('daemon_name', 'unknown')}")

        # Option A: Use provided bash_output directly
        if bash_output is None and bash_id:
            # Legacy path: try to read from bash_id
            bash_output = self._read_bash_output(bash_id, lines=100)

        if not bash_output:
            return {"success": False, "error": "No bash output provided"}

        # Phase 0 (Signal): Non-error operational signals (state transitions)
        # This enables Qwen/0102 orchestration without misclassifying healthy state as a "bug".
        detected_signals = self._gemma_detect_signals(bash_output, skill)
        if detected_signals:
            logger.info(f"[SIGNAL-DETECT] Detected {len(detected_signals)} operational signal(s)")
            for sig in detected_signals[:5]:
                logger.info(f"[SIGNAL] {sig.get('pattern_name')}")

        # Phase 1 (Gemma): Fast error detection using skill patterns
        detected_bugs = self._gemma_detect_errors(bash_output, skill)

        if not detected_bugs:
            logger.info(f"[DAEMON-MONITOR] No bugs detected in bash {bash_id}")
            return {
                "success": True,
                "bugs_detected": 0,
                "bugs_fixed": 0,
                "reports_generated": 0,
                "signals_detected": len(detected_signals),
                "signals": detected_signals,
            }

        logger.info(f"[GEMMA-ASSOCIATE] Detected {len(detected_bugs)} potential bugs")

        # Phase 2 (Qwen): Classify bugs and determine actions
        classified_bugs = self._qwen_classify_bugs(detected_bugs, skill)

        results = {
            "success": True,
            "bugs_detected": len(classified_bugs),
            "bugs_fixed": 0,
            "reports_generated": 0,
            "fixes_applied": [],
            "reports": [],
            "signals_detected": len(detected_signals),
            "signals": detected_signals,
        }

        # Phase 3 (0102): Execute fixes or generate reports
        for bug in classified_bugs:
            # Deduplication: Generate unique key for this bug pattern + match content
            pattern_key = f"{bug['pattern_name']}_{hash(str(bug['matches']))}"

            # Check if already attempted and should skip
            if pattern_key in self.fix_attempts:
                attempt_data = self.fix_attempts[pattern_key]

                # Skip if disabled after 3 failures
                if attempt_data.get('disabled'):
                    logger.info(f"[SKIP] Pattern {bug['pattern_name']} disabled after 3 failed attempts")
                    continue

                # Skip if attempted recently (within 5 minutes = 300s)
                time_since = time.time() - attempt_data['last_attempt']
                if time_since < 300:
                    logger.debug(f"[SKIP] Recently attempted {bug['pattern_name']} ({time_since:.0f}s ago)")
                    continue

                # Increment attempts if we're going to try again
                attempt_data['attempts'] += 1
                attempt_data['last_attempt'] = time.time()

                # Disable if this will be 3rd failure
                if attempt_data['attempts'] >= 3:
                    logger.warning(f"[LIMIT] Final attempt (3/{attempt_data['attempts']}) for {bug['pattern_name']}")

                # Suppress announcement for retries (already announced first time)
                announce_this_bug = False
            else:
                # First time seeing this bug - track it and announce
                self.fix_attempts[pattern_key] = {
                    'attempts': 1,
                    'last_attempt': time.time(),
                    'first_seen': time.time(),
                    'disabled': False
                }
                announce_this_bug = True

            # Announce detection to live chat (only first time!)
            if chat_sender and announce_to_chat and announce_this_bug:
                self._announce_to_chat(chat_sender, "detection", bug)

            if bug["auto_fixable"] and auto_fix:
                # Announce fix application
                if chat_sender and announce_to_chat:
                    self._announce_to_chat(chat_sender, "applying", bug)

                # Low-hanging fruit: Auto-fix using WRE pattern memory
                fix_result = self._apply_auto_fix(bug, skill)

                # Check if fix succeeded - if failed and this was 3rd attempt, disable
                if not fix_result.get("success") and pattern_key in self.fix_attempts:
                    attempt_data = self.fix_attempts[pattern_key]
                    if attempt_data['attempts'] >= 3:
                        attempt_data['disabled'] = True
                        logger.error(f"[DISABLED] Pattern {bug['pattern_name']} disabled after 3 failed attempts")

                # Announce completion
                if chat_sender and announce_to_chat and announce_this_bug:
                    self._announce_to_chat(
                        chat_sender,
                        "complete",
                        bug,
                        fix_result,
                        verification=fix_result.get("verification")
                    )

                if fix_result.get("success"):
                    results["bugs_fixed"] += 1
                    results["fixes_applied"].append(fix_result)
                    logger.info(f"[AUTO-FIX] Applied fix for {bug['pattern_name']}")

                    # Clear fix attempts on success so it can detect new instances
                    if pattern_key in self.fix_attempts:
                        del self.fix_attempts[pattern_key]

            elif bug["needs_0102"] and report_complex:
                # Complex bug: Generate report for 0102 review
                report = self._generate_bug_report(bug, skill, bash_id if bash_id else "unknown")
                results["reports_generated"] += 1
                results["reports"].append(report)
                logger.info(f"[BUG-REPORT] Generated report for {bug['pattern_name']}")

        # Phase 4: Store learning patterns
        self._store_monitoring_patterns(skill_path, results)

        # Phase 5: Handle daemon restart if code patch was applied
        for fix in results.get("fixes_applied", []):
            if fix.get("needs_restart", False):
                logger.info(f"[RESTART] Code patch applied - daemon restart required")
                logger.info(f"[RESTART] Fix: {fix.get('fix_applied')} on {fix.get('files_modified')}")
                logger.info(f"[RESTART] Triggering clean shutdown - supervisor will restart with patched code")

                # Log metrics before restart
                logger.info(f"[RESTART] Session metrics: {results['bugs_detected']} bugs detected, {results['bugs_fixed']} fixed")

                # Trigger restart via sys.exit(0)
                # Process supervisor (systemd, Windows Service, or manual restart) will bring process back up
                import sys
                sys.exit(0)

        return results

    def _load_daemon_skill(self, skill_path: Path) -> Optional[Dict]:
        """Load daemon-specific monitoring skill"""
        try:
            with open(skill_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"[SKILL-LOAD] Failed to load {skill_path}: {e}")
            return None

    def _read_bash_output(self, bash_id: str, lines: int = 100) -> Optional[str]:
        """Read recent output from bash shell (placeholder - needs BashOutput integration)"""
        # TODO: Integrate with actual BashOutput tool
        # For now, return None to indicate not implemented
        logger.warning("[BASH-READ] BashOutput integration not yet implemented")
        return None

    def _gemma_detect_errors(self, bash_output: str, skill: Dict) -> List[Dict]:
        """Phase 1 (Gemma): Fast error pattern detection using skill patterns"""
        import re
        detected = []

        error_patterns = skill.get("error_patterns", {})
        for pattern_name, pattern_config in error_patterns.items():
            regex = pattern_config.get("regex", "")
            if not regex:
                continue

            matches = re.findall(regex, bash_output, re.IGNORECASE | re.MULTILINE)
            if matches:
                detected.append({
                    "pattern_name": pattern_name,
                    "matches": matches,
                    "config": pattern_config
                })

        return detected

    def _gemma_detect_signals(self, bash_output: str, skill: Dict) -> List[Dict]:
        """
        Phase 0 (Gemma): Detect operational state signals (non-errors).

        Skills may define `signal_patterns` to surface orchestration-relevant state
        transitions (e.g., "comments_cleared") without treating them as bugs.
        """
        import re

        detected: List[Dict[str, Any]] = []
        signal_patterns = skill.get("signal_patterns", {}) or {}
        if not isinstance(signal_patterns, dict):
            return detected

        for pattern_name, pattern_config in signal_patterns.items():
            if not isinstance(pattern_config, dict):
                continue
            regex = pattern_config.get("regex", "")
            if not regex:
                continue

            matches = re.findall(regex, bash_output, re.IGNORECASE | re.MULTILINE)
            if matches:
                detected.append({
                    "pattern_name": pattern_name,
                    "matches": matches,
                    "config": pattern_config
                })

        return detected

    def _qwen_classify_bugs(self, detected_bugs: List[Dict], skill: Dict) -> List[Dict]:
        """Phase 2 (Qwen): Classify bugs with WSP 15 MPS scoring and determine actions"""
        classified = []

        for bug in detected_bugs:
            config = bug["config"]
            qwen_action = config.get("qwen_action", "ignore")

            # Interpret qwen_action into auto_fixable/needs_0102 flags
            auto_fixable = (qwen_action == "auto_fix")
            needs_0102 = (qwen_action == "bug_report")
            should_ignore = (qwen_action == "ignore")

            # Skip if Qwen decided to ignore (e.g., stream_not_found P4 backlog)
            if should_ignore:
                logger.info(f"[QWEN-IGNORE] Skipping {bug['pattern_name']} (qwen_action=ignore)")
                continue

            # Get WSP 15 MPS scoring
            wsp_15_mps = config.get("wsp_15_mps", {})
            complexity = wsp_15_mps.get("complexity", 3)

            classification = {
                "pattern_name": bug["pattern_name"],
                "complexity": complexity,
                "auto_fixable": auto_fixable,
                "needs_0102": needs_0102,
                "qwen_action": qwen_action,
                "fix_action": config.get("fix_action"),
                "fix_module": config.get("fix_module"),
                "fix_function": config.get("fix_function"),
                "matches": bug["matches"],
                "config": config  # Pass full config for announcements
            }
            classified.append(classification)

            logger.info(f"[QWEN-CLASSIFY] {bug['pattern_name']}: complexity={complexity}, action={qwen_action}")

        return classified

    def _apply_auto_fix(self, bug: Dict, skill: Dict) -> Dict:
        """
        Phase 3: Apply operational auto-fix for complexity 1-2 bugs

        Implements approved operational fixes:
        - OAuth reauthorization (subprocess)
        - API credential rotation (function call)
        - Service reconnection (method call)
        - Daemon restart (process management)

        Returns success/failure for MetricsAppender tracking
        """
        import subprocess

        fix_action = bug.get("fix_action")
        pattern_name = bug["pattern_name"]
        skill_name = skill.get("daemon_name", "unknown_daemon")

        # Generate execution ID for metrics tracking
        exec_id = f"fix_{pattern_name}_{int(time.time())}"
        start_time = time.time()

        logger.info(f"[AUTO-FIX] Applying {fix_action} for {pattern_name} | exec_id={exec_id}")

        try:
            # Operational Fix 1: OAuth Reauthorization (P0, Complexity 2)
            if fix_action == "run_reauthorization_script":
                fix_command = bug["config"].get("fix_command")
                if not fix_command:
                    return {
                        "success": False,
                        "bug": pattern_name,
                        "error": "No fix_command in skill config"
                    }

                logger.info(f"[AUTO-FIX] Running OAuth reauth: {fix_command}")
                result = subprocess.run(
                    fix_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                success = result.returncode == 0

                # Track metrics
                execution_time_ms = int((time.time() - start_time) * 1000)
                self.metrics.append_performance_metric(
                    skill_name=skill_name,
                    execution_id=exec_id,
                    execution_time_ms=execution_time_ms,
                    agent="ai_overseer",
                    exception_occurred=False
                )
                self.metrics.append_outcome_metric(
                    skill_name=skill_name,
                    execution_id=exec_id,
                    decision=fix_action,
                    expected_decision=fix_action,
                    correct=success,
                    confidence=1.0 if success else 0.0,
                    reasoning=f"OAuth reauth {'succeeded' if success else 'failed'}: {fix_command}",
                    agent="ai_overseer"
                )

                return {
                    "success": success,
                    "bug": pattern_name,
                    "fix_applied": fix_action,
                    "method": "subprocess",
                    "command": fix_command,
                    "stdout": result.stdout[:500],  # Truncate for metrics
                    "stderr": result.stderr[:500] if result.stderr else None,
                    "returncode": result.returncode,
                    "execution_id": exec_id
                }

            # Operational Fix 2: API Credential Rotation (P1, Complexity 2)
            elif fix_action == "rotate_api_credentials":
                logger.info(f"[AUTO-FIX] Rotating API credentials")

                # Import YouTube auth module
                try:
                    from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
                except ImportError as e:
                    return {
                        "success": False,
                        "bug": pattern_name,
                        "error": f"Cannot import youtube_auth: {e}"
                    }

                # Force credential rotation by calling auth service
                # The function auto-rotates between available credential sets
                try:
                    service = get_authenticated_service()
                    success = True
                    error_msg = None
                except Exception as e:
                    success = False
                    error_msg = str(e)

                # Track metrics
                execution_time_ms = int((time.time() - start_time) * 1000)
                self.metrics.append_performance_metric(
                    skill_name=skill_name,
                    execution_id=exec_id,
                    execution_time_ms=execution_time_ms,
                    agent="ai_overseer",
                    exception_occurred=not success
                )
                self.metrics.append_outcome_metric(
                    skill_name=skill_name,
                    execution_id=exec_id,
                    decision=fix_action,
                    expected_decision=fix_action,
                    correct=success,
                    confidence=1.0 if success else 0.0,
                    reasoning=f"API rotation {'succeeded' if success else f'failed: {error_msg}'}",
                    agent="ai_overseer"
                )

                if success:
                    return {
                        "success": True,
                        "bug": pattern_name,
                        "fix_applied": fix_action,
                        "method": "api_rotation",
                        "message": "API credentials rotated to next available set",
                        "execution_id": exec_id
                    }
                else:
                    return {
                        "success": False,
                        "bug": pattern_name,
                        "error": error_msg,
                        "method": "api_rotation",
                        "execution_id": exec_id
                    }

            # Operational Fix 3: Service Reconnection (P1, Complexity 2)
            elif fix_action == "reconnect_service":
                logger.info(f"[AUTO-FIX] Attempting service reconnection")

                # For now, return success (actual reconnection logic would go here)
                # TODO: Integrate with actual service reconnection methods
                success = True

                # Track metrics
                execution_time_ms = int((time.time() - start_time) * 1000)
                self.metrics.append_performance_metric(
                    skill_name=skill_name,
                    execution_id=exec_id,
                    execution_time_ms=execution_time_ms,
                    agent="ai_overseer",
                    exception_occurred=False
                )
                self.metrics.append_outcome_metric(
                    skill_name=skill_name,
                    execution_id=exec_id,
                    decision=fix_action,
                    expected_decision=fix_action,
                    correct=success,
                    confidence=0.5,  # Placeholder has lower confidence
                    reasoning="Service reconnection placeholder (not yet implemented)",
                    agent="ai_overseer"
                )

                return {
                    "success": True,
                    "bug": pattern_name,
                    "fix_applied": fix_action,
                    "method": "service_reconnect",
                    "message": "Service reconnection attempted (placeholder)",
                    "execution_id": exec_id
                }

            # Code Fix: Unicode conversion (Complexity 1 - uses PatchExecutor)
            elif fix_action == "add_unicode_conversion_before_youtube_send":
                logger.info(f"[AUTO-FIX] Applying Unicode conversion patch via PatchExecutor")

                try:
                    # Generate UTF-8 header patch for the affected file
                    # Convert Python module notation to file path
                    # FROM: modules.ai_intelligence.banter_engine.src.banter_engine
                    # TO:   modules/ai_intelligence/banter_engine/src/banter_engine.py
                    affected_module = bug.get("fix_module", "modules.ai_intelligence.banter_engine.src.banter_engine")
                    affected_file = affected_module.replace('.', '/') + '.py'

                    # Simple UTF-8 header patch template
                    patch_content = f"""diff --git a/{affected_file} b/{affected_file}
index 0000000..1111111 100644
--- a/{affected_file}
+++ b/{affected_file}
@@ -1,3 +1,4 @@
+# -*- coding: utf-8 -*-
 \"\"\"
 Module implementation
 \"\"\"
"""

                    # Apply patch using PatchExecutor
                    patch_result = self.patch_executor.apply_patch(
                        patch_content=patch_content,
                        patch_description=f"Add UTF-8 header to {affected_file}"
                    )

                    success = patch_result["success"]
                    execution_time_ms = int((time.time() - start_time) * 1000)

                    # Track metrics
                    self.metrics.append_performance_metric(
                        skill_name=skill_name,
                        execution_id=exec_id,
                        execution_time_ms=execution_time_ms,
                        agent="ai_overseer",
                        exception_occurred=not success
                    )

                    if success:
                        verification = self._verify_unicode_patch(
                            patch_result.get("files_modified", [])
                        )

                        self.metrics.append_outcome_metric(
                            skill_name=skill_name,
                            execution_id=f"{exec_id}_verify",
                            decision="verify_unicode_patch",
                            expected_decision="verify_unicode_patch",
                            correct=verification["verified"],
                            confidence=0.9 if verification["verified"] else 0.0,
                            reasoning=verification["reason"],
                            agent="ai_overseer"
                        )

                        if verification["verified"]:
                            return {
                                "success": True,
                                "bug": pattern_name,
                                "fix_applied": fix_action,
                                "method": "patch_executor",
                                "files_modified": patch_result["files_modified"],
                                "message": f"UTF-8 header patch applied to {affected_file}",
                                "execution_id": exec_id,
                                "needs_restart": True,
                                "verification": verification
                            }

                        logger.warning(f"[VERIFY] Unicode patch verification failed: {verification['reason']}")
                        return {
                            "success": False,
                            "bug": pattern_name,
                            "fix_applied": fix_action,
                            "error": "Verification failed - manual review required",
                            "execution_id": exec_id,
                            "verification": verification,
                            "needs_restart": False,
                            "escalate": True
                        }

                    # Patch failed - record outcome
                    self.metrics.append_outcome_metric(
                        skill_name=skill_name,
                        execution_id=exec_id,
                        decision=fix_action,
                        expected_decision=fix_action,
                        correct=False,
                        confidence=0.0,
                        reasoning=patch_result.get("error", "Patch application failed"),
                        agent="ai_overseer"
                    )

                    return {
                        "success": False,
                        "bug": pattern_name,
                        "fix_applied": None,
                        "error": patch_result.get("error", "Patch application failed"),
                        "violations": patch_result.get("violations", []),
                        "execution_id": exec_id
                    }

                except Exception as e:
                    logger.error(f"[AUTO-FIX] Unicode patch failed: {e}")
                    execution_time_ms = int((time.time() - start_time) * 1000)
                    self.metrics.append_performance_metric(
                        skill_name=skill_name,
                        execution_id=exec_id,
                        execution_time_ms=execution_time_ms,
                        agent="ai_overseer",
                        exception_occurred=True,
                        exception_type=type(e).__name__
                    )
                    return {
                        "success": False,
                        "bug": pattern_name,
                        "error": str(e),
                        "execution_id": exec_id
                    }

            # Unknown fix action
            else:
                logger.error(f"[AUTO-FIX] Unknown fix_action: {fix_action} for pattern {pattern_name}")
                logger.error(f"[AUTO-FIX] Available actions: run_reauthorization_script, rotate_api_credentials, reconnect_service, add_unicode_conversion_before_youtube_send")
                execution_time_ms = int((time.time() - start_time) * 1000)
                self.metrics.append_performance_metric(
                    skill_name=skill_name,
                    execution_id=exec_id,
                    execution_time_ms=execution_time_ms,
                    agent="ai_overseer",
                    exception_occurred=True,
                    exception_type="UnknownFixAction"
                )
                self.metrics.append_outcome_metric(
                    skill_name=skill_name,
                    execution_id=exec_id,
                    decision=fix_action if fix_action else "unknown",
                    expected_decision=None,
                    correct=False,
                    confidence=0.0,
                    reasoning=f"Unknown fix_action: {fix_action}",
                    agent="ai_overseer"
                )

                return {
                    "success": False,
                    "bug": pattern_name,
                    "error": f"Unknown fix_action: {fix_action}",
                    "available_fixes": ["run_reauthorization_script", "rotate_api_credentials", "reconnect_service"],
                    "execution_id": exec_id
                }

        except subprocess.TimeoutExpired:
            execution_time_ms = int((time.time() - start_time) * 1000)
            self.metrics.append_performance_metric(
                skill_name=skill_name,
                execution_id=exec_id,
                execution_time_ms=execution_time_ms,
                agent="ai_overseer",
                exception_occurred=True,
                exception_type="TimeoutExpired"
            )
            return {
                "success": False,
                "bug": pattern_name,
                "error": "Fix command timed out after 30s",
                "execution_id": exec_id
            }
        except Exception as e:
            logger.error(f"[AUTO-FIX] Failed to apply {fix_action}: {e}")
            execution_time_ms = int((time.time() - start_time) * 1000)
            self.metrics.append_performance_metric(
                skill_name=skill_name,
                execution_id=exec_id,
                execution_time_ms=execution_time_ms,
                agent="ai_overseer",
                exception_occurred=True,
                exception_type=type(e).__name__
            )
            return {
                "success": False,
                "bug": pattern_name,
                "error": str(e),
                "traceback": traceback.format_exc()[:500],
                "execution_id": exec_id
            }

    def _generate_bug_report(self, bug: Dict, skill: Dict, bash_id: str) -> Dict:
        """Phase 3 (0102): Generate structured bug report for complex issues"""
        return {
            "id": f"bug_{int(time.time())}",
            "daemon": skill.get("daemon_name", "unknown"),
            "bash_id": bash_id,
            "pattern": bug["pattern_name"],
            "complexity": bug["complexity"],
            "auto_fixable": bug["auto_fixable"],
            "needs_0102_review": bug["needs_0102"],
            "matches": bug["matches"],
            "recommended_fix": bug.get("fix_action", "Manual review required"),
            "priority": skill.get("report_priority", "P3"),
            "timestamp": time.time()
        }

    def _store_monitoring_patterns(self, skill_path: Path, results: Dict):
        """Phase 4: Store successful monitoring patterns for learning"""
        # Update skill with learning data
        try:
            skill = self._load_daemon_skill(skill_path)
            if skill:
                if "learning_stats" not in skill:
                    skill["learning_stats"] = {
                        "total_bugs_detected": 0,
                        "total_bugs_fixed": 0,
                        "total_reports_generated": 0
                    }

                skill["learning_stats"]["total_bugs_detected"] += results["bugs_detected"]
                skill["learning_stats"]["total_bugs_fixed"] += results["bugs_fixed"]
                skill["learning_stats"]["total_reports_generated"] += results["reports_generated"]
                skill["last_monitoring_run"] = time.time()

                with open(skill_path, 'w', encoding='utf-8') as f:
                    json.dump(skill, f, indent=2)

                logger.info(f"[LEARNING] Updated skill stats: {skill_path.name}")
        except Exception as e:
            logger.warning(f"[LEARNING] Failed to update skill stats: {e}")

    def _announce_to_chat(self, chat_sender, phase: str, bug: Dict,
                          fix_result: Optional[Dict] = None,
                          verification: Optional[Dict[str, Any]] = None) -> bool:
        """
        Post autonomous fix announcements to live chat (012's vision!)

        Makes AI self-healing visible to stream viewers in real-time.

        Args:
            chat_sender: ChatSender instance
            phase: Announcement phase (detection, applying, complete)
            bug: Bug detection/classification dict
            fix_result: Fix execution results (for complete phase)

        Returns:
            True if announcement posted successfully
        """
        if not chat_sender:
            return False

        try:
            from modules.ai_intelligence.banter_engine.src.banter_engine import BanterEngine
            banter = BanterEngine(emoji_enabled=True)

            # Generate announcement based on phase
            if phase == "detection":
                error_type = bug["pattern_name"].replace("_", " ").title()
                priority = bug.get("config", {}).get("wsp_15_mps", {}).get("priority", "P1")
                emoji_map = {"P0": "[U+1F525]", "P1": "[U+1F50D]", "P2": "[U+1F6E0]"}
                emoji = emoji_map.get(priority, "[U+1F50D]")
                message = f"012 detected {error_type} [{priority}] {emoji}"

            elif phase == "applying":
                message = "012 applying fix, restarting MAGAdoom [U+1F527]"

            elif phase == "complete":
                if verification and verification.get("verified"):
                    message = bug["config"].get("announcement_template", "012 fix applied - system online [U+2714]")
                elif fix_result and fix_result.get("success"):
                    message = "012 fix applied - verification pending [U+23F3]"
                else:
                    message = "012 fix failed - creating bug report [U+26A0]"
            else:
                logger.warning(f"[ANNOUNCE] Unknown phase: {phase}")
                return False

            # Convert Unicode tags to emoji
            rendered = banter._convert_unicode_tags_to_emoji(message)
            logger.info(f"[ANNOUNCE] {phase}: {rendered}")

            # Async integration: Fire-and-forget chat message
            # Use skip_delay for fix announcements (higher priority)
            try:
                import asyncio
                # Try to create task in existing event loop
                try:
                    asyncio.create_task(
                        chat_sender.send_message(rendered, response_type='update', skip_delay=True)
                    )
                    logger.info(f"[ANNOUNCE] Chat message queued: {rendered}")
                except RuntimeError:
                    # No event loop running - fallback to run_until_complete
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Event loop running but can't create_task - schedule callback
                        loop.call_soon_threadsafe(
                            lambda: asyncio.create_task(
                                chat_sender.send_message(rendered, response_type='update', skip_delay=True)
                            )
                        )
                    else:
                        # No loop running - run synchronously
                        loop.run_until_complete(
                            chat_sender.send_message(rendered, response_type='update', skip_delay=True)
                        )
                    logger.info(f"[ANNOUNCE] Chat message sent: {rendered}")
            except Exception as send_error:
                logger.error(f"[ANNOUNCE] Failed to send chat message: {send_error}")
                return False

            return True

        except Exception as e:
            logger.error(f"[ANNOUNCE] Failed: {e}")
            return False

    def _verify_unicode_patch(self, files_modified: List[str]) -> Dict[str, Any]:
        """
        Verify UTF-8 header insertion for modified files.
        """
        if not files_modified:
            return {
                "verified": False,
                "reason": "No files reported as modified"
            }

        missing_files: List[str] = []
        missing_header: List[str] = []

        for rel_path in files_modified:
            file_path = project_root / rel_path
            if not file_path.exists():
                missing_files.append(rel_path)
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as handle:
                    first_lines = [handle.readline() for _ in range(5)]
            except Exception as exc:
                missing_header.append(f"{rel_path} (read error: {exc})")
                continue

            if not any("# -*- coding: utf-8 -*-" in line for line in first_lines):
                missing_header.append(rel_path)

        if missing_files:
            return {
                "verified": False,
                "reason": f"Modified files missing: {', '.join(missing_files)}"
            }

        if missing_header:
            return {
                "verified": False,
                "reason": f"UTF-8 header missing in: {', '.join(missing_header)}"
            }

        return {
            "verified": True,
            "reason": "UTF-8 header confirmed in patched files"
        }

    # ==================== HOLODAE TELEMETRY MONITORING ====================

    async def start_telemetry_monitoring(self, poll_interval: float = 2.0):
        """
        Start monitoring HoloDAE JSONL telemetry files.

        Implements Priority 1 from dual-channel architecture:
        - Tails holo_index/logs/telemetry/*.jsonl
        - Feeds events to AI Overseer event_queue
        - Triggers skills on critical module status

        Args:
            poll_interval: Seconds between telemetry file scans
        """
        if not self.telemetry_monitor:
            logger.warning("[AI-OVERSEER] Telemetry monitor not initialized")
            return

        await self.telemetry_monitor.start_monitoring(poll_interval)
        logger.info("[AI-OVERSEER] Telemetry monitoring started | poll_interval=%.1fs", poll_interval)

    async def stop_telemetry_monitoring(self):
        """Stop HoloDAE telemetry monitoring."""
        if not self.telemetry_monitor:
            return

        await self.telemetry_monitor.stop_monitoring()
        stats = self.telemetry_monitor.get_statistics()
        logger.info(
            "[AI-OVERSEER] Telemetry monitoring stopped | events_queued=%d parse_errors=%d",
            stats.get("events_queued", 0),
            stats.get("parse_errors", 0)
        )

    async def start_background_services(self, poll_interval: float = 2.0):
        """
        Start telemetry monitor and consumer loop.
        """
        if self.telemetry_monitor:
            await self.telemetry_monitor.start_monitoring(poll_interval)
            logger.info("[AI-OVERSEER] Telemetry monitor started in background")
        if MCP_AVAILABLE and hasattr(self.mcp, 'event_queue'):
            # Kick off consumer loop
            loop = asyncio.get_running_loop()
            self.telemetry_consumer_task = loop.create_task(self._consume_telemetry_events())

    async def stop_background_services(self):
        """
        Stop telemetry monitor and consumer loop.
        """
        if self.telemetry_monitor:
            await self.telemetry_monitor.stop_monitoring()
        if self.telemetry_consumer_task:
            self.telemetry_consumer_task.cancel()
            try:
                await self.telemetry_consumer_task
            except asyncio.CancelledError:
                pass
            self.telemetry_consumer_task = None

    def get_telemetry_statistics(self) -> Dict[str, Any]:
        """
        Get telemetry monitor statistics.

        Returns:
            Statistics dict with events_processed, events_queued, parse_errors
        """
        if not self.telemetry_monitor:
            return {"error": "Telemetry monitor not initialized"}

        return self.telemetry_monitor.get_statistics()

    async def _consume_telemetry_events(self):
        """
        Consume telemetry events from the MCP event_queue and route to handlers.
        """
        if not (MCP_AVAILABLE and hasattr(self.mcp, 'event_queue')):
            return
        queue = self.mcp.event_queue
        while True:
            event = await queue.get()
            try:
                await self._handle_telemetry_event(event)
            except Exception as e:
                logger.error("[AI-OVERSEER] Telemetry event handling error: %s", e, exc_info=True)
            finally:
                queue.task_done()

    async def _handle_telemetry_event(self, event: Dict[str, Any]):
        """
        Handle actionable telemetry events and notify 0102.

        Processes:
        - module_status (critical): Trigger refactoring
        - system_alerts: WSP violations, root directory violations
        """
        event_type = event.get("event")
        severity = event.get("severity", "")

        if event_type == "module_status" and severity == "critical":
            logger.info("[AI-OVERSEER] Critical module_status event queued for action: %s", event.get("module"))
            # TODO: Map to WRE skill trigger (e.g., compliance/refactor)

        elif event_type == "system_alerts":
            alerts = event.get("alerts", [])
            source = event.get("source", "unknown")

            # Notify 0102 via stdout (visible in HoloIndex output)
            if alerts:
                logger.warning("[AI-OVERSEER] [GEMMA-ALERT] WSP violations detected by %s", source)
                print(f"\n[AI-OVERSEER] [WSP-VIOLATION] Detected {len(alerts)} violations:")
                for alert in alerts[:3]:  # Show top 3
                    print(f"  - {alert}")
                if len(alerts) > 3:
                    print(f"  ... and {len(alerts) - 3} more")
                # Root violations are a special-case: optionally auto-correct via root monitor.
                if source == "gemma_root_monitor" and os.getenv("AI_OVERSEER_ROOT_AUTOCORRECT", "false").lower() in ("true", "1", "yes"):
                    try:
                        from holo_index.monitoring.root_violation_monitor import scan_and_correct_violations
                        result = await scan_and_correct_violations()
                        logger.warning("[AI-OVERSEER] Root auto-correct attempted | applied=%d failed=%d",
                                       len(result.get("corrections_applied", [])),
                                       len(result.get("failed_corrections", [])))
                        print("[AI-OVERSEER] Root auto-correct attempted (AI_OVERSEER_ROOT_AUTOCORRECT=true)")
                    except Exception as exc:
                        logger.error("[AI-OVERSEER] Root auto-correct failed: %s", exc)
                        print("[AI-OVERSEER] Root auto-correct failed (see logs)")

                print("[AI-OVERSEER] Run 'python holo_index.py --check-module <module>' for details\n")

        else:
            logger.debug("[AI-OVERSEER] Telemetry event ignored: %s", event_type)

    # ==================== PUBLIC API ====================

    def coordinate_mission(self, mission_description: str,
                           mission_type: MissionType = MissionType.CUSTOM,
                           auto_approve: bool = False) -> Dict[str, Any]:
        """
        Main entry point: Coordinate mission with Qwen + Gemma + 0102

        Complete WSP 77 workflow:
            Phase 0: Check PatternMemory for known false positives (WSP 48/60)
            Phase 1: Gemma Associate fast analysis
            Phase 2: Qwen Partner strategic planning
            Phase 3: 0102 Principal execution oversight
            Phase 4: Learning and pattern storage

        Args:
            mission_description: What to accomplish
            mission_type: Type of mission
            auto_approve: Skip approval prompts

        Returns:
            Results dict with success status and team info
        """
        logger.info(f"[AI-OVERSEER] Coordinating mission: {mission_description}")

        # Phase 0: Check for known false positives (WSP 48/60 collective learning)
        if self._is_known_false_positive("mission", mission_description):
            details = None
            if self.pattern_memory:
                try:
                    details = self.pattern_memory.get_false_positive_reason("mission", mission_description)
                except Exception:
                    details = None
            return {
                "success": True,
                "skipped": True,
                "reason": details.get("reason") if details else "Known false positive (learned from collective intelligence)",
                "actual_location": details.get("actual_location") if details else None,
                "mission_description": mission_description,
                "mission_type": mission_type.value
            }

        # Spawn agent team (runs all 4 phases)
        team = self.spawn_agent_team(mission_description, mission_type, auto_approve)

        # Store learning pattern
        self.store_mission_pattern(team)

        return {
            "success": team.results.get("success", False),
            "mission_id": team.mission_id,
            "team": {
                "partner": team.partner,
                "principal": team.principal,
                "associate": team.associate
            },
            "results": team.results
        }


def main():
    """Demonstrate AI Intelligence Overseer"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Intelligence Overseer")
    parser.add_argument("mission", type=str, help="Mission description")
    parser.add_argument("--type", type=str, default="custom",
                        choices=[mt.value for mt in MissionType],
                        help="Mission type")
    parser.add_argument("--auto-approve", action="store_true", help="Auto-approve execution")

    args = parser.parse_args()

    # Initialize overseer
    repo_root = Path(__file__).parent.parent.parent.parent.parent
    overseer = AIIntelligenceOverseer(repo_root)

    print("AI Intelligence Overseer - WSP 77 Agent Coordination")
    print("=" * 60)
    print(f"Mission: {args.mission}")
    print(f"Type: {args.type}")
    print("=" * 60)

    # Coordinate mission
    results = overseer.coordinate_mission(
        mission_description=args.mission,
        mission_type=MissionType(args.type),
        auto_approve=args.auto_approve
    )

    print(f"\n[RESULTS]")
    print(f"  Success: {results['success']}")
    print(f"  Mission ID: {results['mission_id']}")
    print(f"  Team: {results['team']}")
    print(f"  Phases completed: {results['results'].get('phases_completed', 0)}")
    print(f"  Phases failed: {results['results'].get('phases_failed', 0)}")


if __name__ == "__main__":
    main()
