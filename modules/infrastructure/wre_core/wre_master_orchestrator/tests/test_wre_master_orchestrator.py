#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for WRE Master Orchestrator

WSP Compliance: WSP 5 (Test Coverage), WSP 96 (WRE Skills), WSP 77 (Agent Coordination)
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from modules.infrastructure.wre_core.wre_master_orchestrator.src.wre_master_orchestrator import (
    WREMasterOrchestrator,
    WRE_SKILLS_AVAILABLE
)
from modules.infrastructure.wre_core.src.libido_monitor import LibidoSignal


class TestWREMasterOrchestrator:
    """Test suite for WRE Master Orchestrator"""

    @pytest.fixture
    def orchestrator(self):
        """Create WRE Master Orchestrator instance"""
        return WREMasterOrchestrator()

    def test_initialization(self, orchestrator):
        """Test orchestrator initializes with correct components"""
        assert orchestrator is not None
        assert hasattr(orchestrator, 'pattern_memory')
        assert hasattr(orchestrator, 'wsp_validator')
        assert hasattr(orchestrator, 'plugins')

        # Check WSP 96 v1.3 components if available
        if WRE_SKILLS_AVAILABLE:
            assert hasattr(orchestrator, 'libido_monitor')
            assert hasattr(orchestrator, 'sqlite_memory')
            assert hasattr(orchestrator, 'skills_loader')

    @pytest.mark.skipif(not WRE_SKILLS_AVAILABLE, reason="WRE Skills infrastructure not available")
    def test_execute_skill_first_execution_escalates(self, orchestrator):
        """Test first skill execution triggers ESCALATE signal"""
        skill_name = "qwen_gitpush"
        agent = "qwen"
        input_context = {"files_changed": 14, "lines_added": 250}

        result = orchestrator.execute_skill(skill_name, agent, input_context)

        # First execution should always proceed (ESCALATE signal)
        assert result["success"] is True
        assert "pattern_fidelity" in result
        assert "execution_id" in result
        assert "execution_time_ms" in result

    @pytest.mark.skipif(not WRE_SKILLS_AVAILABLE, reason="WRE Skills infrastructure not available")
    def test_execute_skill_throttle_behavior(self, orchestrator):
        """Test skill execution respects libido THROTTLE signal"""
        skill_name = "qwen_gitpush"
        agent = "qwen"
        input_context = {"files_changed": 5}

        # Execute 5 times (hit max frequency)
        for i in range(5):
            result = orchestrator.execute_skill(skill_name, agent, input_context)
            assert result["success"] is True

        # 6th execution should be throttled
        result = orchestrator.execute_skill(skill_name, agent, input_context)
        assert result.get("throttled") is True

    @pytest.mark.skipif(not WRE_SKILLS_AVAILABLE, reason="WRE Skills infrastructure not available")
    def test_execute_skill_force_override(self, orchestrator):
        """Test force=True overrides libido throttle"""
        skill_name = "qwen_gitpush"
        agent = "qwen"
        input_context = {"files_changed": 10}

        # Execute 5 times (hit max frequency)
        for i in range(5):
            orchestrator.execute_skill(skill_name, agent, input_context)

        # Force execution should succeed despite throttle
        result = orchestrator.execute_skill(skill_name, agent, input_context, force=True)
        assert result["success"] is True
        assert result.get("throttled") is not True

    @pytest.mark.skipif(not WRE_SKILLS_AVAILABLE, reason="WRE Skills infrastructure not available")
    def test_execute_skill_stores_outcome(self, orchestrator):
        """Test skill execution stores outcome in pattern memory"""
        skill_name = "qwen_gitpush"
        agent = "qwen"
        input_context = {"files_changed": 14}

        # Execute skill
        result = orchestrator.execute_skill(skill_name, agent, input_context)
        execution_id = result["execution_id"]

        # Verify outcome stored in SQLite pattern memory
        patterns = orchestrator.sqlite_memory.recall_successful_patterns(skill_name, min_fidelity=0.0, limit=10)

        # Should find the execution we just did
        execution_found = any(p["execution_id"] == execution_id for p in patterns)
        assert execution_found, f"Execution {execution_id} not found in pattern memory"

    @pytest.mark.skipif(not WRE_SKILLS_AVAILABLE, reason="WRE Skills infrastructure not available")
    def test_execute_skill_records_libido_history(self, orchestrator):
        """Test skill execution records in libido monitor history"""
        skill_name = "qwen_gitpush"
        agent = "qwen"
        input_context = {"files_changed": 8}

        # Execute skill
        result = orchestrator.execute_skill(skill_name, agent, input_context)

        # Verify recorded in libido monitor
        stats = orchestrator.libido_monitor.get_skill_statistics(skill_name)
        assert stats["execution_count"] >= 1
        assert stats["avg_fidelity"] >= 0.0

    @pytest.mark.skipif(not WRE_SKILLS_AVAILABLE, reason="WRE Skills infrastructure not available")
    def test_execute_skill_calculates_execution_time(self, orchestrator):
        """Test execution time is measured and returned"""
        skill_name = "qwen_gitpush"
        agent = "qwen"
        input_context = {"files_changed": 12}

        result = orchestrator.execute_skill(skill_name, agent, input_context)

        assert "execution_time_ms" in result
        assert isinstance(result["execution_time_ms"], int)
        assert result["execution_time_ms"] >= 0

    @pytest.mark.skipif(not WRE_SKILLS_AVAILABLE, reason="WRE Skills infrastructure not available")
    def test_execute_skill_pattern_fidelity_recorded(self, orchestrator):
        """Test pattern fidelity is calculated and stored"""
        skill_name = "qwen_gitpush"
        agent = "qwen"
        input_context = {"files_changed": 20}

        result = orchestrator.execute_skill(skill_name, agent, input_context)

        assert "pattern_fidelity" in result
        assert isinstance(result["pattern_fidelity"], float)
        assert 0.0 <= result["pattern_fidelity"] <= 1.0

    @pytest.mark.skipif(not WRE_SKILLS_AVAILABLE, reason="WRE Skills infrastructure not available")
    def test_execute_skill_multiple_agents(self, orchestrator):
        """Test different agents can execute same skill"""
        skill_name = "qwen_gitpush"
        input_context = {"files_changed": 7}

        # Execute with qwen
        result_qwen = orchestrator.execute_skill(skill_name, "qwen", input_context)
        assert result_qwen["success"] is True

        # Execute with gemma (if skill supports it)
        result_gemma = orchestrator.execute_skill(skill_name, "gemma", input_context)
        assert result_gemma["success"] is True

        # Both should be recorded separately
        stats = orchestrator.libido_monitor.get_skill_statistics(skill_name)
        assert stats["execution_count"] >= 2

    @pytest.mark.skipif(not WRE_SKILLS_AVAILABLE, reason="WRE Skills infrastructure not available")
    def test_execute_skill_input_context_stored(self, orchestrator):
        """Test input context is stored in outcome record"""
        skill_name = "qwen_gitpush"
        agent = "qwen"
        input_context = {"files_changed": 14, "lines_added": 250, "critical_files": ["main.py"]}

        result = orchestrator.execute_skill(skill_name, agent, input_context)
        execution_id = result["execution_id"]

        # Recall and verify input context was stored
        patterns = orchestrator.sqlite_memory.recall_successful_patterns(skill_name, min_fidelity=0.0, limit=10)
        execution = next((p for p in patterns if p["execution_id"] == execution_id), None)

        assert execution is not None
        stored_context = json.loads(execution["input_context"])
        assert stored_context["files_changed"] == 14
        assert stored_context["lines_added"] == 250

    def test_validate_module_path(self, orchestrator):
        """Test module path validation"""
        # Valid path
        valid_path = Path("modules/ai_intelligence/pqn_alignment")
        result = orchestrator.validate_module_path(valid_path)
        assert result is True

        # Invalid path
        invalid_path = Path("nonexistent/module/path")
        result = orchestrator.validate_module_path(invalid_path)
        assert result is False

    def test_register_plugin(self, orchestrator):
        """Test plugin registration"""
        class TestPlugin:
            def process(self):
                return "test_result"

        plugin = TestPlugin()
        orchestrator.register_plugin("test_plugin", plugin)

        assert "test_plugin" in orchestrator.plugins
        assert orchestrator.plugins["test_plugin"] == plugin

    def test_get_plugin(self, orchestrator):
        """Test plugin retrieval"""
        class TestPlugin:
            def process(self):
                return "test_result"

        plugin = TestPlugin()
        orchestrator.register_plugin("test_plugin", plugin)

        retrieved = orchestrator.get_plugin("test_plugin")
        assert retrieved == plugin

        # Nonexistent plugin should return None
        nonexistent = orchestrator.get_plugin("nonexistent_plugin")
        assert nonexistent is None


class TestWRESkillsIntegration:
    """Integration tests for WRE Skills system"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance"""
        return WREMasterOrchestrator()

    @pytest.mark.skipif(not WRE_SKILLS_AVAILABLE, reason="WRE Skills infrastructure not available")
    def test_end_to_end_skill_execution_cycle(self, orchestrator):
        """Test complete cycle: execute → store → recall → analyze"""
        skill_name = "qwen_gitpush"
        agent = "qwen"

        # Step 1: Execute skill 3 times
        execution_ids = []
        for i in range(3):
            input_context = {"files_changed": 10 + i, "execution_number": i}
            result = orchestrator.execute_skill(skill_name, agent, input_context)
            execution_ids.append(result["execution_id"])
            assert result["success"] is True

        # Step 2: Recall successful patterns
        patterns = orchestrator.sqlite_memory.recall_successful_patterns(skill_name, min_fidelity=0.0)
        assert len(patterns) >= 3

        # Step 3: Get metrics
        metrics = orchestrator.sqlite_memory.get_skill_metrics(skill_name, days=1)
        assert metrics["execution_count"] >= 3
        assert metrics["avg_fidelity"] >= 0.0

        # Step 4: Get libido statistics
        stats = orchestrator.libido_monitor.get_skill_statistics(skill_name)
        assert stats["execution_count"] >= 3

    @pytest.mark.skipif(not WRE_SKILLS_AVAILABLE, reason="WRE Skills infrastructure not available")
    def test_skill_convergence_simulation(self, orchestrator):
        """Simulate skill convergence over multiple executions"""
        skill_name = "test_convergence_skill"
        agent = "qwen"

        # Execute 10 times and track fidelity
        fidelities = []
        for i in range(10):
            input_context = {"iteration": i}
            result = orchestrator.execute_skill(skill_name, agent, input_context, force=True)
            fidelities.append(result["pattern_fidelity"])

        # Check metrics reflect all executions
        metrics = orchestrator.sqlite_memory.get_skill_metrics(skill_name, days=1)
        assert metrics["execution_count"] == 10

        # Verify execution history exists
        patterns = orchestrator.sqlite_memory.recall_successful_patterns(skill_name, min_fidelity=0.0, limit=20)
        assert len(patterns) >= 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
