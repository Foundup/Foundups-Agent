#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Gemma Libido Monitor

WSP Compliance: WSP 5 (Test Coverage), WSP 96 (WRE Skills), WSP 77 (Agent Coordination)
"""

import pytest
from datetime import datetime, timedelta
from modules.infrastructure.wre_core.src.libido_monitor import (
    GemmaLibidoMonitor,
    LibidoSignal,
    PatternExecution
)


class TestGemmaLibidoMonitor:
    """Test suite for Gemma Libido Monitor (pattern frequency sensor)"""

    def test_initialization(self):
        """Test monitor initializes with correct defaults"""
        monitor = GemmaLibidoMonitor()

        assert monitor.pattern_history.maxlen == 100
        assert monitor.default_thresholds == (1, 5, 600)
        assert "qwen_gitpush" in monitor.frequency_thresholds
        assert monitor.frequency_thresholds["qwen_gitpush"] == (1, 5, 600)

    def test_should_execute_first_time(self):
        """Test ESCALATE signal on first execution (below min frequency)"""
        monitor = GemmaLibidoMonitor()

        signal = monitor.should_execute("qwen_gitpush", "exec_001")

        assert signal == LibidoSignal.ESCALATE  # 0 < min_freq (1)

    def test_should_execute_within_range(self):
        """Test CONTINUE signal when frequency is within acceptable range"""
        monitor = GemmaLibidoMonitor()

        # Record 2 executions (within min=1, max=5)
        monitor.record_execution("qwen_gitpush", "qwen", "exec_001", 0.92)
        monitor.record_execution("qwen_gitpush", "qwen", "exec_002", 0.94)

        signal = monitor.should_execute("qwen_gitpush", "exec_003")

        assert signal == LibidoSignal.CONTINUE  # 2 in [1, 5]

    def test_should_execute_max_frequency_throttle(self):
        """Test THROTTLE signal when max frequency reached"""
        monitor = GemmaLibidoMonitor()

        # Record 5 executions (hit max)
        for i in range(5):
            monitor.record_execution("qwen_gitpush", "qwen", f"exec_{i}", 0.90)

        signal = monitor.should_execute("qwen_gitpush", "exec_006")

        assert signal == LibidoSignal.THROTTLE  # 5 >= max_freq (5)

    def test_should_execute_cooldown_throttle(self):
        """Test THROTTLE signal during cooldown period"""
        monitor = GemmaLibidoMonitor()

        # Record 1 execution
        monitor.record_execution("qwen_gitpush", "qwen", "exec_001", 0.92)

        # Try to execute immediately (within 600s cooldown)
        signal = monitor.should_execute("qwen_gitpush", "exec_002")

        assert signal == LibidoSignal.THROTTLE  # Within cooldown

    def test_should_execute_force_override(self):
        """Test force=True overrides all libido signals"""
        monitor = GemmaLibidoMonitor()

        # Record max executions
        for i in range(5):
            monitor.record_execution("qwen_gitpush", "qwen", f"exec_{i}", 0.90)

        # Force should override throttle
        signal = monitor.should_execute("qwen_gitpush", "exec_006", force=True)

        assert signal == LibidoSignal.CONTINUE

    def test_record_execution(self):
        """Test execution recording in pattern history"""
        monitor = GemmaLibidoMonitor()

        monitor.record_execution("qwen_gitpush", "qwen", "exec_001", 0.92)

        assert len(monitor.pattern_history) == 1
        execution = monitor.pattern_history[0]
        assert execution.skill_name == "qwen_gitpush"
        assert execution.agent == "qwen"
        assert execution.execution_id == "exec_001"
        assert execution.fidelity_score == 0.92

    def test_validate_step_fidelity_all_patterns_present(self):
        """Test fidelity validation when all patterns present"""
        monitor = GemmaLibidoMonitor()

        step_output = {
            "change_type": "feature",
            "summary": "Add X",
            "critical_files": ["main.py"],
            "confidence": 0.85
        }
        expected_patterns = ["change_type", "summary", "critical_files", "confidence"]

        fidelity = monitor.validate_step_fidelity(step_output, expected_patterns)

        assert fidelity == 1.0  # 4/4 patterns present

    def test_validate_step_fidelity_partial_patterns(self):
        """Test fidelity validation with missing patterns"""
        monitor = GemmaLibidoMonitor()

        step_output = {
            "change_type": "feature",
            "summary": "Add X"
            # Missing: critical_files, confidence
        }
        expected_patterns = ["change_type", "summary", "critical_files", "confidence"]

        fidelity = monitor.validate_step_fidelity(step_output, expected_patterns)

        assert fidelity == 0.5  # 2/4 patterns present

    def test_validate_step_fidelity_null_values_fail(self):
        """Test null values don't count as present patterns"""
        monitor = GemmaLibidoMonitor()

        step_output = {
            "change_type": "feature",
            "summary": None,  # Null value
            "critical_files": [],
            "confidence": 0.85
        }
        expected_patterns = ["change_type", "summary", "critical_files", "confidence"]

        fidelity = monitor.validate_step_fidelity(step_output, expected_patterns)

        # summary=None should not count
        assert fidelity == 0.75  # 3/4 patterns (summary doesn't count)

    def test_get_skill_statistics_no_executions(self):
        """Test statistics for skill with no executions"""
        monitor = GemmaLibidoMonitor()

        stats = monitor.get_skill_statistics("nonexistent_skill")

        assert stats["skill_name"] == "nonexistent_skill"
        assert stats["execution_count"] == 0
        assert stats["avg_fidelity"] == 0.0

    def test_get_skill_statistics_with_executions(self):
        """Test statistics calculation with executions"""
        monitor = GemmaLibidoMonitor()

        # Record 3 executions with different fidelities
        monitor.record_execution("qwen_gitpush", "qwen", "exec_001", 0.90)
        monitor.record_execution("qwen_gitpush", "qwen", "exec_002", 0.95)
        monitor.record_execution("qwen_gitpush", "qwen", "exec_003", 0.93)

        stats = monitor.get_skill_statistics("qwen_gitpush")

        assert stats["execution_count"] == 3
        assert stats["avg_fidelity"] == pytest.approx(0.926, abs=0.01)
        assert "last_execution" in stats

    def test_set_thresholds(self):
        """Test custom threshold configuration"""
        monitor = GemmaLibidoMonitor()

        monitor.set_thresholds("custom_skill", min_frequency=2, max_frequency=10, cooldown_seconds=300)

        assert monitor.frequency_thresholds["custom_skill"] == (2, 10, 300)

    def test_history_maxlen_enforcement(self):
        """Test pattern history respects maxlen"""
        monitor = GemmaLibidoMonitor(history_size=5)

        # Record 10 executions (should only keep last 5)
        for i in range(10):
            monitor.record_execution("qwen_gitpush", "qwen", f"exec_{i:03d}", 0.90)

        assert len(monitor.pattern_history) == 5
        # Should have exec_005 through exec_009
        assert monitor.pattern_history[0].execution_id == "exec_005"
        assert monitor.pattern_history[-1].execution_id == "exec_009"

    def test_multiple_skills_tracked_separately(self):
        """Test different skills tracked independently"""
        monitor = GemmaLibidoMonitor()

        # Record executions for two different skills
        monitor.record_execution("qwen_gitpush", "qwen", "exec_001", 0.92)
        monitor.record_execution("youtube_spam", "gemma", "exec_002", 0.88)
        monitor.record_execution("qwen_gitpush", "qwen", "exec_003", 0.94)

        stats_gitpush = monitor.get_skill_statistics("qwen_gitpush")
        stats_youtube = monitor.get_skill_statistics("youtube_spam")

        assert stats_gitpush["execution_count"] == 2
        assert stats_youtube["execution_count"] == 1

    def test_export_history(self, tmp_path):
        """Test pattern history export to JSON"""
        monitor = GemmaLibidoMonitor()

        # Record some executions
        monitor.record_execution("qwen_gitpush", "qwen", "exec_001", 0.92)
        monitor.record_execution("qwen_gitpush", "qwen", "exec_002", 0.94)

        output_file = tmp_path / "history.json"
        monitor.export_history(output_file)

        assert output_file.exists()

        import json
        with open(output_file) as f:
            data = json.load(f)

        assert len(data) == 2
        assert data[0]["execution_id"] == "exec_001"
        assert data[0]["fidelity_score"] == 0.92


class TestLibidoSignal:
    """Test LibidoSignal enum"""

    def test_signal_values(self):
        """Test enum has correct values"""
        assert LibidoSignal.CONTINUE.value == "continue"
        assert LibidoSignal.THROTTLE.value == "throttle"
        assert LibidoSignal.ESCALATE.value == "escalate"


class TestPatternExecution:
    """Test PatternExecution dataclass"""

    def test_pattern_execution_creation(self):
        """Test creating PatternExecution record"""
        execution = PatternExecution(
            skill_name="qwen_gitpush",
            agent="qwen",
            timestamp=datetime.now(),
            execution_id="exec_001",
            fidelity_score=0.92
        )

        assert execution.skill_name == "qwen_gitpush"
        assert execution.agent == "qwen"
        assert execution.execution_id == "exec_001"
        assert execution.fidelity_score == 0.92

    def test_pattern_execution_optional_fidelity(self):
        """Test PatternExecution with optional fidelity score"""
        execution = PatternExecution(
            skill_name="qwen_gitpush",
            agent="qwen",
            timestamp=datetime.now(),
            execution_id="exec_001"
        )

        assert execution.fidelity_score is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
