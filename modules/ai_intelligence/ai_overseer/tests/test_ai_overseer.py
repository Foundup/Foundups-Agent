#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Intelligence Overseer - Unit Tests
=====================================

Tests for WSP 77 agent coordination with Qwen + Gemma + 0102.

Test Coverage:
    - WSP 54 role assignments (Agent Teams variant)
    - WSP 77 4-phase coordination workflow
    - Mission analysis and planning
    - Team spawning and execution
    - Learning and pattern storage (WSP 48)
"""

import unittest
import sys
import json
from pathlib import Path
import tempfile
import shutil

# Import module under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from modules.ai_intelligence.ai_overseer.src.ai_overseer import (
    AIIntelligenceOverseer,
    AgentRole,
    MissionType,
    AgentTeam,
    CoordinationPlan
)


class TestWSP54RoleMapping(unittest.TestCase):
    """Test WSP 54 Agent Teams role assignments"""

    def test_agent_role_enum(self):
        """Verify AgentRole enum has correct WSP 54 mappings"""
        self.assertEqual(AgentRole.PARTNER.value, "qwen")      # Qwen Partner
        self.assertEqual(AgentRole.PRINCIPAL.value, "0102")    # 0102 Principal
        self.assertEqual(AgentRole.ASSOCIATE.value, "gemma")   # Gemma Associate

    def test_agent_team_defaults(self):
        """Verify AgentTeam uses correct default roles"""
        team = AgentTeam(
            mission_id="test_001",
            mission_type=MissionType.CODE_ANALYSIS
        )

        self.assertEqual(team.partner, "qwen")      # Qwen does simple stuff, scales up
        self.assertEqual(team.principal, "0102")    # 0102 lays out plan, oversees
        self.assertEqual(team.associate, "gemma")   # Gemma pattern recognition


class TestAIOverseerInitialization(unittest.TestCase):
    """Test AI Overseer initialization"""

    def setUp(self):
        """Create temporary repo for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.test_dir)

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_initialization(self):
        """Test AI Overseer initializes correctly"""
        overseer = AIIntelligenceOverseer(self.repo_root)

        self.assertEqual(overseer.repo_root, self.repo_root)
        self.assertTrue(overseer.memory_path.exists())
        self.assertIsInstance(overseer.patterns, dict)
        self.assertIsInstance(overseer.active_teams, dict)

    def test_memory_structure(self):
        """Test learning patterns memory structure"""
        overseer = AIIntelligenceOverseer(self.repo_root)

        self.assertIn("successful_missions", overseer.patterns)
        self.assertIn("failed_missions", overseer.patterns)
        self.assertIn("learned_strategies", overseer.patterns)
        self.assertIn("team_performance", overseer.patterns)


class TestPhase1GemmaAnalysis(unittest.TestCase):
    """Test Phase 1: Gemma Associate fast analysis"""

    def setUp(self):
        """Create temporary repo for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.test_dir)
        self.overseer = AIIntelligenceOverseer(self.repo_root)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_analyze_simple_mission(self):
        """Test Gemma analyzes simple mission correctly"""
        analysis = self.overseer.analyze_mission_requirements(
            mission_description="Test code quality",
            mission_type=MissionType.CODE_ANALYSIS
        )

        self.assertIn("method", analysis)
        self.assertIn("mission_type", analysis)
        self.assertIn("classification", analysis)
        self.assertEqual(analysis["mission_type"], "code_analysis")

    def test_complexity_classification(self):
        """Test complexity classification logic"""
        # Simple mission
        simple = self.overseer.analyze_mission_requirements("Test simple function")
        self.assertEqual(simple["classification"]["complexity"], 2)

        # Complex mission
        complex_analysis = self.overseer.analyze_mission_requirements(
            "Refactor multi-module system-wide architecture"
        )
        self.assertEqual(complex_analysis["classification"]["complexity"], 5)

    def test_team_recommendation(self):
        """Test Gemma recommends correct team composition"""
        analysis = self.overseer.analyze_mission_requirements(
            mission_description="Build agent",
            mission_type=MissionType.MODULE_INTEGRATION
        )

        team = analysis["recommended_team"]
        self.assertEqual(team["partner"], "qwen")
        self.assertEqual(team["principal"], "0102")
        self.assertEqual(team["associate"], "gemma")


class TestPhase2QwenPlanning(unittest.TestCase):
    """Test Phase 2: Qwen Partner strategic planning"""

    def setUp(self):
        """Create temporary repo for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.test_dir)
        self.overseer = AIIntelligenceOverseer(self.repo_root)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_generate_coordination_plan(self):
        """Test Qwen generates coordination plan"""
        # First: Gemma analysis
        analysis = self.overseer.analyze_mission_requirements(
            mission_description="Analyze code",
            mission_type=MissionType.CODE_ANALYSIS
        )

        # Then: Qwen planning
        plan = self.overseer.generate_coordination_plan(analysis)

        self.assertIsInstance(plan, CoordinationPlan)
        self.assertEqual(plan.mission_type, MissionType.CODE_ANALYSIS)
        self.assertGreater(len(plan.phases), 0)
        self.assertGreater(plan.estimated_complexity, 0)

    def test_qwen_phases_structure(self):
        """Test Qwen generates correct phase structure"""
        analysis = self.overseer.analyze_mission_requirements("Test mission")
        plan = self.overseer.generate_coordination_plan(analysis)

        for phase in plan.phases:
            self.assertIn("phase", phase)
            self.assertIn("name", phase)
            self.assertIn("agent", phase)
            self.assertIn("description", phase)
            self.assertIn("complexity", phase)
            self.assertIn("estimated_time_ms", phase)
            # WSP 15 MPS scoring
            self.assertIn("mps_score", phase)
            self.assertIn("priority", phase)

    def test_wsp15_mps_scoring(self):
        """Test Qwen applies WSP 15 MPS scoring correctly"""
        analysis = self.overseer.analyze_mission_requirements("Complex integration")
        plan = self.overseer.generate_coordination_plan(analysis)

        for phase in plan.phases:
            mps = phase["mps_score"]
            priority = phase["priority"]

            # MPS score should be reasonable (4-20 range)
            self.assertGreaterEqual(mps, 4)
            self.assertLessEqual(mps, 20)

            # Priority should match MPS ranges
            if mps >= 16:
                self.assertEqual(priority, "P0")
            elif mps >= 13:
                self.assertEqual(priority, "P1")
            elif mps >= 10:
                self.assertEqual(priority, "P2")
            elif mps >= 7:
                self.assertEqual(priority, "P3")
            else:
                self.assertEqual(priority, "P4")

    def test_qwen_scales_with_complexity(self):
        """Test Qwen generates more phases for complex missions"""
        # Simple mission
        simple_analysis = self.overseer.analyze_mission_requirements("Simple test")
        simple_plan = self.overseer.generate_coordination_plan(simple_analysis)

        # Complex mission
        complex_analysis = self.overseer.analyze_mission_requirements(
            "Complex multi-module system architecture refactoring"
        )
        complex_plan = self.overseer.generate_coordination_plan(complex_analysis)

        # Complex should have more phases
        self.assertGreater(len(complex_plan.phases), len(simple_plan.phases))


class TestPhase30102Oversight(unittest.TestCase):
    """Test Phase 3: 0102 Principal execution oversight"""

    def setUp(self):
        """Create temporary repo for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.test_dir)
        self.overseer = AIIntelligenceOverseer(self.repo_root)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_spawn_agent_team(self):
        """Test 0102 spawns agent team correctly"""
        team = self.overseer.spawn_agent_team(
            mission_description="Test mission",
            mission_type=MissionType.CODE_ANALYSIS,
            auto_approve=True  # Skip prompts for testing
        )

        self.assertIsInstance(team, AgentTeam)
        self.assertEqual(team.partner, "qwen")
        self.assertEqual(team.principal, "0102")
        self.assertEqual(team.associate, "gemma")
        self.assertIn(team.status, ["executing", "completed", "failed"])

    def test_0102_oversight_execution(self):
        """Test 0102 executes with oversight"""
        team = self.overseer.spawn_agent_team(
            mission_description="Simple test",
            mission_type=MissionType.CODE_ANALYSIS,
            auto_approve=True
        )

        self.assertIsInstance(team.results, dict)
        self.assertIn("success", team.results)
        self.assertIn("phases_completed", team.results)
        self.assertIn("phases_failed", team.results)
        self.assertIn("phase_results", team.results)


class TestPhase4Learning(unittest.TestCase):
    """Test Phase 4: Learning and pattern storage (WSP 48)"""

    def setUp(self):
        """Create temporary repo for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.test_dir)
        self.overseer = AIIntelligenceOverseer(self.repo_root)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_store_successful_mission(self):
        """Test successful mission stored as learning pattern"""
        team = AgentTeam(
            mission_id="test_success",
            mission_type=MissionType.CODE_ANALYSIS,
            status="completed"
        )
        team.results = {"success": True, "phases_completed": 3}

        self.overseer.store_mission_pattern(team)

        # Verify stored in successful missions
        self.assertEqual(len(self.overseer.patterns["successful_missions"]), 1)
        stored = self.overseer.patterns["successful_missions"][0]
        self.assertEqual(stored["mission_id"], "test_success")
        self.assertTrue(stored["results"]["success"])

    def test_store_failed_mission(self):
        """Test failed mission stored for analysis"""
        team = AgentTeam(
            mission_id="test_failure",
            mission_type=MissionType.MODULE_INTEGRATION,
            status="failed"
        )
        team.results = {"success": False, "errors": ["Test error"]}

        self.overseer.store_mission_pattern(team)

        # Verify stored in failed missions
        self.assertEqual(len(self.overseer.patterns["failed_missions"]), 1)
        stored = self.overseer.patterns["failed_missions"][0]
        self.assertEqual(stored["mission_id"], "test_failure")
        self.assertFalse(stored["results"]["success"])

    def test_pattern_memory_persistence(self):
        """Test patterns persist to disk (WSP 48 learning)"""
        team = AgentTeam(
            mission_id="test_persist",
            mission_type=MissionType.CODE_ANALYSIS,
            status="completed"
        )
        team.results = {"success": True}

        self.overseer.store_mission_pattern(team)

        # Verify saved to file
        self.assertTrue(self.overseer.memory_path.exists())

        # Load in new overseer instance
        overseer2 = AIIntelligenceOverseer(self.repo_root)
        self.assertEqual(len(overseer2.patterns["successful_missions"]), 1)


class TestFullCoordinationWorkflow(unittest.TestCase):
    """Test complete WSP 77 coordination workflow"""

    def setUp(self):
        """Create temporary repo for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.repo_root = Path(self.test_dir)
        self.overseer = AIIntelligenceOverseer(self.repo_root)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_coordinate_mission_workflow(self):
        """Test full WSP 77 4-phase workflow"""
        results = self.overseer.coordinate_mission(
            mission_description="Test full workflow",
            mission_type=MissionType.CODE_ANALYSIS,
            auto_approve=True
        )

        # Verify results structure
        self.assertIsInstance(results, dict)
        self.assertIn("success", results)
        self.assertIn("mission_id", results)
        self.assertIn("team", results)
        self.assertIn("results", results)

        # Verify team composition
        team = results["team"]
        self.assertEqual(team["partner"], "qwen")
        self.assertEqual(team["principal"], "0102")
        self.assertEqual(team["associate"], "gemma")

        # Verify learning pattern was stored
        self.assertGreater(
            len(self.overseer.patterns["successful_missions"]) +
            len(self.overseer.patterns["failed_missions"]),
            0
        )

    def test_mission_type_handling(self):
        """Test different mission types are handled correctly"""
        mission_types = [
            MissionType.CODE_ANALYSIS,
            MissionType.ARCHITECTURE_DESIGN,
            MissionType.MODULE_INTEGRATION,
            MissionType.TESTING_ORCHESTRATION,
            MissionType.WSP_COMPLIANCE
        ]

        for mission_type in mission_types:
            results = self.overseer.coordinate_mission(
                mission_description=f"Test {mission_type.value}",
                mission_type=mission_type,
                auto_approve=True
            )

            self.assertIsInstance(results, dict)
            self.assertIn("success", results)


class TestDeprecatedSystemReplacement(unittest.TestCase):
    """Test that new system replaces deprecated 6-agent system"""

    def test_no_old_agent_types(self):
        """Verify old agent types (WINSERV, RIDER, etc.) are not used"""
        # New system should NOT have these agent types
        with self.assertRaises(AttributeError):
            _ = AgentRole.WINSERV
        with self.assertRaises(AttributeError):
            _ = AgentRole.RIDER
        with self.assertRaises(AttributeError):
            _ = AgentRole.BOARD
        with self.assertRaises(AttributeError):
            _ = AgentRole.FRONT_CELL
        with self.assertRaises(AttributeError):
            _ = AgentRole.BACK_CELL
        with self.assertRaises(AttributeError):
            _ = AgentRole.GEMINI

    def test_new_agent_roles_only(self):
        """Verify only new WSP 54 Agent Teams roles exist"""
        # Should only have these 3 roles
        all_roles = [role.value for role in AgentRole]
        self.assertEqual(len(all_roles), 3)
        self.assertIn("qwen", all_roles)
        self.assertIn("0102", all_roles)
        self.assertIn("gemma", all_roles)


def run_tests():
    """Run all tests"""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == "__main__":
    print("AI Intelligence Overseer - Unit Tests")
    print("WSP 77 Agent Coordination (Qwen + Gemma + 0102)")
    print("=" * 60)
    run_tests()
